"use strict";

const { crc8, parseCompilationFrame } = require("../lib/protocol");

module.exports = function (RED) {
  function RobosenSmartEndNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.injectError = config.injectError || false; // Option to test CRC failure handling

    node.status({ fill: "grey", shape: "ring", text: "Smart Terminator Ready" });

    node.on("input", function (msg, send, done) {
      if (Buffer.isBuffer(msg.payload)) {
        let frameBuf = Buffer.from(msg.payload);

        if (frameBuf[0] === 0xaa) {
          // If error injection is enabled, tamper with CRC
          if (node.injectError) {
            frameBuf[frameBuf.length - 2] = frameBuf[frameBuf.length - 2] ^ 0xff; // Invert CRC
            node.status({ fill: "red", shape: "dot", text: "Injected CRC Error!" });
          } else {
            const parsed = parseCompilationFrame(frameBuf);
            if (parsed.valid) {
              node.status({
                fill: "green",
                shape: "dot",
                text: `Loopback OK (${parsed.blockCount} Blocks, CRC: ${parsed.crcHex})`,
              });
            } else {
              node.status({ fill: "red", shape: "dot", text: `CRC Error: ${parsed.error}` });
            }
          }

          setTimeout(() => {
            node.status({ fill: "grey", shape: "ring", text: "Smart Terminator Ready" });
          }, 2000);

          const outMsg = Object.assign({}, msg, {
            payload: frameBuf,
            hex: frameBuf.toString("hex").toUpperCase(),
            loopback: true,
            returnedAt: Date.now(),
          });

          // Output 1: Return RX Rail (Pin 4 to Master)
          // Output 2: Diagnostics
          send([
            outMsg,
            {
              topic: "loopback_telemetry",
              payload: {
                loopback: true,
                byteLength: frameBuf.length,
                rawHex: frameBuf.toString("hex").toUpperCase(),
                timestamp: new Date().toISOString(),
              },
            },
          ]);
        }
      } else if (typeof msg.payload === "string") {
        // Legacy string loopback
        node.status({ fill: "green", shape: "dot", text: "Loopback String -> RX Rail" });
        setTimeout(() => {
          node.status({ fill: "grey", shape: "ring", text: "Smart Terminator Ready" });
        }, 1500);

        send([
          Object.assign({}, msg, {
            loopback: true,
            returnedAt: Date.now(),
          }),
          null,
        ]);
      }

      if (done) done();
    });
  }

  RED.nodes.registerType("robosen-smart-end", RobosenSmartEndNode);
};
