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
#include <Fonts/FreeSansBold12pt7b.h>
#include <Fonts/FreeSansBold18pt7b.h>
#include "esp32_master_icons.h"

// ==============================================================================
// 1. PIN DEFINITIONS (PROTOTYPE #01 CARRIER PCB SPEC - 4 UI INPUTS)
// ==============================================================================
// --- INPUT 1: KNOB 1 (ACTION SELECTOR ROTARY ENCODER - SW1) ---
const int PIN_K1_CLK    = 8;   // 🟡 Phase A (GPIO 8)
const int PIN_K1_DT     = 9;   // 🟢 Phase B (GPIO 9)
const int PIN_K1_SW     = 10;  // 🔵 Push Switch (GPIO 10)

// --- INPUT 2: KNOB 2 (PARAMETER ADJUSTER ROTARY ENCODER - SW2) ---
const int PIN_K2_CLK    = 11;  // ⚪ Phase A (GPIO 11)
const int PIN_K2_DT     = 12;  // 🟤 Phase B (GPIO 12)
const int PIN_K2_SW     = 13;  // 🔘 Push Switch (GPIO 13)

// --- INPUT 3: MASTER START / CONFIRM BUTTON (SW3 - GREEN 12mm TACTILE) ---
const int PIN_START_BTN = 14;  // 🟢 Green Tactile Button (Confirm / Start / Run) - Active LOW (GPIO 14)

// --- INPUT 4: MASTER STOP / CANCEL BUTTON (SW5 - RED 12mm TACTILE) ---
const int PIN_STOP_BTN  = 2;   // 🔴 Red Tactile Button (Cancel / Emergency Stop / Back) - Active LOW (GPIO 2)

// --- BATTERY SENSE (ADC1_CH0) ---
const int PIN_BATSENSE  = 1;   // 🔋 Battery Voltage Divider Midpoint (100k / 100k + 100nF filter) (GPIO 1)

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

// Production verified driver subclass for DEPG0213BN panel with bounded BUSY timeout,
// pull-down protection against floating BUSY wires, and safe LUT injection.
class RobosenEPD2_213_BN : public GxEPD2_213_BN {
public:
  RobosenEPD2_213_BN(int16_t cs, int16_t dc, int16_t rst, int16_t busy)
    : GxEPD2_213_BN(cs, dc, rst, busy) {
    // Cap each _waitWhileBusy call to 900ms instead of GxEPD2's default 10,000,000us (10s)
    // so a stuck/disconnected BUSY wire never stalls boot for 20s or freezes Core 0.
    _busy_timeout = 900000;
  }

  void configureBusyPin(bool bypassToTimed) {
    if (bypassToTimed) {
      _busy = -1;
    } else {
      _busy = PIN_EPD_BUSY;
      pinMode(PIN_EPD_BUSY, INPUT);
    }
  }

  // Returns true if GPIO 4 (BUSY) is floating (open wire: PD=0, PU=1) or stuck HIGH (PD=1, PU=1).
  // A healthy connected SSD1680 actively drives BUSY LOW when idle (PD=0, PU=0).
  bool detectFaultyBusyPin() {
    pinMode(PIN_EPD_BUSY, INPUT_PULLDOWN);
    delayMicroseconds(150);
    int pd = digitalRead(PIN_EPD_BUSY);
    pinMode(PIN_EPD_BUSY, INPUT_PULLUP);
    delayMicroseconds(150);
    int pu = digitalRead(PIN_EPD_BUSY);
    pinMode(PIN_EPD_BUSY, INPUT_PULLDOWN);
    return (pd != LOW || pu != LOW);
  }

  bool isBusyBypassed() const {
    return (_busy < 0);
  }

  void applyCustomLut(const uint8_t* lutProgmem) {
    if (!_init_display_done) {
      writeScreenBuffer(0xFF); // Ensure _InitDisplay() (0x12 SWRESET) runs BEFORE loading LUT
    }
    if (!_power_is_on) {
      _writeCommand(0x22);
      _writeData(0xf8);
      _writeCommand(0x20);
      _waitWhileBusy("_PowerOn", power_on_time);
      _power_is_on = true;
    }
    _writeCommand(0x32);
    _writeDataPGM(lutProgmem, 153);
    _using_partial_mode = true; // Prevent _Update_Part() from overwriting 0x32 with lut_partial
  }
};

GxEPD2_BW<RobosenEPD2_213_BN, RobosenEPD2_213_BN::HEIGHT> display(
  RobosenEPD2_213_BN(PIN_EPD_CS, PIN_EPD_DC, PIN_EPD_RES, PIN_EPD_BUSY)
);

// --- 2.13" E-PAPER DISPLAY VISIBLE VIEWPORT DEFINITIONS (CALIBRATED FOR 3D BEZEL) ---
#define SCREEN_VISIBLE_X_MIN    40
#define SCREEN_VISIBLE_Y_MIN     0
#define SCREEN_VISIBLE_X_MAX   249
#define SCREEN_VISIBLE_Y_MAX   121
#define SCREEN_VISIBLE_WIDTH   210
#define SCREEN_VISIBLE_HEIGHT  122

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
// 3.1 CONFIG DOCK (0xCF) & RUN PORT (0xAA) LIVE DETECTION STATE
// ==============================================================================
bool isBlockDocked = false;
uint8_t dockedActionId = 0;
uint8_t dockedParamVal = 0;
unsigned long lastConfigPollTime = 0;
unsigned long lastDockResponseTime = 0;
const unsigned long CONFIG_POLL_INTERVAL_MS = 350;
const unsigned long CONFIG_TIMEOUT_MS = 1200;

// Non-blocking UART1 (Config Port) RX parser state
uint8_t cfgRxBuf[8];
uint8_t cfgRxIdx = 0;
unsigned long cfgRxLastByteMs = 0;

// Run Chain Port (UART2) Live Detection State (0xAA Loopback)
bool isRunChainConnected = false;
int detectedChainCount = 0;
uint8_t detectedChainBuf[64];
unsigned long lastChainPollTime = 0;
unsigned long lastChainResponseTime = 0;
const unsigned long CHAIN_POLL_INTERVAL_MS = 800;
const unsigned long CHAIN_TIMEOUT_MS = 2200;

// Non-blocking UART2 (Run Chain Port) RX parser state
uint8_t chainRxHeaderBuf[3];
uint8_t chainRxHeaderIdx = 0;
uint8_t chainRxPayloadBuf[64];
uint8_t chainRxPayloadIdx = 0;
unsigned long chainRxLastByteMs = 0;

inline bool hasAnyBlockConnected() {
  return isBlockDocked || isRunChainConnected;
}

bool syncMenuToDockedBlock(uint8_t token, uint8_t param) {
  for (int i = 0; i < TOTAL_ACTIONS; i++) {
    if (ACTIONS[i].tokenID == token) {
      currentActionIndex = i;
      int val = (int)param;
      if (ACTIONS[i].paramStep > 1) {
        val = ((val + ACTIONS[i].paramStep / 2) / ACTIONS[i].paramStep) * ACTIONS[i].paramStep;
      }
      ACTIONS[i].paramVal = constrain(val, ACTIONS[i].paramMin, ACTIONS[i].paramMax);
      return true;
    }
  }
  return false;
}

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
  STATE_BLE_PAIRING_MENU,
  STATE_RUNNING,
  STATE_MODE_SELECT_MENU,
  STATE_REMOTE_CONTROL,
  STATE_JOINT_CONTROL
};
SystemState currentState = STATE_ACTION_MENU;
SystemState previousOperationalState = STATE_ACTION_MENU;

// ==============================================================================
// 4.01 MULTI-MODE SWITCHER & REMOTE CONTROL (RC) DEFINITIONS
// ==============================================================================
struct SystemModeItem {
  const char* name;
  const char* desc;
  SystemState state;
};

SystemModeItem SYSTEM_MODES[] = {
  {"01: Block Coding & Dock", "Tangible Chain + Flash Dock", STATE_ACTION_MENU},
  {"02: Remote Control (RC)",  "Live Steering + Stunt Drive", STATE_REMOTE_CONTROL},
  {"03: Joint Control Mode",   "Anatomy Groups + Servo Angle", STATE_JOINT_CONTROL}
};
const int TOTAL_SYSTEM_MODES = sizeof(SYSTEM_MODES) / sizeof(SYSTEM_MODES[0]);
int currentModeMenuIndex = 0;

// Remote Control (RC) Gear Selector: 2-way toggle DRIVE <-> STRAFE
enum RcGear {
  RC_GEAR_DRIVE = 0,
  RC_GEAR_STRAFE = 1
};
RcGear currentRcGear = RC_GEAR_DRIVE;

// Live non-blocking motion state
enum RcActiveMotion {
  RC_MOTION_IDLE = 0,
  RC_MOTION_WALK_FWD,
  RC_MOTION_WALK_REV,
  RC_MOTION_TURN_LEFT,
  RC_MOTION_TURN_RIGHT,
  RC_MOTION_STRAFE_LEFT,
  RC_MOTION_STRAFE_RIGHT,
  RC_MOTION_STUNT
};
RcActiveMotion currentRcMotion = RC_MOTION_IDLE;

// Mode 2 Remote Control Action Item (exclusively stunts: Punch, Push-ups, Wave)
struct RcActionItem {
  const char* name;
  uint8_t opcode;
  const char* payload;
  unsigned long durationMs;
  const unsigned char* icon;
};

const RcActionItem RC_ACTIONS[] = {
  {"01: Punch Left", 0x17, "ProAction/Left Punch", 2500,  ICON_PUNCH},
  {"02: Push-ups",   0x17, "ProAction/Push Ups",   12000, ICON_PUSHUPS},
  {"03: Wave Hand",  0x17, "ProAction/Say Hello",  8500,  ICON_WAVE}
};
const int TOTAL_RC_ACTIONS = sizeof(RC_ACTIONS) / sizeof(RC_ACTIONS[0]);
int rcActionIndex = 0;

// RC Momentum & Duration Timers
unsigned long rcSteerActiveUntilMs = 0;
unsigned long rcStuntEndMs = 0;

// ==============================================================================
// 4.02 JOINT CONTROL MODE DEFINITIONS & ANATOMICAL HIERARCHY
// ==============================================================================
struct JointDef {
  uint8_t servoId;
  const char* name;
  uint8_t groupIconIdx; // 0=Head, 1=L.Arm, 2=R.Arm, 3=L.Leg, 4=R.Leg
  uint8_t neutral;
  uint8_t minLimit;
  uint8_t maxLimit;
};

const JointDef ALL_JOINTS[17] = {
  {16, "Head Pan",   0, 123, 42,  202},
  {6,  "L.Shoulder", 1, 222, 22,  242},
  {12, "L.Elbow",    1, 214, 33,  233},
  {13, "L.Wrist",    1, 146, 16,  216},
  {7,  "R.Shoulder", 2, 26,  6,   226},
  {14, "R.Elbow",    2, 42,  34,  224},
  {15, "R.Wrist",    2, 99,  26,  226},
  {0,  "L.Thigh",    3, 126, 29,  229},
  {1,  "L.Calf",     3, 65,  10,  220},
  {2,  "L.Ankle",    3, 100, 26,  226},
  {8,  "L.Hip",      3, 125, 103, 133},
  {9,  "L.Foot",     3, 116, 93,  133},
  {3,  "R.Thigh",    4, 127, 18,  218},
  {4,  "R.Calf",     4, 184, 30,  240},
  {5,  "R.Ankle",    4, 141, 26,  226},
  {10, "R.Hip",      4, 135, 119, 149},
  {11, "R.Foot",     4, 120, 105, 145}
};
const int TOTAL_JOINTS = 17;

// Calibrated factory standing posture baseline
const uint8_t STANDING_SERVO_DEFAULTS[17] = {
  126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99, 123
};

// Live 17-servo coordinate tracking array
uint8_t currentServoPositions[17] = {
  126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99, 123
};

// Mode 3 navigation state (Single flat 17-joint controller)
int currentJointIndex = 0;      // 0..16
unsigned long lastJointBleSendMs = 0;

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

// Live Robot Telemetry State (Opcode 0x0F)
volatile int robotBatteryPercent = -1;
volatile bool hasRobotBattery = false;
volatile uint8_t robotSpeakerVolume = 100;
volatile bool robotAutoStand = true;

// Retry Timing: 1s fast scan + 2s pause between attempts
const unsigned long RETRY_INTERVAL_MS = 2000;
unsigned long lastConnectAttemptTime = 0;
int connectAttemptCounter = 0;

// --- ROTARY ENCODER STATE MACHINE (BUXTRONIX QUADRATURE DECODER) ---
// Immune to mechanical contact bounce, detent vibration, and settling recoil.
#define R_START     0x0
#define R_CW_FINAL  0x1
#define R_CW_BEGIN  0x2
#define R_CW_NEXT   0x3
#define R_CCW_BEGIN 0x4
#define R_CCW_FINAL 0x5
#define R_CCW_NEXT  0x6

#define DIR_NONE 0x00
#define DIR_CW   0x10
#define DIR_CCW  0x20

// Full-step state table: emits code when detent reached (both pins HIGH / state 3)
const unsigned char PROGMEM ttable[7][4] = {
  // 00         01           10           11
  {R_START,    R_CW_BEGIN,  R_CCW_BEGIN, R_START},           // R_START
  {R_CW_NEXT,  R_START,     R_CW_FINAL,  R_START | DIR_CW},  // R_CW_FINAL
  {R_CW_NEXT,  R_CW_BEGIN,  R_START,     R_START},           // R_CW_BEGIN
  {R_CW_NEXT,  R_CW_BEGIN,  R_CW_FINAL,  R_START},           // R_CW_NEXT
  {R_CCW_NEXT, R_START,     R_CCW_BEGIN, R_START},           // R_CCW_BEGIN
  {R_CCW_NEXT, R_CCW_FINAL, R_START,     R_START | DIR_CCW}, // R_CCW_FINAL
  {R_CCW_NEXT, R_CCW_FINAL, R_CCW_BEGIN, R_START},           // R_CCW_NEXT
};

volatile uint8_t k1State = R_START;
volatile uint8_t k2State = R_START;
volatile int k1Delta = 0;
volatile int k2Delta = 0;

void IRAM_ATTR isrK1() {
  uint8_t pinstate = (digitalRead(PIN_K1_CLK) << 1) | digitalRead(PIN_K1_DT);
  uint8_t result = pgm_read_byte(&ttable[k1State & 0x0F][pinstate]);
  k1State = result & 0x0F;
  uint8_t dir = result & 0x30;
  if (dir == DIR_CW) {
    k1Delta++;
  } else if (dir == DIR_CCW) {
    k1Delta--;
  }
}

void IRAM_ATTR isrK2() {
  uint8_t pinstate = (digitalRead(PIN_K2_CLK) << 1) | digitalRead(PIN_K2_DT);
  uint8_t result = pgm_read_byte(&ttable[k2State & 0x0F][pinstate]);
  k2State = result & 0x0F;
  uint8_t dir = result & 0x30;
  if (dir == DIR_CW) {
    k2Delta++;
  } else if (dir == DIR_CCW) {
    k2Delta--;
  }
}

// --- NON-BLOCKING LED BLIP & ASYNC FREERTOS E-INK DISPLAY STATE ---
unsigned long ledBlipUntil = 0;
String lastUiEventMsg = "";
unsigned long lastUiEventTime = 0;

// FreeRTOS Display & BLE Synchronization State
SemaphoreHandle_t bleMutex = nullptr;
volatile bool requestBgReconnect = false;
volatile bool einkFullDirty = false;
volatile bool einkCenterDirty = false;
volatile bool einkScanningDirty = false;
volatile bool einkRunChainDirty = false;
volatile bool einkNeedsCrispSettle = false;
volatile bool einkForceReinit = false;
volatile unsigned long lastEInkInputMs = 0;
volatile unsigned long epdWaitStartMs = 0;

// Snapshot state for Run Chain E-Ink screen
volatile int rcSnapStep = 0;
volatile int rcSnapTotal = 0;
char rcSnapName[32] = "";
volatile int rcSnapParam = 0;
char rcSnapUnit[12] = "";

void requestEInkFullUpdate() {
  lastEInkInputMs = millis();
  einkFullDirty = true;
  einkNeedsCrispSettle = true;
}

void requestEInkCenterUpdate() {
  lastEInkInputMs = millis();
  einkCenterDirty = true;
  einkNeedsCrispSettle = true;
}

void setUiEventFeedback(const char* msg) {
  lastUiEventMsg = msg;
  lastUiEventTime = millis();
  requestEInkFullUpdate();
}

void triggerLedBlip(uint8_t r, uint8_t g, uint8_t b) {
  setStatusLED(r, g, b);
  ledBlipUntil = millis() + 50; // 50ms tactile feedback
}

unsigned long lastUserActivity = 0;
unsigned long lastHeartbeatTime = 0;

// Forward Declarations
void renderActionMenu();
void renderPairingMenu();
void renderModeSelectMenu();
void renderRemoteControlMenu();
void renderJointControlMenu();
void runBleScan();
bool connectToRobot(bool quietBg = false);
bool sendRobosenPacket(const RobosenAction& action);
void updateStatusLED();
void pollConfigDock();
void pollRunChainPort();
void enforcePortModeLock();
bool executeRunChain();
RobosenAction getActionObjByToken(uint8_t token, int param);
float readBatteryVoltage();
int calculateBatteryPercent(float vbat);
void sendLocomotionStop();
bool abortableDelay(unsigned long ms);
void triggerChainAbort(int count);

// Remote Control & Mode Switcher Helpers
void sendRawOpcodeNonBlocking(uint8_t opcode);
void sendStuntPacketNonBlocking(uint8_t opcode, const char* payload);
void stopRcMotionImmediate();
void updateRemoteControlEngine();

// Joint Control Mode 3 Helpers
void sendJointFrameNonBlocking(uint8_t speed = 25);
void resetActiveJointToCenter();
void resetAllJointsToStand();

// Robot Telemetry & Battery Monitoring Helpers
void queryRobotStateNonBlocking();
void sendHeartbeatPingNonBlocking();
void robotNotifyCallback(BLERemoteCharacteristic* pChar, uint8_t* pData, size_t length, bool isNotify);

// E-Ink Display Functions (DEPG0213BN / SSD1680)
void epdBusyYieldCallback(const void* param);
void printEInkAndPowerDiagnostics();
void loadCustomEInkLut(bool fastMode);
void drawActionMenuToBuffer(bool invertMiddle = false);
void updateEInkActionMenu();
void updateEInkPairingMenu();
void updateEInkModeSelectMenu();
void updateEInkRemoteControl();
void updateEInkJointControl();
void updateEInkScanning();
void updateEInkRunChain(int currentStep, int totalSteps, const char* actionName, int paramVal, const char* paramUnit);
void drawModeSelectMenuToBuffer();
void drawRemoteControlToBuffer(bool invertMiddle = false);
void drawJointControlToBuffer(bool invertMiddle = false);
void startBackgroundTasks();

// BLE Client Callbacks for Connection Life-Cycle Management
class RobosenClientCallback : public BLEClientCallbacks {
  void onConnect(BLEClient* pclient) {
    isConnected = true;
    Serial.println("\n[BLE STATUS] 🟢 Physical connection established with robot!");
  }

  void onDisconnect(BLEClient* pclient) {
    isConnected = false;
    pRemoteChar = nullptr;
    hasRobotBattery = false;
    robotBatteryPercent = -1;
    Serial.println("\n[BLE STATUS] 🔴 Robot disconnected / link lost! Resuming retry loop...");
    if (currentState == STATE_ACTION_MENU || currentState == STATE_REMOTE_CONTROL || currentState == STATE_JOINT_CONTROL) {
      updateStatusLED();
    }
  }
};

void updateStatusLED() {
  if (ledBlipUntil > 0 && millis() < ledBlipUntil) return; // Preserve active tactile feedback blip
  if (currentState == STATE_RUNNING) {
    setStatusLED(0, 100, 20); // 🟢 Bright Green: Chain actively executing
  } else if (currentState == STATE_BLE_SCANNING) {
    setStatusLED(0, 0, 40);  // 🔵 Vivid Blue: Active Scanning
  } else if (currentState == STATE_BLE_PAIRING_MENU) {
    setStatusLED(0, 0, 30);  // 🔵 Soft Blue: Pairing Menu Selection
  } else if (currentState == STATE_MODE_SELECT_MENU) {
    setStatusLED(40, 0, 80); // 🟣 Purple: Mode Selector Menu
  } else if (currentState == STATE_JOINT_CONTROL) {
    if (!isConnected) {
      if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
        setStatusLED(30, 0, 0);  // 🔴 Red: Unpaired
      } else {
        setStatusLED(30, 15, 0); // 🟠 Amber/Orange: Paired, reconnecting
      }
    } else {
      setStatusLED(0, 60, 60);  // 🔵 Vivid Cyan/Teal: Direct Joint Articulation
    }
  } else if (currentState == STATE_REMOTE_CONTROL) {
    if (!isConnected) {
      if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
        setStatusLED(30, 0, 0);  // 🔴 Red: Unpaired
      } else {
        setStatusLED(30, 15, 0); // 🟠 Amber/Orange: Paired, reconnecting
      }
    } else {
      if (currentRcMotion == RC_MOTION_WALK_FWD) {
        setStatusLED(0, 100, 10); // 🟢 Vivid Green: Walking Forward
      } else if (currentRcMotion == RC_MOTION_WALK_REV) {
        setStatusLED(100, 50, 0); // 🟠 Vivid Amber-Yellow: Walking Backward
      } else if (currentRcMotion == RC_MOTION_TURN_LEFT || currentRcMotion == RC_MOTION_TURN_RIGHT ||
                 currentRcMotion == RC_MOTION_STRAFE_LEFT || currentRcMotion == RC_MOTION_STRAFE_RIGHT) {
        setStatusLED(0, 40, 100); // 🔵 Vivid Electric Blue: Turning / Strafing
      } else if (currentRcMotion == RC_MOTION_STUNT) {
        setStatusLED(90, 0, 90);  // 🟣 Vivid Magenta: Executing Stunt
      } else {
        setStatusLED(0, 35, 25);  // 🟢 Soft Teal/Cyan: RC Connected & Ready
      }
    }
  } else if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    setStatusLED(30, 0, 0);  // 🔴 Red: Unpaired
  } else if (!isConnected) {
    setStatusLED(30, 15, 0); // 🟠 Amber/Orange: Paired, waiting / reconnecting
  } else {
    setStatusLED(0, 30, 0);  // 🟢 Emerald Green: Connected & Ready
  }
}

// ==============================================================================
// 4.1 BATTERY SENSE & SAFETY HALT IMPLEMENTATIONS
// ==============================================================================
float smoothedBatteryVoltage = 0.0f;
int lastDisplayedMasterPct = -1;
unsigned long lastMasterBatCheckMs = 0;

float sampleRawBatteryVoltage(uint32_t* outRawMv = nullptr) {
  uint32_t sumMv = 0;
  uint32_t maxMv = 0;
  for (int i = 0; i < 8; i++) {
    uint32_t mv = analogReadMilliVolts(PIN_BATSENSE);
    sumMv += mv;
    if (mv > maxMv) maxMv = mv;
  }
  uint32_t avgMv = sumMv / 8;
  uint32_t effMv = (avgMv + maxMv) / 2;
  if (outRawMv != nullptr) *outRawMv = effMv;
  // 1:1 precision voltage divider (R3=100k, R4=100k) => Vbat = Vadc * 2
  return (effMv * 2.0f) / 1000.0f;
}

float readBatteryVoltage() {
  float rawV = sampleRawBatteryVoltage();

  if (smoothedBatteryVoltage <= 0.1f) {
    smoothedBatteryVoltage = rawV;
  } else if (rawV > smoothedBatteryVoltage + 0.04f) {
    // Fast upward lock: immediately capture battery switch-on or recovery from a GPIO 1 contact dip
    smoothedBatteryVoltage = rawV;
  } else if (smoothedBatteryVoltage >= 3.50f && rawV < 3.40f) {
    // Glitch rejection: an intermittent/floating GPIO 1 pin drops to ~1.5V-1.7V ADC (3.0V-3.4V).
    // A real 18650 cell cannot drop from >=3.50V to <3.40V instantaneously; ignore floating-pin dropout.
  } else {
    // Normal gradual discharge smoothing (EMA)
    smoothedBatteryVoltage = (smoothedBatteryVoltage * 0.85f) + (rawV * 0.15f);
  }
  return smoothedBatteryVoltage;
}

int calculateBatteryPercent(float vbat) {
  if (vbat >= 4.20f) return 100;
  if (vbat <= 3.20f) return 0;
  int pct = (int)((vbat - 3.20f) / (4.20f - 3.20f) * 100.0f);
  return constrain(pct, 0, 100);
}

void sendLocomotionStop() {
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(40)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      uint8_t stopPacket[] = {0xFF, 0xFF, 0x02, 0x0C, 0x0E};
      pRemoteChar->writeValue(stopPacket, sizeof(stopPacket));
      Serial.println("  ► [SAFETY] Locomotion Stop [0xFF, 0xFF, 0x02, 0x0C, 0x0E] dispatched.");
    }
    xSemaphoreGive(bleMutex);
  }
}

bool abortableDelay(unsigned long ms) {
  unsigned long start = millis();
  while (millis() - start < ms) {
    if (digitalRead(PIN_STOP_BTN) == LOW) {
      Serial.println("\n🛑 [EMERGENCY STOP] Red Stop Button pressed during delay! Halting immediately!");
      sendLocomotionStop();
      return false;
    }
    delay(10);
  }
  return true;
}

// ==============================================================================
// 4.2 NON-BLOCKING REMOTE CONTROL (RC) BLE DISPATCH & ENGINE
// ==============================================================================
void sendRawOpcodeNonBlocking(uint8_t opcode) {
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(40)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      uint8_t packet[5];
      packet[0] = 0xFF;
      packet[1] = 0xFF;
      packet[2] = 0x02; // length = 1 (opcode) + 1 (checksum)
      packet[3] = opcode;
      packet[4] = (uint8_t)((0x02 + opcode) % 256);
      pRemoteChar->writeValue(packet, sizeof(packet));
    }
    xSemaphoreGive(bleMutex);
  }
}

void sendStuntPacketNonBlocking(uint8_t opcode, const char* payload) {
  uint8_t payloadLen = strlen(payload);
  uint8_t numBytes = 1 + payloadLen + 1;
  uint8_t totalPacketLen = 2 + numBytes + 1;
  uint8_t packet[totalPacketLen];

  packet[0] = 0xFF;
  packet[1] = 0xFF;
  packet[2] = numBytes;
  packet[3] = opcode;

  uint16_t checksum = numBytes + opcode;
  for (int i = 0; i < payloadLen; i++) {
    packet[4 + i] = (uint8_t)payload[i];
    checksum += packet[4 + i];
  }
  packet[totalPacketLen - 1] = (uint8_t)(checksum % 256);

  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(60)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      pRemoteChar->writeValue(packet, totalPacketLen);
    }
    xSemaphoreGive(bleMutex);
  }
}

void stopRcMotionImmediate() {
  if (currentRcMotion != RC_MOTION_IDLE) {
    sendLocomotionStop();
    currentRcMotion = RC_MOTION_IDLE;
  }
  rcSteerActiveUntilMs = 0;
  rcStuntEndMs = 0;
  updateStatusLED();
}

void updateRemoteControlEngine() {
  if (currentState != STATE_REMOTE_CONTROL) return;
  unsigned long now = millis();

  // 1. If executing action, check duration
  if (currentRcMotion == RC_MOTION_STUNT) {
    if (now >= rcStuntEndMs) {
      sendLocomotionStop(); // Ensure robot stops and stands if locomotion step was fired
      currentRcMotion = RC_MOTION_IDLE;
      updateStatusLED();
      Serial.println("[RC] Action execution finished. Returned to neutral posture.");
    }
    return;
  }

  // Read pedals
  bool fwdHeld = (digitalRead(PIN_START_BTN) == LOW);
  bool revHeld = (digitalRead(PIN_STOP_BTN) == LOW);

  // 2. Check steering / strafing momentum window
  if (currentRcMotion == RC_MOTION_TURN_LEFT || currentRcMotion == RC_MOTION_TURN_RIGHT ||
      currentRcMotion == RC_MOTION_STRAFE_LEFT || currentRcMotion == RC_MOTION_STRAFE_RIGHT) {
    if (now >= rcSteerActiveUntilMs) {
      // Momentum window elapsed! Check if Forward or Reverse pedal is still held
      if (fwdHeld && revHeld) {
        sendLocomotionStop();
        currentRcMotion = RC_MOTION_IDLE;
        updateStatusLED();
        Serial.println("[RC] Both pedals held -> Safety Stop");
      } else if (fwdHeld) {
        currentRcMotion = RC_MOTION_WALK_FWD;
        sendRawOpcodeNonBlocking(0x01);
        updateStatusLED();
        Serial.println("[RC] Auto-resumed Walk Forward (Green held)");
      } else if (revHeld) {
        currentRcMotion = RC_MOTION_WALK_REV;
        sendRawOpcodeNonBlocking(0x05);
        updateStatusLED();
        Serial.println("[RC] Auto-resumed Walk Backward (Red held)");
      } else {
        sendLocomotionStop();
        currentRcMotion = RC_MOTION_IDLE;
        updateStatusLED();
        Serial.println("[RC] Steer momentum ended -> Stopped (Neutral posture)");
      }
    }
    return;
  }

  // 3. Dual Pedal Handling: Green (Forward) & Red (Dedicated Reverse)
  if (fwdHeld && revHeld) {
    // Both pedals pressed: immediate safety priority halt
    if (currentRcMotion != RC_MOTION_IDLE) {
      sendLocomotionStop();
      currentRcMotion = RC_MOTION_IDLE;
      updateStatusLED();
      Serial.println("[RC] ⚠️ Both Forward and Reverse pedals held! Safety priority halt.");
    }
  } else if (fwdHeld) {
    if (currentRcMotion != RC_MOTION_WALK_FWD) {
      currentRcMotion = RC_MOTION_WALK_FWD;
      sendRawOpcodeNonBlocking(0x01);
      updateStatusLED();
      Serial.println("[RC] Green pedal held: Walking Forward...");
    }
  } else if (revHeld) {
    if (currentRcMotion != RC_MOTION_WALK_REV) {
      currentRcMotion = RC_MOTION_WALK_REV;
      sendRawOpcodeNonBlocking(0x05);
      updateStatusLED();
      Serial.println("[RC] Red pedal held: Walking Backward (Dedicated Reverse)...");
    }
  } else {
    // Neither pedal held
    if (currentRcMotion == RC_MOTION_WALK_FWD || currentRcMotion == RC_MOTION_WALK_REV) {
      sendLocomotionStop();
      currentRcMotion = RC_MOTION_IDLE;
      updateStatusLED();
      Serial.println("[RC] Pedal released: Locomotion stop locked.");
    }
  }
}

// ==============================================================================
// 4.3 JOINT CONTROL MODE (MODE 3) BLE DISPATCH & RESET HELPERS
// ==============================================================================
void sendJointFrameNonBlocking(uint8_t speed) {
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(40)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      // 30-byte packet format for Opcode 0xE8 (jointMove):
      // [0..1]: Header 0xFF, 0xFF
      // [2]: Length = 27 (0x1B)
      // [3]: Opcode = 0xE8
      // [4..20]: 17 servo positions
      // [21..27]: 7 padding bytes (125, 125, 125, 125, 100, 100, 100)
      // [28]: Speed byte
      // [29]: Checksum = (sum of bytes 2..28) % 256
      uint8_t packet[30];
      packet[0] = 0xFF;
      packet[1] = 0xFF;
      packet[2] = 27;
      packet[3] = 0xE8;

      uint16_t checksum = packet[2] + packet[3];
      for (int i = 0; i < 17; i++) {
        uint8_t pos = currentServoPositions[i];
        if (i == 16) {
          // Invert Head Pan (Servo 16) so physical head rotation matches UI slider and user expectation
          // Neutral = 123: 246 - 123 = 123; Min = 42: 246 - 42 -> 202; Max = 202: 246 - 202 -> 44
          int inverted = 246 - (int)pos;
          pos = (uint8_t)constrain(inverted, 42, 202);
        }
        packet[4 + i] = pos;
        checksum += packet[4 + i];
      }

      // 7 padding bytes
      packet[21] = 125;
      packet[22] = 125;
      packet[23] = 125;
      packet[24] = 125;
      packet[25] = 100;
      packet[26] = 100;
      packet[27] = 100;
      for (int i = 21; i <= 27; i++) {
        checksum += packet[i];
      }

      packet[28] = speed;
      checksum += packet[28];

      packet[29] = (uint8_t)(checksum % 256);

      pRemoteChar->writeValue(packet, sizeof(packet));
    }
    xSemaphoreGive(bleMutex);
  }
}

void resetActiveJointToCenter() {
  const JointDef& j = ALL_JOINTS[currentJointIndex];
  currentServoPositions[j.servoId] = j.neutral;
  sendJointFrameNonBlocking(25);
  triggerLedBlip(0, 80, 0);
  requestEInkCenterUpdate();
  Serial.printf("\n🎯 [JOINT] Reset Joint %d (%s) to neutral (%d)\n",
                j.servoId, j.name, j.neutral);
  setUiEventFeedback("JOINT: RESET TO CTR");
}

void resetAllJointsToStand() {
  for (int i = 0; i < 17; i++) {
    currentServoPositions[i] = STANDING_SERVO_DEFAULTS[i];
  }
  sendJointFrameNonBlocking(20);
  triggerLedBlip(90, 0, 90);
  requestEInkCenterUpdate();
  Serial.println("\n🧍 [JOINT] Reset ALL 17 joints to calibrated standing posture!");
  setUiEventFeedback("ALL JOINTS: STAND");
}

// ==============================================================================
// 4.4 ROBOT TELEMETRY & BATTERY PERCENTAGE MONITOR (OPCODE 0x0F)
// ==============================================================================
void queryRobotStateNonBlocking() {
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(40)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      // 5-byte Opcode 0x0F query: Header(0xFF, 0xFF), Len(0x02), Opcode(0x0F), Checksum(0x11)
      uint8_t queryPacket[5] = {0xFF, 0xFF, 0x02, 0x0F, 0x11};
      pRemoteChar->writeValue(queryPacket, sizeof(queryPacket));
    }
    xSemaphoreGive(bleMutex);
  }
}

void sendHeartbeatPingNonBlocking() {
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(40)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      // Proven 5-byte Opcode 0x0B Ping Packet from main firmware
      uint8_t pingPacket[5] = {0xFF, 0xFF, 0x02, 0x0B, 0x0D};
      pRemoteChar->writeValue(pingPacket, sizeof(pingPacket));
    }
    xSemaphoreGive(bleMutex);
  }
}

void robotNotifyCallback(BLERemoteCharacteristic* pChar, uint8_t* pData, size_t length, bool isNotify) {
  if (length >= 6 && pData[0] == 0xFF && pData[1] == 0xFF) {
    uint8_t opcode = pData[3];
    if (opcode == 0x0F && length >= 12) {
      // 0x0F Telemetry packet: payload starts at pData[4]
      // payload[0] = pattern (pData[4])
      // payload[1] = battery % (pData[5])
      // payload[2] = volume (pData[6])
      // payload[3] = progress (pData[7])
      // payload[4] = autoStand (pData[8])
      // payload[5] = autoTurn (pData[9])
      // payload[6] = autoPose (pData[10])
      // payload[7] = autoOff (pData[11])
      uint8_t bat = pData[5];
      if (bat <= 100) {
        int oldBat = robotBatteryPercent;
        robotBatteryPercent = (int)bat;
        hasRobotBattery = true;
        robotSpeakerVolume = pData[6];
        robotAutoStand = (pData[8] != 0);
        if (oldBat != robotBatteryPercent) {
          Serial.printf("\n[ROBOT TELEMETRY] 🔋 Robot Battery: %d%% | Volume: %d/140 | AutoStand: %s\n",
                        robotBatteryPercent, robotSpeakerVolume, robotAutoStand ? "ON" : "OFF");
          requestEInkFullUpdate();
        }
      }
    }
  }
}

// ==============================================================================
// 5. DIRECT PERSISTENT BLE CONNECTION MANAGER (FAST 1s NON-BLOCKING SCAN CHECK)
// ==============================================================================
bool connectToRobot(bool quietBg) {
  if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    if (!quietBg) Serial.println("[BLE STATUS] ⚠️ No robot paired in NVS flash. Hold Start for 3s to pair.");
    updateStatusLED();
    return false;
  }

  // If already connected with valid characteristic handle, do nothing
  if (isConnected && pClient != nullptr && pClient->isConnected() && pRemoteChar != nullptr) {
    return true;
  }

  if (!quietBg) {
    setStatusLED(40, 30, 0); // 🟡 Yellow: Active foreground connecting
  }

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

  // Subscribe to robot telemetry notifications (battery, volume, status)
  if (pRemoteChar->canNotify()) {
    pRemoteChar->registerForNotify(robotNotifyCallback);
    Serial.println("[BLE STATUS] 📡 Subscribed to Robot Telemetry Notifications (0xFFE1).");
  }

  isConnected = true;
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.printf("║  [BLE STATUS: CONNECTED] Target: %-38s║\n", pairedName.c_str());
  Serial.println("║  Persistent link ACTIVE! Ready for instant commands.                   ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
  updateStatusLED();
  queryRobotStateNonBlocking();
  return true;
}

// ==============================================================================
// 5.1 NON-BLOCKING CONFIG DOCK (UART1) & RUN PORT (UART2) POLLING ENGINE
// ==============================================================================
void enforcePortModeLock() {
  // Never interrupt active chain execution or teacher BLE pairing
  if (currentState == STATE_RUNNING ||
      currentState == STATE_BLE_SCANNING ||
      currentState == STATE_BLE_PAIRING_MENU) {
    return;
  }

  if (hasAnyBlockConnected()) {
    // At least one port (Config Port or Run Port) has an Action Block connected:
    // Strictly lock to Mode 1 (STATE_ACTION_MENU)
    if (currentState != STATE_ACTION_MENU) {
      if (currentState == STATE_REMOTE_CONTROL && currentRcMotion != RC_MOTION_IDLE) {
        stopRcMotionImmediate();
      }
      currentState = STATE_ACTION_MENU;
      triggerLedBlip(0, 80, 40); // Emerald Green
      updateStatusLED();
      Serial.printf("\n[MODE LOCK] 🔒 Block detected (%s) -> Auto-switched & locked to Mode 1!\n",
                    isBlockDocked ? "Config Port" : "Run Port");
      renderActionMenu();
    }
  } else {
    // Neither Config Port nor Run Port has any block connected:
    // Mode 1 is hidden; automatically switch out of Mode 1 into Mode 2 (Remote Control)
    if (currentState == STATE_ACTION_MENU) {
      currentState = STATE_REMOTE_CONTROL;
      triggerLedBlip(0, 100, 100); // Vivid Teal
      updateStatusLED();
      Serial.println("\n[MODE LOCK] 🔓 No blocks connected -> Hiding Mode 1, switched to Mode 2 (RC)!");
      renderRemoteControlMenu();
    }
  }
}

void pollConfigDock() {
  if (currentState == STATE_RUNNING ||
      currentState == STATE_BLE_SCANNING ||
      currentState == STATE_BLE_PAIRING_MENU) {
    return;
  }
  if (currentState == STATE_REMOTE_CONTROL && currentRcMotion != RC_MOTION_IDLE) {
    return; // Pause UART polling while actively driving robot in RC mode
  }

  unsigned long now = millis();

  // 1. Non-blocking state-machine parser for incoming UART1 (Config Port) bytes
  while (Serial1.available() > 0) {
    uint8_t b = (uint8_t)Serial1.read();
    cfgRxLastByteMs = now;

    if (cfgRxIdx == 0) {
      if (b == 0xCF) {
        cfgRxBuf[cfgRxIdx++] = b;
      }
      continue;
    }

    cfgRxBuf[cfgRxIdx++] = b;
    uint8_t cmd = cfgRxBuf[1];

    if (cmd == 0x81) {
      // Query Response: [0xCF, 0x81, ActionID, ParamVal, CRC8, 0x55] (6 bytes)
      if (cfgRxIdx >= 6) {
        uint8_t act    = cfgRxBuf[2];
        uint8_t par    = cfgRxBuf[3];
        uint8_t rxCrc  = cfgRxBuf[4];
        uint8_t footer = cfgRxBuf[5];
        cfgRxIdx = 0;

        uint8_t checkPayload[3] = { 0x81, act, par };
        uint8_t calcCrc = calcCrc8(checkPayload, 3);
        if (calcCrc == rxCrc && footer == 0x55) {
          bool newlyDocked = !isBlockDocked;
          bool storedConfigChanged = (dockedActionId != act || dockedParamVal != par);
          isBlockDocked = true;
          dockedActionId = act;
          dockedParamVal = par;
          lastDockResponseTime = now;

          if (newlyDocked || storedConfigChanged) {
            syncMenuToDockedBlock(act, par);
            Serial.printf("\n[CONFIG DOCK] 🟢 Action Block detected: Token 0x%02X (%s, %d %s)\n",
                          dockedActionId, getActionNameByToken(dockedActionId),
                          dockedParamVal, getParamUnitByToken(dockedActionId));
            bool wasInMode1 = (currentState == STATE_ACTION_MENU);
            enforcePortModeLock();
            if (wasInMode1 && currentState == STATE_ACTION_MENU) {
              renderActionMenu();
            }
          }
        } else {
          Serial.printf("\n[DOCK CRC ERROR] Act=0x%02X Par=%d CRC=0x%02X (calc=0x%02X) Footer=0x%02X\n",
                        act, par, rxCrc, calcCrc, footer);
        }
      }
    } else if (cmd == 0x06) {
      // ACK Response: [0xCF, 0x06, CRC8, 0x55] (4 bytes)
      if (cfgRxIdx >= 4) {
        uint8_t rxCrc  = cfgRxBuf[2];
        uint8_t footer = cfgRxBuf[3];
        cfgRxIdx = 0;
        uint8_t ackPayload[1] = { 0x06 };
        if (calcCrc8(ackPayload, 1) == rxCrc && footer == 0x55) {
          lastDockResponseTime = now;
          Serial.println("\n[CONFIG DOCK] 💾 Flash Write Confirmed! (ACK 0x06 received from Block)");
          triggerLedBlip(0, 180, 40);
          // Immediately query block to refresh stored state
          uint8_t queryPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
          Serial1.write(queryPkt, 4);
          lastConfigPollTime = now;
        }
      }
    } else {
      // Unrecognized command byte; restart frame if byte itself is 0xCF
      if (b == 0xCF) {
        cfgRxBuf[0] = 0xCF;
        cfgRxIdx = 1;
      } else {
        cfgRxIdx = 0;
      }
    }
  }

  if (cfgRxIdx > 0 && (now - cfgRxLastByteMs > 60)) {
    cfgRxIdx = 0; // Reset partial frame on inter-byte timeout
  }

  // 2. Timeout check: if no query response received within CONFIG_TIMEOUT_MS, mark block as undocked
  if (isBlockDocked && (now - lastDockResponseTime > CONFIG_TIMEOUT_MS)) {
    isBlockDocked = false;
    dockedActionId = 0;
    dockedParamVal = 0;
    Serial.println("\n[CONFIG DOCK] ⚪ Action Block undocked / disconnected.");
    enforcePortModeLock();
    if (currentState == STATE_ACTION_MENU) {
      // Still in Mode 1 because Run Chain is connected -> switch UI to Run Mode!
      renderActionMenu();
    }
  }

  // 3. Periodic non-blocking query ping
  if (now - lastConfigPollTime >= CONFIG_POLL_INTERVAL_MS) {
    lastConfigPollTime = now;
    uint8_t queryPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
    Serial1.write(queryPkt, 4);
  }
}

void pollRunChainPort() {
  if (currentState == STATE_RUNNING ||
      currentState == STATE_BLE_SCANNING ||
      currentState == STATE_BLE_PAIRING_MENU) {
    return;
  }
  if (currentState == STATE_REMOTE_CONTROL && currentRcMotion != RC_MOTION_IDLE) {
    return; // Pause UART polling while actively driving robot in RC mode
  }

  unsigned long now = millis();

  // 1. Non-blocking state-machine parser for incoming UART2 (Run Port Return Rail) bytes
  while (ChainSerial.available() > 0) {
    uint8_t b = (uint8_t)ChainSerial.read();
    chainRxLastByteMs = now;

    if (chainRxHeaderIdx == 0) {
      if (b == 0xAA) {
        chainRxHeaderBuf[0] = 0xAA;
        chainRxHeaderIdx = 1;
        chainRxPayloadIdx = 0;
      }
      continue;
    } else if (chainRxHeaderIdx < 3) {
      chainRxHeaderBuf[chainRxHeaderIdx++] = b;
      if (chainRxHeaderIdx == 3) {
        uint8_t len   = chainRxHeaderBuf[1];
        uint8_t count = chainRxHeaderBuf[2];
        // Require at least 1 Action Block (count >= 1) and valid dimensions
        if (count == 0 || len != count * 2 || len > 60) {
          chainRxHeaderIdx = 0;
          chainRxPayloadIdx = 0;
        }
      }
      continue;
    }

    uint8_t len   = chainRxHeaderBuf[1];
    uint8_t count = chainRxHeaderBuf[2];
    chainRxPayloadBuf[chainRxPayloadIdx++] = b;

    if (chainRxPayloadIdx >= (uint8_t)(len + 2)) {
      uint8_t rxCrc  = chainRxPayloadBuf[len];
      uint8_t footer = chainRxPayloadBuf[len + 1];
      chainRxHeaderIdx = 0;
      chainRxPayloadIdx = 0;

      uint8_t checkBuf[64];
      checkBuf[0] = len;
      checkBuf[1] = count;
      for (uint8_t i = 0; i < len; i++) {
        checkBuf[2 + i] = chainRxPayloadBuf[i];
      }
      uint8_t calcCrc = calcCrc8(checkBuf, 2 + len);

      if (calcCrc == rxCrc && footer == 0x55) {
        bool newlyConnected = !isRunChainConnected;
        bool chainChanged = (detectedChainCount != (int)count ||
                             memcmp(detectedChainBuf, chainRxPayloadBuf, len) != 0);
        isRunChainConnected = true;
        detectedChainCount = (int)count;
        memcpy(detectedChainBuf, chainRxPayloadBuf, len);
        lastChainResponseTime = now;

        if (newlyConnected || chainChanged) {
          Serial.printf("\n[RUN PORT] 🟢 Action Block Chain detected: %d Block(s) ready!\n", detectedChainCount);
          bool wasInMode1 = (currentState == STATE_ACTION_MENU);
          enforcePortModeLock();
          if (wasInMode1 && currentState == STATE_ACTION_MENU && !isBlockDocked) {
            renderActionMenu();
          }
        }
      }
    }
  }

  if (chainRxHeaderIdx > 0 && (now - chainRxLastByteMs > 120)) {
    chainRxHeaderIdx = 0;
    chainRxPayloadIdx = 0;
  }

  // 2. Timeout check: if no valid chain loopback received within CHAIN_TIMEOUT_MS, mark disconnected
  if (isRunChainConnected && (now - lastChainResponseTime > CHAIN_TIMEOUT_MS)) {
    isRunChainConnected = false;
    detectedChainCount = 0;
    Serial.println("\n[RUN PORT] ⚪ Action Block Chain disconnected.");
    enforcePortModeLock();
    if (currentState == STATE_ACTION_MENU) {
      renderActionMenu();
    }
  }

  // 3. Periodic non-blocking discovery seed ping
  if (now - lastChainPollTime >= CHAIN_POLL_INTERVAL_MS) {
    lastChainPollTime = now;
    uint8_t seedPkt[5] = { 0xAA, 0x00, 0x00, 0x00, 0x55 };
    ChainSerial.write(seedPkt, 5);
  }
}

// ==============================================================================
// 6. HARDWARE SETUP
// ==============================================================================
void printEInkAndPowerDiagnostics() {
  uint32_t rawMv = 0;
  float rawVbat = sampleRawBatteryVoltage(&rawMv);
  float filtVbat = readBatteryVoltage();
  int batPct = calculateBatteryPercent(filtVbat);

  pinMode(PIN_EPD_BUSY, INPUT_PULLDOWN);
  delayMicroseconds(100);
  int busyPullDown = digitalRead(PIN_EPD_BUSY);

  pinMode(PIN_EPD_BUSY, INPUT_PULLUP);
  delayMicroseconds(100);
  int busyPullUp = digitalRead(PIN_EPD_BUSY);

  // Restore INPUT for healthy BUSY pin, or INPUT_PULLDOWN if bypassed
  pinMode(PIN_EPD_BUSY, display.epd2.isBusyBypassed() ? INPUT_PULLDOWN : INPUT);
  int resState = digitalRead(PIN_EPD_RES);

  const char* busyDiag = "ACTIVE LOW (READY - HEALTHY)";
  if (busyPullDown == LOW && busyPullUp == HIGH) {
    busyDiag = "FLOATING / OPEN WIRE (Gray GPIO 4 disconnected!)";
  } else if (busyPullDown == HIGH && busyPullUp == HIGH) {
    busyDiag = "STUCK HIGH (SSD1680 busy/locked or shorted high!)";
  }

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║              [HARDWARE & E-INK DIAGNOSTIC TELEMETRY]                   ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.printf("║  • Master Battery (GPIO 1) : %1.2f V (%3d%%) [Raw: %1.2fV / %4u mV]     ║\n", filtVbat, batPct, rawVbat, rawMv);
  Serial.printf("║  • EPD BUSY Pin   (GPIO 4) : PD=%d, PU=%d -> %-27s ║\n", busyPullDown, busyPullUp, busyDiag);
  Serial.printf("║  • EPD RES Pin    (GPIO 5) : %d (%-38s) ║\n", resState, resState ? "HIGH - Normal Run" : "LOW - Held in Reset!");
  Serial.printf("║  • EPD Mode                : %-42s║\n",
                display.epd2.isBusyBypassed() ? "TIMED FALLBACK (BUSY Bypassed)" : "HARDWARE BUSY (900ms Max Cap)");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
}

void setup() {
  // Immediate visual power-on cue on RGB LED (<50ms from switch flip)
  setStatusLED(30, 15, 0);

  Serial.begin(115200);
  Serial.setTxTimeoutMs(0); // Non-blocking USB CDC: 0ms timeout prevents loop freeze when USB CDC buffer fills
  delay(300);               // Brief 300ms rail stabilization (reduced from 1500ms for fast boot)

  // Configure Internal Pull-Up Resistors for all 4 UI inputs (2 Encoders + 2 Buttons)
  pinMode(PIN_K1_CLK, INPUT_PULLUP);
  pinMode(PIN_K1_DT,  INPUT_PULLUP);
  pinMode(PIN_K1_SW,  INPUT_PULLUP);

  pinMode(PIN_K2_CLK, INPUT_PULLUP);
  pinMode(PIN_K2_DT,  INPUT_PULLUP);
  pinMode(PIN_K2_SW,  INPUT_PULLUP);

  pinMode(PIN_START_BTN, INPUT_PULLUP);
  pinMode(PIN_STOP_BTN,  INPUT_PULLUP);

  // Configure Battery Voltage ADC Pin (ADC1_CH0)
  pinMode(PIN_BATSENSE, INPUT);

  // Attach CHANGE interrupts on both CLK & DT for full Gray-code quadrature decoding
  attachInterrupt(digitalPinToInterrupt(PIN_K1_CLK), isrK1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_K1_DT),  isrK1, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_K2_CLK), isrK2, CHANGE);
  attachInterrupt(digitalPinToInterrupt(PIN_K2_DT),  isrK2, CHANGE);

  // Initialize Config Dock UART (Serial1 on Pins 18 RX, 17 TX @ 115200)
  pinMode(PIN_CFG_RX, INPUT_PULLUP);
  Serial1.begin(115200, SERIAL_8N1, PIN_CFG_RX, PIN_CFG_TX);

  // Initialize Run Chain UART (ChainSerial on Pins 16 RX, 15 TX @ 115200)
  pinMode(PIN_CHAIN_RX, INPUT_PULLUP);
  ChainSerial.begin(115200, SERIAL_8N1, PIN_CHAIN_RX, PIN_CHAIN_TX);

  // Initialize 2.13" E-Ink Display (DEPG0213BN / SSD1680) at 4MHz SPI (matching verified test sketches)
  Serial.println("[SYSTEM] Initializing 2.13\" E-Ink display (SPI SCL=21, SDA=38 @ 4MHz)...");
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));

  // Perform clean hardware reset pulse on SSD1680 display controller
  pinMode(PIN_EPD_RES, OUTPUT);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(15);
  digitalWrite(PIN_EPD_RES, LOW);
  delay(25);
  digitalWrite(PIN_EPD_RES, HIGH);
  delay(60);

  // Pass 0 for serial_diag_bitrate so GxEPD2 never stalls UART TX
  display.init(0, false, 10, false);
  // Re-assert custom SPI pins @ 4MHz after display.init()
  SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
  display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));
  display.setRotation(1); // 250 width x 122 height (Landscape)
  display.setFullWindow();
  display.epd2.setBusyCallback(epdBusyYieldCallback);

  // Check if BUSY pin is floating (open wire) or stuck HIGH while idle after reset;
  // if so, automatically switch to Timed Fallback Mode (_busy = -1) so screen refreshes still work!
  bool busyFaultyAtBoot = display.epd2.detectFaultyBusyPin();
  display.epd2.configureBusyPin(busyFaultyAtBoot);
  printEInkAndPowerDiagnostics();

  // Load Saved Robot Binding from NVS Flash & set initial RGB LED immediately (<200ms from boot)
  preferences.begin("robosen_cfg", false);
  pairedMAC = preferences.getString("paired_mac", "");
  if (pairedMAC == "" || pairedMAC == "None (Unpaired)") {
    pairedMAC = preferences.getString("last_paired_mac", "None (Unpaired)");
  }
  pairedName = preferences.getString("paired_name", "Robosen Robot");
  updateStatusLED();

  // Perform clean initial dual-buffer sync on Core 1 before starting BLE RF activity
  // (Since _busy is bypassed if floating or capped to 900ms, this never hangs boot!)
  epdWaitStartMs = millis();
  display.epd2.writeScreenBufferAgain(0x00); // Preload Previous (0x26) & Current (0x24) as Black
  display.epd2.writeScreenBuffer(0xFF);      // Set Current (0x24) to White
  loadCustomEInkLut(false);                  // PowerOn (0xF8) + load 30-frame symmetric LUT
  display.epd2.refresh(true);                // Drive entire panel Black -> White (~750ms)
  display.epd2.writeScreenBufferAgain(0xFF); // Sync Previous (0x26) & Current (0x24) as White

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

  // Initial port probe on boot: check if a block is already on Config Port or Run Port
  uint8_t initCfgPing[4] = { 0xCF, 0x01, 0x07, 0x55 };
  Serial1.write(initCfgPing, 4);
  uint8_t initChainPing[5] = { 0xAA, 0x00, 0x00, 0x00, 0x55 };
  ChainSerial.write(initChainPing, 5);
  delay(80);
  pollConfigDock();
  pollRunChainPort();

  startBackgroundTasks();
  if (hasAnyBlockConnected()) {
    currentState = STATE_ACTION_MENU;
    updateStatusLED();
    renderActionMenu();
  } else {
    currentState = STATE_REMOTE_CONTROL;
    updateStatusLED();
    renderRemoteControlMenu();
  }
  lastUserActivity = millis();
  lastConnectAttemptTime = millis();
}

// ==============================================================================
// 7. MAIN EVENT LOOP
// ==============================================================================
void loop() {
  unsigned long now = millis();

  // --- 0. LED TACTILE FEEDBACK TIMEOUT ---
  if (ledBlipUntil > 0 && now >= ledBlipUntil) {
    ledBlipUntil = 0;
    updateStatusLED();
  }

  // --- 1. CONFIG DOCK & RUN PORT LIVE DETECTION ENGINE ---
  pollConfigDock();
  pollRunChainPort();

  // --- 1.1 REMOTE CONTROL ENGINE (NON-BLOCKING LOCOMOTION & STEERING MOMENTUM) ---
  updateRemoteControlEngine();

  // Serial Monitor Interactive Test ('t' = Ping Config Dock, 'r' = Run Chain, 'f' = Reinit E-Ink, 'd' = Diagnostics)
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
    } else if (c == 'f' || c == 'F') {
      Serial.println("\n[E-INK TEST] Queuing hardware reset + Dual-Buffer E-Ink Sync Refresh on Core 0...");
      einkForceReinit = true;
    } else if (c == 'd' || c == 'D') {
      printEInkAndPowerDiagnostics();
    }
  }

  // --- 2. ROTARY ENCODER DELTA PROCESSING (INTERRUPT-DRIVEN) ---
  int d1 = 0, d2 = 0;
  if (k1Delta != 0 || k2Delta != 0) {
    noInterrupts();
    d1 = k1Delta; k1Delta = 0;
    d2 = k2Delta; k2Delta = 0;
    interrupts();
  }

  if (d1 != 0) {
    lastUserActivity = now;

    if (currentState == STATE_ACTION_MENU) {
      // In Mode 1, Knob 1 only adjusts Action selection when a block is on the Config Port (Config Mode)
      if (isBlockDocked) {
        triggerLedBlip(0, 80, 80); // Cyan tactile feedback
        currentActionIndex = (currentActionIndex + d1) % TOTAL_ACTIONS;
        while (currentActionIndex < 0) currentActionIndex += TOTAL_ACTIONS;
        requestEInkCenterUpdate(); // Targeted middle-band fast update on Core 0
        Serial.printf("🔄 [KNOB 1] Action: %s\n", ACTIONS[currentActionIndex].name);
      }
    } else if (currentState == STATE_REMOTE_CONTROL) {
      triggerLedBlip(0, 80, 80);
      // Knob 1 Turn: Live Rotational Steering (Turn Left / Right)
      RcActiveMotion newMotion = (d1 < 0) ? RC_MOTION_TURN_LEFT : RC_MOTION_TURN_RIGHT;
      uint8_t op = (d1 < 0) ? 0x08 : 0x02;
      currentRcMotion = newMotion;
      unsigned long dur = (d1 < 0) ? 550 : 900;
      unsigned long maxWindow = (d1 < 0) ? 1100 : 1500;
      rcSteerActiveUntilMs = constrain(now + dur, rcSteerActiveUntilMs + 400, now + maxWindow);
      sendRawOpcodeNonBlocking(op);
      updateStatusLED();
      Serial.printf("🔄 [RC STEER] Turn %s\n", (d1 < 0) ? "Left" : "Right");
    } else if (currentState == STATE_JOINT_CONTROL) {
      triggerLedBlip(0, 80, 80);
      currentJointIndex = (currentJointIndex + d1) % TOTAL_JOINTS;
      while (currentJointIndex < 0) currentJointIndex += TOTAL_JOINTS;
      requestEInkCenterUpdate();
      Serial.printf("🔄 [JOINT SELECT] %d: %s (ID %d)\n", currentJointIndex + 1, ALL_JOINTS[currentJointIndex].name, ALL_JOINTS[currentJointIndex].servoId);
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      triggerLedBlip(0, 80, 80);
      currentBleIndex = (currentBleIndex + d1) % bleDeviceCount;
      while (currentBleIndex < 0) currentBleIndex += bleDeviceCount;
      requestEInkFullUpdate();
      Serial.printf("🔄 [BLE LIST] %d: %s\n", currentBleIndex + 1, bleList[currentBleIndex].name.c_str());
    }
  }

  if (d2 != 0) {
    lastUserActivity = now;

    if (currentState == STATE_ACTION_MENU) {
      // In Mode 1, Knob 2 only adjusts Parameter when a block is on the Config Port (Config Mode)
      if (isBlockDocked) {
        triggerLedBlip(80, 0, 80); // Magenta tactile feedback
        RobosenAction& act = ACTIONS[currentActionIndex];
        act.paramVal += (d2 * act.paramStep);
        if (act.paramVal > act.paramMax) act.paramVal = act.paramMax;
        if (act.paramVal < act.paramMin) act.paramVal = act.paramMin;
        requestEInkCenterUpdate(); // Targeted middle-band fast update on Core 0
        Serial.printf("🔄 [KNOB 2] Parameter: %d %s\n", act.paramVal, act.paramUnit);
      }
    } else if (currentState == STATE_REMOTE_CONTROL) {
      triggerLedBlip(80, 0, 80);
      // Knob 2 Turn: Scroll Actions Catalog (exclusively stunts: Punch, Push-ups, Wave)
      rcActionIndex = (rcActionIndex + d2) % TOTAL_RC_ACTIONS;
      while (rcActionIndex < 0) rcActionIndex += TOTAL_RC_ACTIONS;
      requestEInkCenterUpdate(); // Fast middle band refresh on Core 0
      Serial.printf("🔄 [RC ACTION] %s\n", RC_ACTIONS[rcActionIndex].name);
    } else if (currentState == STATE_JOINT_CONTROL) {
      triggerLedBlip(80, 0, 80);
      const JointDef& j = ALL_JOINTS[currentJointIndex];
      int newPos = (int)currentServoPositions[j.servoId] + (d2 * 5);
      newPos = constrain(newPos, (int)j.minLimit, (int)j.maxLimit);
      currentServoPositions[j.servoId] = (uint8_t)newPos;
      if (now - lastJointBleSendMs >= 45) {
        lastJointBleSendMs = now;
        sendJointFrameNonBlocking(25);
      }
      requestEInkCenterUpdate();
      int degOffset = (int)currentServoPositions[j.servoId] - (int)j.neutral;
      Serial.printf("🔄 [JOINT ANGLE] %s: %d (offset %+d°)\n",
                    j.name, currentServoPositions[j.servoId], degOffset);
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      triggerLedBlip(80, 0, 80);
      currentBleIndex = (currentBleIndex + d2) % bleDeviceCount;
      while (currentBleIndex < 0) currentBleIndex += bleDeviceCount;
      requestEInkFullUpdate();
      Serial.printf("🔄 [BLE LIST] %d: %s\n", currentBleIndex + 1, bleList[currentBleIndex].name.c_str());
    }
  }

  // --- 3. KNOB 1 SWITCH (GPIO 10 - ACTIVE LOW: DIRECT MODE CYCLE) ---
  int k1SwRaw = digitalRead(PIN_K1_SW);
  static int lastK1SwRaw = HIGH;
  static unsigned long lastK1SwDebounce = 0;
  static bool k1SwPressed = false;

  if (k1SwRaw != lastK1SwRaw) {
    lastK1SwDebounce = now;
    lastK1SwRaw = k1SwRaw;
  }
  if (now - lastK1SwDebounce > 25) {
    if (k1SwRaw == LOW && !k1SwPressed) {
      k1SwPressed = true;
      lastUserActivity = now;

      if (currentState == STATE_ACTION_MENU) {
        // Strictly locked to Mode 1 while any block is connected to Config Port or Run Port
        if (hasAnyBlockConnected()) {
          Serial.println("\n[MODE LOCK] 🔒 Locked to Mode 1 while blocks are attached! Remove blocks to access Mode 2/3.");
        } else {
          currentState = STATE_REMOTE_CONTROL;
          triggerLedBlip(0, 100, 100);
          updateStatusLED();
          renderRemoteControlMenu();
        }
      } else if (currentState == STATE_REMOTE_CONTROL) {
        // Mode 2 -> Mode 3 (Joint Control) — Only stop if robot was actively walking
        Serial.println("\n[MODE] ➡️ Switched to Mode 3: Joint Control");
        if (currentRcMotion != RC_MOTION_IDLE) {
          stopRcMotionImmediate();
        }
        currentState = STATE_JOINT_CONTROL;
        triggerLedBlip(0, 60, 120); // Vivid Cyan/Purple
        updateStatusLED();
        renderJointControlMenu();
      } else if (currentState == STATE_JOINT_CONTROL) {
        // When no blocks are attached, Mode 1 is hidden -> cycle Mode 3 directly back to Mode 2 (RC)!
        if (hasAnyBlockConnected()) {
          Serial.println("\n[MODE] ➡️ Switched to Mode 1: Block Coding & Dock");
          currentState = STATE_ACTION_MENU;
          triggerLedBlip(0, 80, 40); // Emerald Green
          updateStatusLED();
          renderActionMenu();
        } else {
          Serial.println("\n[MODE] ➡️ Switched to Mode 2: Remote Control (RC) (Mode 1 hidden while no blocks attached)");
          currentState = STATE_REMOTE_CONTROL;
          triggerLedBlip(0, 100, 100); // Vivid Teal
          updateStatusLED();
          renderRemoteControlMenu();
        }
      } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
        pairedMAC  = bleList[currentBleIndex].address;
        pairedName = bleList[currentBleIndex].name;
        preferences.putString("paired_mac", pairedMAC);
        preferences.putString("paired_name", pairedName);
        connectAttemptCounter = 0;
        if (hasAnyBlockConnected()) {
          currentState = STATE_ACTION_MENU;
          renderActionMenu();
        } else {
          currentState = STATE_REMOTE_CONTROL;
          renderRemoteControlMenu();
        }
        requestBgReconnect = true;
      }
    } else if (k1SwRaw == HIGH && k1SwPressed) {
      k1SwPressed = false;
      lastUserActivity = now;
    }
  }

  // --- 4. KNOB 2 SWITCH (GPIO 13 - ACTIVE LOW: SHORT CLICK ZERO, 1.5s HOLD STAND) ---
  int k2SwRaw = digitalRead(PIN_K2_SW);
  static int lastK2SwRaw = HIGH;
  static unsigned long lastK2SwDebounce = 0;
  static bool k2SwPressed = false;
  static unsigned long k2SwPressStart = 0;
  static bool k2SwHeld1500ms = false;

  if (k2SwRaw != lastK2SwRaw) {
    lastK2SwDebounce = now;
    lastK2SwRaw = k2SwRaw;
  }
  if (now - lastK2SwDebounce > 25) {
    if (k2SwRaw == LOW && !k2SwPressed) {
      k2SwPressed = true;
      k2SwPressStart = now;
      k2SwHeld1500ms = false;
      lastUserActivity = now;
      if (currentState != STATE_ACTION_MENU || isBlockDocked) {
        triggerLedBlip(80, 0, 80); // Magenta
      }
    } else if (k2SwRaw == LOW && k2SwPressed) {
      lastUserActivity = now;
      if (!k2SwHeld1500ms && (now - k2SwPressStart >= 1500)) {
        k2SwHeld1500ms = true;
        if (currentState == STATE_JOINT_CONTROL) {
          Serial.println("\n[SYSTEM] 🎯 1.5-Second Knob 2 Hold: Resetting all servos to Standing Posture!");
          resetAllJointsToStand();
        }
      }
    } else if (k2SwRaw == HIGH && k2SwPressed) {
      k2SwPressed = false;
      lastUserActivity = now;
      unsigned long heldDuration = now - k2SwPressStart;
      if (!k2SwHeld1500ms && heldDuration >= 20 && heldDuration < 1500) {
        if (currentState == STATE_ACTION_MENU) {
          if (isBlockDocked) {
            RobosenAction& act = ACTIONS[currentActionIndex];
            act.paramVal = act.paramMin;
            Serial.printf("\n>>> [KNOB 2 CLICK] Reset %s Parameter to %d %s <<<\n", 
                          act.name, act.paramVal, act.paramUnit);
            requestEInkCenterUpdate();
          }
        } else if (currentState == STATE_REMOTE_CONTROL) {
          // Fire Selected Stunt Action Instantly
          if (currentRcMotion != RC_MOTION_IDLE && currentRcMotion != RC_MOTION_STUNT) {
            sendLocomotionStop();
            delay(40);
          }
          currentRcMotion = RC_MOTION_STUNT;
          const RcActionItem& act = RC_ACTIONS[rcActionIndex];
          sendStuntPacketNonBlocking(act.opcode, act.payload);
          rcStuntEndMs = now + act.durationMs;
          triggerLedBlip(90, 0, 90);
          updateStatusLED();
          Serial.printf("\n>>> [RC ACTION] Fired: %s (Duration: %lu ms) <<<\n",
                        act.name, act.durationMs);
        } else if (currentState == STATE_JOINT_CONTROL) {
          // Reset active joint to neutral center (0°)
          resetActiveJointToCenter();
        }
      }
    }
  }

  // --- 5. MASTER START / CONFIRM BUTTON (SW3 - GPIO 14: 3s HOLD FOR PAIRING) ---
  int startRaw = digitalRead(PIN_START_BTN);
  static int lastStartRaw = HIGH;
  static unsigned long lastStartDebounce = 0;
  static bool startBtnPressed = false;
  static unsigned long startPressStart = 0;
  static bool startBtnHeld3s = false;

  if (startRaw != lastStartRaw) {
    lastStartDebounce = now;
    lastStartRaw = startRaw;
  }

  if (now - lastStartDebounce > 25) {
    if (startRaw == LOW && !startBtnPressed) {
      startBtnPressed = true;
      startPressStart = now;
      startBtnHeld3s = false;
      lastUserActivity = now;
      triggerLedBlip(0, 100, 0); // Green
      if (currentState != STATE_REMOTE_CONTROL) {
        Serial.println("\n[BUTTON] Start button pressed... (Hold 3s to switch robot)");
      }
    } else if (startRaw == LOW && startBtnPressed) {
      lastUserActivity = now;
      if (!startBtnHeld3s && (now - startPressStart >= 3000)) {
        if (currentState == STATE_ACTION_MENU || currentState == STATE_JOINT_CONTROL) {
          startBtnHeld3s = true;
          Serial.println("\n[SYSTEM] 🎯 3-Second Hold Confirmed! Opening Teacher Pairing Menu...");
          runBleScan();
        }
      }
    } else if (startRaw == HIGH && startBtnPressed) {
      startBtnPressed = false;
      lastUserActivity = now;
      unsigned long heldDuration = now - startPressStart;
      if (!startBtnHeld3s && heldDuration >= 20 && heldDuration < 3000) {
        if (currentState == STATE_ACTION_MENU) {
          if (isBlockDocked) {
            // CONFIG MODE: Only flash docked block on Config Port; running chain is blocked while docked!
            RobosenAction& act = ACTIONS[currentActionIndex];
            Serial.printf("\n>>> [CONFIG DOCK] Flashing '%s' (%d %s) into docked Action Block via Green Button... <<<\n",
                          act.name, act.paramVal, act.paramUnit);
            writeConfigToDockedBlock(act.tokenID, (uint8_t)act.paramVal);
            triggerLedBlip(0, 80, 40);
          } else if (isRunChainConnected) {
            // RUN MODE: Config Port is empty and Run Port chain is connected -> Run Chain!
            Serial.println("\n[SYSTEM] Start button clicked in Run Mode: Initiating Run Chain (GPIO 15/16)...");
            if (!executeRunChain()) {
              Serial.println("\n[SYSTEM] ⚠️ Chain execution aborted: No valid return packet received from return rail!");
              setStatusLED(50, 0, 0);
              delay(500);
              updateStatusLED();
              setUiEventFeedback("START: NO CHAIN BLOCKS!");
            }
          }
        } else if (currentState == STATE_REMOTE_CONTROL) {
          if (!isConnected && pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
            Serial.println("[BLE STATUS] ⚡ Green Start clicked while disconnected in RC Mode: Triggering background reconnect...");
            requestBgReconnect = true;
            setUiEventFeedback("CONNECTING...");
          }
        } else if (currentState == STATE_JOINT_CONTROL) {
          if (!isConnected && pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
            Serial.println("[BLE STATUS] ⚡ Green Start clicked while disconnected in Joint Mode: Triggering background reconnect...");
            requestBgReconnect = true;
            setUiEventFeedback("CONNECTING...");
          } else {
            sendJointFrameNonBlocking(25);
            triggerLedBlip(0, 80, 40);
            const JointDef& j = ALL_JOINTS[currentJointIndex];
            Serial.printf("\n[GREEN CONFIRM] Confirmed angle for %s (ID %d: %d deg)\n",
                          j.name, j.servoId, currentServoPositions[j.servoId]);
            updateStatusLED();
            requestEInkCenterUpdate();
          }
        } else if (currentState == STATE_BLE_PAIRING_MENU) {
          if (bleDeviceCount > 0) {
            pairedMAC  = bleList[currentBleIndex].address;
            pairedName = bleList[currentBleIndex].name;
            preferences.putString("paired_mac", pairedMAC);
            preferences.putString("paired_name", pairedName);
            Serial.printf("\n[BLE STATUS] 🟢 Confirmed robot via Start Button: %s (%s)\n", pairedName.c_str(), pairedMAC.c_str());
          }
          if (hasAnyBlockConnected()) {
            currentState = STATE_ACTION_MENU;
            renderActionMenu();
          } else {
            currentState = STATE_REMOTE_CONTROL;
            renderRemoteControlMenu();
          }
          if (pairedMAC != "None (Unpaired)" && !isConnected) {
            requestBgReconnect = true;
          } else {
            updateStatusLED();
          }
        }
      }
    }
  }

  // --- 6. MASTER STOP / CANCEL BUTTON (SW5 - GPIO 2: 3s HOLD FOR DISCONNECT) ---
  int stopRaw = digitalRead(PIN_STOP_BTN);
  static int lastStopRaw = HIGH;
  static unsigned long lastStopDebounce = 0;
  static bool stopBtnPressed = false;
  static unsigned long stopPressStart = 0;
  static bool stopBtnHeld3s = false;

  if (stopRaw != lastStopRaw) {
    lastStopDebounce = now;
    lastStopRaw = stopRaw;
  }

  if (now - lastStopDebounce > 25) {
    if (stopRaw == LOW && !stopBtnPressed) {
      stopBtnPressed = true;
      stopPressStart = now;
      stopBtnHeld3s = false;
      lastUserActivity = now;
      triggerLedBlip(100, 0, 0); // Red
      if (currentState != STATE_REMOTE_CONTROL) {
        Serial.println("\n[BUTTON] Red Stop/Cancel button pressed... (Hold 3s to disconnect BLE)");
      }
    } else if (stopRaw == LOW && stopBtnPressed) {
      lastUserActivity = now;
      if (currentState != STATE_REMOTE_CONTROL) {
        if (!stopBtnHeld3s && (now - stopPressStart >= 3000)) {
          stopBtnHeld3s = true;
          Serial.println("\n[SYSTEM] 🎯 3-Second Stop Hold Confirmed! Disconnecting BLE session...");
          if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
            if (pClient != nullptr && pClient->isConnected()) {
              pClient->disconnect();
            }
            xSemaphoreGive(bleMutex);
          }
          isConnected = false;
          pRemoteChar = nullptr;
          hasRobotBattery = false;
          robotBatteryPercent = -1;
          setStatusLED(60, 0, 0);
          delay(300);
          updateStatusLED();
        }
      }
    } else if (stopRaw == HIGH && stopBtnPressed) {
      stopBtnPressed = false;
      lastUserActivity = now;
      unsigned long heldDuration = now - stopPressStart;
      if (!stopBtnHeld3s && heldDuration >= 20 && heldDuration < 3000) {
        if (currentState == STATE_ACTION_MENU) {
          if (isBlockDocked) {
            // Revert unsaved Knob 1/2 edits back to the docked block's stored configuration
            syncMenuToDockedBlock(dockedActionId, dockedParamVal);
            Serial.printf("\n[REVERT] Reverted Config UI to docked block's stored config: 0x%02X (%s, %d %s)\n",
                          dockedActionId, getActionNameByToken(dockedActionId),
                          dockedParamVal, getParamUnitByToken(dockedActionId));
            requestEInkCenterUpdate();
          } else {
            Serial.println("\n[EMERGENCY STOP] Red Stop button pressed: Sending locomotion stop to lock posture!");
            sendLocomotionStop();
            setStatusLED(80, 0, 0);
            delay(200);
            updateStatusLED();
            setUiEventFeedback("STOP: EMERGENCY HALT!");
          }
        } else if (currentState == STATE_REMOTE_CONTROL) {
          if (!isConnected && pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
            Serial.println("[BLE STATUS] ⚡ Red button clicked while disconnected in RC Mode: Triggering background reconnect...");
            requestBgReconnect = true;
            setUiEventFeedback("CONNECTING...");
          }
        } else if (currentState == STATE_JOINT_CONTROL) {
          Serial.println("\n[EMERGENCY STOP] Red Stop button pressed in Joint Mode: Sending locomotion stop!");
          sendLocomotionStop();
          setStatusLED(80, 0, 0);
          delay(100);
          updateStatusLED();
          setUiEventFeedback("JOINT: EMERGENCY STOP");
        } else if (currentState == STATE_BLE_PAIRING_MENU || currentState == STATE_BLE_SCANNING) {
          Serial.println("\n[CANCEL] Cancelled pairing/scan, returning to active operational mode.");
          if (hasAnyBlockConnected()) {
            currentState = STATE_ACTION_MENU;
            renderActionMenu();
          } else {
            currentState = STATE_REMOTE_CONTROL;
            renderRemoteControlMenu();
          }
          updateStatusLED();
        }
      }
    }
  }

  // --- 7. BACKGROUND HYBRID HEARTBEAT & TELEMETRY QUERY (WHEN CONNECTED & IDLE) ---
  if ((currentState == STATE_ACTION_MENU || (currentState == STATE_REMOTE_CONTROL && currentRcMotion == RC_MOTION_IDLE) || currentState == STATE_JOINT_CONTROL) && isConnected) {
    if (now - lastHeartbeatTime >= 3000) {
      lastHeartbeatTime = now;
      static uint8_t heartbeatCounter = 0;
      heartbeatCounter++;
      // Every cycle (3s): query live battery and state (Opcode 0x0F)
      queryRobotStateNonBlocking();
      // Every other cycle (6s) or if telemetry unread: send proven Opcode 0x0B Ping from main
      if ((heartbeatCounter % 2 == 0) || !hasRobotBattery) {
        sendHeartbeatPingNonBlocking();
      }
    }
  }

  // --- 8. PERIODIC MASTER BATTERY HEADER REFRESH (EVERY 3s WHEN IDLE) ---
  if (now - lastMasterBatCheckMs >= 3000) {
    lastMasterBatCheckMs = now;
    int currentMasterPct = calculateBatteryPercent(readBatteryVoltage());
    if (lastDisplayedMasterPct < 0) {
      lastDisplayedMasterPct = currentMasterPct;
    } else if (abs(currentMasterPct - lastDisplayedMasterPct) >= 4 && (now - lastUserActivity >= 1000)) {
      lastDisplayedMasterPct = currentMasterPct;
      if (currentState == STATE_ACTION_MENU || currentState == STATE_REMOTE_CONTROL || currentState == STATE_JOINT_CONTROL) {
        requestEInkFullUpdate();
      }
    }
  }

  delay(1); // Yield 1ms for ultra-responsive >500Hz input/LED polling
}

// ==============================================================================
// 8. BUILD & TRANSMIT PARAMETERIZED ROBOSEN PACKET (PERSISTENT CONNECTION)
// ==============================================================================
bool writeBlePacketLocked(const uint8_t* data, size_t len) {
  bool sent = false;
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(100)) == pdTRUE) {
    if (isConnected && pRemoteChar != nullptr && pRemoteChar->canWrite()) {
      pRemoteChar->writeValue((uint8_t*)data, len);
      sent = true;
    }
    xSemaphoreGive(bleMutex);
  }
  return sent;
}

bool sendRobosenPacket(const RobosenAction& action) {
  if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    Serial.println("\n[BLE STATUS] ⚠️ No robot paired! Hold Start for 3s to pair.");
    setStatusLED(40, 0, 0);
    delay(500);
    updateStatusLED();
    return false;
  }

  // Re-establish link if connection was lost (synchronized via bleMutex)
  if (!isConnected || pClient == nullptr || !pClient->isConnected() || pRemoteChar == nullptr) {
    Serial.println("\n[BLE STATUS] ⚡ Connection inactive. Quick scan to connect before dispatch...");
    bool connectedOk = false;
    if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
      connectedOk = connectToRobot();
      xSemaphoreGive(bleMutex);
    }
    if (!connectedOk) {
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
      writeBlePacketLocked(packet, totalPacketLen);
      if (!abortableDelay(turnDurationMs)) return false;

      // IMMEDIATELY Send Locomotion Stop (0x0C) to lock robot at desired angle!
      Serial.print("  ► Locomotion Stop: [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      writeBlePacketLocked(stopPacket, sizeof(stopPacket));
      if (!abortableDelay(1000)) return false; // Allow gait engine to stabilize feet into neutral stand posture
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
      writeBlePacketLocked(packet, totalPacketLen);
      if (!abortableDelay(walkDurationMs)) return false;

      // Send Locomotion Stop (0x0C) to end locomotion
      Serial.print("  ► Locomotion Stop: [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      writeBlePacketLocked(stopPacket, sizeof(stopPacket));
      if (!abortableDelay(1200)) return false; // Allow gait engine to stabilize feet into neutral stand posture
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

        writeBlePacketLocked(packet, totalPacketLen);
        if (!abortableDelay(animDurationMs)) return false;
        if (rep < action.paramVal - 1) {
          if (!abortableDelay(400)) return false; // Inter-repetition settling pause
        }
      }
      Serial.println(">>> [SUCCESS] All action repetitions completed! <<<");

    } else {
      writeBlePacketLocked(packet, totalPacketLen);
      if (!abortableDelay(1000)) return false;
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
      if (!abortableDelay(turnDurationMs)) return false;
      Serial.print("  ► Locomotion Stop (Simulated): [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      if (!abortableDelay(1000)) return false;
      Serial.printf(">>> [SUCCESS] Simulated %s %d Deg° Turn! <<<\n", 
                    (action.opcode == 0x08 ? "Left" : "Right"), action.paramVal);
    } else if (isWalk) {
      unsigned long walkDurationMs = action.paramVal * 1400UL;
      Serial.printf("  ► Locomotion Command (Simulated): [HEX] ");
      for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
      Serial.printf("(Target: %d Steps, Duration: %lu ms)\n", action.paramVal, walkDurationMs);
      if (!abortableDelay(walkDurationMs)) return false;
      Serial.print("  ► Locomotion Stop (Simulated): [HEX] FF FF 02 0C 0E (Gait Stand & Lock)\n");
      if (!abortableDelay(1200)) return false;
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
        if (!abortableDelay(animDurationMs)) return false;
        if (rep < action.paramVal - 1) {
          if (!abortableDelay(400)) return false;
        }
      }
      Serial.println(">>> [SUCCESS] All action repetitions simulated! <<<");
    } else {
      for (int rep = 0; rep < action.paramVal; rep++) {
        Serial.printf("  ► Step/Rep %d of %d (Simulated): [HEX] ", rep + 1, action.paramVal);
        for (int i = 0; i < totalPacketLen; i++) Serial.printf("%02X ", packet[i]);
        Serial.println();
        if (rep < action.paramVal - 1) {
          if (!abortableDelay(800)) return false;
        }
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
void restorePostRunMode(bool redraw = true) {
  chainRxHeaderIdx = 0;
  chainRxPayloadIdx = 0;
  cfgRxIdx = 0;
  unsigned long now = millis();
  if (isRunChainConnected) lastChainResponseTime = now;
  if (isBlockDocked) lastDockResponseTime = now;
  lastChainPollTime = 0;
  lastConfigPollTime = 0;

  currentState = hasAnyBlockConnected() ? STATE_ACTION_MENU : STATE_REMOTE_CONTROL;
  updateStatusLED();
  if (redraw) {
    if (currentState == STATE_ACTION_MENU) {
      renderActionMenu();
    } else {
      renderRemoteControlMenu();
    }
  }
}

void triggerChainAbort(int count) {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║  🛑 [EMERGENCY HALT] Run chain aborted by Red Stop Button!             ║");
  Serial.println("║  Turning off all block LEDs and locking robot standing posture...      ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝\n");

  // Broadcast Step 0 (Abort / Turn off all block LEDs)
  uint8_t abortPayload[2] = { 0x00, (uint8_t)count };
  uint8_t abortCrc = calcCrc8(abortPayload, 2);
  uint8_t abortPkt[5] = { 0xBB, 0x00, (uint8_t)count, abortCrc, 0x55 };
  ChainSerial.write(abortPkt, 5);
  ChainSerial.flush();

  // Send Locomotion Stop to robot
  sendLocomotionStop();

  // Flash Red on status LED
  setStatusLED(120, 0, 0);

  // Update E-Ink Display
  updateEInkRunChain(0, count, "HALT / EMERGENCY STOP", 0, "");

  delay(1500);
  restorePostRunMode(true);
}

bool executeRunChain() {
  currentState = STATE_RUNNING;
  updateStatusLED();
  chainRxHeaderIdx = 0;
  chainRxPayloadIdx = 0;

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 [RUN CHAIN ENGINE] PHASE 1: DISCOVERY                  ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ Emitting Discovery Seed [0xAA, 0, 0, 0, 0x55] on GPIO 15 (TX)...       ║");

  // Check if Stop Button is already held
  if (digitalRead(PIN_STOP_BTN) == LOW) {
    Serial.println("║ 🛑 Execution aborted: Red Stop Button pressed.                         ║");
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    restorePostRunMode(false);
    return false;
  }

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
    if (digitalRead(PIN_STOP_BTN) == LOW) {
      Serial.println("║ 🛑 Discovery aborted by Red Stop Button.                               ║");
      Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
      restorePostRunMode(false);
      return false;
    }
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
    restorePostRunMode(false);
    return false;
  }

  // 4. Read Len and Count
  unsigned long t1 = millis();
  while (ChainSerial.available() < 2 && (millis() - t1 < 100)) {
    if (digitalRead(PIN_STOP_BTN) == LOW) {
      restorePostRunMode(false);
      return false;
    }
    delay(1);
  }
  if (ChainSerial.available() < 2) {
    Serial.println("║ ❌ Incomplete response: Timeout waiting for length and count.          ║");
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    restorePostRunMode(false);
    return false;
  }

  uint8_t len = ChainSerial.read();
  uint8_t count = ChainSerial.read();

  if (count == 0 || len != count * 2 || len > 60) {
    Serial.printf("║ ❌ Invalid chain frame dimensions: Len=%d, Count=%d                       ║\n", len, count);
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    restorePostRunMode(false);
    return false;
  }

  // 5. Read payload (len bytes) + CRC8 (1 byte) + Footer (1 byte)
  uint8_t rxBuf[64];
  unsigned long t2 = millis();
  int bytesRead = 0;
  while (bytesRead < (len + 2) && (millis() - t2 < 200)) {
    if (digitalRead(PIN_STOP_BTN) == LOW) {
      restorePostRunMode(false);
      return false;
    }
    if (ChainSerial.available() > 0) {
      rxBuf[bytesRead++] = ChainSerial.read();
    } else {
      delay(1);
    }
  }

  if (bytesRead < (len + 2)) {
    Serial.printf("║ ❌ Frame truncated: Expected %d bytes, only received %d.                 ║\n", len + 2, bytesRead);
    Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
    restorePostRunMode(false);
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
    restorePostRunMode(false);
    return false;
  }

  // Sync live detected chain state
  isRunChainConnected = true;
  detectedChainCount = (int)count;
  memcpy(detectedChainBuf, rxBuf, len);
  lastChainResponseTime = millis();

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
  if (!abortableDelay(400)) {
    triggerChainAbort(count);
    return false;
  }

  // 8. PHASE 2: REAL-TIME STEP EXECUTION & WS2812B STEP TRACKING (0xBB)
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 [RUN CHAIN ENGINE] PHASE 2: EXECUTION                  ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");

  for (int s = 1; s <= count; s++) {
    // Check if user hit Red Stop button before triggering step
    if (digitalRead(PIN_STOP_BTN) == LOW) {
      triggerChainAbort(count);
      return false;
    }

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
    bool stepOk = sendRobosenPacket(actionObj);
    if (!stepOk) {
      triggerChainAbort(count);
      return false;
    }

    // Inter-step settling delay (abortable via Red Stop button)
    if (!abortableDelay(500)) {
      triggerChainAbort(count);
      return false;
    }
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

  delay(1200);
  restorePostRunMode(true);

  return true;
}

// ==============================================================================
// 9. BLE SCANNING ROUTINE (TEACHER PAIRING / SWITCH ROBOT)
// ==============================================================================
void runBleScan() {
  // If actively connected, disconnect so the robot resumes advertising
  if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(200)) == pdTRUE) {
    if (pClient != nullptr && pClient->isConnected()) {
      Serial.println("\n[BLE STATUS] Disconnecting from current robot before scan...");
      pClient->disconnect();
      isConnected = false;
      pRemoteChar = nullptr;
      delay(200);
    }
    xSemaphoreGive(bleMutex);
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

  char statusStr[32];
  if (isConnected) {
    if (hasRobotBattery && robotBatteryPercent >= 0) {
      snprintf(statusStr, sizeof(statusStr), "CONN 🟢 (%d%%)", robotBatteryPercent);
    } else {
      snprintf(statusStr, sizeof(statusStr), "CONNECTED 🟢");
    }
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
    snprintf(dockLine, sizeof(dockLine), "║ Mode 1 [CONFIG MODE]: %-48s ║", dockInfo);
    Serial.println(dockLine);
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
    Serial.println("║ • Knob 1 Twist: Select Action Block   • Knob 2 Twist: Adjust Parameter ║");
    Serial.println("║ • Start Click : Flash Config to Block • Stop Click  : Revert to Stored ║");
    Serial.println("║ • Remove block from Config Port to enter Run Mode or switch modes      ║");
  } else {
    Serial.printf("║ Mode 1 [RUN MODE]: %2d Action Block(s) Ready on Run Port               ║\n", detectedChainCount);
    Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
    for (int i = 0; i < detectedChainCount; i++) {
      uint8_t actId = detectedChainBuf[i * 2];
      uint8_t parVal = detectedChainBuf[i * 2 + 1];
      Serial.printf("║   Step %2d: [0x%02X] %-20s Parameter: %3d %-6s       ║\n",
                    i + 1, actId, getActionNameByToken(actId), parVal, getParamUnitByToken(actId));
    }
    Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
    Serial.println("║ • Start Click : Execute Run Chain     • Stop Click  : Emergency Stop   ║");
    Serial.println("║ • Dock a block on Config Port to configure | Unplug all for Mode 2/3   ║");
  }
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

void renderModeSelectMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 SYSTEM MODE SELECTOR (SCALABLE 3+ MODES)               ║");
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  for (int i = 0; i < TOTAL_SYSTEM_MODES; i++) {
    char row[100];
    if (i == currentModeMenuIndex) {
      snprintf(row, sizeof(row), "║ ► [%-23s] : %-35s ◄ ║", SYSTEM_MODES[i].name, SYSTEM_MODES[i].desc);
    } else {
      snprintf(row, sizeof(row), "║   %-25s  : %-35s   ║", SYSTEM_MODES[i].name, SYSTEM_MODES[i].desc);
    }
    Serial.println(row);
  }
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Knob 1/2: Scroll Modes      • Start / Click K1: Confirm Selection    ║");
  Serial.println("║ • Red Stop: Cancel & Return   • Hold Knob 1 (1.5s): Re-open anywhere   ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
  updateEInkModeSelectMenu();
}

void renderRemoteControlMenu() {
  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║              ROBOSEN K1 LIVE REMOTE CONTROL (HANDHELD RC)              ║");
  const char* gearStr = "DRIVE [STEER]";
  if (isConnected && hasRobotBattery && robotBatteryPercent >= 0) {
    Serial.printf("║ Active Mode: %-26s Target: %s (Bat: %d%%) ║\n", gearStr, pairedName.c_str(), robotBatteryPercent);
  } else {
    Serial.printf("║ Active Mode: %-26s Target: %-25s ║\n", gearStr, pairedName.c_str());
  }
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.printf("║ Selected Action (K2): %-48s ║\n", RC_ACTIONS[rcActionIndex].name);
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Green Button (Hold) : Walk FORWARD (0x01) (Dead-Man Gas Pedal)       ║");
  Serial.println("║ • Red Button (Hold)   : Walk BACKWARD (0x05) (Dedicated Reverse Pedal) ║");
  Serial.println("║ • Release Button      : Instant Stop & Lock Standing Posture           ║");
  Serial.println("║ • Both Buttons (Hold) : Priority Emergency Safety Halt (0x0C)          ║");
  Serial.println("║ • Knob 1 Short-Click  : Direct Mode Cycle -> Mode 3 (Joints)           ║");
  Serial.println("║ • Knob 1 Twist        : Steering Turn (Turn Left / Right)              ║");
  Serial.println("║ • Knob 2 Twist        : Scroll Actions Catalog (Mode 1 Actions)        ║");
  Serial.println("║ • Knob 2 Short-Click  : Fire Selected Action Instantly                 ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
  updateEInkRemoteControl();
}

void renderJointControlMenu() {
  const JointDef& j = ALL_JOINTS[currentJointIndex];
  int rawVal = currentServoPositions[j.servoId];
  int degOffset = rawVal - j.neutral;

  Serial.println("\n╔════════════════════════════════════════════════════════════════════════╗");
  Serial.println("║                 ROBOSEN JOINT CONTROL MODE (MODE 3)                    ║");
  if (isConnected && hasRobotBattery && robotBatteryPercent >= 0) {
    Serial.printf("║ Target: %-26s Robot Battery: %3d%% (Volume: %-3d)       ║\n",
                  pairedName.c_str(), robotBatteryPercent, robotSpeakerVolume);
  }
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.printf("║ Joint: [%-10s] (%2d/%2d)  (ID %2d)                                     ║\n",
                j.name, currentJointIndex + 1, TOTAL_JOINTS, j.servoId);
  Serial.printf("║ Angle: %3d° (Offset %+3d°)  [Min: %3d°, Max: %3d°]                          ║\n",
                rawVal, degOffset, j.minLimit, j.maxLimit);
  Serial.println("╠════════════════════════════════════════════════════════════════════════╣");
  Serial.println("║ • Knob 1: Direct Joint Cycle (All 17 Joints)                           ║");
  Serial.println("║ • Knob 1 Short-Click: Direct Mode Cycle -> Mode 1 (Blocks)             ║");
  Serial.println("║ • Knob 2: +/- 5 deg Direct Angle Adjust                                ║");
  Serial.println("║ • K2 Click: Reset Active Joint to Neutral (0°)                         ║");
  Serial.println("║ • K2 Hold (1.5s): Reset ALL 17 Servos to Standing Posture              ║");
  Serial.println("║ • Red Stop: Emergency Locomotion Stop                                  ║");
  Serial.println("╚════════════════════════════════════════════════════════════════════════╝");
  updateEInkJointControl();
}

// ==============================================================================
// 11. E-INK DISPLAY CONTROLLER IMPLEMENTATION (DEPG0213BN / SSD1680 - DUAL CORE)
// ==============================================================================

// Factory Symmetric High-Contrast LUT (727ms, 10x3 = 30 symmetric frames):
// Drives B->W (-15V) and W->B (+15V) with 100% equal & opposite duration so
// fringe fields never bleed white into black text.
const uint8_t LUT_STD_727MS[153] PROGMEM = {
  0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0A, 0x0, 0x0, 0x0, 0x0, 0x0, 0x2,
  0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0
};

// Fast Symmetric Partial LUT (~380ms, 8x2 = 16 symmetric transition frames + 2 symmetric clamp frames)
const uint8_t LUT_FAST_280MS[153] PROGMEM = {
  0x0, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x80, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x40, 0x40, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x80, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x08, 0x0, 0x0, 0x0, 0x0, 0x0, 0x1,
  0x2, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x1, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0,
  0x22, 0x22, 0x22, 0x22, 0x22, 0x22, 0x0, 0x0, 0x0
};

void loadCustomEInkLut(bool fastMode) {
  const uint8_t* lut = fastMode ? LUT_FAST_280MS : LUT_STD_727MS;
  display.epd2.applyCustomLut(lut);
}

// Non-blocking FreeRTOS yield during GxEPD2 _waitWhileBusy
// (Bounded to 900ms max by RobosenEPD2_213_BN::_busy_timeout; never aborts refresh mid-transaction)
void epdBusyYieldCallback(const void* param) {
  vTaskDelay(pdMS_TO_TICKS(2));
}

void drawBitmap2x(int16_t x, int16_t y, const uint8_t *bitmap, int16_t w, int16_t h, uint16_t color) {
  for (int16_t j = 0; j < h; j++) {
    for (int16_t i = 0; i < w; i++) {
      int byteIdx = j * ((w + 7) / 8) + (i / 8);
      uint8_t b = pgm_read_byte(&bitmap[byteIdx]);
      if (b & (0x80 >> (i & 7))) {
        display.fillRect(x + i * 2, y + j * 2, 2, 2, color);
      }
    }
  }
}

void drawDualBatteryHeader(int16_t w) {
  // 1. Black header bar (y=2..21, height 20) within visible area (x=41..248)
  display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 2, SCREEN_VISIBLE_WIDTH - 2, 20, GxEPD_BLACK);

  // 2. Connected Robot Name / Connection Status on left (x=45, y=17)
  display.setTextColor(GxEPD_WHITE);
  display.setFont(&FreeSansBold9pt7b);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 5, 17);

  if (isConnected) {
    String rName = pairedName;
    if (rName.length() == 0 || rName == "None") rName = "K1";
    if (rName.length() > 8) rName = rName.substring(0, 8); // Max 8 chars to avoid overlap with battery cells
    display.print(rName);
  } else if (pairedMAC == "None (Unpaired)" || pairedMAC.length() < 10) {
    display.print("UNPAIRED");
  } else if (connectAttemptCounter > 0) {
    display.print("SEARCH");
  } else {
    display.print("DISCONN");
  }

  // 3. Dual Battery Gauges (Header Top-Right) in exact Main Firmware 20x10 Outline Style
  display.setFont();
  display.setTextSize(1);

  float vbat = readBatteryVoltage();
  int masterPct = calculateBatteryPercent(vbat);
  lastDisplayedMasterPct = masterPct;

  // --- Robot Battery Cell [R] (20x10 px outline + 2x6 terminal tip) ---
  int rx = 126;
  display.setCursor(rx, 8);
  display.print("R");

  display.drawRect(rx + 8, 6, 20, 10, GxEPD_WHITE);
  display.fillRect(rx + 28, 8, 2, 6, GxEPD_WHITE); // terminal tip

  if (isConnected && hasRobotBattery && robotBatteryPercent >= 0) {
    int fillW = map(constrain(robotBatteryPercent, 0, 100), 0, 100, 0, 16);
    if (fillW > 0) {
      display.fillRect(rx + 10, 8, fillW, 6, GxEPD_WHITE);
    }
    display.setCursor(rx + 33, 8);
    display.printf("%d%%", robotBatteryPercent);
  } else {
    display.setCursor(rx + 33, 8);
    display.print("--");
  }

  // --- Master Battery Cell [M] (20x10 px outline + 2x6 terminal tip) ---
  int mx = 188;
  display.setCursor(mx, 8);
  display.print("M");

  display.drawRect(mx + 8, 6, 20, 10, GxEPD_WHITE);
  display.fillRect(mx + 28, 8, 2, 6, GxEPD_WHITE); // terminal tip

  int mFillW = map(constrain(masterPct, 0, 100), 0, 100, 0, 16);
  if (mFillW > 0) {
    display.fillRect(mx + 10, 8, mFillW, 6, GxEPD_WHITE);
  }
  display.setCursor(mx + 33, 8);
  display.printf("%d%%", masterPct);
}

void drawActionMenuToBuffer(bool invertMiddle) {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);

  int16_t w = display.width();
  int16_t h = display.height();

  // 1. Frame border around visible window
  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  // 2. Dual Battery Header with Connected Robot Name
  drawDualBatteryHeader(w);

  // 3. Center Section (y = 24..119, full height)
  uint16_t midFg = invertMiddle ? GxEPD_WHITE : GxEPD_BLACK;
  if (invertMiddle) {
    display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 23, SCREEN_VISIBLE_WIDTH - 2, 97, GxEPD_BLACK);
  }

  char numStr[16];
  if (isBlockDocked) {
    // Sub-Mode 1A: Configuration Menu UI (Action Icon + Parameter Value)
    int actIdx = currentActionIndex;
    if (actIdx < 0 || actIdx >= TOTAL_ACTIONS) actIdx = 0;
    RobosenAction act = ACTIONS[actIdx];

    // 48x48 Action Bitmap (centered in left half of visible window: x = 92 - 24 = 68, y = 48)
    drawBitmap2x(68, 48, getActionIcon(actIdx), 24, 24, midFg);

    // Big Parameter Number (dynamically centered in right half of visible window: center = 197)
    if (strcmp(act.paramUnit, "Deg°") == 0) {
      snprintf(numStr, sizeof(numStr), "%d°", act.paramVal);
    } else {
      snprintf(numStr, sizeof(numStr), "%d", act.paramVal);
    }
  } else {
    // Sub-Mode 1B: Run Mode UI (Blocks Icon + Divider + Total Connected Block Count)
    drawBitmap2x(68, 48, ICON_MODE_BLOCKS, 24, 24, midFg);
    display.drawFastVLine(145, 36, 68, midFg);
    snprintf(numStr, sizeof(numStr), "%u", (unsigned int)detectedChainCount);
  }

  display.setTextColor(midFg);
  display.setFont(&FreeSansBold18pt7b);

  int16_t bx, by;
  uint16_t bw, bh;
  display.getTextBounds(numStr, 0, 0, &bx, &by, &bw, &bh);

  int16_t textX = 197 - (bw / 2) - bx;
  display.setCursor(textX, 80);
  display.print(numStr);
}

void drawPairingMenuToBuffer() {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 2, SCREEN_VISIBLE_WIDTH - 2, 20, GxEPD_BLACK);
  display.setTextColor(GxEPD_WHITE);
  display.setFont(&FreeSansBold9pt7b);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 5, 17);
  display.print("PAIR ROBOT (BLE)");

  display.setFont();
  display.setTextSize(1);
  display.setCursor(185, 8);
  display.printf("%d FOUND", bleDeviceCount);

  display.setTextColor(GxEPD_BLACK);
  if (bleDeviceCount == 0) {
    display.setCursor(SCREEN_VISIBLE_X_MIN + 10, 46);
    display.print("No K1 robots found in range.");
    display.setCursor(SCREEN_VISIBLE_X_MIN + 10, 62);
    display.print("Ensure robot is powered ON.");
  } else {
    int startIdx = (currentBleIndex / 3) * 3;
    int yPos = 32;
    for (int i = startIdx; i < bleDeviceCount && i < startIdx + 3; i++) {
      if (i == currentBleIndex) {
        display.fillRect(SCREEN_VISIBLE_X_MIN + 2, yPos - 2, SCREEN_VISIBLE_WIDTH - 4, 15, GxEPD_BLACK);
        display.setTextColor(GxEPD_WHITE);
        display.setCursor(SCREEN_VISIBLE_X_MIN + 6, yPos);
        display.printf("> %-16s %3ddBm", bleList[i].name.substring(0, 16).c_str(), bleList[i].rssi);
      } else {
        display.setTextColor(GxEPD_BLACK);
        display.setCursor(SCREEN_VISIBLE_X_MIN + 6, yPos);
        display.printf("  %-16s %3ddBm", bleList[i].name.substring(0, 16).c_str(), bleList[i].rssi);
      }
      yPos += 16;
    }
  }

  display.drawLine(SCREEN_VISIBLE_X_MIN + 2, 92, SCREEN_VISIBLE_X_MAX - 2, 92, GxEPD_BLACK);
  display.setTextColor(GxEPD_BLACK);
  display.setFont();
  display.setCursor(SCREEN_VISIBLE_X_MIN + 6, 98);
  display.print("Knob: Select  |  Start: Confirm");
  display.setCursor(SCREEN_VISIBLE_X_MIN + 6, 110);
  display.print("Stop (Red): Cancel & Return");
}

void drawScanningToBuffer() {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 2, SCREEN_VISIBLE_WIDTH - 2, 20, GxEPD_BLACK);
  display.setTextColor(GxEPD_WHITE);
  display.setFont(&FreeSansBold9pt7b);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 5, 17);
  display.print("BLE SCANNING...");

  display.setFont();
  display.setTextColor(GxEPD_BLACK);
  display.setTextSize(1);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 8, 46);
  display.print("Searching nearby Robosen K1 robots...");
  display.setCursor(SCREEN_VISIBLE_X_MIN + 8, 62);
  display.print("Sorting by RSSI signal strength.");

  display.drawLine(SCREEN_VISIBLE_X_MIN + 2, 92, SCREEN_VISIBLE_X_MAX - 2, 92, GxEPD_BLACK);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 6, 102);
  display.print("Stop Button (Red): Cancel scan");
}

void drawRunChainToBuffer(int currentStep, int totalSteps, const char* actionName, int paramVal, const char* paramUnit) {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 2, SCREEN_VISIBLE_WIDTH - 2, 20, GxEPD_BLACK);
  display.setTextColor(GxEPD_WHITE);
  display.setFont(&FreeSansBold9pt7b);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 5, 17);
  display.print("RUNNING CHAIN");

  display.setFont();
  display.setTextSize(1);
  display.setCursor(185, 8);
  if (totalSteps > 0) {
    display.printf("STEP %d/%d", currentStep, totalSteps);
  } else {
    display.print("PHASE 1");
  }

  display.setTextColor(GxEPD_BLACK);
  display.setFont(&FreeSansBold9pt7b);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 10, 48);
  display.print(actionName);

  display.setFont();
  display.setTextSize(2);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 10, 64);
  if (paramVal > 0) {
    display.printf("%d %s", paramVal, paramUnit);
  } else {
    display.print("Active");
  }

  display.drawLine(SCREEN_VISIBLE_X_MIN + 2, 92, SCREEN_VISIBLE_X_MAX - 2, 92, GxEPD_BLACK);
  display.setTextSize(1);
  display.setCursor(SCREEN_VISIBLE_X_MIN + 6, 102);
  display.print("Run Chain Active | Stop (Red): Halt");
}

// Non-blocking UI request wrappers (called from Core 1)
void updateEInkActionMenu() {
  requestEInkFullUpdate();
}

void updateEInkPairingMenu() {
  requestEInkFullUpdate();
}

void updateEInkModeSelectMenu() {
  requestEInkFullUpdate();
}

void updateEInkRemoteControl() {
  requestEInkFullUpdate();
}

void updateEInkJointControl() {
  requestEInkFullUpdate();
}

void updateEInkScanning() {
  einkScanningDirty = true;
}

void updateEInkRunChain(int currentStep, int totalSteps, const char* actionName, int paramVal, const char* paramUnit) {
  rcSnapStep = currentStep;
  rcSnapTotal = totalSteps;
  strncpy(rcSnapName, actionName ? actionName : "", sizeof(rcSnapName) - 1);
  rcSnapName[sizeof(rcSnapName) - 1] = '\0';
  rcSnapParam = paramVal;
  strncpy(rcSnapUnit, paramUnit ? paramUnit : "", sizeof(rcSnapUnit) - 1);
  rcSnapUnit[sizeof(rcSnapUnit) - 1] = '\0';
  einkRunChainDirty = true;
}

void drawModeSelectMenuToBuffer() {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  // 1. Frame border around visible window
  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  // 2. Dual Battery Header with Connected Robot Name
  drawDualBatteryHeader(w);

  // 3. 3-Icon Carousel within calibrated visible window (x = 40..249, 60x60 cards)
  const int cardX[3] = {47, 115, 183};
  const int cardY = 40;
  const int cardW = 60;
  const int cardH = 60;

  for (int i = 0; i < 3; i++) {
    bool isSelected = (i == currentModeMenuIndex);
    if (isSelected) {
      // Inverted solid black card for selected mode
      display.fillRect(cardX[i], cardY, cardW, cardH, GxEPD_BLACK);
      drawBitmap2x(cardX[i] + 6, cardY + 6, getModeBadgeIcon(i), 24, 24, GxEPD_WHITE);
    } else {
      // Outlined card for unselected modes
      display.drawRect(cardX[i], cardY, cardW, cardH, GxEPD_BLACK);
      drawBitmap2x(cardX[i] + 6, cardY + 6, getModeBadgeIcon(i), 24, 24, GxEPD_BLACK);
    }
  }
}

void drawRemoteControlToBuffer(bool invertMiddle) {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  // 1. Frame border around visible window
  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  // 2. Dual Battery Header with Connected Robot Name
  drawDualBatteryHeader(w);

  // 3. Center Section (y = 24..119, full height)
  uint16_t midFg = invertMiddle ? GxEPD_WHITE : GxEPD_BLACK;
  if (invertMiddle) {
    display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 23, SCREEN_VISIBLE_WIDTH - 2, 97, GxEPD_BLACK);
  }

  // Left Column: Arcade Joystick 48x48 Icon (centered in left half of visible window: x=68, y=48)
  drawBitmap2x(68, 48, ICON_JOYSTICK, 24, 24, midFg);

  // Vertical Divider at calibrated visible center (x = 145)
  display.drawFastVLine(145, 36, 68, midFg);

  // Right Column: Active Stunt Action 48x48 Icon (centered in right half of visible window: x=173, y=48)
  drawBitmap2x(173, 48, RC_ACTIONS[rcActionIndex].icon, 24, 24, midFg);
}

void drawJointControlToBuffer(bool invertMiddle) {
  display.setFullWindow();
  display.fillScreen(GxEPD_WHITE);
  int16_t w = display.width();
  int16_t h = display.height();

  // 1. Frame border around visible window
  display.drawRect(SCREEN_VISIBLE_X_MIN, SCREEN_VISIBLE_Y_MIN, SCREEN_VISIBLE_WIDTH, SCREEN_VISIBLE_HEIGHT, GxEPD_BLACK);

  // 2. Dual Battery Header with Connected Robot Name
  drawDualBatteryHeader(w);

  // 3. Center Section (y = 24..119, full height)
  uint16_t midFg = invertMiddle ? GxEPD_WHITE : GxEPD_BLACK;
  if (invertMiddle) {
    display.fillRect(SCREEN_VISIBLE_X_MIN + 1, 23, SCREEN_VISIBLE_WIDTH - 2, 97, GxEPD_BLACK);
  }

  const JointDef& j = ALL_JOINTS[currentJointIndex];
  int currentVal = (int)currentServoPositions[j.servoId];
  int offset = currentVal - (int)j.neutral;

  // Anatomy 48x48 Icon (Head, L.Arm, R.Arm, L.Leg, R.Leg at x=48)
  drawBitmap2x(48, 34, getJointGroupIcon(j.groupIconIdx), 24, 24, midFg);

  // Short Joint Name (strip "L." or "R." prefix)
  const char* sName = (j.name[1] == '.') ? (j.name + 2) : j.name;
  display.setTextColor(midFg);
  display.setFont(&FreeSansBold12pt7b);
  display.setCursor(106, 52);
  display.print(sName);

  // Big Degree Readout (y = 76)
  display.setCursor(106, 76);
  if (offset > 0) {
    display.printf("+%d°", offset);
  } else if (offset < 0) {
    display.printf("%d°", offset);
  } else {
    display.print("0°");
  }

  // Full-width Slider Gauge (y = 96, x=46..242)
  int gaugeX = 46;
  int gaugeW = 196;
  int gaugeY = 96;
  display.drawFastHLine(gaugeX, gaugeY, gaugeW, midFg);
  display.drawFastVLine(gaugeX, gaugeY - 5, 11, midFg);
  display.drawFastVLine(gaugeX + gaugeW, gaugeY - 5, 11, midFg);

  int centerTickX = map(j.neutral, j.minLimit, j.maxLimit, gaugeX, gaugeX + gaugeW);
  display.drawFastVLine(centerTickX, gaugeY - 6, 13, midFg);

  int pipX = map(currentVal, j.minLimit, j.maxLimit, gaugeX, gaugeX + gaugeW);
  pipX = constrain(pipX, gaugeX, gaugeX + gaugeW);
  display.fillRect(pipX - 3, gaugeY - 5, 7, 11, midFg);
}

// Dedicated Core 0 E-Ink Rendering Task (0ms impact on Core 1 inputs/LED)
void einkDisplayTask(void* pvParameters) {
  display.epd2.setBusyCallback(epdBusyYieldCallback);

  while (true) {
    unsigned long now = millis();

    // 1. Self-healing hardware reset & dual-buffer sync if requested
    if (einkForceReinit) {
      einkForceReinit = false;
      Serial.println("[E-INK] Starting hardware reset + OTP Full Refresh + Dual-Buffer Sync...");
      pinMode(PIN_EPD_RES, OUTPUT);
      digitalWrite(PIN_EPD_RES, HIGH); vTaskDelay(pdMS_TO_TICKS(15));
      digitalWrite(PIN_EPD_RES, LOW);  vTaskDelay(pdMS_TO_TICKS(25));
      digitalWrite(PIN_EPD_RES, HIGH); vTaskDelay(pdMS_TO_TICKS(60));
      display.init(0, true, 10, false);
      SPI.begin(PIN_EPD_SCL, -1, PIN_EPD_SDA, -1);
      display.epd2.selectSPI(SPI, SPISettings(4000000, MSBFIRST, SPI_MODE0));
      display.setRotation(1);
      display.setFullWindow();
      display.epd2.setBusyCallback(epdBusyYieldCallback);
      bool busyFaulty = display.epd2.detectFaultyBusyPin();
      display.epd2.configureBusyPin(busyFaulty);
      epdWaitStartMs = millis();
      // 1a. Execute Factory OTP Full Refresh (0x22, 0xF4, 0x20) to wake up charge pumps & clear panel
      display.epd2.clearScreen(0xFF);
      // 1b. Re-sync both buffers & load custom partial LUT; einkFullDirty renders active mode below
      display.epd2.writeScreenBufferAgain(0xFF);
      loadCustomEInkLut(false);
      einkFullDirty = true;
      Serial.println("[E-INK] Hardware reset + OTP Full Refresh completed!");
    }

    // 2. Immediate BLE Scanning Screen
    if (einkScanningDirty) {
      einkScanningDirty = false;
      loadCustomEInkLut(true);
      drawScanningToBuffer();
      epdWaitStartMs = millis();
      display.display(true);
      continue;
    }

    // 3. Immediate Run Chain Step Screen
    if (einkRunChainDirty) {
      einkRunChainDirty = false;
      loadCustomEInkLut(true);
      drawRunChainToBuffer(rcSnapStep, rcSnapTotal, rcSnapName, rcSnapParam, rcSnapUnit);
      epdWaitStartMs = millis();
      display.display(true);
      continue;
    }

    // 4. Interactive Updates (Full uses Factory 727ms LUT; Knob turns use Fast Symmetric LUT)
    if ((einkFullDirty || einkCenterDirty) && (now - lastEInkInputMs >= 30)) {
      bool doFull = einkFullDirty;
      einkFullDirty = false;
      einkCenterDirty = false;

      // Use fast symmetric 280ms LUT for interactive knob turns and mode switching;
      // 350ms settle pass below ensures crisp contrast.
      loadCustomEInkLut(true);
      epdWaitStartMs = millis();

      if (currentState == STATE_BLE_PAIRING_MENU) {
        loadCustomEInkLut(false);
        drawPairingMenuToBuffer();
        display.display(true);
      } else if (currentState == STATE_MODE_SELECT_MENU) {
        loadCustomEInkLut(true); // Fast 280ms LUT for snappy, instant carousel response
        drawModeSelectMenuToBuffer();
        display.display(true);
      } else if (currentState == STATE_ACTION_MENU) {
        drawActionMenuToBuffer(false);
        if (doFull) {
          display.display(true);
        } else {
          // Targeted center update within visible bezel area (x=40..249, y=24, h=96): header never flickers!
          display.displayWindow(SCREEN_VISIBLE_X_MIN, 24, SCREEN_VISIBLE_WIDTH, 96);
        }
      } else if (currentState == STATE_REMOTE_CONTROL) {
        drawRemoteControlToBuffer(false);
        if (doFull) {
          display.display(true);
        } else {
          display.displayWindow(SCREEN_VISIBLE_X_MIN, 24, SCREEN_VISIBLE_WIDTH, 96);
        }
      } else if (currentState == STATE_JOINT_CONTROL) {
        drawJointControlToBuffer(false);
        if (doFull) {
          display.display(true);
        } else {
          display.displayWindow(SCREEN_VISIBLE_X_MIN, 24, SCREEN_VISIBLE_WIDTH, 96);
        }
      }
      continue;
    }

    // 5. Hybrid Adaptive Settle Pass: 350ms after knob stops, drive BOTH Black text (1->0)
    //    AND White background (0->1) in the middle band with full 30-frame symmetric factory LUT!
    if (einkNeedsCrispSettle && !einkFullDirty && !einkCenterDirty && (now - lastEInkInputMs >= 350)) {
      einkNeedsCrispSettle = false;
      loadCustomEInkLut(false); // Factory 30-frame symmetric LUT
      epdWaitStartMs = millis();

      if (currentState == STATE_ACTION_MENU) {
        // Pre-load 0x26 (Previous RAM) with middle band INVERTED (White text on Black bg):
        // - Every Black text pixel in middle band sees 1 -> 0 (LUT2: full 30-frame +15V Black!)
        // - Every White bg pixel in middle band sees 0 -> 1 (LUT1: full 30-frame -15V White!)
        // - Header & Footer see 0 -> 0 / 1 -> 1 (untouched, zero flicker!)
        drawActionMenuToBuffer(true);
        display.nextPageToPrevious();
        drawActionMenuToBuffer(false);
        display.display(true);
      } else if (currentState == STATE_REMOTE_CONTROL) {
        drawRemoteControlToBuffer(true);
        display.nextPageToPrevious();
        drawRemoteControlToBuffer(false);
        display.display(true);
      } else if (currentState == STATE_JOINT_CONTROL) {
        drawJointControlToBuffer(true);
        display.nextPageToPrevious();
        drawJointControlToBuffer(false);
        display.display(true);
      }
      continue;
    }

    vTaskDelay(pdMS_TO_TICKS(12));
  }
}

// Dedicated Core 0 Background BLE Reconnect Task (prevents 1s BLE scan from blocking inputs/LED)
void bleReconnectTask(void* pvParameters) {
  while (true) {
    unsigned long now = millis();
    bool userRequested = requestBgReconnect;
    if (userRequested) requestBgReconnect = false;

    if ((currentState == STATE_ACTION_MENU || currentState == STATE_REMOTE_CONTROL || currentState == STATE_JOINT_CONTROL) && !isConnected) {
      if (pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
        if (userRequested || ((now - lastUserActivity > 5000) && (now - lastConnectAttemptTime >= 3000))) {
          if (bleMutex != nullptr && xSemaphoreTake(bleMutex, pdMS_TO_TICKS(50)) == pdTRUE) {
            // Re-verify connection status before starting 1s scan
            if ((currentState == STATE_ACTION_MENU || currentState == STATE_REMOTE_CONTROL || currentState == STATE_JOINT_CONTROL) && !isConnected) {
              connectAttemptCounter++;
              bool ok = connectToRobot(true); // quietBg = true: does not hijack RGB LED!
              lastConnectAttemptTime = millis();
              if (ok) {
                connectAttemptCounter = 0;
                Serial.println("[BLE STATUS] ✅ Background auto-reconnect succeeded!");
                updateStatusLED();
                requestEInkFullUpdate();
              }
            }
            xSemaphoreGive(bleMutex);
          }
        }
      }
    }
    vTaskDelay(pdMS_TO_TICKS(200));
  }
}

void startBackgroundTasks() {
  bleMutex = xSemaphoreCreateMutex();
  xTaskCreatePinnedToCore(einkDisplayTask,  "EInkTask", 8192, nullptr, 2, nullptr, 0);
  xTaskCreatePinnedToCore(bleReconnectTask, "BleTask",  6144, nullptr, 1, nullptr, 0);
}
