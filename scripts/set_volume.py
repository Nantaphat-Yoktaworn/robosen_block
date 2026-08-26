import asyncio
import sys
from bleak import BleakScanner, BleakClient

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

async def set_k1_volume(target_percent: int = 20):
    raw_vol = int(round(140 * (target_percent / 100.0)))
    raw_vol = max(0, min(140, raw_vol))
    print(f"[*] Target Volume: {target_percent}% (Raw value: {raw_vol} / 140)")
    
    print("[*] Scanning for Robosen K1 BLE device...")
    scanner = BleakScanner()
    devices = await scanner.discover(timeout=5.0)
    
    target_device = None
    for d in devices:
        name = d.name or ""
        if any(kw in name for kw in TARGET_NAME_KEYWORDS):
            target_device = d
            break
            
    if not target_device:
        print("[!] No Robosen K1 robot discovered. Please make sure the robot is powered ON.")
        return False
        
    print(f"[+] Found robot: {target_device.name} [{target_device.address}]")
    print("[*] Connecting...")
    
    current_vol = None
    battery_lvl = None
    
    def notification_handler(sender, data: bytearray):
        nonlocal current_vol, battery_lvl
        if len(data) >= 4 and data[3] == 0x0F and len(data) >= 7:
            payload = data[4:-1]
            if len(payload) >= 3:
                battery_lvl = payload[1]
                current_vol = payload[2]
                print(f"[Telemetry] Live Battery: {battery_lvl}%, Speaker Volume: {current_vol} / 140")

    async with BleakClient(target_device.address) as client:
        print("[+] Connected successfully!")
        await client.start_notify(CHARACTERISTIC_UUID, notification_handler)
        await asyncio.sleep(0.5)
        
        # Query initial state
        print("[*] Querying current robot state...")
        await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
        await asyncio.sleep(0.8)
        
        # Set Volume
        print(f"[*] Sending Volume setting -> {raw_vol} ({target_percent}%)...")
        pkt = build_packet(0x0D, bytes([raw_vol]))
        await client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
        await asyncio.sleep(0.8)
        
        # Query updated state to confirm
        print("[*] Verifying updated volume...")
        await client.write_gatt_char(CHARACTERISTIC_UUID, build_packet(0x0F), response=False)
        await asyncio.sleep(1.0)
        
        print(f"[SUCCESS] Robot volume set to {target_percent}% ({raw_vol}/140)!")
        return True

if __name__ == "__main__":
    percent = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    asyncio.run(set_k1_volume(percent))
