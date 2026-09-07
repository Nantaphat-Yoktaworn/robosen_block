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

// --- CONFIG DOCK (UART) ---
const int PIN_CFG_TX    = 17;  // 🔘 Gray Wire (Master TX -> Action Block RX / PD6)
const int PIN_CFG_RX    = 18;  // 🟣 Purple Wire (Master RX <- Action Block TX / PD5)

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
  uint8_t tokenID; // Stored Action Block Token for CH32V003
};

RobosenAction ACTIONS[] = {
  {"01: Walk Forward",   0x01, "",                      "Steps", 1,   1,   5,   1,  0x01},
  {"02: Walk Backward",  0x05, "",                      "Steps", 1,   1,   5,   1,  0x02},
  {"03: Turn Left",      0x08, "",                      "Deg°",  90,  45,  180, 45, 0x03},
  {"04: Turn Right",     0x02, "",                      "Deg°",  90,  45,  180, 45, 0x04},
  {"05: Punch Left",     0x17, "ProAction/Left Punch",  "Reps",  1,   1,   3,   1,  0x10},
  {"06: Push-ups",       0x17, "ProAction/Push Ups",    "Reps",  1,   1,   3,   1,  0x14},
  {"07: Wave Hand",      0x17, "ProAction/Say Hello",   "Reps",  1,   1,   3,   1,  0x18}
};
const int TOTAL_ACTIONS = sizeof(ACTIONS) / sizeof(ACTIONS[0]);
int currentActionIndex = 0; // Default: Walk Forward

// ==============================================================================
// 3.1 CONFIG DOCK PROTOCOL & DOCKED BLOCK STATE (0xCF)
// ==============================================================================
bool isBlockDocked = false;
uint8_t dockedActionId = 0;
uint8_t dockedParamVal = 0;
unsigned long lastConfigPollTime = 0;
unsigned long lastDockResponseTime = 0;
const unsigned long CONFIG_POLL_INTERVAL_MS = 350;

uint8_t calcCrc8(const uint8_t *data, size_t len) {
  uint8_t crc = 0x00;
  for (size_t i = 0; i < len; i++) {
    crc ^= data[i];
    for (int j = 0; j < 8; j++) {
      if (crc & 0x80) {
        crc = ((crc << 1) ^ 0x07) & 0xFF;
      } else {
        crc = (crc << 1) & 0xFF;
      }
    }
  }
  return crc;
}

const char* getActionNameByToken(uint8_t token) {
  switch (token) {
    case 0x01: return "Walk Forward";
    case 0x02: return "Walk Backward";
    case 0x03: return "Turn Left";
    case 0x04: return "Turn Right";
    case 0x07: return "Side-step Left";
    case 0x08: return "Side-step Right";
    case 0x10: return "Left Punch";
    case 0x11: return "Right Punch";
    case 0x12: return "Kung Fu";
    case 0x13: return "Dance";
    case 0x14: return "Push-ups";
    case 0x15: return "Handstand";
    case 0x16: return "Single Kick";
    case 0x17: return "Squats";
    case 0x18: return "Wave Hand";
    case 0x19: return "Celebrate";
    default:   return "Unknown Action";
  }
}

const char* getParamUnitByToken(uint8_t token) {
  switch (token) {
    case 0x01:
    case 0x02:
    case 0x07:
    case 0x08: return "Steps";
    case 0x03:
    case 0x04: return "Deg°";
    default:   return "Reps";
  }
}

void writeConfigToDockedBlock(uint8_t actionToken, uint8_t param) {
  uint8_t payload[3] = { 0x02, actionToken, param };
  uint8_t crc = calcCrc8(payload, 3);
  uint8_t packet[6] = { 0xCF, 0x02, actionToken, param, crc, 0x55 };
  Serial1.write(packet, 6);
  Serial.printf("\n[CONFIG DOCK] ⚡ Flashing Action 0x%02X (%s, %d %s) to docked block...\n", 
                actionToken, getActionNameByToken(actionToken), param, getParamUnitByToken(actionToken));
}

// ==============================================================================
// 4. SYSTEM STATE & PERSISTENT BLE CONNECTION HANDLES
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

// Persistent BLE Connection Instances & Flags
BLEClient* pClient = nullptr;
BLERemoteCharacteristic* pRemoteChar = nullptr;
volatile bool isConnected = false;

// Retry Timing: 1s fast scan + 2s pause between attempts
const unsigned long RETRY_INTERVAL_MS = 2000;
unsigned long lastConnectAttemptTime = 0;
int connectAttemptCounter = 0;

// Debounce, Activity & Timing States
int lastK1Clk = HIGH;
int lastK2Clk = HIGH;
unsigned long startBtnPressTime = 0;
bool startBtnHeld = false;
unsigned long lastUserActivity = 0;
unsigned long lastHeartbeatTime = 0;

// Forward Declarations
void renderActionMenu();
void renderPairingMenu();
void runBleScan();
bool connectToRobot();
bool sendRobosenPacket(const RobosenAction& action);
void updateStatusLED();
void pollConfigDock();

// BLE Client Callbacks for Connection Life-Cycle Management
class RobosenClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
    isConnected = true;
    Serial.println("\n[BLE STATUS] 🟢 Physical connection established with robot!");
  }

  void onDisconnect(BLEClient* pclient) {
    isConnected = false;
    pRemoteChar = nullptr;
    Serial.println("\n[BLE STATUS] 🔴 Robot disconnected / link lost! Resuming retry loop...");
    if (currentState == STATE_ACTION_MENU) {
      updateStatusLED();
    }
  }
};

void updateStatusLED() {
  if (currentState == STATE_BLE_SCANNING) {
    setStatusLED(0, 0, 40);  // 🔵 Vivid Blue: Active Scanning
  } else if (currentState == STATE_BLE_PAIRING_MENU) {
    setStatusLED(0, 0, 30);  // 🔵 Soft Blue: Pairing Menu Selection
  } else if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    setStatusLED(30, 0, 0);  // 🔴 Red: Unpaired
  } else if (!isConnected) {
    setStatusLED(30, 15, 0); // 🟠 Amber/Orange: Paired, waiting / reconnecting
  } else {
    setStatusLED(0, 30, 0);  // 🟢 Emerald Green: Connected & Ready
  }
}

// ==============================================================================
// 5. DIRECT PERSISTENT BLE CONNECTION MANAGER (FAST 1s NON-BLOCKING SCAN CHECK)
// ==============================================================================
bool connectToRobot() {
  if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    Serial.println("[BLE STATUS] ⚠️ No robot paired in NVS flash. Hold Start for 3s to pair.");
    updateStatusLED();
    return false;
  }

  // If already connected with valid characteristic handle, do nothing
  if (isConnected && pClient != nullptr && pClient->isConnected() && pRemoteChar != nullptr) {
    return true;
  }

  setStatusLED(40, 30, 0); // 🟡 Yellow: Scanning / Connecting

  if (pClient != nullptr && pClient->isConnected()) {
    pClient->disconnect();
    delay(50);
  }

  // --------------------------------------------------------------------------
  // STEP 1: Fast 1-Second BLE Scan to verify robot is powered on and advertising.
  // (This eliminates the 60-second blocking timeout when the robot is OFF!)
  // --------------------------------------------------------------------------
  BLEScan* pScan = BLEDevice::getScan();
  pScan->setActiveScan(true);
  pScan->setInterval(50);
  pScan->setWindow(40);

  BLEScanResults* results = pScan->start(1, false); // Exactly 1.0 second scan
  BLEAdvertisedDevice targetDevice;
  bool found = false;

  int count = results->getCount();
  for (int i = 0; i < count; i++) {
    BLEAdvertisedDevice d = results->getDevice(i);
    String dAddr = d.getAddress().toString().c_str();
    if (dAddr.equalsIgnoreCase(pairedMAC)) {
      targetDevice = d;
      found = true;
      break;
    }
  }
  pScan->clearResults();

  if (!found) {
    // Robot is OFF or not advertising — return immediately in 1s without hanging!
    isConnected = false;
    pRemoteChar = nullptr;
    updateStatusLED();
    return false;
  }

  // --------------------------------------------------------------------------
  // STEP 2: Robot detected online! Establish immediate direct connection (<200ms)
  // --------------------------------------------------------------------------
  Serial.println("[BLE STATUS] 🎯 Robot advertising detected! Establishing link...");

  if (pClient == nullptr) {
    pClient = BLEDevice::createClient();
    pClient->setClientCallbacks(new RobosenClientCallback());
  }

  bool ok = pClient->connect(&targetDevice);
  if (!ok) {
    BLEAddress addr(targetDevice.getAddress());
    ok = pClient->connect(addr);
  }

  if (!ok) {
    Serial.println("[BLE STATUS] ❌ Link handshake failed.");
    isConnected = false;
    pRemoteChar = nullptr;
    updateStatusLED();
    return false;
  }

  Serial.println("[BLE STATUS] 🔗 Link established! Discovering GATT Service (0xFFE0)...");
  BLERemoteService* pRemoteService = pClient->getService(SERVICE_UUID);
  if (pRemoteService == nullptr) {
    Serial.println("[BLE STATUS] ⚠️ Service 0xFFE0 not found (Phone mock / simulation device).");
    isConnected = true;
    updateStatusLED();
    return true;
  }

  pRemoteChar = pRemoteService->getCharacteristic(CHAR_UUID);
  if (pRemoteChar == nullptr) {
    Serial.println("[BLE STATUS] ❌ Characteristic 0xFFE1 not found.");
    pClient->disconnect();
    isConnected = false;
    updateStatusLED();
    return false;
  }

  isConnected = true;
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.printf("║  [BLE STATUS: CONNECTED] Target: %-38s║\n", pairedName.c_str());
  Serial.println("║  Persistent link ACTIVE! Ready for instant commands.                   ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
  updateStatusLED();
  return true;
}

// ==============================================================================
// 5.1 CONFIG DOCK UART MONITOR & POLLING ENGINE
// ==============================================================================
void pollConfigDock() {
  unsigned long now = millis();

  // 1. Process incoming UART response bytes from Config Dock
  while (Serial1.available() > 0) {
    uint8_t b = Serial1.peek();
    if (b != 0xCF) {
      Serial1.read(); // Discard noise / unaligned byte
      Serial.printf("[DOCK RAW: 0x%02X] ", b);
      continue;
    }

    if (Serial1.available() < 2) break; // Wait for header + cmd

    uint8_t peekBuf[2];
    Serial1.readBytes(peekBuf, 2); // Read [0xCF, cmd]
    uint8_t cmd = peekBuf[1];

    if (cmd == 0x81) {
      // Query Response: [0xCF, 0x81, ActionID, ParamVal, CRC8, 0x55]
      // Wait up to 60ms for remaining 4 bytes: [act, par, rxCrc, footer]
      unsigned long t0 = millis();
      while (Serial1.available() < 4 && (millis() - t0 < 60)) {
        delay(1);
      }
      if (Serial1.available() >= 4) {
        uint8_t act = Serial1.read();
        uint8_t par = Serial1.read();
        uint8_t rxCrc = Serial1.read();
        uint8_t footer = Serial1.read();

        uint8_t checkPayload[3] = { 0x81, act, par };
        uint8_t calcCrc = calcCrc8(checkPayload, 3);
        if (calcCrc == rxCrc && footer == 0x55) {
          bool stateChanged = (!isBlockDocked || dockedActionId != act || dockedParamVal != par);
          isBlockDocked = true;
          dockedActionId = act;
          dockedParamVal = par;
          lastDockResponseTime = now;

          if (stateChanged && currentState == STATE_ACTION_MENU && (now - lastUserActivity > 250)) {
            Serial.printf("\n[CONFIG DOCK] 🟢 Action Block detected: Token 0x%02X (%s, %d %s)\n",
                          dockedActionId, getActionNameByToken(dockedActionId),
                          dockedParamVal, getParamUnitByToken(dockedActionId));
            renderActionMenu();
          }
        } else {
          Serial.printf("\n[DOCK CRC ERROR] Act=0x%02X Par=%d CRC=0x%02X (calc=0x%02X) Footer=0x%02X\n",
                        act, par, rxCrc, calcCrc, footer);
        }
      }
    } else if (cmd == 0x06) {
      // ACK Response: [0xCF, 0x06, CRC8, 0x55]
      // Wait up to 60ms for remaining 2 bytes: [rxCrc, footer]
      unsigned long t0 = millis();
      while (Serial1.available() < 2 && (millis() - t0 < 60)) {
        delay(1);
      }
      if (Serial1.available() >= 2) {
        uint8_t rxCrc = Serial1.read();
        uint8_t footer = Serial1.read();
        uint8_t ackPayload[1] = { 0x06 };
        if (calcCrc8(ackPayload, 1) == rxCrc && footer == 0x55) {
          Serial.println("\n[CONFIG DOCK] 💾 Flash Write Confirmed! (ACK 0x06 received from Block)");
          // Query again immediately to refresh docked block display
          uint8_t queryPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
          Serial1.write(queryPkt, 4);
          Serial1.flush();
        }
      }
    }
  }

  // 2. Timeout check: if no query response received for 1200ms, mark block as undocked
  if (isBlockDocked && (now - lastDockResponseTime > 1200)) {
    isBlockDocked = false;
    dockedActionId = 0;
    dockedParamVal = 0;
    Serial.println("\n[CONFIG DOCK] ⚪ Action Block undocked / disconnected.");
    if (currentState == STATE_ACTION_MENU && (now - lastUserActivity > 250)) {
      renderActionMenu();
    }
  }

  // 3. Periodic query ping (only in ACTION_MENU state)
  if (currentState == STATE_ACTION_MENU) {
    if (now - lastConfigPollTime >= CONFIG_POLL_INTERVAL_MS) {
      lastConfigPollTime = now;
      uint8_t queryPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
      Serial1.write(queryPkt, 4);
      Serial1.flush();
    }
  }
}

// ==============================================================================
// 6. HARDWARE SETUP
// ==============================================================================
void setup() {
  Serial.begin(115200);
  delay(1500);

  // Initialize Config Dock UART (Serial1 on Pins 18 RX, 17 TX @ 115200)
  pinMode(PIN_CFG_RX, INPUT_PULLUP);
  Serial1.begin(115200, SERIAL_8N1, PIN_CFG_RX, PIN_CFG_TX);

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
  pairedMAC = preferences.getString("paired_mac", "");
  if (pairedMAC == "" || pairedMAC == "None (Unpaired)") {
    pairedMAC = preferences.getString("last_paired_mac", "None (Unpaired)");
  }
  pairedName = preferences.getString("paired_name", "Robosen Robot");

  // Initialize BLE Stack
  BLEDevice::init("Robosen_Master_Block");
  pClient = BLEDevice::createClient();
  pClient->setClientCallbacks(new RobosenClientCallback());

  updateStatusLED();

  Serial.println("\n[SYSTEM] ESP32-S3 Dual-Knob Master Initialized.");

  // Fast auto-connect check on boot (takes only 1s if robot is off!)
  if (pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
    connectAttemptCounter = 1;
    Serial.printf("\n[BLE STATUS] 🔌 Saved Robot Target: %s (%s)\n", pairedName.c_str(), pairedMAC.c_str());
    Serial.printf("[BLE STATUS] ⏳ [Attempt #%d] Auto-connecting on boot (1s check)...\n", connectAttemptCounter);
    if (connectToRobot()) {
      connectAttemptCounter = 0;
    } else {
      Serial.printf("[BLE STATUS] ❌ Attempt #%d: Robot is OFF or not advertising.\n", connectAttemptCounter);
      Serial.println("[BLE STATUS] 🔄 Will retry every 2 seconds. Hold Start 3s to switch robot.\n");
    }
  } else {
    Serial.println("[BLE STATUS] ⚠️ No paired robot configured in flash. Hold Start for 3s to pair.");
  }

  renderActionMenu();
  lastUserActivity = millis();
  lastConnectAttemptTime = millis();
}

// ==============================================================================
// 7. MAIN EVENT LOOP
// ==============================================================================
void loop() {
  unsigned long now = millis();

  // --------------------------------------------------------------------------
  // --- 0. CONFIG DOCK MONITORING & ACTION QUERY ENGINE ---
  // --------------------------------------------------------------------------
  pollConfigDock();

  // Serial Monitor Interactive Test ('t' = Ping Config Dock)
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 't' || c == 'T') {
      Serial.println("\n[DOCK TEST] 📡 Manual Ping [0xCF, 0x01, 0x07, 0x55] sent to GPIO 17...");
      uint8_t qPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
      Serial1.write(qPkt, 4);
      Serial1.flush();
      delay(30);
      Serial.printf("[DOCK TEST] Serial1 buffer has %d bytes waiting on GPIO 18\n", Serial1.available());
    }
  }

  // --------------------------------------------------------------------------
  // --- 1. MASTER START BUTTON (CHECKED FIRST: INSTANT 3s HOLD DETECTION) ---
  // --------------------------------------------------------------------------
  int btnState = digitalRead(PIN_START_BTN);
  if (btnState == LOW) {
    lastUserActivity = now;
    if (startBtnPressTime == 0) {
      startBtnPressTime = millis();
      startBtnHeld = false;
      Serial.println("\n[BUTTON] Start button pressed... (Hold 3s to switch robot)");
    } else if (!startBtnHeld) {
      unsigned long heldDuration = millis() - startBtnPressTime;

      // Print live hold countdown every 700ms so user has real-time feedback
      static unsigned long lastHoldPrint = 0;
      if (millis() - lastHoldPrint >= 700) {
        lastHoldPrint = millis();
        Serial.printf("[BUTTON] Holding: %lu / 3000 ms...\n", heldDuration);
      }

      if (heldDuration >= 3000) {
        startBtnHeld = true;
        Serial.println("\n[SYSTEM] 🎯 3-Second Hold Confirmed! Opening Teacher Pairing Menu...");
        runBleScan();
        startBtnPressTime = 0;
        return; // Return immediately to avoid processing other logic
      }
    }
    // While button is held, return early to prevent BLE retry from interrupting!
    delay(10);
    return;
  } else {
    // Button was released
    if (startBtnPressTime > 0) {
      lastUserActivity = now;
      unsigned long duration = millis() - startBtnPressTime;
      startBtnPressTime = 0;

      if (duration < 3000 && !startBtnHeld) {
        if (currentState == STATE_ACTION_MENU) {
          sendRobosenPacket(ACTIONS[currentActionIndex]);
        } else if (currentState == STATE_BLE_PAIRING_MENU) {
          currentState = STATE_ACTION_MENU;
          renderActionMenu();
          if (pairedMAC != "None (Unpaired)" && !isConnected) {
            connectToRobot();
          } else {
            updateStatusLED();
          }
        }
      }
      startBtnHeld = false;
    }
  }

  // --------------------------------------------------------------------------
  // --- 2. CONTINUOUS AUTO-RECONNECT & BACKGROUND HEARTBEAT ---
  // --------------------------------------------------------------------------
  if (currentState == STATE_ACTION_MENU) {
    if (isConnected && pRemoteChar != nullptr && pClient != nullptr && pClient->isConnected()) {
      connectAttemptCounter = 0;
      // Send handshake ping (0x0B) every 5 seconds when idle to keep Robosen awake
      if (now - lastHeartbeatTime >= 5000) {
        lastHeartbeatTime = now;
        uint8_t pingPacket[] = {0xFF, 0xFF, 0x02, 0x0B, 0x0D};
        if (pRemoteChar->canWrite()) {
          pRemoteChar->writeValue(pingPacket, sizeof(pingPacket));
        }
      }
    } else {
      // Disconnected: CONTINUOUSLY retry with 1s scan + 2s pause
      if (pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
        // Only retry if user is not actively tweaking knobs in the last 1.5s
        if (now - lastUserActivity > 1500) {
          if (now - lastConnectAttemptTime >= RETRY_INTERVAL_MS) {
            connectAttemptCounter++;
            Serial.printf("[BLE STATUS] ⏳ [Attempt #%d] Checking for %s (%s)... (1s scan)\n", 
                          connectAttemptCounter, pairedName.c_str(), pairedMAC.c_str());

            bool success = connectToRobot();

            // Set timestamp AFTER scan finishes so there is ALWAYS a full 2000ms pause!
            lastConnectAttemptTime = millis();

            if (success) {
              connectAttemptCounter = 0;
              Serial.println("[BLE STATUS] ✅ Successfully connected to robot!");
              renderActionMenu();
            } else {
              Serial.printf("[BLE STATUS] ❌ Attempt #%d: Robot not detected. Pausing 2s... (Hold Start 3s to switch)\n",
                            connectAttemptCounter);
            }
          }
        }
      }
    }
  }

  // --------------------------------------------------------------------------
  // --- 3. KNOB 1: ACTION SELECTOR (CLK: 8, DT: 9, SW: 10) ---
  // --------------------------------------------------------------------------
  int k1Clk = digitalRead(PIN_K1_CLK);
  if (k1Clk != lastK1Clk && k1Clk == LOW) {
    lastUserActivity = now;
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
    lastUserActivity = now;
    if (currentState == STATE_ACTION_MENU) {
      if (isBlockDocked) {
        // Write the currently selected action & parameter to the docked Action Block!
        RobosenAction& act = ACTIONS[currentActionIndex];
        Serial.printf("\n>>> [CONFIG DOCK] Flashing '%s' (%d %s) into docked Action Block... <<<\n",
                      act.name, act.paramVal, act.paramUnit);
        writeConfigToDockedBlock(act.tokenID, (uint8_t)act.paramVal);
        setStatusLED(0, 80, 40); // Emerald Green Flash
        delay(100);
        updateStatusLED();
      } else {
        Serial.printf("\n>>> [KNOB 1 CLICK] Selected Action: %s <<<\n", ACTIONS[currentActionIndex].name);
        if (!isConnected && pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
          Serial.println("[BLE STATUS] ⚡ Knob clicked while disconnected: Immediate connection attempt...");
          if (connectToRobot()) {
            connectAttemptCounter = 0;
            renderActionMenu();
          }
          lastConnectAttemptTime = millis();
        } else {
          setStatusLED(0, 60, 30);
          delay(80);
          updateStatusLED();
        }
      }
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      // Save BLE Device & Switch Target
      pairedMAC  = bleList[currentBleIndex].address;
      pairedName = bleList[currentBleIndex].name;
      preferences.putString("paired_mac", pairedMAC);
      preferences.putString("paired_name", pairedName);

      Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
      Serial.printf("║  [BLE STATUS] Selected Robot: %-41s║\n", pairedName.c_str());
      Serial.printf("║  Target MAC:                  %-41s║\n", pairedMAC.c_str());
      Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

      currentState = STATE_ACTION_MENU;
      connectAttemptCounter = 0;
      renderActionMenu();
      Serial.println("[BLE STATUS] ⏳ Connecting to newly selected robot...");
      connectToRobot();
      lastConnectAttemptTime = millis();
    }
    delay(200);
  }
  lastK1Sw = k1Sw;

  // --------------------------------------------------------------------------
  // --- 4. KNOB 2: PARAMETER ADJUSTER (CLK: 11, DT: 12, SW: 13) ---
  // --------------------------------------------------------------------------
  int k2Clk = digitalRead(PIN_K2_CLK);
  if (k2Clk != lastK2Clk && k2Clk == LOW) {
    lastUserActivity = now;
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

  // Knob 2 Click (Reset Parameter in Action Menu | Confirm & Save in Pairing Menu)
  static bool lastK2Sw = HIGH;
  bool k2Sw = digitalRead(PIN_K2_SW);
  if (lastK2Sw == HIGH && k2Sw == LOW) {
    lastUserActivity = now;
    if (currentState == STATE_ACTION_MENU) {
      RobosenAction& act = ACTIONS[currentActionIndex];
      act.paramVal = act.paramMin; // Reset to default minimum
      Serial.printf("\n>>> [KNOB 2 CLICK] Reset %s Parameter to %d %s <<<\n", 
                    act.name, act.paramVal, act.paramUnit);
      renderActionMenu();
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      // Save BLE Device into NVS Flash & Switch Target
      pairedMAC  = bleList[currentBleIndex].address;
      pairedName = bleList[currentBleIndex].name;
      preferences.putString("paired_mac", pairedMAC);
      preferences.putString("paired_name", pairedName);

      Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
      Serial.printf("║  [BLE STATUS] Selected Robot: %-41s║\n", pairedName.c_str());
      Serial.printf("║  Target MAC:                  %-41s║\n", pairedMAC.c_str());
      Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

      setStatusLED(0, 50, 0); // 🟢 Confirmed Green
      currentState = STATE_ACTION_MENU;
      connectAttemptCounter = 0;
      delay(200);
      renderActionMenu();
      Serial.println("[BLE STATUS] ⏳ Connecting to newly selected robot...");
      connectToRobot();
      lastConnectAttemptTime = millis();
    }
    delay(200);
  }
  lastK2Sw = k2Sw;
}

// ==============================================================================
// 8. BUILD & TRANSMIT PARAMETERIZED ROBOSEN PACKET (PERSISTENT CONNECTION)
// ==============================================================================
bool sendRobosenPacket(const RobosenAction& action) {
  if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    Serial.println("\n[BLE STATUS] ⚠️ No robot paired! Hold Start for 3s to pair.");
    setStatusLED(40, 0, 0);
    delay(500);
    updateStatusLED();
    return false;
  }

  // Re-establish link if connection was lost
  if (!isConnected || pClient == nullptr || !pClient->isConnected() || pRemoteChar == nullptr) {
    Serial.println("\n[BLE STATUS] ⚡ Connection inactive. Quick scan to connect before dispatch...");
    if (!connectToRobot()) {
      Serial.println("[BLE STATUS] ❌ Failed to connect to robot. Make sure robot is powered ON.");
      return false;
    }
  }

  setStatusLED(40, 30, 0); // 🟡 Active Transmitting

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.printf("║  [TRANSMITTING] Target:        %-40s║\n", pairedName.c_str());
  Serial.printf("║  Target MAC:                   %-40s║\n", pairedMAC.c_str());
  Serial.printf("║  Action:                       %-40s║\n", action.name);
  Serial.printf("║  Configured Parameter:         %d %-36s║\n", action.paramVal, action.paramUnit);
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

  // Construct Primary Action Packet: [0xFF, 0xFF, NumBytes, Opcode, Payload..., Checksum]
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

  // Construct Standard Stop Packet: [0xFF, 0xFF, 0x02, 0x0C, 0x0E]
  uint8_t stopPacket[] = {0xFF, 0xFF, 0x02, 0x0C, 0x0E};

  bool isTurn = (action.opcode == 0x08 || action.opcode == 0x02);
  bool isWalk = (action.opcode == 0x01 || action.opcode == 0x05);
  bool isPredefined = (action.opcode == 0x17);

  if (pRemoteChar != nullptr && pRemoteChar->canWrite()) {
    if (isTurn) {
      // Turn Left (0x08) vs Turn Right (0x02): paramVal is Angle in Degrees (45°, 90°, 135°, 180°)
      // Turn Left turns at ~1600ms per 90 degrees.
      // Turn Right on K1 hardware has a slower angular rate, requiring ~3200ms per 90 degrees (2x duration).
      unsigned long turnDurationMs = (action.opcode == 0x08) 
                                      ? ((action.paramVal * 1600UL) / 90) 
                                      : ((action.paramVal * 3200UL) / 90);

      Serial.printf("  ► Turn Command: [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Direction: %s, Target: %d Deg°, Duration: %lu ms)\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal, turnDurationMs);

      // Start continuous turn
      pRemoteChar->writeValue(packet, totalPacketLen);
      delay(turnDurationMs);

      // IMMEDIATELY Send Locomotion Stop (0x0C) to lock robot at desired angle!
      Serial.print("  ► Locomotion Stop: [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      pRemoteChar->writeValue(stopPacket, sizeof(stopPacket));
      Serial.printf(">>> [SUCCESS] Turned %s %d Deg° and locked position! <<<\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal);

    } else if (isWalk) {
      // Walk Forward (0x01) or Walk Backward (0x05): paramVal is Steps (1 to 5)
      // ~1400ms per walking stride
      unsigned long walkDurationMs = action.paramVal * 1400UL;
      Serial.printf("  ► Walk Command: [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Target: %d Steps, Duration: %lu ms)\n", action.paramVal, walkDurationMs);

      // Start continuous walk
      pRemoteChar->writeValue(packet, totalPacketLen);
      delay(walkDurationMs);

      // Send Locomotion Stop (0x0C) to end walking
      Serial.print("  ► Locomotion Stop: [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      pRemoteChar->writeValue(stopPacket, sizeof(stopPacket));
      Serial.printf(">>> [SUCCESS] Walked %d Steps and locked position! <<<\n", action.paramVal);

    } else if (isPredefined) {
      // Predefined Action (0x17): paramVal is Repetitions (1 to 3)
      unsigned long animDurationMs = 4000;
      if (strstr(action.payload, "Push Ups") != nullptr)       animDurationMs = 12000;
      else if (strstr(action.payload, "Say Hello") != nullptr) animDurationMs = 8000;
      else if (strstr(action.payload, "Left Punch") != nullptr) animDurationMs = 4000;

      for (int rep = 0; rep < action.paramVal; rep++) {
        Serial.printf("  ► Rep %d of %d: [HEX] ", rep + 1, action.paramVal);
        for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
        Serial.printf("(Duration: %lu ms)\n", animDurationMs);

        pRemoteChar->writeValue(packet, totalPacketLen);
        delay(animDurationMs);
      }
      Serial.println(">>> [SUCCESS] All action repetitions completed! <<<");

    } else {
      pRemoteChar->writeValue(packet, totalPacketLen);
      delay(1000);
    }
  } else {
    // Simulated output for phone mock / debug
    if (isTurn) {
      unsigned long turnDurationMs = (action.opcode == 0x08) 
                                      ? ((action.paramVal * 1600UL) / 90) 
                                      : ((action.paramVal * 3200UL) / 90);
      Serial.printf("  ► Turn Command (Simulated): [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Direction: %s, Target: %d Deg°, Duration: %lu ms)\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal, turnDurationMs);
      delay(turnDurationMs);
      Serial.print("  ► Locomotion Stop (Simulated): [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      Serial.printf(">>> [SUCCESS] Simulated %s %d Deg° Turn! <<<\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal);
    } else if (isWalk) {
      unsigned long walkDurationMs = action.paramVal * 1400UL;
      Serial.printf("  ► Walk Command (Simulated): [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Target: %d Steps, Duration: %lu ms)\n", action.paramVal, walkDurationMs);
      delay(walkDurationMs);
      Serial.print("  ► Locomotion Stop (Simulated): [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      Serial.printf(">>> [SUCCESS] Simulated %d Steps Walk! <<<\n", action.paramVal);
    } else {
      for (int rep = 0; rep < action.paramVal; rep++) {
        Serial.printf("  ► Step/Rep %d of %d (Simulated): [HEX] ", rep + 1, action.paramVal);
        for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
        Serial.println();
        if (rep < action.paramVal - 1) delay(800);
      }
      Serial.println(">>> [SUCCESS] All motion commands simulated! <<<");
    }
  }

  // Refresh timers so keepalive heartbeat doesn't collide
  lastHeartbeatTime = millis();
  lastUserActivity  = millis();

  // KEEP CONNECTION ALIVE! NO DISCONNECT OR DELETE CLIENT!
  updateStatusLED(); // 🟢 Emerald Green: Persistent Link Active
  Serial.println("[BLE STATUS] 🟢 Link remains ACTIVE & ready for subsequent commands.\n");
  return true;
}

// ==============================================================================
// 9. BLE SCANNING ROUTINE (TEACHER PAIRING / SWITCH ROBOT)
// ==============================================================================
void runBleScan() {
  // If actively connected, disconnect so the robot resumes advertising
  if (pClient != nullptr && pClient->isConnected()) {
    Serial.println("\n[BLE STATUS] Disconnecting from current robot before scan...");
    pClient->disconnect();
    isConnected = false;
    pRemoteChar = nullptr;
    delay(200);
  }

  currentState = STATE_BLE_SCANNING;
  updateStatusLED(); // 🔵 Active Scanning

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
    bleList[bleDeviceCount].name     = devName;
    bleList[bleDeviceCount].address  = device.getAddress().toString().c_str();
    bleList[bleDeviceCount].rssi     = device.getRSSI();
    bleDeviceCount++;
  }

  // Sort by RSSI (strongest signal first)
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
  updateStatusLED();
  renderPairingMenu();
}

// ==============================================================================
// 10. DUAL-KNOB UI RENDERING
// ==============================================================================
void renderActionMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║              ROBOSEN K1 PHYSICAL BLOCK MASTER (DUAL-KNOB)              ║");
  String targetStr = pairedName + " (" + pairedMAC + ")";
  if (targetStr.length() > 34) targetStr = targetStr.substring(0, 31) + "...";

  char statusStr[24];
  if (isConnected) {
    snprintf(statusStr, sizeof(statusStr), "CONNECTED 🟢");
  } else if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    snprintf(statusStr, sizeof(statusStr), "UNPAIRED 🔴");
  } else if (connectAttemptCounter > 0) {
    snprintf(statusStr, sizeof(statusStr), "RETRY #%-3d ⏳", connectAttemptCounter);
  } else {
    snprintf(statusStr, sizeof(statusStr), "SEARCHING 🟠");
  }

  Serial.printf("║ Target: %-36s Status: %-17s ║\n", targetStr.c_str(), statusStr);
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  if (isBlockDocked) {
    char dockInfo[80];
    snprintf(dockInfo, sizeof(dockInfo), "DOCKED 🟢 [0x%02X] %s (%d %s)", 
             dockedActionId, getActionNameByToken(dockedActionId),
             dockedParamVal, getParamUnitByToken(dockedActionId));
    char dockLine[120];
    snprintf(dockLine, sizeof(dockLine), "║ Config Dock: %-54s ║", dockInfo);
    Serial.println(dockLine);
  } else {
    Serial.println("║ Config Dock: EMPTY ⚪ (No Action Block Connected)                      ║");
  }
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
  if (isBlockDocked) {
    Serial.println("║ • Knob 1: Select | Click: Burn Config • Knob 2: Adjust Parameter Value ║");
  } else {
    Serial.println("║ • Knob 1: Select Action (Click: Retry)• Knob 2: Adjust Parameter Value ║");
  }
  Serial.println("║ • Start Click: Execute Motion         • Hold Start: BLE Pairing (3s)   ║");
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
