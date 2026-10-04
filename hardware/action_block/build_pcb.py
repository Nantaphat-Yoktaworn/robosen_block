#!/usr/bin/env python3
"""
Automated KiCad 10 PCB Generator for Robosen Tangible Action Block (Unrouted Initial Placement)
- Loads footprints from action_block.pretty/
- Assigns nets from schematic / action_block.net
- Places initial components (J1, J2, U1, D1, C1, TP1)
- Adds board outline on Edge.Cuts
- Zero tracks / zero wiring (ratsnest enabled for user adjustment)
"""

import uuid
import re
import subprocess
from pathlib import Path

def uid():
    return str(uuid.uuid4())

def build_pcb():
    proj_dir = Path(__file__).resolve().parent
    fp_dir = proj_dir / "action_block.pretty"
    pcb_path = proj_dir / "action_block.kicad_pcb"

    # Net mappings from action_block.net
    comp_nets = {
        "IN": {
            "1": "+3V3",
            "2": "GND",
            "3": "/RX_IN",
            "4": "/RETURN_BUS"
        },
        "OUT": {
            "1": "+3V3",
            "2": "GND",
            "3": "/TX_OUT",
            "4": "/RETURN_BUS"
        },
        "MCU": {
            "1": "unconnected-(MCU-PC4-Pad1)",
            "2": "unconnected-(MCU-PC3-Pad2)",
            "3": "unconnected-(MCU-PC2-Pad3)",
            "4": "unconnected-(MCU-PC1-Pad4)",
            "5": "unconnected-(MCU-PC0-Pad5)",
            "6": "/LED_DIN",
            "7": "unconnected-(MCU-PA1-Pad7)",
            "8": "/RX_IN",
            "9": "/TX_OUT",
            "10": "+3V3",
            "11": "GND",
            "12": "unconnected-(MCU-PC5-Pad12)",
            "13": "unconnected-(MCU-PC6-Pad13)",
            "14": "unconnected-(MCU-PC7-Pad14)",
            "15": "unconnected-(MCU-PD0-Pad15)",
            "16": "/SWIO",
            "17": "unconnected-(MCU-PD2-Pad17)",
            "18": "unconnected-(MCU-PD3-Pad18)",
            "19": "unconnected-(MCU-PD4-Pad19)",
            "20": "unconnected-(MCU-PD7-Pad20)",
            "21": "+3V3",
            "22": "GND"
        },
        "RGB": {
            "1": "GND",
            "2": "+3V3",
            "3": "/LED_DIN"
        },
        "C104": {
            "1": "GND",
            "2": "+3V3"
        },
        "PROG": {
            "1": "GND",
            "2": "+3V3",
            "3": "/SWIO"
        }
    }

    # Placements (X, Y, Rot)
    # Board outline: (0, 0) to (48.0, 36.0) mm
    placements = {
        "IN": ("Pogo_4Pin_Dock_2.54mm", "UPSTREAM_IN", 4.0, 14.19, 0),
        "OUT": ("Pogo_4Pin_Dock_2.54mm", "DOWNSTREAM_OUT", 44.0, 14.19, 0),
        "MCU": ("TENSTAR_CH32V003F4P6", "CH32V003F4P6", 24.0, 18.0, 0),
        "RGB": ("WS2812B_Module_1x03_P2.54mm", "WS2812_RGB", 24.0, 4.0, 0),
        "C104": ("C_Disc_P2.54mm", "100nF (104)", 38.0, 4.0, 0),
        "PROG": ("Prog_Header_1x03_P2.54mm", "SWIO_DEBUG", 38.0, 32.0, 0)
    }

    def process_footprint(ref, fp_name, val, x, y, rot):
        fp_file = fp_dir / f"{fp_name}.kicad_mod"
        with open(fp_file, "r", encoding="utf-8") as f:
            content = f.read().strip()

        # Extract body between first newline and last closing parenthesis
        idx = content.find("\n")
        ridx = content.rfind(")")
        body = content[idx:ridx].strip()

        nets = comp_nets.get(ref, {})
        fp_body_lines = []

        for line in body.splitlines():
            sline = line.strip()
            if not sline:
                continue
            if sline.startswith("(version ") or sline.startswith("(generator ") or sline.startswith('(layer "F.Cu")'):
                continue

            # Reference property
            if sline.startswith('(property "Reference"'):
                line = re.sub(r'\(property "Reference" "[^"]*"', f'(property "Reference" "{ref}"', line)
            elif sline.startswith('(property "Value"'):
                line = re.sub(r'\(property "Value" "[^"]*"', f'(property "Value" "{val}"', line)
            elif sline.startswith("(pad "):
                m = re.match(r'^\s*\(pad\s+"([^"]+)"\s+(.*)\)\s*$', line)
                if m:
                    pnum = m.group(1)
                    prest = m.group(2)
                    net_name = nets.get(pnum, "")
                    net_clause = f' (net "{net_name}")' if net_name else ''
                    line = f'\t\t(pad "{pnum}" {prest}{net_clause} (uuid "{uid()}"))'

            fp_body_lines.append(line)

        fp_s_expr = f"""\t(footprint "robosen_action:{fp_name}"
\t\t(layer "F.Cu")
\t\t(uuid "{uid()}")
\t\t(at {x:.2f} {y:.2f} {rot})
""" + "\n".join(fp_body_lines) + "\n\t)"
        return fp_s_expr

    # Assemble PCB file
    pcb_lines = [
        '(kicad_pcb',
        '\t(version 20260206)',
        '\t(generator "pcbnew")',
        '\t(generator_version "10.0")',
        '\t(general',
        '\t\t(thickness 1.6)',
        '\t\t(legacy_teardrops no)',
        '\t)',
        '\t(paper "A4")',
        '\t(layers',
        '\t\t(0 "F.Cu" signal)',
        '\t\t(2 "B.Cu" signal)',
        '\t\t(9 "F.Adhes" user "F.Adhesive")',
        '\t\t(11 "B.Adhes" user "B.Adhesive")',
        '\t\t(13 "F.Paste" user)',
        '\t\t(15 "B.Paste" user)',
        '\t\t(5 "F.SilkS" user "F.Silkscreen")',
        '\t\t(7 "B.SilkS" user "B.Silkscreen")',
        '\t\t(1 "F.Mask" user)',
        '\t\t(3 "B.Mask" user)',
        '\t\t(17 "Dwgs.User" user "User.Drawings")',
        '\t\t(19 "Cmts.User" user "User.Comments")',
        '\t\t(21 "Eco1.User" user "User.Eco1")',
        '\t\t(23 "Eco2.User" user "User.Eco2")',
        '\t\t(25 "Edge.Cuts" user)',
        '\t\t(27 "Margin" user)',
        '\t\t(31 "F.CrtYd" user "F.Courtyard")',
        '\t\t(29 "B.CrtYd" user "B.Courtyard")',
        '\t\t(35 "F.Fab" user)',
        '\t\t(33 "B.Fab" user)',
        '\t)',
        '\t(setup',
        '\t\t(pad_to_mask_clearance 0)',
        '\t\t(allow_soldermask_bridges_in_footprints no)',
        '\t)',
        f'\t(gr_rect (start 0 0) (end 48 36) (stroke (width 0.1) (type default)) (fill no) (layer "Edge.Cuts") (uuid "{uid()}"))'
    ]

    # Add placed footprints
    for ref, (fp_name, val, x, y, rot) in placements.items():
        pcb_lines.append(process_footprint(ref, fp_name, val, x, y, rot))

    pcb_lines.append(')')

    final_text = "\n".join(pcb_lines)

    with open(pcb_path, "w", encoding="utf-8") as f:
        f.write(final_text + "\n")

    print(f"Generated unrouted PCB: {pcb_path.name}")

    # Validate with KiCad CLI export
    preview_dir = proj_dir / "pcb_preview"
    preview_dir.mkdir(exist_ok=True)
    res_svg = subprocess.run([
        "kicad-cli", "pcb", "export", "svg",
        "--fit-page-to-board",
        "--page-size-mode", "2",
        "-l", "Edge.Cuts,F.SilkS,F.Cu",
        "-o", str(preview_dir / "action_block_placement.svg"),
        str(pcb_path)
    ], capture_output=True, text=True)

    if res_svg.returncode == 0:
        print(f"Generated placement SVG preview: {preview_dir / 'action_block_placement.svg'}")
    else:
        print("SVG export notice:", res_svg.stderr)

    # Export PDF preview
    res_pdf = subprocess.run([
        "kicad-cli", "pcb", "export", "pdf",
        "--mode-single",
        "-l", "Edge.Cuts,F.SilkS,F.Cu",
        "-o", str(preview_dir / "action_block_placement.pdf"),
        str(pcb_path)
    ], capture_output=True, text=True)

    if res_pdf.returncode == 0:
        print(f"Generated placement PDF preview: {preview_dir / 'action_block_placement.pdf'}")
    else:
        print("PDF export notice:", res_pdf.stderr)

    # 3D Render PNG
    res_3d = subprocess.run([
        "kicad-cli", "pcb", "render",
        "--side", "top",
        "-o", str(preview_dir / "action_block_top.png"),
        str(pcb_path)
    ], capture_output=True, text=True)

    if res_3d.returncode == 0:
        print(f"Generated placement 3D preview: {preview_dir / 'action_block_top.png'}")
    else:
        print("3D render notice:", res_3d.stderr)

if __name__ == "__main__":
    build_pcb()
