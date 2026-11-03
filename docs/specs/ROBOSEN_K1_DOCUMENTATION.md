# Robosen K1 (Interstellar Scout) Official Documentation & Technical Reference Manual

> **Product Name:** Robosen Interstellar Scout K1 / K1 Pro  
> **Manufacturer:** Robosen Robotics (Shenzhen) Co., Ltd.  
> **FCC ID:** 2ATNWK1  
> **Model Series:** K1 Series (Humanoid Bipedal Programmable Robot)  

---

## 1. Product Overview & Packaging Contents

### 1.1 Product Description
The **Robosen Interstellar Scout K1** is an educational, bipedal humanoid robot designed for programmable interaction, STEM robotics education, and entertainment. Built with a lightweight aluminum alloy internal structure and aerospace-grade outer casing, it is driven by 17 high-performance, high-precision servo motors and 40 internal microchips. The robot supports multiple control modalities, including hands-free voice control, mobile app direct control, manual kinesthetic programming, block-based graphical programming, and low-level Bluetooth Low Energy (BLE) protocol integration.

### 1.2 Package Contents (Packing List)
* **1 × Robosen K1 Robot** (Interstellar Scout)
* **1 × AC/DC Power Adapter / Charger**
* **1 × USB Data Cable (Type-C)**
* **1 × User Manual / Quick Start Guide**
* **1 × Voice Command Reference Card**

---

## 2. Technical Specifications

| Parameter | Official Specification |
| :--- | :--- |
| **Product Dimensions** | 176 mm × 99 mm × 349 mm (6.9 × 3.9 × 13.7 inches) |
| **Product Weight** | 0.94 kg (33.16 oz / 2.07 lbs) |
| **Structural Material** | Aluminum alloy structural frame, ABS + PC aerospace-grade housing |
| **Servo Motors** | 17 high-precision digital servo motors (Head: 1, Arms/Hands: 3 × 2, Legs/Feet: 5 × 2) |
| **Microcontrollers / ICs** | 40 microchips managing joint kinematics and communication |
| **Battery Type** | Rechargeable Lithium-ion battery pack |
| **Battery Capacity** | 2000 mAh, 7.4V (nominal) |
| **Battery Operating Time** | Approximately 50 – 60 minutes (under standard operational load) |
| **Power Adapter Input** | AC 100V – 240V ~ 50/60Hz, 0.6A Max |
| **Power Adapter Output** | DC 8.4V, 2.0A |
| **Wireless Communication** | Bluetooth Low Energy (BLE 4.2) |
| **Bluetooth Service UUID** | `0xFFE0` (`ffe0`) |
| **Bluetooth Characteristic UUID** | `0xFFE1` (`ffe1`) |
| **Bluetooth Manufacturer ID** | `0x15B1` (`15b1`) |
| **Control Interfaces** | Voice Control (Offline Built-in), Mobile App (iOS / Android), BLE SDK |
| **Physical Interfaces** | DC Barrel Jack Charging Port, USB Type-C Data Port |
| **Speaker / Audio** | Integrated high-fidelity speaker with built-in voice prompts & sound effects |

---

## 3. Product Component & Interface Guide

```
                        [ HEAD ]
                  (1 Servo: Pan/Yaw)
                         │
      ┌──────────────────┴──────────────────┐
      │                                     │
 [ LEFT ARM ]                          [ RIGHT ARM ]
 • Left Shoulder (Servo)               • Right Shoulder (Servo)
 • Left Arm / Bicep (Servo)            • Right Arm / Bicep (Servo)
 • Left Hand / Wrist (Servo)           • Right Hand / Wrist (Servo)
      │                                     │
      └──────────────────┬──────────────────┘
                         │
                   [ MAIN TORSO ]
           • Power Button (Long Press)
           • DC Charging Port (8.4V In)
           • Type-C Data Port
           • Status LED / Speaker Grille
                         │
      ┌──────────────────┴──────────────────┐
      │                                     │
 [ LEFT LEG ]                          [ RIGHT LEG ]
 • Left Thigh (Servo)                  • Right Thigh (Servo)
 • Left Calf / Knee (Servo)            • Right Calf / Knee (Servo)
 • Left Ankle (Servo)                  • Right Ankle (Servo)
 • Left Hip (Servo)                    • Right Hip (Servo)
 • Left Foot (Servo)                   • Right Foot (Servo)
```

---

## 4. Power Management & Battery Charging

### 4.1 Powering On
1. Place the robot upright on a smooth, flat, level, and unobstructed surface.
2. Press and hold the **Power Button** located on the torso for 3 seconds.
3. The robot will power on, engage its servo motors into the neutral standing position, and speak the initialization audio prompt:
   > *"Hello, Humanity."*

### 4.2 Powering Off
* **Via Physical Button:** Press and hold the **Power Button** on the robot's body for 3 seconds until the robot plays the shutdown prompt:
  > *"See you next time, Humanity."*
* **Via Mobile App:** In the connection menu of the mobile application, select the **"Shutdown K1"** / **"Power Off"** option.

### 4.3 Charging Procedure
1. Connect the provided DC power adapter to the DC charging interface on the robot.
2. Plug the adapter into a standard AC power wall outlet (100–240V).
3. The robot will emit a voice confirmation:
   > *"Start to supply energy."*
4. **Charger LED Status Indicator:**
   - **Solid Red Light:** Battery is actively charging.
   - **Solid Green Light / Off:** Battery is fully charged.
5. Once fully charged, disconnect the power adapter before operating the robot.

> [!CAUTION]
> - Use only the manufacturer-provided power adapter (DC 8.4V 2A). Using third-party chargers may result in battery degradation, overheating, or circuit damage.
> - Do not operate or trigger high-current motion sequences while the charging cable is connected.

---

## 5. Mobile App Setup & Wireless Connection

### 5.1 App Download & Installation
1. On your smartphone or tablet (iOS or Android), search for **"K One"** or **"Robosen"** in the Apple App Store or Google Play Store.
2. Download and install the application. Ensure permissions for **Bluetooth** and **Location Services** (required on Android for BLE discovery) are granted.

### 5.2 Bluetooth Pairing Steps
1. Power on the Robosen K1 robot.
2. Enable Bluetooth on your mobile device.
3. Open the **K One** application.
4. Tap the **Bluetooth Connection Icon** located in the top-right corner of the home screen.
5. The app will scan for nearby devices. Select your robot from the device list (displayed in the format `K1-XXXX` or serial number `xxx-0000`).
6. Once connected, the app will confirm connection status, and the robot's telemetry (battery level, volume, system status) will appear.

> [!IMPORTANT]
> Voice control and mobile app control are mutually exclusive:
> - When the robot is connected to the app via Bluetooth, **hardware voice control is disabled**.
> - To use voice commands, disconnect the robot from the app or close the application.

---

## 6. Voice Control Reference & Command Catalog

### 6.1 Wake-Up Protocol
1. Ensure the robot is disconnected from the mobile app.
2. Speak clearly towards the robot:
   > **User:** *"Hey, K One"* (or *"Hey K1"*)
3. The robot will acknowledge and enter voice listening mode:
   > **Robot Response:** *"I'm here."*
4. Speak one of the valid command phrases listed below within 5 seconds.

### 6.2 Pre-Installed Voice Command Table

| Category | Voice Command Phrase | Robot Behavior / Action Description |
| :--- | :--- | :--- |
| **System & Greetings** | *"Hey, K One"* | Wake-up trigger; robot responds *"I'm here."* |
| | *"Report Status"* / *"Check Battery"* | Audibly reports battery and operational state |
| | *"Volume Up"* / *"Volume Down"* | Adjusts onboard speaker volume |
| | *"Rest"* / *"Stand Down"* | Returns to neutral low-power standing position |
| **Locomotion** | *"Move forward"* / *"Walk forward"* | Steps forward continuously until stop command |
| | *"Come back"* / *"Move backward"* | Steps backward |
| | *"Turn left"* | Turns body heading to the left |
| | *"Turn right"* | Turns body heading to the right |
| | *"Step left"* / *"Strafe left"* | Side-steps to the left |
| | *"Step right"* / *"Strafe right"* | Side-steps to the right |
| | *"Stop"* / *"Halt"* | Immediately halts current walking motion |
| **Combat & Martial Arts** | *"Left Punch"* | Executes quick left straight punch |
| | *"Right Punch"* | Executes quick right straight punch |
| | *"Double Punch"* | Executes alternating rapid two-handed punches |
| | *"Kung Fu"* | Performs dynamic martial arts routine |
| | *"Ready to Fight"* / *"Combat Pose"* | Assumes defensive fighting stance |
| **Acrobatics & Fitness** | *"Push-ups"* | Drops to floor, performs push-ups, and stands back up |
| | *"Handstand"* | Balances on hands in handstand position |
| | *"Do a flip"* / *"Backflip"* | Executes acrobatic backward flip / roll routine |
| | *"Single Leg Stand"* | Balances entirely on one foot |
| | *"Take a Seat"* / *"Sit down"* | Sits down on floor |
| | *"Stand Up"* | Recovers from sitting/fallen position to standing |
| **Entertainment & Stunts** | *"Showtime"* | Performs full showcase choreography with audio |
| | *"Dance"* / *"Boogaloo"* | Performs rhythmic dance movements with music |
| | *"Wave hands"* / *"Wave hello"* | Waves right hand in friendly greeting |
| | *"Shake Head"* | Shakes head left and right |
| | *"Salute"* | Brings hand to head in formal military salute |

### 6.3 Voice Programming Mode (Hands-Free Macro Chaining)
The K1 supports spoken macro programming without a phone or PC:
1. Say: **"Hey, K One"** $\longrightarrow$ Robot responds: **"I'm here."**
2. Say: **"Start Programming"** $\longrightarrow$ Robot confirms entry into programming mode with a tone.
3. Speak commands one by one (e.g., *"Move forward"*, *"Left Punch"*, *"Turn Right"*). The robot emits an acknowledgment beep after each valid instruction.
4. Say: **"Execute"** $\longrightarrow$ The robot executes the entire chained sequence sequentially.
5. To abort without running, say: **"Cancel."**

---

## 7. Mobile App Programming Modes

### 7.1 Manual (Kinesthetic) Programming
Manual programming allows users to physically pose the robot's limbs with their hands and capture keyframes:
1. Open the **K One App** $\longrightarrow$ Navigate to **Create** $\longrightarrow$ **Manual Programming**.
2. Tap **"Unlock / Free Joints"** (servos release holding torque, indicated by blue highlight in app).
3. Physically move the robot's arms, head, or torso into the desired keyframe posture.
4. Tap **"Sync / Add Frame"** to record the 17 servo angles into the timeline.
5. Set transition duration / speed between keyframes (1–100 speed scale).
6. Repeat for subsequent frames, then tap **"Save"** and **"Play"** to execute the routine.

### 7.2 Block-Based (Graphical) Programming
A Scratch-style visual coding interface designed for STEM education:
* **Motion Blocks:** Move forward, backward, turn left/right, side-step, speed settings.
* **Action Blocks:** Built-in stunts, martial arts, punches, kicks, dances.
* **Joint Control Blocks:** Set specific servo angles ($0–255$) on individual joints (head, arms, legs).
* **Audio & Light Blocks:** Play specific audio tracks and control LED color patterns.
* **Control Flow Blocks:** `Wait (ms)`, `Repeat [N] times`, `Loop Forever`, `If / Else` conditions.

### 7.3 Real-Time Remote Control Mode
* Virtual dual joysticks for omnidirectional walking and strafing.
* Quick-action shortcut buttons for punches, kicks, defense, and showtime routines.
* Limb articulation sliders for manual head and arm aiming.

---

## 8. Joint Kinematics & Servo Specification Table

The Robosen K1 features **17 digital servos** mapped across 5 body groups. In raw protocol packets (`0xE8`/`0xE9`), each servo coordinate is an 8-bit unsigned integer ($0–255$):

| Servo ID | Joint Name | Byte Index | Default (Neutral) | Min Limit | Max Limit | Body Group |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **0** | `leftThigh` | 0 | `126` | 29 | 229 | Left Leg |
| **1** | `leftCalf` | 1 | `65` | 10 | 220 | Left Leg |
| **2** | `leftAnkle` | 2 | `100` | 26 | 226 | Left Leg |
| **3** | `rightThigh` | 3 | `127` | 18 | 218 | Right Leg |
| **4** | `rightCalf` | 4 | `184` | 30 | 240 | Right Leg |
| **5** | `rightAnkle` | 5 | `141` | 26 | 226 | Right Leg |
| **6** | `leftShoulder` | 6 | `222` | 22 | 242 | Left Arm |
| **7** | `rightShoulder` | 7 | `26` | 6 | 226 | Right Arm |
| **8** | `leftHip` | 8 | `125` | 103 | 133 | Left Leg |
| **9** | `leftFoot` | 9 | `116` | 93 | 133 | Left Leg |
| **10** | `rightHip` | 10 | `135` | 119 | 149 | Right Leg |
| **11** | `rightFoot` | 11 | `120` | 105 | 145 | Right Leg |
| **12** | `leftArm` | 12 | `214` | 33 | 233 | Left Arm |
| **13** | `leftHand` | 13 | `146` | 16 | 216 | Left Arm |
| **14** | `rightArm` | 14 | `42` | 34 | 224 | Right Arm |
| **15** | `rightHand` | 15 | `99` | 26 | 226 | Right Arm |
| **16** | `head` | 16 | `123` | 42 | 202 | Head |
| **17–23** | `padding / reserved`| 17–23 | `125` / `100` | 100 | 125 | Internal |
| **24** | `speed` | 24 | `30` | 1 (Fast) | 100 (Slow)| Motion Speed |

---

## 9. Bluetooth Low Energy (BLE) Protocol Specification

### 9.1 Binary Packet Frame Structure
Every command and query sent over BLE Characteristic `0xFFE1` follows this frame structure:

```
┌──────────────┬──────────────────┬───────────────┬──────────────────────┬──────────────┐
│ Header       │ Length (N+2)     │ Opcode (Type) │ Payload / Data (N B) │ Checksum (1) │
│ 2 Bytes: FFFF│ 1 Byte           │ 1 Byte (Hex)  │ Optional Bytes       │ 1 Byte       │
└──────────────┴──────────────────┴───────────────┴──────────────────────┴──────────────┘
```

* **Header:** `0xFF 0xFF` (2 bytes)
* **Length (`numBytes`):** 1 byte = `1 (Opcode) + DataLength + 1 (Checksum)`
* **Opcode (`Type`):** 1 byte command identifier
* **Payload:** Variable length argument string, byte value, or binary struct
* **Checksum:** 1 byte calculated as:
  $$\text{Checksum} = (\text{numBytes} + \text{Opcode} + \sum \text{PayloadBytes}) \pmod{256}$$

### 9.2 Complete Protocol Opcode Reference

| Opcode (Hex) | Command Name | Direction | Payload Type | Description |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveForward` | TX | None | Initiates forward walking |
| `0x02` | `turnRight` | TX | None | Initiates right turning step |
| `0x03` | `moveRight` | TX | None | Initiates right side-step |
| `0x04` | `moveSouthEast` | TX | None | Steps backward to the right |
| `0x05` | `moveBackward` | TX | None | Initiates backward walking |
| `0x06` | `moveSouthWest` | TX | None | Steps backward to the left |
| `0x07` | `moveLeft` | TX | None | Initiates left side-step |
| `0x08` | `turnLeft` | TX | None | Initiates left turning step |
| `0x0B` | `handshake` | TX/RX | None | Connection verification ping |
| `0x0C` | `stop` | TX/RX | None | Emergency / immediate motion stop |
| `0x0D` | `volume` | TX | 1 Byte ($0–140$) | Sets speaker volume level |
| `0x0F` | `state` | TX/RX | 8-byte struct | Queries battery, volume, progress, auto-stand |
| `0x10` | `userNames` | TX/RX | String stream | Queries saved custom user choreography routines |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Enables/disables fall detection auto-stand |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Enables/disables auto power-off timer |
| `0x14` | `actionNames` | TX/RX | String stream | Queries built-in action library |
| `0x16` | `folderNames` | TX/RX | String stream | Queries audio/motion directory categories |
| `0x17` | `action` | TX/RX | String + Progress byte | Triggers action (e.g. `"ProAction/Left Punch"`) |
| `0x18` | `audioNames` | TX/RX | String stream | Queries available sound file list |
| `0x19` | `audio` | TX | String | Plays sound track (e.g. `"AppSysMS/101"`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Toggles auto-turning safety behavior |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Toggles auto-pose stabilization |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enters programming mode and reads joint positions |
| `0xE7` | `programExit` | TX | None | Exits programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Commands all 17 servos to target angles |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Reads back real-time live servo angles |
| `0xEA` | `jointUnlockAll` | TX | None | Releases motor torque on all joints for posing |
| `0xEB` | `jointLockAll` | TX | None | Engages motor torque holding position |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Locks or unlocks individual servo motors |
| `0xEE` | `play` | TX | Number | Triggers programmed sound/action index |
| `0xF6` | `kind` | TX/RX | String | Returns model name (e.g., `"K1"`) |
| `0xF7` | `version` | TX/RX | String | Returns robot firmware version |
| `0xF8` | `date` | TX/RX | String | Returns firmware compile date |
| `0xFA` | `shutdown` / `done` | TX/RX | None | Delimiter or power off command |

---

## 10. Safety Precautions, Maintenance & Handling

### 10.1 Operational Safety
* **Pinch Hazard:** The robot contains 17 high-torque servo motors. Keep fingers, loose hair, jewelry, and clothing clear of joint articulations (elbows, shoulders, hips, knees) during movement.
* **Surface Requirements:** Always operate the robot on smooth, flat, level, hard flooring (wood, tile, or smooth laminate). Do not operate on thick carpets, uneven surfaces, elevated tables without barriers, or near stairs.
* **Obstructions:** Do not attach heavy external weights or accessories that exceed motor payload capacities or restrict joint travel ranges.
* **Water & Moisture:** Keep the robot dry. Do not expose to rain, liquids, high humidity, or submerge in water. Clean only with a dry, soft microfiber cloth.

### 10.2 Battery Handling & Storage
* Do not store the robot in environments exceeding $45^\circ\text{C}$ ($113^\circ\text{F}$) or in direct sunlight (such as inside a hot vehicle).
* If storing for long periods, charge the battery to approximately $50–70\%$ every 3 months to maintain battery chemistry and prevent deep discharge.
* Do not pierce, disassemble, drop, or crush the lithium battery pack.

---

## 11. Troubleshooting & Frequently Asked Questions (FAQ)

| Issue / Symptom | Probable Cause | Recommended Solution |
| :--- | :--- | :--- |
| **Robot does not turn on** | Battery completely drained | Connect the official charger (8.4V 2A). Wait at least 15 minutes before attempting to power on. |
| **Robot does not respond to voice commands** | App is connected over BLE | Disconnect the robot from the mobile app. Voice control only functions when BLE app is closed. |
| | Ambient background noise too high | Move to a quieter room; speak clearly at normal volume within 1–2 meters using *"Hey, K One"*. |
| **Bluetooth connection fails** | Bluetooth disabled / permissions missing | Enable Bluetooth and Location Services on mobile device; ensure robot is powered on and within 5 meters. |
| | Connected to another phone/tablet | Disconnect existing paired device; restart the robot. |
| **Robot stumbles or falls during walking** | Operating on high-friction carpet / uneven surface | Move to a smooth, flat, rigid surface (hardwood, tile, smooth desk). |
| | Calibration drift / loose joint | Perform calibration in the app under Settings $\longrightarrow$ Servo Calibration. |
| **Joint feels loose / does not hold position** | Robot in manual posing mode (`jointUnlock`) | Tap Lock in app or send `0xEB` command to re-engage servo holding torque. |

---

## 12. Regulatory Compliance & FCC Statement

**FCC ID: 2ATNWK1**  
**FCC Compliance Statement (Part 15):**  
This device complies with Part 15 of the FCC Rules. Operation is subject to the following two conditions:
1. This device may not cause harmful interference, and
2. This device must accept any interference received, including interference that may cause undesired operation.

*Note:* This equipment has been tested and found to comply with the limits for a Class B digital device, pursuant to Part 15 of the FCC Rules. These limits are designed to provide reasonable protection against harmful interference in a residential installation. This equipment generates, uses, and can radiate radio frequency energy and, if not installed and used in accordance with the instructions, may cause harmful interference to radio communications.

**Manufacturer Contact & Support:**  
* **Company:** Robosen Robotics (Shenzhen) Co., Ltd.  
* **Official Website:** [https://www.robosen.com](https://www.robosen.com)  
* **Support Email:** `support@robosen.com` / `supportusa@robosen.com`  
