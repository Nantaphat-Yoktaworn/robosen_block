/*
 * ======================================================================================
 * ROBOSEN MASTER BLOCK - ALL INPUT DEVICES & SCREEN SOLDERING VERIFICATION FIRMWARE
 * ======================================================================================
 * Target Hardware : ESP32-S3 (DevKitC-1-N8R8 / N16R8) on Master Block Carrier PCB
 * Verified Scope  : 
 *   1. Rotary Encoder 1 (SW1 Action Knob: CLK=IO8, DT=IO9, SW=IO10)
 *   2. Rotary Encoder 2 (SW2 Param Knob : CLK=IO11, DT=IO12, SW=IO13)
 *   3. Green Push Button (SW3 Start     : GPIO 14)
 *   4. Red Push Button   (SW5 Stop      : GPIO 2)
 *   5. Battery Voltage Monitor (R3/R4 1:1 Divider on GPIO 1 / ADC1_CH0)
 *   6. 2.13" E-Paper SPI Display (DEPG0213BN / SSD1680, 122x250) - PURE TEXT MODE
 *   7. Onboard WS2812 RGB Status LED (GPIO 48)
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include "master_soldering_types.h"
#include "esp_private/brownout.h"

// ==============================================================================
// 1. PIN DEFINITIONS
// ==============================================================================
// --- ROTARY ENCODER 1: ACTION KNOB (SW1) ---
const int PIN_K1_CLK = 8;    // Phase A (GPIO 8)
const int PIN_K1_DT  = 9;    // Phase B (GPIO 9)
const int PIN_K1_SW  = 10;   // Integrated Tactile Push Switch (GPIO 10, Active LOW)

// --- ROTARY ENCODER 2: PARAMETER KNOB (SW2) ---
const int PIN_K2_CLK = 11;   // Phase A (GPIO 11)
const int PIN_K2_DT  = 12;   // Phase B (GPIO 12)
const int PIN_K2_SW  = 13;   // Integrated Tactile Push Switch (GPIO 13, Active LOW)

// --- USER PUSH BUTTONS ---
const int PIN_START_BTN = 14; // SW3: Green Tactile Button (GPIO 14, Active LOW)
const int PIN_STOP_BTN  = 2;  // SW5: Red Tactile Button   (GPIO 2,  Active LOW)

// --- BATTERY VOLTAGE MONITOR ---
const int PIN_BATSENSE  = 1;  // R3(100k) + R4(100k) divider midpoint (GPIO 1 / ADC1_CH0)

// --- 2.13" E-PAPER DISPLAY (DEPG0213BN / SSD1680) ---
// Set USE_BUSY_PIN to 0 to bypass BUSY line (uses reliable internal timed delays ~730ms, prevents freezes)
#define USE_BUSY_PIN 0

#if USE_BUSY_PIN
  const int PIN_EPD_BUSY = 4;   // BUSY line (GPIO 4)
#else
  const int PIN_EPD_BUSY = -1;  // Bypassed: Driver uses safe timed hardware delays
#endif

const int PIN_EPD_RES   = 5;   // Hardware Reset (GPIO 5)
const int PIN_EPD_DC    = 6;   // Data/Command (GPIO 6)
const int PIN_EPD_CS    = 7;   // Chip Select (GPIO 7)
const int PIN_EPD_SCL   = 21;  // SPI Clock (GPIO 21)
const int PIN_EPD_SDA   = 38;  // SPI MOSI / Data (GPIO 38)

// --- ONBOARD STATUS RGB LED ---
#ifndef RGB_BUILTIN
  #define RGB_BUILTIN 48       // DevKitC-1 onboard WS2812
#endif

// ==============================================================================
// 2. DISPLAY DRIVER INSTANTIATION
// ==============================================================================
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT> display(
  GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);

// ==============================================================================
// 3. SYSTEM STATE VARIABLES
// ==============================================================================
EncoderState encKnob1 = {PIN_K1_CLK, PIN_K1_DT, PIN_K1_SW, "KNOB1 (SW1)", 0, HIGH, false, HIGH, 0, 0, 0, 0};
EncoderState encKnob2 = {PIN_K2_CLK, PIN_K2_DT, PIN_K2_SW, "KNOB2 (SW2)", 0, HIGH, false, HIGH, 0, 0, 0, 0};

ButtonState btnStart  = {PIN_START_BTN, "START (SW3-Green)", false, HIGH, 0, 0, 0, 0};
ButtonState btnStop   = {PIN_STOP_BTN,  "STOP  (SW5-Red)  ", false, HIGH, 0, 0, 0, 0};

const unsigned long DEBOUNCE_DELAY_MS = 25;

// Battery telemetry
float lastVbat = 0.0f;
uint32_t lastRawAdcMv = 0;
int lastBatPct = 0;
unsigned long lastBatSampleTime = 0;

// Display update throttling
unsigned long lastDisplayUpdateTime = 0;
bool screenNeedsUpdate = false;
unsigned long lastKnobActivityTime = 0;

// ==============================================================================
// 4. LED STATUS INDICATOR
// ==============================================================================
void setStatusLED(uint8_t r, uint8_t g, uint8_t b) {
  #ifdef RGB_BUILTIN
    rgbLedWrite(RGB_BUILTIN, r, g, b);
  #endif
}

void updateLEDStatus() {
  if (btnStart.isPressed && btnStop.isPressed) {
    // Both Green & Red pressed: Bright Yellow
    setStatusLED(180, 180, 0);
  } else if (btnStart.isPressed) {
    // Green Start pressed: Bright Green
    setStatusLED(0, 200, 0);
  } else if (btnStop.isPressed) {
    // Red Stop pressed: Bright Red
    setStatusLED(200, 0, 0);
  } else if (encKnob1.swPressed) {
    // Knob 1 click: Bright Cyan
    setStatusLED(0, 200, 200);
  } else if (encKnob2.swPressed) {
    // Knob 2 click: Bright Magenta
    setStatusLED(200, 0, 200);
  } else if (millis() - lastKnobActivityTime < 80) {
    // Knob rotating: Flash White
    setStatusLED(120, 120, 120);
  } else {
    // Idle state: Subtle breathing blue
    uint8_t breath = (sin(millis() / 400.0f) + 1.0f) * 15 + 4;
    setStatusLED(0, breath / 2, breath);
  }
}

// ==============================================================================
// 5. BATTERY SENSING & DIAGNOSTIC FUNCTIONS
// ==============================================================================
float readBatteryMilliVolts(uint32_t &rawMvOut) {
  rawMvOut = analogReadMilliVolts(PIN_BATSENSE);
  // 1:1 divider (R3=100k, R4=100k): Vbat = Vadc * 2
  float vbat = (rawMvOut * 2.0f) / 1000.0f;
  return vbat;
}

int calculateBatteryPercent(float vbat) {
  if (vbat >= 4.20f) return 100;
  if (vbat <= 3.20f) return 0;
  int pct = (int)((vbat - 3.20f) / (4.20f - 3.20f) * 100.0f);
  return constrain(pct, 0, 100);
}

const char* getBatteryHealthString(float vbat) {
  if (vbat < 2.00f)  return "OFF/NO BATT";
  if (vbat < 3.20f)  return "CRITICAL LOW";
  if (vbat < 3.55f)  return "LOW BATTERY";
  if (vbat <= 4.25f) return "HEALTHY (OK)";
  return "HIGH/CHARGE";
}

void runDeepBatteryDiagnostic() {
  Serial.println("\n------------------------------------------------------------");
  Serial.println("  [BATTERY SENSE DEEP DIAGNOSTIC - 16 SAMPLES]");
  Serial.println("------------------------------------------------------------");
  Serial.println(" Sample # | Raw ADC (mV) | Calculated Vbat (V)");

  uint32_t sumAdc = 0;
  uint32_t minAdc = 99999;
  uint32_t maxAdc = 0;

  for (int i = 0; i < 16; i++) {
    uint32_t sample = analogReadMilliVolts(PIN_BATSENSE);
    sumAdc += sample;
    if (sample < minAdc) minAdc = sample;
    if (sample > maxAdc) maxAdc = sample;
    float v = (sample * 2.0f) / 1000.0f;
    Serial.printf("   #%02d    |   %4d mV    |   %1.3f V\n", i + 1, sample, v);
    delay(20);
  }

  float avgAdc = sumAdc / 16.0f;
  float avgVbat = (avgAdc * 2.0f) / 1000.0f;
  uint32_t noiseDelta = maxAdc - minAdc;

  Serial.printf("Average ADC : %1.1f mV  (Vbat: %1.3f V)\n", avgAdc, avgVbat);
  Serial.printf("ADC Range   : %d mV to %d mV (Peak-to-Peak Noise: %d mV)\n", minAdc, maxAdc, noiseDelta);

  if (noiseDelta <= 40) {
    Serial.println(">> FILTER CAPACITOR C1 (100nF) SOLDERING STATUS: [EXCELLENT]");
  } else if (noiseDelta <= 100) {
    Serial.println(">> FILTER CAPACITOR C1 SOLDERING STATUS: [GOOD / ACCEPTABLE]");
  } else {
    Serial.println(">> WARNING: High ADC ripple (>100mV). Check C1 capacitor soldering joints!");
  }
  Serial.println("------------------------------------------------------------\n");
}

// ==============================================================================
// 6. ROTARY ENCODER & BUTTON DECODER
// ==============================================================================
bool updateEncoder(EncoderState &enc, bool invertDirection = false) {
  bool activity = false;

  // 1. Quadrature Rotation Detection
  int clk = digitalRead(enc.pinClk);
  if (clk != enc.lastClk && clk == LOW) {
    int dt = digitalRead(enc.pinDt);
    bool cw = (dt != clk);
    if (invertDirection) cw = !cw;

    if (cw) {
      enc.position++;
      Serial.printf("🔄 [%s] ROTATED CW  -> Position: %+d\n", enc.name, enc.position);
    } else {
      enc.position--;
      Serial.printf("🔄 [%s] ROTATED CCW -> Position: %+d\n", enc.name, enc.position);
    }
    lastKnobActivityTime = millis();
    activity = true;
  }
  enc.lastClk = clk;

  // 2. Integrated Pushbutton Debounce
  int swReading = digitalRead(enc.pinSw);
  if (swReading != enc.lastSwRaw) {
    enc.lastDebounceTime = millis();
  }

  if ((millis() - enc.lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    bool currentPressed = (swReading == LOW);
    if (currentPressed != enc.swPressed) {
      enc.swPressed = currentPressed;
      activity = true;
      if (enc.swPressed) {
        enc.swPressStartTime = millis();
        enc.swPressCount++;
        Serial.printf("\n🔘 [%s SWITCH] CLICK PRESSED!  (Total Hits: %u)\n", enc.name, enc.swPressCount);
      } else {
        enc.lastHoldDurationMs = millis() - enc.swPressStartTime;
        Serial.printf("⚪ [%s SWITCH] CLICK RELEASED! (Held for %u ms)\n", enc.name, enc.lastHoldDurationMs);
      }
    }
  }
  enc.lastSwRaw = swReading;

  return activity;
}

bool updateButton(ButtonState &btn) {
  int reading = digitalRead(btn.pin);
  bool stateChanged = false;

  if (reading != btn.lastRawState) {
    btn.lastDebounceTime = millis();
  }

  if ((millis() - btn.lastDebounceTime) > DEBOUNCE_DELAY_MS) {
    bool currentPressed = (reading == LOW);
    if (currentPressed != btn.isPressed) {
      btn.isPressed = currentPressed;
      stateChanged = true;
      if (btn.isPressed) {
        btn.pressStartTime = millis();
        btn.pressCount++;
        Serial.printf("\n🔘 [BUTTON EVENT] %s PRESSED!  (Total Hits: %u)\n", btn.name, btn.pressCount);
      } else {
        btn.lastHoldDurationMs = millis() - btn.pressStartTime;
        Serial.printf("⚪ [BUTTON EVENT] %s RELEASED! (Held for %u ms)\n", btn.name, btn.lastHoldDurationMs);
      }
    }
  }

  btn.lastRawState = reading;
  return stateChanged;
}

// ==============================================================================
// 7. PURE TEXT DISPLAY INTERFACE (ZERO LINES, ZERO DECORATION)
// ==============================================================================

// Renders only clean, crisp lines of text onto the display buffer
void renderPureTextUI() {
  display.fillScreen(GxEPD_WHITE);
  display.setTextColor(GxEPD_BLACK);
  display.setTextSize(1);

  // Line 0: Header (y = 4)
  display.setCursor(4, 4);
  display.print("== ROBOSEN ALL-INPUT TEST ==");

  // Line 1: Knob 1 (SW1 Action Knob: CLK 8, DT 9, SW 10)
  display.setCursor(4, 18);
  display.printf("K1 (SW1-IO08): Pos: %+4d | SW:%s",
                 encKnob1.position, encKnob1.swPressed ? "PRESS" : "IDLE ");

  // Line 2: Knob 2 (SW2 Param Knob: CLK 11, DT 12, SW 13)
  display.setCursor(4, 32);
  display.printf("K2 (SW2-IO11): Pos: %+4d | SW:%s",
                 encKnob2.position, encKnob2.swPressed ? "PRESS" : "IDLE ");

  // Line 3: Green Start Button (SW3: GPIO 14)
  display.setCursor(4, 46);
  display.printf("SW3 Start(14): %-7s | Hits:%u",
                 btnStart.isPressed ? "[PRESS]" : "[IDLE]", btnStart.pressCount);

  // Line 4: Red Stop Button (SW5: GPIO 2)
  display.setCursor(4, 60);
  display.printf("SW5 Stop (02): %-7s | Hits:%u",
                 btnStop.isPressed ? "[PRESS]" : "[IDLE]", btnStop.pressCount);

  // Line 5: Battery ADC & Percentage (GPIO 1)
  display.setCursor(4, 74);
  display.printf("Battery (01) : %1.2fV (%d%%) %4dmV",
                 lastVbat, lastBatPct, lastRawAdcMv);

  // Line 6: Battery Health Status
  display.setCursor(4, 88);
  display.printf("Health Status: %s", getBatteryHealthString(lastVbat));

  // Line 7: Interactive Serial Instructions
  display.setCursor(4, 106);
  display.print("Cmds: 'r'=Refresh | 'c'=Clear | 'b'=Batt");
}

// Full refresh to clear display on boot or manual refresh
void fullRefreshDisplay() {
  Serial.println("[EPD] Performing Full Screen Refresh (clearing screen)...");
  display.setFullWindow();
  display.firstPage();
  do {
    renderPureTextUI();
  } while (display.nextPage());
  #if !USE_BUSY_PIN
    delay(2000); // Allow physical ink microcapsules time to settle
  #endif
  Serial.println("[EPD] Full Screen Refresh Completed.");
}

// Hardware reset pulse and complete re-initialization
void reinitAndFullRefreshDisplay() {
  Serial.println("\n[EPD] >>> Hardware Resetting and Reinitializing DEPG0213BN / SSD1680...");
  pinMode(PIN_EPD_RES, OUTPUT);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(15);
  digitalWrite(PIN_EPD_RES, LOW);
  delay(25);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(60);

  // Re-run GxEPD2 initialization with initial=true to sync framebuffers & load LUT
  display.init(115200, true, 10, false);
  display.setRotation(1);

  fullRefreshDisplay();
}

// Fast partial refresh for snappy live text updates
void partialRefreshDisplay() {
  unsigned long t0 = millis();
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
  do {
    renderPureTextUI();
  } while (display.nextPage());
  #if !USE_BUSY_PIN
    delay(200);
  #endif
  Serial.printf("[EPD] Screen text updated in %lu ms\n", millis() - t0);
}

// Deep Hardware Pin Status Diagnostic
void runHardwarePinDiagnostic() {
  Serial.println("\n------------------------------------------------------------");
  Serial.println("  [ALL-INPUT HARDWARE PIN READOUT]");
  Serial.println("------------------------------------------------------------");
  Serial.printf("  1. Knob 1 CLK (GPIO 8)  : %d (%s)\n", digitalRead(PIN_K1_CLK), digitalRead(PIN_K1_CLK) ? "HIGH" : "LOW");
  Serial.printf("  2. Knob 1 DT  (GPIO 9)  : %d (%s)\n", digitalRead(PIN_K1_DT),  digitalRead(PIN_K1_DT)  ? "HIGH" : "LOW");
  Serial.printf("  3. Knob 1 SW  (GPIO 10) : %d (%s)\n", digitalRead(PIN_K1_SW),  digitalRead(PIN_K1_SW)  ? "HIGH (IDLE)" : "LOW (PRESSED)");
  Serial.printf("  4. Knob 2 CLK (GPIO 11) : %d (%s)\n", digitalRead(PIN_K2_CLK), digitalRead(PIN_K2_CLK) ? "HIGH" : "LOW");
  Serial.printf("  5. Knob 2 DT  (GPIO 12) : %d (%s)\n", digitalRead(PIN_K2_DT),  digitalRead(PIN_K2_DT)  ? "HIGH" : "LOW");
  Serial.printf("  6. Knob 2 SW  (GPIO 13) : %d (%s)\n", digitalRead(PIN_K2_SW),  digitalRead(PIN_K2_SW)  ? "HIGH (IDLE)" : "LOW (PRESSED)");
  Serial.printf("  7. SW3 Start  (GPIO 14) : %d (%s)\n", digitalRead(PIN_START_BTN), digitalRead(PIN_START_BTN) ? "HIGH (IDLE)" : "LOW (PRESSED)");
  Serial.printf("  8. SW5 Stop   (GPIO 2)  : %d (%s)\n", digitalRead(PIN_STOP_BTN),  digitalRead(PIN_STOP_BTN)  ? "HIGH (IDLE)" : "LOW (PRESSED)");

  pinMode(4, INPUT);
  int busyState = digitalRead(4);
  Serial.printf("  9. EPD BUSY   (GPIO 4)  : %d (%s)\n", busyState, busyState == 0 ? "LOW (READY)" : "HIGH (BUSY)");

  pinMode(PIN_EPD_RES, INPUT);
  int resState = digitalRead(PIN_EPD_RES);
  Serial.printf(" 10. EPD RES    (GPIO 5)  : %d (%s)\n", resState, resState ? "HIGH (NORMAL)" : "LOW (HELD IN RESET)");

  Serial.println("------------------------------------------------------------\n");
}

// ==============================================================================
// 8. SERIAL TERMINAL MENU & USER INTERACTION
// ==============================================================================
void printSerialHelp() {
  Serial.println("\n=======================================================");
  Serial.println("  ROBOSEN MASTER BLOCK - ALL INPUTS SOLDER TEST MENU");
  Serial.println("=======================================================");
  Serial.println(" Available Commands (Send via Serial Monitor):");
  Serial.println("   'r' - Hardware Reset + Reinit + Full Refresh");
  Serial.println("   's' - Print Raw State of ALL Hardware Input Pins");
  Serial.println("   'c' - Reset Knob Positions & Button Hits to 0");
  Serial.println("   'b' - Run Deep Battery ADC Diagnostic (16 samples)");
  Serial.println("   'l' - Test RGB LED Color Cycle");
  Serial.println("   '?' - Print this Help Menu");
  Serial.println("=======================================================\n");
}

void handleSerialCommand(char cmd) {
  switch (cmd) {
    case 'b':
    case 'B':
      runDeepBatteryDiagnostic();
      break;

    case 'r':
    case 'R':
      reinitAndFullRefreshDisplay();
      break;

    case 's':
    case 'S':
      runHardwarePinDiagnostic();
      break;

    case 'c':
    case 'C':
      encKnob1.position = 0;
      encKnob1.swPressCount = 0;
      encKnob2.position = 0;
      encKnob2.swPressCount = 0;
      btnStart.pressCount = 0;
      btnStop.pressCount = 0;
      Serial.println(">> All counters & knob positions reset to 0.");
      partialRefreshDisplay();
      break;

    case 'l':
    case 'L':
      Serial.println("[LED] Cycling RGB LED: Red -> Green -> Blue -> White -> Off");
      setStatusLED(255, 0, 0);   delay(400);
      setStatusLED(0, 255, 0);   delay(400);
      setStatusLED(0, 0, 255);   delay(400);
      setStatusLED(255, 255, 255); delay(400);
      setStatusLED(0, 0, 0);
      Serial.println("[LED] Test complete.");
      break;

    case '?':
    case 'h':
    case 'H':
      printSerialHelp();
      break;

    default:
      break;
  }
}

// ==============================================================================
// 9. SETUP
// ==============================================================================
void setup() {
  // Disable hardware brownout detector
  esp_brownout_disable();

  // Booting indicator: Solid Orange
  setStatusLED(100, 40, 0);

  Serial.begin(115200);
  delay(1200);

  Serial.println("\n\n=======================================================");
  Serial.println("  ROBOSEN MASTER BLOCK - ALL INPUT DEVICE SOLDERING TEST");
  Serial.println("=======================================================");
  Serial.println("Configured Pins:");
  Serial.println("  - Knob 1 (SW1 Action) : CLK=IO8,  DT=IO9,  SW=IO10");
  Serial.println("  - Knob 2 (SW2 Param)  : CLK=IO11, DT=IO12, SW=IO13");
  Serial.println("  - Green Start Button  : IO14 (INPUT_PULLUP)");
  Serial.println("  - Red Stop Button     : IO2  (INPUT_PULLUP)");
  Serial.println("  - Battery Voltage ADC : IO1  (ADC1_CH0)");
  Serial.println("  - E-Paper SPI Display : SCL=21, SDA=38, CS=7, DC=6, RES=5, BUSY=4");
  Serial.println("  - Onboard RGB LED     : IO48 (WS2812)");
  Serial.println("=======================================================\n");

  // Configure All Input Pins with Internal Pull-Ups
  pinMode(PIN_K1_CLK, INPUT_PULLUP);
  pinMode(PIN_K1_DT,  INPUT_PULLUP);
  pinMode(PIN_K1_SW,  INPUT_PULLUP);

  pinMode(PIN_K2_CLK, INPUT_PULLUP);
  pinMode(PIN_K2_DT,  INPUT_PULLUP);
  pinMode(PIN_K2_SW,  INPUT_PULLUP);

  pinMode(PIN_START_BTN, INPUT_PULLUP);
  pinMode(PIN_STOP_BTN,  INPUT_PULLUP);

  // Configure Battery Sense ADC Pin
  pinMode(PIN_BATSENSE, INPUT);

  // Read initial states
  encKnob1.lastClk   = digitalRead(PIN_K1_CLK);
  encKnob1.lastSwRaw = digitalRead(PIN_K1_SW);
  encKnob2.lastClk   = digitalRead(PIN_K2_CLK);
  encKnob2.lastSwRaw = digitalRead(PIN_K2_SW);

  // Allow power rail to stabilize before touching display
  delay(300);

  // Initialize Hardware SPI for 2.13" E-Paper
  Serial.println("[SPI] Initializing SPI bus (SCL=21, SDA=38)...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));

  // Perform clean hardware reset pulse on display controller
  pinMode(PIN_EPD_RES, OUTPUT);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(15);
  digitalWrite(PIN_EPD_RES, LOW);
  delay(25);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(60);

  // Initialize GxEPD2 Display with initial=true to sync both buffers & load LUT
  Serial.println("[EPD] Initializing DEPG0213BN E-Paper Display (Pure Text Mode)...");
  display.init(115200, true, 10, false);
  display.setRotation(1); // Landscape: 250 wide x 122 high

  // Read initial battery state
  lastVbat = readBatteryMilliVolts(lastRawAdcMv);
  lastBatPct = calculateBatteryPercent(lastVbat);
  Serial.printf("[BATTERY] Initial Reading: %1.2f V (%d%%) | ADC: %u mV\n", lastVbat, lastBatPct, lastRawAdcMv);

  // Initial Full Screen Refresh: Clean text layout
  Serial.println("[EPD] Initializing Full Screen Refresh...");
  fullRefreshDisplay();
  lastDisplayUpdateTime = millis();

  printSerialHelp();
  Serial.println(">> READY! Turn Knobs or Press Buttons to test soldering joints.\n");
}

// ==============================================================================
// 10. MAIN LOOP
// ==============================================================================
void loop() {
  // 1. Process Rotary Encoders (Knob 2 inverted on PCB layout so CW = +)
  bool k1Active = updateEncoder(encKnob1, false);
  bool k2Active = updateEncoder(encKnob2, false);

  // 2. Process Tactile Push Buttons
  bool startActive = updateButton(btnStart);
  bool stopActive  = updateButton(btnStop);

  if (k1Active || k2Active || startActive || stopActive) {
    screenNeedsUpdate = true;
  }

  // 3. Update Status RGB LED (Zero-latency immediate hardware feedback)
  updateLEDStatus();

  // 4. Periodic Battery Voltage Sampling (Every 2500 ms)
  if (millis() - lastBatSampleTime >= 2500) {
    lastBatSampleTime = millis();
    uint32_t currentAdcMv = 0;
    float currentVbat = readBatteryMilliVolts(currentAdcMv);
    int currentPct = calculateBatteryPercent(currentVbat);

    if (abs(currentVbat - lastVbat) >= 0.08f || abs(currentPct - lastBatPct) >= 4) {
      lastVbat = currentVbat;
      lastRawAdcMv = currentAdcMv;
      lastBatPct = currentPct;
      screenNeedsUpdate = true;
      Serial.printf("[BATTERY] Updated: %1.2f V (%d%%) | ADC: %u mV | %s\n",
                    lastVbat, lastBatPct, lastRawAdcMv, getBatteryHealthString(lastVbat));
    }
  }

  // 5. Update E-Paper Display (Throttled to >= 400ms to avoid flooding during fast knob turns)
  if (screenNeedsUpdate && (millis() - lastDisplayUpdateTime >= 400)) {
    screenNeedsUpdate = false;
    lastDisplayUpdateTime = millis();
    partialRefreshDisplay();
  }

  // 6. Handle Serial Commands
  if (Serial.available()) {
    char cmd = Serial.read();
    handleSerialCommand(cmd);
  }

  delay(2);
}
