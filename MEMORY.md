# RobosenJS & Tangible Coding Block System: Master Project Memory

> **System Overview:** Programmatic Control (Node.js & Python SDK), Custom Node-RED Tangible Block Simulator Palette, and Bluetooth Low Energy (BLE) Reverse Engineering for the **Robosen K1 / Interstellar Scout K1 Series** Humanoid Robot.  
> **Last Updated:** August 23, 2026  
> **FCC ID:** `2ATNWK1` | **Live Verified Robot ID:** `K1-00457` (`3C:A5:51:94:97:70`) | **Firmware:** `VER:3.03L`

---

## 1. Project Architecture & File Organization

```
robosen_block/
├── bin/
│   └── k1.js                             # Node.js CLI executable wrapper
├── recordings/
│   └── K1/
│       └── test.json                     # Recorded joint keyframe motion sequences
├── scripts/
│   ├── control.js                        # Gamepad / Keyboard controller runner (Node.js)
│   ├── demo.js                           # Quick demo choreography script (Node.js)
│   ├── main.js                           # Standard startup & health check script (Node.js)
│   ├── program.js                        # Scripted robot movements & routines (Node.js)
│   ├── prompt.js                         # LLM natural language prompt runner (Node.js)
│   ├── repl.js                           # Interactive REPL session (Node.js)
│   ├── voice.js                          # Voice interaction session (Node.js)
│   ├── k1_ble_daemon.py                  # Persistent background BLE daemon with dynamic 100% progress ACK (Python/Bleak)
│   ├── k1_ble_tester.py                  # Live interactive BLE test menu & telemetry monitor (Python/Bleak)
│   └── k1_action.py                      # Fast one-shot action execution CLI & status query (Python/Bleak)
├── src/
│   ├── K1/
│   │   ├── llm/
│   │   │   ├── command/
│   │   │   │   ├── systemPrompt.txt      # LLM prompt for mapping natural language to actions
│   │   │   │   └── userPrompt.txt        # User prompt wrapper with allowed actions catalog
│   │   │   └── joint/
│   │   │       ├── systemPrompt.txt      # LLM prompt for generating raw 17-servo keyframes
│   │   │       └── userPrompt.txt        # User prompt wrapper for joint kinematics
│   │   └── robot.json                    # Declarative K1 robot specification & kinematics limits
│   ├── K1.d.ts                           # TypeScript definitions for K1 class
│   ├── K1.js                             # K1 subclass inheriting from Robot base
│   ├── Robot.d.ts                        # TypeScript definitions for Robot base class
│   └── Robot.js                          # Core protocol, BLE transport, HID controller & LLM engine
├── test/
│   ├── __mocks__/@abandonware/noble.js   # Mock BLE hardware layer for offline unit testing
│   ├── K1.test.js                        # K1 integration unit tests
│   └── Robot.test.js                     # Robot protocol & packet encoder tests
├── node-red-contrib-robosen-block/       # Custom Node-RED palette simulating physical block daisy chain
│   ├── nodes/
│   │   ├── robosen-master.js / .html     # Master Block controller node (Persistent BLE daemon & string parser)
│   │   ├── robosen-instruction.js / .html# Modular instruction blocks (locomotion, combat, stunts)
│   │   ├── robosen-end.js / .html        # Passive loopback terminator block node
│   │   └── robosen-tester.js / .html     # Standalone action tester & direct controller node
│   ├── examples/
│   │   └── robosen_simulator_flow.json   # Ready-to-import Node-RED simulation flow
│   ├── package.json
│   └── README.md
├── index.d.ts                            # Root TypeScript exports
├── index.js                              # Package entry point (exports K1 and Robot)
├── package.json                          # NPM dependencies and script definitions
├── README.md                             # Original RobosenJS getting started guide
├── ROBOSEN_K1_DOCUMENTATION.md           # Complete official K1 documentation & user manual
├── PHYSICAL_BLOCK_SYSTEM_SPEC.md         # Hardware & electrical spec for modular tangible coding blocks
├── IMPROVEMENT_PLAN.md                   # 5-Pillar master improvement plan & roadmap
└── MEMORY.md                             # Master project memory & knowledge base (this file)
```

---

## 2. Live Hardware Diagnostics & Verified Device State

Live hardware tests conducted directly over Windows Native BLE (`winrt-windows-devices-bluetooth` via `Bleak`):

| Property | Value / Live State | Verification Method |
| :--- | :--- | :--- |
| **Device Model** | `Robosen K1 (Interstellar Scout)` | Discovered over BLE Advertisement |
| **Local Device Name** | `K1-00457` | BLE Local Name Broadcast |
| **Bluetooth MAC Address**| `3C:A5:51:94:97:70` | Windows BLE Adapter Discovery |
| **Signal Strength (RSSI)**| `-63 dBm` | Live RSSI Measurement |
| **Firmware Version** | `VER:3.03L` | Queried via Opcode `0xF7` |
| **Service UUID** | `0000ffe0-0000-1000-8000-00805f9b34fb` (`0xFFE0` / `ffe0`) | GATT Service Discovery |
| **Characteristic UUID** | `0000ffe1-0000-1000-8000-00805f9b34fb` (`0xFFE1` / `ffe1`) | GATT Characteristic Discovery |
| **Live Battery Progress** | `40%` $\rightarrow$ `61%` $\rightarrow$ `64%` $\rightarrow$ `70%` $\rightarrow$ `90%+` (Actively Charging) | Decoded from State Packet `0x0F` |
| **Speaker Volume** | `140 / 140` (Max) | Decoded from State Packet `0x0F` |
| **Auto-Stand (Fall Recovery)** | **Disabled (`0x00`)** | Toggled via `0x11` (0x00) & verified in `0x0F` |
| **Auto-Turn (IMU Heading)** | **Enabled (`0x01`)** | Default factory state verified in `0x0F` |
| **Auto-Off (Sleep Timer)** | **Enabled (`0x01`)** | Factory power-saving timer verified in `0x0F` |
| **Auto-Pose (Idle Moves)** | *N/A (Removed from K1 UI)* | Unsupported by K1 bipedal firmware; removed from telemetry reader |

---

## 3. Power, Charging & Hardware Ports

### 3.1 Dual Port Functions
1. **DC Barrel Jack Charging Port (Torso):**
   - **Dedicated to charging ONLY.**
   - Uses the official AC/DC power brick (**Output: DC 8.4V, 2.0A**).
   - Battery is a **2-cell (7.4V nominal) 2000 mAh Li-ion pack**.
   - Charging indicator: **Solid Red** = Charging, **Solid Green / Off** = Fully Charged ($100\%$).
   - Spoken audio confirmation upon connection: *"Start to supply energy."*
2. **USB Type-C Port (Torso):**
   - **Data Transfer ONLY.**
   - Cannot charge the robot from a standard 5V phone charger (voltage mismatch & no internal USB-C charging circuitry).
   - Used for PC data connection, onboard filesystem exploration, and choreography file transfers.

---

## 4. Automation & Safety Modes Explained

1. **🛡️ Auto-Stand Mode (Opcode `0x11`):**
   - **Function:** Fall recovery. The 6-axis internal gyroscope detects if the robot has fallen flat on its chest or back.
   - **Behavior:** Robot automatically initiates an acrobatic push-up routine to stand back up on its feet.
   - **Control:** Toggled via Opcode `0x11` with payload `0x01` (enable) or `0x00` (disable).

2. **🔄 Auto-Turn Mode (Opcode `0x1A`):**
   - **Function:** Real-time IMU yaw drift & obstacle balance correction during locomotion.
   - **Behavior:** Automatically adjusts individual foot step angles if uneven carpet/floor friction causes heading deviation.
   - **Control:** Toggled via Opcode `0x1A` with payload `0x01` (enable) or `0x00` (disable).

3. **🧘 Auto-Pose Mode (Opcode `0x1B`):**
   - **Function:** Autonomous idle animations and subtle "breathing" posture shifts when waiting for commands.
   - **K1 Firmware Note:** On K1 firmware `VER:3.03L`, autonomous idle posing is locked off (`0x00`) by default to prevent bipedal balance loss while standing unattended. Removed from K1 telemetry display.

4. **⏱️ Auto-Off Timer (Opcode `0x13`):**
   - **Function:** Power management. Shuts down servos and powers down after extended idle periods to preserve battery.
   - **Control:** Toggled via Opcode `0x13` with payload `0x01` (enable) or `0x00` (disable).

---

## 5. Bluetooth Low Energy (BLE) Protocol Specification

### 5.1 Packet Frame Structure
All binary frames transmitted to Characteristic `0xFFE1` follow this structure:

```
┌──────────────┬──────────────────┬───────────────┬──────────────────────┬──────────────┐
│ Header       │ Length (N+2)     │ Opcode (Type) │ Payload / Data (N B) │ Checksum (1) │
│ 2 Bytes: FFFF│ 1 Byte           │ 1 Byte (Hex)  │ Optional Bytes       │ 1 Byte       │
└──────────────┴──────────────────┴───────────────┴──────────────────────┴──────────────┘
```

- **Header:** `0xFF 0xFF` (2 bytes)
- **Length (`numBytes`):** 1 byte = `1 (Opcode) + DataLength + 1 (Checksum)`
- **Opcode (`Type`):** 1 byte representing the command or query
- **Checksum Calculation:**
  $$\text{Checksum} = (\text{numBytes} + \text{Opcode} + \sum \text{PayloadBytes}) \pmod{256}$$

### 5.2 Decoded Protocol Opcode Catalog

| Opcode | Command Name | Direction | Payload Type | Description |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveForward` | TX | None | Initiates forward walking |
| `0x02` | `turnRight` | TX | None | Initiates right turning step |
| `0x03` | `moveRight` | TX | None | Initiates right side-step |
| `0x04` | `moveSouthEast`| TX | None | Steps backward to the right |
| `0x05` | `moveBackward` | TX | None | Initiates backward walking |
| `0x06` | `moveSouthWest`| TX | None | Steps backward to the left |
| `0x07` | `moveLeft` | TX | None | Initiates left side-step |
| `0x08` | `turnLeft` | TX | None | Initiates left turning step |
| `0x0B` | `handshake` | TX/RX | None / 0x00 | Connection ping / alive handshake |
| `0x0C` | `stop` | TX/RX | None | Immediate halt for all motors |
| `0x0D` | `volume` | TX | Byte ($0-140$) | Sets speaker volume |
| `0x0F` | `state` | TX/RX | 8-byte struct | Telemetry query: pattern, battery, volume, progress, autoStand, autoTurn, autoPose, autoOff |
| `0x10` | `userNames` | TX/RX | String stream | List saved custom user choreography files |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Toggle fall recovery get-up routine |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Toggle sleep/auto power-down timer |
| `0x14` | `actionNames` | TX/RX | String stream | List built-in action catalog |
| `0x16` | `folderNames` | TX/RX | String stream | List audio & motion categories |
| `0x17` | `action` | TX/RX | String + Progress byte | Trigger predefined action (e.g. `"ProAction/Left Punch"`, `"Action/Boogaloo"`) |
| `0x18` | `audioNames` | TX/RX | String stream | List available audio track IDs |
| `0x19` | `audio` | TX | String | Play audio track (e.g. `"AppSysMS/101"`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Toggle IMU yaw balance correction |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Toggle autonomous idle poses |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter programming mode & read initial pose |
| `0xE7` | `programExit` | TX | None | Exit programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Set 17 servos to target angles + speed |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Read real-time live angles from all 17 servos |
| `0xEA` | `jointUnlockAll` | TX | None | Release motor torque on all joints for manual posing |
| `0xEB` | `jointLockAll` | TX | None | Engage motor holding torque |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Lock/unlock individual joints |
| `0xEE` | `play` | TX | Number | Trigger programmed sound index |
| `0xF6` | `kind` | TX/RX | String | Returns model name (e.g. `"K1"`) |
| `0xF7` | `version` | TX/RX | String | Returns firmware version (`"VER:3.03L"`) |
| `0xF8` | `date` | TX/RX | String | Returns firmware build date |
| `0xFA` | `shutdown` / `done` | TX/RX | None | Completion delimiter / power down |

---

## 6. Joint Kinematics & Servo Coordinate Mapping

The K1 possesses **17 digital servos** mapped across 5 body groups ($0-255$ integer scale):

| Servo ID | Joint Name | Byte Index | Default Center | Min Limit | Max Limit | Body Group |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **0** | `leftThigh` | 0 | `129` | 29 | 229 | Left Leg |
| **1** | `leftCalf` | 1 | `60` | 10 | 220 | Left Leg |
| **2** | `leftAnkle` | 2 | `106` | 26 | 226 | Left Leg |
| **3** | `rightThigh` | 3 | `118` | 18 | 218 | Right Leg |
| **4** | `rightCalf` | 4 | `190` | 30 | 240 | Right Leg |
| **5** | `rightAnkle` | 5 | `146` | 26 | 226 | Right Leg |
| **6** | `leftShoulder` | 6 | `212` | 22 | 242 | Left Arm |
| **7** | `rightShoulder` | 7 | `36` | 6 | 226 | Right Arm |
| **8** | `leftHip` | 8 | `123` | 103 | 133 | Left Leg |
| **9** | `leftFoot` | 9 | `123` | 93 | 133 | Left Leg |
| **10** | `rightHip` | 10 | `129` | 119 | 149 | Right Leg |
| **11** | `rightFoot` | 11 | `115` | 105 | 145 | Right Leg |
| **12** | `leftArm` | 12 | `223` | 33 | 233 | Left Arm |
| **13** | `leftHand` | 13 | `116` | 16 | 216 | Left Arm |
| **14** | `rightArm` | 14 | `34` | 34 | 224 | Right Arm |
| **15** | `rightHand` | 15 | `126` | 26 | 226 | Right Arm |
| **16** | `head` | 16 | `122` | 42 (Left) | 202 (Right) | Head Pan |
| **17–23** | *Internal / Padding* | 17–23 | `125` / `100` | 100 | 125 | Padding |
| **24** | `speed` | 24 | `30` | 1 (Fastest) | 100 (Slowest) | Transition Speed |

---

## 7. Python BLE CLI & Persistent Daemon Tooling

Because Node v24 on Windows requires MSVC C++ compilation for `@abandonware/noble`, a native Python BLE subsystem was built using `bleak` and Windows WinRT:

### 1. Persistent BLE Background Daemon ([`scripts/k1_ble_daemon.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_daemon.py))
- **Persistent Connection:** Auto-connects to the robot on launch and keeps a long-lived BLE link active to eliminate reconnect latencies.
- **Dynamic 100% Telemetry ACK Resolution:** Actions resolve the exact millisecond the physical robot emits `action_progress: 100%`, enabling instant back-to-back chaining without hardcoded sleep delays.
- **IPC Interface:** Accepts JSON commands via `stdin` (`{"cmd": "action", "action": "punch_left"}`) and streams events over `stdout` (`action_progress`, `action_completed`, `status_update`).

### 2. Quick Command-Line Execution ([`scripts/k1_action.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_action.py))
```powershell
# Query Live Telemetry & Battery Status
python scripts/k1_action.py status

# Test Head Servo Articulations Individually
python scripts/k1_action.py head_left    # Turns head to the Left (angle 42)
python scripts/k1_action.py head_right   # Turns head to the Right (angle 202)
python scripts/k1_action.py head_center  # Returns head to Center (angle 122)
python scripts/k1_action.py head_pan     # Full Sweep (Left -> Right -> Center)

# Martial Arts & Punches
python scripts/k1_action.py punch_left   # ProAction/Left Punch
python scripts/k1_action.py punch_right  # ProAction/Right Punch
python scripts/k1_action.py kung_fu      # ProAction/Kung Fu
python scripts/k1_action.py single_kick  # ProAction/Left Kick

# Dance, Acrobatics & Stunts
python scripts/k1_action.py push_ups     # ProAction/Push Ups (Fixed path)
python scripts/k1_action.py handstand    # ProAction/Handstand
python scripts/k1_action.py boogaloo     # Action/Boogaloo
python scripts/k1_action.py say_hello    # ProAction/Say Hello
python scripts/k1_action.py celebrate    # ProAction/Celebrate
python scripts/k1_action.py do_squats    # ProAction/Do Squats

# Locomotion Steps
python scripts/k1_action.py walk
python scripts/k1_action.py turn_left
python scripts/k1_action.py turn_right
```

### 3. Full Interactive Menu & Telemetry Stream ([`scripts/k1_ble_tester.py`](file:///C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_tester.py))
```powershell
python scripts/k1_ble_tester.py
```

---

## 8. Node-RED Custom Palette: `node-red-contrib-robosen-block`

A dedicated Node-RED palette simulating the physical block-based tangible programming system:

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    NODE-RED SIGNAL FLOW                                         │
│                                                                                                 │
│  [ Master Block ] ────► [ Instruction 1 ] ────► [ Instruction 2 ] ────► [ End Block Loopback ]  │
│  (TX: "start")          (+ ",move_forward")     (+ ",left_punch")       (Routes back to RX)     │
│        ▲                                                                        │               │
│        └──────────────────── Return RX ("start,move_forward,left_punch") ────────┘               │
│                    │                                                                            │
│                    ▼ (Persistent BLE 4.2 Stream)                                                │
│          [ Robosen K1 Robot ]                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Nodes in Palette:
1. **`robosen-master` (Master Block):**
   - Auto-connects to robot on flow deployment via persistent daemon.
   - Clickable button sends `"start"` down the chain.
   - Receives loopback string, parses tokens, and dispatches actions to robot with live telemetry.
   - Default `stepDelay = 0ms` for seamless action chaining.
2. **`robosen-instruction` (Instruction Block):**
   - Configurable action selector (Walk, Turn, Punch, Kung Fu, Dance, Push-ups, Handstand, Head Pan, Delay).
   - Appends its unique `,command` token.
3. **`robosen-end` (End Block):**
   - Passive loopback terminator connecting Pin 3 TX to Pin 4 RX.
4. **`robosen-tester` (Action Tester / Direct Controller):**
   - Standalone node for direct action testing without loopback wiring.
   - Includes **⚡ Execute Action Immediately** button, **Connect / Disconnect** buttons, and live battery & connection status card right inside the properties dialog.
   - Canvas button for one-click action triggering from the Node-RED editor.

### Machine Symlink Setup:
- Linked directly into machine's Node-RED via NTFS Directory Junction:
  `C:\Users\poomz\.node-red\node_modules\node-red-contrib-robosen-block` $\longleftrightarrow$ `C:\Users\poomz\nnnn\robosen_block\node-red-contrib-robosen-block`
- Ready-to-import simulation flow: [`node-red-contrib-robosen-block/examples/robosen_simulator_flow.json`](file:///C:/Users/poomz/nnnn/robosen_block/node-red-contrib-robosen-block/examples/robosen_simulator_flow.json).

---

## 9. Tangible Modular Coding Block System Hardware Specification

Designed for screenless STEM learning, physical modular coding blocks snap together in a daisy-chain bus to control the Robosen K1:

### Standardized 4-Pin Pogo Connector Pinout:
* **Pin 1 (`V+`):** Power rail supplied by Master Block ($3.3\text{V}–3.7\text{V}$).
* **Pin 2 (`GND`):** Common system ground.
* **Pin 3 (`UART TX`):** Downstream serial transmit line (Master $\to$ Block $1 \to$ Block $2 \dots$).
* **Pin 4 (`UART RX`):** Upstream return rail (hardwired loopback in End Block returning to Master RX).

---

## 10. 5-Pillar Master Improvement Plan & Roadmap

1. **Pillar 1: Hardware & Power BOM**
   - Replace instruction block MCUs with **\$0.15 WCH CH32V003 (RISC-V)** or **ATtiny85** to drop idle current from $50\text{mA}$ to $<10\,\mu\text{A}$.
   - Add magnetic polarity keying, TP4056 USB-C BMS charging, and RC debouncing filters on UART pins.
2. **Pillar 2: Protocol & Resilience**
   - Migrate from plaintext comma strings to structured binary frames with **CRC-8** verification.
3. **Pillar 3: Master ESP32 BLE Firmware**
   - Implement an asynchronous non-blocking command execution queue with $100\%$ action ACK confirmation (`0x17` progress byte `0x64`).
4. **Pillar 4: Visual & Auditory UX**
   - Integrate **WS2812B RGB LEDs** on each instruction block to illuminate in real-time as that specific step is executed by the robot. Add a piezo buzzer on the Master block for start/victory audio fanfares.
5. **Pillar 5: Next-Generation Blocks**
   - Develop Parameter Dial blocks (step/angle sliders), `Repeat [N]x` loop blocks, and Ultrasonic Distance obstacle-avoidance blocks.
