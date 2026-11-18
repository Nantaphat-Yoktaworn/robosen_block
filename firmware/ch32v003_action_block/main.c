/*
 * Robosen Physical Modular Block System - Unified Action Block Firmware
 * Target: WCH CH32V003F4P6 (32-bit RISC-V @ 24MHz)
 * 
 * Pin Allocations:
 *   PD6 (Pin 13) - USART1_RX: Upstream Chain RX / Config Dock In
 *   PD5 (Pin 9)  - USART1_TX: Downstream Chain TX / Config Dock ACK
 *   PA2 (Pin 3)  - WS2812B RGB LED Data Line (DIN)
 *   PD0 (Pin 15 on DIP) - /RETURN_BUS / Dynamic Role:
 *                          Action Block: High-Z Floating Input (passive pass-through)
 *                          Smart End Block (0xEE): Active Return Rail Driver (loops 0xAA onto Pin 4)
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

static uint8_t g_action_id = 0x01; // Default: Walk Forward
static uint8_t g_param_val = 0x01; // Default: 1 Step
static uint8_t g_my_index  = 0;    // Assigned dynamically during Phase 1

void flash_unlock() {
    FLASH->KEYR = FLASH_KEY1;
    FLASH->KEYR = FLASH_KEY2;
    FLASH->MODEKEYR = FLASH_KEY1;
    FLASH->MODEKEYR = FLASH_KEY2;
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
    while (FLASH->STATR & FLASH_STATR_BSY);

    volatile uint32_t *ptr = (volatile uint32_t *)FLASH_CFG_ADDR;

    // 1. Erase 64-byte Page
    FLASH->CTLR = FLASH_CTLR_PAGE_ER;
    FLASH->ADDR = (uint32_t)ptr;
    FLASH->CTLR = FLASH_CTLR_STRT | FLASH_CTLR_PAGE_ER;
    while (FLASH->STATR & FLASH_STATR_BSY);

    // 2. Clear buffer and prepare for page programming
    FLASH->CTLR = FLASH_CTLR_PAGE_PG;
    FLASH->CTLR = FLASH_CTLR_BUF_RST | FLASH_CTLR_PAGE_PG;
    FLASH->ADDR = (uint32_t)ptr;
    while (FLASH->STATR & FLASH_STATR_BSY);

    // 3. Write 16 words (64 bytes) into row buffer with BUF_LOAD
    for (int i = 0; i < 16; i++) {
        if (i == 0) {
            ptr[i] = CFG_MAGIC;
        } else if (i == 1) {
            ptr[i] = ((uint32_t)param << 8) | (uint32_t)action;
        } else {
            ptr[i] = 0xFFFFFFFFUL;
        }
        FLASH->CTLR = FLASH_CTLR_PAGE_PG | FLASH_CTLR_BUF_LOAD;
        while (FLASH->STATR & FLASH_STATR_BSY);
    }

    // 4. Trigger actual write to flash
    FLASH->CTLR = FLASH_CTLR_PAGE_PG | FLASH_CTLR_STRT;
    while (FLASH->STATR & FLASH_STATR_BSY);

    // 5. Lock flash controller
    FLASH->CTLR |= FLASH_CTLR_LOCK;
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
        case 0xEE: // Smart End Block - Soft Emerald Green
            ws2812_set(0, 45, 10);
            break;
        default:   // Soft White
            ws2812_set(25, 25, 25);
            break;
    }
}

// ==============================================================================
// 4. UART DRIVER (PD5 = TX, PD6 = RX @ 115200 Baud; PD0 = Return Rail TX)
// ==============================================================================
void uart_init() {
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOD | RCC_APB2Periph_USART1;

    // Explicitly ensure USART1 remap is set to default 0b00 (PD5=TX, PD6=RX)
    AFIO->PCFR1 &= ~(AFIO_PCFR1_USART1_REMAP | AFIO_PCFR1_USART1_REMAP_1);

    // PD5: USART1_TX (Alternate Function Push-Pull, 10MHz)
    funPinMode(PD5, GPIO_CFGLR_OUT_10Mhz_AF_PP);

    // PD6: USART1_RX (Input with Pull-Up)
    funPinMode(PD6, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(PD6, FUN_HIGH);

    // 115200 Baud BRR calculation from system core clock
    USART1->BRR = ((FUNCONF_SYSTEM_CORE_CLOCK) + (115200 / 2)) / 115200;
    USART1->CTLR1 = USART_CTLR1_TE | USART_CTLR1_RE | USART_CTLR1_UE;
}

static inline void uart_tx(uint8_t b) {
    while (!(USART1->STATR & USART_STATR_TXE));
    USART1->DATAR = b;
}

#define PD0_BIT_TICKS      (FUNCONF_SYSTEM_CORE_CLOCK / 115200UL)
#define PD0_HALF_BIT_TICKS (PD0_BIT_TICKS / 2U)

void uart_tx_pd0(uint8_t b) {
    __disable_irq();
    uint32_t t0 = SysTick->CNT;
    // Start bit: LOW
    GPIOD->BCR = (1 << 0);
    while ((uint32_t)(SysTick->CNT - t0) < PD0_BIT_TICKS);

    // 8 Data bits (LSB first)
    for (uint8_t i = 0; i < 8; i++) {
        if (b & (1U << i)) {
            GPIOD->BSHR = (1 << 0);
        } else {
            GPIOD->BCR = (1 << 0);
        }
        uint32_t next_edge = (uint32_t)(i + 2U) * PD0_BIT_TICKS;
        while ((uint32_t)(SysTick->CNT - t0) < next_edge);
    }

    // Stop bit: HIGH
    GPIOD->BSHR = (1 << 0);
    while ((uint32_t)(SysTick->CNT - t0) < (10U * PD0_BIT_TICKS));
    __enable_irq();
}

static inline void pd0_set_idle() {
    funPinMode(PD0, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(PD0, FUN_HIGH);
}

static bool pd0_rx_byte_at_start(uint32_t t0, uint8_t *out) {
    while ((uint32_t)(SysTick->CNT - t0) < PD0_HALF_BIT_TICKS);
    if (GPIOD->INDR & (1 << 0)) {
        return false; // Glitch on start bit
    }
    uint8_t val = 0;
    for (uint8_t i = 0; i < 8; i++) {
        uint32_t target = PD0_HALF_BIT_TICKS + (uint32_t)(i + 1U) * PD0_BIT_TICKS;
        while ((uint32_t)(SysTick->CNT - t0) < target);
        if (GPIOD->INDR & (1 << 0)) {
            val |= (1U << i);
        }
    }
    while ((uint32_t)(SysTick->CNT - t0) < (PD0_HALF_BIT_TICKS + 9U * PD0_BIT_TICKS - 32U));
    if (!(GPIOD->INDR & (1 << 0))) {
        return false; // Missing stop bit
    }
    *out = val;
    return true;
}

static bool pd0_rx_next_byte(uint8_t *out, uint32_t timeout_ticks) {
    uint32_t wait_start = SysTick->CNT;
    while (GPIOD->INDR & (1 << 0)) {
        if ((uint32_t)(SysTick->CNT - wait_start) >= timeout_ticks) {
            return false;
        }
    }
    uint32_t t0 = SysTick->CNT;
    return pd0_rx_byte_at_start(t0, out);
}

static inline bool uart_rx_available() {
    return (USART1->STATR & USART_STATR_RXNE) != 0;
}

static inline uint8_t uart_rx_byte() {
    while (!uart_rx_available());
    return (uint8_t)(USART1->DATAR & 0xFF);
}

bool uart_rx_timeout(uint8_t *b, uint32_t timeout_us) {
    volatile uint32_t count = timeout_us * 8;
    while (!uart_rx_available()) {
        if (--count == 0) return false;
    }
    *b = (uint8_t)(USART1->DATAR & 0xFF);
    return true;
}

// ==============================================================================
// 5. MAIN SYSTEM LOOP & PROTOCOL HANDLERS
// ==============================================================================
static void handle_cf_query(uint8_t cmd, uint8_t rx_crc, uint8_t footer) {
    uint8_t q_payload[1] = { cmd };
    uint8_t exp_crc = crc8(q_payload, 1);
    if (exp_crc == rx_crc && footer == 0x55) {
        uint8_t resp_payload[3] = { 0x81, g_action_id, g_param_val };
        uint8_t resp_crc = crc8(resp_payload, 3);
        uart_tx(0xCF);
        uart_tx(0x81);
        uart_tx(g_action_id);
        uart_tx(g_param_val);
        uart_tx(resp_crc);
        uart_tx(0x55);
    }
}

static void handle_cf_write(uint8_t cmd, uint8_t act, uint8_t par, uint8_t rx_crc, uint8_t footer) {
    uint8_t payload[3] = { cmd, act, par };
    uint8_t calc_crc = crc8(payload, 3);

    if (calc_crc == rx_crc && footer == 0x55) {
        save_config(act, par);
        pd0_set_idle();

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

static void handle_pd0_rx() {
    uint32_t t0 = SysTick->CNT;
    __disable_irq();
    uint8_t header = 0;
    bool ok = pd0_rx_byte_at_start(t0, &header);
    if (!ok || header != 0xCF) {
        __enable_irq();
        if (ok && header == 0xAA) {
            // Wait for end of 0xAA return-bus frame (line continuously HIGH > ~140us)
            uint32_t idle_since = SysTick->CNT;
            while (!uart_rx_available()) {
                if (!(GPIOD->INDR & (1 << 0))) {
                    idle_since = SysTick->CNT;
                } else if ((uint32_t)(SysTick->CNT - idle_since) >= (PD0_BIT_TICKS * 16U)) {
                    break;
                }
            }
        }
        return;
    }

    uint8_t cmd = 0;
    if (!pd0_rx_next_byte(&cmd, PD0_BIT_TICKS * 40U)) {
        __enable_irq();
        return;
    }

    if (cmd == 0x01 || cmd == 0x00) {
        uint8_t rx_crc = 0, footer = 0;
        bool got = pd0_rx_next_byte(&rx_crc, PD0_BIT_TICKS * 40U) &&
                   pd0_rx_next_byte(&footer, PD0_BIT_TICKS * 40U);
        __enable_irq();
        if (got) {
            funDigitalWrite(PD4, FUN_HIGH);
            handle_cf_query(cmd, rx_crc, footer);
            funDigitalWrite(PD4, FUN_LOW);
        }
    } else if (cmd == 0x02) {
        uint8_t act = 0, par = 0, rx_crc = 0, footer = 0;
        bool got = pd0_rx_next_byte(&act, PD0_BIT_TICKS * 40U) &&
                   pd0_rx_next_byte(&par, PD0_BIT_TICKS * 40U) &&
                   pd0_rx_next_byte(&rx_crc, PD0_BIT_TICKS * 40U) &&
                   pd0_rx_next_byte(&footer, PD0_BIT_TICKS * 40U);
        __enable_irq();
        if (got) {
            funDigitalWrite(PD4, FUN_HIGH);
            handle_cf_write(cmd, act, par, rx_crc, footer);
            funDigitalWrite(PD4, FUN_LOW);
        }
    } else {
        __enable_irq();
    }
}

int main() {
    SystemInit();
    funGpioInitAll();

    // Enable RCC for GPIOA, GPIOC, GPIOD
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC | RCC_APB2Periph_GPIOD;

    // Setup PA2 for WS2812B
    funPinMode(PA2, GPIO_CFGLR_OUT_10Mhz_PP);

    // Setup PD4 & PC0 for Activity Indicator
    funPinMode(PD4, GPIO_CFGLR_OUT_10Mhz_PP);
    funPinMode(PC0, GPIO_CFGLR_OUT_10Mhz_PP);
    funDigitalWrite(PD4, FUN_LOW);
    funDigitalWrite(PC0, FUN_LOW);

    // Load saved configuration from flash
    load_config();

    // Keep PD0 high-impedance input with pull-up at idle so OUT Config Dock (GPIO17->PD0)
    // never contends even when configured as 0xEE; 0xAA loopback temporarily drives PD0 PP.
    pd0_set_idle();

    // Init UART at 115200
    uart_init();

    // Power-on indication: Emerald green flash, then idle color
    ws2812_set(0, 100, 30);
    Delay_Ms(300);
    set_action_idle_color();

    uint8_t rx_buf[64];
    uint32_t last_heartbeat = SysTick->CNT;
    uint8_t hb_phase = 0;
    bool prev_pd0 = true;

    while (1) {
        // Non-blocking 500ms Heartbeat:
        // Toggles onboard LED (PD4 / PC0) as a visual liveness indicator.
        // UART TX remains completely silent until queried by Master or relaying Run Chain frames.
        uint32_t now = SysTick->CNT;
        if (TimeElapsed32u(now, last_heartbeat) >= Ticks_from_Ms(500)) {
            last_heartbeat = now;
            hb_phase++;
            funDigitalWrite(PD4, (hb_phase & 1) ? FUN_HIGH : FUN_LOW);
            funDigitalWrite(PC0, (hb_phase & 1) ? FUN_HIGH : FUN_LOW);
        }

        if (!uart_rx_available()) {
            bool cur_pd0 = (GPIOD->INDR & (1 << 0)) != 0;
            if (prev_pd0 && !cur_pd0) {
                handle_pd0_rx();
                cur_pd0 = (GPIOD->INDR & (1 << 0)) != 0;
            }
            prev_pd0 = cur_pd0;
            continue;
        }

        uint8_t header = uart_rx_byte();

        // ----------------------------------------------------------------------
        // PROTOCOL 1: CONFIG DOCK (0xCF)
        // Read:  Master -> Block: [ 0xCF, 0x01, CRC8, 0x55 ]
        //        Block  -> Master: [ 0xCF, 0x81, ACTION_ID, PARAM_VAL, CRC8, 0x55 ]
        // Write: Master -> Block: [ 0xCF, 0x02, ACTION_ID, PARAM_VAL, CRC8, 0x55 ]
        //        Block  -> Master: [ 0xCF, 0x06, CRC8, 0x55 ] (ACK)
        // ----------------------------------------------------------------------
        if (header == 0xCF) {
            funDigitalWrite(PD4, FUN_HIGH);
            uint8_t cmd = 0;
            if (!uart_rx_timeout(&cmd, 10000)) {
                funDigitalWrite(PD4, FUN_LOW);
                continue;
            }

            // Subcommand 0x01 (or 0x00): Query / Read Current Stored Action Config
            if (cmd == 0x01 || cmd == 0x00) {
                uint8_t rx_crc = 0, footer = 0;
                if (uart_rx_timeout(&rx_crc, 10000) && uart_rx_timeout(&footer, 10000)) {
                    handle_cf_query(cmd, rx_crc, footer);
                }
            }
            // Subcommand 0x02: Write New Configuration to Non-Volatile Flash
            else if (cmd == 0x02) {
                uint8_t act = 0, par = 0, rx_crc = 0, footer = 0;
                if (uart_rx_timeout(&act, 10000) &&
                    uart_rx_timeout(&par, 10000) &&
                    uart_rx_timeout(&rx_crc, 10000) &&
                    uart_rx_timeout(&footer, 10000)) {
                    handle_cf_write(cmd, act, par, rx_crc, footer);
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
                    bool is_end_block = (g_action_id == 0xEE) || (funDigitalRead(PD0) == FUN_LOW);

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
                        // Loop packet back onto Pin 4 return rail (temporarily drive PD0 PP, then release to idle)
                        funPinMode(PD0, GPIO_CFGLR_OUT_10Mhz_PP);
                        funDigitalWrite(PD0, FUN_HIGH);
                        Delay_Us(20);

                        uart_tx(0xAA);
                        uart_tx_pd0(0xAA);
                        uart_tx(len);
                        uart_tx_pd0(len);
                        uart_tx(count);
                        uart_tx_pd0(count);
                        for (uint8_t i = 0; i < len; i++) {
                            uart_tx(rx_buf[i]);
                            uart_tx_pd0(rx_buf[i]);
                        }
                        uart_tx(rx_crc);
                        uart_tx_pd0(rx_crc);
                        uart_tx(0x55);
                        uart_tx_pd0(0x55);

                        pd0_set_idle();

                        // Glow emerald green to signal valid termination
                        ws2812_set(0, 240, 30);
                        Delay_Ms(350);
                        set_action_idle_color();
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
                    // Forward 0xBB frame downstream to subsequent blocks in the chain
                    uart_tx(0xBB);
                    uart_tx(active_step);
                    uart_tx(total_steps);
                    uart_tx(rx_crc);
                    uart_tx(0x55);

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
