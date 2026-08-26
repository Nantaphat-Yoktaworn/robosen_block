"""
Robosen K1 Persistent BLE Daemon
Maintains a persistent, long-lived Bluetooth BLE connection to the Robosen K1 robot.
Event-driven action completion based on live 100% robot telemetry ACK.
Maintains exact live joint posture state to articulate head without moving standing legs.
"""

import asyncio
import json
import sys
import threading

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

# Action definitions: (opcode, payload, max_timeout_sec)
ACTIONS = {
    "punch_left": (0x17, b"ProAction/Left Punch", 4.0),
    "punch_right": (0x17, b"ProAction/Right Punch", 4.0),
    "kung_fu": (0x17, b"ProAction/Kung Fu", 11.0),
    "boogaloo": (0x17, b"Action/Boogaloo", 55.0),
    "push_ups": (0x17, b"ProAction/Push Ups", 12.0),
    "handstand": (0x17, b"ProAction/Handstand", 18.0),
    "left_kick": (0x17, b"ProAction/Left Kick", 7.0),
    "right_kick": (0x17, b"ProAction/Right Kick", 7.0),
    "single_kick": (0x17, b"ProAction/Left Kick", 7.0),
    "say_hello": (0x17, b"ProAction/Say Hello", 8.0),
    "celebrate": (0x17, b"ProAction/Celebrate", 8.0),
    "do_squats": (0x17, b"ProAction/Do Squats", 20.0),
    "walk": (0x01, b"", 2.0),
    "move_forward": (0x01, b"", 2.0),
    "move_backward": (0x05, b"", 2.0),
    "turn_left": (0x08, b"", 1.5),
    "turn_right": (0x02, b"", 1.5),
    "move_left": (0x07, b"", 2.0),
    "move_right": (0x03, b"", 2.0),
    "auto_stand_on": (0x11, bytes([1]), 1.0),
    "auto_stand_off": (0x11, bytes([0]), 1.0),
    "status": (0x0F, b"", 1.5),
}

# Calibrated baseline standing pose
DEFAULT_STAND_FRAME = bytearray([
    126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99,
    123, # Head (index 16)
    125, 125, 125, 125, 100, 100, 100,
    35   # Speed (index 24)
])

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

def emit_event(event_type: str, data: dict = None):
    msg = {"event": event_type}
    if data:
        msg.update(data)
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

class RobosenBleDaemon:
    def __init__(self):
        self.client = None
        self.device = None
        self.is_running = True
        self.battery = None
        self.volume = None
        self.firmware = None
        self.auto_stand = None
        self.active_action_event = None
        self.current_joints = bytearray(DEFAULT_STAND_FRAME)

    def notification_handler(self, sender, data: bytearray):
        if len(data) >= 4:
            opcode = data[3]
            payload = data[4:-1]

            if opcode == 0x17 and len(payload) >= 1:
                progress = payload[-1]
                emit_event("action_progress", {"progress": progress})
                if progress == 100 or progress == 0x64:
                    if self.active_action_event and not self.active_action_event.is_set():
                        self.active_action_event.set()

            elif opcode in [0xE9, 0xE8, 0xE6] and len(payload) >= 17:
                # Capture the robot's real-time joint positions
                for i in range(min(len(payload), len(self.current_joints))):
                    self.current_joints[i] = payload[i]

            elif opcode == 0x0F and len(payload) >= 8:
                self.battery = payload[1]
                self.volume = payload[2]
                self.auto_stand = bool(payload[4])
                emit_event("status_update", {
                    "battery": self.battery,
                    "volume": self.volume,
                    "autoStand": self.auto_stand,
                    "autoTurn": bool(payload[5]),
                    "autoOff": bool(payload[7]),
                })

            elif opcode == 0xF7:
                try:
                    self.firmware = payload.decode("ascii", errors="replace").strip()
                    emit_event("firmware_info", {"firmware": self.firmware})
                except Exception:
                    pass

    async def connect_robot(self):
        emit_event("connecting", {"message": "Scanning for Robosen K1 over Bluetooth BLE..."})
        try:
            devices = await BleakScanner.discover(timeout=4.0, return_adv=True)
            target = None
            for d, adv in devices.values():
                name = d.name or adv.local_name or ""
                uuids = adv.service_uuids or []
                if any(kw in name for kw in TARGET_NAME_KEYWORDS) or any("ffe0" in u.lower() for u in uuids):
                    target = d
                    break

            if not target:
                emit_event("connect_failed", {"error": "Robot not found in BLE scan. Make sure robot is ON and mobile app disconnected."})
                return False

            self.device = target
            emit_event("connecting", {"message": f"Found {target.name} ({target.address}), establishing connection..."})

            self.client = BleakClient(target.address)
            await self.client.connect()

            if not self.client.is_connected:
                emit_event("connect_failed", {"error": "Failed to connect to BLE client."})
                return False

            await self.client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)

            # Handshake & Queries
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0B), response=False)
            await asyncio.sleep(0.3)
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xF7), response=False)
            await asyncio.sleep(0.3)
            # Sync live joint positions so we know standing pose
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE9), response=False)
            await asyncio.sleep(0.3)
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
            await asyncio.sleep(0.5)

            emit_event("connected", {
                "name": target.name,
                "address": target.address,
                "battery": self.battery,
                "volume": self.volume,
                "firmware": self.firmware,
            })
            return True

        except Exception as e:
            emit_event("connect_failed", {"error": str(e)})
            return False

    async def move_head_only(self, target_angle: int, speed: int = 35):
        """
        Rotates ONLY the neck/head servo (index 16) while preserving
        all 16 body and leg joint angles to maintain standing balance.
        """
        # Build frame from current live joints
        frame = bytearray(self.current_joints)
        frame[16] = max(42, min(202, target_angle)) # Head angle
        frame[24] = speed                           # Smooth speed

        pkt = build_packet(0xE8, bytes(frame))
        await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
        self.current_joints[16] = frame[16]

    async def execute_action(self, action_key: str):
        if not self.client or not self.client.is_connected:
            emit_event("action_failed", {"action": action_key, "error": "Robot not connected"})
            return

        action_key = action_key.lower().strip()
        emit_event("action_started", {"action": action_key})

        # Distinct head articulation commands (posture-preserving)
        if action_key == "head_left":
            await self.move_head_only(42, speed=35)
            await asyncio.sleep(0.8)
            emit_event("action_completed", {"action": action_key})
            return

        elif action_key == "head_right":
            await self.move_head_only(202, speed=35)
            await asyncio.sleep(0.8)
            emit_event("action_completed", {"action": action_key})
            return

        elif action_key in ["head_center", "head_neutral"]:
            await self.move_head_only(123, speed=35)
            await asyncio.sleep(0.8)
            emit_event("action_completed", {"action": action_key})
            return

        elif action_key == "head_pan":
            # Sweep Left -> Right -> Center smoothly
            await self.move_head_only(42, speed=35)
            await asyncio.sleep(0.9)
            await self.move_head_only(202, speed=35)
            await asyncio.sleep(0.9)
            await self.move_head_only(123, speed=35)
            await asyncio.sleep(0.7)
            emit_event("action_completed", {"action": action_key})
            return

        elif action_key in ["default_stand", "stand", "stand_posture"]:
            # Reset all 17 servos to factory default standing posture
            self.current_joints = bytearray(DEFAULT_STAND_FRAME)
            pkt = build_packet(0xE8, bytes(DEFAULT_STAND_FRAME))
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
            await asyncio.sleep(1.0)
            emit_event("action_completed", {"action": action_key})
            return

        if action_key in ACTIONS:
            opcode, payload, max_timeout = ACTIONS[action_key]
            pkt = build_packet(opcode, payload)

            if opcode == 0x17:
                # Predefined action: Wait dynamically for the robot's 100% progress ACK
                self.active_action_event = asyncio.Event()
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                try:
                    await asyncio.wait_for(self.active_action_event.wait(), timeout=max_timeout)
                except asyncio.TimeoutError:
                    pass
                self.active_action_event = None
                # Update joints snapshot after dynamic action completes
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE9), response=False)
            elif opcode in [0x01, 0x02, 0x03, 0x05, 0x07, 0x08]:
                # Locomotion steps: Walk for exact duration, then send immediate stop (0x0C)
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(max_timeout)
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0C), response=False)
                # Resync joints after walking
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE9), response=False)
            else:
                await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(0.3)

            emit_event("action_completed", {"action": action_key})
        else:
            emit_event("action_failed", {"action": action_key, "error": f"Unknown action '{action_key}'"})

    async def query_status(self):
        if self.client and self.client.is_connected:
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
            await asyncio.sleep(0.3)

    async def disconnect(self):
        if self.client and self.client.is_connected:
            try:
                await self.client.disconnect()
            except Exception:
                pass
        emit_event("disconnected", {"message": "Disconnected cleanly from Robosen K1"})

def stdin_thread_worker(loop, q):
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                loop.call_soon_threadsafe(q.put_nowait, None)
                break
            loop.call_soon_threadsafe(q.put_nowait, line.strip())
        except Exception:
            break

async def main():
    daemon = RobosenBleDaemon()
    await daemon.connect_robot()

    loop = asyncio.get_running_loop()
    input_queue = asyncio.Queue()
    t = threading.Thread(target=stdin_thread_worker, args=(loop, input_queue), daemon=True)
    t.start()

    while daemon.is_running:
        line = await input_queue.get()
        if line is None:
            break
        if not line:
            continue

        try:
            cmd_data = json.loads(line)
        except Exception:
            cmd_data = {"cmd": line}

        cmd_type = cmd_data.get("cmd", "").lower()

        if cmd_type == "connect":
            if not daemon.client or not daemon.client.is_connected:
                await daemon.connect_robot()
            else:
                emit_event("already_connected", {"name": daemon.device.name if daemon.device else "K1"})
        elif cmd_type in ["action", "run"]:
            action = cmd_data.get("action", "")
            await daemon.execute_action(action)
        elif cmd_type == "status":
            await daemon.query_status()
        elif cmd_type == "disconnect":
            await daemon.disconnect()
        elif cmd_type in ["exit", "quit"]:
            await daemon.disconnect()
            daemon.is_running = False
            break

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
