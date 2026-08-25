# node-red-contrib-robosen-block

> **Custom Node-RED Palette:** Tangible Modular Coding Block Simulator (2-Phase Binary Protocol V2 with CRC-8 & CH32V003 Smart Blocks) + Persistent Robosen K1 BLE Robot Controller.  
> **Package Version:** `2.0.0` | **License:** Apache-2.0

---

## 1. Overview & 2-Phase Protocol Architecture

This custom Node-RED palette simulates the **physical modular tangible coding block system** for the **Robosen K1** humanoid robot.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       NODE-RED SIMULATED SIGNAL FLOW                                   │
│                                                                                                        │
│  [ Master Block ] ──Pin 3 (TX)──► [ Smart Block 1 ] ──Pin 3 (TX)──► [ Smart End Terminator ]           │
│  (Emits Seed 0xAA)                (+ Token 0x01, Param 3)           (Validates CRC-8 & Loops to Pin 4) │
│        ▲                                                                    │                          │
│        └──────────────────── Pin 4 Return RX & Broadcast Bus ───────────────┘                          │
│                     │                                                                                  │
│                     ├──────────────────────────────────────────────┐                                   │
│                     ▼ (Phase 1: Binary Return)                     ▼ (Phase 2: Live 0xBB Broadcast)    │
│             [ Master Parser & BLE Queue ]                 [ Smart Block 1 LED: Bright Green! ]         │
│                     │                                                                                  │
│                     ▼ (Bluetooth Low Energy 4.2)                                                       │
│           [ Robosen K1 Robot ]                                                                         │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### ⚡ 2-Phase Bi-Directional Protocol Architecture:
- **Phase 1 (Discovery & Program Compilation - `0xAA`):**  
  Master Block emits a binary seed frame `[0xAA, Len=0, Count=0, CRC]`. Each connected **Smart Block** discovers its physical index (`#1, #2...`), appends its Token ID & Parameter, recalculates CRC-8, and forwards downstream until the **Smart End Block** loops the verified program back to Master RX (Pin 4).
- **Phase 2 (Real-Time Execution & WS2812B LED Tracking - `0xBB`):**  
  As the Master Block executes each step on the physical robot, it broadcasts `[0xBB, ActiveStep, TotalSteps, CRC]` across Pin 4. The corresponding physical block's **WS2812B RGB LED glows bright pulsing green** in real time!
- **Persistent BLE Connection:**  
  Master Block maintains a long-lived BLE link via background Python daemon (`scripts/k1_ble_daemon.py`) with dynamic 100% action completion ACK resolution.

---

## 2. Palette Node Catalog (Version 2.0)

| Node | Category | Color | Type | Description |
| :--- | :--- | :--- | :--- | :--- |
| **`robosen-master`** | `Robosen Block` | 🔴 `#E53935` | Gateway / Controller | **Master Block:** Auto-connects to robot via BLE. Clickable Start button. Emits Phase 1 seed frame (`0xAA`) on Pin 3 TX, verifies CRC-8 on loopback, and broadcasts Phase 2 execution frames (`0xBB`) on Pin 4. |
| **`robosen-smart-block`** | `Robosen Block` | 🔵 `#0277BD` | Instruction Block | **Smart Block (CH32V003):** Features interactive Push Button (Action Selector) and Rotary Knob (Parameter Adjuster). Auto-discovers its sequence index and illuminates **bright pulsating green** when actively executing. |
| **`robosen-smart-end`** | `Robosen Block` | 🟢 `#2E7D32` | Terminator | **Smart End Terminator:** Active end block that verifies CRC-8 checksum, appends framing footer `0x55`, and loops data into Pin 4 Return RX. Includes fault injection toggle for testing CRC errors. |
| **`robosen-protocol-monitor`**| `Robosen Block` | 🔘 `#607D8B` | Bus Analyzer | **Protocol Bus Analyzer & Sniffer:** Real-time inspector for serial frames. Displays raw hex bytes, decoded tokens, parameters, and CRC verification status (`VALID` / `CORRUPT`). |
| **`robosen-tester`** | `Robosen Block` | 🟣 `#7B1FA2` | Controller / Tester | **Direct Action Tester:** Standalone controller node with instant action triggering, live telemetry dashboard card, and BLE connection management. |
| **`robosen-instruction`** | `Robosen Block` | 🔷 `#0288D1` | Legacy Instruction | **Legacy Instruction Block:** 1-action block appending CSV command tokens (V1 backwards compatibility). |
| **`robosen-end`** | `Robosen Block` | ⚫ `#616161` | Legacy Terminator | **Legacy End Block:** Passive loopback terminator bridge (V1 backwards compatibility). |

---

## 3. Node Specifications & Details

### 3.1 `robosen-master` (Master Block Controller)
- **Inputs:** 1 (Pin 4 Return RX Rail - receives compiled binary frame `0xAA` or legacy CSV string).
- **Outputs:**
  - **Output 1 (Pin 3 Downstream TX):** Emits `0xAA` seed frame `[0xAA, 0x00, 0x00, 0x00, 0x55]`.
  - **Output 2 (Telemetry & Status):** Emits real-time execution progress, active step details, robot telemetry, and errors.
  - **Output 3 (Pin 4 RX Broadcast Bus):** Broadcasts `0xBB` active step frames `[0xBB, StepNum, TotalSteps, CRC, 0x55]` to trigger real-time LED illumination on Smart Blocks.
- **Interactive Features:**
  - Clickable button on the node canvas triggers `startChain()`.
  - Edit dialog properties panel contains a live robot status card showing connection state, battery percentage, volume, firmware version, and manual Connect / Disconnect / Query Status buttons.

### 3.2 `robosen-smart-block` (Smart Multi-Action Block)
- **Inputs:** 2 (Input 1: Pin 3 Downstream In; Input 2: Pin 4 Broadcast Bus In).
- **Outputs:** 1 (Pin 3 Downstream Out to next block).
- **Interactive Controls:**
  - Push Button action selector (cycles Walk $\to$ Turn $\to$ Punch $\to$ Kung Fu $\to$ Dance $\to$ Delay).
  - Rotary Knob parameter adjuster (Steps 1–10, Angle 45°–180°, Reps 1–5, Delay 1–5s).
- **Status Badges:** Displays dynamic action mode color, and turns **Bright Pulsing Green** when active step matches its assigned index.

### 3.3 `robosen-smart-end` (Smart Active Terminator)
- **Inputs:** 1 (Pin 3 Downstream In).
- **Outputs:** 1 (Pin 4 Return RX Rail back to Master Block).
- **Features:**
  - Validates CRC-8 checksum of entire chain payload.
  - Appends `0x55` frame footer.
  - Includes **Fault Injection** toggle in properties dialog to simulate CRC corruption for error handling validation.

### 3.4 `robosen-protocol-monitor` (Protocol Bus Sniffer)
- **Inputs:** 1 (Connects to any bus tap or loopback rail).
- **Outputs:** 1 (Emits decoded packet JSON for downstream nodes or dashboard).
- **Features:** Displays live packet inspector table in node status (Header, Length, Count, Decoded Token sequence, and CRC validation badge).

### 3.5 `robosen-tester` (Direct Action Tester)
- **Inputs:** 1 (Accepts action string name in `msg.payload` or `msg.action`).
- **Outputs:** 1 (Emits execution results, progress, and telemetry).
- **Features:**
  - Canvas button triggers immediate execution of selected action.
  - Properties panel contains a direct execution menu, live battery & telemetry card, and connection toggles.

---

## 4. HTTP Admin REST API Endpoints

The palette registers administrative REST endpoints for interactive web control:

### Master Block Endpoints (`/robosen-master/:id`)
- `POST /robosen-master/:id/trigger` - Triggers Phase 1 start chain.
- `GET /robosen-master/:id/info` - Queries live connection status, battery, volume, and firmware info.
- `POST /robosen-master/:id/connect` - Triggers manual BLE connection to K1.
- `POST /robosen-master/:id/disconnect` - Triggers manual BLE disconnection.
- `POST /robosen-master/:id/status` - Queries robot telemetry status (`0x0F`).

### Action Tester Endpoints (`/robosen-tester/:id`)
- `POST /robosen-tester/:id/trigger` - Executes configured action.
- `POST /robosen-tester/:id/execute` - Executes arbitrary action specified in JSON body (`{ "action": "kung_fu" }`).
- `GET /robosen-tester/:id/info` - Queries tester node status and robot info.
- `POST /robosen-tester/:id/connect` - Connects BLE daemon.
- `POST /robosen-tester/:id/disconnect` - Disconnects BLE daemon.
- `POST /robosen-tester/:id/status` - Queries status from robot.

---

## 5. Token Catalog & LED Color Table

| Token ID | Action Name | Label | Default Param | Param Unit | LED Color |
| :---: | :--- | :--- | :---: | :--- | :---: |
| `0x01` | `walk` | Walk Forward | `3` | Steps | 🔵 `#1E88E5` |
| `0x02` | `move_backward` | Walk Backward | `3` | Steps | 🔵 `#1565C0` |
| `0x03` | `turn_left` | Turn Left | `90` | Degrees | 🔷 `#00ACC1` |
| `0x04` | `turn_right` | Turn Right | `90` | Degrees | 🔷 `#00ACC1` |
| `0x07` | `move_left` | Side-Step Left | `2` | Steps | 🟦 `#039BE5` |
| `0x08` | `move_right` | Side-Step Right | `2` | Steps | 🟦 `#039BE5` |
| `0x10` | `punch_left` | Left Punch | `1` | Style | 🔴 `#E53935` |
| `0x11` | `punch_right` | Right Punch | `1` | Style | 🔴 `#D32F2F` |
| `0x12` | `kung_fu` | Kung Fu Stunt | `1` | Routine | 🟠 `#FB8C00` |
| `0x13` | `boogaloo` | Boogaloo Dance | `1` | Style | 🟣 `#8E24AA` |
| `0x14` | `push_ups` | Push-ups | `2` | Reps | 🟤 `#6D4C41` |
| `0x15` | `handstand` | Handstand | `1` | Hold | 🟤 `#6D4C41` |
| `0x16` | `single_kick` | Single Kick | `1` | Type | 🔴 `#E53935` |
| `0x17` | `do_squats` | Do Squats | `2` | Reps | 🟢 `#43A047` |
| `0x18` | `say_hello` | Say Hello | `1` | Variant | 🩵 `#00897B` |
| `0x19` | `celebrate` | Celebrate Cheer| `1` | Style | 🟡 `#FDD835` |
| `0x20` | `head_pan` | Head Pan | `122` | Angle | 🩵 `#00897B` |
| `0x30` | `delay` | Wait Delay | `2` | Seconds | 🟡 `#FBC02D` |
| `0x40` | `repeat` | Repeat Loop | `2` | Count | 🟢 `#7CB342` |

---

## 6. How to Install & Import Simulation Flows

### 6.1 Installation
To use this palette in your local Node-RED instance:

```powershell
# Method 1: Link via npm link or directory junction
cd ~/.node-red
npm install /path/to/robosen_block/node-red-contrib-robosen-block

# Method 2: Windows NTFS Directory Junction
cmd /c mklink /J "%USERPROFILE%\.node-red\node_modules\node-red-contrib-robosen-block" "C:\Users\poomz\nnnn\robosen_block\node-red-contrib-robosen-block"
```

### 6.2 Import the 2-Phase Smart Block Flow (Recommended)
1. Launch Node-RED (`node-red` in terminal, open `http://127.0.0.1:1880`).
2. Open Menu $\to$ **Import** $\to$ select [`examples/robosen_smart_block_flow.json`](examples/robosen_smart_block_flow.json).
3. Click **Deploy**.
4. Click the button on the **Master Block** node to compile the sequence and watch each block turn bright green as the robot executes!

### 6.3 Import the Legacy Simulation Flow
Import [`examples/robosen_simulator_flow.json`](examples/robosen_simulator_flow.json) for single-action CSV chain testing.
