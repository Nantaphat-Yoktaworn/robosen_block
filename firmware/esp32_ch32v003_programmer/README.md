# ESP32 / ESP32-S3 CH32V003 SWIO Programmer

This firmware turns an **ESP32** or **ESP32-S3** (such as your Master Controller board) into a high-speed SWIO programmer and debugger for the **CH32V003F4P6**.

---

## 1. Hardware Connections

| ESP32 / ESP32-S3 Pin | TENSTAR CH32V003 Pin | Notes |
| :--- | :--- | :--- |
| **GPIO 10** | **`PD1` (SWIO)** | 1-wire bidirectional SWIO line. |
| — | Between **`PD1`** & **`V`** | **4.7kΩ to 10kΩ external pull-up resistor required**. |
| **3.3V** | **`V` (VCC)** | 3.3V power rail (matches ESP32 logic levels). |
| **GND** | **`G` (GND)** | Common ground. |

---

## 2. Step 1: Upload Programmer to ESP32

1. Open `esp32_ch32v003_programmer.ino` in the **Arduino IDE**.
2. Select your ESP32 board (e.g., **ESP32S3 Dev Module** or **ESP32 Dev Module**).
3. Select your ESP32 COM port and click **Upload**.

---

## 3. Step 2: Flash Firmware to CH32V003 Using Python

A companion Python CLI tool (`flash_tool.py`) is included in this directory.

1. Install pyserial if needed:
   ```bash
   pip install pyserial
   ```

2. Flash your binary:
   ```bash
   python flash_tool.py --port COMx --bin your_firmware.bin --addr 0x08000000 --reset
   ```
   *(Replace `COMx` with your ESP32's COM port).*
