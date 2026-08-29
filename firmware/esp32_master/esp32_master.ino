#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEClient.h>
#include <BLEAdvertisedDevice.h>
#include <Preferences.h>

// ==============================================================================
// 1. PIN DEFINITIONS (PROTOTYPE #01 SPEC - DUAL-KNOB SYSTEM)
// ==============================================================================
// --- KNOB 1: ACTION SELECTOR ---
const int PIN_K1_CLK    = 8;   // 🟡 Yellow Wire
const int PIN_K1_DT     = 9;   // 🟢 Green Wire
const int PIN_K1_SW     = 10;  // 🔵 Blue Wire

// --- KNOB 2: PARAMETER ADJUSTER ---
const int PIN_K2_CLK    = 11;  // ⚪ White Wire
const int PIN_K2_DT     = 12;  // 🟤 Brown Wire
const int PIN_K2_SW     = 13;  // 🔘 Gray Wire

// --- MASTER START BUTTON ---
const int PIN_START_BTN = 14;  // 🟠 Orange Wire (Diagonal GND Return)

// --- ONBOARD WS2812 RGB STATUS LED ---
#ifndef RGB_BUILTIN
  #define RGB_BUILTIN 48       // ESP32-S3 DevKitC-1 onboard RGB
#endif

void setStatusLED(uint8_t r, uint8_t g, uint8_t b) {
  #ifdef RGB_BUILTIN
    rgbLedWrite(RGB_BUILTIN, r, g, b);
  #endif
}

// ==============================================================================
// 2. ROBOSEN K1 BLE GATT PROTOCOL DEFINITIONS
// ==============================================================================
static BLEUUID SERVICE_UUID("0000ffe0-0000-1000-8000-00805f9b34fb");
static BLEUUID CHAR_UUID   ("0000ffe1-0000-1000-8000-00805f9b34fb");

// ==============================================================================
// 3. ACTION & PARAMETER DEFINITIONS
// ==============================================================================
struct RobosenAction {
  const char* name;
  uint8_t opcode;
  const char* payload;
  const char* paramUnit;
  int paramVal;
  int paramMin;
  int paramMax;
  int paramStep;
};

RobosenAction ACTIONS[] = {
  {"01: Walk Forward",   0x01, "",                      "Steps", 1,   1,   5,   1},
  {"02: Walk Backward",  0x05, "",                      "Steps", 1,   1,   5,   1},
  {"03: Turn Left",      0x08, "",                      "Deg°",  90,  45,  180, 45},
  {"04: Turn Right",     0x02, "",                      "Deg°",  90,  45,  180, 45},
  {"05: Punch Left",     0x17, "ProAction/Left Punch",  "Reps",  1,   1,   3,   1},
  {"06: Push-ups",       0x17, "ProAction/Push Ups",    "Reps",  1,   1,   3,   1},
  {"07: Wave Hand",      0x17, "ProAction/Say Hello",   "Reps",  1,   1,   3,   1}
};
const int TOTAL_ACTIONS = sizeof(ACTIONS) / sizeof(ACTIONS[0]);
int currentActionIndex = 0; // Default: Walk Forward

// ==============================================================================
// 4. SYSTEM STATE & MEMORY
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

// Debounce & Timing States
int lastK1Clk = HIGH;
int lastK2Clk = HIGH;
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

  // Configure Internal Pull-Up Resistors for all inputs
  pinMode(PIN_K1_CLK, INPUT_PULLUP);
  pinMode(PIN_K1_DT,  INPUT_PULLUP);
  pinMode(PIN_K1_SW,  INPUT_PULLUP);

  pinMode(PIN_K2_CLK, INPUT_PULLUP);
  pinMode(PIN_K2_DT,  INPUT_PULLUP);
  pinMode(PIN_K2_SW,  INPUT_PULLUP);

  pinMode(PIN_START_BTN, INPUT_PULLUP);

  lastK1Clk = digitalRead(PIN_K1_CLK);
  lastK2Clk = digitalRead(PIN_K2_CLK);

  // Load Saved Robot Binding from NVS Flash
  preferences.begin("robosen_cfg", false);
  pairedMAC  = preferences.getString("paired_mac", "None (Unpaired)");
  pairedName = preferences.getString("paired_name", "None");

  // Initialize BLE Stack
  BLEDevice::init("Robosen_Master_Block");

  // Set Status LED
  if (pairedMAC == "None (Unpaired)") {
    setStatusLED(30, 0, 0); // 🔴 Red: Unpaired
  } else {
    setStatusLED(0, 30, 0); // 🟢 Emerald Green: Ready
  }

  Serial.println("\n[SYSTEM] ESP32-S3 Dual-Knob Master Initialized.");
  renderActionMenu();
}

// ==============================================================================
// 6. MAIN EVENT LOOP
// ==============================================================================
void loop() {
  // --------------------------------------------------------------------------
  // --- KNOB 1: ACTION SELECTOR (CLK: 8, DT: 9, SW: 10) ---
  // --------------------------------------------------------------------------
  int k1Clk = digitalRead(PIN_K1_CLK);
  if (k1Clk != lastK1Clk && k1Clk == LOW) {
    bool cw = (digitalRead(PIN_K1_DT) != k1Clk);
    if (currentState == STATE_ACTION_MENU) {
      currentActionIndex = cw ? (currentActionIndex + 1) % TOTAL_ACTIONS 
                              : (currentActionIndex - 1 + TOTAL_ACTIONS) % TOTAL_ACTIONS;
      renderActionMenu();
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      currentBleIndex = cw ? (currentBleIndex + 1) % bleDeviceCount 
                           : (currentBleIndex - 1 + bleDeviceCount) % bleDeviceCount;
      renderPairingMenu();
    }
    delay(5);
  }
  lastK1Clk = k1Clk;

  // Knob 1 Click (Select Action / Confirm)
  static bool lastK1Sw = HIGH;
  bool k1Sw = digitalRead(PIN_K1_SW);
  if (lastK1Sw == HIGH && k1Sw == LOW) {
    if (currentState == STATE_ACTION_MENU) {
      Serial.printf("\n>>> [KNOB 1 CLICK] Selected Action: %s <<<\n", ACTIONS[currentActionIndex].name);
      setStatusLED(0, 60, 30);
      delay(80);
      setStatusLED(0, 30, 0);
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      // Save BLE Device
      pairedMAC  = bleList[currentBleIndex].address;
      pairedName = bleList[currentBleIndex].name;
      preferences.putString("paired_mac", pairedMAC);
      preferences.putString("paired_name", pairedName);
      setStatusLED(0, 50, 0);
      currentState = STATE_ACTION_MENU;
      delay(1000);
      renderActionMenu();
    }
    delay(200);
  }
  lastK1Sw = k1Sw;

  // --------------------------------------------------------------------------
  // --- KNOB 2: PARAMETER ADJUSTER (CLK: 11, DT: 12, SW: 13) ---
  // --------------------------------------------------------------------------
  int k2Clk = digitalRead(PIN_K2_CLK);
  if (k2Clk != lastK2Clk && k2Clk == LOW) {
    // Inverted so Clockwise INCREASES the parameter
    bool cw = (digitalRead(PIN_K2_DT) == k2Clk);
    if (currentState == STATE_ACTION_MENU) {
      RobosenAction& act = ACTIONS[currentActionIndex];
      if (cw) {
        act.paramVal += act.paramStep;
        if (act.paramVal > act.paramMax) act.paramVal = act.paramMax;
      } else {
        act.paramVal -= act.paramStep;
        if (act.paramVal < act.paramMin) act.paramVal = act.paramMin;
      }
      renderActionMenu();
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      currentBleIndex = cw ? (currentBleIndex + 1) % bleDeviceCount 
                           : (currentBleIndex - 1 + bleDeviceCount) % bleDeviceCount;
      renderPairingMenu();
    }
    delay(5);
  }
  lastK2Clk = k2Clk;

  // Knob 2 Click (Reset Parameter to Default)
  static bool lastK2Sw = HIGH;
  bool k2Sw = digitalRead(PIN_K2_SW);
  if (lastK2Sw == HIGH && k2Sw == LOW) {
    if (currentState == STATE_ACTION_MENU) {
      RobosenAction& act = ACTIONS[currentActionIndex];
      act.paramVal = act.paramMin; // Reset to default minimum
      Serial.printf("\n>>> [KNOB 2 CLICK] Reset %s Parameter to %d %s <<<\n", 
                    act.name, act.paramVal, act.paramUnit);
      renderActionMenu();
    }
    delay(200);
  }
  lastK2Sw = k2Sw;

  // --------------------------------------------------------------------------
  // --- MASTER START BUTTON (TAP = RUN | 3s HOLD = PAIR) ---
  // --------------------------------------------------------------------------
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
// 7. BUILD & TRANSMIT PARAMETERIZED ROBOSEN PACKET
// ==============================================================================
bool sendRobosenPacket(const RobosenAction& action) {
  if (pairedMAC == "None (Unpaired)") {
    Serial.println("\n[ERROR] No robot paired! Hold Start for 3s to pair.");
    setStatusLED(40, 0, 0);
    delay(500);
    return false;
  }

  setStatusLED(40, 30, 0); // 🟡 Active Transmitting

  Serial.println("\n╔════════════════════════════════════════════════════════════════╗");
  Serial.printf("║  [TRANSMITTING] Connecting to: %-32s║\n", pairedName.c_str());
  Serial.printf("║  Target MAC:                   %-32s║\n", pairedMAC.c_str());
  Serial.printf("║  Action:                       %-32s║\n", action.name);
  Serial.printf("║  Configured Parameter:         %d %-28s║\n", action.paramVal, action.paramUnit);
  Serial.println("╚════════════════════════════════════════════════════════════════╝");

  // Construct Binary Packet: [0xFF, 0xFF, NumBytes, Opcode, Payload..., Checksum]
  uint8_t payloadLen = strlen(action.payload);
  uint8_t numBytes = 1 + payloadLen + 1;
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
  BLEAddress pAddressRandom(pairedMAC.c_str(), BLE_ADDR_RANDOM);
  BLEAddress pAddressPublic(pairedMAC.c_str(), BLE_ADDR_PUBLIC);

  bool connected = pClient->connect(pAddressRandom);
  if (!connected) {
    connected = pClient->connect(pAddressPublic);
  }

  if (!connected) {
    Serial.println("[BLE] Connection failed. Make sure device is awake & connectable.");
    setStatusLED(40, 0, 0);
    delay(400);
    setStatusLED(0, 30, 0);
    delete pClient;
    return false;
  }

  Serial.println("[BLE] Connected! Discovering services...");
  BLERemoteService* pRemoteService = pClient->getService(SERVICE_UUID);
  if (pRemoteService == nullptr) {
    Serial.println("[BLE] Target connected successfully! (Service 0xFFE0 not active on target).");
    setStatusLED(0, 30, 0);
    pClient->disconnect();
    delete pClient;
    return true;
  }

  BLERemoteCharacteristic* pRemoteChar = pRemoteService->getCharacteristic(CHAR_UUID);
  if (pRemoteChar != nullptr && pRemoteChar->canWrite()) {
    // Send action with repetitions if configured > 1
    for (int rep = 0; rep < action.paramVal; rep++) {
      if (rep > 0) {
        Serial.printf("[REPEAT] Transmitting Repetition %d of %d...\n", rep + 1, action.paramVal);
        delay(1200); // Inter-command interval
      }
      pRemoteChar->writeValue(packet, totalPacketLen);
    }
    Serial.println(">>> [SUCCESS] All motion commands delivered to robot! <<<");
  }

  setStatusLED(0, 40, 0);
  pClient->disconnect();
  delete pClient;
  return true;
}

// ==============================================================================
// 8. BLE SCANNING ROUTINE
// ==============================================================================
void runBleScan() {
  currentState = STATE_BLE_SCANNING;
  setStatusLED(0, 0, 40); // 🔵 Active Scanning

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

  // Sort by RSSI
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
  setStatusLED(0, 0, 30);
  renderPairingMenu();
}

// ==============================================================================
// 9. DUAL-KNOB UI RENDERING
// ==============================================================================
void renderActionMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║              ROBOSEN K1 PHYSICAL BLOCK MASTER (DUAL-KNOB)              ║");
  Serial.printf("║ Paired Target: %-55s ║\n", (pairedName + " (" + pairedMAC + ")").c_str());
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║   [KNOB 1: ACTION SELECT]             [KNOB 2: PARAMETER ADJUST]       ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  
  for (int i = 0; i < TOTAL_ACTIONS; i++) {
    char line[100];
    if (i == currentActionIndex) {
      snprintf(line, sizeof(line), "║ ► [%-19s] ◄       Parameter: [ %3d %-6s ] (ACTIVE) ║", 
               ACTIONS[i].name, ACTIONS[i].paramVal, ACTIONS[i].paramUnit);
    } else {
      snprintf(line, sizeof(line), "║   %-23s             Parameter:   %3d %-6s          ║", 
               ACTIONS[i].name, ACTIONS[i].paramVal, ACTIONS[i].paramUnit);
    }
    Serial.println(line);
  }
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Knob 1: Select Action        • Knob 2: Adjust Parameter Value        ║");
  Serial.println("║ • Start Click: Execute Motion  • Hold Start: BLE Teacher Pairing (3s)  ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
}

void renderPairingMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                     TEACHER BLE PAIRING DISCOVERY                      ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  if (bleDeviceCount == 0) {
    Serial.println("║  No BLE devices discovered. Press Start button to exit.                ║");
  } else {
    for (int i = 0; i < bleDeviceCount; i++) {
      char row[80];
      if (i == currentBleIndex) {
        snprintf(row, sizeof(row), "║ ► [%d] %-18s (%3d dBm) %-17s ◄        ║", 
                 i + 1, bleList[i].name.substring(0, 18).c_str(), bleList[i].rssi, bleList[i].address.c_str());
      } else {
        snprintf(row, sizeof(row), "║   [%d] %-18s (%3d dBm) %-17s          ║", 
                 i + 1, bleList[i].name.substring(0, 18).c_str(), bleList[i].rssi, bleList[i].address.c_str());
      }
      Serial.println(row);
    }
  }
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Turn Knob: Scroll List       • Click Knob: Save to NVS Flash         ║");
  Serial.println("║ • Start Click: Cancel & Exit                                           ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
}
