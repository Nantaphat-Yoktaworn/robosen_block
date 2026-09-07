# Robosen Tangible Modular Block - Smart End Block Firmware

Dedicated firmware for the **Smart End Block (Terminator Cap)** powered by the **WCH CH32V003F4P6** (32-bit RISC-V @ 24MHz).

---

## 1. Physical Role & Electrical Architecture

In the 4-Pin Magnetic Physical Bus:
* **Terminal End Cap**: The Smart End Block snaps onto the right side of the final Action Block in the sequence. It has **no downstream pins** (it caps the chain).
* **Active Line Driver Loopback**: Receives the assembled sequence on **Pin 3 (`PD6` RX)**, verifies the cumulative CRC-8 checksum, and actively drives the verified sequence onto **Pin 4 Return Rail (`PD5` TX)** directly back to the Master Block.
* **Visual Confirmation for Children**:
  - **Idle / Connected**: Soft Emerald Green (`0, 45, 10`) glowing calm and ready.
  - **Chain Verified & Ready**: Vivid Emerald Green (`0, 255, 30`) pulse (350ms).
  - **Program Complete**: Celebration **Rainbow Victory Sparkle** (`0xFF`).
* **Silent Return Rail Architecture**: Pin 4 Return Rail TX (`PD5`) remains 100% silent during idle to avoid bus contention, transmitting only when looping back verified Phase 1 (`0xAA`) sequences or responding to Config Dock queries (`0xCF`). Onboard LEDs toggle every 500ms as a silent liveness heartbeat.

---

## 2. Pin Connections (TENSTAR CH32V003F4P6)

| Pin Name | Board Label | Physical Role | Notes |
| :--- | :--- | :--- | :--- |
| **`PD6`** | **`RX`** | **Chain Data In** (115200 8N1) | Connects to last Action Block's Downstream TX (Pin 3 Out) |
| **`PD5`** | **`TX`** | **Return Rail Driver** (115200 8N1) | Connects to Pin 4 Return Rail (back to Master Return RX) |
| **`PA2`** | **`PA2`** | **WS2812B RGB LED** (DIN) | Drives the status & celebration RGB LED |
| **`PD4`** | **`PD4`** | **Onboard Activity LED** | Toggles on active packet processing |
| **`PC0`** | **`PC0`** | **Alternate Activity LED** | Parallel activity toggle |
| **`PD1`** | **`PD1`** | **SWIO** | 1-wire programming line (connected to ESP32 programmer only when flashing) |
| **`V`** | **`V`** | **3.3V Power** | System 3.3V power |
| **`G`** | **`G`** | **Ground** | System ground |

---

## 3. How to Flash the Smart End Block

### Step 1: Upload Programmer to ESP32
In Arduino IDE, open `firmware/esp32_ch32v003_programmer/esp32_ch32v003_programmer.ino` and upload to the ESP32 on `COM3`.

### Step 2: Wire Programmer to new CH32V003 IC
- **ESP32 3V3** $\longrightarrow$ **Tenstar `V`**
- **ESP32 GND** $\longrightarrow$ **Tenstar `G`**
- **ESP32 GPIO 10** $\longrightarrow$ **Tenstar `PD1` (SWIO)**

### Step 3: Run Flash Script
In PowerShell:
```powershell
python firmware/esp32_ch32v003_programmer/flash_tool.py --port COM3 --bin firmware/ch32v003_end_block/end_block.bin --reset
```

---

## 4. How to Test on Config Dock

1. Disconnect `GPIO 10`.
2. Connect UART to ESP32 Master:
   - **ESP32 GPIO 17** $\longrightarrow$ **Tenstar `RX` (PD6)**
   - **ESP32 GPIO 18** $\longrightarrow$ **Tenstar `TX` (PD5)**
3. Upload `firmware/esp32_master/esp32_master.ino`.
4. Open Serial Monitor:
   The Master will detect the Smart End Block and display:
   ```text
   ║ Config Dock: DOCKED 🟢 [0xEE] End Terminator (0 Cap) ║
   ```

---

## 5. How to Test Full Chain (Master -> Action Block -> End Block)

```text
[ESP32 Master]
   │  (Run Chain TX)  ──► [Action Block #1: RX]
   │                                   │
   │                      [Action Block #1: TX] ──► [Smart End Block: RX]
   │                                                             │
   │  (Return Rail RX) ◄─────────────────────────── [Smart End Block: TX]
   ▼
Master validates cumulative program!
```
