# Robosen K1 Onboard Filesystem & Deep Architecture Archive

> **Captured Date:** August 28, 2026 - 17:09:39  
> **Robot Model:** `Robosen K1 (Interstellar Scout)`  
> **Firmware Version:** `VER:3.03L` (`SH2022-07-23`)  

---

## 1. Complete Internal Filesystem Hierarchy (Discovered via Opcode `0xE2`)

The Robosen K1 flash storage contains the following directory tree and files:


---

## 2. 50-Byte Telemetry & IMU Packet Structure (`0xF1` Query -> `0xF0` Stream)

Queried via `0xF1`, the robot streams high-speed 50-byte binary telemetry blocks (`0xF0`):

```
Header: 0xFF 0xFF
Length: 0x32 (50 Bytes)
Opcode: 0xF0
```

Raw sample captures:

---

## 3. Verified Opcode Catalog (Exhaustive Reverse Engineering Matrix)

| Opcode (Hex) | Name / Category | Direction | Payload Structure | Physical Robot Behavior |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveForward` | TX | None | Bipedal continuous forward walking |
| `0x02` | `turnRight` | TX | None | Right heading step articulation |
| `0x03` | `moveRight` | TX | None | Right lateral sidestep |
| `0x04` | `moveSouthEast` | TX | None | Diagonal backward-right step |
| `0x05` | `moveBackward` | TX | None | Backward walking step |
| `0x06` | `moveSouthWest` | TX | None | Diagonal backward-left step |
| `0x07` | `moveLeft` | TX | None | Left lateral sidestep |
| `0x08` | `turnLeft` | TX | None | Left heading step articulation |
| `0x0B` | `handshake` | TX/RX | `0x00` (Ack) | Alive heartbeat connection check |
| `0x0C` | `stop` | TX | None | Emergency / immediate motion halt |
| `0x0D` | `volume` | TX | Byte ($0-140$) | Speaker volume configuration |
| `0x0F` | `state` | TX/RX | 8-byte struct | Battery, Volume, AutoStand, AutoTurn, AutoOff |
| `0x10` | `userNames` | TX/RX | String stream | Custom choreography names |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Fall recovery gyroscope auto-stand |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Power-saving auto-off timer |
| `0x14` | `actionNames` | TX/RX | String stream | Built-in action name catalog (60+ actions) |
| `0x16` | `folderNames` | TX/RX | Delimiter | Audio/Action category listing |
| `0x17` | `action` | TX/RX | Path string + Progress | Action execution with live % progress ACK |
| `0x18` | `audioNames` | TX/RX | String stream | Sound track identifier query |
| `0x19` | `audio` | TX | String path | Audio playback (e.g. `"AppSysMS/..."`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Yaw drift gyroscope balance correction |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Autonomous idle posture animations |
| `0xE0` | `readEE` | TX/RX | String | Internal EEPROM / config check |
| `0xE1` | `writeEE` | TX/RX | String | Internal EEPROM / parameter storage |
| `0xE2` | `dirList` | TX/RX | Path string / Results | Filesystem directory & file explorer |
| `0xE3` | `fileCheck` | TX/RX | String / `OK` | File existence / checksum verification |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter kinesthetic programming timeline |
| `0xE7` | `programExit` | TX | None | Exit kinesthetic programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Direct 17-servo coordinate command + speed |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Real-time live angle feedback of all 17 servos |
| `0xEA` | `jointUnlockAll` | TX | None | Release motor torque on all joints |
| `0xEB` | `jointLockAll` | TX | None | Re-engage motor holding torque |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Per-servo holding torque configuration |
| `0xEE` | `play` | TX | Number | Programmed sound/action trigger |
| `0xF0` | `imuStream` | RX | 50-byte struct | Real-time 6-axis IMU & joint telemetry buffer |
| `0xF1` | `imuQuery` | TX | None | Query 50-byte IMU / sensor buffer |
| `0xF5` | `factoryTest` | TX/RX | Byte stream | Factory calibration & testing mode |
| `0xF6` | `kind` | TX/RX | String (`"K1"`) | Model name |
| `0xF7` | `version` | TX/RX | String (`"VER:3.03L"`) | Firmware version |
| `0xF8` | `date` | TX/RX | String (`"SH2022-07-23"`) | Firmware compile date |
| `0xFA` | `delimiter` | RX | `0xFA` / `OK` | EOF stream delimiter / packet ACK |
