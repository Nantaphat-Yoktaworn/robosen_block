"use strict";

const { parseCompilationFrame, parseBroadcastFrame, crc8 } = require("../lib/protocol");

module.exports = function (RED) {
  function RobosenProtocolMonitorNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.status({ fill: "grey", shape: "ring", text: "Bus Sniffer Idle" });

    node.on("input", function (msg, send, done) {
      let analysis = null;

      if (Buffer.isBuffer(msg.payload)) {
        const header = msg.payload[0];

        if (header === 0xaa) {
          // Phase 1 Compilation Frame
          const parsed = parseCompilationFrame(msg.payload);
          analysis = {
            frameType: "PHASE_1_DISCOVERY",
            header: "0xAA",
            valid: parsed.valid,
            packetLength: parsed.packetLen,
            blockCount: parsed.blockCount,
            blocks: parsed.blocks,
            crcHex: parsed.crcHex,
            calculatedCrc: parsed.calculatedCrc,
            error: parsed.error,
            rawHex: parsed.rawHex,
            timestamp: new Date().toISOString(),
          };

          if (parsed.valid) {
            node.status({
              fill: "green",
              shape: "dot",
              text: `0xAA Frame: ${parsed.blockCount} Blocks [CRC: ${parsed.crcHex} OK]`,
            });
          } else {
            node.status({
              fill: "red",
              shape: "dot",
              text: `0xAA CRC ERROR: ${parsed.error}`,
            });
          }
        } else if (header === 0xbb) {
          // Phase 2 Broadcast Frame
          const parsed = parseBroadcastFrame(msg.payload);
          analysis = {
            frameType: "PHASE_2_BROADCAST",
            header: "0xBB",
            valid: parsed.valid,
            activeStep: parsed.activeStep,
            totalSteps: parsed.totalSteps,
            isComplete: parsed.isComplete,
            rawHex: parsed.rawHex,
            timestamp: new Date().toISOString(),
          };

          if (parsed.isComplete) {
            node.status({ fill: "green", shape: "dot", text: "0xBB Broadcast: Program Complete" });
          } else {
            node.status({
              fill: "yellow",
              shape: "dot",
              text: `0xBB Step ${parsed.activeStep}/${parsed.totalSteps} Active`,
            });
          }
        }
      } else if (typeof msg.payload === "string") {
        analysis = {
          frameType: "LEGACY_STRING_CSV",
          payload: msg.payload,
          tokenCount: msg.payload.split(",").length,
          timestamp: new Date().toISOString(),
        };
        node.status({ fill: "blue", shape: "ring", text: `CSV String: ${msg.payload.substring(0, 25)}...` });
      }

      // Output 1: Pass-through untouched
      // Output 2: Protocol Analysis JSON
      send([
        msg,
        {
          topic: "protocol_analysis",
          payload: analysis,
        },
      ]);

      if (done) done();
    });
  }

  RED.nodes.registerType("robosen-protocol-monitor", RobosenProtocolMonitorNode);
};
