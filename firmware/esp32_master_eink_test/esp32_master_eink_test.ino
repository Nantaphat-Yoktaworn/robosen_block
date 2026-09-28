/*
 * ======================================================================================
 * ROBOSEN PHYSICAL BLOCK SYSTEM - MASTER BLOCK E-INK TEST SKETCH
 * ======================================================================================
 * Target Hardware: ESP32-S3 (DevKitC-1)
 * Target Display : 2.13" E-Paper Display (SSD1680 / UC8151D, 122x250, SPI)
 * Library Req'd  : 
 *   1. "GxEPD2" by Jean-Marc Zingg (Install via Arduino Library Manager)
 *   2. "Adafruit GFX Library" by Adafruit
 *
 * Wiring Configuration (From Master Block Hardware Spec):
 * --------------------------------------------------------------------------------------
 *  Display Pin Label  | ESP32-S3 GPIO | Wire Color | Function
 * --------------------------------------------------------------------------------------
 *  VCC                | 3V3           | RED        | 3.3V Power (Never 5V!)
 *  GND                | GND           | BLACK      | Ground Rail
 *  SCL / SCK          | GPIO 21       | GREEN      | SPI Clock
 *  SDA / MOSI / DIN   | GPIO 38       | WHITE      | SPI Data In
 *  RES / RST          | GPIO 5        | BROWN      | Hardware Reset
 *  DC                 | GPIO 6        | PURPLE     | Data/Command
 *  CS                 | GPIO 7        | YELLOW     | Chip Select
 *  BUSY               | GPIO 4        | GRAY       | Active Busy Status
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Fonts/FreeSansBold9pt7b.h>
#include <Fonts/FreeSansBold12pt7b.h>
#include "soc/soc.h"
#include "soc/rtc_cntl_reg.h"

// Onboard WS2812 RGB LED (GPIO 48 on DevKitC-1)
#ifndef RGB_BUILTIN
  #define RGB_BUILTIN 48
#endif

void setLED(uint8_t r, uint8_t g, uint8_t b) {
  #ifdef RGB_BUILTIN
    rgbLedWrite(RGB_BUILTIN, r, g, b);
  #endif
}

// ==============================================================================
// 1. PIN DEFINITIONS
// ==============================================================================
// NOTE: Set USE_BUSY_PIN to 0 if your screen freezes at Yellow LED (Bypasses BUSY)
#define USE_BUSY_PIN    0   // 0 = Ignore BUSY (prevents freeze), 1 = Use GPIO 4

#if USE_BUSY_PIN
  #define PIN_EPD_BUSY  4   // BUSY line (GPIO 4)
#else
  #define PIN_EPD_BUSY -1   // Bypassed: Driver uses safe timed delays instead
#endif

#define PIN_EPD_RES     5   // Reset (RES)
#define PIN_EPD_DC      6   // Data / Command (DC)
#define PIN_EPD_CS      7   // Chip Select (CS)
#define PIN_EPD_SCL    21   // SPI Clock (SCL / SCK)
#define PIN_EPD_SDA    38   // SPI MOSI (SDA / DIN)

// ==============================================================================
// 2. DISPLAY DRIVER SELECTION (GxEPD2)
// ==============================================================================
// EXACT MATCH for Shopee "SSD1680 / JD79661" (DEPG0213BN, 122x250):
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT> display(
  GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);

// --- ALTERNATIVE DRIVERS ---
// For Waveshare 2.13" V3/V4 (GDEH0213B74):
// GxEPD2_BW<GxEPD2_213_B74, GxEPD2_213_B74::HEIGHT> display(
//   GxEPD2_213_B74(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY));

// For Waveshare 2.13" V2 (UC8151D / DEPG0213Bx):
// GxEPD2_BW<GxEPD2_213_flex, GxEPD2_213_flex::HEIGHT> display(
//   GxEPD2_213_flex(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY));

// ==============================================================================
// 3. TEST DATA & PROTOTYPES
// ==============================================================================
struct TestAction {
  const char* title;
  const char* unit;
  int value;
};

TestAction DEMO_ACTIONS[] = {
  {"Walk Forward",  "Steps", 3},
  {"Turn Right",    "Deg",   90},
  {"Punch Left",    "Reps",  2},
  {"Say Hello",     "Reps",  1},
  {"Push-ups",      "Reps",  3}
};
const int TOTAL_DEMO = sizeof(DEMO_ACTIONS) / sizeof(DEMO_ACTIONS[0]);

void drawFullBaseUI();
void updateDynamicParamBox(const char* actionName, int val, const char* unit, int stepNum);

// ==============================================================================
// 4. SETUP
// ==============================================================================
void setup() {
  // Disable brownout detector in case USB power sags during screen refresh
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0);

  // Status LED: Solid Blue (Starting boot)
  setLED(0, 0, 50);

  Serial.begin(115200);
  
  // Wait up to 3 seconds for USB Serial CDC to attach
  unsigned long tStart = millis();
  while (!Serial && (millis() - tStart < 3000)) {
    delay(10);
  }

  Serial.println("\n=======================================================");
  Serial.println("  ROBOSEN MASTER BLOCK - 2.13\" E-INK HARDWARE TEST");
  Serial.println("=======================================================");
  Serial.printf("Pins: SCL=GPIO%d, SDA=GPIO%d, CS=GPIO%d, DC=GPIO%d, RES=GPIO%d, BUSY=GPIO%d\n",
                PIN_EPD_SCL, PIN_EPD_SDA, PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY);

  // Status LED: Yellow (Initializing SPI)
  setLED(50, 40, 0);

  // Initialize ESP32-S3 Hardware SPI with custom pins: (sck, miso, mosi, ss=-1)
  // Passing -1 for SS allows GxEPD2 to manually control PIN_EPD_CS via GPIO
  Serial.println("[SPI] Initializing SPI bus...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);

  // CRITICAL: Explicitly bind custom SPI bus and SPISettings to GxEPD2
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));

  // Check BUSY pin state before init
#if USE_BUSY_PIN
  pinMode(PIN_EPD_BUSY, INPUT);
  Serial.printf("[EPD] Initial BUSY pin state: %d (0=Idle, 1=Busy)\n", digitalRead(PIN_EPD_BUSY));
#else
  Serial.println("[EPD] BUSY pin bypassed (-1). Using internal timed delays.");
#endif

  // Initialize E-Ink display
  Serial.println("[EPD] Initializing GxEPD2 display controller...");
  display.init(115200, true, 10, false);
  display.setRotation(1); // 1 = Landscape orientation (250 width x 122 height)

  // Status LED: Purple (Drawing baseline UI)
  setLED(40, 0, 50);

  // Step 1: Perform a Full Refresh Baseline
  Serial.println("[EPD] Drawing Full Static UI Frame...");
  drawFullBaseUI();
#if !USE_BUSY_PIN
  delay(2000); // Safe delay for full refresh when BUSY pin is bypassed
#endif
  Serial.println("[EPD] Baseline UI drawn successfully!");

  // Status LED: Bright Green (Running loop)
  setLED(0, 100, 0);
  Serial.println("Now testing fast Partial Refresh (SSD1680 ~300ms)...");
}

// ==============================================================================
// 5. MAIN LOOP (SIMULATES ROTARY KNOB VALUE ADJUSTMENTS)
// ==============================================================================
int demoIndex = 0;
int counter = 1;

void loop() {
  delay(2500); // Pause between test updates

  // Green Heartbeat Blink on each update cycle
  setLED(0, 150, 0);
  delay(80);
  setLED(0, 20, 0);

  const auto& item = DEMO_ACTIONS[demoIndex];
  Serial.printf("\n[PARTIAL REFRESH] Action: %-15s Value: %d %s (Step #%d)\n",
                item.title, counter, item.unit, demoIndex + 1);

  // Perform partial window refresh without clearing the rest of the screen
  updateDynamicParamBox(item.title, counter, item.unit, demoIndex + 1);
#if !USE_BUSY_PIN
  delay(400); // Safe delay for partial refresh settling when BUSY is bypassed
#endif

  counter++;
  if (counter > 5) {
    counter = 1;
    demoIndex = (demoIndex + 1) % TOTAL_DEMO;
  }
}

// ==============================================================================
// 6. UI DRAWING FUNCTIONS
// ==============================================================================

/**
 * Draws the static header, border, and labels using a Full Refresh.
 */
void drawFullBaseUI() {
  display.setFullWindow();
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);

    // --- Outer Frame ---
    display.drawRect(0, 0, 250, 122, GxEPD_BLACK);
    display.drawRect(1, 1, 248, 120, GxEPD_BLACK);

    // --- Top Title Bar ---
    display.fillRect(2, 2, 246, 22, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(6, 18);
    display.print("ROBOSEN K1 MASTER");

    // Status pill
    display.setCursor(185, 18);
    display.print("TEST");

    // --- Static Section Divider ---
    display.drawLine(2, 86, 248, 86, GxEPD_BLACK);

    // --- Bottom Dock Status Bar ---
    display.setFont(); // Default 5x7 font
    display.setTextSize(1);
    display.setTextColor(GxEPD_BLACK);
    display.setCursor(8, 93);
    display.print("Config Dock: DOCKED [0xCF]");
    display.setCursor(8, 107);
    display.print("Knob 1: Select  |  Knob 2: Adjust");

  } while (display.nextPage());
}

/**
 * Updates only the center region (Action name, big parameter number, and unit)
 * using Fast Partial Refresh (SSD1680 ~300ms, no screen flickering).
 */
void updateDynamicParamBox(const char* actionName, int val, const char* unit, int stepNum) {
  // Region coordinates: X=4, Y=26, Width=242, Height=58
  uint16_t boxX = 4;
  uint16_t boxY = 26;
  uint16_t boxW = 242;
  uint16_t boxH = 58;

  display.setPartialWindow(boxX, boxY, boxW, boxH);
  display.firstPage();
  do {
    // Clear the partial window background
    display.fillRect(boxX, boxY, boxW, boxH, GxEPD_WHITE);

    // Draw Action Name
    display.setTextColor(GxEPD_BLACK);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(10, 48);
    display.printf("#%d: %s", stepNum, actionName);

    // Draw Big Parameter Number
    display.setFont(&FreeSansBold12pt7b);
    display.setCursor(14, 76);
    display.printf("[%d]", val);

    // Draw Parameter Unit
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(65, 74);
    display.printf("%s", unit);

    // Draw a visual gauge / dots for the value
    for (int i = 0; i < 5; i++) {
      int dotX = 175 + (i * 12);
      int dotY = 68;
      if (i < val) {
        display.fillCircle(dotX, dotY, 4, GxEPD_BLACK);
      } else {
        display.drawCircle(dotX, dotY, 4, GxEPD_BLACK);
      }
    }

  } while (display.nextPage());
}
