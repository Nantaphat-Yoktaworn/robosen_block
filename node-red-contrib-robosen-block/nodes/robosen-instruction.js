"use strict";

module.exports = function (RED) {
  function RobosenInstructionNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.command = config.command || "move_forward";

    // Set initial visual status
    node.status({ fill: "grey", shape: "ring", text: node.command });

    node.on("input", function (msg, send, done) {
      const _send = send || function () { node.send.apply(node, arguments); };

      let incomingPayload = "";
      if (typeof msg.payload === "string") {
        incomingPayload = msg.payload.trim();
      } else if (Buffer.isBuffer(msg.payload)) {
        incomingPayload = msg.payload.toString("utf8").trim();
      } else if (msg.payload && typeof msg.payload === "object") {
        incomingPayload = msg.payload.toString ? msg.payload.toString() : "";
      }

      if (incomingPayload) {
        const mutatedPayload = `${incomingPayload},${node.command}`;

        // Visual flash showing signal propagation
        node.status({ fill: "blue", shape: "dot", text: `+ ${node.command}` });

        setTimeout(() => {
          node.status({ fill: "grey", shape: "ring", text: node.command });
        }, 1500);

        const outMsg = Object.assign({}, msg, {
          payload: mutatedPayload,
          chain: Array.isArray(msg.chain) ? [...msg.chain, node.command] : [node.command],
          lastBlock: node.command,
        });

        _send(outMsg);
      } else {
        node.warn("Instruction block expected string payload ('start...'), but received: " + typeof msg.payload + ". If using Smart Blocks, use 'Smart Master Block' instead.");
      }

      if (done) {
        done();
      }
    });
  }

  RED.nodes.registerType("robosen-instruction", RobosenInstructionNode);
};
