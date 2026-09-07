# Arduino Uno R3 as CH32V003 SWIO Programmer (Ardulink)

This sketch turns an ordinary **Arduino Uno R3** into a single-wire debug interface (SWIO) programmer for WCH **CH32V003** microcontrollers using the Ardulink protocol.

---

## 1. Hardware Connections

| Arduino Uno R3 Pin | TENSTAR CH32V003 Pin | Notes |
| :--- | :--- | :--- |
| **Pin 8** (`PB0`) | **`PD1` (SWIO)** | 1-wire SWIO data line. **1kΩ series resistor recommended** to protect against line contention during reset/sync. |
| **Pin 9** (`PB1`) | *(Optional)* Target VCC | Software-switched power. (If not used, connect board `V` to Arduino 5V or 3.3V directly). |
| **5V** (or **3.3V**) | **`V` (VCC)** | Power rail. CH32V003 operates safely up to 5.5V. |
| **GND** | **`G` (GND)** | Common ground. |

---

## 2. Step 1: Upload Programmer Firmware to Arduino Uno

1. Open `arduino_uno_ch32v003_programmer.ino` in the **Arduino IDE**.
2. Select **Tools > Board > Arduino AVR Boards > Arduino Uno**.
3. Select the COM port corresponding to your Arduino Uno.
4. Click **Upload** (Ctrl + U).

---

## 3. Step 2: Flash Firmware to CH32V003

Use **`minichlink`** (from the open-source [ch32v003fun](https://github.com/cnlohr/ch32fun) toolkit):

```bash
minichlink -a COMx -w your_firmware.bin 0x08000000
```
*(Replace `COMx` with your Arduino Uno's COM port, e.g., `COM3` or `/dev/ttyACM0`).*

### Verify or Read Target:
```bash
minichlink -a COMx -r test.bin 0x08000000 1024
```
