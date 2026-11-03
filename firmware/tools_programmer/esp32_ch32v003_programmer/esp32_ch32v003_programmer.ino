#include <Arduino.h>

#include "dmi.h"
#include "swio.h"
#include "target.h"

namespace {

char commandLine[1152];
size_t commandLength = 0;

void printFailure(const char* stage, DmiResult result) {
  Serial.printf("%s: FAILED (%s)\n", stage, dmiResultText(result));
}

void printTargetFailure(const char* stage, TargetResult result) {
  Serial.printf("%s: FAILED (%s)\n", stage, targetResultText(result));
}

bool parseArbitraryHexBytes(const char* text, uint8_t* out, size_t maxLen, size_t& outLen) {
  const size_t textLen = strlen(text);
  if (textLen == 0 || (textLen % 2) != 0 || (textLen / 2) > maxLen) return false;
  outLen = textLen / 2;
  for (size_t i = 0; i < outLen; ++i) {
    char pair[3] = {text[i * 2], text[i * 2 + 1], 0};
    char* end = nullptr;
    const unsigned long value = strtoul(pair, &end, 16);
    if (*end != 0 || value > 0xFF) return false;
    out[i] = static_cast<uint8_t>(value);
  }
  return true;
}

void runDetect() {
  TargetInfo info{};
  TargetResult result = targetDetect(info);
  if (result != TargetResult::Ok) {
    printTargetFailure("Target detect", result);
    return;
  }
  Serial.printf("Target detect: OK (CH32 ID = 0x%08lX, DMHARTINFO = 0x%08lX)\n",
                static_cast<unsigned long>(info.chipId), static_cast<unsigned long>(info.hartInfo));
  uint32_t deviceIdWord = 0;
  result = targetReadWord(CH32V003_DEVICE_ID_ADDRESS, deviceIdWord);
  if (result != TargetResult::Ok || deviceIdWord == 0 || deviceIdWord == 0xFFFFFFFFUL) {
    printTargetFailure("Target memory read", result == TargetResult::Ok ? TargetResult::InvalidTarget : result);
    return;
  }
  Serial.printf("Target memory read: OK (0x%08lX = 0x%08lX)\n",
                static_cast<unsigned long>(CH32V003_DEVICE_ID_ADDRESS),
                static_cast<unsigned long>(deviceIdWord));

  Serial.println("\nFlash contents 0x08000000 through 0x0800003F (16 x 32-bit words):");
  for (uint8_t i = 0; i < 16; ++i) {
    uint32_t val = 0;
    const uint32_t addr = CH32V003_FLASH_BASE + i * 4U;
    const TargetResult r = targetReadWord(addr, val);
    if (r == TargetResult::Ok) {
      Serial.printf("  0x%08lX: 0x%08lX\n", static_cast<unsigned long>(addr), static_cast<unsigned long>(val));
    } else {
      Serial.printf("  0x%08lX: READ FAILED (%s)\n", static_cast<unsigned long>(addr), targetResultText(r));
    }
  }
}

void onProgress(size_t bytesProcessed, size_t totalBytes, uint32_t currentAddress) {
  Serial.printf("  Progress: %u/%u bytes (at 0x%08lX)\n",
                static_cast<unsigned>(bytesProcessed),
                static_cast<unsigned>(totalBytes),
                static_cast<unsigned long>(currentAddress));
}

void runCommand(char* line) {
  char* context = nullptr;
  const char* command = strtok_r(line, " ", &context);
  if (command == nullptr) return;
  if (strcmp(command, "detect") == 0) {
    runDetect();
  } else if (strcmp(command, "unlock") == 0) {
    uint32_t ctlr = 0;
    targetReadWord(0x40022010UL, ctlr);
    Serial.printf("FLASH_CTLR before unlock: 0x%08lX\n", (unsigned long)ctlr);

    const TargetResult result = targetUnlockFlash();

    targetReadWord(0x40022010UL, ctlr);
    Serial.printf("FLASH_CTLR after unlock:  0x%08lX\n", (unsigned long)ctlr);

    if (result == TargetResult::Ok) {
      Serial.println("Unlock: OK");
    } else {
      printTargetFailure("Unlock", result);
    }
  } else if (strcmp(command, "erase") == 0) {
    const char* confirm = strtok_r(nullptr, " ", &context);
    if (confirm == nullptr || strcmp(confirm, "confirm") != 0) {
      Serial.println("Erase refused. Use: erase confirm");
      return;
    }
    Serial.println("Starting controlled page erase test (64 bytes at 0x08000000)...");
    uint32_t origData[16] = {0};
    uint32_t erasedData[16] = {0};

    const TargetResult result = targetTestPageErase(CH32V003_FLASH_BASE, origData, erasedData);

    Serial.println("Original Flash Contents (first 4 words at 0x08000000):");
    for (int i = 0; i < 4; ++i) {
      Serial.printf("  0x%08lX: 0x%08lX\n", (unsigned long)(CH32V003_FLASH_BASE + i * 4), (unsigned long)origData[i]);
    }

    Serial.println("Post-Erase 16-Word Flash Readback (0x08000000 - 0x0800003F):");
    for (int i = 0; i < 16; ++i) {
      Serial.printf("  0x%08lX: 0x%08lX\n", (unsigned long)(CH32V003_FLASH_BASE + i * 4), (unsigned long)erasedData[i]);
    }

    if (result == TargetResult::Ok) {
      Serial.println("Final Erase Verification: OK (All 64 bytes verified 0xFFFFFFFF)");
    } else {
      printTargetFailure("Final Erase Verification", result);
    }
  } else if (strcmp(command, "testprogram") == 0 || strcmp(command, "program") == 0) {
    const char* confirm = strtok_r(nullptr, " ", &context);
    if (confirm == nullptr || strcmp(confirm, "confirm") != 0) {
      Serial.println("Program refused. Use: testprogram confirm");
      return;
    }
    Serial.println("Starting core API 64-byte binary programming test at 0x08000000...");
    
    TargetInfo info{};
    TargetResult detectRes = targetDetect(info);
    if (detectRes != TargetResult::Ok) {
      printTargetFailure("Target detect", detectRes);
      return;
    }
    Serial.printf("Target detect: OK (CH32 ID = 0x%08lX, DMHARTINFO = 0x%08lX)\n",
                  static_cast<unsigned long>(info.chipId), static_cast<unsigned long>(info.hartInfo));

    uint8_t pattern[64];
    for (uint8_t i = 0; i < 64; ++i) {
      pattern[i] = i;  // Deterministic 0x00..0x3F payload
    }

    Serial.println("Executing targetProgramBinary()...");
    TargetResult result = targetProgramBinary(CH32V003_FLASH_BASE, pattern, 64, onProgress);
    if (result != TargetResult::Ok) {
      printTargetFailure("targetProgramBinary", result);
      return;
    }
    Serial.println("targetProgramBinary: OK");

    Serial.println("Executing targetVerifyBinary()...");
    result = targetVerifyBinary(CH32V003_FLASH_BASE, pattern, 64, onProgress);
    if (result != TargetResult::Ok) {
      printTargetFailure("targetVerifyBinary", result);
      return;
    }
    Serial.println("targetVerifyBinary: OK");

    uint8_t readbackBuffer[64] = {0};
    targetReadMemory(CH32V003_FLASH_BASE, readbackBuffer, 64);
    Serial.println("Programmed 64-Byte Readback (16 x 32-bit words at 0x08000000):");
    for (int i = 0; i < 16; ++i) {
      uint32_t wVal = 0;
      memcpy(&wVal, &readbackBuffer[i * 4], sizeof(wVal));
      Serial.printf("  0x%08lX: 0x%08lX\n", (unsigned long)(CH32V003_FLASH_BASE + i * 4), (unsigned long)wVal);
    }
    Serial.println("Verification Result: OK (0 mismatches)");
  } else if (strcmp(command, "flash") == 0 || strcmp(command, "verify") == 0) {
    const char* addressText = strtok_r(nullptr, " ", &context);
    const char* hexData = strtok_r(nullptr, " ", &context);
    if (addressText == nullptr || hexData == nullptr) {
      Serial.printf("Usage: %s <hex-address> <hex-data-string>\n", command);
      return;
    }
    char* end = nullptr;
    const uint32_t address = static_cast<uint32_t>(strtoul(addressText, &end, 16));
    static uint8_t payloadBuffer[512];
    size_t payloadLen = 0;
    if (*end != 0 || !parseArbitraryHexBytes(hexData, payloadBuffer, sizeof(payloadBuffer), payloadLen)) {
      Serial.println("Invalid address or hex data string (must be even number of valid hex characters).");
      return;
    }
    const TargetResult result = strcmp(command, "flash") == 0
                                    ? targetProgramBinary(address, payloadBuffer, payloadLen, onProgress)
                                    : targetVerifyBinary(address, payloadBuffer, payloadLen, onProgress);
    if (result == TargetResult::Ok) {
      Serial.printf("%s: OK (%u bytes processed at 0x%08lX)\n", command, static_cast<unsigned>(payloadLen), (unsigned long)address);
    } else {
      printTargetFailure(command, result);
    }
  } else if (strcmp(command, "reset") == 0) {
    const TargetResult result = targetResetRun();
    if (result == TargetResult::Ok) {
      Serial.println("Reset/run: OK");
    } else {
      printTargetFailure("Reset/run", result);
    }
  } else {
    Serial.println("Commands: detect | unlock | erase confirm | testprogram confirm | flash <addr> <hex> | verify <addr> <hex> | reset");
  }
}

void pollCommands() {
  while (Serial.available()) {
    const char c = static_cast<char>(Serial.read());
    if (c == '\r') continue;
    if (c == '\n') {
      commandLine[commandLength] = 0;
      runCommand(commandLine);
      commandLength = 0;
    } else if (commandLength < sizeof(commandLine) - 1) {
      commandLine[commandLength++] = c;
    } else {
      commandLength = 0;
      Serial.println("Command too long");
    }
  }
}

}  // namespace

void setup() {
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("ESP32-S3 CH32 Programmer");

  if (!swioInit()) {
    Serial.println("SWIO init: FAILED");
    return;
  }
  Serial.println("SWIO init: OK");
  Serial.printf("SWIO timing: upstream PrecDelay(10) measured ~%lu CPU cycles\n",
                static_cast<unsigned long>(swioMeasureUpstreamT1Cycles()));

  swioSynchronize();
  uint32_t configValue = 0;
  DmiResult result = dmiSynchronize(configValue);
  if (result != DmiResult::Ok) {
    printFailure("SWIO sync", result);
    Serial.printf("DMCFGR (0x%02X) read: 0x%08lX\n", DMI_CONFIG,
                  static_cast<unsigned long>(configValue));
    return;
  }
  Serial.printf("SWIO sync: OK (DMCFGR 0x%02X = 0x%08lX)\n", DMI_CONFIG,
                static_cast<unsigned long>(configValue));

  uint32_t dmstatus = 0;
  result = dmiReadReg32(DMI_DMSTATUS, dmstatus);
  if (result != DmiResult::Ok || dmstatus == 0 || dmstatus == 0xFFFFFFFFUL) {
    printFailure("DMI communication",
                 result == DmiResult::Ok ? DmiResult::InvalidResponse : result);
    Serial.printf("DMSTATUS (0x%02X) read: 0x%08lX\n", DMI_DMSTATUS,
                  static_cast<unsigned long>(dmstatus));
    return;
  }
  Serial.printf("DMI communication: OK (DMSTATUS 0x%02X = 0x%08lX)\n",
                DMI_DMSTATUS, static_cast<unsigned long>(dmstatus));

  runDetect();
  Serial.println("Commands: detect | unlock | erase confirm | flash <addr> <128hex> | verify <addr> <128hex> | reset");
}

void loop() {
  pollCommands();
}
