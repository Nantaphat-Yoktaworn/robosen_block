#!/usr/bin/env python3
"""
Generate KiCad footprints and SVG previews for Action Block:
1. TENSTAR_CH32V003F4P6 (Breadboard-compatible 2x11 DIP-22 0.6" socket/module, 31x17.8mm)
2. WS2812B_5050 (Addressable RGB LED 5.0x5.0mm SMD)
3. Pogo_4Pin_Dock_2.54mm (Copied / customized from master block)
4. C_0805 (Decoupling Capacitor)
"""

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FP_DIR = ROOT / "hardware" / "action_block" / "action_block.pretty"
SVG_DIR = ROOT / "hardware" / "action_block" / "footprint_svg"
FP_DIR.mkdir(parents=True, exist_ok=True)
SVG_DIR.mkdir(parents=True, exist_ok=True)

# Copy Pogo 4-Pin and C_Disc from master_block for convenience
master_fp_dir = ROOT / "hardware" / "master_block" / "robosen_master.pretty"
if (master_fp_dir / "Pogo_4Pin_Dock_2.54mm.kicad_mod").exists():
    shutil.copy(master_fp_dir / "Pogo_4Pin_Dock_2.54mm.kicad_mod", FP_DIR / "Pogo_4Pin_Dock_2.54mm.kicad_mod")
    print("Copied Pogo_4Pin_Dock_2.54mm.kicad_mod")
if (master_fp_dir / "C_Disc_P2.54mm.kicad_mod").exists():
    shutil.copy(master_fp_dir / "C_Disc_P2.54mm.kicad_mod", FP_DIR / "C_Disc_P2.54mm.kicad_mod")
    print("Copied C_Disc_P2.54mm.kicad_mod")

# -----------------------------------------------------------------------------
# 1. TENSTAR_CH32V003F4P6 Footprint
# -----------------------------------------------------------------------------
# 31.0 mm x 17.8 mm
# 2 rows of 11 pins: Pitch = 2.54 mm, Row span = 15.24 mm (600 mil)
# Top row: Y = -7.62 mm
# Bottom row: Y = +7.62 mm
# X range: 10 spaces of 2.54 = 25.4 mm -> X from -12.7 mm to +12.7 mm
# Board outline: X: [-15.5, +15.5], Y: [-8.9, +8.9]

top_labels = ["PC4", "PC3", "PC2", "PC1", "PC0", "PA2", "PA1", "RX", "TX", "3V3", "GND"]
bot_labels = ["PC5", "PC6", "PC7", "PD0", "SWIO", "PD2", "PD3", "PD4", "PD7", "3V3", "GND"]

tenstar_lines = [
    '(footprint "TENSTAR_CH32V003F4P6"',
    '\t(version 20240108)',
    '\t(generator "antigravity-kicad-generator")',
    '\t(layer "F.Cu")',
    '\t(descr "TENSTAR CH32V003F4P6 Development Board, 2x11 pins, 2.54mm pitch, 15.24mm (600 mil / 0.6 in) row spacing, 31x17.8mm outer boundary, breadboard compatible")',
    '\t(tags "WCH CH32V003 RISC-V TENSTAR Breadboard 2.54mm DIP-22")',
    '\t(property "Reference" "U**"',
    '\t\t(at 0 -11.0 0)',
    '\t\t(layer "F.SilkS")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(property "Value" "TENSTAR_CH32V003F4P6"',
    '\t\t(at 0 11.0 0)',
    '\t\t(layer "F.Fab")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(attr through_hole)',
    '',
    '\t; Outer PCB Outline (31.0 x 17.8 mm)',
    '\t(fp_rect (start -15.5 -8.9) (end 15.5 8.9) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_rect (start -15.5 -8.9) (end 15.5 8.9) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))',
    '\t(fp_rect (start -16.0 -9.4) (end 17.5 9.4) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    '',
    '\t; USB Type-C Receptacle Overhang (Right Edge)',
    '\t(fp_rect (start 12.0 -4.5) (end 17.0 4.5) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_rect (start 12.0 -4.5) (end 17.0 4.5) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))',
    '\t(fp_text user "USB-C" (at 14.5 0 90) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    '',
    '\t; MCU & Button Outlines',
    '\t(fp_rect (start -3.5 -3.5) (end 3.5 3.5) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_circle (center -2.5 -2.5) (end -2.0 -2.5) (stroke (width 0.12) (type solid)) (fill solid) (layer "F.SilkS"))',
    '\t(fp_text user "CH32V003" (at 0 0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    '\t(fp_rect (start -8.0 -2.0) (end -4.5 2.0) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_text user "RST" (at -6.25 0 90) (layer "F.SilkS") (effects (font (size 0.6 0.6) (thickness 0.09))))',
    ''
]

# Add Top Row Pads (Pins 1..11) at Y = -7.62 mm
for i in range(11):
    pnum = i + 1
    x = -12.7 + (i * 2.54)
    y = -7.62
    pad_shape = "rect" if pnum == 1 else "circle"
    tenstar_lines.append(f'\t(pad "{pnum}" thru_hole {pad_shape} (at {x:.2f} {y:.2f}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))')
    lbl = top_labels[i]
    # Silkscreen pin label slightly inside
    tenstar_lines.append(f'\t(fp_text user "{lbl}" (at {x:.2f} {y+2.0:.2f} 90) (layer "F.SilkS") (effects (font (size 0.65 0.65) (thickness 0.09))))')

# Add Bottom Row Pads (Pins 12..22) at Y = +7.62 mm
for i in range(11):
    pnum = i + 12
    x = -12.7 + (i * 2.54)
    y = 7.62
    pad_shape = "rect" if pnum == 12 else "circle"
    tenstar_lines.append(f'\t(pad "{pnum}" thru_hole {pad_shape} (at {x:.2f} {y:.2f}) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))')
    lbl = bot_labels[i]
    # Silkscreen pin label slightly inside
    tenstar_lines.append(f'\t(fp_text user "{lbl}" (at {x:.2f} {y-2.0:.2f} 90) (layer "F.SilkS") (effects (font (size 0.65 0.65) (thickness 0.09))))')

tenstar_lines.append(')')

with open(FP_DIR / "TENSTAR_CH32V003F4P6.kicad_mod", "w") as f:
    f.write("\n".join(tenstar_lines) + "\n")
print("Generated TENSTAR_CH32V003F4P6.kicad_mod")

# -----------------------------------------------------------------------------
# 2. WS2812B_5050 Footprint (Addressable RGB LED)
# -----------------------------------------------------------------------------
# 5.0 mm x 5.0 mm SMD PLCC-4
# Pin 1: VDD, Pin 2: DOUT, Pin 3: GND, Pin 4: DIN
# Pitch: 1.65 mm, Span between opposite pads: 4.8 mm
# Pad size: 1.7 mm wide x 1.0 mm tall

ws2812_lines = [
    '(footprint "WS2812B_5050"',
    '\t(version 20240108)',
    '\t(generator "antigravity-kicad-generator")',
    '\t(layer "F.Cu")',
    '\t(descr "WS2812B Addressable RGB LED, 5.0x5.0mm PLCC-4 SMD package")',
    '\t(tags "WS2812B RGB LED NeoPixel 5050 PLCC-4 SMD")',
    '\t(property "Reference" "D**"',
    '\t\t(at 0 -3.6 0)',
    '\t\t(layer "F.SilkS")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(property "Value" "WS2812B"',
    '\t\t(at 0 3.6 0)',
    '\t\t(layer "F.Fab")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(attr smd)',
    '',
    '\t; Body outline 5.0 x 5.0 mm',
    '\t(fp_rect (start -2.5 -2.5) (end 2.5 2.5) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_rect (start -2.5 -2.5) (end 2.5 2.5) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))',
    '\t(fp_rect (start -3.2 -3.0) (end 3.2 3.0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    '',
    '\t; Pin 1 Chamfer mark',
    '\t(fp_line (start -2.5 -1.2) (end -1.2 -2.5) (stroke (width 0.15) (type solid)) (layer "F.SilkS"))',
    '\t(fp_circle (center -1.8 -1.8) (end -1.4 -1.8) (stroke (width 0.15) (type solid)) (fill solid) (layer "F.SilkS"))',
    '\t(fp_circle (center 0 0) (end 1.8 0) (stroke (width 0.12) (type solid)) (fill none) (layer "F.SilkS"))',
    '',
    '\t; Pads: Pin 1 = Top-Left (VDD), Pin 2 = Bottom-Left (DOUT), Pin 3 = Bottom-Right (GND), Pin 4 = Top-Right (DIN)',
    '\t(pad "1" smd roundrect (at -2.4 -1.65) (size 1.7 1.0) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    '\t(pad "2" smd roundrect (at -2.4 1.65) (size 1.7 1.0) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    '\t(pad "3" smd roundrect (at 2.4 1.65) (size 1.7 1.0) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    '\t(pad "4" smd roundrect (at 2.4 -1.65) (size 1.7 1.0) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    '',
    '\t(fp_text user "VDD" (at -1.0 -1.65 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))',
    '\t(fp_text user "DOUT" (at -1.0 1.65 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))',
    '\t(fp_text user "GND" (at 1.0 1.65 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))',
    '\t(fp_text user "DIN" (at 1.0 -1.65 0) (layer "F.SilkS") (effects (font (size 0.5 0.5) (thickness 0.08))))',
    ')'
]

with open(FP_DIR / "WS2812B_5050.kicad_mod", "w") as f:
    f.write("\n".join(ws2812_lines) + "\n")
print("Generated WS2812B_5050.kicad_mod")

# -----------------------------------------------------------------------------
# 3. C_0805_2012Metric Footprint (Bypass capacitor)
# -----------------------------------------------------------------------------
c0805_lines = [
    '(footprint "C_0805_2012Metric"',
    '\t(version 20240108)',
    '\t(generator "antigravity-kicad-generator")',
    '\t(layer "F.Cu")',
    '\t(descr "Capacitor SMD 0805 (2012 Metric), 2.0x1.25mm")',
    '\t(tags "C 0805 2012 capacitor")',
    '\t(property "Reference" "C**"',
    '\t\t(at 0 -1.6 0)',
    '\t\t(layer "F.SilkS")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(property "Value" "C_0805"',
    '\t\t(at 0 1.6 0)',
    '\t\t(layer "F.Fab")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(attr smd)',
    '\t(fp_rect (start -1.0 -0.625) (end 1.0 0.625) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))',
    '\t(fp_line (start -0.2 -0.7) (end 0.2 -0.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
    '\t(fp_line (start -0.2 0.7) (end 0.2 0.7) (stroke (width 0.12) (type solid)) (layer "F.SilkS"))',
    '\t(fp_rect (start -1.7 -0.95) (end 1.7 0.95) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    '\t(pad "1" smd roundrect (at -0.95 0) (size 1.0 1.3) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    '\t(pad "2" smd roundrect (at 0.95 0) (size 1.0 1.3) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0.2))',
    ')'
]

with open(FP_DIR / "C_0805_2012Metric.kicad_mod", "w") as f:
    f.write("\n".join(c0805_lines) + "\n")
print("Generated C_0805_2012Metric.kicad_mod")

print("All Action Block footprints generated successfully!")
