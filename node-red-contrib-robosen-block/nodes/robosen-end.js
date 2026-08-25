"use strict";

module.exports = function (RED) {
  function RobosenEndNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.status({ fill: "grey", shape: "ring", text: "Passive Loopback Ready" });

    node.on("input", function (msg, send, done) {
      const _send = send || function () { node.send.apply(node, arguments); };

      if (typeof msg.payload === "string") {
        node.status({ fill: "green", shape: "dot", text: "Loopback TX -> RX Rail" });

        setTimeout(() => {
          node.status({ fill: "grey", shape: "ring", text: "Passive Loopback Ready" });
        }, 1500);

        const outMsg = Object.assign({}, msg, {
          loopback: true,
          returnedAt: Date.now(),
        });

        _send(outMsg);
      } else {
        node.warn("End block received non-string payload: " + typeof msg.payload);
      }

      if (done) {
        done();
      }
    });
  }

  RED.nodes.registerType("robosen-end", RobosenEndNode);
};
