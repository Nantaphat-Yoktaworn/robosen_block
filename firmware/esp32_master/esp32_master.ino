#include <Arduino.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEScan.h>
#include <BLEClient.h>
#include <BLEAdvertisedDevice.h>
#include <Preferences.h>
#include <SPI.h>
#include <GxEPD2_BW.h>
#include <Adafruit_GFX.h>
#include <Fonts/FreeSansBold9pt7b.h>

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

// --- CONFIG DOCK (UART1) ---
const int PIN_CFG_TX    = 17;  // 🔘 Gray Wire (Master TX -> Action Block RX / PD6)
const int PIN_CFG_RX    = 18;  // 🟣 Purple Wire (Master RX <- Action Block TX / PD5)

// --- RUN CHAIN BUS (UART2) ---
const int PIN_CHAIN_TX  = 15;  // Master Run Chain Output -> Block 1 RX (PD6)
const int PIN_CHAIN_RX  = 16;  // Master Return Rail Input <- Smart End Block TX (PD5)
HardwareSerial ChainSerial(2);

// --- 2.13" E-INK DISPLAY PINS (DEPG0213BN / SSD1680, 122x250, SPI) ---
const int PIN_EPD_BUSY  = 4;   // 🔘 Gray Wire (Active Status Flag)
const int PIN_EPD_RES   = 5;   // 🟤 Brown Wire (Hardware Reset)
const int PIN_EPD_DC    = 6;   // 🟣 Purple Wire (Data / Command)
const int PIN_EPD_CS    = 7;   // 🟡 Yellow Wire (Chip Select)
const int PIN_EPD_SCL   = 21;  // 🟢 Green Wire (SPI SCK / Clock)
const int PIN_EPD_SDA   = 38;  // ⚪ White Wire (SPI MOSI / DIN)

// Production verified driver for DEPG0213BN panel
GxEPD2_BW<GxEPD2_213_BN, GxEPD2_213_BN::HEIGHT> display(
  GxEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);

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
    case 0xEE: return "End Terminator";
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
    case 0xEE: return "Cap";
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
bool executeRunChain();
RobosenAction getActionObjByToken(uint8_t token, int param);

// E-Ink Display Functions (DEPG0213BN / SSD1680)
void updateEInkActionMenu();
void updateEInkPairingMenu();
void updateEInkScanning();
void updateEInkRunChain(int currentStep, int totalSteps, const char* actionName, int paramVal, const char* paramUnit);

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

  // Initialize Run Chain UART (ChainSerial on Pins 16 RX, 15 TX @ 115200)
  pinMode(PIN_CHAIN_RX, INPUT_PULLUP);
  ChainSerial.begin(115200, SERIAL_8N1, PIN_CHAIN_RX, PIN_CHAIN_TX);

  // Initialize 2.13" E-Ink Display (DEPG0213BN / SSD1680)
  Serial.println("[SYSTEM] Initializing 2.13\" E-Ink display (SPI SCL=21, SDA=38)...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));
  // initial = false eliminates disruptive boot flashing and 10s busy timeouts
  display.init(115200, false, 2, false);
  display.setRotation(1); // 250 width x 122 height (Landscape)

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

  // Serial Monitor Interactive Test ('t' = Ping Config Dock, 'r' = Run Chain)
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 't' || c == 'T') {
      Serial.println("\n[DOCK TEST] 📡 Manual Ping [0xCF, 0x01, 0x07, 0x55] sent to GPIO 17...");
      uint8_t qPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
      Serial1.write(qPkt, 4);
      Serial1.flush();
      delay(30);
      Serial.printf("[DOCK TEST] Serial1 buffer has %d bytes waiting on GPIO 18\n", Serial1.available());
    } else if (c == 'r' || c == 'R') {
      Serial.println("\n[RUN CHAIN TEST] 🚀 Manual trigger executeRunChain()...");
      if (!executeRunChain()) {
        Serial.println("[RUN CHAIN TEST] ⚠️ Run chain execution failed (No blocks / End block found).");
      }
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
          Serial.println("\n[SYSTEM] Start button pressed: Initiating Run Chain (GPIO 15/16)...");
          if (!executeRunChain()) {
            Serial.println("\n[SYSTEM] ⚠️ Chain execution aborted: No valid return packet received from return rail!");
            Serial.println("[SYSTEM] Ensure all blocks and the Smart End Block are connected magnetically.\n");
            // Flash red on onboard status LED to warn user of broken chain
            setStatusLED(50, 0, 0);
            delay(500);
            updateStatusLED();
          }
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
  bool isWalk = (action.opcode == 0x01 || action.opcode == 0x05 || action.opcode == 0x07 || action.opcode == 0x03);
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
      delay(1000); // Allow gait engine to stabilize feet into neutral stand posture
      Serial.printf(">>> [SUCCESS] Turned %s %d Deg° and locked position! <<<\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal);

    } else if (isWalk) {
      // Walk Forward (0x01), Walk Backward (0x05), Side-step Left (0x07), Side-step Right (0x03)
      // ~1400ms per walking/stepping stride
      unsigned long walkDurationMs = action.paramVal * 1400UL;
      Serial.printf("  ► Locomotion Command: [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Target: %d Steps, Duration: %lu ms)\n", action.paramVal, walkDurationMs);

      // Start continuous locomotion
      pRemoteChar->writeValue(packet, totalPacketLen);
      delay(walkDurationMs);

      // Send Locomotion Stop (0x0C) to end locomotion
      Serial.print("  ► Locomotion Stop: [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      pRemoteChar->writeValue(stopPacket, sizeof(stopPacket));
      delay(1200); // Allow gait engine to stabilize feet into neutral stand posture
      Serial.printf(">>> [SUCCESS] Locomotion completed (%d Steps) and locked position! <<<\n", action.paramVal);

    } else if (isPredefined) {
      // Predefined Action (0x17): paramVal is Repetitions (1 to 3)
      unsigned long animDurationMs = 4000;
      if (strstr(action.payload, "Push Ups") != nullptr)       animDurationMs = 12000;
      else if (strstr(action.payload, "Say Hello") != nullptr) animDurationMs = 8500;
      else if (strstr(action.payload, "Handstand") != nullptr) animDurationMs = 18000;
      else if (strstr(action.payload, "Kung Fu") != nullptr)   animDurationMs = 11000;
      else if (strstr(action.payload, "Boogaloo") != nullptr)  animDurationMs = 55000;
      else if (strstr(action.payload, "Dance") != nullptr)     animDurationMs = 10000;
      else if (strstr(action.payload, "Squat") != nullptr)     animDurationMs = 20000;
      else if (strstr(action.payload, "Celebrate") != nullptr) animDurationMs = 8000;
      else if (strstr(action.payload, "Left Punch") != nullptr) animDurationMs = 2500;
      else if (strstr(action.payload, "Right Punch") != nullptr) animDurationMs = 2500;
      else if (strstr(action.payload, "Kick") != nullptr)      animDurationMs = 7000;

      for (int rep = 0; rep < action.paramVal; rep++) {
        Serial.printf("  ► Rep %d of %d: [HEX] ", rep + 1, action.paramVal);
        for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
        Serial.printf("(Duration: %lu ms)\n", animDurationMs);

        pRemoteChar->writeValue(packet, totalPacketLen);
        delay(animDurationMs);
        if (rep < action.paramVal - 1) {
          delay(400); // Inter-repetition settling pause
        }
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
      delay(1000);
      Serial.printf(">>> [SUCCESS] Simulated %s %d Deg° Turn! <<<\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal);
    } else if (isWalk) {
      unsigned long walkDurationMs = action.paramVal * 1400UL;
      Serial.printf("  ► Locomotion Command (Simulated): [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Target: %d Steps, Duration: %lu ms)\n", action.paramVal, walkDurationMs);
      delay(walkDurationMs);
      Serial.print("  ► Locomotion Stop (Simulated): [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      delay(1200);
      Serial.printf(">>> [SUCCESS] Simulated %d Steps Locomotion! <<<\n", action.paramVal);
    } else if (isPredefined) {
      unsigned long animDurationMs = 4000;
      if (strstr(action.payload, "Push Ups") != nullptr)       animDurationMs = 12000;
      else if (strstr(action.payload, "Say Hello") != nullptr) animDurationMs = 8500;
      else if (strstr(action.payload, "Handstand") != nullptr) animDurationMs = 18000;
      else if (strstr(action.payload, "Kung Fu") != nullptr)   animDurationMs = 11000;
      else if (strstr(action.payload, "Boogaloo") != nullptr)  animDurationMs = 55000;
      else if (strstr(action.payload, "Dance") != nullptr)     animDurationMs = 10000;
      else if (strstr(action.payload, "Squat") != nullptr)     animDurationMs = 20000;
      else if (strstr(action.payload, "Celebrate") != nullptr) animDurationMs = 8000;
      else if (strstr(action.payload, "Left Punch") != nullptr) animDurationMs = 2500;
      else if (strstr(action.payload, "Right Punch") != nullptr) animDurationMs = 2500;
      else if (strstr(action.payload, "Kick") != nullptr)      animDurationMs = 7000;
      for (int rep = 0; rep < action.paramVal; rep++) {
        Serial.printf("  ► Action Rep %d of %d (Simulated): [HEX] ", rep + 1, action.paramVal);
        for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
        Serial.printf("(Duration: %lu ms)\n", animDurationMs);
        delay(animDurationMs);
        if (rep < action.paramVal - 1) {
          delay(400);
        }
      }
      Serial.println(">>> [SUCCESS] All action repetitions simulated! <<<");
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
// 8.1 TOKEN TO ACTION OBJECT MAPPER
// ==============================================================================
RobosenAction getActionObjByToken(uint8_t token, int param) {
  RobosenAction act;
  act.tokenID   = token;
  act.paramVal  = (param <= 0) ? 1 : param;
  act.paramMin  = 1;
  act.paramMax  = 5;
  act.paramStep = 1;

  switch (token) {
    case 0x01: // Walk Forward
      act.name = "Walk Forward";
      act.opcode = 0x01;
      act.payload = "";
      act.paramUnit = "Steps";
      act.paramMin = 1; act.paramMax = 5; act.paramStep = 1;
      break;
    case 0x02: // Walk Backward
      act.name = "Walk Backward";
      act.opcode = 0x05;
      act.payload = "";
      act.paramUnit = "Steps";
      act.paramMin = 1; act.paramMax = 5; act.paramStep = 1;
      break;
    case 0x03: // Turn Left
      act.name = "Turn Left";
      act.opcode = 0x08;
      act.payload = "";
      act.paramUnit = "Deg°";
      act.paramMin = 45; act.paramMax = 180; act.paramStep = 45;
      if (param < 45) act.paramVal = 90;
      break;
    case 0x04: // Turn Right
      act.name = "Turn Right";
      act.opcode = 0x02;
      act.payload = "";
      act.paramUnit = "Deg°";
      act.paramMin = 45; act.paramMax = 180; act.paramStep = 45;
      if (param < 45) act.paramVal = 90;
      break;
    case 0x07: // Side-step Left
      act.name = "Side-step Left";
      act.opcode = 0x07;
      act.payload = "";
      act.paramUnit = "Steps";
      act.paramMin = 1; act.paramMax = 5; act.paramStep = 1;
      break;
    case 0x08: // Side-step Right
      act.name = "Side-step Right";
      act.opcode = 0x03;
      act.payload = "";
      act.paramUnit = "Steps";
      act.paramMin = 1; act.paramMax = 5; act.paramStep = 1;
      break;
    case 0x10: // Left Punch
      act.name = "Left Punch";
      act.opcode = 0x17;
      act.payload = "ProAction/Left Punch";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x11: // Right Punch
      act.name = "Right Punch";
      act.opcode = 0x17;
      act.payload = "ProAction/Right Punch";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x12: // Kung Fu
      act.name = "Kung Fu";
      act.opcode = 0x17;
      act.payload = "ProAction/Kung Fu";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x13: // Dance
      act.name = "Dance";
      act.opcode = 0x17;
      act.payload = "Action/Boogaloo";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x14: // Push-ups
      act.name = "Push-ups";
      act.opcode = 0x17;
      act.payload = "ProAction/Push Ups";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x15: // Handstand
      act.name = "Handstand";
      act.opcode = 0x17;
      act.payload = "ProAction/Handstand";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x16: // Single Kick
      act.name = "Single Kick";
      act.opcode = 0x17;
      act.payload = "ProAction/Left Kick";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x17: // Squats
      act.name = "Squats";
      act.opcode = 0x17;
      act.payload = "ProAction/Do Squats";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x18: // Wave Hand
      act.name = "Wave Hand";
      act.opcode = 0x17;
      act.payload = "ProAction/Say Hello";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    case 0x19: // Celebrate
      act.name = "Celebrate";
      act.opcode = 0x17;
      act.payload = "ProAction/Celebrate";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
    default:
      act.name = "Custom Action";
      act.opcode = 0x00;
      act.payload = "";
      act.paramUnit = "Reps";
      act.paramMin = 1; act.paramMax = 3; act.paramStep = 1;
      break;
  }
  return act;
}

// ==============================================================================
// 8.2 RUN CHAIN ENGINE: PHASE 1 (DISCOVERY 0xAA) & PHASE 2 (EXECUTION 0xBB)
// ==============================================================================
bool executeRunChain() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 [RUN CHAIN ENGINE] PHASE 1: DISCOVERY                  ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ Emitting Discovery Seed [0xAA, 0, 0, 0, 0x55] on GPIO 15 (TX)...       ║");

  // 1. Flush any residual noise or old bytes on Chain Return Rail
  while (ChainSerial.available() > 0) {
    ChainSerial.read();
  }

  // 2. Dispatch Phase 1 Discovery Seed Frame: [0xAA, Len=0, Count=0, CRC=0, Footer=0x55]
  uint8_t seedPkt[5] = { 0xAA, 0x00, 0x00, 0x00, 0x55 };
  ChainSerial.write(seedPkt, 5);
  ChainSerial.flush();

  // 3. Await header (0xAA) on Return Rail (PIN_CHAIN_RX = GPIO 16) with 350ms timeout
  unsigned long t0 = millis();
  bool headerFound = false;
  while (millis() - t0 < 350) {
    if (ChainSerial.available() > 0) {
      uint8_t b = ChainSerial.read();
      if (b == 0xAA) {
        headerFound = true;
        break;
      }
    }
    delay(1);
  }

  if (!headerFound) {
    Serial.println("║ ❌ Return Rail: No response / open circuit. (No blocks or no End Block)║");
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    return false;
  }

  // 4. Read Len and Count
  unsigned long t1 = millis();
  while (ChainSerial.available() < 2 && (millis() - t1 < 100)) delay(1);
  if (ChainSerial.available() < 2) {
    Serial.println("║ ❌ Incomplete response: Timeout waiting for length and count.          ║");
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    return false;
  }

  uint8_t len = ChainSerial.read();
  uint8_t count = ChainSerial.read();

  if (count == 0 || len != count * 2 || len > 60) {
    Serial.printf("║ ❌ Invalid chain frame dimensions: Len=%d, Count=%d                       ║\n", len, count);
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    return false;
  }

  // 5. Read payload (len bytes) + CRC8 (1 byte) + Footer (1 byte)
  uint8_t rxBuf[64];
  unsigned long t2 = millis();
  int bytesRead = 0;
  while (bytesRead < (len + 2) && (millis() - t2 < 200)) {
    if (ChainSerial.available() > 0) {
      rxBuf[bytesRead++] = ChainSerial.read();
    } else {
      delay(1);
    }
  }

  if (bytesRead < (len + 2)) {
    Serial.printf("║ ❌ Frame truncated: Expected %d bytes, only received %d.                 ║\n", len + 2, bytesRead);
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    return false;
  }

  uint8_t rxCrc = rxBuf[len];
  uint8_t footer = rxBuf[len + 1];

  // 6. Verify cumulative CRC-8 (covers [len, count, payload...])
  uint8_t checkBuf[64];
  checkBuf[0] = len;
  checkBuf[1] = count;
  for (int i = 0; i < len; i++) {
    checkBuf[2 + i] = rxBuf[i];
  }
  uint8_t calcCrc = calcCrc8(checkBuf, 2 + len);

  if (calcCrc != rxCrc || footer != 0x55) {
    Serial.printf("║ ❌ CRC-8 Mismatch! Calc: 0x%02X, Recv: 0x%02X, Footer: 0x%02X                   ║\n",
                  calcCrc, rxCrc, footer);
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    return false;
  }

  // 7. Compilation Success! Print complete program sequence
  Serial.printf("║ 🟢 Loopback Verified! Sequence Compiled: %d Steps, CRC: 0x%02X (VALID ✓) ║\n", count, rxCrc);
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  for (int i = 0; i < count; i++) {
    uint8_t actId = rxBuf[i * 2];
    uint8_t parVal = rxBuf[i * 2 + 1];
    Serial.printf("║  Step %d: [0x%02X] %-20s Parameter: %3d %-6s        ║\n",
                  i + 1, actId, getActionNameByToken(actId), parVal, getParamUnitByToken(actId));
  }
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

  // Brief pause before execution begins
  delay(400);

  // 8. PHASE 2: REAL-TIME STEP EXECUTION & WS2812B STEP TRACKING (0xBB)
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 [RUN CHAIN ENGINE] PHASE 2: EXECUTION                  ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

  for (int s = 1; s <= count; s++) {
    uint8_t actId  = rxBuf[(s - 1) * 2];
    uint8_t parVal = rxBuf[(s - 1) * 2 + 1];
    RobosenAction actionObj = getActionObjByToken(actId, parVal);

    // Broadcast Step Execution Frame: [0xBB, ActiveStep, TotalSteps, CRC8, 0x55]
    uint8_t stepPayload[2] = { (uint8_t)s, (uint8_t)count };
    uint8_t stepCrc = calcCrc8(stepPayload, 2);
    uint8_t stepPkt[5] = { 0xBB, (uint8_t)s, (uint8_t)count, stepCrc, 0x55 };
    ChainSerial.write(stepPkt, 5);
    ChainSerial.flush();

    setStatusLED(0, 100, 20); // Vivid Green: Active step
    Serial.printf("\n>>> [STEP %d of %d] Block #%d ACTIVE (Glowing Bright Green) <<<\n", s, count, s);
    Serial.printf(">>> Executing: '%s' (%d %s) on Robot <<<\n", 
                  actionObj.name, actionObj.paramVal, actionObj.paramUnit);

    // Update E-Ink Display with current active step
    updateEInkRunChain(s, count, actionObj.name, actionObj.paramVal, actionObj.paramUnit);

    // Dispatch BLE motion command to physical robot
    sendRobosenPacket(actionObj);

    // Inter-step settling delay
    delay(500);
  }

  // 9. PHASE 3: PROGRAM COMPLETE & RAINBOW VICTORY CELEBRATION (ActiveStep = 0xFF)
  uint8_t endPayload[2] = { 0xFF, (uint8_t)count };
  uint8_t endCrc = calcCrc8(endPayload, 2);
  uint8_t endPkt[5] = { 0xBB, 0xFF, (uint8_t)count, endCrc, 0x55 };
  ChainSerial.write(endPkt, 5);
  ChainSerial.flush();

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║  🎉 [MISSION COMPLETE] All chain steps successfully executed!          ║");
  Serial.println("║  Triggering Rainbow Victory Sparkle across all connected blocks!       ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝\n");

  updateEInkRunChain(count, count, "ALL STEPS DONE! [OK]", 0, "");

  // Master RGB LED Rainbow Sparkle
  for (int k = 0; k < 3; k++) {
    setStatusLED(100, 0, 0);   delay(80);
    setStatusLED(100, 50, 0);  delay(80);
    setStatusLED(100, 100, 0); delay(80);
    setStatusLED(0, 100, 0);   delay(80);
    setStatusLED(0, 0, 100);   delay(80);
    setStatusLED(50, 0, 100);  delay(80);
  }
  updateStatusLED();

  delay(1200);
  renderActionMenu(); // Return display back to Action Menu

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
  updateEInkScanning(); // Render Scanning status on E-Ink

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
  Serial.println("║ • Start Click: Run Chain Sequence     • Hold Start: BLE Pairing (3s)   ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

  // Render to 2.13" E-Paper Display
  updateEInkActionMenu();
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

  // Render to 2.13" E-Paper Display
  updateEInkPairingMenu();
}

// ==============================================================================
// 11. E-INK DISPLAY CONTROLLER IMPLEMENTATION (DEPG0213BN / SSD1680)
// ==============================================================================

/**
 * Renders the main Master Block user interface onto the 2.13" E-Paper display.
 * Uses Fast Partial Refresh with zero-flicker transitions.
 */
void updateEInkActionMenu() {
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);

    int16_t w = display.width();
    int16_t h = display.height();

    // 1. Frame border
    display.drawRect(0, 0, w, h, GxEPD_BLACK);
    display.drawRect(1, 1, w - 2, h - 2, GxEPD_BLACK);

    // 2. Top Title Bar (Inverted Header)
    display.fillRect(2, 2, w - 4, 20, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(6, 17);
    display.print("ROBOSEN K1");

    // Top-Right Status Badge
    display.setFont(); // Default 5x7 font
    display.setTextSize(1);
    display.setCursor(160, 8);
    if (isConnected) {
      display.print("[CONNECTED]");
    } else if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
      display.print("[UNPAIRED]");
    } else if (connectAttemptCounter > 0) {
      display.printf("[RETRY #%d]", connectAttemptCounter);
    } else {
      display.print("[SEARCHING]");
    }

    // 3. Center Action & Parameter Section
    RobosenAction& act = ACTIONS[currentActionIndex];

    // Action Name
    display.setTextColor(GxEPD_BLACK);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(8, 44);
    display.print(act.name);

    // Parameter Value & Unit
    display.setCursor(10, 68);
    display.printf("[%d]", act.paramVal);

    display.setCursor(55, 68);
    display.print(act.paramUnit);

    // Visual Dots / Gauge for Parameter (1 to 5)
    display.setFont();
    for (int i = 0; i < 5; i++) {
      int dotX = 180 + (i * 12);
      int dotY = 62;
      if (i < act.paramVal) {
        display.fillCircle(dotX, dotY, 4, GxEPD_BLACK);
      } else {
        display.drawCircle(dotX, dotY, 4, GxEPD_BLACK);
      }
    }

    // 4. Horizontal Divider Line
    display.drawLine(2, 82, w - 3, 82, GxEPD_BLACK);

    // 5. Bottom Config Dock Status Area
    display.setFont();
    display.setTextSize(1);
    display.setCursor(8, 89);
    if (isBlockDocked) {
      display.printf("DOCK: [0x%02X] %s (%d %s)", 
                     dockedActionId, getActionNameByToken(dockedActionId),
                     dockedParamVal, getParamUnitByToken(dockedActionId));
      display.setCursor(8, 103);
      display.print("Knob 1 Click: Burn Config to Block");
    } else {
      display.print("DOCK: EMPTY (Insert Block to Config)");
      display.setCursor(8, 103);
      display.print("Start: Run Chain | Hold: Pair (3s)");
    }

  } while (display.nextPage());
}

/**
 * Renders the Teacher BLE Pairing Menu on the E-Ink display.
 */
void updateEInkPairingMenu() {
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    int16_t w = display.width();
    int16_t h = display.height();

    // Frame
    display.drawRect(0, 0, w, h, GxEPD_BLACK);
    display.drawRect(1, 1, w - 2, h - 2, GxEPD_BLACK);

    // Header
    display.fillRect(2, 2, w - 4, 20, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(6, 17);
    display.print("PAIR ROBOT (BLE)");

    display.setFont();
    display.setTextSize(1);
    display.setCursor(170, 8);
    display.printf("%d FOUND", bleDeviceCount);

    // Device List
    display.setTextColor(GxEPD_BLACK);
    if (bleDeviceCount == 0) {
      display.setCursor(14, 46);
      display.print("No K1 robots found in range.");
      display.setCursor(14, 62);
      display.print("Ensure robot is powered ON.");
    } else {
      int startIdx = (currentBleIndex / 3) * 3;
      int yPos = 32;
      for (int i = startIdx; i < bleDeviceCount && i < startIdx + 3; i++) {
        if (i == currentBleIndex) {
          display.fillRect(4, yPos - 2, w - 8, 15, GxEPD_BLACK);
          display.setTextColor(GxEPD_WHITE);
          display.setCursor(8, yPos);
          display.printf("> %-16s %3ddBm", bleList[i].name.substring(0, 16).c_str(), bleList[i].rssi);
        } else {
          display.setTextColor(GxEPD_BLACK);
          display.setCursor(8, yPos);
          display.printf("  %-16s %3ddBm", bleList[i].name.substring(0, 16).c_str(), bleList[i].rssi);
        }
        yPos += 16;
      }
    }

    // Divider & Footer
    display.drawLine(2, 92, w - 3, 92, GxEPD_BLACK);
    display.setTextColor(GxEPD_BLACK);
    display.setFont();
    display.setCursor(8, 98);
    display.print("Knob: Select  |  Click: Connect & Save");
    display.setCursor(8, 110);
    display.print("Start: Cancel & Return");

  } while (display.nextPage());
}

/**
 * Displays Scanning screen while BLE scan is active (4 seconds).
 */
void updateEInkScanning() {
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    int16_t w = display.width();
    int16_t h = display.height();

    display.drawRect(0, 0, w, h, GxEPD_BLACK);
    display.drawRect(1, 1, w - 2, h - 2, GxEPD_BLACK);

    display.fillRect(2, 2, w - 4, 20, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(6, 17);
    display.print("BLE SCANNING...");

    display.setFont();
    display.setTextColor(GxEPD_BLACK);
    display.setTextSize(1);
    display.setCursor(16, 46);
    display.print("Searching nearby Robosen K1 robots...");
    display.setCursor(16, 62);
    display.print("Sorting by RSSI signal strength.");

    display.drawLine(2, 92, w - 3, 92, GxEPD_BLACK);
    display.setCursor(8, 102);
    display.print("Hold Start Button to cancel");
  } while (display.nextPage());
}

/**
 * Displays Run Chain real-time execution status on E-Ink screen.
 */
void updateEInkRunChain(int currentStep, int totalSteps, const char* actionName, int paramVal, const char* paramUnit) {
  display.setPartialWindow(0, 0, display.width(), display.height());
  display.firstPage();
  do {
    display.fillScreen(GxEPD_WHITE);
    int16_t w = display.width();
    int16_t h = display.height();

    display.drawRect(0, 0, w, h, GxEPD_BLACK);
    display.drawRect(1, 1, w - 2, h - 2, GxEPD_BLACK);

    display.fillRect(2, 2, w - 4, 20, GxEPD_BLACK);
    display.setTextColor(GxEPD_WHITE);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(6, 17);
    display.print("RUNNING CHAIN");

    display.setFont();
    display.setTextSize(1);
    display.setCursor(170, 8);
    if (totalSteps > 0) {
      display.printf("STEP %d/%d", currentStep, totalSteps);
    } else {
      display.print("PHASE 1");
    }

    // Action Name
    display.setTextColor(GxEPD_BLACK);
    display.setFont(&FreeSansBold9pt7b);
    display.setCursor(10, 48);
    display.print(actionName);

    display.setFont();
    display.setTextSize(2);
    display.setCursor(10, 64);
    if (paramVal > 0) {
      display.printf("%d %s", paramVal, paramUnit);
    } else {
      display.print("Active");
    }

    display.drawLine(2, 92, w - 3, 92, GxEPD_BLACK);
    display.setTextSize(1);
    display.setCursor(8, 102);
    display.print("Physical Chain Bus Active (Phase 2)");
  } while (display.nextPage());
}
