"use strict";

/**
 * CRC-8 Calculation (Polynomial: 0x07 = x^8 + x^2 + x + 1, Initial: 0x00)
 */
function crc8(buffer) {
  let crc = 0x00;
  for (let i = 0; i < buffer.length; i++) {
    crc ^= buffer[i];
    for (let j = 0; j < 8; j++) {
      if (crc & 0x80) {
        crc = ((crc << 1) ^ 0x07) & 0xff;
      } else {
        crc = (crc << 1) & 0xff;
      }
    }
  }
  return crc;
}

// Token ID Catalog Mapping Table
const TOKEN_CATALOG = {
  // Locomotion
  0x01: { name: "MOVE_FORWARD", label: "Walk Forward", action: "walk", defaultParam: 3, paramName: "Steps", color: "#1E88E5" },
  0x02: { name: "MOVE_BACKWARD", label: "Walk Backward", action: "move_backward", defaultParam: 3, paramName: "Steps", color: "#1565C0" },
  0x03: { name: "TURN_LEFT", label: "Turn Left", action: "turn_left", defaultParam: 90, paramName: "Angle", color: "#00ACC1" },
  0x04: { name: "TURN_RIGHT", label: "Turn Right", action: "turn_right", defaultParam: 90, paramName: "Angle", color: "#00ACC1" },
  0x07: { name: "MOVE_LEFT", label: "Side-Step Left", action: "move_left", defaultParam: 2, paramName: "Steps", color: "#039BE5" },
  0x08: { name: "MOVE_RIGHT", label: "Side-Step Right", action: "move_right", defaultParam: 2, paramName: "Steps", color: "#039BE5" },

  // Combat & Martial Arts
  0x10: { name: "LEFT_PUNCH", label: "Left Punch", action: "punch_left", defaultParam: 1, paramName: "Style", color: "#E53935" },
  0x11: { name: "RIGHT_PUNCH", label: "Right Punch", action: "punch_right", defaultParam: 1, paramName: "Style", color: "#D32F2F" },
  0x12: { name: "KUNG_FU", label: "Kung Fu Stunt", action: "kung_fu", defaultParam: 1, paramName: "Routine", color: "#FB8C00" },

  // Stunts & Entertainment
  0x13: { name: "DANCE_BOOGALOO", label: "Boogaloo Dance", action: "boogaloo", defaultParam: 1, paramName: "Style", color: "#8E24AA" },
  0x14: { name: "PUSH_UPS", label: "Push-ups", action: "push_ups", defaultParam: 2, paramName: "Reps", color: "#6D4C41" },
  0x15: { name: "HANDSTAND", label: "Handstand", action: "handstand", defaultParam: 1, paramName: "Hold", color: "#6D4C41" },
  0x16: { name: "SINGLE_KICK", label: "Single Kick", action: "single_kick", defaultParam: 1, paramName: "Type", color: "#E53935" },
  0x17: { name: "DO_SQUATS", label: "Do Squats", action: "do_squats", defaultParam: 2, paramName: "Reps", color: "#43A047" },
  0x18: { name: "SAY_HELLO", label: "Say Hello", action: "say_hello", defaultParam: 1, paramName: "Variant", color: "#00897B" },
  0x19: { name: "CELEBRATE", label: "Celebrate Cheer", action: "celebrate", defaultParam: 1, paramName: "Style", color: "#FDD835" },

  // Head & Joint Kinematics
  0x20: { name: "HEAD_MOVE", label: "Head Pan", action: "head_pan", defaultParam: 123, paramName: "Angle", color: "#00897B" },
  0x21: { name: "DEFAULT_STAND", label: "Default Stand", action: "default_stand", defaultParam: 35, paramName: "Speed", color: "#00897B" },

  // Control Flow
  0x30: { name: "WAIT_DELAY", label: "Wait Delay", action: "delay", defaultParam: 2, paramName: "Seconds", color: "#FBC02D" },
  0x40: { name: "REPEAT_LOOP", label: "Repeat Loop", action: "repeat", defaultParam: 2, paramName: "Count", color: "#7CB342" },
};

// String to Token ID lookup
const NAME_TO_TOKEN_ID = {};
const ACTION_TO_TOKEN_ID = {};
for (const [idStr, info] of Object.entries(TOKEN_CATALOG)) {
  const id = parseInt(idStr, 10);
  NAME_TO_TOKEN_ID[info.name] = id;
  ACTION_TO_TOKEN_ID[info.action] = id;
  // Also support legacy command strings
  if (info.action === "walk") NAME_TO_TOKEN_ID["move_forward"] = id;
  if (info.action === "punch_left") NAME_TO_TOKEN_ID["left_punch"] = id;
  if (info.action === "punch_right") NAME_TO_TOKEN_ID["right_punch"] = id;
}

/**
 * Creates an initial Phase 1 Seed Frame [0xAA, Len=0, Count=0, CRC, 0x55]
 */
function createSeedFrame() {
  const payload = Buffer.from([0x00, 0x00]); // Len = 0, BlockCount = 0
  const checksum = crc8(payload);
  return Buffer.from([0xaa, 0x00, 0x00, checksum, 0x55]);
}

/**
 * Appends a block's Token ID and Parameter to a Phase 1 Binary Frame
 */
function appendBlockToFrame(frameBuf, tokenId, paramVal) {
  if (!Buffer.isBuffer(frameBuf) || frameBuf.length < 5 || frameBuf[0] !== 0xaa) {
    // If not a valid binary buffer, create a new one
    frameBuf = createSeedFrame();
  }

  const currentLen = frameBuf[1];
  const currentCount = frameBuf[2];
  const currentPayload = frameBuf.slice(3, 3 + currentLen);

  const newCount = currentCount + 1;
  const newLen = currentLen + 2;

  // New payload consists of old payload + [tokenId, paramVal]
  const newPayload = Buffer.concat([currentPayload, Buffer.from([tokenId & 0xff, paramVal & 0xff])]);
  const crcHeader = Buffer.from([newLen, newCount]);
  const fullPayloadForCrc = Buffer.concat([crcHeader, newPayload]);
  const checksum = crc8(fullPayloadForCrc);

  return Buffer.concat([Buffer.from([0xaa, newLen, newCount]), newPayload, Buffer.from([checksum, 0x55])]);
}

/**
 * Parses and verifies a Phase 1 Binary Frame (0xAA)
 */
function parseCompilationFrame(frameBuf) {
  if (!Buffer.isBuffer(frameBuf)) {
    if (typeof frameBuf === "string") {
      frameBuf = Buffer.from(frameBuf.replace(/\s+/g, ""), "hex");
    } else {
      return { valid: false, error: "Input is not a buffer or hex string" };
    }
  }

  if (frameBuf.length < 5) {
    return { valid: false, error: `Frame too short (${frameBuf.length} bytes)` };
  }

  if (frameBuf[0] !== 0xaa) {
    return { valid: false, error: `Invalid Header: 0x${frameBuf[0].toString(16)} (Expected 0xAA)` };
  }

  const packetLen = frameBuf[1];
  const blockCount = frameBuf[2];

  if (frameBuf.length !== 3 + packetLen + 2) {
    return { valid: false, error: `Length mismatch: header says ${packetLen} data bytes, frame is ${frameBuf.length} bytes` };
  }

  const footer = frameBuf[frameBuf.length - 1];
  if (footer !== 0x55) {
    return { valid: false, error: `Invalid Footer: 0x${footer.toString(16)} (Expected 0x55)` };
  }

  const receivedCrc = frameBuf[frameBuf.length - 2];
  const crcPayload = frameBuf.slice(1, frameBuf.length - 2);
  const calculatedCrc = crc8(crcPayload);

  if (receivedCrc !== calculatedCrc) {
    return {
      valid: false,
      error: `CRC Mismatch! Received 0x${receivedCrc.toString(16).padStart(2, "0")}, Calculated 0x${calculatedCrc.toString(16).padStart(2, "0")}`,
      receivedCrc,
      calculatedCrc,
    };
  }

  const blocks = [];
  const dataPayload = frameBuf.slice(3, 3 + packetLen);
  for (let i = 0; i < dataPayload.length; i += 2) {
    const tokenId = dataPayload[i];
    const param = dataPayload[i + 1] !== undefined ? dataPayload[i + 1] : 0;
    const info = TOKEN_CATALOG[tokenId] || {
      name: `UNKNOWN_0x${tokenId.toString(16)}`,
      label: `Unknown (0x${tokenId.toString(16)})`,
      action: "unknown",
      defaultParam: 0,
      paramName: "Value",
      color: "#9E9E9E",
    };

    blocks.push({
      index: blocks.length + 1,
      tokenId,
      tokenHex: `0x${tokenId.toString(16).padStart(2, "0").toUpperCase()}`,
      name: info.name,
      label: info.label,
      action: info.action,
      param,
      color: info.color,
    });
  }

  return {
    valid: true,
    frameType: "PHASE_1_DISCOVERY",
    headerHex: "0xAA",
    packetLen,
    blockCount,
    blocks,
    crc: receivedCrc,
    crcHex: `0x${receivedCrc.toString(16).padStart(2, "0").toUpperCase()}`,
    rawHex: frameBuf.toString("hex").toUpperCase(),
  };
}

/**
 * Creates a Phase 2 Step Broadcast Frame [0xBB, ActiveStep, TotalSteps, CRC, 0x55]
 */
function createBroadcastFrame(activeStep, totalSteps) {
  const payload = Buffer.from([activeStep & 0xff, totalSteps & 0xff]);
  const checksum = crc8(payload);
  return Buffer.from([0xbb, activeStep & 0xff, totalSteps & 0xff, checksum, 0x55]);
}

/**
 * Parses and verifies a Phase 2 Broadcast Frame (0xBB)
 */
function parseBroadcastFrame(frameBuf) {
  if (!Buffer.isBuffer(frameBuf)) {
    if (typeof frameBuf === "string") {
      frameBuf = Buffer.from(frameBuf.replace(/\s+/g, ""), "hex");
    } else {
      return { valid: false, error: "Input is not a buffer or hex string" };
    }
  }

  if (frameBuf.length !== 5 || frameBuf[0] !== 0xbb || frameBuf[4] !== 0x55) {
    return { valid: false, error: "Invalid 0xBB broadcast frame format" };
  }

  const activeStep = frameBuf[1];
  const totalSteps = frameBuf[2];
  const receivedCrc = frameBuf[3];
  const calculatedCrc = crc8(frameBuf.slice(1, 3));

  if (receivedCrc !== calculatedCrc) {
    return {
      valid: false,
      error: `CRC Mismatch in broadcast frame: Received 0x${receivedCrc.toString(16)}, Calculated 0x${calculatedCrc.toString(16)}`,
    };
  }

  return {
    valid: true,
    frameType: "PHASE_2_BROADCAST",
    activeStep,
    totalSteps,
    crc: receivedCrc,
    isComplete: activeStep === 0xff,
    isIdle: activeStep === 0x00,
    rawHex: frameBuf.toString("hex").toUpperCase(),
  };
}

module.exports = {
  crc8,
  TOKEN_CATALOG,
  NAME_TO_TOKEN_ID,
  ACTION_TO_TOKEN_ID,
  createSeedFrame,
  appendBlockToFrame,
  parseCompilationFrame,
  createBroadcastFrame,
  parseBroadcastFrame,
};
