"use strict";

const { TOKEN_CATALOG, NAME_TO_TOKEN_ID, appendBlockToFrame, parseBroadcastFrame } = require("../lib/protocol");

module.exports = function (RED) {
  function RobosenSmartBlockNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.tokenId = config.tokenId ? parseInt(config.tokenId, 10) : 0x01;
    node.param = config.param !== undefined && config.param !== "" ? parseInt(config.param, 10) : 3;
    node.blockName = config.name || "";
    node.myIndex = null; // Discovered dynamically during Phase 1
    node.isActive = false;

    // Ordered list of selectable action tokens for button cycling
    const CYCLE_ORDER = [0x01, 0x03, 0x04, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18, 0x19, 0x20, 0x30, 0x40];

    function getInfo() {
      return (
        TOKEN_CATALOG[node.tokenId] || {
          name: "UNKNOWN",
          label: "Unknown Action",
          action: "unknown",
          defaultParam: 1,
          paramName: "Value",
          color: "#9E9E9E",
        }
      );
    }

    // Refresh node appearance in Node-RED canvas
    node.refreshStatus = function () {
      const info = getInfo();
      const indexStr = node.myIndex ? `#${node.myIndex} ` : "";
      if (node.isActive) {
        node.status({ fill: "green", shape: "dot", text: `${indexStr}ACTIVE: ${info.label} (${node.param} ${info.paramName})` });
      } else {
        node.status({ fill: "blue", shape: "ring", text: `${indexStr}${info.label} [${info.paramName}: ${node.param}]` });
      }
    };

    node.refreshStatus();

    // Handle incoming signals
    node.on("input", function (msg, send, done) {
      // Determine if message is arriving on Pin 3 In (Downstream Pipeline) or Pin 4 (Broadcast Rail)
      const isBroadcast = msg.topic === "rx_bus_broadcast" || (Buffer.isBuffer(msg.payload) && msg.payload[0] === 0xbb) || msg.activeStep !== undefined;

      if (isBroadcast) {
        // --- PHASE 2: REAL-TIME STEP EXECUTION BROADCAST (Pin 4 RX_BUS) ---
        let activeStep = 0;
        let totalSteps = 0;

        if (Buffer.isBuffer(msg.payload) && msg.payload[0] === 0xbb) {
          const parsed = parseBroadcastFrame(msg.payload);
          if (parsed.valid) {
            activeStep = parsed.activeStep;
            totalSteps = parsed.totalSteps;
          }
        } else if (msg.payload && typeof msg.payload === "object" && msg.payload.activeStep !== undefined) {
          activeStep = msg.payload.activeStep;
          totalSteps = msg.payload.totalSteps || 0;
        } else if (msg.activeStep !== undefined) {
          activeStep = msg.activeStep;
          totalSteps = msg.totalSteps || 0;
        }

        const wasActive = node.isActive;
        node.isActive = node.myIndex !== null && activeStep === node.myIndex;

        const info = getInfo();
        const indexStr = node.myIndex ? `#${node.myIndex} ` : "";

        if (activeStep === 0xff) {
          // Victory complete state
          node.status({ fill: "green", shape: "dot", text: `${indexStr}Program Complete (Victory)` });
          node.isActive = false;
        } else if (node.isActive) {
          node.status({
            fill: "green",
            shape: "dot",
            text: `▶ ${indexStr}EXECUTING: ${info.label} (${node.param} ${info.paramName})`,
          });
        } else {
          node.status({
            fill: "grey",
            shape: "ring",
            text: `${indexStr}${info.label} [${info.paramName}: ${node.param}]`,
          });
        }

        // Emit WS2812B LED status on Output 2 (Telemetry)
        send([
          null,
          {
            topic: "led_state",
            payload: {
              index: node.myIndex,
              action: info.name,
              label: info.label,
              param: node.param,
              isActive: node.isActive,
              ledColor: node.isActive ? "#00E676" : info.color,
              timestamp: Date.now(),
            },
          },
        ]);
      } else {
        // --- PHASE 1: DISCOVERY & PROGRAM COMPILATION (Pin 3 Downstream Pipeline) ---
        const info = getInfo();

        if (Buffer.isBuffer(msg.payload) && msg.payload[0] === 0xaa) {
          // Binary protocol frame
          const currentCount = msg.payload[2] || 0;
          node.myIndex = currentCount + 1; // Dynamically assign index!

          const mutatedBuf = appendBlockToFrame(msg.payload, node.tokenId, node.param);

          node.status({ fill: "blue", shape: "dot", text: `+#${node.myIndex} ${info.label} (${node.param})` });
          setTimeout(() => node.refreshStatus(), 1200);

          const chainList = Array.isArray(msg.chain) ? [...msg.chain, { index: node.myIndex, action: info.action, param: node.param }] : [{ index: node.myIndex, action: info.action, param: node.param }];

          send([
            Object.assign({}, msg, {
              payload: mutatedBuf,
              hex: mutatedBuf.toString("hex").toUpperCase(),
              chain: chainList,
              lastBlockIndex: node.myIndex,
            }),
            {
              topic: "block_enumerated",
              payload: { index: node.myIndex, tokenId: node.tokenId, action: info.action, param: node.param },
            },
          ]);
        } else if (typeof msg.payload === "string") {
          // Legacy string compatibility
          const incomingPayload = msg.payload.trim();
          const mutatedPayload = incomingPayload ? `${incomingPayload},${info.action}` : info.action;

          const currentTokens = incomingPayload.split(",").filter((t) => t.length > 0 && t !== "start");
          node.myIndex = currentTokens.length + 1;

          node.status({ fill: "blue", shape: "dot", text: `+#${node.myIndex} ${info.label}` });
          setTimeout(() => node.refreshStatus(), 1200);

          send([
            Object.assign({}, msg, {
              payload: mutatedPayload,
              chain: Array.isArray(msg.chain) ? [...msg.chain, info.action] : [info.action],
              lastBlock: info.action,
            }),
            null,
          ]);
        }
      }

      if (done) done();
    });

    // Hardware Button Click (Cycle Action)
    node.cycleAction = function () {
      const curIdx = CYCLE_ORDER.indexOf(node.tokenId);
      const nextIdx = (curIdx + 1) % CYCLE_ORDER.length;
      node.tokenId = CYCLE_ORDER[nextIdx];
      const info = getInfo();
      node.param = info.defaultParam;
      node.refreshStatus();
      return info;
    };

    // Hardware Knob Rotate (Adjust Parameter)
    node.setParam = function (val) {
      node.param = Math.max(1, parseInt(val, 10) || 1);
      node.refreshStatus();
      return node.param;
    };
  }

  RED.nodes.registerType("robosen-smart-block", RobosenSmartBlockNode);

  // Clickable button on the node (Cycles action like physical button)
  RED.httpAdmin.post("/robosen-smart-block/:id/cycle", RED.auth.needsPermission("robosen-smart-block.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      const nextInfo = node.cycleAction();
      res.json({ success: true, tokenId: node.tokenId, action: nextInfo.name, label: nextInfo.label, param: node.param });
    } else {
      res.sendStatus(404);
    }
  });

  // Knob adjustment API
  RED.httpAdmin.post("/robosen-smart-block/:id/set-param", RED.auth.needsPermission("robosen-smart-block.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      const val = req.body && req.body.param !== undefined ? req.body.param : req.query.param;
      const updatedParam = node.setParam(val);
      res.json({ success: true, param: updatedParam });
    } else {
      res.sendStatus(404);
    }
  });
};
