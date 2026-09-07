/*
 * Robosen Physical Modular Block System - Smart End Block Firmware
 * Target: WCH CH32V003F4P6 (32-bit RISC-V @ 24MHz)
 * 
 * Physical Role:
 *   Terminal End Cap of the tangible block chain.
 *   - Closes the 4-pin physical bus.
 *   - Verifies incoming CRC-8 of compiled action sequence.
 *   - Drives the active Pin 4 Return Rail back to the Master Block.
 *   - Provides visual "Chain Ready" emerald green confirmation for children.
 * 
 * Pin Allocations:
 *   PD6 (Pin 13 / RX) - USART1_RX: Incoming Chain Data (from last Action Block Pin 3 Out)
 *   PD5 (Pin 9  / TX) - USART1_TX: Active Return Rail Driver (loops back into Pin 4 Return Rail)
 *   PA2 (Pin 3)       - WS2812B RGB LED Data Line (DIN)
 *   PD4 (Pin 8)       - Onboard Activity LED
 *   PC0 (Pin 15)      - Alternate Onboard Activity LED
 *   PD1 (Pin 4)       - SWIO 1-wire programming line
 * 
 * Supported Protocols:
 *   1. Config Port Protocol (0xCF):
 *      Announces itself as Token 0xEE ("Smart End Terminator").
 *      When docked: Master displays [0xEE] Smart End Terminator.
 * 
 *   2. Run Chain Discovery & Assembly (0xAA Phase 1):
 *      Receives compiled program: [0xAA, Len, Count, (ActionID, ParamVal)*, CRC8, 0x55]
 *      Validates CRC-8.
 *      Active Line Loopback: Transmits identical packet onto Pin 4 Return Rail.
 *      Visual Feedback: Pulses Vivid Emerald Green (0, 255, 30).
 * 
 *   3. Run Chain Execution Step Tracking (0xBB Phase 2):
 *      Monitors broadcast execution: [0xBB, ActiveStep, TotalSteps, CRC8, 0x55]
 *      ActiveStep == 0xFF: Program complete -> Plays Rainbow Victory Sparkle!
 *      Otherwise: Steady Soft Emerald Green (0, 45, 10).
 */

#include "ch32fun.h"
#include <stdint.h>
#include <stdbool.h>

#define END_BLOCK_TOKEN 0xEE

// ==============================================================================
// 1. CRC-8 (Polynomial: 0x07, Init: 0x00)
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
// 2. WS2812B RGB LED DRIVER (PA2 @ 24MHz)
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

void set_end_idle_color() {
    // Soft, friendly emerald green indicating ready termination
    ws2812_set(0, 45, 10);
}

void rainbow_victory_sparkle() {
    for (int k = 0; k < 3; k++) {
        ws2812_set(120, 0, 0);   Delay_Ms(70);
        ws2812_set(120, 60, 0);  Delay_Ms(70);
        ws2812_set(120, 120, 0); Delay_Ms(70);
        ws2812_set(0, 120, 0);   Delay_Ms(70);
        ws2812_set(0, 0, 120);   Delay_Ms(70);
        ws2812_set(60, 0, 120);  Delay_Ms(70);
    }
    set_end_idle_color();
}

// ==============================================================================
// 3. UART DRIVER (PD5 = TX Out onto Pin 4, PD6 = RX In from Chain @ 115200 Baud)
// ==============================================================================
void uart_init() {
    RCC->APB2PCENR |= RCC_APB2Periph_AFIO | RCC_APB2Periph_GPIOD | RCC_APB2Periph_USART1;

    // Explicitly lock USART1 remap to 0b00 (PD5=TX, PD6=RX)
    AFIO->PCFR1 &= ~(AFIO_PCFR1_USART1_REMAP | AFIO_PCFR1_USART1_REMAP_1);

    // PD5: USART1_TX (Alternate Function Push-Pull, 10MHz)
    funPinMode(PD5, GPIO_CFGLR_OUT_10Mhz_AF_PP);

    // PD6: USART1_RX (Input with Pull-Up)
    funPinMode(PD6, GPIO_CFGLR_IN_PUPD);
    funDigitalWrite(PD6, FUN_HIGH);

    // 115200 Baud from 24MHz system clock (BRR = 208)
    USART1->BRR = ((FUNCONF_SYSTEM_CORE_CLOCK) + (115200 / 2)) / 115200;
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
    volatile uint32_t count = timeout_us * 8;
    while (!uart_rx_available()) {
        if (--count == 0) return false;
    }
    *b = (uint8_t)(USART1->DATAR & 0xFF);
    return true;
}

// ==============================================================================
// 4. MAIN SYSTEM ENTRY & STATE MACHINE
// ==============================================================================
int main() {
    SystemInit();
    funGpioInitAll();

    // Enable RCC for GPIOA, GPIOC, GPIOD
    RCC->APB2PCENR |= RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC | RCC_APB2Periph_GPIOD;

    // Setup PA2 for WS2812B
    funPinMode(PA2, GPIO_CFGLR_OUT_10Mhz_PP);

    // Setup PD4 & PC0 for Activity Indicator (Output PP)
    funPinMode(PD4, GPIO_CFGLR_OUT_10Mhz_PP);
    funPinMode(PC0, GPIO_CFGLR_OUT_10Mhz_PP);
    funDigitalWrite(PD4, FUN_LOW);
    funDigitalWrite(PC0, FUN_LOW);

    // Init UART at 115200
    uart_init();

    // Boot Indication: Double Emerald Flash
    ws2812_set(0, 180, 25);
    Delay_Ms(150);
    ws2812_set(0, 0, 0);
    Delay_Ms(100);
    ws2812_set(0, 180, 25);
    Delay_Ms(150);
    set_end_idle_color();

    uint8_t rx_buf[64];
    uint32_t last_heartbeat = SysTick->CNT;
    uint8_t hb_phase = 0;

    while (1) {
        // Non-blocking 500ms Heartbeat:
        // Toggles onboard LEDs (PD4 / PC0) as a visual liveness indicator.
        // Return Rail TX remains completely silent until queried by Master or looping back 0xAA frames.
        uint32_t now = SysTick->CNT;
        if (TimeElapsed32u(now, last_heartbeat) >= Ticks_from_Ms(500)) {
            last_heartbeat = now;
            hb_phase++;
            funDigitalWrite(PD4, (hb_phase & 1) ? FUN_HIGH : FUN_LOW);
            funDigitalWrite(PC0, (hb_phase & 1) ? FUN_HIGH : FUN_LOW);
        }

        if (!uart_rx_available()) continue;

        uint8_t header = uart_rx_byte();

        // ----------------------------------------------------------------------
        // PROTOCOL 1: CONFIG DOCK (0xCF)
        // When docked: Master queries stored action. End Block replies with 0xEE.
        // ----------------------------------------------------------------------
        if (header == 0xCF) {
            funDigitalWrite(PD4, FUN_HIGH);
            funDigitalWrite(PC0, FUN_HIGH);
            uint8_t cmd = 0;
            if (!uart_rx_timeout(&cmd, 10000)) {
                funDigitalWrite(PD4, FUN_LOW);
                funDigitalWrite(PC0, FUN_LOW);
                continue;
            }

            // Query / Read Current Stored Action Config
            if (cmd == 0x01 || cmd == 0x00) {
                uint8_t rx_crc = 0, footer = 0;
                if (uart_rx_timeout(&rx_crc, 10000) && uart_rx_timeout(&footer, 10000)) {
                    uint8_t q_payload[1] = { cmd };
                    uint8_t exp_crc = crc8(q_payload, 1);
                    if (exp_crc == rx_crc && footer == 0x55) {
                        uint8_t resp_payload[3] = { 0x81, END_BLOCK_TOKEN, 0x00 };
                        uint8_t resp_crc = crc8(resp_payload, 3);
                        uart_tx(0xCF);
                        uart_tx(0x81);
                        uart_tx(END_BLOCK_TOKEN);
                        uart_tx(0x00);
                        uart_tx(resp_crc);
                        uart_tx(0x55);
                    }
                }
            }
            // If Master attempts to flash an End Block, send ACK to confirm dock intact
            else if (cmd == 0x02) {
                uint8_t act = 0, par = 0, rx_crc = 0, footer = 0;
                if (uart_rx_timeout(&act, 10000) &&
                    uart_rx_timeout(&par, 10000) &&
                    uart_rx_timeout(&rx_crc, 10000) &&
                    uart_rx_timeout(&footer, 10000)) {
                    
                    uint8_t payload[3] = { cmd, act, par };
                    uint8_t calc_crc = crc8(payload, 3);
                    if (calc_crc == rx_crc && footer == 0x55) {
                        uint8_t ack_payload[1] = { 0x06 };
                        uint8_t ack_crc = crc8(ack_payload, 1);
                        uart_tx(0xCF);
                        uart_tx(0x06);
                        uart_tx(ack_crc);
                        uart_tx(0x55);

                        // Emerald Green confirmation pulse
                        ws2812_set(0, 255, 40);
                        Delay_Ms(300);
                        set_end_idle_color();
                    }
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
            funDigitalWrite(PC0, FUN_LOW);
        }

        // ----------------------------------------------------------------------
        // PROTOCOL 2: RUN CHAIN DISCOVERY (0xAA)
        // [ 0xAA, Len, Count, (ActionID, ParamVal)*, CRC8, 0x55 ]
        // SMART END BLOCK: Validates CRC, active loopback onto Pin 4 Return Rail!
        // ----------------------------------------------------------------------
        else if (header == 0xAA) {
            funDigitalWrite(PD4, FUN_HIGH);
            funDigitalWrite(PC0, FUN_HIGH);
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
                // Verify incoming CRC-8
                uint8_t check_buf[64];
                check_buf[0] = len;
                check_buf[1] = count;
                for (uint8_t i = 0; i < len; i++) check_buf[2 + i] = rx_buf[i];
                uint8_t calc_crc = crc8(check_buf, 2 + len);

                if (calc_crc == rx_crc) {
                    // SMART END BLOCK ACTIVE LINE DRIVER LOOPBACK:
                    // Loop verified packet out onto Pin 4 Return Rail directly to Master!
                    uart_tx(0xAA);
                    uart_tx(len);
                    uart_tx(count);
                    for (uint8_t i = 0; i < len; i++) uart_tx(rx_buf[i]);
                    uart_tx(rx_crc);
                    uart_tx(0x55);

                    // Visual Feedback: Vivid Emerald Green Success Glow
                    ws2812_set(0, 240, 30);
                    Delay_Ms(350);
                    set_end_idle_color();
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
            funDigitalWrite(PC0, FUN_LOW);
        }

        // ----------------------------------------------------------------------
        // PROTOCOL 3: STEP EXECUTION BROADCAST (0xBB)
        // [ 0xBB, ActiveStep, TotalSteps, CRC8, 0x55 ]
        // ----------------------------------------------------------------------
        else if (header == 0xBB) {
            funDigitalWrite(PD4, FUN_HIGH);
            funDigitalWrite(PC0, FUN_HIGH);
            uint8_t active_step = 0, total_steps = 0, rx_crc = 0, footer = 0;
            if (uart_rx_timeout(&active_step, 10000) &&
                uart_rx_timeout(&total_steps, 10000) &&
                uart_rx_timeout(&rx_crc, 10000) &&
                uart_rx_timeout(&footer, 10000)) {
                
                uint8_t check[2] = { active_step, total_steps };
                if (crc8(check, 2) == rx_crc && footer == 0x55) {
                    if (active_step == 0xFF) {
                        // Program Complete: Rainbow Celebration Sparkle!
                        rainbow_victory_sparkle();
                    } else {
                        // Execution ongoing: steady calm green terminator glow
                        set_end_idle_color();
                    }
                }
            }
            funDigitalWrite(PD4, FUN_LOW);
            funDigitalWrite(PC0, FUN_LOW);
        }
    }
}
