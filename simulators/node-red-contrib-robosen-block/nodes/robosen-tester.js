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

  function RobosenTesterNode(config) {
    RED.nodes.createNode(this, config);
    const node = this;

    node.command = config.command || "punch_left";
    node.autoConnect = config.autoConnect !== false;
    node.daemonPath = getDaemonScriptPath();

    node.pyDaemon = null;
    node.isConnected = false;
    node.robotInfo = { name: "K1", battery: "--", volume: "--", firmware: "--", address: "" };
    node.lastEvent = "Initialized";
    node.currentActionResolver = null;

    // Start background persistent BLE daemon
    node.startDaemon = function () {
      if (node.pyDaemon && node.pyDaemon.exitCode === null) {
        return; // Already running
      }

      node.status({ fill: "yellow", shape: "ring", text: "Connecting to K1..." });
      node.lastEvent = "Connecting to K1 over Bluetooth BLE...";

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
            const data = JSON.parse(trimmed);
            handleDaemonEvent(data);
          } catch (e) {
            node.log(`[Tester Daemon Raw]: ${trimmed}`);
          }
        }
      });

      node.pyDaemon.stderr.on("data", (err) => {
        node.warn(`[Tester Daemon Error]: ${err.toString().trim()}`);
      });

      node.pyDaemon.on("close", (code) => {
        node.isConnected = false;
        node.lastEvent = `Daemon disconnected (code ${code})`;
        node.status({ fill: "red", shape: "ring", text: "Disconnected" });
      });

      node.pyDaemon.on("error", (err) => {
        node.isConnected = false;
        node.lastEvent = `Error: ${err.message}`;
        node.status({ fill: "red", shape: "dot", text: "Launch Error" });
      });
    };

    function handleDaemonEvent(data) {
      switch (data.event) {
        case "connecting":
          node.lastEvent = data.message || "Connecting...";
          node.status({ fill: "yellow", shape: "ring", text: "Connecting..." });
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
          node.lastEvent = `Connected to ${node.robotInfo.name} (${node.robotInfo.battery}%)`;
          node.status({
            fill: "green",
            shape: "dot",
            text: `Connected (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
          });
          node.send({
            topic: "robot_connected",
            payload: {
              status: "connected",
              robot: node.robotInfo,
              timestamp: new Date().toISOString(),
            },
          });
          break;

        case "status_update":
          if (data.battery !== undefined) node.robotInfo.battery = data.battery;
          if (data.volume !== undefined) node.robotInfo.volume = data.volume;
          if (node.isConnected) {
            node.status({
              fill: "green",
              shape: "dot",
              text: `Connected (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
            });
          }
          break;

        case "action_progress":
          node.lastEvent = `Progress: ${data.progress}%`;
          node.status({ fill: "blue", shape: "dot", text: `Action Progress: ${data.progress}%` });
          node.send({
            topic: "action_progress",
            payload: { progress: data.progress, timestamp: Date.now() },
          });
          break;

        case "action_started":
          node.lastEvent = `Executing: ${data.action}`;
          node.status({ fill: "blue", shape: "dot", text: `Running: ${data.action}` });
          break;

        case "action_completed":
          node.lastEvent = `Completed: ${data.action}`;
          if (node.isConnected) {
            node.status({
              fill: "green",
              shape: "dot",
              text: `Ready (${node.robotInfo.name}, ${node.robotInfo.battery}%)`,
            });
          }
          if (node.currentActionResolver) {
            node.currentActionResolver(data);
            node.currentActionResolver = null;
          }
          node.send({
            topic: "action_complete",
            payload: {
              status: "success",
              action: data.action,
              timestamp: new Date().toISOString(),
            },
          });
          break;

        case "action_failed":
          node.lastEvent = `Failed: ${data.error || "unknown"}`;
          node.status({ fill: "red", shape: "dot", text: `Failed: ${data.action}` });
          if (node.currentActionResolver) {
            node.currentActionResolver(data);
            node.currentActionResolver = null;
          }
          node.send({
            topic: "action_error",
            payload: {
              status: "failed",
              action: data.action,
              error: data.error,
              timestamp: new Date().toISOString(),
            },
          });
          break;

        case "connect_failed":
          node.isConnected = false;
          node.lastEvent = data.error || "Connection failed";
          node.status({ fill: "red", shape: "ring", text: "Connection Failed" });
          break;

        case "disconnected":
          node.isConnected = false;
          node.lastEvent = "Disconnected cleanly";
          node.status({ fill: "red", shape: "ring", text: "Disconnected" });
          break;
      }
    }

    // Execute an action on the robot
    node.executeAction = function (actionName) {
      const act = actionName || node.command;
      return new Promise((resolve) => {
        if (!node.pyDaemon || !node.pyDaemon.stdin.writable) {
          node.warn("Daemon not running or not writable. Starting daemon...");
          node.startDaemon();
          return resolve({ status: "error", message: "Connecting to robot... please retry in a moment." });
        }
        node.currentActionResolver = resolve;
        node.pyDaemon.stdin.write(JSON.stringify({ cmd: "action", action: act }) + "\n");
      });
    };

    // Connect manually
    node.connectRobot = function () {
      if (!node.pyDaemon || node.pyDaemon.exitCode !== null) {
        node.startDaemon();
      } else {
        node.pyDaemon.stdin.write(JSON.stringify({ cmd: "connect" }) + "\n");
      }
    };

    // Disconnect manually
    node.disconnectRobot = function () {
      if (node.pyDaemon && node.pyDaemon.stdin.writable) {
        node.pyDaemon.stdin.write(JSON.stringify({ cmd: "disconnect" }) + "\n");
      }
    };

    // Query status manually
    node.queryStatus = function () {
      if (node.pyDaemon && node.pyDaemon.stdin.writable) {
        node.pyDaemon.stdin.write(JSON.stringify({ cmd: "status" }) + "\n");
      }
    };

    // Message input handler
    node.on("input", function (msg, send, done) {
      const targetAction = (typeof msg.payload === "string" && msg.payload.length > 0) ? msg.payload : (msg.action || node.command);
      node.executeAction(targetAction).then((res) => {
        if (done) done();
      });
    });

    // Node cleanup on close
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

    if (node.autoConnect) {
      node.startDaemon();
    } else {
      node.status({ fill: "grey", shape: "ring", text: "Disconnected (Manual Mode)" });
    }
  }

  RED.nodes.registerType("robosen-tester", RobosenTesterNode);

  // 1. Trigger from canvas button
  RED.httpAdmin.post("/robosen-tester/:id/trigger", RED.auth.needsPermission("robosen-tester.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      node.executeAction(node.command);
      res.sendStatus(200);
    } else {
      res.sendStatus(404);
    }
  });

  // 2. Execute action from properties dialog
  RED.httpAdmin.post("/robosen-tester/:id/execute", RED.auth.needsPermission("robosen-tester.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      const action = req.body && req.body.action ? req.body.action : node.command;
      node.executeAction(action);
      res.json({ status: "executing", action: action });
    } else {
      res.sendStatus(404);
    }
  });

  // 3. Connect from properties dialog
  RED.httpAdmin.post("/robosen-tester/:id/connect", RED.auth.needsPermission("robosen-tester.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      node.connectRobot();
      res.json({ status: "connecting" });
    } else {
      res.sendStatus(404);
    }
  });

  // 4. Disconnect from properties dialog
  RED.httpAdmin.post("/robosen-tester/:id/disconnect", RED.auth.needsPermission("robosen-tester.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      node.disconnectRobot();
      res.json({ status: "disconnecting" });
    } else {
      res.sendStatus(404);
    }
  });

  // 5. Query status from properties dialog
  RED.httpAdmin.post("/robosen-tester/:id/status", RED.auth.needsPermission("robosen-tester.write"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      node.queryStatus();
      res.json({ status: "queried" });
    } else {
      res.sendStatus(404);
    }
  });

  // 6. Get live info for properties dialog
  RED.httpAdmin.get("/robosen-tester/:id/info", RED.auth.needsPermission("robosen-tester.read"), function (req, res) {
    const node = RED.nodes.getNode(req.params.id);
    if (node != null) {
      res.json({
        isConnected: node.isConnected,
        robotInfo: node.robotInfo,
        lastEvent: node.lastEvent,
        command: node.command,
      });
    } else {
      res.sendStatus(404);
    }
  });
};
