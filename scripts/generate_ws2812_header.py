#!/usr/bin/env python3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FP_DIR = ROOT / "hardware" / "action_block" / "action_block.pretty"
SVG_DIR = ROOT / "hardware" / "action_block" / "footprint_svg"

lines = [
    '(footprint "WS2812B_Module_1x04_P2.54mm"',
    '\t(version 20240108)',
    '\t(generator "antigravity-kicad-generator")',
    '\t(layer "F.Cu")',
    '\t(descr "Pre-soldered WS2812 RGB LED Module, 1x04 Pin Header, 2.54mm pitch (OUT, IN, GND, VCC)")',
    '\t(tags "WS2812 NeoPixel RGB Module 1x04 2.54mm Header THT")',
    '\t(property "Reference" "D**"',
    '\t\t(at 0 -3.5 0)',
    '\t\t(layer "F.SilkS")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(property "Value" "WS2812_Module"',
    '\t\t(at 0 3.5 0)',
    '\t\t(layer "F.Fab")',
    '\t\t(effects (font (size 1 1) (thickness 0.15)))',
    '\t)',
    '\t(attr through_hole)',
    '\t(fp_rect (start -5.0 -1.5) (end 5.0 1.5) (stroke (width 0.15) (type solid)) (fill none) (layer "F.SilkS"))',
    '\t(fp_rect (start -5.0 -1.5) (end 5.0 1.5) (stroke (width 0.10) (type solid)) (fill none) (layer "F.Fab"))',
    '\t(fp_rect (start -5.5 -2.0) (end 5.5 2.0) (stroke (width 0.05) (type solid)) (fill none) (layer "F.CrtYd"))',
    '\t(pad "1" thru_hole rect (at -3.81 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))',
    '\t(fp_text user "OUT" (at -3.81 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    '\t(pad "2" thru_hole circle (at -1.27 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))',
    '\t(fp_text user "IN" (at -1.27 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    '\t(pad "3" thru_hole circle (at 1.27 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))',
    '\t(fp_text user "GND" (at 1.27 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    '\t(pad "4" thru_hole circle (at 3.81 0) (size 1.8 1.8) (drill 1.0) (layers "*.Cu" "*.Mask"))',
    '\t(fp_text user "VCC" (at 3.81 -2.0 0) (layer "F.SilkS") (effects (font (size 0.7 0.7) (thickness 0.1))))',
    ')'
]

fp_path = FP_DIR / "WS2812B_Module_1x04_P2.54mm.kicad_mod"
with open(fp_path, "w") as f:
    f.write("\n".join(lines) + "\n")
print(f"Generated {fp_path.name}")

# Export SVG
res = subprocess.run([
    "kicad-cli", "fp", "export", "svg",
    "-o", str(SVG_DIR),
    "--fp", "WS2812B_Module_1x04_P2.54mm",
    str(FP_DIR)
], capture_output=True, text=True)
print(res.stdout)
if res.returncode != 0:
    print("Stderr:", res.stderr)
else:
    print("SVG exported successfully!")
