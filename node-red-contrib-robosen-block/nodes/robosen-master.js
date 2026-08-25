"use strict";

const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");
const {
  createSeedFrame,
  parseCompilationFrame,
  createBroadcastFrame,
  TOKEN_CATALOG,
  NAME_TO_TOKEN_ID,
} = require("../lib/protocol");

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
    node.protocolVersion = config.protocolVersion || "binary"; // "binary" (V2) or "string" (V1)
    node.stepDelay = config.stepDelay !== undefined && config.stepDelay !== "" ? parseInt(config.stepDelay, 10) : 0;
    node.daemonPath = getDaemonScriptPath();

    node.pyDaemon = null;
    node.isConnected = false;
    node.robotInfo = { name: "K1", battery: "--", volume: "--", firmware: "--" };
    node.lastEvent = "Ready";
    node.currentActionResolver = null;

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

    // 1. Initialize persistent BLE daemon on startup (Master Block Power ON)
    function startDaemon() {
      if (node.mode !== "live") {
        node.status({ fill: "blue", shape: "dot", text: "Simulation Mode Active" });
        return;
      }

      node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1 via BLE..." });
      node.lastEvent = "Starting persistent BLE daemon...";
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
        node.lastEvent = "BLE daemon exited";
        node.log(`[Master Block] BLE daemon exited with code ${code}`);
        node.status({ fill: "red", shape: "ring", text: "Disconnected (Daemon stopped)" });
      });

      node.pyDaemon.on("error", (err) => {
        node.isConnected = false;
        node.lastEvent = `Failed to launch daemon: ${err.message}`;
        node.error(`[Master Block] Failed to launch daemon: ${err.message}`);
        node.status({ fill: "red", shape: "dot", text: "Daemon Launch Error" });
      });
    }

    // 2. Handle events streaming from persistent Python daemon
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
            null,
          ]);
          break;

        case "status_update":
          if (data.battery !== undefined) {
            node.robotInfo.battery = data.battery;
          }
          if (data.volume !== undefined) {
            node.robotInfo.volume = data.volume;
          }
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
          if (data.firmware) {
            node.robotInfo.firmware = data.firmware;
          }
          break;

        case "action_progress":
          node.lastEvent = `Action Progress: ${data.progress}%`;
          node.send([
            null,
            {
              topic: "action_progress",
              payload: { progress: data.progress, timestamp: Date.now() },
            },
            null,
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
          node.send([
            null,
            {
              topic: "robot_error",
              payload: { error: data.error, timestamp: new Date().toISOString() },
            },
            null,
          ]);
          break;

        case "disconnected":
          node.isConnected = false;
          node.lastEvent = "Disconnected from K1";
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

    // Manual connect method
    node.connectRobot = function () {
      if (node.mode !== "live") {
        node.status({ fill: "blue", shape: "dot", text: "Simulation Mode Active" });
        return;
      }
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

    // Manual disconnect method
    node.disconnectRobot = function () {
      if (node.pyDaemon) {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "disconnect" }) + "\n");
        } catch (e) {}
      }
      node.isConnected = false;
      node.status({ fill: "red", shape: "ring", text: "Disconnected" });
    };

    // Manual status query method
    node.queryStatus = function () {
      if (node.pyDaemon) {
        try {
          node.pyDaemon.stdin.write(JSON.stringify({ cmd: "status" }) + "\n");
        } catch (e) {}
      }
    };

    // 4. Function to trigger downstream transmission (Phase 1 Seed Frame)
    node.startChain = function () {
      if (node.protocolVersion === "binary") {
        const seedBuf = createSeedFrame();
        node.status({ fill: "blue", shape: "ring", text: "Transmitting 0xAA Seed Frame..." });

        const msg = {
          payload: seedBuf,
          hex: seedBuf.toString("hex").toUpperCase(),
          chain: [],
          protocol: "2-Phase Binary (CRC-8)",
          source: "master",
          timestamp: Date.now(),
        };

        // Output 1: Pin 3 Downstream TX
        // Output 2: Telemetry
        // Output 3: Broadcast Bus (Pin 4)
        node.send([
          msg,
          {
            topic: "status",
            payload: {
              event: "chain_started",
              protocol: "binary_v2",
              seedHex: seedBuf.toString("hex").toUpperCase(),
              message: "Master Block emitted Phase 1 Seed Frame [0xAA, Len=0, Count=0, CRC] on Pin 3 TX",
              timestamp: Date.now(),
            },
          },
          null,
        ]);
      } else {
        // Legacy String mode
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
              protocol: "string_v1",
              message: "Master Block sent initial 'start' seed down Pin 3 TX rail",
              timestamp: Date.now(),
            },
          },
          null,
        ]);
      }
    };

    // 5. Action execution queue (Phase 2 with Real-Time Broadcast on Output 3)
    async function executeQueue(commandObjects, originalMsg) {
      const totalSteps = commandObjects.length;
      node.status({ fill: "yellow", shape: "dot", text: `Executing ${totalSteps} steps...` });

      node.send([
        null,
        {
          topic: "execution_start",
          payload: {
            totalSteps,
            commands: commandObjects,
            mode: node.mode,
            timestamp: new Date().toISOString(),
          },
        },
        null,
      ]);

      for (let i = 0; i < totalSteps; i++) {
        const item = commandObjects[i];
        const stepNum = i + 1;
        const actionKey = item.action || item.cmd || item;
        const paramVal = item.param !== undefined ? item.param : 1;
        const label = item.label || actionKey;

        node.status({ fill: "yellow", shape: "dot", text: `Step ${stepNum}/${totalSteps}: ${label}` });

        // Phase 2 Step Broadcast Frame [0xBB, ActiveStep, TotalSteps, CRC, 0x55]
        const broadcastBuf = createBroadcastFrame(stepNum, totalSteps);

        // Broadcast to Output 3 (Pin 4 RX_BUS) so target Smart Block's LED glows bright green!
        node.send([
          null,
          {
            topic: "step_executing",
            payload: {
              step: stepNum,
              totalSteps,
              command: actionKey,
              param: paramVal,
              label,
              timestamp: new Date().toISOString(),
            },
          },
          {
            topic: "rx_bus_broadcast",
            payload: broadcastBuf,
            activeStep: stepNum,
            totalSteps,
            hex: broadcastBuf.toString("hex").toUpperCase(),
          },
        ]);

        if (node.mode === "live") {
          const resolvedAction = ACTION_MAP[actionKey] || actionKey;
          if (resolvedAction === "delay") {
            const delayMs = Math.max(1000, (parseInt(paramVal, 10) || 2) * 1000);
            await new Promise((r) => setTimeout(r, delayMs));
          } else {
            const result = await sendDaemonCommand({ cmd: "action", action: resolvedAction, param: paramVal });
            node.log(`[Master Block] Step ${stepNum} [${resolvedAction}] Result: ${JSON.stringify(result)}`);

            node.send([
              null,
              {
                topic: "step_result",
                payload: {
                  step: stepNum,
                  action: resolvedAction,
                  param: paramVal,
                  result,
                },
              },
              null,
            ]);
          }
        } else {
          // Simulation mode delay
          const simDelay = actionKey === "delay" ? (parseInt(paramVal, 10) || 2) * 1000 : 1500;
          await new Promise((r) => setTimeout(r, simDelay));
        }

        // Inter-step stabilization delay
        if (node.stepDelay > 0) {
          await new Promise((r) => setTimeout(r, node.stepDelay));
        }
      }

      // Phase 2 Victory Broadcast [0xBB, 0xFF, TotalSteps, CRC]
      const victoryBuf = createBroadcastFrame(0xff, totalSteps);

      if (node.isConnected) {
        node.status({
          fill: "green",
          shape: "dot",
          text: `Completed (${totalSteps} steps) - Ready`,
        });
      } else {
        node.status({ fill: "grey", shape: "dot", text: `Completed (${totalSteps} steps)` });
      }

      // Broadcast victory state to Output 3
      node.send([
        null,
        {
          topic: "execution_complete",
          payload: {
            status: "success",
            totalSteps,
            completedAt: new Date().toISOString(),
          },
        },
        {
          topic: "rx_bus_broadcast",
          payload: victoryBuf,
          activeStep: 0xff,
          totalSteps,
          hex: victoryBuf.toString("hex").toUpperCase(),
        },
      ]);
    }

    // Handle incoming messages on Input 1 (Pin 4 Return Rail)
    node.on("input", function (msg, send, done) {
      if (Buffer.isBuffer(msg.payload) && msg.payload[0] === 0xaa) {
        // Binary Compilation Frame received from End Block!
        const parsed = parseCompilationFrame(msg.payload);

        if (!parsed.valid) {
          node.error(`[Master Block] Binary Frame CRC Error: ${parsed.error}`);
          node.status({ fill: "red", shape: "dot", text: `CRC Error (${parsed.error})` });
          node.send([
            null,
            {
              topic: "protocol_error",
              payload: {
                error: parsed.error,
                rawHex: msg.payload.toString("hex").toUpperCase(),
              },
            },
            null,
          ]);
          if (done) done();
          return;
        }

        if (parsed.blocks.length === 0) {
          node.status({ fill: "grey", shape: "ring", text: "Empty chain (0 Blocks)" });
          if (done) done();
          return;
        }

        node.log(`[Master Block] Valid Program Received: ${parsed.blockCount} blocks, CRC: ${parsed.crcHex}`);
        executeQueue(parsed.blocks, msg).then(() => {
          if (done) done();
        });
      } else if (typeof msg.payload === "string" && msg.payload.startsWith("start")) {
        // Legacy string loopback
        const tokens = msg.payload
          .split(",")
          .map((t) => t.trim())
          .filter((t) => t.length > 0 && t !== "start");

        if (tokens.length === 0) {
          node.status({ fill: "grey", shape: "ring", text: "Empty chain (No commands)" });
        } else {
          const commandObjs = tokens.map((t) => ({ action: t, cmd: t, param: 1, label: t }));
          executeQueue(commandObjs, msg).then(() => {
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

  // HTTP endpoint to query live status & robot info
  RED.httpAdmin.get("/robosen-master/:id/info", RED.auth.needsPermission("robosen-master.read"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      res.json({
        isConnected: node.isConnected,
        robotInfo: node.robotInfo,
        mode: node.mode,
        protocolVersion: node.protocolVersion,
        lastEvent: node.lastEvent || "Ready",
      });
    } else {
      res.sendStatus(404);
    }
  });

  // HTTP endpoint to trigger manual BLE connection
  RED.httpAdmin.post("/robosen-master/:id/connect", RED.auth.needsPermission("robosen-master.write"), function (req, res) {
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

  // HTTP endpoint to trigger manual BLE disconnection
  RED.httpAdmin.post("/robosen-master/:id/disconnect", RED.auth.needsPermission("robosen-master.write"), function (req, res) {
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

  // HTTP endpoint to trigger telemetry status query
  RED.httpAdmin.post("/robosen-master/:id/status", RED.auth.needsPermission("robosen-master.write"), function (req, res) {
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
