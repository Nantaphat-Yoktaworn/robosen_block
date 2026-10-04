import pcbnew
import math

board = pcbnew.LoadBoard(r"C:\Users\nnnn\Projects\robosen_block\hardware\kicad\robosen_master_block.kicad_pcb")

print("=== COMPONENT SIDES & BOUNDING BOXES ===")
front_fps = []
back_fps = []

for fp in board.GetFootprints():
    ref = fp.GetReference()
    pos = fp.GetPosition()
    bb = fp.GetBoundingBox(False, False)
    item = {
        "ref": ref,
        "fp": fp,
        "x": pos.x / 1e6,
        "y": pos.y / 1e6,
        "xmin": bb.GetX() / 1e6,
        "xmax": (bb.GetX() + bb.GetWidth()) / 1e6,
        "ymin": bb.GetY() / 1e6,
        "ymax": (bb.GetY() + bb.GetHeight()) / 1e6,
        "w": bb.GetWidth() / 1e6,
        "h": bb.GetHeight() / 1e6,
        "rot": fp.GetOrientationDegrees()
    }
    if fp.IsFlipped():
        back_fps.append(item)
    else:
        front_fps.append(item)

def check_overlaps(fp_list, side_name):
    print(f"\n--- Checking Overlaps on {side_name} ({len(fp_list)} footprints) ---")
    overlaps = []
    for i in range(len(fp_list)):
        for j in range(i + 1, len(fp_list)):
            f1 = fp_list[i]
            f2 = fp_list[j]
            # Bounding box overlap test
            overlap_x = max(0, min(f1["xmax"], f2["xmax"]) - max(f1["xmin"], f2["xmin"]))
            overlap_y = max(0, min(f1["ymax"], f2["ymax"]) - max(f1["ymin"], f2["ymin"]))
            if overlap_x > 0.5 and overlap_y > 0.5:
                overlaps.append((f1, f2, overlap_x, overlap_y))
    if not overlaps:
        print(f"  No bounding box overlaps detected on {side_name}!")
    else:
        for f1, f2, ox, oy in overlaps:
            print(f"  [OVERLAP {side_name}] {f1['ref']} <--> {f2['ref']} : {ox:.1f}mm x {oy:.1f}mm overlap zone")

check_overlaps(front_fps, "FRONT")
check_overlaps(back_fps, "BACK")

print("\n=== FRONT vs BACK STACKING ANALYSIS ===")
for b in back_fps:
    for f in front_fps:
        ox = max(0, min(b["xmax"], f["xmax"]) - max(b["xmin"], f["xmin"]))
        oy = max(0, min(b["ymax"], f["ymax"]) - max(b["ymin"], f["ymin"]))
        if ox > 2.0 and oy > 2.0:
            print(f"  [Z-STACK] Back:{b['ref']} is underneath Front:{f['ref']} (Overlap area: {ox:.1f}mm x {oy:.1f}mm)")
