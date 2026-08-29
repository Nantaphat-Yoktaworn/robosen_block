#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEClient.h>
#include <BLEAdvertisedDevice.h>
#include <Preferences.h>

// ==============================================================================
// 1. PIN DEFINITIONS & COLOR-CODED WIRING MAP (PROTOTYPE #01 SPEC)
// ==============================================================================
// 🔴 Red:    +3.3V Power Rail (ESP32 3V3 -> Breadboard + Rail -> Encoder VCC)
// ⚫ Black:  Common GND Rail  (ESP32 GND -> Breadboard - Rail -> Encoder GND / Button GND)
// 🟡 Yellow: Rotary Encoder CLK (Phase A) -> GPIO 8
// 🟢 Green:  Rotary Encoder DT  (Phase B) -> GPIO 9
// 🔵 Blue:   Rotary Encoder SW  (Push Click) -> GPIO 10
// 🟠 Orange: Tactile Start Button (Diagonal Trigger) -> GPIO 14
// ==============================================================================
const int PIN_ENC_CLK   = 8;
const int PIN_ENC_DT    = 9;
const int PIN_ENC_SW    = 10;
const int PIN_START_BTN = 14;

// Onboard WS2812 RGB LED (GPIO 48 on ESP32-S3 DevKitC-1)
#ifndef RGB_BUILTIN
  #define RGB_BUILTIN 48
#endif

void setStatusLED(uint8_t r, uint8_t g, uint8_t b) {
  #ifdef RGB_BUILTIN
    neopixelWrite(RGB_BUILTIN, r, g, b);
  #endif
}

// ==============================================================================
// 2. ROBOSEN K1 BLE GATT PROTOCOL DEFINITIONS
// ==============================================================================
static BLEUUID SERVICE_UUID("0000ffe0-0000-1000-8000-00805f9b34fb");
static BLEUUID CHAR_UUID   ("0000ffe1-0000-1000-8000-00805f9b34fb");

// ==============================================================================
// 3. ROBOSEN ACTION LIBRARY CATALOG
// ==============================================================================
struct RobosenAction {
  const char* name;
  uint8_t opcode;
  const char* payload;
};

const RobosenAction ACTIONS[] = {
  {"01: Walk Forward",   0x01, ""},
  {"02: Walk Backward",  0x05, ""},
  {"03: Turn Left 90°",  0x08, ""},
  {"04: Turn Right 90°", 0x02, ""},
  {"05: Punch Left",     0x17, "ProAction/Left Punch"},
  {"06: Push-ups",       0x17, "ProAction/Push Ups"},
  {"07: Wave Hand",      0x17, "ProAction/Say Hello"}
};
const int TOTAL_ACTIONS = sizeof(ACTIONS) / sizeof(ACTIONS[0]);
int currentActionIndex = 4; // Default: Punch Left

// ==============================================================================
// 4. SYSTEM STATE MACHINE & STORAGE
// ==============================================================================
enum SystemState { 
  STATE_ACTION_MENU, 
  STATE_BLE_SCANNING, 
  STATE_BLE_PAIRING_MENU 
};
SystemState currentState = STATE_ACTION_MENU;

Preferences preferences;
String pairedMAC  = "None (Unpaired)";
String pairedName = "None";

struct DiscoveredDevice { 
  String name; 
  String address; 
  int rssi; 
};
const int MAX_BLE_DEVICES = 10;
DiscoveredDevice bleList[MAX_BLE_DEVICES];
int bleDeviceCount = 0;
int currentBleIndex = 0;

int lastClkState = HIGH;
unsigned long startBtnPressTime = 0;
bool startBtnHeld = false;

// Forward Declarations
void renderActionMenu();
void renderPairingMenu();
void runBleScan();
bool sendRobosenPacket(const RobosenAction& action);

// ==============================================================================
// 5. HARDWARE SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(1500);

  // Initialize Input Pins with Internal Pull-Up Resistors
  pinMode(PIN_ENC_CLK, INPUT_PULLUP);
  pinMode(PIN_ENC_DT, INPUT_PULLUP);
  pinMode(PIN_ENC_SW, INPUT_PULLUP);
  pinMode(PIN_START_BTN, INPUT_PULLUP);
  lastClkState = digitalRead(PIN_ENC_CLK);

  // Load Saved Robot Binding from NVS Flash Partition
  preferences.begin("robosen_cfg", false);
  pairedMAC  = preferences.getString("paired_mac", "None (Unpaired)");
  pairedName = preferences.getString("paired_name", "None");

  // Initialize Bluetooth Low Energy Subsystem
  BLEDevice::init("Robosen_Master_Block");

  // Update Status LED based on NVS State
  if (pairedMAC == "None (Unpaired)") {
    setStatusLED(30, 0, 0); // 🔴 Red: Unpaired
  } else {
    setStatusLED(0, 30, 0); // 🟢 Emerald Green: Ready & Paired!
  }

  Serial.println("\n[SYSTEM] ESP32-S3 Master Hardware Initialized.");
  renderActionMenu();
}

// ==============================================================================
// 6. MAIN EVENT LOOP
// ==============================================================================
void loop() {
  // --- 1. ROTARY ENCODER ROTATION (SHARED NAVIGATOR) ---
  int clkState = digitalRead(PIN_ENC_CLK);
  if (clkState != lastClkState && clkState == LOW) {
    bool cw = (digitalRead(PIN_ENC_DT) != clkState);

    if (currentState == STATE_ACTION_MENU) {
      currentActionIndex = cw ? (currentActionIndex + 1) % TOTAL_ACTIONS 
                              : (currentActionIndex - 1 + TOTAL_ACTIONS) % TOTAL_ACTIONS;
      renderActionMenu();
    } 
    else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      currentBleIndex = cw ? (currentBleIndex + 1) % bleDeviceCount 
                           : (currentBleIndex - 1 + bleDeviceCount) % bleDeviceCount;
      renderPairingMenu();
    }
    delay(5); // Quadrature debounce
  }
  lastClkState = clkState;

  // --- 2. ENCODER PUSH BUTTON (SW) ---
  static bool lastSwState = HIGH;
  bool swState = digitalRead(PIN_ENC_SW);
  if (lastSwState == HIGH && swState == LOW) {
    if (currentState == STATE_ACTION_MENU) {
      Serial.printf("\n>>> [KNOB CLICKED] Selected: %s <<<\n", ACTIONS[currentActionIndex].name);
      // Soft flash to acknowledge click
      setStatusLED(0, 60, 30);
      delay(80);
      setStatusLED(0, 30, 0);
    } 
    else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      // Save selected device to NVS Flash memory
      pairedMAC  = bleList[currentBleIndex].address;
      pairedName = bleList[currentBleIndex].name;
      preferences.putString("paired_mac", pairedMAC);
      preferences.putString("paired_name", pairedName);

      Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
      Serial.printf("║  [NVS FLASH SAVED] Paired to: %-33s║\n", pairedName.c_str());
      Serial.printf("║  MAC Address:                 %-33s║\n", pairedMAC.c_str());
      Serial.println("╚════════════════════════════════════════════════════════════════╝");

      setStatusLED(0, 50, 0); // 🟢 Confirmed Green
      currentState = STATE_ACTION_MENU;
      delay(1000);
      renderActionMenu();
    }
    delay(200); // Debounce
  }
  lastSwState = swState;

  // --- 3. TACTILE START BUTTON (SHORT PRESS = RUN | 3s HOLD = PAIR) ---
  int btnState = digitalRead(PIN_START_BTN);
  if (btnState == LOW) {
    if (startBtnPressTime == 0) {
      startBtnPressTime = millis();
      startBtnHeld = false;
    } else if (!startBtnHeld && (millis() - startBtnPressTime >= 3000)) {
      startBtnHeld = true;
      runBleScan();
    }
  } else {
    if (startBtnPressTime > 0) {
      unsigned long duration = millis() - startBtnPressTime;
      if (duration < 3000 && !startBtnHeld) {
        if (currentState == STATE_ACTION_MENU) {
          sendRobosenPacket(ACTIONS[currentActionIndex]);
        } else if (currentState == STATE_BLE_PAIRING_MENU) {
          currentState = STATE_ACTION_MENU;
          setStatusLED((pairedMAC == "None (Unpaired)") ? 30 : 0, 
                       (pairedMAC == "None (Unpaired)") ? 0 : 30, 0);
          renderActionMenu();
        }
      }
      startBtnPressTime = 0;
      startBtnHeld = false;
    }
  }
}

// ==============================================================================
// 7. BUILD & TRANSMIT ROBOSEN BINARY PACKET
// ==============================================================================
bool sendRobosenPacket(const RobosenAction& action) {
  if (pairedMAC == "None (Unpaired)") {
    Serial.println("\n[ERROR] No robot paired! Hold Start for 3s to pair.");
    setStatusLED(40, 0, 0); // 🔴 Red error
    delay(500);
    return false;
  }

  setStatusLED(40, 30, 0); // 🟡 Yellow: Active BLE Transmitting

  Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
  Serial.printf("║  [TRANSMITTING] Connecting to: %-32s║\n", pairedName.c_str());
  Serial.printf("║  Target MAC:                   %-32s║\n", pairedMAC.c_str());
  Serial.printf("║  Action:                       %-32s║\n", action.name);
  Serial.println("╚════════════════════════════════════════════════════════════════╝");

  // Construct Binary Packet: [0xFF, 0xFF, NumBytes, Opcode, Payload..., Checksum]
  uint8_t payloadLen = strlen(action.payload);
  uint8_t numBytes = 1 + payloadLen + 1; // opcode + payload + checksum
  uint8_t totalPacketLen = 2 + numBytes + 1;
  uint8_t packet[totalPacketLen];

  packet[0] = 0xFF;
  packet[1] = 0xFF;
  packet[2] = numBytes;
  packet[3] = action.opcode;

  uint16_t checksum = numBytes + action.opcode;
  for (int i = 0; i < payloadLen; i++) {
    packet[4 + i] = (uint8_t)action.payload[i];
    checksum += packet[4 + i];
  }
  packet[totalPacketLen - 1] = (uint8_t)(checksum % 256);

  Serial.print("[HEX PACKET] ");
  for (int i = 0; i < totalPacketLen; i++) {
    Serial.printf("%02X ", packet[i]);
  }
  Serial.println();

  BLEClient* pClient = BLEDevice::createClient();

  // Support both Random Address (phone advertiser) and Public Address (real robot)
  BLEAddress pAddressRandom(pairedMAC.c_str(), BLE_ADDR_RANDOM);
  BLEAddress pAddressPublic(pairedMAC.c_str(), BLE_ADDR_PUBLIC);

  bool connected = pClient->connect(pAddressRandom);
  if (!connected) {
    connected = pClient->connect(pAddressPublic);
  }

  if (!connected) {
    Serial.println("[BLE] Connection failed. Make sure device is awake & connectable.");
    setStatusLED(40, 0, 0); // 🔴 Flash red on fail
    delay(400);
    setStatusLED(0, 30, 0);
    delete pClient;
    return false;
  }

  Serial.println("[BLE] Connected! Discovering services...");
  BLERemoteService* pRemoteService = pClient->getService(SERVICE_UUID);
  if (pRemoteService == nullptr) {
    Serial.println("[BLE] Target connected successfully! (Service 0xFFE0 not active on target).");
    setStatusLED(0, 30, 0); // 🟢 Back to green
    pClient->disconnect();
    delete pClient;
    return true;
  }

  BLERemoteCharacteristic* pRemoteChar = pRemoteService->getCharacteristic(CHAR_UUID);
  if (pRemoteChar != nullptr && pRemoteChar->canWrite()) {
    pRemoteChar->writeValue(packet, totalPacketLen);
    Serial.println(">>> [SUCCESS] Binary packet written to remote characteristic! <<<");
  }

  setStatusLED(0, 40, 0); // 🟢 Solid emerald green
  pClient->disconnect();
  delete pClient;
  return true;
}

// ==============================================================================
// 8. BLE SCANNING ROUTINE (DISCOVERY & RSSI PROXIMITY SORTING)
// ==============================================================================
void runBleScan() {
  currentState = STATE_BLE_SCANNING;
  setStatusLED(0, 0, 40); // 🔵 Blue: Active BLE Scanning

  Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
  Serial.println("║            [TEACHER PAIRING MODE: SCANNING BLE...]             ║");
  Serial.println("║  Scanning nearby Bluetooth devices for 4 seconds...            ║");
  Serial.println("╚════════════════════════════════════════════════════════════════╝");

  BLEScan* pBLEScan = BLEDevice::getScan();
  pBLEScan->setActiveScan(true);
  pBLEScan->setInterval(100);
  pBLEScan->setWindow(99);

  BLEScanResults* results = pBLEScan->start(4, false);
  bleDeviceCount = 0;

  int totalFound = results->getCount();
  for (int i = 0; i < totalFound && bleDeviceCount < MAX_BLE_DEVICES; i++) {
    BLEAdvertisedDevice device = results->getDevice(i);
    String devName = device.getName().c_str();
    if (devName.length() == 0) devName = "Unknown Device";
    bleList[bleDeviceCount].name    = devName;
    bleList[bleDeviceCount].address = device.getAddress().toString().c_str();
    bleList[bleDeviceCount].rssi    = device.getRSSI();
    bleDeviceCount++;
  }

  // Sort devices by RSSI descending (strongest/closest signal at top)
  for (int i = 0; i < bleDeviceCount - 1; i++) {
    for (int j = 0; j < bleDeviceCount - i - 1; j++) {
      if (bleList[j].rssi < bleList[j + 1].rssi) {
        DiscoveredDevice temp = bleList[j];
        bleList[j] = bleList[j + 1];
        bleList[j + 1] = temp;
      }
    }
  }

  pBLEScan->clearResults();
  currentBleIndex = 0;
  currentState = STATE_BLE_PAIRING_MENU;
  setStatusLED(0, 0, 30); // 🔵 Soft blue in pairing menu
  renderPairingMenu();
}

// ==============================================================================
// 9. SERIAL DISPLAY RENDERING
// ==============================================================================
void renderActionMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
  Serial.println("║              ROBOSEN K1 PHYSICAL BLOCK CONTROLLER              ║");
  Serial.printf("║ Paired Target: %-47s ║\n", (pairedName + " (" + pairedMAC + ")").c_str());
  Serial.println("╠════════════════════════════════════════════════════════════════╣");
  for (int i = 0; i < TOTAL_ACTIONS; i++) {
    if (i == currentActionIndex) {
      Serial.printf("║  ► [%-20s]  ◄ (READY TO TRANSMIT)       ║\n", ACTIONS[i].name);
    } else {
      Serial.printf("║     %-58s ║\n", ACTIONS[i].name);
    }
  }
  Serial.println("╠════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Turn Knob: Select Action      • Start Click: Transmit Action ║");
  Serial.println("║ • Hold Start: Re-Pair BLE (3s)                                 ║");
  Serial.println("╚════════════════════════════════════════════════════════════════╝");
}

void renderPairingMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
  Serial.println("║                TEACHER BLE PAIRING DISCOVERY                   ║");
  Serial.println("╠════════════════════════════════════════════════════════════════╣");
  if (bleDeviceCount == 0) {
    Serial.println("║  No BLE devices discovered. Press Start button to exit.        ║");
  } else {
    for (int i = 0; i < bleDeviceCount; i++) {
      char row[70];
      if (i == currentBleIndex) {
        snprintf(row, sizeof(row), "║  ► [%d] %-18s (%3d dBm) %-17s ◄║", 
                 i + 1, bleList[i].name.substring(0, 18).c_str(), bleList[i].rssi, bleList[i].address.c_str());
      } else {
        snprintf(row, sizeof(row), "║    [%d] %-18s (%3d dBm) %-17s  ║", 
                 i + 1, bleList[i].name.substring(0, 18).c_str(), bleList[i].rssi, bleList[i].address.c_str());
      }
      Serial.println(row);
    }
  }
  Serial.println("╠════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Turn Knob: Scroll List       • Click Knob: Save to NVS Flash ║");
  Serial.println("║ • Start Click: Cancel & Exit                                   ║");
  Serial.println("╚════════════════════════════════════════════════════════════════╝");
}
