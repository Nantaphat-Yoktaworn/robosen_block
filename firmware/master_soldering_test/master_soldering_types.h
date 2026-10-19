#pragma once
#include <Arduino.h>

struct ButtonState {
  int pin;
  const char* name;
  bool isPressed;
  bool lastRawState;
  unsigned long lastDebounceTime;
  unsigned long pressStartTime;
  uint32_t pressCount;
  uint32_t lastHoldDurationMs;
};

struct EncoderState {
  int pinClk;
  int pinDt;
  int pinSw;
  const char* name;
  int position;
  int lastClk;
  bool swPressed;
  bool lastSwRaw;
  unsigned long lastDebounceTime;
  unsigned long swPressStartTime;
  uint32_t swPressCount;
  uint32_t lastHoldDurationMs;
};
