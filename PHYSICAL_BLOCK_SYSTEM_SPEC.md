# Tangible Modular Coding Block System for Robosen Robot Control

> **Document Version:** 1.0  
> **Target Hardware:** Physical Modular Programming Blocks (ESP32-based) $\longleftrightarrow$ Robosen K1 Humanoid Robot (Bluetooth BLE)

---

## 1. System Overview

This project is a **tangible / physical block-based programming system** designed to control the Robosen humanoid robot without a screen or computer. 

Users physically snap together modular code blocks in a linear sequence to create an algorithmic program. When the user presses the **Start Button** on the Master Block, an initial string is transmitted down the daisy chain. Each connected instruction block appends its own command, and the complete accumulated program loops back at the End Block to the Master Block. The Master Block then translates these commands into **Robosen Bluetooth Low Energy (BLE) protocol packets** and executes them on the physical robot.

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       PHYSICAL HARDWARE CHAIN                                          │
│                                                                                                        │
│  [ MASTER BLOCK ] ──Pin 3 (TX)──► [ INSTRUCTION BLOCK 1 ] ──Pin 3 (TX)──► [ END BLOCK (Loopback) ]     │
│  - Battery & Power                 - ESP32                         ▲          - Passive Loopback       │
│  - On/Off Switch                   - "move_forward"                │            (Pin 3 TX ─► Pin 4 RX) │
│  - Start Button                    - Pin In & Pin Out              │                                   │
│  - Master ESP32                                                    │                                   │
│         ▲                                                          │                                   │
│         └─────────────────────── Pin 4 (Return RX Rail) ───────────┴───────────────────────────────────┘
│                                            │
│                                 Accumulated String Return
│                                            │
│                                            ▼
│                              [ MASTER ESP32 PARSER ]
│                         - Splits: ["move_forward", ...]
│                         - Generates Robosen BLE Packets
│                                            │
│                                            ▼ (Bluetooth Low Energy)
│                                  [ ROBOSEN K1 ROBOT ]
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Block Hardware Specifications

### Block 1: Master Block (Start / Controller Block)
The Master Block is the "brain", power station, and BLE gateway of the physical system.

- **Onboard Components**:
  1. **Rechargeable Battery**: Supplies the `V+` power rail across all downstream connected blocks.
  2. **Main On/Off Power Switch**: Controls system-wide power delivery.
  3. **Physical Start Push Button**: User trigger to initiate program scanning and execution.
  4. **4-Pin Pogo Connector Port (Pin Out)**: Magnetic/spring-loaded pogo interface.
  5. **Master ESP32 Microcontroller**:
     - Controls UART serial transmission and reception.
     - Parses the returned command string.
     - Operates as a **Bluetooth BLE Central Client** to scan, connect, and stream binary command packets to the Robosen K1 robot.

---

### Block 2: Instruction Blocks (Command Modules)
Each instruction block physically represents one discrete command (e.g. *Move Forward*, *Move Backward*, *Turn Left*, *Turn Right*, *Left Punch*, *Kung Fu*, *Dance*, etc.).

- **Onboard Components**:
  1. **ESP32 Microcontroller**: Programmed with the block's unique command identifier.
  2. **Pin In (4-Pin Pogo Connector)**: Snaps into the previous block (receives `V+`, `GND`, and upstream `UART TX`).
  3. **Pin Out (4-Pin Pogo Connector)**: Snaps into the subsequent block (transmits `V+`, `GND`, and downstream `UART TX`).

---

### Block 3: End Block (Termination Module)
The End Block marks the physical end of the user's code sequence.

- **Onboard Components**:
  1. **No Microcontroller**: 100% passive hardware component.
  2. **4-Pin Connector Interface**: Contains an internal electrical bridge connecting **Pin 3 (`UART TX`) directly to Pin 4 (`UART RX`)**, creating the return loopback.

---

## 3. 4-Pin Pogo Connector Pinout & Electrical Layout

All blocks share a standardized 4-pin pogo pin connector layout:

| Pin # | Signal Name | Type | Description |
| :---: | :--- | :---: | :--- |
| **Pin 1** | **`V+`** | Power | Power rail provided by the Master Block battery |
| **Pin 2** | **`GND`** | Power | Common system ground |
| **Pin 3** | **`UART TX`** | Data Out | Downstream serial transmit line (Master $\to$ Block 1 $\to$ Block 2 $\to$ End Block) |
| **Pin 4** | **`UART RX`** | Data In | Upstream return serial rail (End Block loopback $\to$ Master Block RX) |

```
                ┌────────────────────────────────┐
                │ 4-PIN POGO PIN CONNECTOR       │
                │                                │
                │  (1) [ V+ ]      (Power)       │
                │  (2) [ GND ]     (Ground)      │
                │  (3) [ UART TX ] (Downstream)  │
                │  (4) [ UART RX ] (Return Rail) │
                └────────────────────────────────┘
```

---

## 4. End-to-End Workflow & Signal Flow

### Step 1: Physical Assembly
The user arranges the blocks into a logical sequence:
$$\text{[Master Block]} \longrightarrow \text{[Block 1: Forward]} \longrightarrow \text{[Block 2: Turn Left]} \longrightarrow \text{[Block 3: Punch]} \longrightarrow \text{[End Block]}$$

### Step 2: Triggering Execution
The user presses the **Start Button** on the Master Block.

### Step 3: Initiation & Initial Payload
The Master ESP32 transmits the seed string `"start"` out of its `UART TX` port on **Pin 3**.

### Step 4: Daisy-Chain String Mutation
1. **Block 1 (Move Forward)** receives `"start"` on its `Pin In` (Pin 3).
   - Its ESP32 reads `"start"`.
   - It appends its own command identifier: `",move_forward"`.
   - Resulting string: `"start,move_forward"`.
   - Transmits `"start,move_forward"` out of its `Pin Out` (Pin 3).
2. **Block 2 (Turn Left)** receives `"start,move_forward"` on its `Pin In`.
   - Its ESP32 appends `",turn_left"`.
   - Resulting string: `"start,move_forward,turn_left"`.
   - Transmits `"start,move_forward,turn_left"` out of its `Pin Out` (Pin 3).
3. **Block 3 (Left Punch)** receives `"start,move_forward,turn_left"`.
   - Its ESP32 appends `",left_punch"`.
   - Resulting string: `"start,move_forward,turn_left,left_punch"`.
   - Transmits `"start,move_forward,turn_left,left_punch"` out of its `Pin Out` (Pin 3).

### Step 5: Loopback at the End Block
The final string reaches the **End Block**. Because Pin 3 (`TX`) is hardwired internally to Pin 4 (`RX`), the signal is redirected straight into the **Pin 4 Return Rail**.

### Step 6: Direct Return to Master Block
The complete string:
```text
"start,move_forward,turn_left,left_punch"
```
travels along the continuous Pin 4 pass-through rail directly into the Master ESP32's `UART RX` pin.

---

## 5. Translation to Robosen K1 Bluetooth BLE Protocol

Once the Master ESP32 receives the full program string, it parses each token and translates it into binary BLE command frames for the Robosen K1 robot.

### 1. BLE Connection Specs
- **Service UUID**: `0xFFE0`
- **Characteristic UUID**: `0xFFE1`
- **Device Header**: `0xFFFF`

### 2. Binary Packet Structure
$$\text{Packet} = \text{[0xFFFF (Header)]} + \text{[numBytes (Length)]} + \text{[Opcode (Type)]} + \text{[Payload]} + \text{[Checksum]}$$
$$\text{Checksum} = (\text{numBytes} + \text{Opcode} + \text{DataBytes}) \pmod{256}$$

### 3. Command Token Mapping Table

| Physical Block String | Action Category | Robosen Opcode | Payload / Parameters | Binary Frame Example (Hex) |
| :--- | :--- | :---: | :--- | :--- |
| `move_forward` | Locomotion | `0x01` | Walk duration (e.g. 2000 ms) | `ffff020103` + Stop |
| `move_backward` | Locomotion | `0x05` | Walk duration (e.g. 2000 ms) | `ffff020507` + Stop |
| `turn_left` | Locomotion | `0x08` | Turn duration (e.g. 1500 ms) | `ffff02080a` + Stop |
| `turn_right` | Locomotion | `0x02` | Turn duration (e.g. 1500 ms) | `ffff020204` + Stop |
| `move_left` | Locomotion | `0x07` | Side-step duration | `ffff020709` + Stop |
| `move_right` | Locomotion | `0x03` | Side-step duration | `ffff020305` + Stop |
| `left_punch` | Action | `0x17` | String: `"ProAction/Left Punch"` | `ffff161750726f416374696f6e2f4c6566742050756e636894` |
| `right_punch` | Action | `0x17` | String: `"ProAction/Right Punch"` | `ffff171750726f416374696f6e2f52696768742050756e6368a7` |
| `kung_fu` | Action | `0x17` | String: `"ProAction/Kung Fu"` | `ffff131750726f416374696f6e2f4b756e6720467554` |
| `boogaloo` | Action (Dance) | `0x17` | String: `"Action/Boogaloo"` | `ffff1117416374696f6e2f426f6f67616c6f6ff3` |
| `head_left` | Joint Kinematics | `0xE8` | 25-byte struct (Head: `42`, Speed: `30`) | Direct 17-servo frame |
| `head_right` | Joint Kinematics | `0xE8` | 25-byte struct (Head: `202`, Speed: `30`) | Direct 17-servo frame |
| `initial_pose` | System Pose | `0xE8` | 25-byte struct (Neutral coordinates) | Direct 17-servo frame |

---

## 6. Execution Queue & State Handling in Master ESP32

To ensure smooth and error-free robot execution, the Master ESP32 executes commands **sequentially** using the following state machine:

```
[ Master Receives Return String ]
               │
               ▼
[ Parse Comma-Separated Array ]
               │
               ▼
┌──────────────┴───────────────────────────────────────────────────────┐
│ FOR EACH COMMAND IN QUEUE:                                           │
│                                                                      │
│  1. Send Robosen BLE Command Packet                                  │
│  2. If Action (`0x17`):                                              │
│     - Listen for BLE notification on Characteristic `0xFFE1`         │
│     - Wait until Progress Byte === 100% (`0x64`)                     │
│  3. If Locomotion (`0x01`-`0x08`):                                   │
│     - Run hardware timer for step duration                           │
│     - Send Stop Packet (`0x0C`) or Handshake (`0x0B`)                │
│  4. Apply Cooldown Buffer (e.g. 500ms for balance stabilization)     │
└──────────────┬───────────────────────────────────────────────────────┘
               │
               ▼
   [ All Blocks Completed ]
```

---

## 7. Key Architecture Strengths & Improvement Opportunities

### Strengths:
1. **Intuitive Screenless Coding**: Tactile, hands-on learning suitable for STEM education.
2. **Infinite Chain Scalability**: Adding more blocks simply extends the daisy-chain length.
3. **Passive Loopback Reliability**: Using an unpowered End Block to bridge TX to RX avoids the need for a separate controller on the terminator.

### Identified Improvement Opportunities:
1. **Cost & Power Optimization**: Replace the ESP32 in instruction blocks with ultra-low-cost, low-power 8-bit / 32-bit MCUs (e.g. CH32V003 at ~$0.15), keeping the ESP32 only on the Master Block.
2. **Pogo Debouncing & Magnetic Keying**: Add magnetic polarity alignment to prevent reverse-connection short circuits and add RC filters to prevent UART contact bounce.
3. **Live Step Visual Feedback**: Add an RGB LED to each block that pulses green as the robot executes that specific step in real time.
4. **Parameterized / Dial Blocks**: Support blocks with dials or selectors (e.g. *"Walk Forward: 1 vs 3 vs 5 steps"* or *"Repeat 3x"*).
