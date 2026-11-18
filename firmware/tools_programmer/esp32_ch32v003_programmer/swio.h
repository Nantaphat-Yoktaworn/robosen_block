#pragma once

#include <Arduino.h>

// Classic ESP32 wires GPIO6-11 to internal SPI flash, so use GPIO18 there;
// ESP32-S2/S3 keep GPIO10. A physical 3.3 V pull-up is required on SWIO.
#if defined(CONFIG_IDF_TARGET_ESP32)
constexpr uint8_t SWIO_PIN = 18;
#else
constexpr uint8_t SWIO_PIN = 10;
#endif

enum class SwioBitResult : uint8_t {
  Zero,
  One,
  Timeout,
};

bool swioInit();

// CNLohr ESP32-S2 startup state: actively drive SWIO high for 5 ms.
void swioSynchronize();

// A non-critical diagnostic measurement of the exact upstream delay loop.
uint32_t swioMeasureUpstreamT1Cycles();

void IRAM_ATTR swioDriveLow();
void IRAM_ATTR swioDriveHigh();
void IRAM_ATTR swioRelease();
void IRAM_ATTR swioWriteBit(bool value);
SwioBitResult IRAM_ATTR swioReadBit();
