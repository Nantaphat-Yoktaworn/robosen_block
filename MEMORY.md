# RobosenJS Memory & Knowledge Base

> **RobosenJS** is a Node.js library, CLI tool, and programmatic framework for controlling **Robosen** humanoid robotics (specifically the **Robosen K1 / Interstellar Scout K1 Series**) over Bluetooth Low Energy (BLE).

---

## 1. Project Metadata & Overview

- **Repository**: [oklemenz/RobosenJS](https://github.com/oklemenz/RobosenJS)
- **Author**: Oliver Klemenz
- **License**: Apache-2.0
- **Runtime**: Node.js `>= 22` (ESM / CommonJS / TypeScript)
- **Target Hardware**: Robosen K1 Interstellar Scout humanoid bipedal robot
- **Primary Dependencies**:
  - `@abandonware/noble`: Bluetooth Low Energy (BLE) central communication
  - `node-hid`: USB/Bluetooth Gamepad / HID controller interface
  - `node-record-lpcm16`: Microphone audio recording & voice detection
  - `openai`: LLM natural language intent compilation & Whisper transcription

---

## 2. Core Architecture & File Organization

```
robosen_project/
├── bin/
│   └── k1.js                             # Global & local CLI executable
├── recordings/
│   └── K1/
│       └── test.json                     # Recorded joint keyframe motion sequences
├── scripts/
│   ├── control.js                        # Gamepad/Keyboard controller runner
│   ├── demo.js                           # Quick demo choreography script
│   ├── main.js                           # Standard startup & health check script
│   ├── program.js                        # Scripted robot movements & routines
│   ├── prompt.js                         # LLM natural language prompt runner
│   ├── repl.js                           # Interactive REPL session
│   └── voice.js                          # Voice interaction session
├── src/
│   ├── K1/
│   │   ├── llm/
│   │   │   ├── command/
│   │   │   │   ├── systemPrompt.txt      # Prompt for mapping intent to predefined actions
│   │   │   │   └── userPrompt.txt        # User prompt wrapper with allowed commands list
│   │   │   └── joint/
│   │   │       ├── systemPrompt.txt      # Prompt for generating raw joint keyframe sequences
│   │   │       └── userPrompt.txt        # User prompt wrapper for joint motion
│   │   └── robot.json                    # Full declarative K1 robot specification
│   ├── K1.d.ts                           # TypeScript definitions for K1 class
│   ├── K1.js                             # K1 subclass inheriting from Robot
│   ├── Robot.d.ts                        # TypeScript definitions for Robot base class
│   └── Robot.js                          # Core protocol, BLE transport, HID & LLM engine
├── test/
│   ├── __mocks__/@abandonware/noble.js   # Mock BLE hardware layer for offline testing
│   ├── K1.test.js                        # K1 integration unit tests
│   └── Robot.test.js                     # Robot protocol & packet encoder tests
├── index.d.ts                            # Root TypeScript exports
├── index.js                              # Package entry point (exports K1 and Robot)
├── package.json                          # NPM dependencies and script definitions
├── README.md                             # User-facing guide
└── MEMORY.md                             # Complete project memory & reference (this file)
```

---

## 3. Bluetooth BLE Protocol Specification

### Hardware BLE Identifiers
- **Service UUID**: `0xFFE0` (`ffe0`)
- **Characteristic UUID**: `0xFFE1` (`ffe1`)
- **Manufacturer ID**: `0x15B1` (`15b1`)

### Packet Frame Structure
All communication uses binary packet frames:

```
┌──────────────┬──────────────────┬───────────────┬──────────────────────┬──────────────┐
│ Header       │ Length (N+2)     │ Opcode (Type) │ Payload / Data (N B) │ Checksum (1) │
│ 2 Bytes: FFFF│ 1 Byte           │ 1 Byte (Hex)  │ Optional Bytes       │ 1 Byte       │
└──────────────┴──────────────────┴───────────────┴──────────────────────┴──────────────┘
```

- **Header**: `0xFF 0xFF` (2 bytes)
- **Length (`numBytes`)**: 1 byte = `1 (Opcode) + DataLength + 1 (Checksum)`
- **Opcode (`Type`)**: 1 byte representing the command or query
- **Payload**: Optional data (ASCII string, integer, boolean byte, or binary struct)
- **Checksum**: 1 byte calculated as:
  $$\text{Checksum} = \left(\sum \text{BodyBytes}\right) \pmod{256} = (\text{numBytes} + \text{Opcode} + \text{DataBytes}) \pmod{256}$$

### Protocol Opcode Reference Table

| Opcode | Identifier | Direction | Payload Type | Description |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveNorth` / `moveForward` | TX | None | Walk forward |
| `0x02` | `moveNorthEast` / `turnRight` | TX | None | Turn/step right forward |
| `0x03` | `moveEast` / `moveRight` | TX | None | Side step right |
| `0x04` | `moveSouthEast` | TX | None | Turn/step right backward |
| `0x05` | `moveSouth` / `moveBackward` | TX | None | Walk backward |
| `0x06` | `moveSouthWest` | TX | None | Turn/step left backward |
| `0x07` | `moveWest` / `moveLeft` | TX | None | Side step left |
| `0x08` | `moveNorthWest` / `turnLeft` | TX | None | Turn/step left forward |
| `0x0B` | `handshake` | TX/RX | None | Connection handshake |
| `0x0C` | `stop` | TX/RX | None | Emergency / immediate motion stop |
| `0x0D` | `volume` | TX | Byte ($0 - 140$) | Set speaker volume |
| `0x0F` | `state` | TX/RX | 8-byte struct | Query status: `pattern`, `battery`, `volume`, `progress`, `autoStand`, `autoTurn`, `autoPose`, `autoOff` |
| `0x10` | `userNames` | TX/RX | Strings | Stream of saved custom user action names |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Toggle auto-stand on fall detection |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Toggle automatic shutdown timer |
| `0x14` | `actionNames` | TX/RX | Strings | Stream of built-in action names |
| `0x16` | `folderNames` | TX/RX | Strings | Stream of stored audio/choreography folder names |
| `0x17` | `action` | TX/RX | String + Progress byte | Trigger predefined action (progress notifications $0 \to 100\%$) |
| `0x18` | `audioNames` | TX/RX | Strings | Stream of available audio file names |
| `0x19` | `audio` | TX | String | Play audio track (e.g. `"AppSysMS/101"`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Toggle auto-turn safety behavior |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Toggle auto-pose mode |
| `0x33`-`0x3A` | Alternative movement | TX | `0x01` | Continuous directional steps |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter programming mode & fetch initial joint state |
| `0xE7` | `programExit` | TX | None | Exit programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Direct joint positioning frame (17 servos + parameters + speed) |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Synchronize & read back live joint positions |
| `0xEA` | `jointUnlockAll` | TX | None | Release torque on all 17 joints for manual posing |
| `0xEB` | `jointLockAll` | TX | None | Engage torque on all 17 joints |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Lock/unlock individual joints |
| `0xEE` | `play` | TX | Number | Play programmed sound/message ID |
| `0xF6` | `kind` | TX/RX | String | Query robot model name (e.g. `"K1"`) |
| `0xF7` | `version` | TX/RX | String | Query firmware version |
| `0xF8` | `date` | TX/RX | String | Query firmware build date |
| `0xFA` | `shutdown` / `done` | TX/RX | None | Power down robot / completion delimiter |

---

## 4. Servo Joints & Kinematics Specification

The K1 robot has **17 digital servos** mapped across 5 body segments. In `0xE8` / `0xE9` structs, each joint position is an 8-bit unsigned integer ($0 - 255$):

| Joint Name | Byte Index | Default | Min | Max | Body Group | Norm Center |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **`leftThigh`** | 0 | `129` | 29 | 229 | `leftLeg` | 129 |
| **`leftCalf`** | 1 | `60` | 10 | 220 | `leftLeg` | 60 |
| **`leftAnkle`** | 2 | `106` | 26 | 226 | `leftLeg` | 106 |
| **`rightThigh`** | 3 | `118` | 18 | 218 | `rightLeg` | 118 |
| **`rightCalf`** | 4 | `190` | 30 | 240 | `rightLeg` | 190 |
| **`rightAnkle`** | 5 | `146` | 26 | 226 | `rightLeg` | 146 |
| **`leftShoulder`** | 6 | `212` | 22 | 242 | `leftArm` | 212 |
| **`rightShoulder`** | 7 | `36` | 6 | 226 | `rightArm` | 36 |
| **`leftHip`** | 8 | `123` | 103 | 133 | `leftLeg` | 123 |
| **`leftFoot`** | 9 | `123` | 93 | 133 | `leftLeg` | 123 |
| **`rightHip`** | 10 | `129` | 119 | 149 | `rightLeg` | 129 |
| **`rightFoot`** | 11 | `115` | 105 | 145 | `rightLeg` | 115 |
| **`leftArm`** | 12 | `223` | 33 | 233 | `leftArm` | 223 |
| **`leftHand`** | 13 | `116` | 16 | 216 | `leftArm` | 116 |
| **`rightArm`** | 14 | `34` | 34 | 224 | `rightArm` | 34 |
| **`rightHand`** | 15 | `126` | 26 | 226 | `rightArm` | 126 |
| **`head`** | 16 | `122` | 42 | 202 | `head` | 122 |
| *`value17 - value23`* | 17-23 | `125 / 100` | 100 | 125 | Padding/internal | 125 |
| **`speed`** | 24 | `30` | 1 | 100 | Speed ($1=\text{fastest}, 100=\text{slowest}$) | N/A |

### Value Representation Rules
- **Absolute Number**: `122` (sets exact servo coordinate)
- **Relative Delta**: `"+20"` / `"-15"` (offsets current joint coordinate)
- **Relative Percentage**: `"+40%"` / `"-30%"` (percentage of total span $(max - min)$)
- **Absolute Percentage**: `"50%"` (maps $0\% \to min$ and $100\% \to max$)

---

## 5. Interaction Modes & CLI Quick Reference

### 1. REPL Mode (`npm run repl` or `k1 repl`)
- Direct command entry with Tab completion.
- Examples: `Volume 100`, `Left Punch`, `Head Left`, `Boogaloo`, `Take A Seat`.

### 2. Gamepad & Keyboard Mode (`npm run control` or `k1 control`)
- **Gamepad (Nintendo Switch Pro / Generic HID)**:
  - Left Stick: Directional walking / strafing
  - D-Pad: Select body part (`Up`=Head, `Left`=Left Arm, `Right`=Right Arm, `Down`=Neutral/Robot)
  - Right Stick: Real-time joint articulation of selected body part
  - Buttons: Triggers punches, kicks, flips, handstands, push-ups
- **Keyboard**:
  - `Arrow Keys`: Move / Turn
  - `Delete` / `PageDown`: Side step left / right
  - `W` / `A` / `D` / `S`: Select Head / Left Arm / Right Arm / Neutral
  - `Space`: Neutral stop position

### 3. AI / LLM Natural Language Prompt Mode (`npm run prompt` or `k1 prompt`)
- Configured via `.env` with `OPENAI_API_KEY`.
- `k1 prompt`: Compiles natural language (any language) to discrete actions (e.g., `"Walk forward and punch left"`).
- `k1 prompt joint`: Compiles natural language to sequential joint frames (e.g., `"Wave your right hand and shake your head"`).

### 4. Voice Mode (`npm run voice` or `k1 voice`)
- Listens to microphone, performs RMS silence detection, sends audio to OpenAI Whisper (`gpt-4o-mini-transcribe`), and executes recognized commands through the LLM compiler.

### 5. Kinesthetic Motion Recording & Playback
1. Start recording: `record <filename>` (e.g., `record my_dance`)
2. Unlock target joint: `unlock head`
3. Manually position limb, then sync frame: `sync`
4. Add pause if desired: `pause 1000`
5. Repeat manual posing and `sync`
6. Save: `save change` (saves to `recordings/K1/<filename>.json`)
7. Replay: `run <filename>`

---

## 6. Programmatic Node.js SDK Usage

### Full Working Example
```javascript
const { K1 } = require("robosen-js");

async function main() {
  const k1 = new K1();
  
  // 1. Connect over BLE
  await k1.on();
  
  // 2. Query Robot Info & State
  const version = await k1.version();
  console.log("Firmware Version:", version);
  const state = await k1.state();
  console.log("Battery Level:", state.battery);
  
  // 3. Configure Safety & Audio
  await k1.volume(100);
  await k1.autoStand(true);
  
  // 4. Locomotion & High-Level Actions
  await k1.moveForward(2000);
  await k1.turnRight();
  await k1.leftPunch();
  await k1.boogaloo();
  
  // 5. Direct Joint Kinematics
  await k1.headLeft();
  await k1.leftHand("+40%", 30);
  await k1.moveJoints({
    head: 150,
    leftShoulder: 200,
    rightShoulder: 50,
    speed: 25
  });
  
  // 6. Playback Custom Choreography
  await k1.run("test");
  
  // 7. Disconnect cleanly
  await k1.end();
}

main().catch(console.error);
```

---

## 7. How to Extend: Adding New Robosen Robot Models

To add support for other Robosen models (e.g., *Flagship Optimus Prime*, *Bumblebee*, *Buzz Lightyear*, *Megatron*):

1. Create a new profile folder: `src/<ModelName>/`
2. Create `src/<ModelName>/robot.json` defining:
   - Manufacturer, Service, and Characteristic UUIDs
   - Joint mappings (names, limits, byte indexes)
   - Command opcodes and action library
3. Create `src/<ModelName>.js` subclassing `Robot`:
   ```javascript
   const Robot = require("./Robot");
   module.exports = class OptimusPrime extends Robot {
     constructor(options) {
       super("OptimusPrime", options);
     }
   };
   ```
4. Export the new class in `index.js` and provide types in `index.d.ts`.
