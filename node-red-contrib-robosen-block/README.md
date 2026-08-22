# node-red-contrib-robosen-block

> **Custom Node-RED Palette:** Tangible Modular Coding Block Simulator & Persistent Robosen K1 BLE Robot Controller.

---

## 1. Overview & Persistent Connection Architecture

This custom Node-RED palette simulates the **physical modular coding block system** for the **Robosen K1** humanoid robot.

### ⚡ Persistent Auto-Connect Mechanism (Hardware-Accurate):
- **On Startup (Master Block Power ON):** The Master Block automatically scans, connects to the Robosen K1 over Bluetooth BLE, and maintains a **persistent long-lived connection**.
- **Instant Command Execution:** When the Start button is pressed and the loopback string arrives, actions execute **instantly** with zero BLE connection overhead.
- **Continuous Telemetry:** Streams real-time battery levels, firmware versions, and action completion percentages into Node-RED.
- **On Shutdown / Redeploy (Master Block Power OFF):** Cleanly disconnects and releases the BLE hardware adapter.

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    NODE-RED SIGNAL FLOW                                         │
│                                                                                                 │
│  [ Master Block ] ────► [ Instruction 1 ] ────► [ Instruction 2 ] ────► [ End Block Loopback ]  │
│  (TX: "start")          (+ ",move_forward")     (+ ",left_punch")       (Routes back to RX)     │
│        ▲                                                                        │               │
│        └──────────────────── Return RX ("start,move_forward,left_punch") ────────┘               │
│                    │                                                                            │
│                    ▼ (Persistent BLE 4.2 Stream)                                                │
│          [ Robosen K1 Robot ]                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Palette Node Catalog

| Node | Category | Icon / Color | Description |
| :--- | :--- | :--- | :--- |
| **`robosen-master`** | `Robosen Block` | 🔴 `#E53935` | **Master Block:** Auto-connects to the robot on boot and keeps connection alive. Has a clickable Start button in Node-RED to trigger the sequence. Receives loopback return string and dispatches actions instantly. |
| **`robosen-instruction`** | `Robosen Block` | 🔵 `#0288D1` | **Instruction Block:** Configurable dropdown commands (Walk, Turn, Left/Right Punch, Kung Fu, Boogaloo Dance, Push-ups, Handstand, Head Pan, Delay). Appends its command token. |
| **`robosen-end`** | `Robosen Block` | ⚫ `#616161` | **End Block:** Passive loopback module that connects Pin 3 TX to Pin 4 RX. |
| **`robosen-tester`** | `Robosen Block` | 🟣 `#7B1FA2` | **Action Tester (Direct Controller):** Standalone testing node. Select any action and click **⚡ Execute Action Immediately** in the node properties or canvas button. Includes live connection and battery dashboard. |

---

## 3. How to Install & Run in Node-RED

To install this custom palette into your local Node-RED instance:

```bash
# Navigate to your Node-RED user directory (typically in user home folder)
cd ~/.node-red

# Link and install the custom palette
npm install "C:/Users/poomz/nnnn/robosen_block/node-red-contrib-robosen-block"
```

Then start Node-RED:
```bash
node-red
```

---

## 4. How to Use & Import the Example Flow

1. Open your Node-RED browser interface (default: `http://127.0.0.1:1880`).
2. Click the top-right menu icon $\rightarrow$ **Import**.
3. Select and import the example flow file:  
   [`examples/robosen_simulator_flow.json`](examples/robosen_simulator_flow.json)
4. Click **Deploy**. Notice the Master Block status changes to **`Connected (K1-00457, 90%)`**.
5. Click the **Start Button** on the left of the **Master Block** node to trigger the chain and see the robot execute the sequence instantly!
