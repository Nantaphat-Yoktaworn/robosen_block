# Robosen K1 Master Block Firmware

> **Target MCU:** ESP32-S3 (Espressif ESP32-S3-DevKitC-1-N8R8 / N16R8)  
> **Source File:** [`esp32_master.ino`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/esp32_master.ino)  
> **Framework:** Arduino ESP32 Core 3.x / ESP-IDF  
> **Display:** 2.13" SPI E-Paper (DEPG0213BN / SSD1680, 122×250, GxEPD2)  
> **Wireless:** BLE 4.2 / 5.0 Client (Robosen K1 Humanoid Robot GATT Protocol)  
> **Status:** Fully Functional Prototype #01 + Firmware Update Required for Hardware Revisions  

---

## 1. System Overview

The Master Block firmware serves as the tangible programming hub for the Robosen K1 humanoid robot:
1. **Interactive Dual-Knob UI**:
   - **Knob 1 (Action Selector)**: Cycles through pre-programmed robot actions (Walk Forward, Walk Backward, Turn Left, Turn Right, Punch Left, Push-ups, Wave Hand).
   - **Knob 2 (Parameter Adjuster)**: Adjusts action parameters (step count, degrees, repetition counts).
2. **Config Dock (UART1, GPIO 17/18)**:
   - Detects when a smart action block (CH32V003) is docked onto the 4-pin magnetic dock.
   - Reads the block token, verifies connection, and writes configuration commands (`0xCF`).
3. **Run Chain Bus (UART2, GPIO 15/16)**:
   - Initiates Phase 1 Discovery (`0xAA`) down the physical block chain to sequence and read all snapped-in blocks.
   - Broadcasts Phase 2 Step Execution (`0xBB`) while streaming BLE commands to the robot.
4. **E-Paper Display (SPI, GPIO 4, 5, 6, 7, 21, 38)**:
   - Displays real-time action icons, parameter values, docked block status, and system feedback with 746ms partial refresh.
5. **BLE Client Gateway**:
   - Scans and connects to the Robosen K1 robot (Service `0xFFE0`, Characteristic `0xFFE1`), translating block sequences into Robosen motor/animation opcodes.

---

## 2. Hardware Pinout Mapping

| Subsystem | Signal Name | ESP32-S3 Pin | Hardware Component | Mode / Role |
|:---|:---|:---|:---|:---|
| **Power Sense** | `BATSENSE` | **GPIO 1** | $100\text{ k}\Omega : 100\text{ k}\Omega$ Divider + $100\text{ nF}$ filter | ADC1_CH0 Battery Voltage Monitor |
| **User Input** | `BTN_STOP` | **GPIO 2** | `SW5` (12×12mm Tactile Button - Red) | Active LOW (Stop / Cancel / Back) |
| **User Input** | `BTN_START` | **GPIO 14** | `SW3` (12×12mm Tactile Button - Green) | Active LOW (Confirm / Start / Run) |
| **Knob 1 (Action)** | `K1_CLK` | **GPIO 8** | `SW1` (KY-040 Rotary Encoder) | Quadrature Phase A |
| | `K1_DT` | **GPIO 9** | `SW1` (KY-040 Rotary Encoder) | Quadrature Phase B |
| | `K1_SW` | **GPIO 10** | `SW1` (KY-040 Push Switch) | Action Select Confirmation |
| **Knob 2 (Param)** | `K2_CLK` | **GPIO 11** | `SW2` (KY-040 Rotary Encoder) | Quadrature Phase A |
| | `K2_DT` | **GPIO 12** | `SW2` (KY-040 Rotary Encoder) | Quadrature Phase B |
| | `K2_SW` | **GPIO 13** | `SW2` (KY-040 Push Switch) | Parameter Reset / BLE Save |
| **E-Paper Display** | `EPD_BUSY` | **GPIO 4** | `DISP1` (DEPG0213BN 1×08 Header) | Display Busy status flag |
| | `EPD_RES` | **GPIO 5** | `DISP1` | Hardware reset line |
| | `EPD_DC` | **GPIO 6** | `DISP1` | Data / Command control |
| | `EPD_CS` | **GPIO 7** | `DISP1` | SPI Chip Select |
| | `EPD_SCK` | **GPIO 21** | `DISP1` | SPI Clock (`SCL`) |
| | `EPD_MOSI` | **GPIO 38** | `DISP1` | SPI MOSI Data (`SDA`) |
| **Config Dock** | `CFG_TX` | **GPIO 17** | `J1` (Pogo 4-Pin Dock) | Master UART1 TX $\to$ Block PD6 RX |
| | `CFG_RX` | **GPIO 18** | `J1` (Pogo 4-Pin Dock) | Master UART1 RX $\gets$ Block PD5 TX |
| **Run Chain Bus** | `CHAIN_TX` | **GPIO 15** | `J2` (Pogo 4-Pin Run Port) + $10\text{ k}\Omega$ pull-up | Master UART2 TX $\to$ Block 1 PD6 RX |
| | `CHAIN_RX` | **GPIO 16** | `J2` (Pogo 4-Pin Run Port) + $10\text{ k}\Omega$ pull-up | Master UART2 RX $\gets$ End Block Return |
| **Status LED** | `RGB_BUILTIN` | **GPIO 48** | Onboard WS2812 NeoPixel | System Status Indicator |

---

## 3. Required Firmware Updates for Hardware Revisions

The hardware carrier motherboard (`hardware/kicad/`) has been updated with two critical features that require firmware enhancements:

### 3.1 New Red Push Button (`SW5` — Stop / Cancel / Back on `GPIO 2`)

> [!IMPORTANT]
> **Firmware Action Required:** The current firmware in [`esp32_master.ino`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/esp32_master.ino) only defines and monitors `PIN_START_BTN` (`GPIO 14`). It must be updated to support the new **Red Tactile Push Button** (`SW5`, `GPIO 2`).

#### Rationale & UI Roles:
1. **Emergency Stop & Run Abort**:
   - During program execution (`STATE_RUNNING`), pressing `BTN_STOP` immediately aborts chain broadcasting, turns off the active glowing blocks, and sends emergency stop packets (`0x00` / idle pose) to the Robosen K1 robot.
2. **Cancel & Back Navigation**:
   - In UI menus or docking modes, pressing `BTN_STOP` cancels the active selection, resets parameter edits, or returns to the home screen without committing changes.
3. **BLE Disconnect / Sleep**:
   - Long-pressing `BTN_STOP` (3 seconds) cleanly disconnects the BLE session or puts the master block into deep sleep.

#### Recommended Code Implementation:
```cpp
// --- PUSH BUTTON DEFINITIONS ---
const int PIN_START_BTN = 14;  // Green Button (Confirm / Start / Run) - Active LOW
const int PIN_STOP_BTN  = 2;   // Red Button (Cancel / Stop / Back)    - Active LOW

void setupButtons() {
  pinMode(PIN_START_BTN, INPUT_PULLUP);
  pinMode(PIN_STOP_BTN,  INPUT_PULLUP);
}

void handleButtons() {
  // --- Check Red Stop/Cancel Button ---
  static bool lastStopState = HIGH;
  static uint32_t stopPressTime = 0;
  bool stopState = digitalRead(PIN_STOP_BTN);

  if (lastStopState == HIGH && stopState == LOW) {
    stopPressTime = millis();
  } else if (lastStopState == LOW && stopState == HIGH) {
    uint32_t duration = millis() - stopPressTime;
    if (duration > 50 && duration < 2000) {
      // Short press: Cancel current action / Emergency halt
      handleStopCancelPress();
    }
  } else if (stopState == LOW && (millis() - stopPressTime >= 3000)) {
    // 3-second hold: BLE Disconnect / Reset
    handleEmergencyReset();
    stopPressTime = millis() + 10000; // prevent duplicate trigger
  }
  lastStopState = stopState;
}

void handleStopCancelPress() {
  if (systemState == STATE_RUNNING) {
    Serial.println("[HALT] Red Button Pressed! Halting robot sequence...");
    sendRobosenHaltCommand();
    stopChainExecution();
    setStatusLED(255, 0, 0); // Red
  } else if (isBlockDocked) {
    Serial.println("[CANCEL] Dock configuration cancelled.");
    isBlockDocked = false;
    updateDisplayHome();
  }
}
```

---

### 3.2 Battery Percentage Monitoring (`BATSENSE` on `GPIO 1` / ADC1_CH0)

> [!IMPORTANT]
> **Firmware Action Required:** The carrier motherboard features a 1:1 precision voltage divider ($R_3=100\text{ k}\Omega, R_4=100\text{ k}\Omega$) with a $100\text{ nF}$ filter capacitor ($C_1$) connected to `GPIO 1` (ADC1 Channel 0). The firmware must read this ADC channel and render battery level on the E-Paper display.

#### Engineering Details:
- **Voltage Calculation**:
  $$V_{BAT} = 2 \times V_{ADC1\_CH0}$$
- **Li-ion Voltage Curve**:
  - $4.20\text{ V}$ = 100% (Fully charged)
  - $3.85\text{ V}$ = 75%
  - $3.70\text{ V}$ = 50% (Nominal)
  - $3.50\text{ V}$ = 25%
  - $3.30\text{ V}$ = 5% (Low battery warning)
  - $3.00\text{ V}$ = 0% (Shutdown threshold)
- **ADC1 Compatibility**:
  - Uses **ADC1_CH0** (`GPIO 1`), which functions concurrently with Bluetooth Low Energy (unlike ADC2 pins which are shared with RF Wi-Fi/BT subsystems).

#### Recommended Code Implementation:
```cpp
const int PIN_BATSENSE = 1; // ESP32-S3 ADC1_CH0

float readBatteryVoltage() {
  // Read calibrated millivolts using ESP32-S3 eFuse calibration
  uint32_t rawMv = analogReadMilliVolts(PIN_BATSENSE);
  // 1:1 divider (R3 = 100k, R4 = 100k) => Vbat = 2 * Vadc
  float vbat = (rawMv * 2.0f) / 1000.0f;
  return vbat;
}

int calculateBatteryPercent(float vbat) {
  if (vbat >= 4.20f) return 100;
  if (vbat <= 3.20f) return 0;
  // Linear approximation over 3.2V to 4.2V range
  int pct = (int)((vbat - 3.20f) / (4.20f - 3.20f) * 100.0f);
  return constrain(pct, 0, 100);
}

void renderBatteryIcon(int x, int y, int percent) {
  // Draw battery frame on E-Paper display header
  display.drawRect(x, y, 22, 10, GxEPD_BLACK);
  display.fillRect(x + 22, y + 2, 2, 6, GxEPD_BLACK); // terminal
  int fillW = map(percent, 0, 100, 0, 18);
  display.fillRect(x + 2, y + 2, fillW, 6, GxEPD_BLACK);
}
```

---

### 3.3 E-Paper Display Module Footprint Alignment

- The hardware display footprint (`EPaper_2.13in_Header_1x08`) has been updated to the exact **$71.0\text{ mm} \times 30.0\text{ mm}$** outer PCB dimensions with an active area of **$48.55\text{ mm} \times 23.71\text{ mm}$** ($250 \times 122$ pixels).
- The existing `GxEPD2_213_BN` driver configuration remains fully compatible and operational.

---

## 4. Verification & Testing Checklist

When deploying the firmware update:
- [ ] Verify `pinMode(2, INPUT_PULLUP)` is configured during `setup()`.
- [ ] Test Red Button single press triggers `handleStopCancelPress()` and aborts active BLE commands.
- [ ] Test Red Button long press (3s) triggers clean disconnect.
- [ ] Verify `analogReadMilliVolts(1)` returns between $1500\text{ mV}$ and $2100\text{ mV}$ when powered by a $3.0\text{V} - 4.2\text{V}$ cell.
- [ ] Check E-Paper display renders the battery icon and percentage in the status header.
- [ ] Ensure Bluetooth BLE streaming to Robosen K1 operates without ADC conflicts.
