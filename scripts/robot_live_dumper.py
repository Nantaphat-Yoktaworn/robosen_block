import asyncio
import json
import sys
import time
from datetime import datetime
from bleak import BleakScanner, BleakClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

received_packets = []

def notification_handler(sender, data: bytearray):
    ts = datetime.now().isoformat()
    raw_hex = data.hex(" ")
    packet_entry = {
        "timestamp": ts,
        "raw_hex": raw_hex,
        "length": len(data),
        "raw_bytes": list(data)
    }
    
    if len(data) >= 4 and data[0] == 0xFF and data[1] == 0xFF:
        num_bytes = data[2]
        opcode = data[3]
        payload = data[4:-1]
        checksum = data[-1]
        packet_entry["opcode_hex"] = f"0x{opcode:02X}"
        packet_entry["opcode_dec"] = opcode
        packet_entry["payload_hex"] = payload.hex(" ")
        packet_entry["payload_bytes"] = list(payload)
        
        # Try decoding as ASCII / UTF-8
        try:
            packet_entry["payload_ascii"] = payload.decode("ascii", errors="replace")
        except Exception:
            packet_entry["payload_ascii"] = None
            
        # Special parsers
        if opcode == 0x0F and len(payload) >= 8:
            packet_entry["parsed_type"] = "state"
            packet_entry["state"] = {
                "pattern": payload[0],
                "battery": payload[1],
                "volume": payload[2],
                "progress": payload[3],
                "autoStand": bool(payload[4]),
                "autoTurn": bool(payload[5]),
                "autoPose": bool(payload[6]),
                "autoOff": bool(payload[7])
            }
        elif opcode in [0xE9, 0xE8, 0xE6] and len(payload) >= 17:
            packet_entry["parsed_type"] = "joints"
            packet_entry["joints"] = list(payload[:25])
        elif opcode == 0x17 and len(payload) >= 1:
            packet_entry["parsed_type"] = "action_progress"
            packet_entry["progress"] = payload[-1]
    
    received_packets.append(packet_entry)
    print(f"[RX {ts}] {raw_hex} | {packet_entry.get('payload_ascii', '')}")

async def run_dumper():
    print("=" * 60)
    print("🔍 STEP 1: Scanning for Robosen K1...")
    print("=" * 60)
    devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
    target = None
    for device, adv in devices.values():
        name = device.name or adv.local_name or "Unknown"
        uuids = adv.service_uuids or []
        print(f"  Found device: '{name}' | Address: {device.address} | RSSI: {adv.rssi}")
        if any(kw in name for kw in TARGET_NAME_KEYWORDS) or any("ffe0" in u.lower() for u in uuids):
            print(f"  🎯 MATCHED K1: {name} ({device.address})")
            target = device
            
    if not target:
        print("\n❌ Could not find Robosen K1 via BLE scan.")
        print("Please verify:")
        print(" 1. The robot is turned ON.")
        print(" 2. Bluetooth is enabled on this PC.")
        print(" 3. The mobile app (K One) is not connected.")
        return

    print(f"\n🔗 STEP 2: Connecting to {target.name} ({target.address})...")
    async with BleakClient(target.address) as client:
        if not client.is_connected:
            print("❌ Failed to connect.")
            return
        print("✅ Connected!")
        
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        print("📡 Subscribed to notifications.")
        await asyncio.sleep(0.5)

        # Helper to query and wait
        async def query(opcode: int, name: str, payload: bytes = b"", wait_sec: float = 1.0):
            print(f"\n➡️ Querying 0x{opcode:02X} ({name})...")
            pkt = build_packet(opcode, payload)
            await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
            await asyncio.sleep(wait_sec)

        # 1. Handshake
        await query(0x0B, "handshake", wait_sec=0.5)
        
        # 2. Firmware Version (0xF7)
        await query(0xF7, "version", wait_sec=0.8)
        
        # 3. Model / Kind (0xF6)
        await query(0xF6, "kind", wait_sec=0.8)
        
        # 4. Firmware Build Date (0xF8)
        await query(0xF8, "date", wait_sec=0.8)
        
        # 5. State / Telemetry (0x0F)
        await query(0x0F, "state", wait_sec=0.8)
        
        # 6. Joint Sync / Current Pose (0xE9)
        await query(0xE9, "jointSync", wait_sec=0.8)
        
        # 7. Query Action Names (0x14)
        await query(0x14, "actionNames", wait_sec=2.0)
        
        # 8. Query Folder Names (0x16)
        await query(0x16, "folderNames", wait_sec=2.0)
        
        # 9. Query Audio Names (0x18)
        await query(0x18, "audioNames", wait_sec=2.0)
        
        # 10. Query User Names / Programs (0x10)
        await query(0x10, "userNames", wait_sec=2.0)

        # Save dump to json
        out_file = f"robot_dump_{int(time.time())}.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "device": {
                    "name": target.name,
                    "address": target.address
                },
                "dump_time": datetime.now().isoformat(),
                "packets_received": received_packets
            }, f, indent=2, ensure_ascii=False)
            
        print(f"\n💾 DUMP SAVED TO {out_file} (Total {len(received_packets)} packets captured)")

if __name__ == "__main__":
    asyncio.run(run_dumper())
