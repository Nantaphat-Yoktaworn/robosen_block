import os
import shutil
import subprocess
import tempfile

POSTER_HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<title>Robosen Tangible Coding Block System — 14-Week Engineering Poster</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body {
    width: 1152px;
    height: 2064px;
    overflow: hidden;
    background: #070C14;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    color: #E2E8F0;
    position: relative;
  }
  .circuit-bg {
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 50% 18%, rgba(56, 189, 248, 0.14), transparent 45%),
      radial-gradient(circle at 50% 62%, rgba(245, 158, 11, 0.10), transparent 55%),
      linear-gradient(rgba(30, 58, 138, 0.15) 1px, transparent 1px),
      linear-gradient(90deg, rgba(30, 58, 138, 0.15) 1px, transparent 1px);
    background-size: 100% 100%, 100% 100%, 48px 48px, 48px 48px;
  }
  .header {
    position: relative;
    z-index: 5;
    text-align: center;
    padding: 36px 40px 18px;
  }
  .eyebrow {
    font-size: 15px;
    font-weight: 800;
    letter-spacing: 3.5px;
    color: #38BDF8;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  h1 {
    font-size: 40px;
    font-weight: 900;
    letter-spacing: 1px;
    line-height: 1.15;
    background: linear-gradient(90deg, #67E8F9, #E0F2FE, #FCD34D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .sub {
    margin-top: 8px;
    font-size: 15px;
    color: #94A3B8;
    font-weight: 600;
  }
  .legend {
    margin: 14px auto 0;
    display: inline-flex;
    gap: 24px;
    background: rgba(15, 23, 42, 0.85);
    border: 1px solid rgba(56, 189, 248, 0.35);
    border-radius: 999px;
    padding: 8px 24px;
    font-size: 13px;
    font-weight: 700;
  }
  .leg-item { display: flex; align-items: center; gap: 8px; }
  .dot { width: 11px; height: 11px; border-radius: 50%; }
  svg.spine {
    position: absolute;
    top: 0;
    left: 0;
    width: 1152px;
    height: 2064px;
    z-index: 2;
    pointer-events: none;
  }
  .card {
    position: absolute;
    width: 446px;
    height: 112px;
    border-radius: 14px;
    padding: 13px 16px;
    z-index: 4;
    background: linear-gradient(145deg, rgba(15, 23, 42, 0.92), rgba(30, 41, 59, 0.92));
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.55);
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .card.done {
    border: 1.5px solid rgba(34, 211, 238, 0.65);
    box-shadow: 0 0 18px rgba(34, 211, 238, 0.14);
  }
  .card.active {
    border: 2px solid #F59E0B;
    box-shadow: 0 0 22px rgba(245, 158, 11, 0.32);
  }
  .card.milestone {
    border-color: #EC4899;
    box-shadow: 0 0 20px rgba(236, 72, 153, 0.24);
  }
  .card-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .wk-pill {
    font-size: 13px;
    font-weight: 900;
    letter-spacing: 0.6px;
    color: #38BDF8;
    font-family: monospace;
  }
  .card.active .wk-pill { color: #FCD34D; }
  .status-pill {
    font-size: 10px;
    font-weight: 800;
    padding: 2px 8px;
    border-radius: 999px;
    letter-spacing: 0.5px;
  }
  .pill-done { background: rgba(16, 185, 129, 0.18); color: #34D399; border: 1px solid #10B981; }
  .pill-prog { background: rgba(245, 158, 11, 0.22); color: #FCD34D; border: 1px solid #F59E0B; }
  .pill-star { background: rgba(236, 72, 153, 0.24); color: #F9A8D4; border: 1px solid #EC4899; margin-left: 6px; }
  .card-title {
    font-size: 16px;
    font-weight: 800;
    color: #F8FAFC;
    line-height: 1.2;
  }
  .bullets {
    font-size: 12px;
    color: #CBD5E1;
    line-height: 1.35;
  }
  .footer {
    position: absolute;
    bottom: 18px;
    left: 48px;
    right: 48px;
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #64748B;
    border-top: 1px solid rgba(51, 65, 85, 0.5);
    padding-top: 10px;
    z-index: 5;
  }
</style>
</head>
<body>
  <div class="circuit-bg"></div>
  <div class="header">
    <div class="eyebrow">Robosen K1 Tangible Coding Block System</div>
    <h1>HARDWARE &amp; FIRMWARE TIMELINE (14 WEEKS)</h1>
    <div class="sub">ESP32-S3 Master + Unified CH32V003 Action/End PCBs • 16 Aug – 21 Nov 2026</div>
    <div class="legend">
      <div class="leg-item"><div class="dot" style="background:#10B981;"></div><span style="color:#34D399;">DONE: Weeks 1–13</span></div>
      <div class="leg-item"><div class="dot" style="background:#F59E0B;"></div><span style="color:#FCD34D;">IN PROGRESS: Week 14</span></div>
      <div class="leg-item"><div class="dot" style="background:#EC4899;"></div><span style="color:#F9A8D4;">★ Key Milestones</span></div>
    </div>
  </div>
'''

CARDS = [
    ("W1", "16–22 Aug", "Project Kick-off & BLE Baseline", "• Modular 4-pin pogo & 3.3V bus spec\n• K1 BLE 0xFFE0/0xFFE1 walk decode", "done", False),
    ("W2", "23–29 Aug", "Protocol Reverse-Eng & Daemon", "• Decoded 25+ K1 BLE opcodes & 0x64 ACK\n• Python k1_ble_daemon & CRC-8 sim", "done", False),
    ("W3", "30 Aug–05 Sep", "Master Core & Hardware BOM", "• ESP32-S3, CH32V003F4P6, 2.13\" E-Ink BOM\n• KY-040 debounce & auto BLE pairing", "done", False),
    ("W4", "06–12 Sep", "KiCad Schematics & 3D Enclosures", "• 2 PCB Schematics: Master + Action/End\n• Polarized magnet keying & light pipes", "done", False),
    ("W5", "13–19 Sep", "PCB Layout & Unified RISC-V FW", "• Master & Unified 32x32mm PCB routing\n• CH32V003 0x08003FC0 Flash & 0xCF/0xAA", "done", False),
    ("W6", "20–26 Sep", "PCB Fab Order & E-Ink UI Graphics", "• 2 PCB orders dispatched (0 DRC errors)\n• 2.13\" SSD1680 E-Ink icons & 280ms LUT", "done", False),
    ("W7", "27 Sep–03 Oct", "Midterm Review & 3D Case Prints", "• 5-block production 3D cases printed\n• Mode state machine & midterm defense", "done", True),
    ("W8", "04–10 Oct", "SMT Assembly & Power Qualification", "• TP4056 USB-C, TPS63020 3.3V & BATSENSE\n• Master bring-up, E-Ink & dual knobs test", "done", False),
    ("W9", "11–17 Oct", "SWIO Flashing & 0xCF Config Dock", "• SWIO flash via PD1 on Action/End PCBs\n• Master #1-1 25.4mm ECO & scope bus check", "done", False),
    ("W10", "18–24 Oct", "5-Block K1 Live Integration", "• Master + 3 Action + End Block chained\n• Live BLE steps & 0xBB green LED sync", "done", True),
    ("W11", "25–31 Oct", "Drop Durability & Emergency Stop", "• 1m drop test & sustained thermal check\n• SW5 Red Stop & hot-plug K1 0x0C halt", "done", False),
    ("W12", "01–07 Nov", "Classroom Child Usability Pilot", "• Hands-on pilot with kids (Sat 7 Nov)\n• Captured free-sequencing SUS metrics", "done", True),
    ("W13", "08–14 Nov", "Feedback Polish & 0xEE Dock Menu", "• Added 0xEE End option in Mode 1 Config\n• Auto-dir J1 probe & 50-run soak test", "done", False),
    ("W14", "15–21 Nov", "Final Release & Project Defense", "• PD0 0xCF RX + ESP32/Uno SWIO updates\n• Complete Gerbers, docs & final demo", "active", True),
]


def build_poster_html():
    width, height = 1152, 2064
    cx = width // 2
    y_start = 262
    y_step = 126

    svg_lines = [
        f'<svg class="spine" viewBox="0 0 {width} {height}">',
        f'  <line x1="{cx - 7}" y1="225" x2="{cx - 7}" y2="1965" stroke="#22D3EE" stroke-width="5" stroke-linecap="round" opacity="0.85" />',
        f'  <line x1="{cx + 7}" y1="225" x2="{cx + 7}" y2="1965" stroke="#F59E0B" stroke-width="5" stroke-linecap="round" opacity="0.85" />',
    ]

    cards_html = []
    for idx, (wk, dates, title, bullets, status, star) in enumerate(CARDS):
        yc = y_start + idx * y_step
        is_right = (idx % 2 == 0)
        color = "#F59E0B" if status == "active" else ("#EC4899" if star else "#22D3EE")

        if is_right:
            card_left = cx + 68
            line_x1, line_x2 = cx + 18, card_left
        else:
            card_left = cx - 68 - 446
            line_x1, line_x2 = cx - 18, card_left + 446

        svg_lines.append(f'  <line x1="{line_x1}" y1="{yc}" x2="{line_x2}" y2="{yc}" stroke="{color}" stroke-width="2.5" />')
        svg_lines.append(f'  <circle cx="{cx}" cy="{yc}" r="22" fill="#090F1D" stroke="{color}" stroke-width="3.5" />')
        svg_lines.append(f'  <text x="{cx}" y="{yc + 5}" text-anchor="middle" font-size="13" font-weight="900" fill="#F8FAFC">{wk}</text>')

        pill_cls = "pill-prog" if status == "active" else "pill-done"
        pill_txt = "IN PROGRESS" if status == "active" else "DONE"
        star_html = '<span class="status-pill pill-star">★ MILESTONE</span>' if star else ""
        card_cls = f"card {'active' if status == 'active' else 'done'}{' milestone' if star else ''}"
        card_top = yc - 56
        bullet_html = bullets.replace("\n", "<br/>")

        cards_html.append(f'''
        <div class="{card_cls}" style="left:{card_left}px; top:{card_top}px;">
          <div class="card-top">
            <span class="wk-pill">{wk} • {dates}</span>
            <div>{star_html}<span class="status-pill {pill_cls}">{pill_txt}</span></div>
          </div>
          <div class="card-title">{title}</div>
          <div class="bullets">{bullet_html}</div>
        </div>
        ''')

    svg_lines.append('</svg>')
    footer = '''
      <div class="footer">
        <span>Robosen Block Capstone Project 2026 • Department of Computer Engineering &amp; Robotics</span>
        <span>Verified against Git Repo &amp; Hardware/Firmware Builds</span>
      </div>
    </body></html>
    '''
    return POSTER_HTML + "\n".join(svg_lines) + "\n".join(cards_html) + footer


def find_browser():
    for candidate in (
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        shutil.which("google-chrome"),
        shutil.which("chromium"),
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    ):
        if candidate and os.path.exists(candidate):
            return candidate
    raise RuntimeError("No headless Chromium/Chrome/Edge browser found")


repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
out_dir = os.path.join(repo_root, 'docs', 'diagrams')
os.makedirs(out_dir, exist_ok=True)
jpg_path = os.path.join(out_dir, 'robosen_timeline_poster_concept.jpg')

with tempfile.NamedTemporaryFile('w', suffix='.html', encoding='utf-8', delete=False) as tmp_h:
    tmp_h.write(build_poster_html())
    html_file = tmp_h.name

png_file = html_file.replace('.html', '.png')

try:
    browser = find_browser()
    subprocess.run(
        [
            browser,
            '--headless',
            '--disable-gpu',
            '--window-size=1152,2064',
            f'--screenshot={png_file}',
            f'file://{html_file}',
        ],
        check=True,
    )
    if shutil.which("sips"):
        subprocess.run(
            ['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '92', png_file, '--out', jpg_path],
            check=True,
            stdout=subprocess.DEVNULL,
        )
    else:
        from PIL import Image
        Image.open(png_file).convert('RGB').save(jpg_path, quality=92)
    print(f'Poster JPEG generated at: {jpg_path}')
finally:
    for p in (html_file, png_file):
        if os.path.exists(p):
            os.remove(p)
