import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

weeks_data = [
    {
        "week": 1,
        "week_label": "WEEK 01",
        "dates": "16/08 - 22/08/2026",
        "milestone": "วางรากฐานระบบ & บลูทูธเบื้องต้น",
        "milestone_en": "System Foundation & Initial BLE",
        "status": "DONE (เสร็จสิ้น)",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] ร่างโครงสร้างระบบจ่ายไฟ & กำหนดสัญญาณหน้าสัมผัส",
            "[3D] กำหนดขนาดตัวบล็อกให้จับถือถนัดมือ & วางพอร์ต",
            "[FW] ถอดรหัสคำสั่ง BLE พื้นฐานหุ่นยนต์ K1 (เดิน/เลี้ยว)",
            "[UX] ศึกษาหลักสรีรศาสตร์เด็ก & การใช้สี/รูปทรง",
            "[QA] กำหนดเกณฑ์ความปลอดภัย & ป้องกันการลัดวงจร"
        ]
    },
    {
        "week": 2,
        "week_label": "WEEK 02",
        "dates": "23/08 - 29/08/2026",
        "milestone": "ถอดรหัสคำสั่งครบวงจร & ระบบจำลอง",
        "milestone_en": "Protocol Reverse-Engineering & Sim",
        "status": "DONE (เสร็จสิ้น)",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] วิเคราะห์วงจรชาร์จไฟ & จัดเตรียมไฟล์เสียงคำสั่ง",
            "[3D] สรุปรายการชิ้นส่วนต้นแบบ & วัดขนาดจริงแผงวงจร",
            "[FW] ถอดรหัสคำสั่งขั้นสูงกว่า 25 รูปแบบ & ระบบ ACK",
            "[UX] วางโฟลว์: เสียบแท่น Dock -> ต่อแม่เหล็ก -> ไฟสถานะ",
            "[QA] ระบบจำลองการสื่อสารเพื่อทดสอบความถูกต้องข้อมูล"
        ]
    },
    {
        "week": 3,
        "week_label": "WEEK 03",
        "dates": "30/08 - 05/09/2026",
        "milestone": "โปรแกรมควบคุมหลัก & สรุปรายการ BOM",
        "milestone_en": "Master Controller Core & Hardware BOM",
        "status": "DONE (เสร็จสิ้น)",
        "status_code": "done",
        "is_star": False,
        "items": [
            "[HW] สรุป BOM หลัก: ไมโครคอนโทรลเลอร์, ไฟ RGB, จอ, แบต",
            "[3D] ร่างแบบแท่นยึดอุปกรณ์สำหรับชุดทดลองต้นแบบ",
            "[FW] โปรแกรม Master: ค้นหา & เชื่อมต่อหุ่นยนต์อัตโนมัติ",
            "[UX] จัดทำแผนภาพสรุปโฟลว์ขั้นตอนการทำงานระบบ",
            "[QA] ทดสอบฟิลเตอร์ตัดสัญญาณกวนปุ่มหมุน Rotary"
        ]
    },
    {
        "week": 4,
        "week_label": "WEEK 04",
        "dates": "06/09 - 12/09/2026",
        "milestone": "ผังวงจรไฟฟ้าครบชุด & โมเดล 3D",
        "milestone_en": "Schematics Design & 3D Enclosure CAD",
        "status": "IN PROGRESS (กำลังทำ)",
        "status_code": "progress",
        "is_star": False,
        "items": [
            "[HW] ออกแบบวงจร Master, Action, End Block",
            "[3D] ออกแบบ 3D แม่เหล็กกันกลับขั้ว & ท่อนำแสง LED",
            "[FW] ทดสอบเชื่อมต่อส่งคำสั่ง BLE หุ่นยนต์จริงบนบอร์ด",
            "[UX] ออกแบบกราฟิกตัวบล็อก/หน้าจอ: ไอคอนอ่านง่าย",
            "[QA] ตรวจความปลอดภัยไฟฟ้าและวงจรควบคุมการชาร์จ"
        ]
    },
    {
        "week": 5,
        "week_label": "WEEK 05",
        "dates": "13/09 - 19/09/2026",
        "milestone": "ออกแบบแผ่น PCB & พิมพ์ 3D ทดสอบ",
        "milestone_en": "PCB Layout & 3D Prototype Fit Check",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ออกแบบลายวงจร PCB บล็อกทั้ง 3 แบบให้กะทัดรัด",
            "[3D] พิมพ์ 3D เคสทดสอบ: ตรวจความกระชับ & แสงไฟ",
            "[FW] เฟิร์มแวร์ Action Block: บันทึกค่าคำสั่งลง Flash",
            "[UX] ออกแบบสัญลักษณ์ระบุทิศทาง & สเกลปุ่มหมุน",
            "[QA] รันชุดทดสอบสื่อสาร: รับมือขั้วสัมผัสหลวม"
        ]
    },
    {
        "week": 6,
        "week_label": "WEEK 06",
        "dates": "20/09 - 26/09/2026",
        "milestone": "สั่งผลิต PCB & กราฟิกหน้าจอแสดงผล",
        "milestone_en": "PCB Fabrication & OLED UI Graphics",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจแบบวงจร & ส่งสั่งผลิต PCB พร้อมซื้อชิ้นส่วน",
            "[3D] ซื้อแม่เหล็ก N52 แรงสูง, พินสปริง Pogo, แบตเตอรี่",
            "[FW] ระบบแสดงผล OLED: ไอคอนคำสั่ง & แถบระดับค่า",
            "[UX] ผลิตตัวอย่างสติกเกอร์สัญลักษณ์คำสั่งกันรอย",
            "[QA] สเตรสเทสประมวลผลคำสั่งต่อเนื่อง 100 รอบ"
        ]
    },
    {
        "week": 7,
        "week_label": "WEEK 07",
        "dates": "27/09 - 03/10/2026",
        "milestone": "🎯 ประเมินผลกลางภาค (Midterm)",
        "milestone_en": "Midterm Progress Review & Evaluation",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] เตรียมห้องแล็บและเครื่องมือประกอบชิ้นส่วน",
            "[3D] พิมพ์เคส 3D ชุดจริงความทนทานสูงครบ 5 บล็อก",
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
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] บัดกรี SMD/THT อุปกรณ์, พิน, สวิตช์, จอภาพ",
            "[3D] ขัดผิวเคส 3D เรียบเนียน & Dry-fit แผงวงจรลงเคส",
            "[FW] โปรแกรมทดสอบ Master: ตรวจสอบจอ & ลูกบิดหมุน",
            "[UX] ติดสติกเกอร์สัญลักษณ์เคลือบผิวพิเศษบนเคสจริง",
            "[QA] ทดสอบระบบไฟ: แรงดันไฟเลี้ยง & ตัดชาร์จสมบูรณ์"
        ]
    },
    {
        "week": 9,
        "week_label": "WEEK 09",
        "dates": "11/10 - 17/10/2026",
        "milestone": "แฟลชบอร์ดจริง & แท่น Dock",
        "milestone_en": "Firmware Bring-up & Config Dock Test",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจสอบความต่อเนื่องลายวงจร & ความเรียบพิน Pogo",
            "[3D] ติดตั้งแม่เหล็กเข้าเคสตามแนวขั้วแน่นหนา",
            "[FW] แฟลช 4 Action Blocks & ทดสอบตั้งค่าผ่าน Dock",
            "[UX] จัดทำแบบประเมินความสะดวกการใช้งาน (Usability)",
            "[QA] ตรวจวัดสัญญาณ Scope พร้อมทดสอบขยับโยกบล็อก"
        ]
    },
    {
        "week": 10,
        "week_label": "WEEK 10",
        "dates": "18/10 - 24/10/2026",
        "milestone": "🤖 ประกอบครบ 5 บล็อก & สั่งหุ่นยนต์",
        "milestone_en": "5-Block Integration & K1 Live Run",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] ติดตั้งแบตเตอรี่ & สวิตช์ปิด-เปิด Master Block",
            "[3D] ประกอบชิ้นส่วนเข้าเคสสมบูรณ์ครบทั้ง 5 บล็อก",
            "[FW] ครบวงจร: Dock -> ต่อบล็อก -> Run -> หุ่นขยับสำเร็จ",
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
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": False,
        "items": [
            "[HW] ตรวจวัดความร้อนต่อเนื่อง & ไฟเลี้ยงรางยาวสุด",
            "[3D] Drop Test ตกกระแทก 1 ม.: เคสและพินไม่เสียหาย",
            "[FW] ดึงบล็อกออกฉุกเฉิน (E-Stop): หุ่นหยุดทันทีอัตโนมัติ",
            "[UX] ตรวจมาตรฐานความปลอดภัยเด็ก: ขอบมน & ไร้สารพิษ",
            "[QA] ซักซ้อมขั้นตอนทดสอบภาคสนามเสมือนจริง"
        ]
    },
    {
        "week": 12,
        "week_label": "WEEK 12",
        "dates": "01/11 - 07/11/2026",
        "milestone": "🌟 ทดสอบกับผู้ใช้จริง (Pilot Test)",
        "milestone_en": "Weekend Field Pilot & User Experience",
        "status": "SCHEDULED (ตามแผน)",
        "status_code": "scheduled",
        "is_star": True,
        "items": [
            "[HW] ดูแลฮาร์ดแวร์: ติดตามแบตเตอรี่ & อะไหล่สำรอง",
            "[3D] สังเกตการใช้งานจริง: แรงดูดแม่เหล็ก & การหมุนลูกบิด",
            "[FW] ตรวจสอบความเสถียร BLE Telemetry สด",
            "[UX] กิจกรรมต่อบล็อกทดสอบอิสระ & ประเมินความพึงพอใจ",
            "🌟 บันทึกเวลาประมวลผล, ไฟสถานะ & บันทึกปัญหา"
        ]
    },
    {
        "week": 13,
        "week_label": "WEEK 13",
        "dates": "08/11 - 14/11/2026",
        "milestone": "ปรับปรุงตามฟีดแบ็ก & จูนระบบ",
        "milestone_en": "Feedback Refinement & System Polish",
        "status": "SCHEDULED (ตามแผน)",
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
        "status": "SCHEDULED (ตามแผน)",
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

def create_pptx():
    prs = Presentation()
    
    # Ultra-wide landscape whiteboard dimensions: 48 inches wide by 16 inches high
    prs.slide_width = Inches(48)
    prs.slide_height = Inches(16)
    
    blank_slide_layout = prs.slide_layouts[6]
    slide = prs.slides.add_slide(blank_slide_layout)

    # 1. Dark Background Canvas
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
    bg.fill.solid()
    bg.fill.fore_color.rgb = RGBColor(9, 13, 22)
    bg.line.fill.background()

    # 2. Header Section
    header_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.5), Inches(28), Inches(1.2))
    tf = header_box.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    p1.text = "ROBOSEN K1 PHYSICAL MODULAR BLOCKS — 14-WEEK TIMELINE"
    p1.font.bold = True
    p1.font.size = Pt(26)
    p1.font.color.rgb = RGBColor(56, 189, 248) # Cyan

    p2 = tf.add_paragraph()
    p2.text = "Canva Whiteboard Native Vector Presentation • Fully Editable Text & Cards • Horizontal Progression"
    p2.font.size = Pt(13)
    p2.font.color.rgb = RGBColor(148, 163, 184) # Slate

    # 3. Legend on the right of header
    legend_box = slide.shapes.add_textbox(Inches(30), Inches(0.5), Inches(17), Inches(1.2))
    ltf = legend_box.text_frame
    lp = ltf.paragraphs[0]
    lp.text = "🟢 DONE (W1-W3)   |   🟠 IN PROGRESS (W4)   |   🔵 SCHEDULED (W5-W14)   |   ★ KEY MILESTONES (W7, W10, W12, W14)"
    lp.font.size = Pt(13)
    lp.font.bold = True
    lp.font.color.rgb = RGBColor(226, 232, 240)
    lp.alignment = PP_ALIGN.RIGHT

    # 4. Main Horizontal Spine
    spine_y = Inches(8.0)
    spine_left = Inches(1.0)
    spine_width = Inches(46.0)
    spine_height = Inches(0.1)

    spine = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, spine_left, spine_y, spine_width, spine_height)
    spine.fill.solid()
    spine.fill.fore_color.rgb = RGBColor(56, 189, 248) # Cyan line
    spine.line.fill.background()

    # Arrowhead at the end
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, spine_left + spine_width - Inches(0.2), spine_y - Inches(0.12), Inches(0.4), Inches(0.34))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = RGBColor(236, 72, 153)
    arrow.line.fill.background()

    # 5. 14 Cards (Alternating Above & Below)
    start_x = Inches(1.5)
    step_x = Inches(3.25)
    card_w = Inches(3.05)
    card_h = Inches(5.3)
    stem_len = Inches(0.7)

    for idx, w in enumerate(weeks_data):
        node_x = start_x + (idx * step_x)
        is_upper = (w["week"] % 2 != 0)

        # Theme colors
        if w["status_code"] == "done":
            theme_color = RGBColor(16, 185, 129) # Emerald
            card_bg_color = RGBColor(6, 40, 30)
            text_accent = RGBColor(52, 211, 153)
        elif w["status_code"] == "progress":
            theme_color = RGBColor(245, 158, 11) # Amber
            card_bg_color = RGBColor(41, 24, 4)
            text_accent = RGBColor(252, 211, 77)
        else:
            theme_color = RGBColor(56, 189, 248) # Sky Blue
            card_bg_color = RGBColor(15, 23, 42)
            text_accent = RGBColor(125, 211, 252)

        if w["is_star"]:
            border_color = RGBColor(236, 72, 153) # Pink
        else:
            border_color = theme_color

        card_x = node_x - (card_w / 2)

        if is_upper:
            card_y = spine_y - stem_len - card_h
            stem_y = spine_y - stem_len
        else:
            card_y = spine_y + stem_len
            stem_y = spine_y

        # Connector line (Stem)
        stem = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, node_x - Inches(0.02), stem_y, Inches(0.04), stem_len)
        stem.fill.solid()
        stem.fill.fore_color.rgb = theme_color
        stem.line.fill.background()

        # Node dot on horizontal spine
        dot = slide.shapes.add_shape(MSO_SHAPE.OVAL, node_x - Inches(0.12), spine_y - Inches(0.07), Inches(0.24), Inches(0.24))
        dot.fill.solid()
        dot.fill.fore_color.rgb = theme_color
        dot.line.fill.background()

        # Node label W1..W14
        wlabel_box = slide.shapes.add_textbox(node_x - Inches(0.4), spine_y + (Inches(0.15) if is_upper else Inches(-0.45)), Inches(0.8), Inches(0.3))
        wltf = wlabel_box.text_frame
        wlp = wltf.paragraphs[0]
        wlp.text = f"W{w['week']}"
        wlp.font.size = Pt(11)
        wlp.font.bold = True
        wlp.font.color.rgb = RGBColor(248, 250, 252)
        wlp.alignment = PP_ALIGN.CENTER

        # Card shape (Rounded Rectangle)
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, card_x, card_y, card_w, card_h)
        card.fill.solid()
        card.fill.fore_color.rgb = card_bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(2.5 if w["is_star"] else 1.5)

        # Text Frame inside card
        ctf = card.text_frame
        ctf.word_wrap = True
        ctf.margin_left = Inches(0.15)
        ctf.margin_right = Inches(0.15)
        ctf.margin_top = Inches(0.15)
        ctf.margin_bottom = Inches(0.15)

        # Paragraph 1: Week Label & Status
        cp1 = ctf.paragraphs[0]
        cp1.text = f"{w['week_label']}  •  {w['dates']}"
        cp1.font.bold = True
        cp1.font.size = Pt(10)
        cp1.font.color.rgb = text_accent

        # Paragraph 2: Status pill / Star tag
        cp2 = ctf.add_paragraph()
        if w["is_star"]:
            cp2.text = f"[{w['status']}] ★ KEY MILESTONE"
            cp2.font.color.rgb = RGBColor(236, 72, 153)
        else:
            cp2.text = f"[{w['status']}]"
            cp2.font.color.rgb = text_accent
        cp2.font.bold = True
        cp2.font.size = Pt(9.5)

        # Paragraph 3: Milestone Focus Title
        cp3 = ctf.add_paragraph()
        cp3.text = w['milestone']
        cp3.font.bold = True
        cp3.font.size = Pt(12)
        cp3.font.color.rgb = RGBColor(56, 189, 248)

        # Paragraph 4: English Subtitle
        cp4 = ctf.add_paragraph()
        cp4.text = w['milestone_en']
        cp4.font.italic = True
        cp4.font.size = Pt(9)
        cp4.font.color.rgb = RGBColor(148, 163, 184)

        # Deliverables Items
        for itm in w['items']:
            ip = ctf.add_paragraph()
            ip.text = f"• {itm}"
            ip.font.size = Pt(9.5)
            ip.font.color.rgb = RGBColor(226, 232, 240)

    # Footer note
    footer = slide.shapes.add_textbox(Inches(1.0), Inches(15.2), Inches(46), Inches(0.5))
    ftf = footer.text_frame
    fp = ftf.paragraphs[0]
    fp.text = "Robosen Block Physical Tangible Programming System • Senior Capstone Project 2026 • 100% Native Editable Canva Whiteboard Vector Objects"
    fp.font.size = Pt(11)
    fp.font.color.rgb = RGBColor(100, 116, 139)

    # Save presentation
    os.makedirs("C:/Users/nnnn/Projects/robosen_block/docs/diagrams", exist_ok=True)
    pptx_path = "C:/Users/nnnn/Projects/robosen_block/docs/diagrams/robosen_14_weeks_timeline_whiteboard.pptx"
    prs.save(pptx_path)
    print(f"Successfully generated Canva-ready PPTX at: {pptx_path}")

create_pptx()
