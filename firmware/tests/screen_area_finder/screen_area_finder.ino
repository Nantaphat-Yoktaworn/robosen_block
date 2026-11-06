/*
 * ======================================================================================
 * ROBOSEN MASTER BLOCK - SCREEN AREA FINDER & BEZEL CALIBRATION FIRMWARE
 * ======================================================================================
 * Target Hardware : ESP32-S3 (DevKitC-1-N8R8 / N16R8) on Master Block Carrier PCB
 * Target Display  : 2.13" E-Paper SPI Display (DEPG0213BN / SSD1680, 250x122 Landscape)
 * 
 * Purpose:
 *   Calibrates the visible display bounding box when a custom 3D-printed enclosure bezel
 *   covers portions of the display edges to center the screen between the two rotary knobs.
 * 
 * Hardware Controls:
 *   - Green Button (SW3 / GPIO 14) : Cycles active corner (TL -> TR -> BR -> BL -> TL)
 *   - Left Knob    (SW1 / GPIO 8,9): Adjusts Vertical (Y) coordinate of the active corner
 *   - Right Knob   (SW2 / GPIO 11,12): Adjusts Horizontal (X) coordinate of the active corner
 *   - Knob Click   (SW1/SW2 Push)  : Toggles step resolution between Fine (1px) and Coarse (5px)
 *   - Red Button   (SW5 / GPIO 2)  : Saves calibrated boundaries to NVS flash & prints C++ macros
 *   - RGB LED      (GPIO 48)       : Color-coded active corner & tactile feedback
 * ======================================================================================
 */

#include <Arduino.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include <Preferences.h>

// ==============================================================================
// 1. PIN DEFINITIONS (MATCHING MASTER BLOCK CARRIER PCB)
// ==============================================================================

// --- ROTARY ENCODER 1: VERTICAL ADJUST / LEFT KNOB (SW1) ---
const int PIN_K1_CLK = 8;    // Phase A (GPIO 8)
const int PIN_K1_DT  = 9;    // Phase B (GPIO 9)
const int PIN_K1_SW  = 10;   // Integrated Push Switch (GPIO 10, Active LOW)

// --- ROTARY ENCODER 2: HORIZONTAL ADJUST / RIGHT KNOB (SW2) ---
const int PIN_K2_CLK = 11;   // Phase A (GPIO 11)
const int PIN_K2_DT  = 12;   // Phase B (GPIO 12)
const int PIN_K2_SW  = 13;   // Integrated Push Switch (GPIO 13, Active LOW)

// --- TACTILE PUSH BUTTONS ---
const int PIN_START_BTN = 14; // SW3: Green Tactile Button (GPIO 14, Active LOW - Next Corner)
const int PIN_STOP_BTN  = 2;  // SW5: Red Tactile Button   (GPIO 2,  Active LOW - Save & Finish)

// --- 2.13" E-PAPER DISPLAY (DEPG0213BN / SSD1680) ---
const int PIN_EPD_BUSY = 4;   // BUSY line (GPIO 4)
const int PIN_EPD_RES  = 5;   // Hardware Reset (GPIO 5)
const int PIN_EPD_DC   = 6;   // Data/Command (GPIO 6)
const int PIN_EPD_CS   = 7;   // Chip Select (GPIO 7)
const int PIN_EPD_SCL  = 21;  // SPI Clock (GPIO 21)
const int PIN_EPD_SDA  = 38;  // SPI MOSI / Data (GPIO 38)

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

// Display physical native dimensions
const int PANEL_WIDTH  = 250;
const int PANEL_HEIGHT = 122;

// Minimum allowed active window dimensions (prevents inverted coordinates)
const int MIN_ACTIVE_WIDTH  = 40;
const int MIN_ACTIVE_HEIGHT = 30;

// ==============================================================================
// 3. CALIBRATION STATE & CORNER ENUM
// ==============================================================================
enum ActiveCorner {
  CORNER_TOP_LEFT = 0,
  CORNER_TOP_RIGHT,
  CORNER_BOTTOM_RIGHT,
  CORNER_BOTTOM_LEFT
};

const char* CORNER_NAMES[] = {
  "TOP-LEFT (TL)",
  "TOP-RIGHT (TR)",
  "BOTTOM-RIGHT (BR)",
  "BOTTOM-LEFT (BL)"
};

ActiveCorner currentCorner = CORNER_TOP_LEFT;

// Calibrated bounding box coordinates (Initial state: calibrated bezel default)
int xMin = 40;
int yMin = 0;
int xMax = PANEL_WIDTH - 1;   // 249
int yMax = PANEL_HEIGHT - 1;  // 121

// Step resolution: 1px (Fine) or 5px (Coarse)
int stepSize = 1;

// System operation state
bool isCalibratedAndSaved = false;
Preferences preferences;

// ==============================================================================
// 4. INTERRUPT-DRIVEN ENCODER STATE
// ==============================================================================
volatile int k1Delta = 0;
volatile int k2Delta = 0;
volatile unsigned long lastK1IsrUs = 0;
volatile unsigned long lastK2IsrUs = 0;

void IRAM_ATTR isrK1() {
  unsigned long nowUs = micros();
  if (nowUs - lastK1IsrUs < 8000) return; // 8ms debounce filter
  lastK1IsrUs = nowUs;
  if (digitalRead(PIN_K1_DT) == HIGH) {
    k1Delta++;
  } else {
    k1Delta--;
  }
}

void IRAM_ATTR isrK2() {
  unsigned long nowUs = micros();
  if (nowUs - lastK2IsrUs < 8000) return; // 8ms debounce filter
  lastK2IsrUs = nowUs;
  // Direction configured so Clockwise moves edge to the Right (+X)
  if (digitalRead(PIN_K2_DT) == LOW) {
    k2Delta++;
  } else {
    k2Delta--;
  }
}

// Display refresh throttling
bool einkNeedsUpdate = true;
unsigned long lastInputActivityMs = 0;
const unsigned long EINK_DEBOUNCE_MS = 150;

// LED tactile blip timeout
unsigned long ledBlipUntilMs = 0;

// ==============================================================================
// 5. STATUS LED & TACTILE FEEDBACK
// ==============================================================================
void setStatusLED(uint8_t r, uint8_t g, uint8_t b) {
#ifdef RGB_BUILTIN
  rgbLedWrite(RGB_BUILTIN, r, g, b);
#endif
}

void triggerLedBlip(uint8_t r, uint8_t g, uint8_t b, unsigned long durationMs = 60) {
  setStatusLED(r, g, b);
  ledBlipUntilMs = millis() + durationMs;
}

void updateActiveCornerLED() {
  if (ledBlipUntilMs > 0 && millis() < ledBlipUntilMs) return;

  if (isCalibratedAndSaved) {
    setStatusLED(0, 80, 20); // 🟢 Bright Emerald Green: Calibration Complete
    return;
  }

  // Corner-specific color cues
  switch (currentCorner) {
    case CORNER_TOP_LEFT:
      setStatusLED(0, 30, 80);  // 🔵 Vivid Blue: Top-Left
      break;
    case CORNER_TOP_RIGHT:
      setStatusLED(70, 0, 70);  // 🟣 Magenta: Top-Right
      break;
    case CORNER_BOTTOM_RIGHT:
      setStatusLED(80, 30, 0);  // 🟠 Amber: Bottom-Right
      break;
    case CORNER_BOTTOM_LEFT:
      setStatusLED(0, 60, 40);  // 🟢 Teal: Bottom-Left
      break;
  }
}

// ==============================================================================
// 6. E-PAPER DRAWING & VISUALIZATION
// ==============================================================================

/**
 * Draws the calibration interface to the GxEPD2 screen buffer.
 * - Solid double border outlining the active visible boundary.
 * - Bold marker and crosshair ticks on the active corner.
 * - Center telemetry HUD showing coordinates, dimensions, step resolution, and controls.
 */
void renderCalibrationScreen(bool finalSummary = false) {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);

  int width  = xMax - xMin + 1;
  int height = yMax - yMin + 1;

  // 1. Draw outer calibrated boundary box (2px solid black line for high contrast)
  display.drawRect(xMin, yMin, width, height, GxEPD_BLACK);
  if (width > 2 && height > 2) {
    display.drawRect(xMin + 1, yMin + 1, width - 2, height - 2, GxEPD_BLACK);
  }

  // 2. Corner crosshairs and active corner indicator
  // Corner coordinates:
  int cornerCoords[4][2] = {
    {xMin, yMin}, // 0: Top-Left
    {xMax, yMin}, // 1: Top-Right
    {xMax, yMax}, // 2: Bottom-Right
    {xMin, yMax}  // 3: Bottom-Left
  };

  for (int i = 0; i < 4; i++) {
    int cx = cornerCoords[i][0];
    int cy = cornerCoords[i][1];

    if (i == (int)currentCorner && !finalSummary) {
      // Prominent active corner marker: 8x8 filled square + crosshair brackets
      int boxX = constrain(cx - 3, 0, PANEL_WIDTH - 7);
      int boxY = constrain(cy - 3, 0, PANEL_HEIGHT - 7);
      display.fillRect(boxX, boxY, 7, 7, GxEPD_BLACK);

      // Corner target brackets
      int signX = (i == 1 || i == 2) ? -1 : 1;
      int signY = (i == 2 || i == 3) ? -1 : 1;
      display.drawFastHLine(cx, cy + (signY * 6), signX * 12, GxEPD_BLACK);
      display.drawFastVLine(cx + (signX * 6), cy, signY * 12, GxEPD_BLACK);
    } else {
      // Inactive corner: minimal 4x4 tick
      int boxX = constrain(cx - 1, 0, PANEL_WIDTH - 3);
      int boxY = constrain(cy - 1, 0, PANEL_HEIGHT - 3);
      display.drawRect(boxX, boxY, 3, 3, GxEPD_BLACK);
    }
  }

  // 3. Center Telemetry HUD card
  int cardW = 168;
  int cardH = 68;
  int cardX = (PANEL_WIDTH - cardW) / 2;
  int cardY = (PANEL_HEIGHT - cardH) / 2;

  // Clear card area so text is razor crisp
  display.fillRect(cardX, cardY, cardW, cardH, GxEPD_WHITE);
  display.drawRect(cardX, cardY, cardW, cardH, GxEPD_BLACK);

  // Card Header Banner
  display.fillRect(cardX + 1, cardY + 1, cardW - 2, 14, GxEPD_BLACK);
  display.setTextColor(GxEPD_WHITE);
  display.setFont();
  display.setTextSize(1);
  display.setCursor(cardX + 6, cardY + 4);

  if (finalSummary) {
    display.print("*** CALIBRATION SAVED ***");
  } else {
    display.printf("> %s", CORNER_NAMES[currentCorner]);
  }

  // Card Body Lines
  display.setTextColor(GxEPD_BLACK);

  // Line 1: Active dimensions & step mode
  display.setCursor(cardX + 6, cardY + 20);
  display.printf("Size: %3dx%-3d px", width, height);

  display.setCursor(cardX + 110, cardY + 20);
  if (finalSummary) {
    display.print("[NVS OK]");
  } else {
    display.printf("[%d px]", stepSize);
  }

  // Line 2: X Coordinates
  display.setCursor(cardX + 6, cardY + 32);
  display.printf("X: %3d -> %-3d  (dX: %d)", xMin, xMax, width);

  // Line 3: Y Coordinates
  display.setCursor(cardX + 6, cardY + 44);
  display.printf("Y: %3d -> %-3d  (dY: %d)", yMin, yMax, height);

  // Divider Line inside Card
  display.drawFastHLine(cardX + 3, cardY + 54, cardW - 6, GxEPD_BLACK);

  // Line 4: Controls Hint
  display.setCursor(cardX + 6, cardY + 58);
  if (finalSummary) {
    display.print("Reboot to restart calib");
  } else {
    display.print("Grn: Next | K1/2: Move | Red: Save");
  }

  // Commit buffer to panel via Fast Partial Refresh (~180ms) or Full Refresh on finish
  if (finalSummary) {
    display.display(false); // Full refresh for permanent pigment retention
  } else {
    display.display(true);  // Smooth partial refresh without flashing
  }
}

// ==============================================================================
// 7. SAVE CALIBRATION & GENERATE C++ CODE
// ==============================================================================
void saveAndFinishCalibration() {
  if (isCalibratedAndSaved) return;

  int width  = xMax - xMin + 1;
  int height = yMax - yMin + 1;

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║              SCREEN AREA FINDER: CALIBRATION COMPLETED                 ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.printf("║  Visible Boundary: X=[%3d..%3d], Y=[%3d..%3d]                            ║\n",
                xMin, xMax, yMin, yMax);
  Serial.printf("║  Calibrated Active Screen Size: %3d x %3d pixels                        ║\n",
                width, height);
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ Saving calibrated boundaries to ESP32-S3 NVS Flash (Preferences)...    ║");

  // Save to Preferences NVS namespace "screen_cal"
  preferences.begin("screen_cal", false);
  preferences.putInt("x_min",  xMin);
  preferences.putInt("y_min",  yMin);
  preferences.putInt("x_max",  xMax);
  preferences.putInt("y_max",  yMax);
  preferences.putInt("width",  width);
  preferences.putInt("height", height);
  preferences.putBool("calibrated", true);
  preferences.end();

  Serial.println("║ ✅ Successfully saved to NVS namespace: 'screen_cal'                   ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ Ready-to-copy C++ header macros for esp32_master.ino:                  ║");
  Serial.println("║                                                                        ║");
  Serial.printf("║   #define SCREEN_VISIBLE_X_MIN    %3d                                  ║\n", xMin);
  Serial.printf("║   #define SCREEN_VISIBLE_Y_MIN    %3d                                  ║\n", yMin);
  Serial.printf("║   #define SCREEN_VISIBLE_X_MAX    %3d                                  ║\n", xMax);
  Serial.printf("║   #define SCREEN_VISIBLE_Y_MAX    %3d                                  ║\n", yMax);
  Serial.printf("║   #define SCREEN_VISIBLE_WIDTH    %3d                                  ║\n", width);
  Serial.printf("║   #define SCREEN_VISIBLE_HEIGHT   %3d                                  ║\n", height);
  Serial.println("║                                                                        ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝\n");

  isCalibratedAndSaved = true;
  triggerLedBlip(0, 100, 20, 300); // Long Green Feedback
  renderCalibrationScreen(true);
}

// ==============================================================================
// 8. SETUP & INITIALIZATION
// ==============================================================================
void setup() {
  Serial.begin(115200);
  Serial.setTxTimeoutMs(0); // Non-blocking USB CDC transmit

  // Configure Internal Pull-Up Resistors for UI Inputs
  pinMode(PIN_K1_CLK, INPUT_PULLUP);
  pinMode(PIN_K1_DT,  INPUT_PULLUP);
  pinMode(PIN_K1_SW,  INPUT_PULLUP);

  pinMode(PIN_K2_CLK, INPUT_PULLUP);
  pinMode(PIN_K2_DT,  INPUT_PULLUP);
  pinMode(PIN_K2_SW,  INPUT_PULLUP);

  pinMode(PIN_START_BTN, INPUT_PULLUP);
  pinMode(PIN_STOP_BTN,  INPUT_PULLUP);

  // Attach Interrupts for Encoders
  attachInterrupt(digitalPinToInterrupt(PIN_K1_CLK), isrK1, FALLING);
  attachInterrupt(digitalPinToInterrupt(PIN_K2_CLK), isrK2, FALLING);

  // Set initial LED state
  updateActiveCornerLED();

  Serial.println("\n=======================================================");
  Serial.println("  ROBOSEN MASTER BLOCK - SCREEN AREA FINDER UTILITY");
  Serial.println("=======================================================");
  Serial.println("Instructions:");
  Serial.println("  1. Press Green Button (SW3) to switch active corner.");
  Serial.println("  2. Turn Left Knob (SW1) to adjust Vertical (Y) edge.");
  Serial.println("  3. Turn Right Knob (SW2) to adjust Horizontal (X) edge.");
  Serial.println("  4. Click either Knob to toggle Step Size (1px fine / 5px fast).");
  Serial.println("  5. Align outer box with 3D print bezel opening.");
  Serial.println("  6. Press Red Button (SW5) to Save and output dimensions.");
  Serial.println("-------------------------------------------------------");

  // Load existing calibration from NVS if available
  preferences.begin("screen_cal", true);
  if (preferences.getBool("calibrated", false)) {
    xMin = preferences.getInt("x_min", 40);
    yMin = preferences.getInt("y_min", 0);
    xMax = preferences.getInt("x_max", PANEL_WIDTH - 1);
    yMax = preferences.getInt("y_max", PANEL_HEIGHT - 1);
    Serial.printf("[INIT] Loaded prior calibration: X=[%d..%d], Y=[%d..%d], Size: %dx%d\n",
                  xMin, xMax, yMin, yMax, xMax - xMin + 1, yMax - yMin + 1);
  } else {
    Serial.println("[INIT] No prior calibration found. Initialized to calibrated default (X=[40..249], Y=[0..121]).");
  }
  preferences.end();

  // Initialize E-Paper SPI & Controller
  Serial.println("[INIT] Initializing 2.13\" E-Paper display (DEPG0213BN)...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));

  // Initialize display controller without violent boot flashing
  display.init(0, false, 10, false);
  display.setRotation(1); // 250 width x 122 height Landscape
  display.setFullWindow();

  // Initial draw
  renderCalibrationScreen(false);
  lastInputActivityMs = millis();
}

// ==============================================================================
// 9. MAIN EVENT LOOP
// ==============================================================================
void loop() {
  unsigned long now = millis();

  // LED feedback timeout
  if (ledBlipUntilMs > 0 && now >= ledBlipUntilMs) {
    ledBlipUntilMs = 0;
    updateActiveCornerLED();
  }

  if (isCalibratedAndSaved) {
    delay(50);
    return;
  }

  // --- 1. ROTARY ENCODER DELTA PROCESSING ---
  int d1 = 0, d2 = 0;
  if (k1Delta != 0 || k2Delta != 0) {
    noInterrupts();
    d1 = k1Delta; k1Delta = 0;
    d2 = k2Delta; k2Delta = 0;
    interrupts();
  }

  bool changed = false;

  // Left Knob (d1): Vertical (Y) adjustment
  if (d1 != 0) {
    int deltaY = d1 * stepSize;
    if (currentCorner == CORNER_TOP_LEFT || currentCorner == CORNER_TOP_RIGHT) {
      // Top Edge (yMin)
      yMin = constrain(yMin + deltaY, 0, yMax - MIN_ACTIVE_HEIGHT);
    } else {
      // Bottom Edge (yMax)
      yMax = constrain(yMax + deltaY, yMin + MIN_ACTIVE_HEIGHT, PANEL_HEIGHT - 1);
    }
    triggerLedBlip(0, 80, 80); // Cyan tactile blip
    changed = true;
  }

  // Right Knob (d2): Horizontal (X) adjustment
  if (d2 != 0) {
    int deltaX = d2 * stepSize;
    if (currentCorner == CORNER_TOP_LEFT || currentCorner == CORNER_BOTTOM_LEFT) {
      // Left Edge (xMin)
      xMin = constrain(xMin + deltaX, 0, xMax - MIN_ACTIVE_WIDTH);
    } else {
      // Right Edge (xMax)
      xMax = constrain(xMax + deltaX, xMin + MIN_ACTIVE_WIDTH, PANEL_WIDTH - 1);
    }
    triggerLedBlip(80, 0, 80); // Magenta tactile blip
    changed = true;
  }

  if (changed) {
    einkNeedsUpdate = true;
    lastInputActivityMs = now;
    Serial.printf("[MOVE] Corner: %-18s | Box: [%3d, %3d] -> [%3d, %3d] | Size: %3dx%-3d | Step: %dpx\n",
                  CORNER_NAMES[currentCorner], xMin, yMin, xMax, yMax,
                  xMax - xMin + 1, yMax - yMin + 1, stepSize);
  }

  // --- 2. GREEN BUTTON (SW3 - GPIO 14: CYCLE ACTIVE CORNER) ---
  int startRaw = digitalRead(PIN_START_BTN);
  static int lastStartRaw = HIGH;
  static unsigned long lastStartDebounce = 0;
  static bool startBtnPressed = false;
  static unsigned long startPressStart = 0;
  static bool startBtnHeld1500ms = false;

  if (startRaw != lastStartRaw) {
    lastStartDebounce = now;
    lastStartRaw = startRaw;
  }
  if (now - lastStartDebounce > 30) {
    if (startRaw == LOW && !startBtnPressed) {
      startBtnPressed = true;
      startPressStart = now;
      startBtnHeld1500ms = false;
      triggerLedBlip(0, 100, 0); // Green
    } else if (startRaw == LOW && startBtnPressed) {
      if (!startBtnHeld1500ms && (now - startPressStart >= 1500)) {
        startBtnHeld1500ms = true;
        Serial.println("\n[BUTTON] 🎯 Green Button Hold (1.5s): Finishing & Saving Calibration...");
        saveAndFinishCalibration();
      }
    } else if (startRaw == HIGH && startBtnPressed) {
      startBtnPressed = false;
      unsigned long duration = now - startPressStart;
      if (!startBtnHeld1500ms && duration >= 30 && duration < 1500) {
        // Short click: cycle active corner
        currentCorner = (ActiveCorner)((currentCorner + 1) % 4);
        Serial.printf("\n[CORNER SWITCH] Active Corner is now: %s\n", CORNER_NAMES[currentCorner]);
        updateActiveCornerLED();
        einkNeedsUpdate = true;
        lastInputActivityMs = now;
      }
    }
  }

  // --- 3. KNOB PUSH SWITCHES (TOGGLE STEP RESOLUTION: 1px / 5px) ---
  int k1SwRaw = digitalRead(PIN_K1_SW);
  int k2SwRaw = digitalRead(PIN_K2_SW);
  static int lastKSwCombined = HIGH;
  static unsigned long lastKSwDebounce = 0;
  static bool kSwPressed = false;

  int currentKSwCombined = (k1SwRaw == LOW || k2SwRaw == LOW) ? LOW : HIGH;
  if (currentKSwCombined != lastKSwCombined) {
    lastKSwDebounce = now;
    lastKSwCombined = currentKSwCombined;
  }
  if (now - lastKSwDebounce > 30) {
    if (currentKSwCombined == LOW && !kSwPressed) {
      kSwPressed = true;
      stepSize = (stepSize == 1) ? 5 : 1;
      triggerLedBlip(80, 80, 0); // Yellow
      Serial.printf("\n[STEP RESOLUTION] Toggled to: %d px (%s)\n",
                    stepSize, (stepSize == 1) ? "FINE" : "COARSE");
      einkNeedsUpdate = true;
      lastInputActivityMs = now;
    } else if (currentKSwCombined == HIGH && kSwPressed) {
      kSwPressed = false;
    }
  }

  // --- 4. RED BUTTON (SW5 - GPIO 2: SAVE & FINISH CALIBRATION) ---
  int stopRaw = digitalRead(PIN_STOP_BTN);
  static int lastStopRaw = HIGH;
  static unsigned long lastStopDebounce = 0;
  static bool stopBtnPressed = false;
  static unsigned long stopPressStart = 0;

  if (stopRaw != lastStopRaw) {
    lastStopDebounce = now;
    lastStopRaw = stopRaw;
  }
  if (now - lastStopDebounce > 30) {
    if (stopRaw == LOW && !stopBtnPressed) {
      stopBtnPressed = true;
      stopPressStart = now;
      triggerLedBlip(100, 0, 0); // Red
    } else if (stopRaw == HIGH && stopBtnPressed) {
      stopBtnPressed = false;
      unsigned long duration = now - stopPressStart;
      if (duration >= 30) {
        Serial.println("\n[BUTTON] 🛑 Red Button Clicked: Finishing & Saving Calibration...");
        saveAndFinishCalibration();
      }
    }
  }

  // --- 5. DEBOUNCED E-PAPER REFRESH ---
  // When knobs are rotated rapidly, debounce display refresh so the screen updates smoothly
  if (einkNeedsUpdate && (now - lastInputActivityMs >= EINK_DEBOUNCE_MS)) {
    einkNeedsUpdate = false;
    renderCalibrationScreen(false);
  }

  delay(2);
}
