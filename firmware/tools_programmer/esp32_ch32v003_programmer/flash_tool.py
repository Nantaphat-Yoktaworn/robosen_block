#!/usr/bin/env python3
"""
ESP32-S3 CH32V003 Binary Flasher Tool
--------------------------------------
Host workflow utility for programming and verifying binary firmware images
on the WCH CH32V003 microcontroller via the ESP32-S3 programmer.

Usage:
  python tools/flash_tool.py --port COM10 --bin firmware/ch32_blink/blink.bin --addr 0x08000000 [--reset]
"""

import argparse
import os
import sys
import time
import serial

CH32V003_FLASH_BASE = 0x08000000
CH32V003_FLASH_SIZE = 16 * 1024  # 16 KB

def main():
    parser = argparse.ArgumentParser(description="ESP32-S3 CH32V003 Binary Flasher Tool")
    parser.add_argument("--port", default="COM3", help="Serial port (default: COM3)")
    parser.add_argument("--test", "--detect", action="store_true", help="Test connection and detect CH32V003 target without flashing")
    parser.add_argument("--bin", default=None, help="Path to target binary file (.bin)")
    parser.add_argument("--addr", default="0x08000000", help="Target flash memory address (default: 0x08000000)")
    parser.add_argument("--reset", action="store_true", help="Execute target reset/run after flashing and verification")
    args = parser.parse_args()

    # If --test is selected, we skip binary file checks
    if not args.test and not args.bin:
        default_bin = os.path.join("firmware", "ch32_blink", "blink.bin")
        if os.path.exists(default_bin):
            args.bin = default_bin
        else:
            print("Error: No binary file specified. Use --bin <path_to.bin> or run with --test to check connection.", file=sys.stderr)
            sys.exit(1)

    file_size = 0
    addr_val = 0x08000000
    hex_payload = ""

    if not args.test:
        if not os.path.exists(args.bin):
            print(f"Error: Binary file not found at '{args.bin}'", file=sys.stderr)
            sys.exit(1)

        try:
            with open(args.bin, "rb") as f:
                data = f.read()
        except Exception as e:
            print(f"Error: Failed to read binary file '{args.bin}': {e}", file=sys.stderr)
            sys.exit(1)

        file_size = len(data)
        if file_size == 0:
            print(f"Error: Binary file '{args.bin}' is empty (0 bytes).", file=sys.stderr)
            sys.exit(1)

        try:
            addr_val = int(args.addr, 16)
        except ValueError:
            print(f"Error: Invalid hex address string '{args.addr}'", file=sys.stderr)
            sys.exit(1)

        print(f"Loaded binary '{args.bin}': {file_size} bytes")
        print(f"Target memory address: 0x{addr_val:08X}")

        if addr_val < CH32V003_FLASH_BASE or (addr_val + file_size) > (CH32V003_FLASH_BASE + CH32V003_FLASH_SIZE):
            print(
                f"Error: Binary bounds (0x{addr_val:08X} - 0x{(addr_val + file_size):08X}) "
                f"exceed CH32V003 16KB flash memory (0x{CH32V003_FLASH_BASE:08X} - 0x{(CH32V003_FLASH_BASE + CH32V003_FLASH_SIZE):08X}).",
                file=sys.stderr
            )
            sys.exit(1)

        hex_payload = data.hex()



    # 3. Connect to ESP32-S3 programmer over serial
    print(f"Connecting to ESP32-S3 programmer on port {args.port} (115200 baud)...")
    try:
        s = serial.Serial(args.port, 115200, timeout=3)
    except Exception as e:
        print(f"Error: Failed to open serial port {args.port}: {e}", file=sys.stderr)
        sys.exit(1)

    s.dtr = False
    s.rts = True
    time.sleep(0.1)
    s.rts = False
    time.sleep(0.5)

    startup_out = ""
    t_end = time.time() + 3
    while time.time() < t_end:
        if s.in_waiting:
            startup_out += s.read(s.in_waiting).decode("utf-8", errors="ignore")
        time.sleep(0.05)

    print("=== PROGRAMMER INITIALIZATION LOG ===")
    print(startup_out.strip())

    # 4. Target detection check
    if "Target detect: OK" not in startup_out:
        # Re-send explicit detect command if startup trace was truncated
        s.write(b"detect\n")
        detect_out = ""
        t_end = time.time() + 2
        while time.time() < t_end:
            if s.in_waiting:
                detect_out += s.read(s.in_waiting).decode("utf-8", errors="ignore")
            time.sleep(0.05)
        if "Target detect: OK" not in detect_out:
            print("Error: Target CH32V003 not detected on programmer!", file=sys.stderr)
            s.close()
            sys.exit(1)

    print("\n[STEP 1] Target Detection: OK")

    if args.test:
        print("\n=== TEST COMPLETED SUCCESSFULLY ===")
        print("CH32V003 target is connected and responding properly over SWIO!")
        s.close()
        sys.exit(0)

    # 5. Program binary payload in 256-byte chunks
    CHUNK_SIZE = 256
    print(f"\n[STEP 2] Programming target binary via targetProgramBinary() ({file_size} bytes)...")

    for offset in range(0, file_size, CHUNK_SIZE):
        chunk_data = data[offset:offset + CHUNK_SIZE]
        chunk_addr = addr_val + offset
        chunk_hex = chunk_data.hex()

        flash_cmd = f"flash {chunk_addr:08X} {chunk_hex}\n".encode("utf-8")
        s.write(flash_cmd)

        flash_out = ""
        t_end = time.time() + 5
        while time.time() < t_end:
            if s.in_waiting:
                chunk_str = s.read(s.in_waiting).decode("utf-8", errors="ignore")
                flash_out += chunk_str
                if "flash: OK" in flash_out or "FAILED" in flash_out:
                    break
            time.sleep(0.01)

        if "flash: OK" not in flash_out:
            print(f"\nError: Programming failed at 0x{chunk_addr:08X}: {flash_out}", file=sys.stderr)
            s.close()
            sys.exit(1)
        else:
            pct = min(100, int((offset + len(chunk_data)) * 100 / file_size))
            print(f"  Flashing: {offset + len(chunk_data)}/{file_size} bytes ({pct}%) at 0x{chunk_addr:08X} [OK]")

    print("\n[STEP 2 RESULT] targetProgramBinary: All chunks OK")

    # 6. Verify programmed binary in 256-byte chunks
    print(f"\n[STEP 3] Verifying programmed memory via targetVerifyBinary() ({file_size} bytes)...")
    for offset in range(0, file_size, CHUNK_SIZE):
        chunk_data = data[offset:offset + CHUNK_SIZE]
        chunk_addr = addr_val + offset
        chunk_hex = chunk_data.hex()

        verify_cmd = f"verify {chunk_addr:08X} {chunk_hex}\n".encode("utf-8")
        s.write(verify_cmd)

        verify_out = ""
        t_end = time.time() + 5
        while time.time() < t_end:
            if s.in_waiting:
                chunk_str = s.read(s.in_waiting).decode("utf-8", errors="ignore")
                verify_out += chunk_str
                if "verify: OK" in verify_out or "FAILED" in verify_out:
                    break
            time.sleep(0.01)

        if "verify: OK" not in verify_out:
            print(f"\nError: Verification failed at 0x{chunk_addr:08X}: {verify_out}", file=sys.stderr)
            s.close()
            sys.exit(1)
        else:
            pct = min(100, int((offset + len(chunk_data)) * 100 / file_size))
            print(f"  Verifying: {offset + len(chunk_data)}/{file_size} bytes ({pct}%) [OK]")

    print("\n[STEP 3 RESULT] targetVerifyBinary: 100% verified match!")


    print("\n=== FLASHING & VERIFICATION SUMMARY ===")
    print("SUCCESS: Firmware successfully programmed and verified on CH32V003!")

    # 7. Optional explicit target reset/run
    if args.reset:
        print("\n[STEP 4] Executing explicit targetResetRun()...")
        s.write(b"reset\n")
        reset_out = ""
        t_end = time.time() + 3
        while time.time() < t_end:
            if s.in_waiting:
                chunk = s.read(s.in_waiting).decode("utf-8", errors="ignore")
                reset_out += chunk
                sys.stdout.write(chunk)
                sys.stdout.flush()
            time.sleep(0.05)
        if "Reset/run: OK" in reset_out:
            print("[STEP 4 RESULT] targetResetRun: OK (Target execution resumed)")
        else:
            print("Error: Target reset/run failed!", file=sys.stderr)
            s.close()
            sys.exit(1)
    else:
        print("Note: Target remains in debug halt state. (Pass --reset option to execute binary).")

    s.close()
    sys.exit(0)

if __name__ == "__main__":
    main()
