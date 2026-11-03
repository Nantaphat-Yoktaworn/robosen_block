/*
 * Arduino Uno R3 as CH32V003 SWIO Programmer (Ardulink)
 * 
 * Based on BlueSyncLine / Ardulink (arduino-ch32v003-swio).
 * Turns an Arduino Uno R3 (ATmega328P @ 16MHz) into a 1-wire SWIO programmer
 * for WCH CH32V003 microcontrollers.
 *
 * Hardware Wiring:
 *   Arduino Uno Pin 8 (PB0)  --> CH32V003 Pin PD1 (SWIO)
 *                                (A 1k series resistor is recommended to avoid bus contention)
 *   Arduino Uno Pin 9 (PB1)  --> Optional Target Power switch (or connect V directly to 5V/3.3V)
 *   Arduino Uno 5V (or 3.3V) --> CH32V003 Pin V (VCC)
 *   Arduino Uno GND          --> CH32V003 Pin G (GND)
 *
 * Flashing with minichlink (ch32v003fun):
 *   minichlink -a COMx -w your_firmware.bin 0x08000000
 *   (Replace COMx with your Arduino Uno COM port)
 */

#include <avr/io.h>
#include <util/delay.h>
#include <stdint.h>

#define TARGET_POWER_PORT  PORTB
#define TARGET_POWER_DDR   DDRB
#define TARGET_POWER_BIT   1  // Arduino Pin 9 (PB1)

#define SWIO_DDR  DDRB
#define SWIO_PORT PORTB
#define SWIO_PIN  PINB
#define SWIO_BIT  0  // Arduino Pin 8 (PB0)

void target_power(int x) {
    if (x)
        TARGET_POWER_PORT |= _BV(TARGET_POWER_BIT);
    else
        TARGET_POWER_PORT &= ~_BV(TARGET_POWER_BIT);
}

#define PROTOCOL_START     '!'
#define PROTOCOL_ACK       '+'
#define PROTOCOL_TEST      '?'
#define PROTOCOL_POWER_ON  'p'
#define PROTOCOL_POWER_OFF 'P'
#define PROTOCOL_WRITE_REG 'w'
#define PROTOCOL_READ_REG  'r'

// Cycle-accurate bitbang routines for 16MHz ATmega328P
static inline void swio_send_one() {
    SWIO_DDR |= _BV(SWIO_BIT);
    SWIO_PORT &= ~_BV(SWIO_BIT);
    __asm__ __volatile__("nop\n\tnop\n\t");
    SWIO_PORT |= _BV(SWIO_BIT);
    SWIO_DDR &= ~_BV(SWIO_BIT);
}

static inline void swio_send_zero() {
    SWIO_DDR |= _BV(SWIO_BIT);
    SWIO_PORT &= ~_BV(SWIO_BIT);
    __asm__ __volatile__(
        "nop\n\tnop\n\t"
        "nop\n\tnop\n\t"
        "nop\n\tnop\n\t"
        "nop\n\tnop\n\t"
        "nop\n\tnop\n\t"
        "nop\n\tnop\n\t"
    );
    SWIO_PORT |= _BV(SWIO_BIT);
    SWIO_DDR &= ~_BV(SWIO_BIT);
}

static inline char swio_recv_bit() {
    char x;
    SWIO_DDR |= _BV(SWIO_BIT);
    SWIO_PORT &= ~_BV(SWIO_BIT);
    SWIO_PORT |= _BV(SWIO_BIT);  // Precharge when the line is floating
    SWIO_DDR &= ~_BV(SWIO_BIT);
    __asm__ __volatile__("nop\n\tnop\n\t");
    __asm__ __volatile__("nop\n\tnop\n\t");
    x = SWIO_PIN;
    while (!(SWIO_PIN & _BV(SWIO_BIT)))
        ;
    return x & _BV(SWIO_BIT);
}

void swio_write_reg(uint8_t addr, uint32_t val) {
    char i;
    swio_send_one();  // Start bit
    for (i = 0; i < 7; i++) {
        if (addr & 0x40)
            swio_send_one();
        else
            swio_send_zero();
        addr <<= 1;
    }
    swio_send_one();  // Data start bit
    for (i = 0; i < 32; i++) {
        if (val & 0x80000000)
            swio_send_one();
        else
            swio_send_zero();
        val <<= 1;
    }
    _delay_us(10);  // Stop bit
}

uint32_t swio_read_reg(uint8_t addr) {
    char i;
    uint32_t x = 0;
    swio_send_one();  // Start bit
    for (i = 0; i < 7; i++) {
        if (addr & 0x40)
            swio_send_one();
        else
            swio_send_zero();
        addr <<= 1;
    }
    swio_send_zero();  // Data start bit (read request)
    for (i = 0; i < 32; i++) {
        x <<= 1;
        if (swio_recv_bit())
            x |= 1;
    }
    _delay_us(10);  // Stop bit
    return x;
}

void swio_init() {
    SWIO_PORT |= _BV(SWIO_BIT);
    SWIO_DDR |= _BV(SWIO_BIT);
    _delay_ms(5);
    SWIO_PORT &= ~_BV(SWIO_BIT);
    _delay_ms(20);
    SWIO_PORT |= _BV(SWIO_BIT);
    SWIO_DDR &= ~_BV(SWIO_BIT);
}

// 115200 baud direct hardware UART routines (2X speed, error < 2.1%)
static inline void uart_init_fast() {
    UCSR0A |= _BV(U2X0);
    UBRR0L = 16;
    UCSR0B |= _BV(TXEN0) | _BV(RXEN0);
}

static inline void uart_putchar(char c) {
    while (!(UCSR0A & _BV(UDRE0)))
        ;
    UDR0 = c;
}

static inline uint8_t uart_getchar() {
    while (!(UCSR0A & _BV(RXC0)))
        ;
    return UDR0;
}

void setup() {
    // Disable interrupts so timer interrupts (millis/micros) do not jitter SWIO timing
    cli();
    TARGET_POWER_DDR |= _BV(TARGET_POWER_BIT);
    uart_init_fast();
    swio_init();
    uart_putchar(PROTOCOL_START);  // Send '!' ready signal
}

void loop() {
    uint8_t reg;
    uint32_t val;
    uint8_t cmd = uart_getchar();
    switch (cmd) {
        case PROTOCOL_TEST:
            uart_putchar(PROTOCOL_ACK);
            break;
        case PROTOCOL_POWER_ON:
            target_power(1);
            uart_putchar(PROTOCOL_ACK);
            break;
        case PROTOCOL_POWER_OFF:
            target_power(0);
            uart_putchar(PROTOCOL_ACK);
            break;
        case PROTOCOL_WRITE_REG:
            reg = uart_getchar();
            for (int i = 0; i < 4; i++) {
                ((uint8_t*)&val)[i] = uart_getchar();
            }
            swio_write_reg(reg, val);
            uart_putchar(PROTOCOL_ACK);
            break;
        case PROTOCOL_READ_REG:
            reg = uart_getchar();
            val = swio_read_reg(reg);
            for (int i = 0; i < 4; i++) {
                uart_putchar(((uint8_t*)&val)[i]);
            }
            break;
    }
}
