# 2.13" E-Ink Display (DEPG0213BN / SSD1680) Hardware Guide & Test Sketch

This directory contains the standalone Arduino test firmware and complete hardware documentation for controlling the **2.13" E-Paper / E-Ink Display Module** using the **ESP32-S3 (DevKitC-1)** Master Block.

---

## 1. Hardware Overview & Specifications

| Parameter | Specification | Notes |
| :--- | :--- | :--- |
| **Display Model** | **DEPG0213BN** (DKE / GoodDisplay) | 2.13" Active Matrix Electrophoretic Display |
| **Driver IC** | **SSD1680** (or JD79661 variant) | Built-in OTP Look-Up Table (LUT) waveform |
| **Resolution** | **122 x 250 Pixels** | Black & White (1-bit monochrome) |
| **Interface** | **4-Wire SPI** | High-speed SPI up to 10 MHz |
| **Logic Voltage** | **3.3V DC** | ⚠️ **Never connect to 5V!** |
| **Full Refresh Time** | ~2.0 – 3.0 s | Alternating black/white clearing waveform |
| **Partial Refresh Time** | **727 ms** (`_Update_Part: 726998 µs`) | Measured live on silicon |
| **Max Refresh Rate** | **1.34 updates/sec** (~746 ms roundtrip) | Hardware waveform limit of DEPG0213BN |

> [!WARNING]
> **Power Supply Rule:** Always connect `VCC` to the ESP32-S3 **3.3V (`3V3`)** pin. Connecting to 5V or VIN will permanently damage the electrophoretic microcapsules and driver silicon.

---

## 2. Complete ESP32-S3 Wiring Pinout

Even though breakout boards frequently label the clock and data pins as **`SCL`** and **`SDA`**, this module uses **4-Wire SPI** (not I2C) because it includes dedicated **`CS`** (Chip Select) and **`DC`** (Data/Command) control lines.

| E-Ink Breakout Pin | Signal Name | ESP32-S3 GPIO | Recommended Wire Color | Hardware Role |
| :---: | :---: | :---: | :---: | :--- |
| **`VCC`** | Power | **`3V3`** | 🔴 Red | 3.3V DC power rail |
| **`GND`** | Ground | **`GND`** | ⚫ Black | System ground rail |
| **`SCL`** | SPI Clock (`SCK`) | **`GPIO 21`** | 🟢 Green | Hardware SPI Clock |
| **`SDA`** | SPI MOSI (`DIN`) | **`GPIO 38`** | ⚪ White | Master-Out Slave-In SPI Data |
| **`RES`** | Reset (`RST`) | **`GPIO 5`** | 🟤 Brown | Active-Low hardware reset |
| **`DC`** | Data / Command | **`GPIO 6`** | 🟣 Purple | High = Data, Low = Command |
| **`CS`** | Chip Select | **`GPIO 7`** | 🟡 Yellow | Active-Low chip select |
| **`BUSY`** | Status Flag | **`GPIO 4`** | 🔘 Gray | High when refreshing, Low when idle |

*All GPIO allocations avoid ESP32-S3 strapping pins, USB CDC lines, UART Config/Run ports, and internal Octal PSRAM/Flash lines (GPIOs 33–37 on N16R8).*

---

## 3. Required Arduino Libraries

Install the following libraries via the **Arduino IDE Library Manager** (`Ctrl + Shift + I`):
1. **`GxEPD2`** (by *Jean-Marc Zingg*) – High-performance e-paper display library with partial refresh paging.
2. **`Adafruit GFX Library`** (by *Adafruit*) – Core 2D graphics primitives (text, fonts, lines, circles, bitmaps).

---

## 4. Driver Architecture & Configuration

### A. Display Driver Class
In `standalone_eink_test.ino`, the display is instantiated using the exact matching driver for the **DEPG0213BN** panel:

```cpp
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT> display(
  GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);
```

> [!NOTE]
> Testing showed that alternative driver classes like `GxEPD2_213_B74` freeze this panel because their initialization commands and custom LUT timings are rejected by the DEPG0213BN controller. **Always use `GxEPD2_213_BN` for this screen.**

### B. Hardware SPI Initialization on ESP32-S3
Because the ESP32-S3 allows custom pin routing via the GPIO matrix, the SPI bus must be initialized and explicitly linked to `GxEPD2`:

```cpp
// 1. Initialize SPI with custom SCL (21) and SDA (38) pins
SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);

// 2. Explicitly bind SPI bus to GxEPD2 at 4 MHz
display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));
```

---

## 5. How to Eliminate Startup Blinking (`SKIP_BOOT_BLINKING`)

By default, e-paper libraries execute a full clear sequence at boot (`display.init(..., initial=true)`), causing violent black/white invert flashing and waiting up to 10 seconds on the busy line (`Busy Timeout!`).

In this firmware, boot blinking is completely bypassed:
```cpp
#define SKIP_BOOT_BLINKING 1
```

### Under the Hood:
1. **`display.init(115200, false, 2, false)`**: Passing `initial = false` prevents GxEPD2 from executing the initial screen wipe.
2. **`display.setPartialWindow(0, 0, display.width(), display.height())`**: The initial base UI is rendered using the **partial refresh waveform** instead of full refresh.
3. **Result:** Screen transitions smoothly in **`~746 ms`** with zero flashing, zero timeouts, and instant boot response.

---

## 6. How to Perform Fast Partial Refreshes (e.g., Rotary Knob Adjustments)

For interactive elements (such as action names, parameters, or progress counters), update only a localized bounding box:

```cpp
void drawPartialCounter(int count, unsigned long lastDurationMs) {
  // Use byte-aligned coordinates (multiples of 8) for optimal SPI transfer
  uint16_t boxX = 8;
  uint16_t boxY = 56;
  uint16_t boxW = 144;
  uint16_t boxH = 42;

  display.setPartialWindow(boxX, boxY, boxW, boxH);
  display.firstPage();
  do {
    // 1. Clear bounding box background
    display.fillRect(boxX, boxY, boxW, boxH, GxEPD_WHITE);
    display.drawRoundRect(boxX, boxY, boxW, boxH, 4, GxEPD_BLACK);

    // 2. Draw text inside the box
    display.setTextColor(GxEPD_BLACK);
    display.setTextSize(1);
    display.setCursor(boxX + 6, boxY + 8);
    display.printf("Count: %d", count);

    display.setCursor(boxX + 6, boxY + 24);
    if (lastDurationMs > 0) {
      display.printf("Time: %lums (%.1fHz)", lastDurationMs, 1000.0f / lastDurationMs);
    }
  } while (display.nextPage());
}
```

### Best Practices:
* **Byte Alignment:** Set `boxX` and `boxW` to multiples of 8 (`8, 16, 24, ...`) to eliminate bit-shift overhead in display memory.
* **Ghosting Maintenance:** Over hundreds of continuous partial refreshes, faint electrical charge ghosting may appear. Triggering a single full refresh (`display.setFullWindow()`) once every ~50 to 100 updates completely resets the particles.

---

## 7. Silicon Verification Benchmark Results

Live physical benchmark on ESP32-S3:

```text
[1/4] Starting SPI bus...
[2/4] BUSY pin level at boot: 0 (0 = Ready, 1 = Busy)
[3/4] Initializing e-ink controller...
[3/4] Boot blinking disabled (Smooth Partial Mode enabled).
[4/4] Drawing initial screen using Smooth Partial Refresh (No flicker)...
_PowerOn : 94001
_Update_Part : 726998
>> Initial screen update complete!

Beginning Partial Refresh loop...
_Update_Part : 726998
[REFRESH BENCHMARK] Count: 48   | Refresh: 746 ms | Rate: 1.34 updates/sec (Target: 2.0)
_Update_Part : 726999
[REFRESH BENCHMARK] Count: 49   | Refresh: 746 ms | Rate: 1.34 updates/sec (Target: 2.0)
_Update_Part : 726998
[REFRESH BENCHMARK] Count: 50   | Refresh: 746 ms | Rate: 1.34 updates/sec (Target: 2.0)
```

* **SPI Transmission:** ~19 ms
* **Panel Electrophoretic Waveform:** 727 ms
* **Verified Silicon Max Speed:** **`1.34 Hz` (~746 ms)**
