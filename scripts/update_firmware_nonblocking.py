import os

path = r"C:\Users\nnnn\Projects\robosen_block\firmware\esp32_master\esp32_master.ino"
with open(path, "r", encoding="utf-8") as f:
    text = f.read()

start_marker = "void loop() {"
end_marker = "  lastK2Sw = k2Sw;\n}"

idx1 = text.find(start_marker)
idx2 = text.find(end_marker)

if idx1 == -1 or idx2 == -1:
    print(f"Error: markers not found. idx1={idx1}, idx2={idx2}")
    exit(1)

new_loop = """void loop() {
  unsigned long now = millis();

  // --- 0. LED TACTILE FEEDBACK TIMEOUT ---
  if (ledBlipUntil > 0 && now >= ledBlipUntil) {
    ledBlipUntil = 0;
    updateStatusLED();
  }

  // --- 1. CONFIG DOCK MONITORING & ACTION QUERY ENGINE ---
  pollConfigDock();

  // Serial Monitor Interactive Test ('t' = Ping Config Dock, 'r' = Run Chain)
  if (Serial.available() > 0) {
    char c = Serial.read();
    if (c == 't' || c == 'T') {
      Serial.println("\\n[DOCK TEST] 📡 Manual Ping [0xCF, 0x01, 0x07, 0x55] sent to GPIO 17...");
      uint8_t qPkt[4] = { 0xCF, 0x01, 0x07, 0x55 };
      Serial1.write(qPkt, 4);
      Serial1.flush();
      delay(30);
      Serial.printf("[DOCK TEST] Serial1 buffer has %d bytes waiting on GPIO 18\\n", Serial1.available());
    } else if (c == 'r' || c == 'R') {
      Serial.println("\\n[RUN CHAIN TEST] 🚀 Manual trigger executeRunChain()...");
      if (!executeRunChain()) {
        Serial.println("[RUN CHAIN TEST] ⚠️ Run chain execution failed (No blocks / End block found).");
      }
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
    lastKnobTurnTime = now;
    screenNeedsUpdate = true;
    triggerLedBlip(0, 80, 80); // Cyan tactile feedback

    if (currentState == STATE_ACTION_MENU) {
      currentActionIndex = (currentActionIndex + d1) % TOTAL_ACTIONS;
      while (currentActionIndex < 0) currentActionIndex += TOTAL_ACTIONS;
      Serial.printf("🔄 [KNOB 1] Action: %s\\n", ACTIONS[currentActionIndex].name);
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      currentBleIndex = (currentBleIndex + d1) % bleDeviceCount;
      while (currentBleIndex < 0) currentBleIndex += bleDeviceCount;
      Serial.printf("🔄 [BLE LIST] %d: %s\\n", currentBleIndex + 1, bleList[currentBleIndex].name.c_str());
    }
  }

  if (d2 != 0) {
    lastUserActivity = now;
    lastKnobTurnTime = now;
    screenNeedsUpdate = true;
    triggerLedBlip(80, 0, 80); // Magenta tactile feedback

    if (currentState == STATE_ACTION_MENU) {
      RobosenAction& act = ACTIONS[currentActionIndex];
      act.paramVal += (d2 * act.paramStep);
      if (act.paramVal > act.paramMax) act.paramVal = act.paramMax;
      if (act.paramVal < act.paramMin) act.paramVal = act.paramMin;
      Serial.printf("🔄 [KNOB 2] Parameter: %d %s\\n", act.paramVal, act.paramUnit);
    } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
      currentBleIndex = (currentBleIndex + d2) % bleDeviceCount;
      while (currentBleIndex < 0) currentBleIndex += bleDeviceCount;
      Serial.printf("🔄 [BLE LIST] %d: %s\\n", currentBleIndex + 1, bleList[currentBleIndex].name.c_str());
    }
  }

  // --- 3. KNOB 1 SWITCH (GPIO 10 - ACTIVE LOW) ---
  int k1SwRaw = digitalRead(PIN_K1_SW);
  static int lastK1SwRaw = HIGH;
  static unsigned long lastK1SwDebounce = 0;
  static bool k1SwPressed = false;

  if (k1SwRaw != lastK1SwRaw) {
    lastK1SwDebounce = now;
    lastK1SwRaw = k1SwRaw;
  }
  if (now - lastK1SwDebounce > 30) {
    if (k1SwRaw == LOW && !k1SwPressed) {
      k1SwPressed = true;
      lastUserActivity = now;
      triggerLedBlip(0, 80, 40); // Emerald Green
      if (currentState == STATE_ACTION_MENU) {
        if (isBlockDocked) {
          RobosenAction& act = ACTIONS[currentActionIndex];
          Serial.printf("\\n>>> [CONFIG DOCK] Flashing '%s' (%d %s) into docked Action Block... <<<\\n",
                        act.name, act.paramVal, act.paramUnit);
          writeConfigToDockedBlock(act.tokenID, (uint8_t)act.paramVal);
          triggerLedBlip(0, 80, 40);
        } else {
          Serial.printf("\\n>>> [KNOB 1 CLICK] Selected Action: %s <<<\\n", ACTIONS[currentActionIndex].name);
          if (!isConnected && pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
            Serial.println("[BLE STATUS] ⚡ Knob clicked while disconnected: Immediate connection attempt...");
            if (connectToRobot()) {
              connectAttemptCounter = 0;
              renderActionMenu();
            }
            lastConnectAttemptTime = millis();
          } else {
            triggerLedBlip(0, 60, 30);
          }
        }
      } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
        pairedMAC  = bleList[currentBleIndex].address;
        pairedName = bleList[currentBleIndex].name;
        preferences.putString("paired_mac", pairedMAC);
        preferences.putString("paired_name", pairedName);
        currentState = STATE_ACTION_MENU;
        connectAttemptCounter = 0;
        renderActionMenu();
        connectToRobot();
        lastConnectAttemptTime = millis();
      }
    } else if (k1SwRaw == HIGH && k1SwPressed) {
      k1SwPressed = false;
    }
  }

  // --- 4. KNOB 2 SWITCH (GPIO 13 - ACTIVE LOW) ---
  int k2SwRaw = digitalRead(PIN_K2_SW);
  static int lastK2SwRaw = HIGH;
  static unsigned long lastK2SwDebounce = 0;
  static bool k2SwPressed = false;

  if (k2SwRaw != lastK2SwRaw) {
    lastK2SwDebounce = now;
    lastK2SwRaw = k2SwRaw;
  }
  if (now - lastK2SwDebounce > 30) {
    if (k2SwRaw == LOW && !k2SwPressed) {
      k2SwPressed = true;
      lastUserActivity = now;
      triggerLedBlip(80, 0, 80); // Magenta
      if (currentState == STATE_ACTION_MENU) {
        RobosenAction& act = ACTIONS[currentActionIndex];
        act.paramVal = act.paramMin;
        Serial.printf("\\n>>> [KNOB 2 CLICK] Reset %s Parameter to %d %s <<<\\n", 
                      act.name, act.paramVal, act.paramUnit);
        screenNeedsUpdate = true;
        lastKnobTurnTime = now;
      } else if (currentState == STATE_BLE_PAIRING_MENU && bleDeviceCount > 0) {
        pairedMAC  = bleList[currentBleIndex].address;
        pairedName = bleList[currentBleIndex].name;
        preferences.putString("paired_mac", pairedMAC);
        preferences.putString("paired_name", pairedName);
        setStatusLED(0, 50, 0);
        currentState = STATE_ACTION_MENU;
        connectAttemptCounter = 0;
        renderActionMenu();
        connectToRobot();
        lastConnectAttemptTime = millis();
      }
    } else if (k2SwRaw == HIGH && k2SwPressed) {
      k2SwPressed = false;
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

  if (now - lastStartDebounce > 30) {
    if (startRaw == LOW && !startBtnPressed) {
      startBtnPressed = true;
      startPressStart = now;
      startBtnHeld3s = false;
      lastUserActivity = now;
      triggerLedBlip(0, 100, 0); // Green
      Serial.println("\\n[BUTTON] Start button pressed... (Hold 3s to switch robot)");
    } else if (startRaw == LOW && startBtnPressed) {
      lastUserActivity = now;
      if (!startBtnHeld3s && (now - startPressStart >= 3000)) {
        startBtnHeld3s = true;
        Serial.println("\\n[SYSTEM] 🎯 3-Second Hold Confirmed! Opening Teacher Pairing Menu...");
        runBleScan();
      }
    } else if (startRaw == HIGH && startBtnPressed) {
      startBtnPressed = false;
      lastUserActivity = now;
      unsigned long heldDuration = now - startPressStart;
      if (!startBtnHeld3s && heldDuration >= 40 && heldDuration < 3000) {
        if (currentState == STATE_ACTION_MENU) {
          Serial.println("\\n[SYSTEM] Start button clicked: Initiating Run Chain (GPIO 15/16)...");
          if (!executeRunChain()) {
            Serial.println("\\n[SYSTEM] ⚠️ Chain execution aborted: No valid return packet received from return rail!");
            setStatusLED(50, 0, 0);
            delay(500);
            updateStatusLED();
          }
        } else if (currentState == STATE_BLE_PAIRING_MENU) {
          if (bleDeviceCount > 0) {
            pairedMAC  = bleList[currentBleIndex].address;
            pairedName = bleList[currentBleIndex].name;
            preferences.putString("paired_mac", pairedMAC);
            preferences.putString("paired_name", pairedName);
            Serial.printf("\\n[BLE STATUS] 🟢 Confirmed robot via Start Button: %s (%s)\\n", pairedName.c_str(), pairedMAC.c_str());
          }
          currentState = STATE_ACTION_MENU;
          renderActionMenu();
          if (pairedMAC != "None (Unpaired)" && !isConnected) {
            connectToRobot();
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

  if (now - lastStopDebounce > 30) {
    if (stopRaw == LOW && !stopBtnPressed) {
      stopBtnPressed = true;
      stopPressStart = now;
      stopBtnHeld3s = false;
      lastUserActivity = now;
      triggerLedBlip(100, 0, 0); // Red
      Serial.println("\\n[BUTTON] Red Stop/Cancel button pressed... (Hold 3s to disconnect BLE)");
    } else if (stopRaw == LOW && stopBtnPressed) {
      lastUserActivity = now;
      if (!stopBtnHeld3s && (now - stopPressStart >= 3000)) {
        stopBtnHeld3s = true;
        Serial.println("\\n[SYSTEM] 🎯 3-Second Stop Hold Confirmed! Disconnecting BLE session...");
        if (pClient != nullptr && pClient->isConnected()) {
          pClient->disconnect();
        }
        isConnected = false;
        pRemoteChar = nullptr;
        setStatusLED(60, 0, 0);
        delay(300);
        updateStatusLED();
      }
    } else if (stopRaw == HIGH && stopBtnPressed) {
      stopBtnPressed = false;
      lastUserActivity = now;
      unsigned long heldDuration = now - stopPressStart;
      if (!stopBtnHeld3s && heldDuration >= 40 && heldDuration < 3000) {
        if (currentState == STATE_ACTION_MENU) {
          if (isBlockDocked) {
            Serial.println("\\n[CANCEL] Dismissed docked block configuration.");
            isBlockDocked = false;
            renderActionMenu();
          } else {
            Serial.println("\\n[EMERGENCY STOP] Red Stop button pressed: Sending locomotion stop to lock posture!");
            sendLocomotionStop();
            setStatusLED(80, 0, 0);
            delay(200);
            updateStatusLED();
          }
        } else if (currentState == STATE_BLE_PAIRING_MENU || currentState == STATE_BLE_SCANNING) {
          Serial.println("\\n[CANCEL] Cancelled pairing/scan, returning to Action Menu.");
          currentState = STATE_ACTION_MENU;
          renderActionMenu();
          updateStatusLED();
        }
      }
    }
  }

  // --- 7. CONTINUOUS AUTO-RECONNECT & BACKGROUND HEARTBEAT ---
  if (currentState == STATE_ACTION_MENU) {
    if (isConnected && pRemoteChar != nullptr && pClient != nullptr && pClient->isConnected()) {
      connectAttemptCounter = 0;
      if (now - lastHeartbeatTime >= 5000) {
        lastHeartbeatTime = now;
        uint8_t pingPacket[] = {0xFF, 0xFF, 0x02, 0x0B, 0x0D};
        if (pRemoteChar->canWrite()) {
          pRemoteChar->writeValue(pingPacket, sizeof(pingPacket));
        }
      }
    } else {
      // Disconnected: retry only if user has been inactive for >= 5s
      if (pairedMAC != "None (Unpaired)" && pairedMAC.length() >= 10) {
        if (now - lastUserActivity > 5000) {
          if (now - lastConnectAttemptTime >= RETRY_INTERVAL_MS) {
            connectAttemptCounter++;
            Serial.printf("[BLE STATUS] ⏳ [Attempt #%d] Checking for %s (%s)... (1s scan)\\n", 
                          connectAttemptCounter, pairedName.c_str(), pairedMAC.c_str());

            bool success = connectToRobot();
            lastConnectAttemptTime = millis();

            if (success) {
              connectAttemptCounter = 0;
              Serial.println("[BLE STATUS] ✅ Successfully connected to robot!");
              renderActionMenu();
            } else {
              Serial.printf("[BLE STATUS] ❌ Attempt #%d: Robot not detected. Pausing 2s... (Hold Start 3s to switch)\\n",
                            connectAttemptCounter);
            }
          }
        }
      }
    }
  }

  // --- 8. SETTLE-DELAYED E-PAPER REFRESH ---
  if (screenNeedsUpdate && (now - lastKnobTurnTime >= SCREEN_SETTLE_MS)) {
    screenNeedsUpdate = false;
    if (currentState == STATE_ACTION_MENU) {
      renderActionMenu();
    } else if (currentState == STATE_BLE_PAIRING_MENU) {
      renderPairingMenu();
    }
  }
}"""

new_text = text[:idx1] + new_loop + text[idx2 + len(end_marker):]

with open(path, "w", encoding="utf-8") as f:
    f.write(new_text)

print("SUCCESS: loop() replaced cleanly!")
