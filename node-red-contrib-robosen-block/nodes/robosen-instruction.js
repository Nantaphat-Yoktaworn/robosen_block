"use strict";

module.exports = function (RED) {
  function RobosenInstructionNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.command = config.command || "move_forward";

    // Set initial visual status
    node.status({ fill: "grey", shape: "ring", text: node.command });

    node.on("input", function (msg, send, done) {
      if (typeof msg.payload === "string") {
        const incomingPayload = msg.payload.trim();
        const mutatedPayload = incomingPayload ? `${incomingPayload},${node.command}` : node.command;

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

        send(outMsg);
      } else {
        node.warn("Instruction block received non-string payload: " + typeof msg.payload);
      }

      if (done) {
        done();
      }
    });
  }

  RED.nodes.registerType("robosen-instruction", RobosenInstructionNode);
};
