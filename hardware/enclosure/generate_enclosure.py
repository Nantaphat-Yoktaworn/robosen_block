"""
Robosen Block - Master Controller 3D Enclosure Generator
FreeCAD Script to generate a 4-part 3D printable enclosure:
  1. Case (Bottom housing with internal PCB standoffs and rubber feet recesses)
  2. Lid (Top cover with E-paper bezel, dual encoder openings, and dual button pockets)
  3. Knob (18mm knurled D-shaft dial with indicator dot)
  4. Button (Captive flanged tactile switch plunger)

Generated for: FreeCAD 1.1+
Author: Antigravity Assistant & Nantaphat Yoktaworn
"""

import sys
import os
import math

# Add FreeCAD binary directory to sys.path if not present
fc_bin = r"C:\Program Files\FreeCAD 1.1\bin"
if fc_bin not in sys.path:
    sys.path.append(fc_bin)

import FreeCAD
import Part
from FreeCAD import Base, Vector

def make_rounded_prism(w, d, h, r, z0=0.0):
    """Creates a solid prism of size (w, d, h) centered at (0,0) in X,Y with vertical corners rounded with radius r."""
    hw = w / 2.0
    hd = d / 2.0
    k = r * (1.0 - 1.0 / math.sqrt(2.0))
    
    p1 = Vector(hw - r, hd, z0)
    p2 = Vector(-hw + r, hd, z0)
    arc1 = Part.Arc(Vector(-hw + r, hd, z0), Vector(-hw + k, hd - k, z0), Vector(-hw, hd - r, z0))
    p3 = Vector(-hw, -hd + r, z0)
    arc2 = Part.Arc(Vector(-hw, -hd + r, z0), Vector(-hw + k, -hd + k, z0), Vector(-hw + r, -hd, z0))
    p4 = Vector(hw - r, -hd, z0)
    arc3 = Part.Arc(Vector(hw - r, -hd, z0), Vector(hw - k, -hd + k, z0), Vector(hw, -hd + r, z0))
    p5 = Vector(hw, hd - r, z0)
    arc4 = Part.Arc(Vector(hw, hd - r, z0), Vector(hw - k, hd - k, z0), Vector(hw - r, hd, z0))
    
    e1 = Part.makeLine(p1, p2)
    e2 = arc1.toShape()
    e3 = Part.makeLine(Vector(-hw, hd - r, z0), p3)
    e4 = arc2.toShape()
    e5 = Part.makeLine(Vector(-hw + r, -hd, z0), p4)
    e6 = arc3.toShape()
    e7 = Part.makeLine(Vector(hw, -hd + r, z0), p5)
    e8 = arc4.toShape()
    
    wire = Part.Wire([e1, e2, e3, e4, e5, e6, e7, e8])
    face = Part.Face(wire)
    solid = face.extrude(Vector(0, 0, h))
    return solid

def build_case():
    print("-> Constructing Case (Bottom Box)...")
    # 1. Main outer prism (129 x 72 x 26 mm, R4 corner radius)
    outer = make_rounded_prism(129.0, 72.0, 26.0, 4.0, 0.0)
    # 2. Main cavity (117.5 x 64.0 mm, depth 23.6 mm, base floor 2.4 mm)
    inner = make_rounded_prism(117.5, 64.0, 24.5, 2.0, 2.4)
    case_shell = outer.cut(inner)
    
    # 3. Rubber feet recesses on bottom face (Z=0, diam 8mm, depth 0.8mm)
    feet = [
        Part.makeCylinder(4.0, 0.8, Vector(fx, fy, -0.01), Vector(0, 0, 1))
        for fx in [-52.0, 52.0] for fy in [-25.0, 25.0]
    ]
    for f in feet:
        case_shell = case_shell.cut(f)
        
    # 4. PCB Standoffs (H1, H2, H3, H4) - 22.0mm tall from Z=2.4 to Z=24.4
    standoff_coords = [
        (-48.00, 1.00),    # H1
        (48.00, 1.00),     # H2
        (-52.75, -27.50),  # H3
        (52.75, -27.50)    # H4
    ]
    standoff_bosses = []
    standoff_holes = []
    for sx, sy in standoff_coords:
        boss = Part.makeCylinder(3.5, 22.0, Vector(sx, sy, 2.4), Vector(0, 0, 1))
        hole = Part.makeCylinder(2.1, 6.0, Vector(sx, sy, 18.9), Vector(0, 0, 1))
        standoff_bosses.append(boss)
        standoff_holes.append(hole)
        
    # 5. Lid Corner Screw Bosses (4 outer corners) - 23.6mm tall from Z=2.4 to Z=26.0
    lid_corner_coords = [
        (-60.5, -31.0),
        (-60.5, 31.0),
        (60.5, -31.0),
        (60.5, 31.0)
    ]
    corner_bosses = []
    corner_holes = []
    for cx, cy in lid_corner_coords:
        boss = Part.makeCylinder(3.8, 23.6, Vector(cx, cy, 2.4), Vector(0, 0, 1))
        hole = Part.makeCylinder(2.1, 6.5, Vector(cx, cy, 19.8), Vector(0, 0, 1))
        corner_bosses.append(boss)
        corner_holes.append(hole)
        
    for b in standoff_bosses + corner_bosses:
        case_shell = case_shell.fuse(b)
        
    for h in standoff_holes + corner_holes:
        case_shell = case_shell.cut(h)
        
    # 6. Side Cutouts (U-notches in base)
    # Left Pogo Dock J1 at X=-64.5, Y=+1.00
    pogo_l = Part.makeBox(6.0, 20.2, 5.0, Vector(-66.0, 1.00 - 10.1, 22.5))
    chamfer_l = Part.makeBox(2.0, 22.0, 6.0, Vector(-66.0, 1.00 - 11.0, 21.5))
    
    # Right Pogo Dock J2 at X=+64.5, Y=+1.00
    pogo_r = Part.makeBox(6.0, 20.2, 5.0, Vector(60.0, 1.00 - 10.1, 22.5))
    chamfer_r = Part.makeBox(2.0, 22.0, 6.0, Vector(64.0, 1.00 - 11.0, 21.5))
    
    # USB-C at front (Y=-36.0), X=-18.00
    usbc = Part.makeBox(12.0, 6.0, 5.0, Vector(-18.00 - 6.0, -37.0, 23.5))
    
    # 20mm round Power Switch Hole on rear wall (Y=+36.0), centered at X=0.0, Z=21.0
    pwr_hole = Part.makeCylinder(10.0, 10.0, Vector(0, 31.0, 21.0), Vector(0, 1, 0))
    
    case_shell = case_shell.cut(pogo_l).cut(chamfer_l).cut(pogo_r).cut(chamfer_r).cut(usbc).cut(pwr_hole)
    return case_shell

def build_lid():
    print("-> Constructing Lid (Top Box Cover)...")
    # 1. Main outer prism from Z=26.0 to Z=42.4 (height=16.4mm)
    outer = make_rounded_prism(129.0, 72.0, 16.4, 4.0, 26.0)
    # 2. Main cavity from Z=26.0 to Z=40.0 (height=14.0mm, top plate=2.4mm)
    inner = make_rounded_prism(117.5, 64.0, 14.0, 2.0, 25.9)
    lid_shell = outer.cut(inner)
    
    # 3. Corner posts for screw retention
    lid_corner_coords = [
        (-60.5, -31.0),
        (-60.5, 31.0),
        (60.5, -31.0),
        (60.5, 31.0)
    ]
    for cx, cy in lid_corner_coords:
        post = Part.makeCylinder(3.8, 14.0, Vector(cx, cy, 26.0), Vector(0, 0, 1))
        lid_shell = lid_shell.fuse(post)
        
    for cx, cy in lid_corner_coords:
        # Through hole diam 3.4mm
        thru = Part.makeCylinder(1.7, 18.0, Vector(cx, cy, 25.0), Vector(0, 0, 1))
        # Counterbore diam 6.2mm, depth 2.5mm
        cbore = Part.makeCylinder(3.1, 3.0, Vector(cx, cy, 39.9), Vector(0, 0, 1))
        lid_shell = lid_shell.cut(thru).cut(cbore)
        
    # 4. E-Paper Screen Window (Horizontally centered at X=0.0, Y=15.5)
    screen_cut = Part.makeBox(48.0, 23.5, 5.0, Vector(-24.0, 15.5 - 11.75, 39.5))
    bezel_cut = Part.makeBox(50.5, 26.0, 1.5, Vector(-25.25, 15.5 - 13.0, 39.0))
    lid_shell = lid_shell.cut(screen_cut).cut(bezel_cut)
    
    # 5. Rotary Encoder Holes (Dual Knobs)
    for kx, ky in [(-47.75, 17.50), (48.13, 17.50)]:
        khole = Part.makeCylinder(4.5, 6.0, Vector(kx, ky, 38.5), Vector(0, 0, 1))
        lid_shell = lid_shell.cut(khole)
        
    # 6. Push Button Holes & Captive Flange Pockets (Dual Buttons)
    for bx, by in [(-42.00, -13.00), (40.00, -13.00)]:
        bhole = Part.makeCylinder(4.3, 6.0, Vector(bx, by, 38.5), Vector(0, 0, 1))
        pocket = Part.makeCylinder(6.0, 2.0, Vector(bx, by, 39.0), Vector(0, 0, 1))
        lid_shell = lid_shell.cut(bhole).cut(pocket)
        
    # 7. Port Upper Clearances
    pogo_l_top = Part.makeBox(6.0, 20.2, 3.0, Vector(-66.0, 1.00 - 10.1, 25.5))
    chamfer_l_top = Part.makeBox(2.0, 22.0, 3.0, Vector(-66.0, 1.00 - 11.0, 25.5))
    pogo_r_top = Part.makeBox(6.0, 20.2, 3.0, Vector(60.0, 1.00 - 10.1, 25.5))
    chamfer_r_top = Part.makeBox(2.0, 22.0, 3.0, Vector(64.0, 1.00 - 11.0, 25.5))
    usbc_top = Part.makeBox(12.0, 6.0, 4.0, Vector(-18.00 - 6.0, -37.0, 25.5))
    pwr_hole_top = Part.makeCylinder(10.0, 10.0, Vector(0, 31.0, 21.0), Vector(0, 1, 0))
    
    lid_shell = lid_shell.cut(pogo_l_top).cut(chamfer_l_top).cut(pogo_r_top).cut(chamfer_r_top).cut(usbc_top).cut(pwr_hole_top)
    return lid_shell

def build_knob():
    print("-> Constructing Knob (Rotary Dial)...")
    # Main body: diam 18mm, height 14mm
    body = Part.makeCylinder(9.0, 14.0, Vector(0, 0, 0), Vector(0, 0, 1))
    
    # Top edge chamfer
    top_rim = Part.makeCylinder(9.5, 1.5, Vector(0, 0, 13.0), Vector(0, 0, 1))
    cone = Part.makeCone(8.0, 9.5, 1.5, Vector(0, 0, 13.0), Vector(0, 0, 1))
    chamfer_ring = top_rim.cut(cone)
    body = body.cut(chamfer_ring)
    
    # 24 knurled grip flutes
    for i in range(24):
        ang = i * (2.0 * math.pi / 24.0)
        gx = 9.0 * math.cos(ang)
        gy = 9.0 * math.sin(ang)
        groove = Part.makeCylinder(0.65, 14.2, Vector(gx, gy, -0.1), Vector(0, 0, 1))
        body = body.cut(groove)
        
    # Indicator dot on top face
    dot = Part.makeCylinder(1.0, 1.0, Vector(0, 6.5, 13.2), Vector(0, 0, 1))
    body = body.cut(dot)
    
    # Bottom skirt recess
    skirt = Part.makeCylinder(5.5, 2.01, Vector(0, 0, -0.01), Vector(0, 0, 1))
    body = body.cut(skirt)
    
    # 6.0mm D-shaft socket (diam 6.2mm with flat at Y=1.55, depth 10mm from Z=2.0 to 12.0)
    d_cyl = Part.makeCylinder(3.1, 10.1, Vector(0, 0, 1.99), Vector(0, 0, 1))
    d_flat_block = Part.makeBox(8.0, 5.0, 10.2, Vector(-4.0, 1.55, 1.95))
    d_socket = d_cyl.cut(d_flat_block)
    body = body.cut(d_socket)
    return body

def build_button():
    print("-> Constructing Button (Captive Tactile Switch Cap)...")
    # Base flange: diam 11.0mm, height 1.5mm
    flange = Part.makeCylinder(5.5, 1.5, Vector(0, 0, 0), Vector(0, 0, 1))
    # Stem: diam 8.0mm, height 10.0mm (from Z=1.5 to 11.5)
    stem = Part.makeCylinder(4.0, 10.0, Vector(0, 0, 1.5), Vector(0, 0, 1))
    # Actuator nub: diam 3.5mm, height 1.0mm underneath
    nub = Part.makeCylinder(1.75, 1.0, Vector(0, 0, -1.0), Vector(0, 0, 1))
    
    button = flange.fuse(stem).fuse(nub)
    # Concave spherical dish on top
    dish = Part.makeSphere(12.0, Vector(0, 0, 22.8))
    button = button.cut(dish)
    return button

def main():
    output_dir = r"C:\Users\nnnn\Projects\robosen_block\hardware\enclosure"
    fcstd_path = os.path.join(output_dir, "master_block_enclosure.FCStd")
    
    print(f"Creating FreeCAD Document: {fcstd_path}")
    doc = FreeCAD.newDocument("MasterBlockEnclosure")
    
    # Build parts
    case_solid = build_case()
    lid_solid = build_lid()
    knob_solid = build_knob()
    button_solid = build_button()
    
    # Add to document
    f_case = doc.addObject("Part::Feature", "Case")
    f_case.Label = "Case (Bottom Box)"
    f_case.Shape = case_solid
    
    f_lid = doc.addObject("Part::Feature", "Lid")
    f_lid.Label = "Lid (Top Cover)"
    f_lid.Shape = lid_solid
    
    f_knob = doc.addObject("Part::Feature", "Knob")
    f_knob.Label = "Knob (18mm D-Shaft Dial)"
    f_knob.Shape = knob_solid
    
    f_button = doc.addObject("Part::Feature", "Button")
    f_button.Label = "Button (Captive Cap)"
    f_button.Shape = button_solid
    
    doc.recompute()
    doc.saveAs(fcstd_path)
    FreeCAD.closeDocument("MasterBlockEnclosure")
    print(f"[SUCCESS] FreeCAD model successfully saved to:\n  {fcstd_path}")

if __name__ == "__main__":
    main()
