# Robosen K1 Master Block Firmware

> **Target MCU:** ESP32-S3 (Espressif ESP32-S3-DevKitC-1-N8R8 / N16R8)  
> **Source File:** [`esp32_master.ino`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/esp32_master.ino)  
> **Framework:** Arduino ESP32 Core 3.x / ESP-IDF  
> **Display:** 2.13" SPI E-Paper (DEPG0213BN / SSD1680, 122×250, GxEPD2)  
> **Wireless:** BLE 4.2 / 5.0 Client (Robosen K1 Humanoid Robot GATT Protocol)  
> **Status:** Fully Functional Prototype #01 — Updated & Verified with Carrier PCB Configuration (4 UI Inputs: 2 Encoders + 2 Buttons)

---

## 1. System Overview

The Master Block firmware serves as the tangible programming hub for the Robosen K1 humanoid robot:
1. **Interactive 4-Input Control Surface**:
   - **Knob 1 (Action Selector - SW1)**: Cycles through pre-programmed robot actions (Walk Forward, Walk Backward, Turn Left, Turn Right, Punch Left, Push-ups, Wave Hand) and menu items.
   - **Knob 2 (Parameter Adjuster - SW2)**: Adjusts action parameters (step count, degrees, repetition counts).
   - **Green Start Button (SW3 - GPIO 14)**: Confirm, initiate run chain execution (`0xAA`/`0xBB`), or enter Teacher BLE Pairing discovery (3s hold).
   - **Red Stop Button (SW5 - GPIO 2)**: Emergency halt / run chain abort, cancel action / dismiss docked config, or cleanly disconnect BLE session (3s hold).
2. **Battery Voltage Monitor (BATSENSE - GPIO 1 / ADC1_CH0)**:
   - Reads precision 1:1 voltage divider with 100nF filter, calculating live Li-ion battery voltage and percentage.
   - Renders battery gauge icon and percentage on the E-Paper status header.
3. **Config Dock (UART1, GPIO 17/18)**:
   - Detects when a smart action block (CH32V003) is docked onto the 4-pin magnetic dock.
   - Reads the block token, verifies connection, and writes configuration commands (`0xCF`).
4. **Run Chain Bus (UART2, GPIO 15/16)**:
   - Initiates Phase 1 Discovery (`0xAA`) down the physical block chain to sequence and read all snapped-in blocks.
   - Broadcasts Phase 2 Step Execution (`0xBB`) while streaming BLE commands to the robot.
   - Instant emergency halt capability via Red Stop Button.
5. **E-Paper Display (SPI, GPIO 4, 5, 6, 7, 21, 38)**:
   - Displays real-time action icons, parameter values, docked block status, battery meter, and 4-input UI hints with fast partial refresh.
6. **BLE Client Gateway**:
   - Scans and connects to the Robosen K1 robot (Service `0xFFE0`, Characteristic `0xFFE1`), translating block sequences into Robosen motor/animation opcodes.

---

## 2. Hardware Pinout Mapping

| Subsystem | Signal Name | ESP32-S3 Pin | Hardware Component | Mode / Role |
|:---|:---|:---|:---|:---|
| **Power Sense** | `BATSENSE` | **GPIO 1** | $100\text{ k}\Omega : 100\text{ k}\Omega$ Divider + $100\text{ nF}$ filter | ADC1_CH0 Battery Voltage Monitor |
| **User Input 4** | `BTN_STOP` | **GPIO 2** | `SW5` (12×12mm Tactile Button - Red) | Active LOW (Emergency Stop / Cancel / Back) |
| **User Input 3** | `BTN_START` | **GPIO 14** | `SW3` (12×12mm Tactile Button - Green) | Active LOW (Confirm / Start / Run) |
| **User Input 1** | `K1_CLK` | **GPIO 8** | `SW1` (KY-040 Rotary Encoder) | Quadrature Phase A |
| | `K1_DT` | **GPIO 9** | `SW1` (KY-040 Rotary Encoder) | Quadrature Phase B |
| | `K1_SW` | **GPIO 10** | `SW1` (KY-040 Push Switch) | Action Select Confirmation |
| **User Input 2** | `K2_CLK` | **GPIO 11** | `SW2` (KY-040 Rotary Encoder) | Quadrature Phase A |
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

## 3. Implemented Hardware Revisions & Safety Logic

### 3.1 Red Push Button (`SW5` — Stop / Cancel / Back on `GPIO 2`)

The firmware implements comprehensive handling for the new **Red Tactile Push Button** (`SW5`, `GPIO 2`):
1. **Emergency Stop & Run Abort**:
   - Polled inside `abortableDelay()` during all turn, walk, and animation sequences.
   - Pressing `BTN_STOP` at any time instantly terminates motion execution, broadcasts an abort packet `[0xBB, 0x00, ...]` to turn off all instruction block LEDs, sends a Locomotion Stop (`0xFF, 0xFF, 0x02, 0x0C, 0x0E`) to lock robot posture, and shows emergency halt on the E-Paper display.
2. **Cancel & Back Navigation**:
   - In `STATE_ACTION_MENU`, dismisses active docked block configuration without writing to flash.
   - In `STATE_BLE_PAIRING_MENU` and `STATE_BLE_SCANNING`, cancels device selection and returns safely to the action menu.
3. **Clean Disconnect**:
   - Long-pressing `BTN_STOP` for 3 seconds cleanly disconnects the active BLE session.

### 3.2 Battery Percentage Monitoring (`BATSENSE` on `GPIO 1` / ADC1_CH0)

- Implemented `readBatteryVoltage()` reading calibrated millivolts via `analogReadMilliVolts(PIN_BATSENSE)`.
- Calculates accurate battery percentage using Li-ion discharge characteristics ($3.20\text{V} - 4.20\text{V}$).
- Renders real-time battery outline icon and dynamic fill level on the E-Paper status header.

---

## 4. Verification & Testing Checklist

- [x] Verified `pinMode(PIN_STOP_BTN, INPUT_PULLUP)` is configured during `setup()`.
- [x] Verified Red Button single press triggers `sendLocomotionStop()` and aborts active BLE commands.
- [x] Verified Red Button long press (3s) triggers clean BLE disconnect.
- [x] Verified `analogReadMilliVolts(PIN_BATSENSE)` with 1:1 voltage divider.
- [x] Verified E-Paper display renders battery meter and updated 4-input UI hints.
- [x] Successfully compiled using Arduino CLI for `esp32:esp32:esp32s3` (Zero warnings/errors).
