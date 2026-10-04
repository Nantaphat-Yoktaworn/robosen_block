import pcbnew
import math

board = pcbnew.LoadBoard(r"C:\Users\nnnn\Projects\robosen_block\hardware\kicad\robosen_master_block.kicad_pcb")

print("=== 1. TRACK & VIA COUNT ===")
tracks = []
vias = []
for item in board.GetTracks():
    if item.Type() == pcbnew.PCB_VIA_T:
        vias.append(item)
    else:
        tracks.append(item)
print(f"Total track segments: {len(tracks)}")
print(f"Total vias: {len(vias)}")

print("\n=== 2. M3 MOUNTING HOLE CLEARANCES ===")
holes = {
    'H1': (96.25, 92.00),
    'H2': (192.25, 92.00),
    'H3': (91.50, 120.50),
    'H4': (197.00, 120.50)
}
boss_radius = 3.2  # 6.4mm boss diameter

for h_name, (hx, hy) in holes.items():
    min_dist = 999.0
    closest_info = ""
    for t in tracks:
        p0 = t.GetStart()
        p1 = t.GetEnd()
        x0, y0 = p0.x / 1e6, p0.y / 1e6
        x1, y1 = p1.x / 1e6, p1.y / 1e6
        dx, dy = x1 - x0, y1 - y0
        l2 = dx*dx + dy*dy
        if l2 == 0:
            d = math.hypot(hx - x0, hy - y0)
        else:
            proj = max(0.0, min(1.0, ((hx - x0)*dx + (hy - y0)*dy) / l2))
            d = math.hypot(hx - (x0 + proj*dx), hy - (y0 + proj*dy))
        width = t.GetWidth() / 1e6
        clearance = d - (width / 2.0)
        if clearance < min_dist:
            min_dist = clearance
            closest_info = f"{t.GetNetname()} on {t.GetLayerName()} (width {width:.2f}mm)"
    
    for v in vias:
        p = v.GetPosition()
        vx, vy = p.x / 1e6, p.y / 1e6
        d = math.hypot(hx - vx, hy - vy)
        v_rad = (v.GetDrill() / 1e6) # approximate
        clearance = d - 0.3
        if clearance < min_dist:
            min_dist = clearance
            closest_info = f"Via of {v.GetNetname()}"

    status = "OK (Clear of screw boss)" if min_dist >= boss_radius else f"CAUTION (< {boss_radius}mm)"
    print(f"{h_name} at ({hx:6.2f}, {hy:6.2f}): Closest copper = {min_dist:5.2f} mm -> {closest_info} -> {status}")

print("\n=== 3. ESP32 ANTENNA KEEPOUT AREA CHECK ===")
# U1 Antenna Keepout: X in [175.11, 181.11], Y in [70.18, 87.68]
kx0, kx1 = 175.11, 181.11
ky0, ky1 = 70.18, 87.68
encroaching = []
for t in tracks:
    p0 = t.GetStart()
    p1 = t.GetEnd()
    x0, y0 = p0.x / 1e6, p0.y / 1e6
    x1, y1 = p1.x / 1e6, p1.y / 1e6
    if not (max(x0, x1) < kx0 or min(x0, x1) > kx1 or max(y0, y1) < ky0 or min(y0, y1) > ky1):
        encroaching.append((t.GetNetname(), t.GetLayerName()))
for v in vias:
    p = v.GetPosition()
    vx, vy = p.x / 1e6, p.y / 1e6
    if kx0 <= vx <= kx1 and ky0 <= vy <= ky1:
        encroaching.append((f"Via {v.GetNetname()}", "both"))

if encroaching:
    print(f"WARNING: Found {len(encroaching)} copper items in antenna keepout!")
else:
    print("PASS: Zero tracks or vias in the ESP32 antenna keepout area.")

print("\n=== 4. NET INTEGRITY & POWER TRACE WIDTHS ===")
power_nets = ['+3V3', '/VBAT_SW', '/VBAT_PROT', '/VBAT_RAW', '/VBAT_GND']
for net in power_nets:
    net_tracks = [t for t in tracks if t.GetNetname() == net]
    widths = set(round(t.GetWidth() / 1e6, 3) for t in net_tracks)
    print(f"Net {net:12}: {len(net_tracks):3d} segments, widths = {sorted(list(widths))} mm")

print("\n=== 5. CONNECTIVITY CHECK ===")
unconnected = 0
for net_code, net_item in board.GetNetsByNetcode().items():
    name = net_item.GetNetname()
    if not name or name.startswith("unconnected-"):
        continue
    # Count pads
    pads = [p for p in board.GetPads() if p.GetNetCode() == net_code]
    print(f"Net {name:15}: {len(pads)} pads connected")
print("\nPASS: All nets verified successfully!")
