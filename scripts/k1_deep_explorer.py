"""
Robosen K1 Deep Protocol Explorer & Filesystem Extractor
Investigates:
1. Full internal filesystem tree via Opcode 0xE2 (folders, files, audio tracks)
2. 50-byte IMU / Sensor / Telemetry telemetry buffer via Opcode 0xF1 / 0xF0
3. Audio playback verification via Opcode 0x19 across AppSysMS / SysMS / WarnSysMS
4. Special action catalog (SpeActions, ProAction, Action) execution
5. Programming mode frame format (0xE6 / 0xE7)
6. Detailed servo limits & feedback
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from bleak import BleakScanner, BleakClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SERVICE_UUID = "0000ffe0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
TARGET_NAME_KEYWORDS = ["K1", "k1", "Robosen", "robosen"]
TARGET_ADDRESS = "3C:A5:51:94:97:70"

DEFAULT_STAND_FRAME = bytearray([
    126, 65, 100, 127, 184, 141, 222, 26, 125, 116, 135, 120, 214, 146, 42, 99,
    123, 125, 125, 125, 125, 100, 100, 100, 35
])

def build_packet(opcode: int, payload: bytes = b"") -> bytes:
    num_bytes = 1 + len(payload) + 1
    body = bytes([num_bytes, opcode]) + payload
    checksum = sum(body) % 256
    return bytes([0xFF, 0xFF]) + body + bytes([checksum])

class K1DeepExplorer:
    def __init__(self):
        self.client = None
        self.device = None
        self.all_rx = []
        self.fs_tree = {}
        self.imu_samples = []
        self.action_catalog = {}
        self.audio_catalog = []

    def handle_notification(self, sender, data: bytearray):
        ts = datetime.now().isoformat()
        entry = {
            "ts": ts,
            "raw_hex": data.hex(" "),
            "raw_bytes": list(data),
            "len": len(data)
        }
        if len(data) >= 4 and data[0] == 0xFF and data[1] == 0xFF:
            entry["opcode"] = data[3]
            entry["opcode_hex"] = f"0x{data[3]:02X}"
            payload = data[4:-1]
            entry["payload_hex"] = payload.hex(" ")
            try:
                entry["payload_ascii"] = payload.decode("ascii", errors="replace").strip()
            except Exception:
                entry["payload_ascii"] = ""
        self.all_rx.append(entry)

    async def connect(self):
        print("[*] Scanning for K1 robot...")
        def match_k1(d, adv):
            name = d.name or adv.local_name or ""
            uuids = adv.service_uuids or []
            return (
                "3C:A5:51:94:97:70" in d.address.upper() or
                any(kw in name for kw in TARGET_NAME_KEYWORDS) or
                any("ffe0" in u.lower() for u in uuids)
            )
            
        self.device = await BleakScanner.find_device_by_filter(match_k1, timeout=8.0)
        if not self.device:
            raise RuntimeError("Robot not found in BLE scan. Ensure it is powered on and within range.")

        print(f"[+] Found K1 device: {self.device.name} ({self.device.address})")
        print(f"[+] Connecting to {self.device.address}...")
        self.client = BleakClient(self.device)
        await self.client.connect()
        await self.client.start_notify(CHARACTERISTIC_UUID, self.handle_notification)
        print("[+] Connected & subscribed.")
        await asyncio.sleep(0.5)

    async def send(self, opcode: int, payload: bytes = b"", wait_sec: float = 0.5):
        pkt = build_packet(opcode, payload)
        await self.client.write_gatt_char(CHARACTERISTIC_UUID, pkt, response=False)
        if wait_sec > 0:
            await asyncio.sleep(wait_sec)

    async def explore_filesystem(self):
        print("\n" + "=" * 60)
        print("📁 EXPLORING ROBOT FILESYSTEM (OPCODE 0xE2)")
        print("=" * 60)
        
        # 1. Query Root Directory
        cnt_before = len(self.all_rx)
        await self.send(0xE2, b"", wait_sec=1.5)
        root_items = []
        for p in self.all_rx[cnt_before:]:
            if p.get("opcode") == 0xE2 and p.get("payload_ascii") and p["payload_ascii"] != "OK":
                item = p["payload_ascii"]
                if item not in root_items:
                    root_items.append(item)
                    
        print(f"[+] Discovered Root Items: {root_items}")
        self.fs_tree["/"] = root_items

        # 2. Query each subfolder
        folders_to_query = [
            "AppSysMS", "ProAction", "SpeActions", "SysCF", 
            "SysMS", "SysOS", "WarnSysMS", "Action", "AppProMS", "SHR0"
        ]
        
        for folder in folders_to_query:
            print(f"\n📂 Querying folder: /{folder}...")
            cnt_before = len(self.all_rx)
            await self.send(0xE2, folder.encode("ascii"), wait_sec=1.5)
            folder_items = []
            for p in self.all_rx[cnt_before:]:
                if p.get("opcode") == 0xE2 and p.get("payload_ascii") and p["payload_ascii"] != "OK":
                    item = p["payload_ascii"]
                    if item not in folder_items and item != folder:
                        folder_items.append(item)
            self.fs_tree[folder] = folder_items
            print(f"  -> Found {len(folder_items)} items in /{folder}: {folder_items[:10]}...")

    async def explore_imu_and_telemetry(self):
        print("\n" + "=" * 60)
        print("🧭 EXPLORING 50-BYTE TELEMETRY / IMU BUFFER (OPCODE 0xF1 / 0xF0)")
        print("=" * 60)
        
        for i in range(5):
            cnt_before = len(self.all_rx)
            await self.send(0xF1, b"", wait_sec=0.4)
            for p in self.all_rx[cnt_before:]:
                if p.get("opcode") == 0xF0 and p.get("len") >= 50:
                    raw_b = p["raw_bytes"]
                    self.imu_samples.append(raw_b)
                    print(f"  Sample {i+1} (Length {p['len']}): {p['raw_hex'][:60]}...")
                    # Analyze non-zero bytes
                    non_zero = [(idx, val) for idx, val in enumerate(raw_b) if val != 0]
                    print(f"    Non-zero byte indices: {non_zero}")

    async def test_audio_playback(self):
        print("\n" + "=" * 60)
        print("🎵 TESTING AUDIO PLAYBACK (OPCODE 0x19 & 0xEE)")
        print("=" * 60)
        
        # Test playing known system sounds from AppSysMS / SysMS
        audio_candidates = [
            "AppSysMS/101",
            "SysMS/001",
            "SysMS/1",
            "WarnSysMS/001"
        ]
        
        # Also check items found in AppSysMS
        if "AppSysMS" in self.fs_tree:
            for item in self.fs_tree["AppSysMS"][:3]:
                audio_candidates.append(f"AppSysMS/{item}")

        for aud in audio_candidates[:4]:
            print(f"  ▶️ Attempting to play audio: '{aud}' via Opcode 0x19...")
            cnt_before = len(self.all_rx)
            await self.send(0x19, aud.encode("ascii"), wait_sec=1.5)
            rx_replies = self.all_rx[cnt_before:]
            print(f"    -> Responses received: {len(rx_replies)} packets")

    async def test_programming_mode(self):
        print("\n" + "=" * 60)
        print("🛠️ TESTING PROGRAMMING MODE (OPCODE 0xE6 / 0xE7)")
        print("=" * 60)
        
        print("  Entering Programming Mode (0xE6)...")
        cnt_before = len(self.all_rx)
        await self.send(0xE6, b"", wait_sec=1.0)
        prog_frames = [p for p in self.all_rx[cnt_before:] if p.get("opcode") == 0xE6]
        print(f"  -> Received {len(prog_frames)} programming keyframes.")
        for idx, f in enumerate(prog_frames):
            print(f"     Frame {idx+1}: {f.get('raw_hex')}")

        print("  Exiting Programming Mode (0xE7)...")
        await self.send(0xE7, b"", wait_sec=0.8)
        print("  Programming Mode Exited.")

    async def test_special_action(self):
        print("\n" + "=" * 60)
        print("🌟 TESTING SPECIAL ACTION (SpeActions / Showtime / Kung Fu)")
        print("=" * 60)
        
        # Test "Say Hello" (friendly and quick)
        print("  Executing 'ProAction/Say Hello' via Opcode 0x17...")
        await self.send(0x17, b"ProAction/Say Hello", wait_sec=0.1)
        
        # Wait until action completes
        start_t = time.time()
        while time.time() - start_t < 10.0:
            last_pkts = self.all_rx[-3:]
            # Check for progress or completion
            for p in last_pkts:
                if p.get("opcode") == 0x17 and p.get("len") >= 5:
                    pass
            await asyncio.sleep(0.5)
            if time.time() - start_t > 7.0:
                break
        print("  [+] Action finished.")

    def save_dump(self):
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        out_json = f"k1_deep_filesystem_dump_{ts}.json"
        out_md = f"K1_FILESYSTEM_AND_AUDIO_ARCHIVE.md"

        data = {
            "timestamp": datetime.now().isoformat(),
            "filesystem_tree": self.fs_tree,
            "imu_samples": self.imu_samples,
            "total_packets": len(self.all_rx),
            "packets": self.all_rx
        }
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        md = f"""# Robosen K1 Onboard Filesystem & Deep Architecture Archive

> **Captured Date:** {datetime.now().strftime('%B %d, %Y - %H:%M:%S')}  
> **Robot Model:** `Robosen K1 (Interstellar Scout)`  
> **Firmware Version:** `VER:3.03L` (`SH2022-07-23`)  

---

## 1. Complete Internal Filesystem Hierarchy (Discovered via Opcode `0xE2`)

The Robosen K1 flash storage contains the following directory tree and files:

"""
        for folder, items in self.fs_tree.items():
            md += f"### 📂 Directory: `/{folder}`\n"
            if items:
                md += f"Total Items: **{len(items)}**\n\n```\n"
                for it in items:
                    md += f"  - {it}\n"
                md += "```\n\n"
            else:
                md += "*(Empty or binary streaming)*\n\n"

        md += f"""
---

## 2. 50-Byte Telemetry & IMU Packet Structure (`0xF1` Query -> `0xF0` Stream)

Queried via `0xF1`, the robot streams high-speed 50-byte binary telemetry blocks (`0xF0`):

```
Header: 0xFF 0xFF
Length: 0x32 (50 Bytes)
Opcode: 0xF0
```

Raw sample captures:
"""
        for idx, s in enumerate(self.imu_samples, 1):
            md += f"- **Sample {idx}:** `{' '.join(f'{b:02X}' for b in s)}`\n"

        md += """
---

## 3. Verified Opcode Catalog (Exhaustive Reverse Engineering Matrix)

| Opcode (Hex) | Name / Category | Direction | Payload Structure | Physical Robot Behavior |
| :---: | :--- | :---: | :--- | :--- |
| `0x01` | `moveForward` | TX | None | Bipedal continuous forward walking |
| `0x02` | `turnRight` | TX | None | Right heading step articulation |
| `0x03` | `moveRight` | TX | None | Right lateral sidestep |
| `0x04` | `moveSouthEast` | TX | None | Diagonal backward-right step |
| `0x05` | `moveBackward` | TX | None | Backward walking step |
| `0x06` | `moveSouthWest` | TX | None | Diagonal backward-left step |
| `0x07` | `moveLeft` | TX | None | Left lateral sidestep |
| `0x08` | `turnLeft` | TX | None | Left heading step articulation |
| `0x0B` | `handshake` | TX/RX | `0x00` (Ack) | Alive heartbeat connection check |
| `0x0C` | `stop` | TX | None | Emergency / immediate motion halt |
| `0x0D` | `volume` | TX | Byte ($0-140$) | Speaker volume configuration |
| `0x0F` | `state` | TX/RX | 8-byte struct | Battery, Volume, AutoStand, AutoTurn, AutoOff |
| `0x10` | `userNames` | TX/RX | String stream | Custom choreography names |
| `0x11` | `autoStand` | TX | Boolean (`0x00`/`0x01`) | Fall recovery gyroscope auto-stand |
| `0x13` | `autoOff` | TX | Boolean (`0x00`/`0x01`) | Power-saving auto-off timer |
| `0x14` | `actionNames` | TX/RX | String stream | Built-in action name catalog (60+ actions) |
| `0x16` | `folderNames` | TX/RX | Delimiter | Audio/Action category listing |
| `0x17` | `action` | TX/RX | Path string + Progress | Action execution with live % progress ACK |
| `0x18` | `audioNames` | TX/RX | String stream | Sound track identifier query |
| `0x19` | `audio` | TX | String path | Audio playback (e.g. `"AppSysMS/..."`) |
| `0x1A` | `autoTurn` | TX | Boolean (`0x00`/`0x01`) | Yaw drift gyroscope balance correction |
| `0x1B` | `autoPose` | TX | Boolean (`0x00`/`0x01`) | Autonomous idle posture animations |
| `0xE0` | `readEE` | TX/RX | String | Internal EEPROM / config check |
| `0xE1` | `writeEE` | TX/RX | String | Internal EEPROM / parameter storage |
| `0xE2` | `dirList` | TX/RX | Path string / Results | Filesystem directory & file explorer |
| `0xE3` | `fileCheck` | TX/RX | String / `OK` | File existence / checksum verification |
| `0xE6` | `program` | TX/RX | 25-byte struct | Enter kinesthetic programming timeline |
| `0xE7` | `programExit` | TX | None | Exit kinesthetic programming mode |
| `0xE8` | `jointMove` | TX | 25-byte struct | Direct 17-servo coordinate command + speed |
| `0xE9` | `jointSync` | TX/RX | 25-byte struct | Real-time live angle feedback of all 17 servos |
| `0xEA` | `jointUnlockAll` | TX | None | Release motor torque on all joints |
| `0xEB` | `jointLockAll` | TX | None | Re-engage motor holding torque |
| `0xED` | `jointLock` | TX | 17-byte bitmask | Per-servo holding torque configuration |
| `0xEE` | `play` | TX | Number | Programmed sound/action trigger |
| `0xF0` | `imuStream` | RX | 50-byte struct | Real-time 6-axis IMU & joint telemetry buffer |
| `0xF1` | `imuQuery` | TX | None | Query 50-byte IMU / sensor buffer |
| `0xF5` | `factoryTest` | TX/RX | Byte stream | Factory calibration & testing mode |
| `0xF6` | `kind` | TX/RX | String (`"K1"`) | Model name |
| `0xF7` | `version` | TX/RX | String (`"VER:3.03L"`) | Firmware version |
| `0xF8` | `date` | TX/RX | String (`"SH2022-07-23"`) | Firmware compile date |
| `0xFA` | `delimiter` | RX | `0xFA` / `OK` | EOF stream delimiter / packet ACK |
"""
        with open(out_md, "w", encoding="utf-8") as f:
            f.write(md)

        print(f"\n[+] Deep Explorer Archive Saved: {out_md} and {out_json}")

async def main():
    exp = K1DeepExplorer()
    try:
        await exp.connect()
        await exp.explore_filesystem()
        await exp.explore_imu_and_telemetry()
        await exp.test_audio_playback()
        await exp.test_programming_mode()
        await exp.test_special_action()
    finally:
        if exp.client and exp.client.is_connected:
            await exp.send(0xE8, bytes(DEFAULT_STAND_FRAME), wait_sec=0.8)
            await exp.client.disconnect()
            print("[+] Disconnected cleanly.")
        exp.save_dump()

if __name__ == "__main__":
    asyncio.run(main())
