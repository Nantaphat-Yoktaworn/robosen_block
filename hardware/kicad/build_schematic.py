import uuid
from pathlib import Path

def uid():
    return str(uuid.uuid4())

def generate():
    kicad_dir = Path(r"C:\Users\nnnn\Projects\robosen_block\hardware\kicad")
    sch_path = kicad_dir / "robosen_master_block.kicad_sch"
    sym_path = kicad_dir / "robosen_master.kicad_sym"
    
    root_uuid = uid()
    proj = "robosen_master_block"

    # =========================================================================
    # 1. EXACT SYSTEM POWER SYMBOLS
    # =========================================================================
    plus3v3_body = """\t(symbol "+3V3"
\t\t(power global)
\t\t(pin_numbers
\t\t\t(hide yes)
\t\t)
\t\t(pin_names
\t\t\t(offset 0)
\t\t\t(hide yes)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "#PWR"
\t\t\t(at 0 -3.81 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "+3V3"
\t\t\t(at 0 3.556 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "Power symbol creates a global label with name \\"+3V3\\""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "ki_keywords" "global power"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "+3V3_0_1"
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy -0.762 1.27) (xy 0 2.54)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 2.54) (xy 0.762 1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 2.54)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "+3V3_1_1"
\t\t\t(pin power_in line
\t\t\t\t(at 0 0 90)
\t\t\t\t(length 0)
\t\t\t\t(name ""
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)"""

    gnd_body = """\t(symbol "GND"
\t\t(power global)
\t\t(pin_numbers
\t\t\t(hide yes)
\t\t)
\t\t(pin_names
\t\t\t(offset 0)
\t\t\t(hide yes)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "#PWR"
\t\t\t(at 0 -6.35 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "GND"
\t\t\t(at 0 -3.81 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "Power symbol creates a global label with name \\"GND\\" , ground"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "ki_keywords" "global power"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "GND_0_1"
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 -1.27) (xy 1.27 -1.27) (xy 0 -2.54) (xy -1.27 -1.27) (xy 0 -1.27)
\t\t\t\t)
\t\t\t(stroke
\t\t\t\t(width 0)
\t\t\t\t(type default)
\t\t\t)
\t\t\t(fill
\t\t\t\t(type none)
\t\t\t)
\t\t)
\t\t)
\t\t(symbol "GND_1_1"
\t\t\t(pin power_in line
\t\t\t\t(at 0 0 270)
\t\t\t\t(length 0)
\t\t\t\t(name ""
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)"""

    pwr_flag_body = """\t(symbol "PWR_FLAG"
\t\t(power global)
\t\t(pin_numbers
\t\t\t(hide yes)
\t\t)
\t\t(pin_names
\t\t\t(offset 0)
\t\t\t(hide yes)
\t\t)
\t\t(exclude_from_sim no)
\t\t(in_bom yes)
\t\t(on_board yes)
\t\t(in_pos_files yes)
\t\t(duplicate_pin_numbers_are_jumpers no)
\t\t(property "Reference" "#FLG"
\t\t\t(at 0 1.905 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Value" "PWR_FLAG"
\t\t\t(at 0 3.81 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Footprint" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Datasheet" ""
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "Description" "Special symbol for telling ERC where power comes from"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(property "ki_keywords" "flag power"
\t\t\t(at 0 0 0)
\t\t\t(show_name no)
\t\t\t(do_not_autoplace no)
\t\t\t(hide yes)
\t\t\t(effects
\t\t\t\t(font
\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PWR_FLAG_0_0"
\t\t\t(pin power_out line
\t\t\t\t(at 0 0 90)
\t\t\t\t(length 0)
\t\t\t\t(name ""
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t\t(number "1"
\t\t\t\t\t(effects
\t\t\t\t\t\t(font
\t\t\t\t\t\t\t(size 1.27 1.27)
\t\t\t\t\t\t)
\t\t\t\t\t)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(symbol "PWR_FLAG_0_1"
\t\t\t(polyline
\t\t\t\t(pts
\t\t\t\t\t(xy 0 0) (xy 0 1.27) (xy -1.016 1.905) (xy 0 2.54) (xy 1.016 1.905) (xy 0 1.27)
\t\t\t\t)
\t\t\t\t(stroke
\t\t\t\t\t(width 0)
\t\t\t\t\t(type default)
\t\t\t\t)
\t\t\t\t(fill
\t\t\t\t\t(type none)
\t\t\t\t)
\t\t\t)
\t\t)
\t\t(embedded_fonts no)
\t)"""

    # =========================================================================
    # 2. BUILD CUSTOM SYMBOLS (Used for both .kicad_sym and lib_symbols)
    # =========================================================================
    symbols_def = {}

    # --- ESP32-S3-DevKitC-1 ---
    esp_lines = []
    esp_lines.append('\t\t(pin_names (offset 1.016))')
    esp_lines.append('\t\t(in_bom yes) (on_board yes)')
    esp_lines.append('\t\t(property "Reference" "U" (at 0 -38.1 0) (effects (font (size 1.27 1.27))))')
    esp_lines.append('\t\t(property "Value" "ESP32-S3-DevKitC-1" (at 0 38.1 0) (effects (font (size 1.27 1.27))))')
    esp_lines.append('\t\t(property "Footprint" "robosen_master:ESP32-S3-DevKitC-1-Socket" (at 0 40.64 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    esp_lines.append('\t\t(property "Datasheet" "https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/hw-reference/esp32s3/user-guide-devkitc-1.html" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    esp_lines.append('\t\t(property "Description" "ESP32-S3 Dual-Core WiFi/BLE 44-Pin Development Board Socket" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    esp_lines.append('\t\t(symbol "ESP32-S3-DevKitC-1_0_1"')
    esp_lines.append('\t\t\t(rectangle (start -22.86 -35.56) (end 22.86 35.56) (stroke (width 0.254) (type solid)) (fill (type background)))')
    esp_lines.append('\t\t)')
    esp_lines.append('\t\t(symbol "ESP32-S3-DevKitC-1_1_1"')
    left_pins = [
        (1, "3V3", "power_in"), (2, "3V3", "power_in"), (3, "EN/RST", "input"),
        (4, "GPIO4", "bidirectional"), (5, "GPIO5", "bidirectional"), (6, "GPIO6", "bidirectional"),
        (7, "GPIO7", "bidirectional"), (8, "GPIO15", "bidirectional"), (9, "GPIO16", "bidirectional"),
        (10, "GPIO17", "bidirectional"), (11, "GPIO18", "bidirectional"), (12, "GPIO8", "bidirectional"),
        (13, "GPIO3", "bidirectional"), (14, "GPIO46", "bidirectional"), (15, "GPIO9", "bidirectional"),
        (16, "GPIO10", "bidirectional"), (17, "GPIO11", "bidirectional"), (18, "GPIO12", "bidirectional"),
        (19, "GPIO13", "bidirectional"), (20, "GPIO14", "bidirectional"), (21, "5V", "power_in"),
        (22, "GND", "power_in")
    ]
    for idx, (pnum, pname, ptype) in enumerate(left_pins):
        y = 31.75 - (idx * 2.54)
        esp_lines.append(f'\t\t\t(pin {ptype} line (at -27.94 {y:.2f} 0) (length 5.08) (name "{pname}" (effects (font (size 1.0 1.0)))) (number "{pnum}" (effects (font (size 0.8 0.8)))))')

    right_pins = [
        (23, "GND", "power_in"), (24, "TX/IO43", "bidirectional"), (25, "RX/IO44", "bidirectional"),
        (26, "GPIO1", "bidirectional"), (27, "GPIO2", "bidirectional"), (28, "GPIO42", "bidirectional"),
        (29, "GPIO41", "bidirectional"), (30, "GPIO40", "bidirectional"), (31, "GPIO39", "bidirectional"),
        (32, "GPIO38", "bidirectional"), (33, "GPIO37", "bidirectional"), (34, "GPIO36", "bidirectional"),
        (35, "GPIO35", "bidirectional"), (36, "GPIO0", "bidirectional"), (37, "GPIO45", "bidirectional"),
        (38, "GPIO48", "bidirectional"), (39, "GPIO47", "bidirectional"), (40, "GPIO21", "bidirectional"),
        (41, "GPIO20", "bidirectional"), (42, "GPIO19", "bidirectional"), (43, "GND", "power_in"),
        (44, "GND", "power_in")
    ]
    for idx, (pnum, pname, ptype) in enumerate(right_pins):
        y = 31.75 - (idx * 2.54)
        esp_lines.append(f'\t\t\t(pin {ptype} line (at 27.94 {y:.2f} 180) (length 5.08) (name "{pname}" (effects (font (size 1.0 1.0)))) (number "{pnum}" (effects (font (size 0.8 0.8)))))')
    esp_lines.append('\t\t)')
    symbols_def["ESP32-S3-DevKitC-1"] = esp_lines

    # --- KY-040 ---
    ky_lines = [
        '\t\t(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "SW" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "KY-040" (at 0 12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:KY-040_Rotary_Encoder_Module" (at 0 15.24 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "KY-040 Incremental Rotary Encoder Module with Pushbutton" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "KY-040_0_1"',
        '\t\t\t(rectangle (start -10.16 -10.16) (end 10.16 10.16) (stroke (width 0.254) (type solid)) (fill (type background)))',
        '\t\t)',
        '\t\t(symbol "KY-040_1_1"',
        '\t\t\t(pin output line (at -15.24 5.08 0) (length 5.08) (name "CLK" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin output line (at -15.24 2.54 0) (length 5.08) (name "DT" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at -15.24 0 0) (length 5.08) (name "SW" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -15.24 -2.54 0) (length 5.08) (name "+" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -15.24 -5.08 0) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["KY-040"] = ky_lines

    # --- Pogo_4Pin ---
    pogo_lines = [
        '\t\t(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "J" (at 0 -10.16 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "Pogo_4Pin" (at 0 10.16 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:Pogo_4Pin_Dock_2.54mm" (at 0 12.7 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "4-Pin Pogo Connector / Dock Socket (2.54mm pitch)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "Pogo_4Pin_0_1"',
        '\t\t\t(rectangle (start -10.16 -7.62) (end 10.16 7.62) (stroke (width 0.254) (type solid)) (fill (type background)))',
        '\t\t)',
        '\t\t(symbol "Pogo_4Pin_1_1"',
        '\t\t\t(pin passive line (at -15.24 3.81 0) (length 5.08) (name "V+" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at -15.24 1.27 0) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin bidirectional line (at -15.24 -1.27 0) (length 5.08) (name "DATA" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin bidirectional line (at -15.24 -3.81 0) (length 5.08) (name "PASS" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["Pogo_4Pin"] = pogo_lines

    # --- EPaper_8Pin ---
    epd_lines = [
        '\t\t(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "DISP" (at 0 -15.24 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "EPaper_2.13in" (at 0 15.24 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:EPaper_2.13in_Header_1x08" (at 0 17.78 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "DEPG0213BN / SSD1680" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "2.13 inch E-Paper Display Module Header (SPI, SSD1680)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "EPaper_8Pin_0_1"',
        '\t\t\t(rectangle (start -12.7 -13.97) (end 12.7 13.97) (stroke (width 0.254) (type solid)) (fill (type background)))',
        '\t\t)',
        '\t\t(symbol "EPaper_8Pin_1_1"',
        '\t\t\t(pin output line (at -17.78 8.89 0) (length 5.08) (name "BUSY" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin input line (at -17.78 6.35 0) (length 5.08) (name "CS" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin input line (at -17.78 3.81 0) (length 5.08) (name "DC" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin input line (at -17.78 1.27 0) (length 5.08) (name "RES" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin input line (at -17.78 -1.27 0) (length 5.08) (name "SDA" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin input line (at -17.78 -3.81 0) (length 5.08) (name "SCL" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -17.78 -6.35 0) (length 5.08) (name "VCC" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -17.78 -8.89 0) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["EPaper_8Pin"] = epd_lines

    # --- TP4056_Module ---
    tp_lines = [
        '\t\t(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "TP4056_Type-C" (at 0 12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:TP4056_Type-C_Module" (at 0 15.24 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "TP4056 1A Li-Ion Battery Charger & DW01A Protection Module with Type-C" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "TP4056_Module_0_1"',
        '\t\t\t(rectangle (start -12.7 -10.16) (end 12.7 10.16) (stroke (width 0.254) (type solid)) (fill (type background)))',
        '\t\t)',
        '\t\t(symbol "TP4056_Module_1_1"',
        '\t\t\t(pin passive line (at -17.78 5.08 0) (length 5.08) (name "B+" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at -17.78 -5.08 0) (length 5.08) (name "B-" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at -17.78 2.54 0) (length 5.08) (name "IN+" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at -17.78 -2.54 0) (length 5.08) (name "IN-" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_out line (at 17.78 2.54 180) (length 5.08) (name "OUT+" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at 17.78 -2.54 180) (length 5.08) (name "OUT-" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["TP4056_Module"] = tp_lines

    # --- TPS63020_Module ---
    tps_lines = [
        '\t\t(pin_names (offset 1.016)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "U" (at 0 -12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "TPS63020_BuckBoost" (at 0 12.7 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:TPS63020_BuckBoost_Module" (at 0 15.24 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "Texas Instruments TPS63020" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "High Efficiency Single Inductor Buck-Boost Converter 3.3V Module (Horizontal)" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "TPS63020_Module_0_1"',
        '\t\t\t(rectangle (start -15.24 -10.16) (end 15.24 10.16) (stroke (width 0.254) (type solid)) (fill (type background)))',
        '\t\t)',
        '\t\t(symbol "TPS63020_Module_1_1"',
        '\t\t\t(pin power_in line (at -20.32 6.35 0) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -20.32 3.81 0) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -20.32 -3.81 0) (length 5.08) (name "VIN" (effects (font (size 1.0 1.0)))) (number "3" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at -20.32 -6.35 0) (length 5.08) (name "VIN" (effects (font (size 1.0 1.0)))) (number "4" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at 20.32 6.35 180) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "5" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_in line (at 20.32 3.81 180) (length 5.08) (name "GND" (effects (font (size 1.0 1.0)))) (number "6" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin power_out line (at 20.32 -3.81 180) (length 5.08) (name "OUT" (effects (font (size 1.0 1.0)))) (number "7" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at 20.32 -6.35 180) (length 5.08) (name "OUT" (effects (font (size 1.0 1.0)))) (number "8" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["TPS63020_Module"] = tps_lines

    # --- 18650_Cell ---
    cell_lines = [
        '\t\t(pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "BT" (at 0 -8.89 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "18650_Li-ion" (at 0 8.89 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:18650_Battery_Holder_Single" (at 0 11.43 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "Single-cell 18650 3.7V Lithium-Ion Battery Holder" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "18650_Cell_0_1"',
        '\t\t\t(polyline (pts (xy -2.54 2.54) (xy 2.54 2.54)) (stroke (width 0.508) (type solid)))',
        '\t\t\t(polyline (pts (xy -5.08 0) (xy 5.08 0)) (stroke (width 0.254) (type solid)))',
        '\t\t\t(polyline (pts (xy -2.54 -2.54) (xy 2.54 -2.54)) (stroke (width 0.508) (type solid)))',
        '\t\t\t(polyline (pts (xy -5.08 -5.08) (xy 5.08 -5.08)) (stroke (width 0.254) (type solid)))',
        '\t\t)',
        '\t\t(symbol "18650_Cell_1_1"',
        '\t\t\t(pin passive line (at 0 5.08 270) (length 2.54) (name "+" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at 0 -5.08 90) (length 2.54) (name "-" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["18650_Cell"] = cell_lines

    # --- SW_Push ---
    sw_lines = [
        '\t\t(pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "SW" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "SW_Push_12mm" (at 0 6.35 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:SW_PUSH_12x12mm" (at 0 8.89 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "12x12mm Push Button Switch Tactile Momentary" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "SW_Push_0_1"',
        '\t\t\t(circle (center -2.54 0) (radius 0.508) (stroke (width 0.254) (type solid)) (fill (type none)))',
        '\t\t\t(circle (center 2.54 0) (radius 0.508) (stroke (width 0.254) (type solid)) (fill (type none)))',
        '\t\t\t(polyline (pts (xy -3.81 2.54) (xy 3.81 2.54)) (stroke (width 0.254) (type solid)))',
        '\t\t\t(polyline (pts (xy 0 2.54) (xy 0 5.08)) (stroke (width 0.254) (type solid)))',
        '\t\t)',
        '\t\t(symbol "SW_Push_1_1"',
        '\t\t\t(pin passive line (at -5.08 0 0) (length 2.032) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at 5.08 0 180) (length 2.032) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["SW_Push"] = sw_lines

    # --- SW_SPST ---
    spst_lines = [
        '\t\t(pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "SW" (at 0 -6.35 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "SW_SPST" (at 0 6.35 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:SW_Power_2Wire_Pads" (at 0 8.89 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "Single-Pole Single-Throw 2-Wire Power Switch" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "SW_SPST_0_1"',
        '\t\t\t(circle (center -2.54 0) (radius 0.508) (stroke (width 0.254) (type solid)) (fill (type none)))',
        '\t\t\t(circle (center 2.54 0) (radius 0.508) (stroke (width 0.254) (type solid)) (fill (type none)))',
        '\t\t\t(polyline (pts (xy -2.0 0.5) (xy 2.0 2.0)) (stroke (width 0.254) (type solid)))',
        '\t\t)',
        '\t\t(symbol "SW_SPST_1_1"',
        '\t\t\t(pin passive line (at -5.08 0 0) (length 2.54) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at 5.08 0 180) (length 2.54) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["SW_SPST"] = spst_lines

    # --- R ---
    r_lines = [
        '\t\t(pin_names (offset 0) (hide yes)) (in_bom yes) (on_board yes)',
        '\t\t(property "Reference" "R" (at 0 -5.08 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Value" "R" (at 0 5.08 0) (effects (font (size 1.27 1.27))))',
        '\t\t(property "Footprint" "robosen_master:R_Axial_P10.16mm" (at 0 7.62 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(property "Description" "Resistor 0.25W Axial Through-Hole" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))',
        '\t\t(symbol "R_0_1"',
        '\t\t\t(rectangle (start -1.016 -3.0) (end 1.016 3.0) (stroke (width 0.254) (type solid)) (fill (type none)))',
        '\t\t)',
        '\t\t(symbol "R_1_1"',
        '\t\t\t(pin passive line (at 0 5.08 270) (length 2.08) (name "1" (effects (font (size 1.0 1.0)))) (number "1" (effects (font (size 0.8 0.8)))))',
        '\t\t\t(pin passive line (at 0 -5.08 90) (length 2.08) (name "2" (effects (font (size 1.0 1.0)))) (number "2" (effects (font (size 0.8 0.8)))))',
        '\t\t)'
    ]
    symbols_def["R"] = r_lines

    # =========================================================================
    # 3. WRITE .kicad_sym STANDALONE SYMBOL LIBRARY
    # =========================================================================
    sym_file_lines = []
    sym_file_lines.append('(kicad_symbol_lib')
    sym_file_lines.append('\t(version 20231120)')
    sym_file_lines.append('\t(generator "antigravity-kicad-generator")')
    sym_file_lines.append('\t(generator_version "10.0")')
    for name, s_lines in symbols_def.items():
        sym_file_lines.append(f'\t(symbol "{name}"')
        sym_file_lines.extend(s_lines)
        sym_file_lines.append('\t)')
    sym_file_lines.append(')')
    with open(sym_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(sym_file_lines) + '\n')
    print(f"Generated Symbol Library at {sym_path}")

    # =========================================================================
    # 4. BUILD .kicad_sch SCHEMATIC
    # =========================================================================
    sch = []
    sch.append('(kicad_sch')
    sch.append('\t(version 20250114)')
    sch.append('\t(generator "eeschema")')
    sch.append('\t(generator_version "10.0")')
    sch.append(f'\t(uuid "{root_uuid}")')
    sch.append('\t(paper "A3")')
    sch.append('\t(title_block')
    sch.append('\t\t(title "Robosen K1 Master Block Carrier Board")')
    sch.append('\t\t(date "2026-10-04")')
    sch.append('\t\t(rev "v1.0")')
    sch.append('\t\t(company "Robosen Tangible Coding Block Project")')
    sch.append('\t\t(comment 1 "Dual Rotary Knobs, 2.13 E-Paper Display, Config Dock & Run Chain Ports, Li-Ion BMS & 3.3V Buck-Boost")')
    sch.append('\t)')
    sch.append('\t(lib_symbols')
    
    # Embed custom symbols under robosen_master:<name>
    for name, s_lines in symbols_def.items():
        sch.append(f'\t\t(symbol "robosen_master:{name}"')
        sch.extend(s_lines)
        sch.append('\t\t)')

    # Add exact system power symbols with power: prefix
    # 1) +3V3
    p3v3 = plus3v3_body.replace('(symbol "+3V3"', '(symbol "power:+3V3"')
    sch.append('\t' + p3v3.strip())

    # 2) GND
    pgnd = gnd_body.replace('(symbol "GND"', '(symbol "power:GND"')
    sch.append('\t' + pgnd.strip())

    # 3) PWR_FLAG
    pflg = pwr_flag_body.replace('(symbol "PWR_FLAG"', '(symbol "power:PWR_FLAG"')
    sch.append('\t' + pflg.strip())

    sch.append('\t)') # end lib_symbols

    # Helpers
    def place_sym(lib_id, ref, val, footprint, x, y, pin_count, unit=1, dnp=False):
        s_id = uid()
        res = []
        res.append(f'\t(symbol (lib_id "{lib_id}") (at {x:.2f} {y:.2f} 0) (unit {unit})')
        res.append('\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)')
        res.append(f'\t\t(dnp {"yes" if dnp else "no"}) (uuid "{s_id}")')
        res.append(f'\t\t(property "Reference" "{ref}" (at {x:.2f} {y-11.43:.2f} 0) (effects (font (size 1.27 1.27))))')
        res.append(f'\t\t(property "Value" "{val}" (at {x:.2f} {y+11.43:.2f} 0) (effects (font (size 1.27 1.27))))')
        res.append(f'\t\t(property "Footprint" "{footprint}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(property "Description" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        for p in range(1, pin_count + 1):
            res.append(f'\t\t(pin "{p}" (uuid "{uid()}"))')
        res.append('\t\t(instances')
        res.append(f'\t\t\t(project "{proj}"')
        res.append(f'\t\t\t\t(path "/{root_uuid}"')
        res.append(f'\t\t\t\t\t(reference "{ref}")')
        res.append(f'\t\t\t\t\t(unit {unit})')
        res.append('\t\t\t\t)')
        res.append('\t\t\t)')
        res.append('\t\t)')
        res.append('\t)')
        return '\n'.join(res)

    def place_pwr(name, ref_pwr, x, y, rot=0):
        s_id = uid()
        res = []
        res.append(f'\t(symbol (lib_id "power:{name}") (at {x:.2f} {y:.2f} {rot}) (unit 1)')
        res.append('\t\t(exclude_from_sim no) (in_bom yes) (on_board yes)')
        res.append(f'\t\t(dnp no) (uuid "{s_id}")')
        res.append(f'\t\t(property "Reference" "{ref_pwr}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(property "Value" "{name}" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27))))')
        res.append(f'\t\t(property "Footprint" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(property "Datasheet" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(property "Description" "" (at {x:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        res.append(f'\t\t(pin "1" (uuid "{uid()}"))')
        res.append('\t\t(instances')
        res.append(f'\t\t\t(project "{proj}"')
        res.append(f'\t\t\t\t(path "/{root_uuid}"')
        res.append(f'\t\t\t\t\t(reference "{ref_pwr}")')
        res.append('\t\t\t\t\t(unit 1)')
        res.append('\t\t\t\t)')
        res.append('\t\t\t)')
        res.append('\t\t)')
        res.append('\t)')
        return '\n'.join(res)

    def wire(x1, y1, x2, y2):
        return f'\t(wire (pts (xy {x1:.2f} {y1:.2f}) (xy {x2:.2f} {y2:.2f})) (stroke (width 0) (type solid)) (uuid "{uid()}"))'

    def label(text, x, y, rot=0):
        return f'\t(label "{text}" (at {x:.2f} {y:.2f} {rot}) (effects (font (size 1.27 1.27))) (uuid "{uid()}"))'

    def no_conn(x, y):
        return f'\t(no_connect (at {x:.2f} {y:.2f}) (uuid "{uid()}"))'

    # =========================================================================
    # 5. PLACE COMPONENTS (All centered on exact 1.27mm / 2.54mm grid)
    # =========================================================================
    # Core MCU
    sch.append(place_sym("robosen_master:ESP32-S3-DevKitC-1", "U1", "ESP32-S3-DevKitC-1", "robosen_master:ESP32-S3-DevKitC-1-Socket", 190.50, 139.70, 44))
    
    # Left Zone: UI Elements
    sch.append(place_sym("robosen_master:KY-040", "SW1", "Knob 1 (Action)", "robosen_master:KY-040_Rotary_Encoder_Module", 63.50, 63.50, 5))
    sch.append(place_sym("robosen_master:KY-040", "SW2", "Knob 2 (Param)", "robosen_master:KY-040_Rotary_Encoder_Module", 63.50, 101.60, 5))
    sch.append(place_sym("robosen_master:SW_Push", "SW3", "START_BUTTON", "robosen_master:SW_PUSH_12x12mm", 63.50, 139.70, 2))
    sch.append(place_sym("robosen_master:EPaper_8Pin", "DISP1", "2.13in_EPaper_SSD1680", "robosen_master:EPaper_2.13in_Header_1x08", 63.50, 203.20, 8))

    # Right Zone: Pogo Ports & Pull-ups
    sch.append(place_sym("robosen_master:Pogo_4Pin", "J1", "CONFIG_DOCK_PORT", "robosen_master:Pogo_4Pin_Dock_2.54mm", 342.90, 63.50, 4))
    sch.append(place_sym("robosen_master:Pogo_4Pin", "J2", "RUN_CHAIN_PORT", "robosen_master:Pogo_4Pin_Dock_2.54mm", 342.90, 101.60, 4))
    sch.append(place_sym("robosen_master:R", "R1", "10k (Pull-up)", "robosen_master:R_Axial_P10.16mm", 317.50, 139.70, 2))
    sch.append(place_sym("robosen_master:R", "R2", "10k (Pull-up)", "robosen_master:R_Axial_P10.16mm", 342.90, 139.70, 2))

    # Power Zone
    sch.append(place_sym("robosen_master:18650_Cell", "BT1", "18650 3.7V 3500mAh", "robosen_master:18650_Battery_Holder_Single", 254.00, 215.90, 2))
    sch.append(place_sym("robosen_master:TP4056_Module", "U2", "TP4056_USB-C_BMS", "robosen_master:TP4056_Type-C_Module", 304.80, 215.90, 6))
    sch.append(place_sym("robosen_master:SW_SPST", "SW4", "POWER_SWITCH", "robosen_master:SW_Power_2Wire_Pads", 342.90, 213.36, 2))
    sch.append(place_sym("robosen_master:TPS63020_Module", "U3", "TPS63020_3.3V_BuckBoost", "robosen_master:TPS63020_BuckBoost_Module", 355.60, 254.00, 8))

    # =========================================================================
    # 6. NET CONNECTIONS, WIRES & LABELS
    # =========================================================================
    
    # --- U1 Left Pins (X = 162.56) ---
    # Pin 1 (3V3, Y = 107.95)
    sch.append(wire(162.56, 107.95, 152.40, 107.95))
    sch.append(place_pwr("+3V3", "#PWR01", 152.40, 107.95, 90))

    # Pin 2 (3V3, Y = 110.49)
    sch.append(wire(162.56, 110.49, 152.40, 110.49))
    sch.append(place_pwr("+3V3", "#PWR02", 152.40, 110.49, 90))

    # Pin 3 (EN/RST, Y = 113.03) -> No Connect
    sch.append(no_conn(162.56, 113.03))

    # Pin 4 (GPIO4, Y = 115.57) -> EPD_BUSY
    sch.append(wire(162.56, 115.57, 152.40, 115.57))
    sch.append(label("EPD_BUSY", 152.40, 115.57, 180))

    # Pin 5 (GPIO5, Y = 118.11) -> EPD_RES
    sch.append(wire(162.56, 118.11, 152.40, 118.11))
    sch.append(label("EPD_RES", 152.40, 118.11, 180))

    # Pin 6 (GPIO6, Y = 120.65) -> EPD_DC
    sch.append(wire(162.56, 120.65, 152.40, 120.65))
    sch.append(label("EPD_DC", 152.40, 120.65, 180))

    # Pin 7 (GPIO7, Y = 123.19) -> EPD_CS
    sch.append(wire(162.56, 123.19, 152.40, 123.19))
    sch.append(label("EPD_CS", 152.40, 123.19, 180))

    # Pin 8 (GPIO15, Y = 125.73) -> CHAIN_TX
    sch.append(wire(162.56, 125.73, 152.40, 125.73))
    sch.append(label("CHAIN_TX", 152.40, 125.73, 180))

    # Pin 9 (GPIO16, Y = 128.27) -> CHAIN_RX
    sch.append(wire(162.56, 128.27, 152.40, 128.27))
    sch.append(label("CHAIN_RX", 152.40, 128.27, 180))

    # Pin 10 (GPIO17, Y = 130.81) -> CFG_TX
    sch.append(wire(162.56, 130.81, 152.40, 130.81))
    sch.append(label("CFG_TX", 152.40, 130.81, 180))

    # Pin 11 (GPIO18, Y = 133.35) -> CFG_RX
    sch.append(wire(162.56, 133.35, 152.40, 133.35))
    sch.append(label("CFG_RX", 152.40, 133.35, 180))

    # Pin 12 (GPIO8, Y = 135.89) -> K1_CLK
    sch.append(wire(162.56, 135.89, 152.40, 135.89))
    sch.append(label("K1_CLK", 152.40, 135.89, 180))

    # Pin 13 (GPIO3, Y = 138.43) -> No Connect
    sch.append(no_conn(162.56, 138.43))

    # Pin 14 (GPIO46, Y = 140.97) -> No Connect
    sch.append(no_conn(162.56, 140.97))

    # Pin 15 (GPIO9, Y = 143.51) -> K1_DT
    sch.append(wire(162.56, 143.51, 152.40, 143.51))
    sch.append(label("K1_DT", 152.40, 143.51, 180))

    # Pin 16 (GPIO10, Y = 146.05) -> K1_SW
    sch.append(wire(162.56, 146.05, 152.40, 146.05))
    sch.append(label("K1_SW", 152.40, 146.05, 180))

    # Pin 17 (GPIO11, Y = 148.59) -> K2_CLK
    sch.append(wire(162.56, 148.59, 152.40, 148.59))
    sch.append(label("K2_CLK", 152.40, 148.59, 180))

    # Pin 18 (GPIO12, Y = 151.13) -> K2_DT
    sch.append(wire(162.56, 151.13, 152.40, 151.13))
    sch.append(label("K2_DT", 152.40, 151.13, 180))

    # Pin 19 (GPIO13, Y = 153.67) -> K2_SW
    sch.append(wire(162.56, 153.67, 152.40, 153.67))
    sch.append(label("K2_SW", 152.40, 153.67, 180))

    # Pin 20 (GPIO14, Y = 156.21) -> BTN_START
    sch.append(wire(162.56, 156.21, 152.40, 156.21))
    sch.append(label("BTN_START", 152.40, 156.21, 180))

    # Pin 21 (5V, Y = 158.75) -> No Connect
    sch.append(no_conn(162.56, 158.75))

    # Pin 22 (GND, Y = 161.29) -> GND
    sch.append(wire(162.56, 161.29, 152.40, 161.29))
    sch.append(place_pwr("GND", "#PWR03", 152.40, 161.29, 270))

    # --- U1 Right Pins (X = 218.44) ---
    # Pin 23 (GND, Y = 107.95) -> GND
    sch.append(wire(218.44, 107.95, 228.60, 107.95))
    sch.append(place_pwr("GND", "#PWR04", 228.60, 107.95, 270))

    # Pin 24 (TX/IO43, Y = 110.49) -> No Connect
    sch.append(no_conn(218.44, 110.49))
    # Pin 25 (RX/IO44, Y = 113.03) -> No Connect
    sch.append(no_conn(218.44, 113.03))
    # Pin 26 (GPIO1, Y = 115.57) -> No Connect (Future battery divider)
    sch.append(no_conn(218.44, 115.57))
    # Pin 27 (GPIO2, Y = 118.11) -> No Connect
    sch.append(no_conn(218.44, 118.11))
    # Pin 28 (GPIO42, Y = 120.65) -> No Connect
    sch.append(no_conn(218.44, 120.65))
    # Pin 29 (GPIO41, Y = 123.19) -> No Connect
    sch.append(no_conn(218.44, 123.19))
    # Pin 30 (GPIO40, Y = 125.73) -> No Connect
    sch.append(no_conn(218.44, 125.73))
    # Pin 31 (GPIO39, Y = 128.27) -> No Connect
    sch.append(no_conn(218.44, 128.27))

    # Pin 32 (GPIO38, Y = 130.81) -> EPD_MOSI
    sch.append(wire(218.44, 130.81, 228.60, 130.81))
    sch.append(label("EPD_MOSI", 228.60, 130.81, 0))

    # Pin 33 (GPIO37, Y = 133.35) -> No Connect
    sch.append(no_conn(218.44, 133.35))
    # Pin 34 (GPIO36, Y = 135.89) -> No Connect
    sch.append(no_conn(218.44, 135.89))
    # Pin 35 (GPIO35, Y = 138.43) -> No Connect
    sch.append(no_conn(218.44, 138.43))
    # Pin 36 (GPIO0, Y = 140.97) -> No Connect
    sch.append(no_conn(218.44, 140.97))
    # Pin 37 (GPIO45, Y = 143.51) -> No Connect
    sch.append(no_conn(218.44, 143.51))
    # Pin 38 (GPIO48, Y = 146.05) -> No Connect
    sch.append(no_conn(218.44, 146.05))
    # Pin 39 (GPIO47, Y = 148.59) -> No Connect
    sch.append(no_conn(218.44, 148.59))

    # Pin 40 (GPIO21, Y = 151.13) -> EPD_SCK
    sch.append(wire(218.44, 151.13, 228.60, 151.13))
    sch.append(label("EPD_SCK", 228.60, 151.13, 0))

    # Pin 41 (GPIO20, Y = 153.67) -> No Connect
    sch.append(no_conn(218.44, 153.67))
    # Pin 42 (GPIO19, Y = 156.21) -> No Connect
    sch.append(no_conn(218.44, 156.21))

    # Pin 43 (GND, Y = 158.75) -> GND
    sch.append(wire(218.44, 158.75, 228.60, 158.75))
    sch.append(place_pwr("GND", "#PWR05", 228.60, 158.75, 270))

    # Pin 44 (GND, Y = 161.29) -> GND
    sch.append(wire(218.44, 161.29, 228.60, 161.29))
    sch.append(place_pwr("GND", "#PWR06", 228.60, 161.29, 270))

    # --- SW1 (Knob 1, X = 48.26) ---
    sch.append(wire(48.26, 58.42, 38.10, 58.42))
    sch.append(label("K1_CLK", 38.10, 58.42, 180))
    sch.append(wire(48.26, 60.96, 38.10, 60.96))
    sch.append(label("K1_DT", 38.10, 60.96, 180))
    sch.append(wire(48.26, 63.50, 38.10, 63.50))
    sch.append(label("K1_SW", 38.10, 63.50, 180))
    sch.append(wire(48.26, 66.04, 38.10, 66.04))
    sch.append(place_pwr("+3V3", "#PWR07", 38.10, 66.04, 90))
    sch.append(wire(48.26, 68.58, 38.10, 68.58))
    sch.append(place_pwr("GND", "#PWR08", 38.10, 68.58, 270))

    # --- SW2 (Knob 2, X = 48.26) ---
    sch.append(wire(48.26, 96.52, 38.10, 96.52))
    sch.append(label("K2_CLK", 38.10, 96.52, 180))
    sch.append(wire(48.26, 99.06, 38.10, 99.06))
    sch.append(label("K2_DT", 38.10, 99.06, 180))
    sch.append(wire(48.26, 101.60, 38.10, 101.60))
    sch.append(label("K2_SW", 38.10, 101.60, 180))
    sch.append(wire(48.26, 104.14, 38.10, 104.14))
    sch.append(place_pwr("+3V3", "#PWR09", 38.10, 104.14, 90))
    sch.append(wire(48.26, 106.68, 38.10, 106.68))
    sch.append(place_pwr("GND", "#PWR10", 38.10, 106.68, 270))

    # --- SW3 (Start Button, Y = 139.70) ---
    sch.append(wire(58.42, 139.70, 48.26, 139.70))
    sch.append(label("BTN_START", 48.26, 139.70, 180))
    sch.append(wire(68.58, 139.70, 78.74, 139.70))
    sch.append(place_pwr("GND", "#PWR11", 78.74, 139.70, 270))

    # --- DISP1 (E-Paper Header, X = 45.72) ---
    # Pin 1: BUSY (Y = 194.31)
    sch.append(wire(45.72, 194.31, 35.56, 194.31))
    sch.append(label("EPD_BUSY", 35.56, 194.31, 180))

    # Pin 2: CS (Y = 196.85)
    sch.append(wire(45.72, 196.85, 35.56, 196.85))
    sch.append(label("EPD_CS", 35.56, 196.85, 180))

    # Pin 3: DC (Y = 199.39)
    sch.append(wire(45.72, 199.39, 35.56, 199.39))
    sch.append(label("EPD_DC", 35.56, 199.39, 180))

    # Pin 4: RES (Y = 201.93)
    sch.append(wire(45.72, 201.93, 35.56, 201.93))
    sch.append(label("EPD_RES", 35.56, 201.93, 180))

    # Pin 5: SDA / MOSI (Y = 204.47)
    sch.append(wire(45.72, 204.47, 35.56, 204.47))
    sch.append(label("EPD_MOSI", 35.56, 204.47, 180))

    # Pin 6: SCL / SCK (Y = 207.01)
    sch.append(wire(45.72, 207.01, 35.56, 207.01))
    sch.append(label("EPD_SCK", 35.56, 207.01, 180))

    # Pin 7: VCC / +3V3 (Y = 209.55)
    sch.append(wire(45.72, 209.55, 35.56, 209.55))
    sch.append(place_pwr("+3V3", "#PWR12", 35.56, 209.55, 90))

    # Pin 8: GND (Y = 212.09)
    sch.append(wire(45.72, 212.09, 35.56, 212.09))
    sch.append(place_pwr("GND", "#PWR13", 35.56, 212.09, 270))

    # --- J1 (Config Dock, X = 327.66) ---
    sch.append(wire(327.66, 59.69, 317.50, 59.69))
    sch.append(place_pwr("+3V3", "#PWR14", 317.50, 59.69, 90))
    sch.append(wire(327.66, 62.23, 317.50, 62.23))
    sch.append(place_pwr("GND", "#PWR15", 317.50, 62.23, 270))
    sch.append(wire(327.66, 64.77, 317.50, 64.77))
    sch.append(label("CFG_RX", 317.50, 64.77, 180))
    sch.append(wire(327.66, 67.31, 317.50, 67.31))
    sch.append(label("CFG_TX", 317.50, 67.31, 180))

    # --- J2 (Run Chain Port, X = 327.66) ---
    sch.append(wire(327.66, 97.79, 317.50, 97.79))
    sch.append(place_pwr("+3V3", "#PWR16", 317.50, 97.79, 90))
    sch.append(wire(327.66, 100.33, 317.50, 100.33))
    sch.append(place_pwr("GND", "#PWR17", 317.50, 100.33, 270))
    sch.append(wire(327.66, 102.87, 317.50, 102.87))
    sch.append(label("CHAIN_TX", 317.50, 102.87, 180))
    sch.append(wire(327.66, 105.41, 317.50, 105.41))
    sch.append(label("CHAIN_RX", 317.50, 105.41, 180))

    # --- R1 (Pull-up for CHAIN_TX, X = 317.50) ---
    sch.append(wire(317.50, 134.62, 317.50, 127.00))
    sch.append(place_pwr("+3V3", "#PWR18", 317.50, 127.00, 90))
    sch.append(wire(317.50, 144.78, 317.50, 152.40))
    sch.append(label("CHAIN_TX", 317.50, 152.40, 270))

    # --- R2 (Pull-up for CHAIN_RX, X = 342.90) ---
    sch.append(wire(342.90, 134.62, 342.90, 127.00))
    sch.append(place_pwr("+3V3", "#PWR19", 342.90, 127.00, 90))
    sch.append(wire(342.90, 144.78, 342.90, 152.40))
    sch.append(label("CHAIN_RX", 342.90, 152.40, 270))

    # --- Power Architecture: BT1 -> U2 -> SW4 -> U3 ---
    # BT1 (18650 Cell, X = 254.00)
    # Direct physical wire from BT1 Pin 1 (254.00, 210.82) to U2 Pin 2 B+ (287.02, 210.82)
    sch.append(wire(254.00, 210.82, 287.02, 210.82))
    sch.append(label("VBAT_RAW", 270.00, 210.82, 0))

    # Direct physical wire from BT1 Pin 2 (254.00, 220.98) to U2 Pin 3 B- (287.02, 220.98)
    sch.append(wire(254.00, 220.98, 287.02, 220.98))
    sch.append(label("VBAT_GND", 270.00, 220.98, 0))

    # U2 TP4056 External 5V Pads (X = 287.02) -> Unused
    sch.append(no_conn(287.02, 213.36)) # IN+ (Pin 6)
    sch.append(no_conn(287.02, 218.44)) # IN- (Pin 5)

    # Direct physical wire from U2 Pin 1 OUT+ (322.58, 213.36) to SW4 Pin 1 (337.82, 213.36)
    sch.append(wire(322.58, 213.36, 337.82, 213.36))
    sch.append(label("VBAT_PROT", 330.20, 213.36, 0))

    # U2 Pin 4 OUT- (322.58, 218.44) -> Tied to common GND
    sch.append(wire(322.58, 218.44, 330.20, 218.44))
    sch.append(place_pwr("GND", "#PWR20", 330.20, 218.44, 270))

    # SW4 Pin 2 Switched Power (347.98, 213.36) -> VBAT_SW
    sch.append(wire(347.98, 213.36, 355.60, 213.36))
    sch.append(label("VBAT_SW", 355.60, 213.36, 0))
    sch.append(place_pwr("PWR_FLAG", "#FLG02", 355.60, 213.36, 90))

    # U3 (TPS63020 Buck-Boost, X = 355.60, Y = 254.00)
    # Left Pins (IN side, X = 335.28):
    # Pin 1 & Pin 2: GND (Y = 247.65, 250.19)
    sch.append(wire(335.28, 247.65, 325.12, 247.65))
    sch.append(wire(335.28, 250.19, 325.12, 250.19))
    sch.append(wire(325.12, 247.65, 325.12, 250.19))
    sch.append(place_pwr("GND", "#PWR21", 325.12, 250.19, 270))

    # Pin 3 & Pin 4: VIN (Y = 257.81, 260.35)
    sch.append(wire(335.28, 257.81, 325.12, 257.81))
    sch.append(wire(335.28, 260.35, 325.12, 260.35))
    sch.append(wire(325.12, 257.81, 325.12, 260.35))
    sch.append(label("VBAT_SW", 325.12, 257.81, 180))

    # Right Pins (OUT side, X = 375.92):
    # Pin 5 & Pin 6: GND (Y = 247.65, 250.19)
    sch.append(wire(375.92, 247.65, 386.08, 247.65))
    sch.append(wire(375.92, 250.19, 386.08, 250.19))
    sch.append(wire(386.08, 247.65, 386.08, 250.19))
    sch.append(place_pwr("GND", "#PWR23", 386.08, 250.19, 270))
    sch.append(place_pwr("PWR_FLAG", "#FLG01", 386.08, 250.19, 270))

    # Pin 7 & Pin 8: OUT (Y = 257.81, 260.35)
    sch.append(wire(375.92, 257.81, 386.08, 257.81))
    sch.append(wire(375.92, 260.35, 386.08, 260.35))
    sch.append(wire(386.08, 257.81, 386.08, 260.35))
    sch.append(place_pwr("+3V3", "#PWR22", 386.08, 257.81, 90))

    # Sheet instances & footer
    sch.append('\t(sheet_instances')
    sch.append('\t\t(path "/"')
    sch.append('\t\t\t(page "1")')
    sch.append('\t\t)')
    sch.append('\t)')
    sch.append('\t(embedded_fonts no)')
    sch.append(')')

    with open(sch_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(sch) + '\n')
    print(f"Generated Schematic at {sch_path} ({len(sch)} lines)")

if __name__ == "__main__":
    generate()
