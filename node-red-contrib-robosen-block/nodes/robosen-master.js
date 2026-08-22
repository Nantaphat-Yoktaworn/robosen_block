"use strict";

const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

module.exports = function (RED) {
  // Helper to safely find the Python BLE daemon script across symlinks and directories
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

  function RobosenMasterNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.mode = config.mode || "live"; // "live" or "sim"
    node.stepDelay = config.stepDelay !== undefined && config.stepDelay !== "" ? parseInt(config.stepDelay, 10) : 0;
    node.daemonPath = getDaemonScriptPath();

    node.pyDaemon = null;
    node.isConnected = false;
    node.robotInfo = { name: "K1", battery: "--", volume: "--" };
    node.currentActionResolver = null;

    // Command mapping dictionary
    const ACTION_MAP = {
      move_forward: "walk",
      move_backward: "move_backward",
      turn_left: "turn_left",
      turn_right: "turn_right",
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
      head_left: "head_left",
      head_right: "head_right",
      head_center: "head_center",
      head_pan: "head_pan",
      wait_delay: "delay",
    };

    // 1. Initialize persistent BLE daemon on startup (Master Block Power ON)
    function startDaemon() {
      if (node.mode !== "live") {
        node.status({ fill: "blue", shape: "dot", text: "Simulation Mode Active" });
        return;
      }

      node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1 via BLE..." });
      node.log(`[Master Block] Starting persistent BLE daemon: ${node.daemonPath}`);

      node.pyDaemon = spawn("python", [node.daemonPath], {
        windowsHide: true,
      });

      let lineBuffer = "";

      node.pyDaemon.stdout.on("data", (chunk) => {
        lineBuffer += chunk.toString();
        const lines = lineBuffer.split("\n");
        lineBuffer = lines.pop(); // Keep incomplete line

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed) continue;
          try {
            const msg = JSON.parse(trimmed);
            handleDaemonEvent(msg);
          } catch (e) {
            node.log(`[Daemon Raw]: ${trimmed}`);
          }
        }
      });

      node.pyDaemon.stderr.on("data", (err) => {
        node.warn(`[Daemon Error]: ${err.toString().trim()}`);
      });

      node.pyDaemon.on("close", (code) => {
        node.isConnected = false;
        node.log(`[Master Block] BLE daemon exited with code ${code}`);
        node.status({ fill: "red", shape: "ring", text: "Disconnected (Daemon stopped)" });
      });

      node.pyDaemon.on("error", (err) => {
        node.isConnected = false;
        node.error(`[Master Block] Failed to launch daemon: ${err.message}`);
        node.status({ fill: "red", shape: "dot", text: "Daemon Launch Error" });
      });
    }

    // 2. Handle events streaming from persistent Python daemon
    function handleDaemonEvent(data) {
      switch (data.event) {
        case "connecting":
          node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1..." });
          break;

        case "connected":
          node.isConnected = true;
          node.robotInfo = {
            name: data.name || "K1",
            battery: data.battery !== undefined ? data.battery : "--",
            volume: data.volume || "--",
            address: data.address || "",
          };
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
          if (data.battery !== undefined) {
            node.robotInfo.battery = data.battery;
          }
          if (data.volume !== undefined) {
            node.robotInfo.volume = data.volume;
          }
          if (node.isConnected) {
            node.status({
              fill: "green",
              shape: "dot",
              text: `Connected (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
            });
          }
          break;

        case "action_progress":
          node.send([
            null,
            {
              topic: "action_progress",
              payload: { progress: data.progress, timestamp: Date.now() },
            },
          ]);
          break;

        case "action_completed":
        case "action_failed":
          if (node.currentActionResolver) {
            node.currentActionResolver(data);
            node.currentActionResolver = null;
          }
          break;

        case "connect_failed":
          node.isConnected = false;
          node.status({ fill: "red", shape: "ring", text: "Connection Failed" });
          node.send([
            null,
            {
              topic: "robot_error",
              payload: { error: data.error, timestamp: new Date().toISOString() },
            },
          ]);
          break;

        case "disconnected":
          node.isConnected = false;
          node.status({ fill: "red", shape: "ring", text: "Disconnected" });
          break;
      }
    }

    // 3. Send command to persistent daemon over stdin
    function sendDaemonCommand(cmdObj) {
      return new Promise((resolve) => {
        if (!node.pyDaemon || !node.pyDaemon.stdin.writable) {
          return resolve({ event: "action_failed", error: "Daemon stdin not writable" });
        }
        node.currentActionResolver = resolve;
        node.pyDaemon.stdin.write(JSON.stringify(cmdObj) + "\n");
      });
    }

    // 4. Function to trigger downstream string transmission ("start")
    node.startChain = function () {
      node.status({ fill: "blue", shape: "ring", text: "Transmitting 'start'..." });
      const msg = {
        payload: "start",
        chain: ["start"],
        source: "master",
        timestamp: Date.now(),
      };
      node.send([
        msg,
        {
          topic: "status",
          payload: {
            event: "chain_started",
            message: "Master Block sent initial 'start' seed down Pin 3 TX rail",
            timestamp: Date.now(),
          },
        },
      ]);
    };

    // 5. Action execution queue
    async function executeQueue(commandTokens, originalMsg) {
      node.status({ fill: "yellow", shape: "dot", text: `Executing ${commandTokens.length} steps...` });

      node.send([
        null,
        {
          topic: "execution_start",
          payload: {
            totalSteps: commandTokens.length,
            commands: commandTokens,
            mode: node.mode,
            rawProgram: originalMsg.payload,
            timestamp: new Date().toISOString(),
          },
        },
      ]);

      for (let i = 0; i < commandTokens.length; i++) {
        const cmd = commandTokens[i].trim();
        const stepNum = i + 1;

        node.status({ fill: "yellow", shape: "dot", text: `Step ${stepNum}/${commandTokens.length}: ${cmd}` });

        node.send([
          null,
          {
            topic: "step_executing",
            payload: {
              step: stepNum,
              totalSteps: commandTokens.length,
              command: cmd,
              timestamp: new Date().toISOString(),
            },
          },
        ]);

        if (node.mode === "live") {
          const actionKey = ACTION_MAP[cmd] || cmd;
          if (actionKey === "delay") {
            await new Promise((r) => setTimeout(r, 2000));
          } else {
            const result = await sendDaemonCommand({ cmd: "action", action: actionKey });
            node.log(`[Master Block] Step ${stepNum} [${actionKey}] Result: ${JSON.stringify(result)}`);

            node.send([
              null,
              {
                topic: "step_result",
                payload: {
                  step: stepNum,
                  command: cmd,
                  actionKey: actionKey,
                  result: result,
                },
              },
            ]);
          }
        } else {
          // Simulation mode delay
          await new Promise((r) => setTimeout(r, 1500));
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
          text: `Completed (${commandTokens.length} steps) - Ready`,
        });
      } else {
        node.status({ fill: "grey", shape: "dot", text: `Completed (${commandTokens.length} steps)` });
      }

      node.send([
        null,
        {
          topic: "execution_complete",
          payload: {
            status: "success",
            totalSteps: commandTokens.length,
            commands: commandTokens,
            completedAt: new Date().toISOString(),
          },
        },
      ]);
    }

    // Handle incoming messages
    node.on("input", function (msg, send, done) {
      if (typeof msg.payload === "string" && msg.payload.startsWith("start")) {
        // String returned from loopback!
        const tokens = msg.payload
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t.length > 0 && t !== "start");

        if (tokens.length === 0) {
          node.status({ fill: "grey", shape: "ring", text: "Empty chain (No commands)" });
          node.send([null, { topic: "status", payload: "No command blocks connected in chain." }]);
        } else {
          executeQueue(tokens, msg).then(() => {
            if (done) done();
          });
        }
      } else if (msg.topic === "start" || msg.payload === true || msg.payload === "trigger") {
        node.startChain();
        if (done) done();
      } else {
        node.warn("Unexpected input message to Master Block: " + JSON.stringify(msg.payload));
        if (done) done();
      }
    });

    // Cleanup on Node-RED close / redeploy
    node.on("close", function (done) {
      if (node.pyDaemon) {
        node.log("[Master Block] Terminating persistent BLE daemon on node close...");
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

    // Start persistent connection immediately
    startDaemon();
  }

  RED.nodes.registerType("robosen-master", RobosenMasterNode);

  // HTTP endpoint for the clickable button on the Master Block node
  RED.httpAdmin.post("/robosen-master/:id/trigger", RED.auth.needsPermission("robosen-master.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      try {
        node.startChain();
        res.sendStatus(200);
      } catch (err) {
        res.sendStatus(500);
        node.error("Failed to trigger master block: " + err.toString());
      }
    } else {
      res.sendStatus(404);
    }
  });
};
