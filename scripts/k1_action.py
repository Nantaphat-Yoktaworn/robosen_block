"""
Robosen K1 Quick Action & Motion CLI
Run individual actions, toggle safety modes, or query telemetry over BLE.
Maintains standing posture when articulating head.
"""

import asyncio
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

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
    "walk": (0x01, b"", 2.5),
    "turn_left": (0x08, b"", 2.0),
    "turn_right": (0x02, b"", 2.0),
    "auto_stand_on": (0x11, bytes([1]), 1.0),
    "auto_stand_off": (0x11, bytes([0]), 1.0),
    "auto_turn_on": (0x1A, bytes([1]), 1.0),
    "auto_turn_off": (0x1A, bytes([0]), 1.0),
    "auto_off_on": (0x13, bytes([1]), 1.0),
    "auto_off_off": (0x13, bytes([0]), 1.0),
    "status": (0x0F, b"", 1.5),
}

current_joints = bytearray([
    129, 60, 106, 118, 190, 146, 212, 36, 123, 123, 129, 115, 223, 116, 34, 126,
    122, 125, 125, 125, 125, 100, 100, 100, 35
])

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

def notification_handler(sender, data: bytearray):
    global current_joints
    if len(data) >= 4:
        opcode = data[3]
        payload = data[4:-1]
        if opcode in [0xE9, 0xE8, 0xE6] and len(payload) >= 17:
            for i in range(min(len(payload), len(current_joints))):
                current_joints[i] = payload[i]
        elif opcode == 0x17 and len(payload) >= 1:
            progress = payload[-1]
            print(f"[Telemetry] Action Progress: {progress}%")
        elif opcode == 0x0F and len(payload) >= 8:
            battery = payload[1]
            volume = payload[2]
            auto_stand = bool(payload[4])
            auto_turn = bool(payload[5])
            auto_off = bool(payload[7])
            print("\n" + "=" * 45)
            print("📊 ROBOSEN K1 TELEMETRY STATUS")
            print("=" * 45)
            print(f"  🔋 Battery Level:     {battery}%")
            print(f"  🔊 Speaker Volume:    {volume} / 140")
            print(f"  🛡️ Auto-Stand Mode:   {'Enabled' if auto_stand else 'Disabled'}")
            print(f"  🔄 Auto-Turn Mode:    {'Enabled' if auto_turn else 'Disabled'}")
            print(f"  ⏱️ Auto-Off Timer:    {'Enabled' if auto_off else 'Disabled'}")
            print("=" * 45)

async def get_k1_device():
    print("[*] Scanning for K1 robot...")
    devices = await BleakScanner.discover(timeout=4.0, return_adv=True)
    for device, adv in devices.values():
        name = device.name or adv.local_name or ""
        uuids = adv.service_uuids or []
        if any(kw in name for kw in TARGET_NAME_KEYWORDS) or any("ffe0" in u.lower() for u in uuids):
            print(f"[+] Found {name} ({device.address})")
            return device
    return None

async def move_head_safely(client, target_angle: int, speed: int = 35):
    global current_joints
    frame = bytearray(current_joints)
    frame[16] = max(42, min(202, target_angle))
    frame[24] = speed
    await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, bytes(frame)), response=False)
    current_joints[16] = frame[16]

async def execute_action(action_key: str):
    device = await get_k1_device()
    if not device:
        print("[-] Robot not found. Make sure it is ON and not connected to the mobile app.")
        return

    print(f"[*] Connecting to {device.name} ({device.address})...")
    async with BleakClient(device.address) as client:
        if not client.is_connected:
            print("[-] Failed to connect.")
            return

        print("[+] Connected!")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        
        # Handshake & Sync live joint positions
        await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0B), response=False)
        await asyncio.sleep(0.3)
        await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE9), response=False)
        await asyncio.sleep(0.4)

        if action_key == "status":
            print("[*] Querying status...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
            await asyncio.sleep(1.5)
            return

        if action_key == "head_left":
            print("[*] Turning Head Left (preserving standing pose)...")
            await move_head_safely(client, 42, speed=35)
            await asyncio.sleep(0.8)
            print("[+] Head Left complete.")
            return

        if action_key == "head_right":
            print("[*] Turning Head Right (preserving standing pose)...")
            await move_head_safely(client, 202, speed=35)
            await asyncio.sleep(0.8)
            print("[+] Head Right complete.")
            return

        if action_key in ["head_center", "head_neutral"]:
            print("[*] Centering Head (preserving standing pose)...")
            await move_head_safely(client, 122, speed=35)
            await asyncio.sleep(0.8)
            print("[+] Head Center complete.")
            return

        if action_key == "head_pan":
            print("[*] Executing Head Pan (Left -> Right -> Center)...")
            await move_head_safely(client, 42, speed=35)
            await asyncio.sleep(0.9)
            await move_head_safely(client, 202, speed=35)
            await asyncio.sleep(0.9)
            await move_head_safely(client, 122, speed=35)
            await asyncio.sleep(0.7)
            print("[+] Head Pan complete.")
            return

        if action_key in ACTIONS:
            opcode, payload, duration = ACTIONS[action_key]
            print(f"[*] Executing action '{action_key}'...")
            pkt = build_packet(opcode, payload)
            await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
            
            if opcode in [0x01, 0x02, 0x05, 0x08]:
                await asyncio.sleep(duration)
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0C), response=False)
                print("[*] Sent Stop command.")
            else:
                await asyncio.sleep(duration)

            print(f"[+] Action '{action_key}' completed successfully.")
        else:
            print(f"[-] Unknown action '{action_key}'. Available actions:")
            for k in ACTIONS:
                print(f"    - {k}")
            print("    - head_left")
            print("    - head_right")
            print("    - head_center")
            print("    - head_pan")

async def main():
    if len(sys.argv) < 2 or sys.argv[1] == "scan":
        device = await get_k1_device()
        if device:
            print(f"[+] Ready to execute commands on {device.name}!")
            print("Usage: python scripts/k1_action.py <action_name>")
            print("Available actions:")
            for k in ACTIONS:
                print(f"  python scripts/k1_action.py {k}")
            print("  python scripts/k1_action.py head_left")
            print("  python scripts/k1_action.py head_right")
            print("  python scripts/k1_action.py head_center")
            print("  python scripts/k1_action.py head_pan")
        return

    action = sys.argv[1].lower()
    await execute_action(action)

if __name__ == "__main__":
    asyncio.run(main())
