"""
Robosen K1 Quick Action & Motion CLI
Run individual actions, toggle safety modes, or query telemetry over BLE.
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
    "punch_left": (0x17, b"ProAction/Left Punch", 3.0),
    "punch_right": (0x17, b"ProAction/Right Punch", 3.0),
    "kung_fu": (0x17, b"ProAction/Kung Fu", 6.0),
    "boogaloo": (0x17, b"Action/Boogaloo", 6.0),
    "single_kick": (0x17, b"Action/Single Leg Kick", 4.0),
    "push_ups": (0x17, b"Action/Push-ups", 8.0),
    "handstand": (0x17, b"Action/Handstand", 6.0),
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

def make_head_frame(head_angle: int = 122, speed: int = 25) -> bytes:
    frame = bytearray([
        129, 60, 106, 118, 190, 146, 212, 36, 123, 123, 129, 115, 223, 116, 34, 126,
        head_angle,
        125, 125, 125, 125, 100, 100, 100,
        speed
    ])
    return bytes(frame)

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

def notification_handler(sender, data: bytearray):
    if len(data) >= 4:
        opcode = data[3]
        payload = data[4:-1]
        if opcode == 0x17 and len(payload) >= 1:
            progress = payload[-1]
            print(f"[Telemetry] Action Progress: {progress}%")
        elif opcode == 0x0F and len(payload) >= 8:
            pattern = payload[0]
            battery = payload[1]
            volume = payload[2]
            progress = payload[3]
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
        else:
            try:
                text = payload.decode("ascii", errors="replace").strip()
                if text:
                    print(f"[Telemetry] Response (0x{opcode:02X}): {text}")
            except Exception:
                pass

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
        
        # Handshake
        await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0B), response=False)
        await asyncio.sleep(0.5)

        if action_key == "status":
            print("[*] Querying status...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
            await asyncio.sleep(1.5)
            return

        if action_key == "head_left":
            print("[*] Turning Head Left (Angle 42)...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(42, 25)), response=False)
            await asyncio.sleep(1.0)
            print("[+] Head Left complete.")
            return

        if action_key == "head_right":
            print("[*] Turning Head Right (Angle 202)...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(202, 25)), response=False)
            await asyncio.sleep(1.0)
            print("[+] Head Right complete.")
            return

        if action_key in ["head_center", "head_neutral"]:
            print("[*] Centering Head (Angle 122)...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(122, 25)), response=False)
            await asyncio.sleep(0.8)
            print("[+] Head Center complete.")
            return

        if action_key == "head_pan":
            print("[*] Executing Head Pan routine (Left -> Right -> Center)...")
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(42, 25)), response=False)
            await asyncio.sleep(1.0)
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(202, 25)), response=False)
            await asyncio.sleep(1.0)
            await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, make_head_frame(122, 25)), response=False)
            await asyncio.sleep(0.8)
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
