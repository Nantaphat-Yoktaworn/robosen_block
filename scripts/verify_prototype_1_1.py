from pathlib import Path
import pcbnew
import math

ROOT = Path(__file__).resolve().parent.parent
pcb_path = ROOT / 'hardware' / 'prototype_1_1' / 'master_block' / 'robosen_master_block.kicad_pcb'
board = pcbnew.LoadBoard(str(pcb_path))

print("=== 1. TRACK & VIA COUNT ===")
tracks = [t for t in board.GetTracks() if t.Type() != pcbnew.PCB_VIA_T]
vias = [t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]
print(f"Total track segments: {len(tracks)}")
print(f"Total vias: {len(vias)}")

print("\n=== 2. ESP32-S3 (U1) ROW SPACING & PAD POSITIONS ===")
for f in board.GetFootprints():
    if f.GetReference() == 'U1':
        p1 = f.FindPadByNumber('1').GetPosition()
        p22 = f.FindPadByNumber('22').GetPosition()
        p23 = f.FindPadByNumber('23').GetPosition()
        p44 = f.FindPadByNumber('44').GetPosition()
        row1_y = p1.y / 1e6
        row2_y = p23.y / 1e6
        spacing = abs(row1_y - row2_y)
        print(f"Pad 1:  ({p1.x/1e6:.2f}, {p1.y/1e6:.2f}) mm")
        print(f"Pad 22: ({p22.x/1e6:.2f}, {p22.y/1e6:.2f}) mm")
        print(f"Pad 23: ({p23.x/1e6:.2f}, {p23.y/1e6:.2f}) mm")
        print(f"Pad 44: ({p44.x/1e6:.2f}, {p44.y/1e6:.2f}) mm")
        print(f"Row 1 Y: {row1_y:.2f} mm, Row 2 Y: {row2_y:.2f} mm")
        print(f"Calculated Pin Row Spacing: {spacing:.2f} mm ({spacing/25.4:.3f} inches / {spacing/0.0254:.1f} mils)")

print("\n=== 3. M3 MOUNTING HOLE CLEARANCES ===")
holes = {
    'H1': (96.25, 92.00),
    'H2': (192.25, 92.00),
    'H3': (91.50, 120.50),
    'H4': (197.00, 120.50)
}
boss_radius = 3.2

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
        clearance = d - 0.3
        if clearance < min_dist:
            min_dist = clearance
            closest_info = f"Via of {v.GetNetname()}"

    status = "OK (Clear of screw boss)" if min_dist >= boss_radius else f"CAUTION (< {boss_radius}mm)"
    print(f"{h_name} at ({hx:6.2f}, {hy:6.2f}): Closest copper = {min_dist:5.2f} mm -> {closest_info} -> {status}")
