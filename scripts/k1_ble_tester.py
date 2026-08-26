"""
Robosen K1 Bluetooth Low Energy (BLE) Diagnostic & Test Utility
Uses native Windows BLE (via Bleak) to scan, connect, query, and test K1 robot motions.
"""

import asyncio
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from bleak import BleakScanner, BleakClient

# Robosen K1 BLE Constants
SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"        # 0xFFE0
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"  # 0xFFE1
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    """
    Builds a Robosen binary packet:
    [0xFF, 0xFF, numBytes (1 + len(payload) + 1), opcode, payload..., checksum]
    """
    num_bytes = 1 + len(payload) + 1  # opcode + payload + checksum
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

def notification_handler(sender, data: bytearray):
    if len(data) >= 4:
        opcode = data[3]
        payload = data[4:-1]
        if opcode == 0x0F and len(payload) >= 8:
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
            return

        hex_str = data.hex(" ")
        print(f"\n[<-- Robot Response] ({len(data)} bytes): {hex_str}")
        try:
            text = payload.decode("ascii", errors="replace")
            print(f"    Decoded Opcode: 0x{opcode:02X}, Text: {text.strip()}")
        except Exception:
            pass

async def scan_for_k1(timeout: float = 6.0):
    print("=" * 60)
    print("[*] Scanning for Robosen K1 over Bluetooth BLE...")
    print("=" * 60)
    devices = await BleakScanner.discover(timeout=timeout, return_adv=True)
    k1_candidates = []
    
    for device, adv in devices.values():
        name = device.name or adv.local_name or "Unknown"
        rssi = adv.rssi
        uuids = adv.service_uuids or []
        is_k1 = any(kw in name for kw in TARGET_NAME_KEYWORDS) or any("ffe0" in u.lower() for u in uuids)
        
        if is_k1:
            print(f"  [+] FOUND K1 CANDIDATE: '{name}' | Address: {device.address} | RSSI: {rssi} dBm")
            k1_candidates.append(device)
        else:
            if name != "Unknown":
                print(f"      Device: '{name}' ({device.address})")
                
    return k1_candidates

async def interactive_test(address: str):
    print(f"\n[*] Connecting to {address}...")
    async with BleakClient(address) as client:
        if not client.is_connected:
            print("[-] Failed to connect!")
            return
            
        print("[+] Successfully connected to Robosen K1 via Windows BLE!")
        
        # Subscribe to notifications
        try:
            await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
            print(f"[*] Subscribed to telemetry notifications on {CHARACTERISTIC_UUID}")
        except Exception as e:
            print(f"[!] Notification subscribe note: {e}")
            
        # 1. Send Handshake (0x0B)
        print("\n[*] [1/4] Sending Handshake ping (0x0B)...")
        handshake_pkt = build_packet(0x0B)
        await client.write_gatt_char(CHARACTERISTIC_UUID, handshake_pkt, response=False)
        await asyncio.sleep(1.0)
        
        # 2. Query Firmware Version (0xF7)
        print("[*] [2/4] Querying Firmware Version (0xF7)...")
        version_pkt = build_packet(0xF7)
        await client.write_gatt_char(CHARACTERISTIC_UUID, version_pkt, response=False)
        await asyncio.sleep(1.0)
        
        # 3. Query Robot State (0x0F)
        print("[*] [3/4] Querying Robot Status / Battery (0x0F)...")
        state_pkt = build_packet(0x0F)
        await client.write_gatt_char(CHARACTERISTIC_UUID, state_pkt, response=False)
        await asyncio.sleep(1.5)
        
        # 4. Interactive Command Menu
        while True:
            print("\n" + "-" * 50)
            print("ROBOSEN K1 CONTROL TEST MENU")
            print("-" * 50)
            print("  1. Left Punch (Action)")
            print("  2. Right Punch (Action)")
            print("  3. Kung Fu (Action)")
            print("  4. Boogaloo Dance (Action)")
            print("  5. Head Left / Right / Center (Servo Move)")
            print("  6. Set Volume (100)")
            print("  7. Query Battery & Status")
            print("  0. Disconnect and Exit")
            print("-" * 50)
            
            try:
                choice = input("Enter choice (0-7): ").strip()
            except EOFError:
                break
                
            if choice == "0":
                print("Disconnecting...")
                break
            elif choice == "1":
                pkt = build_packet(0x17, b"ProAction/Left Punch")
                print(">> Sending Left Punch...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(3.0)
            elif choice == "2":
                pkt = build_packet(0x17, b"ProAction/Right Punch")
                print(">> Sending Right Punch...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(3.0)
            elif choice == "3":
                pkt = build_packet(0x17, b"ProAction/Kung Fu")
                print(">> Sending Kung Fu...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(5.0)
            elif choice == "4":
                pkt = build_packet(0x17, b"Action/Boogaloo")
                print(">> Sending Boogaloo Dance...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
                await asyncio.sleep(5.0)
            elif choice == "5":
                print(">> Panning Head Left -> Right -> Center...")
                # Head Left (angle 42)
                frame_left = bytearray([126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99, 42, 125, 125, 125, 125, 100, 100, 100, 30])
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, bytes(frame_left)), response=False)
                await asyncio.sleep(1.5)
                # Head Right (angle 202)
                frame_right = bytearray([126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99, 202, 125, 125, 125, 125, 100, 100, 100, 30])
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, bytes(frame_right)), response=False)
                await asyncio.sleep(1.5)
                # Head Center (angle 123)
                frame_center = bytearray([126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99, 123, 125, 125, 125, 125, 100, 100, 100, 30])
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0xE8, bytes(frame_center)), response=False)
                await asyncio.sleep(1.5)
            elif choice == "6":
                print(">> Setting Volume to 100...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0D, bytes([100])), response=False)
                await asyncio.sleep(0.5)
            elif choice == "7":
                print(">> Querying State...")
                await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
                await asyncio.sleep(1.0)
            else:
                print("Invalid option.")

async def main():
    devices = await scan_for_k1(timeout=5.0)
    if not devices:
        print("\n[!] No Robosen K1 detected in BLE scan.")
        print("Please check:")
        print(" 1. The robot is turned ON (Press and hold power button until 'Hello, Humanity').")
        print(" 2. Bluetooth is enabled on this PC in Windows Settings.")
        print(" 3. The phone app (K One) is DISCONNECTED (BLE supports only one connection at a time).")
        return
        
    target = devices[0]
    await interactive_test(target.address)

if __name__ == "__main__":
    asyncio.run(main())
