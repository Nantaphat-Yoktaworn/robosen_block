#!/usr/bin/env python3
"""
Robosen K1 Interactive Joint Kinematics Controller
==================================================
Allows real-time interactive control of all 17 digital servos individually using
keyboard arrow keys, with strict hardware safeguard limit enforcement, visual
gauges, live telemetry, and resilient error handling.

Controls:
  ↑ / ↓       : Select previous / next joint
  ← / →       : Decrease / Increase active joint angle
  [ / ]       : Select previous / next joint (alternative)
  PageUp/Down : Fast adjustment (±10 units)
  + / -       : Increase / Decrease step size (1, 2, 5, 10)
  0 - 9       : Jump directly to joint index
  C           : Connect / Reconnect to robot over BLE
  D           : Disconnect cleanly from robot
  R           : Reset active joint to default neutral angle
  Shift + R   : Reset ALL 17 joints to default standing pose
  S           : Sync live positions from physical robot (0xE9)
  U           : Unlock / Free motor torque (0xEA) for manual posing
  L           : Lock / Engage motor holding torque (0xEB)
  Q / ESC     : Exit cleanly
"""

import asyncio
import os
import sys
import time

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

try:
    from bleak import BleakClient, BleakScanner
except ImportError:
    print("[!] Error: 'bleak' library is not installed.")
    print("    Please install it using: pip install bleak")
    sys.exit(1)

# Platform-specific non-blocking keyboard input
IS_WINDOWS = sys.platform.startswith("win")
if IS_WINDOWS:
    import msvcrt
else:
    import select
    import termios
    import tty

# ==============================================================================
# ROBOSEN K1 PROTOCOL CONSTANTS
# ==============================================================================
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

# 17 Digital Servos Configuration & Strict Hardware Limits
JOINTS_CONFIG = [
    {"id": 0,  "name": "leftThigh",     "default": 126, "min": 29,  "max": 229, "group": "Left Leg",   "desc": "Left Thigh Pitch"},
    {"id": 1,  "name": "leftCalf",      "default": 65,  "min": 10,  "max": 220, "group": "Left Leg",   "desc": "Left Calf/Knee Pitch"},
    {"id": 2,  "name": "leftAnkle",     "default": 100, "min": 26,  "max": 226, "group": "Left Leg",   "desc": "Left Ankle Pitch"},
    {"id": 3,  "name": "rightThigh",    "default": 127, "min": 18,  "max": 218, "group": "Right Leg",  "desc": "Right Thigh Pitch"},
    {"id": 4,  "name": "rightCalf",     "default": 184, "min": 30,  "max": 240, "group": "Right Leg",  "desc": "Right Calf/Knee Pitch"},
    {"id": 5,  "name": "rightAnkle",    "default": 141, "min": 26,  "max": 226, "group": "Right Leg",  "desc": "Right Ankle Pitch"},
    {"id": 6,  "name": "leftShoulder",  "default": 222, "min": 22,  "max": 242, "group": "Left Arm",   "desc": "Left Shoulder Pitch"},
    {"id": 7,  "name": "rightShoulder", "default": 26,  "min": 6,   "max": 226, "group": "Right Arm",  "desc": "Right Shoulder Pitch"},
    {"id": 8,  "name": "leftHip",       "default": 125, "min": 103, "max": 133, "group": "Left Leg",   "desc": "Left Hip Roll"},
    {"id": 9,  "name": "leftFoot",      "default": 116, "min": 93,  "max": 133, "group": "Left Leg",   "desc": "Left Foot Roll"},
    {"id": 10, "name": "rightHip",      "default": 135, "min": 119, "max": 149, "group": "Right Leg",  "desc": "Right Hip Roll"},
    {"id": 11, "name": "rightFoot",     "default": 120, "min": 105, "max": 145, "group": "Right Leg",  "desc": "Right Foot Roll"},
    {"id": 12, "name": "leftArm",       "default": 214, "min": 33,  "max": 233, "group": "Left Arm",   "desc": "Left Elbow Roll"},
    {"id": 13, "name": "leftHand",      "default": 146, "min": 16,  "max": 216, "group": "Left Arm",   "desc": "Left Wrist Yaw"},
    {"id": 14, "name": "rightArm",      "default": 42,  "min": 34,  "max": 224, "group": "Right Arm",  "desc": "Right Elbow Roll"},
    {"id": 15, "name": "rightHand",     "default": 99,  "min": 26,  "max": 226, "group": "Right Arm",  "desc": "Right Wrist Yaw"},
    {"id": 16, "name": "head",          "default": 123, "min": 42,  "max": 202, "group": "Head",       "desc": "Head / Neck Pan"},
]

# Calibrated baseline default 25-byte frame
DEFAULT_FRAME = [
    126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99,
    123, # Head (16)
    125, 125, 125, 125, 100, 100, 100, # Padding (17-23)
    35   # Default speed (24)
]

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    """Build standard Robosen binary packet with header and modulo checksum."""
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])


# ==============================================================================
# KEYBOARD INPUT READER
# ==============================================================================
class KeyboardReader:
    """Cross-platform non-blocking keyboard input reader supporting arrow keys."""
    def __init__(self):
        self.old_settings = None

    def setup(self):
        if not IS_WINDOWS:
            try:
                self.old_settings = termios.tcgetattr(sys.stdin)
                tty.setcbreak(sys.stdin.fileno())
            except Exception:
                pass

    def cleanup(self):
        if not IS_WINDOWS and self.old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self.old_settings)
            except Exception:
                pass

    def get_key(self) -> str:
        """Returns normalized key string: 'UP', 'DOWN', 'LEFT', 'RIGHT', 'PAGE_UP', 'PAGE_DOWN', or char."""
        if IS_WINDOWS:
            if not msvcrt.kbhit():
                return ""
            ch = msvcrt.getch()
            if ch in (b"\x00", b"\xe0"):
                ch2 = msvcrt.getch()
                code_map = {
                    b"H": "UP",
                    b"P": "DOWN",
                    b"K": "LEFT",
                    b"M": "RIGHT",
                    b"I": "PAGE_UP",
                    b"Q": "PAGE_DOWN",
                    b"G": "HOME",
                    b"O": "END",
                }
                return code_map.get(ch2, "")
            elif ch == b"\x1b":
                return "ESC"
            elif ch == b"\r" or ch == b"\n":
                return "ENTER"
            elif ch == b"\t":
                return "TAB"
            else:
                try:
                    return ch.decode("utf-8")
                except UnicodeDecodeError:
                    return ""
        else:
            dr, _, _ = select.select([sys.stdin], [], [], 0.0)
            if not dr:
                return ""
            ch = sys.stdin.read(1)
            if ch == "\x1b":
                # Check for escape sequence (arrow keys on POSIX)
                dr2, _, _ = select.select([sys.stdin], [], [], 0.05)
                if dr2:
                    seq = sys.stdin.read(2)
                    if seq == "[A":
                        return "UP"
                    elif seq == "[B":
                        return "DOWN"
                    elif seq == "[C":
                        return "RIGHT"
                    elif seq == "[D":
                        return "LEFT"
                    elif seq == "[5":
                        sys.stdin.read(1) # consume ~
                        return "PAGE_UP"
                    elif seq == "[6":
                        sys.stdin.read(1) # consume ~
                        return "PAGE_DOWN"
                return "ESC"
            elif ch in ("\r", "\n"):
                return "ENTER"
            elif ch == "\t":
                return "TAB"
            return ch


# ==============================================================================
# MAIN ROBOT CONTROLLER
# ==============================================================================
class RobosenJointController:
    def __init__(self):
        self.client = None
        self.device = None
        self.is_connected = False
        self.is_running = True
        self.kb = KeyboardReader()

        # State
        self.current_joints = bytearray(DEFAULT_FRAME)
        self.selected_joint_idx = 16  # Default start with Head for safety
        self.step_size = 5            # Adjustment step (1, 2, 5, 10)
        self.speed = 35               # Speed byte (1=fastest, 100=slowest)
        self.torque_locked = True
        self.battery = "--"
        self.volume = "--"
        self.firmware = "--"

        # UI & Feedback Messages
        self.status_msg = "Ready (Disconnected). Press 'C' to connect to Robosen K1 over Bluetooth."
        self.status_type = "info"  # "info", "success", "warning", "error"
        self.last_sent_time = 0
        self.send_queue = asyncio.Queue()
        self.show_help = False

    def notification_handler(self, sender, data: bytearray):
        """Processes incoming telemetry and position synchronizations from K1."""
        if len(data) >= 4:
            opcode = data[3]
            payload = data[4:-1]

            if opcode in (0xE9, 0xE8, 0xE6) and len(payload) >= 17:
                # Update local joint state from robot's live feedback
                for i in range(min(len(payload), 17)):
                    self.current_joints[i] = payload[i]
                self.set_feedback("Synchronized live joint positions from robot.", "success")

            elif opcode == 0x0F and len(payload) >= 8:
                self.battery = f"{payload[1]}%"
                self.volume = f"{payload[2]}/140"

    def set_feedback(self, msg: str, msg_type: str = "info"):
        self.status_msg = msg
        self.status_type = msg_type

    def draw_gauge(self, val: int, min_val: int, max_val: int, width: int = 14) -> str:
        """Renders an ASCII position gauge."""
        if max_val <= min_val:
            return "[" + " " * width + "]"
        ratio = max(0.0, min(1.0, (val - min_val) / (max_val - min_val)))
        pos = int(ratio * (width - 1))
        chars = ["-"] * width
        chars[pos] = "█"
        return "[" + "".join(chars) + "]"

    def render_ui(self):
        """Draws the live interactive dashboard in the terminal."""
        # Clear screen ANSI
        out = "\033[H"
        
        # Color codes
        C_RESET = "\033[0m"
        C_BOLD = "\033[1m"
        C_CYAN = "\033[36m"
        C_GREEN = "\033[32m"
        C_YELLOW = "\033[33m"
        C_RED = "\033[31m"
        C_MAGENTA = "\033[35m"
        C_BG_BLUE = "\033[44m\033[37m"
        C_BG_SELECT = "\033[48;5;238m"

        conn_badge = f"{C_GREEN}● CONNECTED{C_RESET}" if self.is_connected else f"{C_RED}○ DISCONNECTED{C_RESET}"
        dev_name = self.device.name if self.device else "Unknown"
        torque_status = f"{C_GREEN}LOCKED{C_RESET}" if self.torque_locked else f"{C_YELLOW}FREE (UNLOCKED){C_RESET}"

        out += f"{C_BOLD}╔══════════════════════════════════════════════════════════════════════════════════╗{C_RESET}\n"
        out += f"{C_BOLD}║           🤖 ROBOSEN K1 — LIVE JOINT KINEMATICS SAFEGUARD CONTROLLER             ║{C_RESET}\n"
        out += f"{C_BOLD}╠══════════════════════════════════════════════════════════════════════════════════╣{C_RESET}\n"
        out += f"║ Status: {conn_badge:<22} Device: {dev_name:<12} Battery: {self.battery:<6} Torque: {torque_status:<10} ║\n"
        out += f"║ Step Size: {C_BOLD}{self.step_size:>2}{C_RESET} [+/- to change]   Speed: {C_BOLD}{self.speed:>2}{C_RESET}       Joints: 17 Digital Servos        ║\n"
        out += f"{C_BOLD}╠══════════════════════════════════════════════════════════════════════════════════╣{C_RESET}\n"
        out += f"║ {C_BOLD}SEL  ID  JOINT NAME       GROUP      CURRENT   MIN   MAX   GAUGE          STATUS{C_RESET}  ║\n"
        out += f"{C_BOLD}╟──────────────────────────────────────────────────────────────────────────────────╢{C_RESET}\n"

        for idx, j in enumerate(JOINTS_CONFIG):
            jid = j["id"]
            val = self.current_joints[jid]
            is_selected = (idx == self.selected_joint_idx)
            
            # Status check for limits
            if val >= j["max"]:
                limit_stat = f"{C_RED}AT MAX LIMIT{C_RESET}"
            elif val <= j["min"]:
                limit_stat = f"{C_YELLOW}AT MIN LIMIT{C_RESET}"
            elif val == j["default"]:
                limit_stat = f"{C_GREEN}CENTER (DEF){C_RESET}"
            else:
                limit_stat = f"{C_CYAN}NORMAL{C_RESET}"

            gauge = self.draw_gauge(val, j["min"], j["max"])

            if is_selected:
                cursor = f"{C_BOLD}{C_GREEN}👉{C_RESET}"
                name_fmt = f"{C_BOLD}{C_GREEN}{j['name']:<15}{C_RESET}"
                val_fmt = f"{C_BOLD}{C_GREEN}{val:>5}{C_RESET}"
            else:
                cursor = "  "
                name_fmt = f"{j['name']:<15}"
                val_fmt = f"{val:>5}"

            row = (
                f"║ {cursor} {jid:>2}  {name_fmt}  {j['group']:<9}  "
                f"{val_fmt}  {j['min']:>4}  {j['max']:>4}  {gauge}  {limit_stat:<20} ║\n"
            )
            out += row

        out += f"{C_BOLD}╠══════════════════════════════════════════════════════════════════════════════════╣{C_RESET}\n"

        # Status & Message Bar
        if self.status_type == "error":
            msg_color = C_RED + C_BOLD
            prefix = "❌ ERROR: "
        elif self.status_type == "warning":
            msg_color = C_YELLOW + C_BOLD
            prefix = "⚠️  SAFEGUARD: "
        elif self.status_type == "success":
            msg_color = C_GREEN
            prefix = "✅ "
        else:
            msg_color = C_CYAN
            prefix = "ℹ️  "

        truncated_msg = (self.status_msg[:68] + "..") if len(self.status_msg) > 70 else self.status_msg
        out += f"║ {msg_color}{prefix}{truncated_msg:<74}{C_RESET} ║\n"
        out += f"{C_BOLD}╠══════════════════════════════════════════════════════════════════════════════════╣{C_RESET}\n"
        out += f"║ {C_BOLD}CONTROLS:{C_RESET} C: Connect | D: Disconnect | ↑/↓: Select | ←/→: Value | +/-: Step        ║\n"
        out += f"║          R: Reset Joint | Shift+R: Stand Pose | S: Sync | U: Free | L: Lock | Q: Quit  ║\n"
        out += f"{C_BOLD}╚══════════════════════════════════════════════════════════════════════════════════╝{C_RESET}\n"

        sys.stdout.write(out)
        sys.stdout.flush()

    def validate_and_apply_delta(self, delta: int) -> bool:
        """
        Safeguard Enforcement Engine:
        Validates whether target angle stays within strict min/max limits.
        Refuses packet generation and alerts the user if limits are violated.
        """
        j = JOINTS_CONFIG[self.selected_joint_idx]
        jid = j["id"]
        current_val = self.current_joints[jid]
        target_val = current_val + delta

        # SAFEGUARD CHECK 1: Exceeds Maximum Limit
        if target_val > j["max"]:
            if current_val == j["max"]:
                self.set_feedback(
                    f"BLOCKED: '{j['name']}' already at maximum limit ({j['max']})!",
                    "warning"
                )
            else:
                self.current_joints[jid] = j["max"]
                self.set_feedback(
                    f"Clamped '{j['name']}' to max limit ({j['max']}).",
                    "warning"
                )
                self.queue_joint_move()
            return False

        # SAFEGUARD CHECK 2: Below Minimum Limit
        if target_val < j["min"]:
            if current_val == j["min"]:
                self.set_feedback(
                    f"BLOCKED: '{j['name']}' already at minimum limit ({j['min']})!",
                    "warning"
                )
            else:
                self.current_joints[jid] = j["min"]
                self.set_feedback(
                    f"Clamped '{j['name']}' to min limit ({j['min']}).",
                    "warning"
                )
                self.queue_joint_move()
            return False

        # SAFEGUARD PASSED: Apply value safely
        self.current_joints[jid] = target_val
        self.set_feedback(f"Moved '{j['name']}' to angle {target_val} (Δ{delta:+d}).", "info")
        self.queue_joint_move()
        return True

    def queue_joint_move(self):
        """Queues a 0xE8 jointMove command to be transmitted over BLE."""
        if not self.is_connected or not self.client:
            self.set_feedback("Cannot send packet: Robot is disconnected!", "error")
            return

        frame = bytearray(self.current_joints)
        frame[24] = self.speed
        pkt = build_packet(0xE8, bytes(frame))

        # Put into queue, dropping stale frames if overwhelmed
        while not self.send_queue.empty():
            try:
                self.send_queue.get_nowait()
            except Exception:
                break
        self.send_queue.put_nowait(pkt)

    async def ble_writer_task(self):
        """Asynchronous worker that pushes queued packets to BLE GATT characteristic."""
        while self.is_running:
            try:
                pkt = await asyncio.wait_for(self.send_queue.get(), timeout=0.1)
                if self.client and self.is_connected:
                    await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                    self.send_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                self.set_feedback(f"BLE Write Exception: {e}", "error")
                await asyncio.sleep(0.1)

    async def send_command(self, opcode: int, payload: bytes = b"", desc: str = ""):
        """Sends a one-off opcode command with error handling."""
        if not self.is_connected or not self.client:
            self.set_feedback(f"Cannot execute '{desc}': Robot disconnected!", "error")
            return False
        try:
            pkt = build_packet(opcode, payload)
            await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
            if desc:
                self.set_feedback(f"Executed: {desc}", "success")
            return True
        except Exception as e:
            self.set_feedback(f"Failed to execute '{desc}': {e}", "error")
            return False

    async def reset_selected_joint(self):
        """Resets the currently selected joint to its neutral default angle."""
        j = JOINTS_CONFIG[self.selected_joint_idx]
        jid = j["id"]
        self.current_joints[jid] = j["default"]
        self.set_feedback(f"Reset '{j['name']}' to neutral ({j['default']}).", "success")
        self.queue_joint_move()

    async def reset_all_joints_stand(self):
        """Resets ALL 17 joints back to factory default standing posture."""
        self.current_joints = bytearray(DEFAULT_FRAME)
        self.set_feedback("Reset ALL 17 servos to default standing posture.", "success")
        self.queue_joint_move()

    async def connect_robot(self) -> bool:
        """Discovers and establishes connection to the Robosen K1."""
        self.set_feedback("Scanning for Robosen K1 over BLE...", "info")
        self.render_ui()

        try:
            devices = await BleakScanner.discover(timeout=4.0, return_adv=True)
            target = None
            for device, adv in devices.values():
                name = device.name or adv.local_name or ""
                uuids = adv.service_uuids or []
                if any(kw in name for kw in TARGET_NAME_KEYWORDS) or any("ffe0" in u.lower() for u in uuids):
                    target = device
                    break

            if not target:
                self.set_feedback("Robot not found! Ensure robot is ON and BLE is enabled.", "error")
                return False

            self.device = target
            self.set_feedback(f"Connecting to {target.name} ({target.address})...", "info")
            self.render_ui()

            self.client = BleakClient(target.address)
            await self.client.connect()
            
            if not self.client.is_connected:
                self.set_feedback("Connection failed during handshake.", "error")
                return False

            self.is_connected = True
            await self.client.start_notify(CHARACTERISTIC_UUID, self.notification_handler)

            # Handshake & initial sync
            await self.send_command(0x0B, desc="Handshake")
            await asyncio.sleep(0.3)
            await self.send_command(0xE9, desc="Sync Live Poses")
            await asyncio.sleep(0.3)
            await self.send_command(0x0F, desc="Query Battery")

            self.set_feedback(f"Connected to {target.name}! Initial pose synchronized.", "success")
            return True

        except Exception as e:
            self.is_connected = False
            self.set_feedback(f"Connection error: {e}", "error")
            return False

    async def disconnect_robot(self):
        """Disconnects cleanly from the Robosen K1 without closing the application."""
        if not self.is_connected and not self.client:
            self.set_feedback("Already disconnected. Press 'C' to connect.", "info")
            return

        self.set_feedback("Disconnecting from robot...", "info")
        self.render_ui()
        self.is_connected = False
        if self.client:
            try:
                await self.client.disconnect()
            except Exception as e:
                self.set_feedback(f"Disconnect note: {e}", "warning")
            self.client = None
        self.battery = "--"
        self.volume = "--"
        self.set_feedback("Disconnected cleanly. Press 'C' to reconnect.", "warning")

    async def run(self):
        """Main event loop."""
        # Clear screen on start
        os.system("cls" if IS_WINDOWS else "clear")
        self.kb.setup()

        # Start BLE writer background worker
        writer_task = asyncio.create_task(self.ble_writer_task())

        # Start in Disconnected mode (wait for user to press 'C')
        self.set_feedback("Ready (Disconnected). Press 'C' to connect to Robosen K1 over Bluetooth.", "info")

        try:
            while self.is_running:
                self.render_ui()

                # Poll keyboard
                key = self.kb.get_key()

                if key:
                    if key in ("q", "Q", "ESC"):
                        self.set_feedback("Exiting joint controller...", "info")
                        self.is_running = False
                        break

                    # Navigation: Select Joint (Vertical Table Navigation)
                    elif key in ("UP", "["):
                        self.selected_joint_idx = (self.selected_joint_idx - 1) % len(JOINTS_CONFIG)
                        j = JOINTS_CONFIG[self.selected_joint_idx]
                        self.set_feedback(f"Selected: #{j['id']} {j['name']} ({j['desc']})", "info")

                    elif key in ("DOWN", "]", "TAB"):
                        self.selected_joint_idx = (self.selected_joint_idx + 1) % len(JOINTS_CONFIG)
                        j = JOINTS_CONFIG[self.selected_joint_idx]
                        self.set_feedback(f"Selected: #{j['id']} {j['name']} ({j['desc']})", "info")

                    # Articulation: Adjust Value (Horizontal Slider)
                    elif key == "LEFT":
                        self.validate_and_apply_delta(-self.step_size)

                    elif key == "RIGHT":
                        self.validate_and_apply_delta(+self.step_size)

                    elif key == "PAGE_DOWN":
                        self.validate_and_apply_delta(-10)

                    elif key == "PAGE_UP":
                        self.validate_and_apply_delta(+10)

                    # Step Size Adjustments
                    elif key in ("+", "="):
                        steps = [1, 2, 5, 10, 20]
                        idx = steps.index(self.step_size) if self.step_size in steps else 0
                        self.step_size = steps[min(len(steps) - 1, idx + 1)]
                        self.set_feedback(f"Step size increased to {self.step_size}.", "info")

                    elif key in ("-", "_"):
                        steps = [1, 2, 5, 10, 20]
                        idx = steps.index(self.step_size) if self.step_size in steps else 0
                        self.step_size = steps[max(0, idx - 1)]
                        self.set_feedback(f"Step size decreased to {self.step_size}.", "info")

                    # Direct Numeric Jump
                    elif key.isdigit():
                        num = int(key)
                        if num < len(JOINTS_CONFIG):
                            self.selected_joint_idx = num
                            j = JOINTS_CONFIG[num]
                            self.set_feedback(f"Jumped to #{j['id']} {j['name']}", "info")

                    # Actions & Resets
                    elif key == "r":
                        await self.reset_selected_joint()

                    elif key == "R":
                        await self.reset_all_joints_stand()

                    elif key in ("s", "S"):
                        await self.send_command(0xE9, desc="Sync Live Positions")

                    elif key in ("u", "U"):
                        await self.send_command(0xEA, desc="Release Motor Torque (Free Joints)")
                        self.torque_locked = False

                    elif key in ("l", "L"):
                        await self.send_command(0xEB, desc="Engage Motor Holding Torque")
                        self.torque_locked = True

                    elif key in ("c", "C"):
                        await self.connect_robot()

                    elif key in ("d", "D"):
                        await self.disconnect_robot()

                await asyncio.sleep(0.04)  # ~25 FPS UI refresh

        except KeyboardInterrupt:
            pass
        except Exception as e:
            print(f"\n[!] Unexpected Error: {e}")
        finally:
            self.is_running = False
            self.kb.cleanup()
            writer_task.cancel()

            if self.client and self.client.is_connected:
                try:
                    await self.client.disconnect()
                except Exception:
                    pass

            print("\n[+] Joint Controller closed cleanly. Robot connection released.\n")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    controller = RobosenJointController()
    try:
        asyncio.run(controller.run())
    except KeyboardInterrupt:
        print("\nSession interrupted by user.")
