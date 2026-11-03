import os

weeks_data = [
    {
        "week": 1,
        "week_label": "WEEK 01",
        "dates": "16/08 - 22/08/2026",
        "milestone": "วางรากฐานระบบ & บลูทูธเบื้องต้น",
        "milestone_en": "System Foundation & Initial BLE",
        "status": "DONE",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] ร่างโครงสร้างระบบจ่ายไฟ & ขั้วเชื่อมต่อ",
            "[3D] กำหนดขนาดตัวบล็อกให้จับถือถนัดมือ",
            "[FW] ถอดรหัสคำสั่ง BLE พื้นฐาน (เดิน/ถอย/เลี้ยว)",
            "[UX] ศึกษาหลักสรีรศาสตร์เด็ก & สี/รูปทรง",
            "[QA] กำหนดเกณฑ์ความปลอดภัย & กันลัดวงจร"
        ]
    },
    {
        "week": 2,
        "week_label": "WEEK 02",
        "dates": "23/08 - 29/08/2026",
        "milestone": "ถอดรหัสคำสั่งครบวงจร & ระบบจำลอง",
        "milestone_en": "Protocol Reverse-Engineering & Sim",
        "status": "DONE",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] วิเคราะห์วงจรชาร์จไฟ & ไฟล์เสียงคำสั่ง",
            "[3D] สรุปรายการชิ้นส่วน BOM ต้นแบบ & ขนาดจริง",
            "[FW] ถอดรหัส 25+ คำสั่งขั้นสูง & ระบบตอบกลับ ACK",
            "[UX] ลำดับโฟลว์: เสียบแท่น Dock -> ต่อแม่เหล็ก",
            "[QA] ระบบจำลองการสื่อสารทดสอบรับส่งข้อมูล"
        ]
    },
    {
        "week": 3,
        "week_label": "WEEK 03",
        "dates": "30/08 - 05/09/2026",
        "milestone": "โปรแกรมควบคุมหลัก & สรุปรายการ BOM",
        "milestone_en": "Master Controller Core & Hardware BOM",
        "status": "DONE",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] สรุป BOM: MCU, ไฟ RGB, จอ, ปุ่มหมุน, แบต",
            "[3D] ร่างแบบแท่นยึดอุปกรณ์ทดลองต้นแบบ",
            "[FW] โปรแกรม Master: ค้นหา & ต่อหุ่นยนต์อัตโนมัติ",
            "[UX] จัดทำแผนภาพสรุปโฟลว์ส่งผ่านคำสั่งระบบ",
            "[QA] ฟิลเตอร์ตัดสัญญาณกวนปุ่มหมุน Rotary"
        ]
    },
    {
        "week": 4,
        "week_label": "WEEK 04",
        "dates": "06/09 - 12/09/2026",
        "milestone": "ผังวงจรไฟฟ้าครบชุด & โมเดล 3D",
        "milestone_en": "Schematics Design & 3D Enclosure CAD",
        "status": "IN PROGRESS",
        "status_code": "progress",
        "is_star": False,
        "items": [
            "[HW] ออกแบบวงจร Master, Action, End Block",
            "[3D] ออกแบบ 3D แม่เหล็กกันกลับขั้ว & ท่อนำแสง",
            "[FW] ทดสอบเชื่อมต่อส่งคำสั่ง BLE หุ่นยนต์จริง",
            "[UX] กราฟิกไอคอนอ่านง่าย, แถบสี & ลูกศร",
            "[QA] ตรวจความปลอดภัยวงจรชาร์จแบตเตอรี่"
        ]
    },
    {
        "week": 5,
        "week_label": "WEEK 05",
        "dates": "13/09 - 19/09/2026",
        "milestone": "ออกแบบแผ่น PCB & พิมพ์ 3D ทดสอบ",
        "milestone_en": "PCB Layout & 3D Prototype Fit Check",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ออกแบบลายวงจร PCB บล็อกทั้ง 3 แบบ",
            "[3D] พิมพ์ 3D เคสทดสอบ: ตรวจความกระชับ & แสงไฟ",
            "[FW] เฟิร์มแวร์ Action Block: บันทึกค่าลง Flash",
            "[UX] ออกแบบสัญลักษณ์ระบุทิศทาง & สเกลปุ่มหมุน",
            "[QA] ชุดทดสอบสื่อสาร: รับมือขั้วสัมผัสหลวม"
        ]
    },
    {
        "week": 6,
        "week_label": "WEEK 06",
        "dates": "20/09 - 26/09/2026",
        "milestone": "สั่งผลิต PCB & กราฟิกหน้าจอแสดงผล",
        "milestone_en": "PCB Fabrication & OLED UI Graphics",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจแบบวงจร & สั่งผลิต PCB พร้อมซื้อชิ้นส่วน",
            "[3D] ซื้อแม่เหล็ก N52, พินสปริง Pogo, แบตเตอรี่",
            "[FW] ระบบแสดงผล OLED: ไอคอนคำสั่ง & แถบค่า",
            "[UX] ผลิตตัวอย่างสติกเกอร์สัญลักษณ์กันรอย",
            "[QA] สเตรสเทสประมวลผลคำสั่งต่อเนื่อง 100 รอบ"
        ]
    },
    {
        "week": 7,
        "week_label": "WEEK 07",
        "dates": "27/09 - 03/10/2026",
        "milestone": "🎯 ประเมินผลกลางภาค (Midterm)",
        "milestone_en": "Midterm Progress Review & Evaluation",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] จัดเตรียมห้องแล็บและเครื่องมือประกอบบอร์ด",
            "[3D] พิมพ์เคส 3D ชุดจริงความทนทานสูง 5 บล็อก",
            "[FW] State Machine: สลับเมนู & โหมดแท่น Dock",
            "[UX] ประเมินความโค้งมนไม่บาดมือ & ความชัดหน้าจอ",
            "🎯 【ประเมินผลกลางภาค】: ส่งรายงาน & สอบกลางภาค"
        ]
    },
    {
        "week": 8,
        "week_label": "WEEK 08",
        "dates": "04/10 - 10/10/2026",
        "milestone": "ประกอบ บัดกรี & ระบบจ่ายไฟ",
        "milestone_en": "PCB Assembly & Power Rail Qualification",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] บัดกรี SMD/THT อุปกรณ์, พิน, สวิตช์, จอภาพ",
            "[3D] ขัดผิวเคส 3D เรียบเนียน & Dry-fit แผงวงจร",
            "[FW] โปรแกรมทดสอบ Master: ตรวจสอบจอ & ลูกบิด",
            "[UX] ติดสติกเกอร์สัญลักษณ์เคลือบผิวทนพิเศษ",
            "[QA] ทดสอบระบบไฟ: แรงดันไฟเลี้ยง & ตัดชาร์จ"
        ]
    },
    {
        "week": 9,
        "week_label": "WEEK 09",
        "dates": "11/10 - 17/10/2026",
        "milestone": "แฟลชบอร์ดจริง & แท่น Dock",
        "milestone_en": "Firmware Bring-up & Config Dock Test",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจสอบความต่อเนื่องลายวงจร & ความเรียบพิน",
            "[3D] ติดตั้งแม่เหล็กเข้าเคสตามแนวขั้วแน่นหนา",
            "[FW] แฟลช 4 Action Blocks & ทดสอบตั้งค่าผ่าน Dock",
            "[UX] แบบประเมินความสะดวกการใช้งาน (Usability)",
            "[QA] ตรวจวัดสัญญาณ Scope พร้อมทดสอบโยกบล็อก"
        ]
    },
    {
        "week": 10,
        "week_label": "WEEK 10",
        "dates": "18/10 - 24/10/2026",
        "milestone": "🤖 ประกอบครบ 5 บล็อก & สั่งหุ่นยนต์",
        "milestone_en": "5-Block Integration & K1 Live Run",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] ติดตั้งแบตเตอรี่ & สวิตช์ปิด-เปิด Master Block",
            "[3D] ประกอบชิ้นส่วนเข้าเคสสมบูรณ์ครบทั้ง 5 บล็อก",
            "[FW] ครบวงจร: Dock -> ต่อบล็อก -> Run -> หุ่นขยับ",
            "[UX] จัดเซตกล่องบล็อกครบชุด & คู่มือใช้งานเบื้องต้น",
            "🤖 ตรวจสอบไฟสถานะวิ่งตามจังหวะหุ่นยนต์ 100%"
        ]
    },
    {
        "week": 11,
        "week_label": "WEEK 11",
        "dates": "25/10 - 31/10/2026",
        "milestone": "Drop Test, E-Stop & ซ้อมใหญ่",
        "milestone_en": "Durability Test, Emergency E-Stop & Prep",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจวัดความร้อนต่อเนื่อง & ไฟเลี้ยงรางยาวสุด",
            "[3D] Drop Test ตกกระแทก 1 ม.: เคสไม่แตกหัก",
            "[FW] ดึงบล็อกออกฉุกเฉิน (E-Stop): หุ่นหยุดทันที",
            "[UX] ตรวจมาตรฐานความปลอดภัยเด็ก: ขอบมน & ไร้พิษ",
            "[QA] ซักซ้อมขั้นตอนทดสอบภาคสนามเสมือนจริง"
        ]
    },
    {
        "week": 12,
        "week_label": "WEEK 12",
        "dates": "01/11 - 07/11/2026",
        "milestone": "🌟 ทดสอบกับผู้ใช้จริง (Pilot Test)",
        "milestone_en": "Weekend Field Pilot & User Experience",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] ดูแลฮาร์ดแวร์: แบตเตอรี่, ทำความสะอาดขั้ว",
            "[3D] สังเกตการใช้งานจริง: แรงดูดแม่เหล็ก & ลูกบิด",
            "[FW] ตรวจสอบความเสถียร BLE Telemetry สด",
            "[UX] กิจกรรมต่อบล็อกทดสอบอิสระ & แบบสอบถาม",
            "🌟 บันทึกเวลาประมวลผล, ไฟสถานะ & บันทึกปัญหา"
        ]
    },
    {
        "week": 13,
        "week_label": "WEEK 13",
        "dates": "08/11 - 14/11/2026",
        "milestone": "ปรับปรุงตามฟีดแบ็ก & จูนระบบ",
        "milestone_en": "Feedback Refinement & System Polish",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจสภาพจุดต่อหลังงานหนัก & ประหยัดพลังงาน",
            "[3D] ปรับปรุงเคส: ลายกันลื่นลูกบิด & มุมต่อประกบ",
            "[FW] จูนลูกบิดให้นิ่ง & คอนทราสต์ไอคอนจอ OLED",
            "[UX] วิเคราะห์ผล: คำนวณ SUS Score & กราฟสรุป",
            "[QA] รันคำสั่งผสมผสานต่อเนื่อง 50+ รอบเสถียร 100%"
        ]
    },
    {
        "week": 14,
        "week_label": "WEEK 14",
        "dates": "15/11 - 21/11/2026",
        "milestone": "🏆 ส่งมอบสมบูรณ์ & สอบป้องกันโครงงาน",
        "milestone_en": "Final Release, Demo Reel & Project Defense",
        "status": "SCHEDULED",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] รวมเอกสารวิศวกรรม: Schematic, PCB, BOM",
            "[3D] ทำความสะอาดเคส & บรรจุกล่องจัดแสดง",
            "[FW] แท็กซอร์สโค้ดสมบูรณ์ (Release v1.0.0)",
            "[UX] เล่มรายงานวิชาการฉบับสมบูรณ์ & สไลด์นำเสนอ",
            "🏆 【สอบป้องกันโครงงาน】: วิดีโอสาธิต & สาธิตสด"
        ]
    }
]

def generate_pure_canva_svg():
    width = 5200
    height = 1600
    spine_y = 800
    start_x = 220
    step_x = 366
    card_w = 330
    card_h = 470
    stem_len = 65

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background-color: #0B1120; font-family: system-ui, -apple-system, sans-serif;">',
        '  <defs>',
        '    <linearGradient id="spineGradient" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#10B981" />',
        '      <stop offset="25%" stop-color="#10B981" />',
        '      <stop offset="30%" stop-color="#F59E0B" />',
        '      <stop offset="55%" stop-color="#38BDF8" />',
        '      <stop offset="85%" stop-color="#818CF8" />',
        '      <stop offset="100%" stop-color="#EC4899" />',
        '    </linearGradient>',
        '    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#38BDF8" />',
        '      <stop offset="50%" stop-color="#818CF8" />',
        '      <stop offset="100%" stop-color="#EC4899" />',
        '    </linearGradient>',
        '  </defs>',
        '',
        '  <!-- Background -->',
        f'  <rect width="{width}" height="{height}" fill="#090D16" />',
        '',
        '  <!-- Header -->',
        '  <g id="header">',
        '    <rect x="50" y="30" width="56" height="56" rx="12" fill="#0284C7" />',
        '    <text x="78" y="68" font-size="28" text-anchor="middle" fill="#FFFFFF">🤖</text>',
        '    <text x="125" y="58" font-size="28" font-weight="900" fill="url(#headerGrad)">ROBOSEN K1 PHYSICAL MODULAR BLOCKS — 14-WEEK MASTER TIMELINE</text>',
        '    <text x="125" y="82" font-size="14" fill="#94A3B8">CANVA WHITEBOARD COMPATIBLE VECTOR INFOGRAPHIC • SINGLE HORIZONTAL PROGRESSION</text>',
        '',
        '    <!-- Legend -->',
        f'    <g transform="translate({width - 1100}, 45)">',
        '      <rect x="0" y="0" width="1050" height="42" rx="21" fill="#0F172A" stroke="#334155" />',
        '      <circle cx="25" cy="21" r="7" fill="#10B981" />',
        '      <text x="40" y="26" font-size="13" font-weight="700" fill="#34D399">DONE (เสร็จสิ้น): W1-W3</text>',
        '      <circle cx="250" cy="21" r="7" fill="#F59E0B" />',
        '      <text x="265" y="26" font-size="13" font-weight="700" fill="#FCD34D">IN PROGRESS (กำลังทำ): W4</text>',
        '      <circle cx="530" cy="21" r="7" fill="#38BDF8" />',
        '      <text x="545" y="26" font-size="13" font-weight="700" fill="#7DD3FC">SCHEDULED (ตามแผน): W5-W14</text>',
        '      <circle cx="810" cy="21" r="7" fill="#EC4899" />',
        '      <text x="825" y="26" font-size="13" font-weight="700" fill="#F472B6">★ KEY MILESTONE (W7,10,12,14)</text>',
        '    </g>',
        '  </g>',
        '',
        '  <!-- Horizontal Spine Line -->',
        f'  <line x1="80" y1="{spine_y}" x2="{width - 90}" y2="{spine_y}" stroke="url(#spineGradient)" stroke-width="8" stroke-linecap="round" />',
        f'  <line x1="80" y1="{spine_y}" x2="{width - 90}" y2="{spine_y}" stroke="#FFFFFF" stroke-width="2" stroke-opacity="0.4" stroke-linecap="round" />',
        f'  <polygon points="{width - 80},{spine_y} {width - 105},{spine_y - 12} {width - 105},{spine_y + 12}" fill="#EC4899" />',
        ''
    ]

    # Generate each week's node, stem, and whiteboard card
    for idx, w in enumerate(weeks_data):
        node_x = start_x + (idx * step_x)
        is_upper = (w["week"] % 2 != 0)

        if w["status_code"] == "done":
            theme_color = "#10B981"
            card_bg = "#06281E"
            badge_bg = "#064E3B"
            badge_text = "#34D399"
        elif w["status_code"] == "progress":
            theme_color = "#F59E0B"
            card_bg = "#291804"
            badge_bg = "#78350F"
            badge_text = "#FCD34D"
        else:
            theme_color = "#38BDF8"
            card_bg = "#0F172A"
            badge_bg = "#1E293B"
            badge_text = "#7DD3FC"

        card_x = node_x - (card_w // 2)

        if is_upper:
            card_y = spine_y - stem_len - card_h
            stem_y1 = spine_y
            stem_y2 = spine_y - stem_len
            arrow_pts = f"{node_x-6},{stem_y2+8} {node_x},{stem_y2} {node_x+6},{stem_y2+8}"
        else:
            card_y = spine_y + stem_len
            stem_y1 = spine_y
            stem_y2 = spine_y + stem_len
            arrow_pts = f"{node_x-6},{stem_y2-8} {node_x},{stem_y2} {node_x+6},{stem_y2-8}"

        lines.append(f'  <!-- ===== WEEK {w["week"]} WHITEBOARD OBJECT ===== -->')
        lines.append(f'  <g id="week_{w["week"]}_group">')
        
        # Stem
        dash = 'stroke-dasharray="6,4"' if w["status_code"] == "scheduled" else ""
        lines.append(f'    <line x1="{node_x}" y1="{stem_y1}" x2="{node_x}" y2="{stem_y2}" stroke="{theme_color}" stroke-width="3" {dash} />')
        lines.append(f'    <polyline points="{arrow_pts}" fill="none" stroke="{theme_color}" stroke-width="3" stroke-linecap="round" />')
        
        # Central Node
        lines.append(f'    <circle cx="{node_x}" cy="{spine_y}" r="16" fill="{theme_color}" opacity="0.25" />')
        lines.append(f'    <circle cx="{node_x}" cy="{spine_y}" r="10" fill="#0F172A" stroke="{theme_color}" stroke-width="3" />')
        lines.append(f'    <circle cx="{node_x}" cy="{spine_y}" r="4" fill="{theme_color}" />')
        lines.append(f'    <text x="{node_x}" y="{spine_y + (4 if is_upper else -16)}" font-size="11" font-weight="900" fill="#F8FAFC" text-anchor="middle">W{w["week"]}</text>')

        # Whiteboard Card Background
        border_stroke = '#EC4899' if w['is_star'] else theme_color
        border_w = 3 if (w['is_star'] or w['status_code'] == 'progress') else 1.5
        lines.append(f'    <rect x="{card_x}" y="{card_y}" width="{card_w}" height="{card_h}" rx="14" fill="{card_bg}" stroke="{border_stroke}" stroke-width="{border_w}" />')

        # Card Header: Week Pill + Date
        lines.append(f'    <rect x="{card_x + 14}" y="{card_y + 14}" width="75" height="24" rx="6" fill="{badge_bg}" />')
        lines.append(f'    <text x="{card_x + 51}" y="{card_y + 30}" font-size="12" font-weight="800" fill="{badge_text}" text-anchor="middle">{w["week_label"]}</text>')
        lines.append(f'    <text x="{card_x + 98}" y="{card_y + 30}" font-size="11" fill="#94A3B8" font-family="monospace">{w["dates"]}</text>')

        # Status Tag
        lines.append(f'    <rect x="{card_x + card_w - 75}" y="{card_y + 14}" width="60" height="22" rx="11" fill="{badge_bg}" stroke="{theme_color}" stroke-width="1" />')
        lines.append(f'    <text x="{card_x + card_w - 45}" y="{card_y + 29}" font-size="10" font-weight="800" fill="{badge_text}" text-anchor="middle">{w["status"]}</text>')

        # Star badge if milestone
        text_start_y = card_y + 68
        if w["is_star"]:
            lines.append(f'    <rect x="{card_x + 14}" y="{card_y + 44}" width="110" height="18" rx="4" fill="#EC4899" />')
            lines.append(f'    <text x="{card_x + 69}" y="{card_y + 57}" font-size="10" font-weight="800" fill="#FFFFFF" text-anchor="middle">★ KEY MILESTONE</text>')
            text_start_y = card_y + 82

        # Milestone Title (Thai)
        lines.append(f'    <text x="{card_x + 14}" y="{text_start_y}" font-size="14.5" font-weight="800" fill="#38BDF8">{w["milestone"]}</text>')
        # Milestone Subtitle (English)
        lines.append(f'    <text x="{card_x + 14}" y="{text_start_y + 18}" font-size="11" font-style="italic" fill="#64748B">{w["milestone_en"]}</text>')

        # Divider line
        div_y = text_start_y + 28
        lines.append(f'    <line x1="{card_x + 14}" y1="{div_y}" x2="{card_x + card_w - 14}" y2="{div_y}" stroke="#334155" stroke-width="1" />')

        # Deliverable Items (5 items)
        item_y = div_y + 24
        for itm in w["items"]:
            # Wrap long text if needed or print clean text
            lines.append(f'    <text x="{card_x + 14}" y="{item_y}" font-size="12" fill="#E2E8F0">• {itm}</text>')
            item_y += 24

        lines.append('  </g>\n')

    # Footer
    lines.append('  <!-- Footer -->')
    lines.append(f'  <g transform="translate(50, {height - 40})">')
    lines.append('    <text x="0" y="20" font-size="13" fill="#64748B">Robosen Block Capstone Senior Project 2026 • Ready to import directly into Canva Whiteboard</text>')
    lines.append(f'    <text x="{width - 100}" y="20" text-anchor="end" font-size="13" fill="#64748B">Source: 14 Weeks Plan Google Spreadsheet</text>')
    lines.append('  </g>')
    lines.append('</svg>')

    return "\n".join(lines)

svg_str = generate_pure_canva_svg()
canva_svg_path = "C:/Users/nnnn/Projects/robosen_block/docs/diagrams/canva_whiteboard_timeline.svg"
with open(canva_svg_path, "w", encoding="utf-8") as f:
    f.write(svg_str)

print(f"Generated pure Canva-compatible SVG at: {canva_svg_path} (Size: {len(svg_str)} chars)")
