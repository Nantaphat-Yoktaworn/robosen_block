"use strict";

const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

module.exports = function (RED) {
  function getDaemonScriptPath() {
    const candidates = [
      path.resolve(__dirname, "../../scripts/k1_ble_daemon.py"),
      path.resolve(__dirname, "../../../scripts/k1_ble_daemon.py"),
      path.resolve(__dirname, "../scripts/k1_ble_daemon.py"),
      "C:/Users/poomz/nnnn/robosen_block/scripts/k1_ble_daemon.py",
    ];
    for (const p of candidates) {
      if (fs.existsSync(p)) {
        return p;
      }
    }
    return candidates[candidates.length - 1];
  }

  function RobosenLegacyMasterNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.mode = config.mode || "live"; // "live" or "sim"
    node.stepDelay = config.stepDelay !== undefined && config.stepDelay !== "" ? parseInt(config.stepDelay, 10) : 0;
    node.daemonPath = getDaemonScriptPath();

    node.pyDaemon = null;
    node.isConnected = false;
    node.robotInfo = { name: "K1", battery: "--", volume: "--", firmware: "--" };
    node.lastEvent = "Ready";
    node.currentActionResolver = null;
    let chainTimeout = null;

    // Command mapping dictionary
    const ACTION_MAP = {
      move_forward: "walk",
      move_backward: "move_backward",
      turn_left: "turn_left",
      turn_right: "turn_right",
      move_left: "move_left",
      move_right: "move_right",
      left_punch: "punch_left",
      right_punch: "punch_right",
      kung_fu: "kung_fu",
      boogaloo: "boogaloo",
      single_kick: "single_kick",
      push_ups: "push_ups",
      handstand: "handstand",
      do_squats: "do_squats",
      say_hello: "say_hello",
      celebrate: "celebrate",
      default_stand: "default_stand",
      stand: "default_stand",
      stand_posture: "default_stand",
      head_left: "head_left",
      head_right: "head_right",
      head_center: "head_center",
      head_pan: "head_pan",
      wait_delay: "delay",
      walk: "walk",
      punch_left: "punch_left",
      punch_right: "punch_right",
      delay: "delay",
    };

    // 1. Initialize persistent BLE daemon on startup
    function startDaemon() {
      if (node.mode !== "live") {
        node.status({ fill: "blue", shape: "dot", text: "Simulation Mode Active" });
        return;
      }

      node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1 via BLE..." });
      node.lastEvent = "Starting persistent BLE daemon...";

      node.pyDaemon = spawn("python", [node.daemonPath], {
        windowsHide: true,
      });

      let lineBuffer = "";

      node.pyDaemon.stdout.on("data", (chunk) => {
        lineBuffer += chunk.toString();
        const lines = lineBuffer.split("\n");
        lineBuffer = lines.pop();

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            const msg = JSON.parse(trimmed);
            handleDaemonEvent(msg);
          } catch (e) {
            node.log(`[Legacy Daemon Raw]: ${trimmed}`);
          }
        }
      });

      node.pyDaemon.stderr.on("data", (err) => {
        node.warn(`[Legacy Daemon Error]: ${err.toString().trim()}`);
      });

      node.pyDaemon.on("close", (code) => {
        node.isConnected = false;
        node.lastEvent = "BLE daemon exited";
        node.status({ fill: "red", shape: "ring", text: "Disconnected (Daemon stopped)" });
      });

      node.pyDaemon.on("error", (err) => {
        node.isConnected = false;
        node.lastEvent = `Failed to launch daemon: ${err.message}`;
        node.status({ fill: "red", shape: "dot", text: "Daemon Launch Error" });
      });
    }

    // 2. Handle daemon events
    function handleDaemonEvent(data) {
      switch (data.event) {
        case "connecting":
          node.lastEvent = data.message || "Scanning & connecting to K1...";
          node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1..." });
          break;

        case "connected":
          node.isConnected = true;
          node.robotInfo = {
            name: data.name || "K1",
            battery: data.battery !== undefined ? data.battery : "--",
            volume: data.volume || "--",
            firmware: data.firmware || "--",
            address: data.address || "",
          };
          node.lastEvent = `Connected to ${node.robotInfo.name} (${node.robotInfo.address})`;
          node.status({
            fill: "green",
            shape: "dot",
            text: `Connected (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
          });
          node.send([
            null,
            {
              topic: "robot_connected",
              payload: {
                status: "connected",
                robot: node.robotInfo,
                timestamp: new Date().toISOString(),
              },
            },
          ]);
          break;

        case "status_update":
          if (data.battery !== undefined) node.robotInfo.battery = data.battery;
          if (data.volume !== undefined) node.robotInfo.volume = data.volume;
          node.lastEvent = `Telemetry: Battery ${node.robotInfo.battery}%, Volume ${node.robotInfo.volume}`;
          if (node.isConnected) {
            node.status({
              fill: "green",
              shape: "dot",
              text: `Connected (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
            });
          }
          break;

        case "firmware_info":
          if (data.firmware) node.robotInfo.firmware = data.firmware;
          break;

        case "action_progress":
          node.lastEvent = `Action Progress: ${data.progress}%`;
          node.send([
            null,
            {
              topic: "action_progress",
              payload: { progress: data.progress, timestamp: Date.now() },
            },
          ]);
          break;

        case "action_completed":
          node.lastEvent = `Action Completed: ${data.action || ""}`;
          if (node.currentActionResolver) {
            node.currentActionResolver(data);
            node.currentActionResolver = null;
          }
          break;

        case "action_failed":
          node.lastEvent = `Action Failed: ${data.error || ""}`;
          if (node.currentActionResolver) {
            node.currentActionResolver(data);
            node.currentActionResolver = null;
          }
          break;

        case "connect_failed":
          node.isConnected = false;
          node.lastEvent = data.error || "Connection Failed";
          node.status({ fill: "red", shape: "ring", text: "Connection Failed" });
          break;

        case "disconnected":
          node.isConnected = false;
          node.lastEvent = "Disconnected from K1";
          node.status({ fill: "red", shape: "ring", text: "Disconnected" });
          break;
      }
    }

    // 3. Send command to persistent daemon over stdin with safety timeout
    function sendDaemonCommand(cmdObj, timeoutMs = 15000) {
      return new Promise((resolve) => {
        if (!node.pyDaemon || !node.pyDaemon.stdin.writable) {
          return resolve({ event: "action_failed", error: "Daemon stdin not writable" });
        }
        let timer = setTimeout(() => {
          node.currentActionResolver = null;
          node.warn(`[Legacy Master] Command '${cmdObj.action || cmdObj.cmd}' timed out after ${timeoutMs}ms. Advancing queue.`);
          resolve({ event: "action_timeout", error: "Command timed out" });
        }, timeoutMs);

        node.currentActionResolver = (res) => {
          clearTimeout(timer);
          resolve(res);
        };

        try {
          node.pyDaemon.stdin.write(JSON.stringify(cmdObj) + "\n");
        } catch (e) {
          clearTimeout(timer);
          resolve({ event: "action_failed", error: e.message });
        }
      });
    }

    node.connectRobot = function () {
      if (node.mode !== "live") return;
      if (!node.pyDaemon) {
        startDaemon();
      } else {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "connect" }) + "\n");
        } catch (e) {
          startDaemon();
        }
      }
    };

    node.disconnectRobot = function () {
      if (node.pyDaemon) {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "disconnect" }) + "\n");
        } catch (e) {}
      }
      node.isConnected = false;
      node.status({ fill: "red", shape: "ring", text: "Disconnected" });
    };

    node.queryStatus = function () {
      if (node.pyDaemon) {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "status" }) + "\n");
        } catch (e) {}
      }
    };

    // 4. Trigger downstream string transmission ("start")
    node.startChain = function () {
      if (chainTimeout) clearTimeout(chainTimeout);

      node.status({ fill: "blue", shape: "ring", text: "Transmitting 'start'..." });
      const msg = {
        payload: "start",
        chain: ["start"],
        source: "legacy-master",
        timestamp: Date.now(),
      };

      // Output 1: Downstream String TX
      // Output 2: Telemetry
      node.send([
        msg,
        {
          topic: "status",
          payload: {
            event: "chain_started",
            protocol: "legacy_string",
            message: "Legacy Master Block sent 'start' string down Pin 3 TX rail",
            timestamp: Date.now(),
          },
        },
      ]);

      // Safety timeout if return rail is disconnected
      chainTimeout = setTimeout(() => {
        node.status({ fill: "red", shape: "ring", text: "Chain Broken: Loopback wire not connected to Master Input!" });
        node.warn("[Legacy Master] 'start' string sent, but no return string received within 4s. Connect End Block output back to Master input.");
      }, 4000);
    };

    // 5. Action execution queue for CSV tokens
    async function executeQueue(tokens, originalMsg) {
      if (chainTimeout) clearTimeout(chainTimeout);
      const totalSteps = tokens.length;
      node.status({ fill: "yellow", shape: "dot", text: `Executing ${totalSteps} steps...` });

      node.send([
        null,
        {
          topic: "execution_start",
          payload: {
            totalSteps,
            commands: tokens,
            mode: node.mode,
            timestamp: new Date().toISOString(),
          },
        },
      ]);

      for (let i = 0; i < totalSteps; i++) {
        const cmd = tokens[i];
        const stepNum = i + 1;

        node.status({ fill: "yellow", shape: "dot", text: `Step ${stepNum}/${totalSteps}: ${cmd}` });

        node.send([
          null,
          {
            topic: "step_executing",
            payload: {
              step: stepNum,
              totalSteps,
              command: cmd,
              timestamp: new Date().toISOString(),
            },
          },
        ]);

        if (node.mode === "live") {
          const resolvedAction = ACTION_MAP[cmd] || cmd;
          if (resolvedAction === "delay") {
            await new Promise((r) => setTimeout(r, 2000));
          } else {
            const result = await sendDaemonCommand({ cmd: "action", action: resolvedAction });
            node.log(`[Legacy Master] Step ${stepNum} [${resolvedAction}] Result: ${JSON.stringify(result)}`);

            node.send([
              null,
              {
                topic: "step_result",
                payload: {
                  step: stepNum,
                  command: cmd,
                  action: resolvedAction,
                  result,
                },
              },
            ]);
          }
        } else {
          // Simulation mode delay
          const simDelay = cmd === "wait_delay" ? 2000 : 1500;
          await new Promise((r) => setTimeout(r, simDelay));
        }

        // Inter-step stabilization delay
        if (node.stepDelay > 0) {
          await new Promise((r) => setTimeout(r, node.stepDelay));
        }
      }

      if (node.isConnected) {
        node.status({
          fill: "green",
          shape: "dot",
          text: `Completed (${totalSteps} steps) - Ready`,
        });
      } else {
        node.status({ fill: "grey", shape: "dot", text: `Completed (${totalSteps} steps)` });
      }

      node.send([
        null,
        {
          topic: "execution_complete",
          payload: {
            status: "success",
            totalSteps,
            commands: tokens,
            completedAt: new Date().toISOString(),
          },
        },
      ]);
    }

    // Handle incoming return strings on Input 1
    node.on("input", function (msg, send, done) {
      if (chainTimeout) clearTimeout(chainTimeout);

      let payloadStr = "";
      if (typeof msg.payload === "string") {
        payloadStr = msg.payload;
      } else if (Buffer.isBuffer(msg.payload)) {
        payloadStr = msg.payload.toString("utf8");
      }

      if (payloadStr.startsWith("start")) {
        const tokens = payloadStr
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t.length > 0 && t !== "start");

        if (tokens.length === 0) {
          node.status({ fill: "grey", shape: "ring", text: "Empty chain (No commands)" });
          node.send([null, { topic: "status", payload: "No command blocks connected in chain." }]);
        } else {
          node.log(`[Legacy Master] Valid CSV Program: ${tokens.length} commands: [${tokens.join(", ")}]`);
          executeQueue(tokens, msg).then(() => {
            if (done) done();
          });
        }
      } else if (msg.topic === "start" || msg.payload === true || msg.payload === "trigger") {
        node.startChain();
        if (done) done();
      } else {
        node.warn("Legacy Master received unexpected input payload: " + JSON.stringify(msg.payload));
        if (done) done();
      }
    });

    node.on("close", function (done) {
      if (node.pyDaemon) {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "exit" }) + "\n");
        } catch (e) {}
        setTimeout(() => {
          try {
            node.pyDaemon.kill();
          } catch (e) {}
          done();
        }, 300);
      } else {
        done();
      }
    });

    startDaemon();
  }

  RED.nodes.registerType("robosen-legacy-master", RobosenLegacyMasterNode);

  RED.httpAdmin.post("/robosen-legacy-master/:id/trigger", RED.auth.needsPermission("robosen-legacy-master.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        node.startChain();
        res.sendStatus(200);
      } catch (err) {
        res.sendStatus(500);
      }
    } else {
      res.sendStatus(404);
    }
  });

  RED.httpAdmin.get("/robosen-legacy-master/:id/info", RED.auth.needsPermission("robosen-legacy-master.read"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      res.json({
        isConnected: node.isConnected,
        robotInfo: node.robotInfo,
        mode: node.mode,
        lastEvent: node.lastEvent || "Ready",
      });
    } else {
      res.sendStatus(404);
    }
  });

  RED.httpAdmin.post("/robosen-legacy-master/:id/connect", RED.auth.needsPermission("robosen-legacy-master.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        node.connectRobot();
        res.sendStatus(200);
      } catch (err) {
        res.status(500).json({ error: err.toString() });
      }
    } else {
      res.sendStatus(404);
    }
  });

  RED.httpAdmin.post("/robosen-legacy-master/:id/disconnect", RED.auth.needsPermission("robosen-legacy-master.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        node.disconnectRobot();
        res.sendStatus(200);
      } catch (err) {
        res.status(500).json({ error: err.toString() });
      }
    } else {
      res.sendStatus(404);
    }
  });

  RED.httpAdmin.post("/robosen-legacy-master/:id/status", RED.auth.needsPermission("robosen-legacy-master.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        node.queryStatus();
        res.sendStatus(200);
      } catch (err) {
        res.status(500).json({ error: err.toString() });
      }
    } else {
      res.sendStatus(404);
    }
  });
};
