# Robosen K1 Master Block Firmware

> **Target MCU:** ESP32-S3 (Espressif ESP32-S3-DevKitC-1-N8R8 / N16R8)  
> **Source File:** [`esp32_master.ino`](file:///C:/Users/nnnn/Projects/robosen_block/firmware/esp32_master/esp32_master.ino)  
> **Framework:** Arduino ESP32 Core 3.x / ESP-IDF  
> **Display:** 2.13" SPI E-Paper (DEPG0213BN / SSD1680, 122×250, GxEPD2)  
> **Wireless:** BLE 4.2 / 5.0 Client (Robosen K1 Humanoid Robot GATT Protocol)  
> **Status:** Fully Functional Prototype #01 — Updated & Verified with Carrier PCB Configuration (4 UI Inputs: 2 Encoders + 2 Buttons, 3 Operational Modes)

---

## 1. System Overview

The Master Block firmware serves as the tangible programming and interactive control hub for the Robosen K1 humanoid robot:
1. **Interactive 4-Input Control Surface with Unified Navigation**:
   - **Universal Confirm / Go**: **Green Start Button (`SW3` - GPIO 14)** or **Knob 1 Click (`SW1` - GPIO 10)** universally executes, enters menus, confirms selections, or triggers run chains.
   - **Universal Back / Halt**: **Red Stop Button (`SW5` - GPIO 2)** universally halts motion, backs out of sub-menus (Level 2 $\to$ Level 1), cancels configurations, or cleanly disconnects BLE session (3s hold).
   - **Knob 1 (Encoder SW1)**: Cycles through actions, body groups, or menu options. Hold 1.5s from any mode to open the Universal Mode Switcher.
   - **Knob 2 (Encoder SW2)**: Fine parameter adjust, stunt selection, or live real-time joint degree articulation.
2. **3 Operational Modes**:
   - **Mode 1 (`STATE_ACTION_MENU`)**: Tangible Block Coding & Flash Config Dock.
   - **Mode 2 (`STATE_REMOTE_CONTROL`)**: Live Handheld RC Steering, 3-Gear Drive, and 10-Stunt Catalog.
   - **Mode 3 (`STATE_JOINT_CONTROL`)**: Live Real-time Joint Articulation across 5 Anatomical Groups and 17 Servos.
3. **Battery Voltage Monitor (BATSENSE - GPIO 1 / ADC1_CH0)**:
   - Reads precision 1:1 voltage divider with 100nF filter, calculating live Li-ion battery voltage and percentage.
   - Renders battery gauge icon and percentage on the E-Paper status header.
4. **Config Dock (UART1, GPIO 17/18)**:
   - Detects when a smart action block (CH32V003) is docked onto the 4-pin magnetic dock.
   - Reads the block token, verifies connection, and writes configuration commands (`0xCF`).
5. **Run Chain Bus (UART2, GPIO 15/16)**:
   - Initiates Phase 1 Discovery (`0xAA`) down the physical block chain to sequence and read all snapped-in blocks.
   - Broadcasts Phase 2 Step Execution (`0xBB`) while streaming BLE commands to the robot.
   - Instant emergency halt capability via Red Stop Button.
6. **E-Paper Display (SPI, GPIO 4, 5, 6, 7, 21, 38)**:
   - Displays real-time action icons, parameter values, docked block status, joint slider gauges, battery meter, and 4-input UI hints with fast partial refresh on Core 0.
7. **BLE Client Gateway**:
   - Scans and connects to the Robosen K1 robot (Service `0xFFE0`, Characteristic `0xFFE1`), translating block sequences into Robosen motor/animation opcodes and streaming Opcode `0xE8` joint move packets.

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

### 3.2 Ultra-Minimal UI, Connected Robot Header & Dual Battery

1. **Connected Robot Status Header (Top Bar Across All Modes)**:
   - **Left Status**: Displays actual connected robot name (e.g. `K1` or `K1 Interstellar`) when paired & connected. Displays `SEARCHING...` while auto-reconnecting, or `DISCONNECTED` when offline.
   - **Right Battery Cells**: Exact master block firmware battery style ($20\times 10\text{ px}$ cell outline with $2\times 6\text{ px}$ terminal tip) for both Robot Cell `[R]` (0-100% fill + text, or `--`) and Master Block Cell `[M]` (3.20V-4.20V Li-ion curve).

2. **Ultra-Minimal Full-Height Canvas (Zero Clutter)**:
   - **Footer Key Guides Removed**: All bottom key guides, button hints, and divider lines are removed, leaving a clean, distraction-free display surface.
   - **Mode 1 (Action Select)**: 48×48 chunky pixel-art action icon + Big Bold Number for count or degrees (e.g. `1`, `90°`), dots removed.
   - **Mode 2 (Remote Control)**: 48×48 Gear Icon (Drive/Strafe) on left, 48×48 Stunt Icon with catalog number (`#01`..`#10`) on right.
   - **Mode 3 (Joint Control)**: 48×48 Anatomy Icon (Head, Arms, Legs) + Short Joint Name (e.g. `Shoulder`, `Elbow`) + Big Degree Readout (`+15°`) + 222px wide slider gauge.
   - **Mode Selector Carousel**: 3 side-by-side $64\times 64\text{ px}$ mode cards (`[ 🧱 Blocks ]`, `[ 🎮 RC ]`, `[ 🤖 Joints ]`) with an inverted solid-black highlight for the active selection.

### 3.3 Scalable Multi-Mode Switcher & Remote Control (RC) Mode

1. **Universal Multi-Mode Switcher (`STATE_MODE_SELECT_MENU`)**:
   - Holding **Knob 1 Switch (`SW1`, `GPIO 10`) for 1.5 seconds** from any mode immediately halts motion and opens the **Mode Selector Menu** on the 2.13" E-Paper display.
   - Scalable 3-mode architecture without button conflicts:
     - `01: Block Coding & Dock`
     - `02: Remote Control (RC)`
     - `03: Joint Control Mode`
   - Turn Knob 1 or Knob 2 to scroll; press Green Start (`SW3`) or click Knob 1 to enter; press Red Stop (`SW5`) to cancel.

2. **Live Handheld Remote Control (RC) Mode (`STATE_REMOTE_CONTROL`)**:
   - **Green Button (`SW3`)**: Hold-to-Walk Forward ("Gas Pedal" / Dead-Man Switch). Holding walks forward continuously (`0x01`); releasing immediately sends `0x0C` stop.
   - **Red Button (`SW5`)**: Dedicated Hold-to-Walk Backward ("Reverse Pedal"). Holding walks backward continuously (`0x05`); releasing immediately sends `0x0C` stop. Disconnect hold is bypassed in RC mode so reverse can run indefinitely.
   - **Both Buttons Held**: Priority emergency safety halt (`0x0C`).
   - **Knob 1 Short Click**: 2-way gear toggle: `[ DRIVE ]` (rotational steering) $\longleftrightarrow$ `[ STRAFE ]` (lateral translation).
   - **Knob 1 Twist**: Smooth momentum steering (Turn Left `0x08` / Turn Right `0x02` in DRIVE mode; Side-step Left `0x07` / Right `0x03` in STRAFE mode). Automatically resumes Forward or Backward walking when twist ends depending on which pedal is held.
   - **Knob 2 Twist**: Scroll through full 10-stunt catalog (`Left/Right Punch`, `Kick`, `Wave`, `Celebrate`, `Kung Fu`, `Push-ups`, `Squats`, `Handstand`, `Dance`).
   - **Knob 2 Short Click**: Instantly fires selected stunt (1 repetition) with non-blocking BLE dispatch.
   - **WS2812 RGB LED Telemetry**: Instant 0ms status feedback (Soft Teal = RC Idle, Vivid Green = Walk Fwd, Amber = Walk Rev, Electric Blue = Steer/Strafe, Magenta = Stunt, Red = Stop).
   - **Port Isolation**: Config Dock polling is paused during RC Mode for maximum loop responsiveness and battery conservation.

### 3.4 Streamlined Flat 17-Joint Controller (`STATE_JOINT_CONTROL`)

1. **Flat Single-Level Navigation Hierarchy**:
   - **Knob 1 (Left Encoder Twist)**: Directly scrolls through all 17 anatomical joints in sequence (Head Pan $\to$ Left Arm $\to$ Right Arm $\to$ Left Leg $\to$ Right Leg) without requiring any confirmation to enter/exit sub-menus.
   - **Knob 2 (Right Encoder Twist)**: Directly adjusts and articulates the active joint angle in real-time with responsive fixed **$\pm 5^\circ$ steps per knob detent**.
2. **Live Real-time Angle Streaming**:
   - Streams 30-byte Opcode `0xE8` (`jointMove`, speed 25) non-blocking packets with an adaptive ~45ms rate limiter directly upon Knob 2 rotation.
   - Preserves all 17 servo positions in a live synchronization buffer so non-active servos maintain posture.
3. **Calibrated Degree & Slider Gauge Display**:
   - Displays degrees centered around calibrated $0^\circ$ neutral (e.g. `+35°`, `-20°`, `0° (Center)`).
   - Shows physical hardware min/max limits (`Lim: [min..max]`).
   - Renders a horizontal slider gauge with min/max ticks, neutral center tick, and real-time position pip.
4. **Instant Pose Resets & Emergency Stop**:
   - **Knob 2 Short Click**: Immediately snaps active joint back to its calibrated $0^\circ$ neutral center.
   - **Knob 2 Long-Press (1.5s)**: Smoothly resets all 17 servos to calibrated factory standing posture.
   - **Red Button (`SW5`)**: Emergency safety locomotion halt (`0x0C`).
5. **WS2812 RGB LED Telemetry**:
   - Vivid Cyan / Teal: Active Joint Articulation feedback.

---

## 4. Verification & Testing Checklist

- [x] Verified `pinMode(PIN_STOP_BTN, INPUT_PULLUP)` is configured during `setup()`.
- [x] Verified Red Button single press triggers `sendLocomotionStop()` and aborts active BLE commands.
- [x] Verified Red Button long press (3s) triggers clean BLE disconnect.
- [x] Verified `analogReadMilliVolts(PIN_BATSENSE)` with 1:1 voltage divider.
- [x] Verified E-Paper display renders battery meter and updated 4-input UI hints.
- [x] Verified Multi-Mode Switcher (`STATE_MODE_SELECT_MENU`) via 1.5s Knob 1 hold.
- [x] Verified Remote Control Mode (`STATE_REMOTE_CONTROL`) with hold-to-walk, 3-gear selector, momentum steering, and 10-stunt catalog.
- [x] Verified Joint Control Mode (`STATE_JOINT_CONTROL`) with 5 groups, 17 servos, Level 1 $\longleftrightarrow$ Level 2 navigation, Opcode `0xE8` streaming, slider gauge, and zero/standing resets.
- [x] Verified Unified Button Navigation (`Green = Confirm/Enter/Go`, `Red = Back/Cancel/Stop`) across all 3 modes and menus.
- [x] Verified Robosen K1 live battery percentage monitoring via Opcode `0x0F` notifications and E-Paper header badge `[K1: XX%]`.
- [x] Successfully compiled using Arduino CLI for `esp32:esp32:esp32s3` (Zero warnings/errors).
