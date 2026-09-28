/*
 * ======================================================================================
 * STANDALONE E-INK / E-PAPER TEST SKETCH FOR ESP32-S3
 * ======================================================================================
 * 
 * Hardware Pin Mapping:
 * --------------------------------------------------------------------------------------
 *  E-Ink Label | Function       | ESP32-S3 GPIO | Note
 * --------------------------------------------------------------------------------------
 *  VCC         | Power          | 3V3           | Strictly 3.3V (NEVER CONNECT TO 5V!)
 *  GND         | Ground         | GND           | Common Ground
 *  SCL         | SPI Clock      | GPIO 21       | SCK
 *  SDA         | SPI Data In    | GPIO 38       | MOSI / DIN
 *  RES         | Reset          | GPIO 5        | Hardware Reset
 *  DC          | Data / Command | GPIO 6        | D/C
 *  CS          | Chip Select    | GPIO 7        | CS
 *  BUSY        | Busy Status    | GPIO 4        | Active status (can set -1 if stuck)
 * --------------------------------------------------------------------------------------
 * 
 * Required Libraries (Install via Arduino IDE Library Manager: Ctrl+Shift+I):
 *   1. "GxEPD2" by Jean-Marc Zingg
 *   2. "Adafruit GFX Library" by Adafruit
 * 
 * Arduino IDE Settings for ESP32-S3:
 *   - Board: "ESP32S3 Dev Module" (or "ESP32-S3-DevKitC-1")
 *   - USB CDC On Boot: "Enabled" (to view Serial output over USB)
 *   - Flash Size: "8MB" or "16MB" (depending on your board)
 *   - PSRAM: "OPI PSRAM" (if N16R8) or "Disabled"
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>

// ==============================================================================
// 1. PIN CONFIGURATION
// ==============================================================================
// If your screen freezes or gets stuck waiting for BUSY, set USE_BUSY_PIN to 0
#define USE_BUSY_PIN        1   // 1 = Use GPIO 4, 0 = Bypass BUSY (timed delays)

// Set to 1 to COMPLETELY SKIP the violent black/white blinking/flashing on startup!
// When enabled, it draws the initial screen using fast partial refresh (~700ms, zero flicker)
#define SKIP_BOOT_BLINKING  1   // 1 = No blinking at boot (smooth partial), 0 = Full refresh flash

#if USE_BUSY_PIN
  #define PIN_EPD_BUSY  4   // BUSY pin
#else
  #define PIN_EPD_BUSY -1   // Bypassed
#endif

#define PIN_EPD_RES     5   // Reset (RES)
#define PIN_EPD_DC      6   // Data / Command (DC)
#define PIN_EPD_CS      7   // Chip Select (CS)
#define PIN_EPD_SCL    21   // SPI Clock (SCL / SCK)
#define PIN_EPD_SDA    38   // SPI MOSI (SDA / DIN)

// Optional Onboard WS2812 LED on DevKitC-1
#ifndef RGB_BUILTIN
  #define RGB_BUILTIN 48
#endif

void setLED(uint8_t r, uint8_t g, uint8_t b) {
#ifdef RGB_BUILTIN
  rgbLedWrite(RGB_BUILTIN, r, g, b);
#endif
}

// ==============================================================================
// 2. DISPLAY DRIVER SELECTION (GxEPD2)
// Select the line matching your display model. Only ONE display line must be active!
// ==============================================================================

// [OPTION A] Confirmed Working Driver: DEPG0213BN (122x250, 727ms partial refresh)
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT> display(
  GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);

// [OPTION B] GDEH0213B74 (Incompatible with this panel hardware)
// GxEPD2_BW<GxEPD2_213_B74, GxEPD2_213_B74::HEIGHT> display(
//   GxEPD2_213_B74(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
// );

// [OPTION C] Waveshare 2.13" V2 (UC8151D / DEPG0213Bx)
// GxEPD2_BW<GxEPD2_213_flex, GxEPD2_213_flex::HEIGHT> display(
//   GxEPD2_213_flex(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
// );

// [OPTION D] 1.54" Black/White (200x200 / SSD1681 / GDEH0154D67)
// GxEPD2_BW<GxEPD2_154_D67, GxEPD2_154_D67::HEIGHT> display(
//   GxEPD2_154_D67(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
// );

// [OPTION E] 2.9" Black/White (296x128 / SSD1680 / GDEM029T94)
// GxEPD2_BW<GxEPD2_290_T94, GxEPD2_290_T94::HEIGHT> display(
//   GxEPD2_290_T94(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
// );

// ==============================================================================
// 3. FORWARD DECLARATIONS
// ==============================================================================
void drawFullTestPattern();
void drawPartialCounter(int count);

// ==============================================================================
// 4. SETUP
// ==============================================================================
void setup() {
  setLED(0, 0, 50); // LED Blue during boot

  Serial.begin(115200);

  // Allow USB CDC up to 2 seconds to attach
  unsigned long t0 = millis();
  while (!Serial && (millis() - t0 < 2000)) {
    delay(10);
  }

  Serial.println("\n=======================================================");
  Serial.println("  ESP32-S3 STANDALONE E-INK TEST");
  Serial.println("=======================================================");
  Serial.printf("Configured Pins:\n");
  Serial.printf("  SCL  (Clock) : GPIO %d\n", PIN_EPD_SCL);
  Serial.printf("  SDA  (Data)  : GPIO %d\n", PIN_EPD_SDA);
  Serial.printf("  CS   (Select): GPIO %d\n", PIN_EPD_CS);
  Serial.printf("  DC   (Cmd)   : GPIO %d\n", PIN_EPD_DC);
  Serial.printf("  RES  (Reset) : GPIO %d\n", PIN_EPD_RES);
  Serial.printf("  BUSY (Status): GPIO %d\n", PIN_EPD_BUSY);
  Serial.println("-------------------------------------------------------");

  // Initialize hardware SPI with custom pins: (sck, miso=-1, mosi, ss=-1)
  Serial.println("[1/4] Starting SPI bus...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);

  // Link SPI instance to GxEPD2
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));

#if USE_BUSY_PIN
  pinMode(PIN_EPD_BUSY, INPUT);
  Serial.printf("[2/4] BUSY pin level at boot: %d (0 = Ready, 1 = Busy)\n", digitalRead(PIN_EPD_BUSY));
#else
  Serial.println("[2/4] BUSY pin check bypassed (-1).");
#endif

  // Initialize Display
  Serial.println("[3/4] Initializing e-ink controller...");
  setLED(50, 40, 0); // Yellow

#if SKIP_BOOT_BLINKING
  // 2nd param 'initial = false' prevents GxEPD2 from executing the initial full white/black clear
  display.init(115200, false, 2, false);
  Serial.println("[3/4] Boot blinking disabled (Smooth Partial Mode enabled).");
#else
  display.init(115200, true, 10, false);
#endif

  display.setRotation(1); // Landscape (width > height)

  // Draw Initial Screen Frame
#if SKIP_BOOT_BLINKING
  Serial.println("[4/4] Drawing initial screen using Smooth Partial Refresh (No flicker)...");
#else
  Serial.println("[4/4] Performing initial Full Refresh (Full strobe blink)...");
#endif
  drawFullTestPattern();
  Serial.println(">> Initial screen update complete!");

  setLED(0, 0, 0); // Turn off LED after setup completes
  Serial.println("\nBeginning Partial Refresh loop (count updates every 3s)...");
}

// ==============================================================================
// 5. LOOP - REFRESH RATE BENCHMARK (TARGET: 2 UPDATES PER SECOND = 500ms)
// ==============================================================================
int testCounter = 1;
unsigned long lastRefreshTime = 0;
const unsigned long TARGET_INTERVAL_MS = 500; // 500 ms = 2.0 Hz

void loop() {
  unsigned long tStart = millis();

  testCounter++;
  drawPartialCounter(testCounter, lastRefreshTime);

  unsigned long elapsed = millis() - tStart;
  lastRefreshTime = elapsed;

  float actualHz = 1000.0f / (elapsed > 0 ? elapsed : 1);
  Serial.printf("[REFRESH BENCHMARK] Count: %-4d | Refresh: %lu ms | Rate: %.2f updates/sec (Target: 2.0)\n",
                testCounter, elapsed, actualHz);

  // If the display refreshed faster than 500ms, delay the remaining time
  // to maintain exactly 2 updates per second:
  if (elapsed < TARGET_INTERVAL_MS) {
    delay(TARGET_INTERVAL_MS - elapsed);
  }
}

// ==============================================================================
// 6. DRAWING FUNCTIONS
// ==============================================================================

/**
 * Draws the baseline test pattern.
 * If SKIP_BOOT_BLINKING is enabled, uses setPartialWindow to eliminate screen flashing!
 */
void drawFullTestPattern() {
#if SKIP_BOOT_BLINKING
  // Use Fast Partial Refresh on the whole screen (zero invert-blinking, ~700ms)
  display.setPartialWindow(0, 0, display.width(), display.height());
#else
  // Standard Full Refresh (strobe blinks to reset pigment charges)
  display.setFullWindow();
#endif
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);

    int16_t w = display.width();
    int16_t h = display.height();

    // 1. Double Border Frame
    display.drawRect(0, 0, w, h, GxEPD_BLACK);
    display.drawRect(2, 2, w - 4, h - 4, GxEPD_BLACK);

    // 2. Title Header Banner
    display.fillRect(3, 3, w - 6, 20, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setTextSize(1);
    display.setCursor(8, 9);
    display.print("ESP32-S3 E-INK BENCHMARK");

    // 3. Static Labels
    display.setTextColor(GxEPD_BLACK);
    display.setCursor(8, 28);
    display.printf("Res: %dx%d px", w, h);

    display.setCursor(8, 40);
    display.print("Target Rate: 2.0 Hz (500ms)");

    // Divider Line
    display.drawLine(4, 52, w - 5, 52, GxEPD_BLACK);

    // Dynamic Counter Box outline (Byte-aligned X=8, Width=144)
    display.drawRoundRect(8, 56, 144, 42, 4, GxEPD_BLACK);
    display.setCursor(14, 66);
    display.print("Count: 1");
    display.setCursor(14, 80);
    display.print("Timing: Benchmarking...");

    // 4. Test Shapes on the right
    display.drawCircle(w - 35, 76, 14, GxEPD_BLACK);
    display.fillCircle(w - 35, 76, 6, GxEPD_BLACK);
    display.drawTriangle(w - 70, 90, w - 55, 62, w - 85, 62, GxEPD_BLACK);

    // 5. Footer Bar
    display.drawLine(4, 102, w - 5, 102, GxEPD_BLACK);
    display.setCursor(8, 109);
    display.print("Robosen Modular Block System");

  } while (display.nextPage());
}

/**
 * Updates the counter box at maximum partial refresh speed.
 * Uses byte-aligned coordinates (multiples of 8) for optimal SPI transfer.
 */
void drawPartialCounter(int count, unsigned long lastDurationMs) {
  // Byte-aligned bounding box: X=8, Y=56, Width=144, Height=42
  uint16_t boxX = 8;
  uint16_t boxY = 56;
  uint16_t boxW = 144;
  uint16_t boxH = 42;

  display.setPartialWindow(boxX, boxY, boxW, boxH);
  display.firstPage();
  do {
    display.fillRect(boxX, boxY, boxW, boxH, GxEPD_WHITE);
    display.drawRoundRect(boxX, boxY, boxW, boxH, 4, GxEPD_BLACK);

    display.setTextColor(GxEPD_BLACK);
    display.setTextSize(1);
    display.setCursor(boxX + 6, boxY + 8);
    display.printf("Count: %d", count);

    display.setCursor(boxX + 6, boxY + 24);
    if (lastDurationMs > 0) {
      display.printf("Time: %lums (%.1fHz)", lastDurationMs, 1000.0f / lastDurationMs);
    } else {
      display.print("Measuring...");
    }

  } while (display.nextPage());
}
