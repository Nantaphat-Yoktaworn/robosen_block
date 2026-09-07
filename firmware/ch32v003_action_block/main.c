/*
 * Robosen Physical Modular Block System - Unified Action Block Firmware
 * Target: WCH CH32V003F4P6 (32-bit RISC-V @ 24MHz)
 * 
 * Pin Allocations:
 *   PD6 (Pin 13) - USART1_RX: Upstream Chain RX / Config Dock In
 *   PD5 (Pin 9)  - USART1_TX: Downstream Chain TX / Config Dock ACK
 *   PA2 (Pin 3)  - WS2812B RGB LED Data Line (DIN)
 *   PD0 (Pin 12) - Role Detect (Internal Pull-Up):
 *                   High/Floating = Action Block
 *                   Grounded      = Smart End Block
 *   PD4 (Pin 8)  - Onboard Activity LED (toggles on packet receive)
 *   PD1 (Pin 4)  - SWIO 1-wire debug / factory programming line
 * 
 * Protocols Implemented:
 *   1. Config Port Protocol (0xCF):
 *      Master -> Docked Block: [ 0xCF, 0x02, ACTION_ID, PARAM_VAL, CRC8, 0x55 ]
 *      Block  -> Master ACK:   [ 0xCF, 0x06, CRC8, 0x55 ]
 *      Action Block saves configuration permanently in non-volatile flash.
 * 
 *   2. Run Chain Protocol (0xAA Phase 1 Discovery & Compilation):
 *      Master -> Block 1: [ 0xAA, Len=0, Count=0, CRC8, 0x55 ]
 *      Block appends its [ActionID, ParamVal], increments Count & Len, updates CRC8,
 *      and relays downstream.
 * 
 *   3. Run Chain Protocol (0xBB Phase 2 Real-Time Step Tracking):
 *      Master -> Broadcast: [ 0xBB, ActiveStep, TotalSteps, CRC8, 0x55 ]
 *      Block glows bright green when its step is active, or shows action color.
 */

#include "ch32fun.h"
#include <stdint.h>
#include <stdbool.h>

// ==============================================================================
// 1. HARDWARE DEFINITIONS & FLASH STORAGE
// ==============================================================================
#define FLASH_CFG_ADDR 0x08003FC0UL  // Top 64-byte page of 16KB flash
#define CFG_MAGIC      0xA55A0002UL

typedef struct {
    volatile uint32_t ACTLR;
    volatile uint32_t KEYR;
    volatile uint32_t OBKEYR;
    volatile uint32_t STATR;
    volatile uint32_t CTLR;
    volatile uint32_t ADDR;
    volatile uint32_t OBR;
    volatile uint32_t WPR;
    volatile uint32_t RESERVED[2];
    volatile uint32_t MODEKEYR;
} FlashController;
#define FLASH_CTRL ((FlashController *)0x40022000UL)

static uint8_t g_action_id = 0x01; // Default: Walk Forward
static uint8_t g_param_val = 0x01; // Default: 1 Step
static uint8_t g_my_index  = 0;    // Assigned dynamically during Phase 1

void flash_unlock() {
    FLASH_CTRL->KEYR = 0x45670123UL;
    FLASH_CTRL->KEYR = 0xCDEF89ABUL;
    FLASH_CTRL->MODEKEYR = 0x45670123UL;
    FLASH_CTRL->MODEKEYR = 0xCDEF89ABUL;
}

void load_config() {
    volatile uint32_t *p = (volatile uint32_t *)FLASH_CFG_ADDR;
    if (p[0] == CFG_MAGIC) {
        g_action_id = (uint8_t)(p[1] & 0xFF);
        g_param_val = (uint8_t)((p[1] >> 8) & 0xFF);
    } else {
        g_action_id = 0x01; // Default: Walk Forward
        g_param_val = 0x01; // Default: 1 Step
    }
}

void save_config(uint8_t action, uint8_t param) {
    g_action_id = action;
    g_param_val = param;

    flash_unlock();
    while (FLASH_CTRL->STATR & 0x01); // Wait for busy

    // 64-byte page erase
    FLASH_CTRL->CTLR |= 0x00020000UL; // CR_PAGE_ER
    FLASH_CTRL->ADDR = FLASH_CFG_ADDR;
    FLASH_CTRL->CTLR |= 0x00000040UL; // STRT
    while (FLASH_CTRL->STATR & 0x01);
    FLASH_CTRL->CTLR &= ~0x00020000UL;

    // Buffer reset & write
    FLASH_CTRL->CTLR |= 0x00010000UL; // CR_PAGE_PG
    FLASH_CTRL->CTLR |= 0x00080000UL; // CR_BUF_RST

    volatile uint32_t *p = (volatile uint32_t *)FLASH_CFG_ADDR;
    p[0] = CFG_MAGIC;
    p[1] = ((uint32_t)param << 8) | (uint32_t)action;

    FLASH_CTRL->ADDR = FLASH_CFG_ADDR;
    FLASH_CTRL->CTLR |= 0x00000040UL; // STRT
    while (FLASH_CTRL->STATR & 0x01);

    FLASH_CTRL->CTLR &= ~0x00010000UL;
    FLASH_CTRL->CTLR |= 0x00000080UL; // Lock
}

// ==============================================================================
// 2. CRC-8 (Polynomial: 0x07, Init: 0x00)
// ==============================================================================
uint8_t crc8(const uint8_t *data, size_t len) {
    uint8_t crc = 0x00;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 0x80) {
                crc = ((crc << 1) ^ 0x07) & 0xFF;
            } else {
                crc = (crc << 1) & 0xFF;
            }
        }
    }
    return crc;
}

// ==============================================================================
// 3. WS2812B RGB LED DRIVER (PA2 @ 24MHz)
// ==============================================================================
static inline void ws2812_byte(uint8_t b) {
    for (int i = 7; i >= 0; i--) {
        if (b & (1 << i)) {
            GPIOA->BSHR = (1 << 2);
            asm volatile("nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;");
            GPIOA->BCR = (1 << 2);
            asm volatile("nop; nop; nop; nop; nop; nop;");
        } else {
            GPIOA->BSHR = (1 << 2);
            asm volatile("nop; nop; nop; nop; nop;");
            GPIOA->BCR = (1 << 2);
            asm volatile("nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop; nop;");
        }
    }
}

void ws2812_set(uint8_t r, uint8_t g, uint8_t b) {
    __disable_irq();
    ws2812_byte(g); // WS2812 expects Green first
    ws2812_byte(r);
    ws2812_byte(b);
    __enable_irq();
    Delay_Us(65);
}

void set_action_idle_color() {
    switch (g_action_id) {
        case 0x01: // Walk Forward - Vivid Blue
            ws2812_set(0, 20, 80);
            break;
        case 0x02: // Walk Backward - Dark Blue
            ws2812_set(0, 10, 80);
            break;
        case 0x03: // Turn Left - Cyan
            ws2812_set(0, 50, 50);
            break;
        case 0x04: // Turn Right - Cyan
            ws2812_set(0, 50, 50);
            break;
        case 0x07: // Side-step Left - Light Blue
        case 0x08: // Side-step Right - Light Blue
            ws2812_set(0, 35, 70);
            break;
        case 0x10: // Left Punch - Red
        case 0x11: // Right Punch - Red
        case 0x16: // Single Kick - Red
            ws2812_set(80, 5, 5);
            break;
        case 0x12: // Kung Fu - Orange
            ws2812_set(80, 30, 0);
            break;
        case 0x13: // Dance - Purple
            ws2812_set(60, 0, 60);
            break;
        case 0x14: // Push-ups - Brown/Amber
        case 0x15: // Handstand - Brown/Amber
            ws2812_set(50, 25, 0);
            break;
        case 0x17: // Squats - Green
            ws2812_set(5, 70, 5);
            break;
        case 0x18: // Say Hello - Teal
            ws2812_set(0, 50, 30);
            break;
        case 0x19: // Celebrate - Yellow
            ws2812_set(60, 50, 0);
            break;
        default:   // Soft White
            ws2812_set(25, 25, 25);
            break;
    }
}

// ==============================================================================
// 4. UART DRIVER (PD5 = TX, PD6 = RX @ 115200 Baud)
// ==============================================================================
void uart_init() {
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOD | RCC_APB2Periph_USART1;

    // PD5: USART1_TX (Alternate Function Push-Pull, 10MHz)
    funPinMode(PD5, GPIO_CFGLR_OUT_10Mhz_AF_PP);

    // PD6: USART1_RX (Input with Pull-Up)
    funPinMode(PD6, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(PD6, FUN_HIGH);

    // 115200 Baud @ 24MHz Clock: BRR = 24000000 / 115200 = 208 (0xD0)
    USART1->BRR = 208;
    USART1->CTLR1 = USART_CTLR1_TE | USART_CTLR1_RE | USART_CTLR1_UE;
}

static inline void uart_tx(uint8_t b) {
    while (!(USART1->STATR & USART_STATR_TXE));
    USART1->DATAR = b;
}

static inline bool uart_rx_available() {
    return (USART1->STATR & USART_STATR_RXNE) != 0;
}

static inline uint8_t uart_rx_byte() {
    while (!uart_rx_available());
    return (uint8_t)(USART1->DATAR & 0xFF);
}

bool uart_rx_timeout(uint8_t *b, uint32_t timeout_us) {
    uint32_t start = SysTick->CNT;
    // 24 cycles per microsecond
    uint32_t ticks = timeout_us * 24;
    while (!uart_rx_available()) {
        if ((uint32_t)(SysTick->CNT - start) > ticks) return false;
    }
    *b = (uint8_t)(USART1->DATAR & 0xFF);
    return true;
}

// ==============================================================================
// 5. MAIN SYSTEM LOOP & PROTOCOL HANDLERS
// ==============================================================================
int main() {
    SystemInit();
    funGpioInitAll();

    // Enable RCC for GPIOA, GPIOD
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOD;

    // Setup PA2 for WS2812B
    funPinMode(PA2, GPIO_CFGLR_OUT_10Mhz_PP);

    // Setup PD0 for Role Detect (Input Pull-Up)
    funPinMode(PD0, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(PD0, FUN_HIGH);

    // Setup PD4 for Activity Indicator (Output PP)
    funPinMode(PD4, GPIO_CFGLR_OUT_10Mhz_PP);
    funDigitalWrite(PD4, FUN_LOW);

    // Load saved configuration from flash
    load_config();

    // Init UART at 115200
    uart_init();

    // Power-on indication: Emerald green flash, then idle color
    ws2812_set(0, 100, 30);
    Delay_Ms(300);
    set_action_idle_color();

    uint8_t rx_buf[64];

    while (1) {
        if (!uart_rx_available()) continue;

        uint8_t header = uart_rx_byte();

        // ----------------------------------------------------------------------
        // PROTOCOL 1: CONFIG DOCK (0xCF)
        // [ 0xCF, 0x02, ACTION_ID, PARAM_VAL, CRC8, 0x55 ]
        // ----------------------------------------------------------------------
        if (header == 0xCF) {
            funDigitalWrite(PD4, FUN_HIGH);
            uint8_t len = 0;
            if (!uart_rx_timeout(&len, 10000)) continue;
            if (len == 0x02) {
                uint8_t act = 0, par = 0, rx_crc = 0, footer = 0;
                if (uart_rx_timeout(&act, 10000) &&
                    uart_rx_timeout(&par, 10000) &&
                    uart_rx_timeout(&rx_crc, 10000) &&
                    uart_rx_timeout(&footer, 10000)) {
                    
                    uint8_t payload[3] = { len, act, par };
                    uint8_t calc_crc = crc8(payload, 3);

                    if (calc_crc == rx_crc && footer == 0x55) {
                        save_config(act, par);

                        // Send ACK: [ 0xCF, 0x06, CRC8, 0x55 ]
                        uint8_t ack_payload[1] = { 0x06 };
                        uint8_t ack_crc = crc8(ack_payload, 1);
                        uart_tx(0xCF);
                        uart_tx(0x06);
                        uart_tx(ack_crc);
                        uart_tx(0x55);

                        // Visual confirmation: Emerald Green Success Pulse
                        ws2812_set(0, 255, 40);
                        Delay_Ms(400);
                        set_action_idle_color();
                    }
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
        }

        // ----------------------------------------------------------------------
        // PROTOCOL 2: RUN CHAIN DISCOVERY (0xAA)
        // [ 0xAA, Len, Count, (ActionID, ParamVal)*, CRC8, 0x55 ]
        // ----------------------------------------------------------------------
        else if (header == 0xAA) {
            funDigitalWrite(PD4, FUN_HIGH);
            uint8_t len = 0, count = 0;
            if (!uart_rx_timeout(&len, 10000)) continue;
            if (!uart_rx_timeout(&count, 10000)) continue;

            bool ok = true;
            for (uint8_t i = 0; i < len; i++) {
                if (!uart_rx_timeout(&rx_buf[i], 10000)) { ok = false; break; }
            }
            uint8_t rx_crc = 0, footer = 0;
            if (!uart_rx_timeout(&rx_crc, 10000)) ok = false;
            if (!uart_rx_timeout(&footer, 10000)) ok = false;

            if (ok && footer == 0x55) {
                // Verify incoming CRC: covers [len, count, payload...]
                uint8_t check_buf[64];
                check_buf[0] = len;
                check_buf[1] = count;
                for (uint8_t i = 0; i < len; i++) check_buf[2 + i] = rx_buf[i];
                uint8_t calc_crc = crc8(check_buf, 2 + len);

                if (calc_crc == rx_crc) {
                    bool is_end_block = (funDigitalRead(PD0) == FUN_LOW);

                    if (!is_end_block) {
                        // ACTION BLOCK BEHAVIOR:
                        // Assign self index in sequence
                        g_my_index = count + 1;

                        // Append stored [action_id, param_val]
                        rx_buf[len]     = g_action_id;
                        rx_buf[len + 1] = g_param_val;
                        uint8_t new_len   = len + 2;
                        uint8_t new_count = count + 1;

                        // Recompute CRC-8
                        check_buf[0] = new_len;
                        check_buf[1] = new_count;
                        for (uint8_t i = 0; i < new_len; i++) check_buf[2 + i] = rx_buf[i];
                        uint8_t new_crc = crc8(check_buf, 2 + new_len);

                        // Transmit modified frame downstream
                        uart_tx(0xAA);
                        uart_tx(new_len);
                        uart_tx(new_count);
                        for (uint8_t i = 0; i < new_len; i++) uart_tx(rx_buf[i]);
                        uart_tx(new_crc);
                        uart_tx(0x55);

                        // Ping LED amber briefly
                        ws2812_set(60, 40, 0);
                        Delay_Ms(50);
                        set_action_idle_color();
                    } else {
                        // SMART END BLOCK BEHAVIOR:
                        // Loop packet back onto Pin 4 return rail
                        uart_tx(0xAA);
                        uart_tx(len);
                        uart_tx(count);
                        for (uint8_t i = 0; i < len; i++) uart_tx(rx_buf[i]);
                        uart_tx(rx_crc);
                        uart_tx(0x55);

                        // Glow green to signal valid termination
                        ws2812_set(0, 150, 20);
                        Delay_Ms(300);
                        ws2812_set(0, 40, 10);
                    }
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
        }

        // ----------------------------------------------------------------------
        // PROTOCOL 3: STEP EXECUTION BROADCAST (0xBB)
        // [ 0xBB, ActiveStep, TotalSteps, CRC8, 0x55 ]
        // ----------------------------------------------------------------------
        else if (header == 0xBB) {
            funDigitalWrite(PD4, FUN_HIGH);
            uint8_t active_step = 0, total_steps = 0, rx_crc = 0, footer = 0;
            if (uart_rx_timeout(&active_step, 10000) &&
                uart_rx_timeout(&total_steps, 10000) &&
                uart_rx_timeout(&rx_crc, 10000) &&
                uart_rx_timeout(&footer, 10000)) {
                
                uint8_t check[2] = { active_step, total_steps };
                if (crc8(check, 2) == rx_crc && footer == 0x55) {
                    if (active_step == 0xFF) {
                        // Program Complete: Celebration Rainbow Sparkle!
                        for (int k = 0; k < 3; k++) {
                            ws2812_set(120, 0, 0);   Delay_Ms(80);
                            ws2812_set(120, 60, 0);  Delay_Ms(80);
                            ws2812_set(120, 120, 0); Delay_Ms(80);
                            ws2812_set(0, 120, 0);   Delay_Ms(80);
                            ws2812_set(0, 0, 120);   Delay_Ms(80);
                            ws2812_set(60, 0, 120);  Delay_Ms(80);
                        }
                        set_action_idle_color();
                    } else if (active_step == g_my_index && g_my_index > 0) {
                        // THIS BLOCK IS CURRENTLY EXECUTING: Glow Bright Green!
                        ws2812_set(0, 255, 0);
                    } else {
                        // OTHER BLOCKS: Dim Action Idle Color
                        set_action_idle_color();
                    }
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
        }
    }
}
