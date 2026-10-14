import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
P11_DIR = ROOT / 'hardware' / 'prototype_1_1' / 'master_block'

def update_footprint_mod():
    mod_path = P11_DIR / 'robosen_master.pretty' / 'ESP32-S3-DevKitC-1-Socket.kicad_mod'
    content = mod_path.read_text(encoding='utf-8')

    content = content.replace('22.86mm (0.9 in) row spacing', '25.40mm (1.0 in) row spacing')
    content = re.sub(r'\(start -13\.5 -29\.0\)\s*\(end 13\.5 29\.0\)', '(start -14.2 -29.0)\n\t\t(end 14.2 29.0)', content)
    content = re.sub(r'\(start -14\.0 -29\.5\)\s*\(end 14\.0 29\.5\)', '(start -14.7 -29.5)\n\t\t(end 14.7 29.5)', content)

    content = re.sub(r'\(fp_text user "1" \(at -14\.0 -26\.67', '(fp_text user "1" (at -15.2 -26.67', content)
    content = re.sub(r'\(fp_text user "22" \(at -14\.0 26\.67', '(fp_text user "22" (at -15.2 26.67', content)
    content = re.sub(r'\(fp_text user "23" \(at 14\.0 -26\.67', '(fp_text user "23" (at 15.2 -26.67', content)
    content = re.sub(r'\(fp_text user "44" \(at 14\.0 26\.67', '(fp_text user "44" (at 15.2 26.67', content)

    # Pad substitutions
    content = re.sub(r'\(pad "([1-9]|1[0-9]|2[0-2])" thru_hole (rect|circle) \(at -11\.43 ', r'(pad "\1" thru_hole \2 (at -12.70 ', content)
    content = re.sub(r'\(pad "(2[3-9]|3[0-9]|4[0-4])" thru_hole (rect|circle) \(at 11\.43 ', r'(pad "\1" thru_hole \2 (at 12.70 ', content)

    mod_path.write_text(content, encoding='utf-8')
    print("Updated ESP32-S3-DevKitC-1-Socket.kicad_mod successfully.")

def parse_sexpr_top_level(text):
    start_idx = text.find('(kicad_pcb')
    header_end = text.find('\n', start_idx) + 1
    header = text[:header_end]
    
    i = header_end
    n = len(text)
    
    elements = []
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n or text[i] == ')':
            break
        if text[i] == '(':
            elem_start = i
            depth = 1
            i += 1
            in_string = False
            escape = False
            while i < n and depth > 0:
                c = text[i]
                if escape:
                    escape = False
                elif c == '\\':
                    escape = True
                elif c == '"':
                    in_string = not in_string
                elif not in_string:
                    if c == '(':
                        depth += 1
                    elif c == ')':
                        depth -= 1
                i += 1
            elements.append(text[elem_start:i])
        else:
            i += 1
    return header, elements

def prepare_unrouted_pcb():
    pcb_path = P11_DIR / 'robosen_master_block.kicad_pcb'
    text = pcb_path.read_text(encoding='utf-8')
    header, elements = parse_sexpr_top_level(text)

    kept = []
    for elem in elements:
        tag = elem.split()[0].lstrip('(')
        if tag in ('segment', 'via'):
            continue
        if tag == 'zone':
            if 'GND' in elem:
                continue
        if tag == 'footprint' and 'robosen_master:ESP32-S3-DevKitC-1-Socket' in elem:
            # Update U1 embedded footprint
            elem = re.sub(r'\(at -11\.43\b', '(at -12.7', elem)
            elem = re.sub(r'\(at 11\.43\b', '(at 12.7', elem)
            elem = re.sub(r'\(start -13\.5 29\)\s*\(end 13\.5 -29\)', '(start -14.2 29)\n\t\t\t(end 14.2 -29)', elem)
            elem = re.sub(r'\(start -14 29\.5\)\s*\(end 14 -29\.5\)', '(start -14.7 29.5)\n\t\t\t(end 14.7 -29.5)', elem)
            elem = re.sub(r'\(at -14 (26\.67|-26\.67) 90\)', r'(at -15.2 \1 90)', elem)
            elem = re.sub(r'\(at 14 (26\.67|-26\.67) 90\)', r'(at 15.2 \1 90)', elem)
            elem = elem.replace('22.86mm (0.9 in) row spacing', '25.40mm (1.0 in) row spacing')
        kept.append(elem)

    unrouted_text = header + '\n'.join('\t' + k for k in kept) + '\n)\n'
    pcb_path.write_text(unrouted_text, encoding='utf-8')
    print(f"Prepared unrouted PCB for Prototype #1-1 at {pcb_path}")

if __name__ == '__main__':
    update_footprint_mod()
    prepare_unrouted_pcb()
