import os
import subprocess
import sys

weeks_data = [
    {
        "week": 1,
        "week_label": "WEEK 01",
        "dates": "16/08/2026 - 22/08/2026",
        "milestone": "วางรากฐานระบบ & บลูทูธเบื้องต้น",
        "milestone_en": "System Foundation & Initial BLE",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ร่างโครงสร้างระบบจ่ายไฟ & หน้าสัมผัสเชื่อมต่อระหว่างบล็อก"},
            {"cat": "3D", "icon": "🧊", "text": "กำหนดขนาดและสัดส่วนตัวบล็อกให้จับถือถนัดมือ & วางจุดต่อ"},
            {"cat": "FW", "icon": "💻", "text": "ถอดรหัสคำสั่งบลูทูธพื้นฐานของหุ่นยนต์ K1 (เดิน/ถอย/เลี้ยว)"},
            {"cat": "UX", "icon": "🎨", "text": "ศึกษาหลักสรีรศาสตร์เด็ก & การใช้สี/รูปทรงสื่อความหมาย"},
            {"cat": "QA", "icon": "🛡️", "text": "กำหนดเกณฑ์ความปลอดภัย: แรงยึดแม่เหล็ก & กันลัดวงจร"}
        ]
    },
    {
        "week": 2,
        "week_label": "WEEK 02",
        "dates": "23/08/2026 - 29/08/2026",
        "milestone": "ถอดรหัสคำสั่งครบวงจร & ระบบจำลอง",
        "milestone_en": "Protocol Reverse-Engineering & Sim",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "วิเคราะห์วงจรชาร์จไฟหุ่นยนต์ & จัดเตรียมชุดไฟล์เสียงคำสั่ง"},
            {"cat": "3D", "icon": "🧊", "text": "สรุปรายการชิ้นส่วนต้นแบบ & วัดขนาดจริงของแผงวงจร"},
            {"cat": "FW", "icon": "💻", "text": "ถอดรหัสคำสั่งขั้นสูงกว่า 25 รูปแบบ & ระบบตอบกลับ ACK"},
            {"cat": "UX", "icon": "🎨", "text": "วางลำดับโฟลว์: เสียบแท่น Dock -> ต่อแม่เหล็ก -> ไฟสถานะ"},
            {"cat": "QA", "icon": "🛡️", "text": "พัฒนาระบบจำลองการสื่อสารทดสอบรับส่งข้อมูลความถูกต้อง"}
        ]
    },
    {
        "week": 3,
        "week_label": "WEEK 03",
        "dates": "30/08/2026 - 05/09/2026",
        "milestone": "โปรแกรมควบคุมหลัก & สรุปรายการ BOM",
        "milestone_en": "Master Controller Core & Hardware BOM",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "สรุป BOM หลัก: ไมโครคอนโทรลเลอร์, ไฟ RGB, จอ, ปุ่มปรับ, แบตเตอรี่"},
            {"cat": "3D", "icon": "🧊", "text": "ร่างแบบแท่นยึดอุปกรณ์สำหรับชุดทดลองต้นแบบ & พอร์ตเชื่อมต่อ"},
            {"cat": "FW", "icon": "💻", "text": "โปรแกรม Master: ค้นหาและเชื่อมต่อหุ่นยนต์อัตโนมัติ + Watchdog"},
            {"cat": "UX", "icon": "🎨", "text": "จัดทำแผนภาพสรุปโฟลว์ขั้นตอนการส่งผ่านคำสั่งของระบบบล็อก"},
            {"cat": "QA", "icon": "🛡️", "text": "ทดสอบฟิลเตอร์ตัดสัญญาณกวนปุ่มหมุน Rotary & ลิมิตขอบเขตค่า"}
        ]
    },
    {
        "week": 4,
        "week_label": "WEEK 04",
        "dates": "06/09/2026 - 12/09/2026",
        "milestone": "ผังวงจรไฟฟ้าครบชุด & โมเดล 3D",
        "milestone_en": "Schematics Design & 3D Enclosure CAD",
        "status": "กำลังดำเนินการ (IN PROGRESS)",
        "status_code": "progress",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ออกแบบวงจรไฟฟ้าครบ 3 ส่วน: Master Block, Action, End Block"},
            {"cat": "3D", "icon": "🧊", "text": "ออกแบบ 3D: แม่เหล็กป้องกันต่อกลับด้าน, ท่อนำแสง & เคสหลัก"},
            {"cat": "FW", "icon": "💻", "text": "ทดสอบเชื่อมต่อส่งคำสั่ง BLE หุ่นยนต์จริงบนชุดทดลอง"},
            {"cat": "UX", "icon": "🎨", "text": "ออกแบบกราฟิกตัวบล็อก/หน้าจอ: ไอคอนอ่านง่าย, แถบสี & ลูกศร"},
            {"cat": "QA", "icon": "🛡️", "text": "ตรวจความปลอดภัยไฟฟ้าและวงจรควบคุมการชาร์จแบตเตอรี่"}
        ]
    },
    {
        "week": 5,
        "week_label": "WEEK 05",
        "dates": "13/09/2026 - 19/09/2026",
        "milestone": "ออกแบบแผ่น PCB & พิมพ์ 3D ทดสอบ",
        "milestone_en": "PCB Layout & 3D Prototype Fit Check",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ออกแบบลายวงจร PCB บล็อกทั้ง 3 แบบให้กะทัดรัดลงตัว"},
            {"cat": "3D", "icon": "🧊", "text": "พิมพ์ 3D เคสทดสอบ: ตรวจความกระชับ, แรงดูดแม่เหล็ก & แสงไฟ"},
            {"cat": "FW", "icon": "💻", "text": "เฟิร์มแวร์ Action Block: บันทึกค่าลง Flash & คุมไฟสถานะ"},
            {"cat": "UX", "icon": "🎨", "text": "ออกแบบสัญลักษณ์ระบุทิศทางเสียบต่อ & สเกลรอบปุ่มหมุน"},
            {"cat": "QA", "icon": "🛡️", "text": "รันชุดทดสอบสื่อสารอัตโนมัติ: รับมือกรณีขั้วสัมผัสหลวม"}
        ]
    },
    {
        "week": 6,
        "week_label": "WEEK 06",
        "dates": "20/09/2026 - 26/09/2026",
        "milestone": "สั่งผลิต PCB & กราฟิกหน้าจอแสดงผล",
        "milestone_en": "PCB Fabrication & OLED UI Graphics",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ตรวจสอบความถูกต้องวงจร & สั่งผลิต PCB พร้อมจัดซื้ออุปกรณ์"},
            {"cat": "3D", "icon": "🧊", "text": "จัดซื้อแม่เหล็ก N52 แรงสูง, พินสปริง (Pogo Pin), ลูกบิด, แบตเตอรี่"},
            {"cat": "FW", "icon": "💻", "text": "พัฒนาระบบแสดงผล OLED: ไอคอนคำสั่งใหญ่ชัดเจน & แถบระดับค่า"},
            {"cat": "UX", "icon": "🎨", "text": "ผลิตตัวอย่างสติกเกอร์สัญลักษณ์: ตรวจสอบความคมชัดและกันรอย"},
            {"cat": "QA", "icon": "🛡️", "text": "สเตรสเทสประมวลผลคำสั่งต่อเนื่องกว่า 100 รอบโดยไม่สะดุด"}
        ]
    },
    {
        "week": 7,
        "week_label": "WEEK 07",
        "dates": "27/09/2026 - 03/10/2026",
        "milestone": "🎯 ประเมินผลกลางภาค (Midterm)",
        "milestone_en": "Midterm Progress Review & Evaluation",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "จัดเตรียมห้องแล็บและเครื่องมือสำหรับประกอบชิ้นส่วนอิเล็กทรอนิกส์"},
            {"cat": "3D", "icon": "🧊", "text": "พิมพ์เคส 3D ชุดจริงความทนทานสูงครบเซต 5 บล็อก (1+3+1)"},
            {"cat": "FW", "icon": "💻", "text": "เชื่อมต่อ State Machine: สลับเมนู, โหมดตั้งค่าที่แท่น & โหมดต่อบล็อก"},
            {"cat": "UX", "icon": "🎨", "text": "ประเมินความโค้งมนไม่บาดมือ, ความหนืดลูกบิด & ความชัดหน้าจอ"},
            {"cat": "MILESTONE", "icon": "🎯", "text": "【ประเมินผลกลางภาค】: ส่งรายงานความก้าวหน้า & สอบประเมินผล"}
        ]
    },
    {
        "week": 8,
        "week_label": "WEEK 08",
        "dates": "04/10/2026 - 10/10/2026",
        "milestone": "ประกอบ บัดกรี & ระบบจ่ายไฟ",
        "milestone_en": "PCB Assembly & Power Rail Qualification",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "บัดกรี SMD/THT ชิ้นส่วนอิเล็กทรอนิกส์, พินสปริง, จอภาพ, สวิตช์"},
            {"cat": "3D", "icon": "🧊", "text": "ขัดเก็บผิวสัมผัสเคส 3D ให้เรียบเนียน & Dry-fit แผงวงจรลงในเคส"},
            {"cat": "FW", "icon": "💻", "text": "ติดตั้งโปรแกรมทดสอบลงบอร์ด Master: ตรวจสอบจอ OLED และลูกบิด"},
            {"cat": "UX", "icon": "🎨", "text": "ติดสติกเกอร์สัญลักษณ์คำสั่งเคลือบผิวพิเศษลงบนตัวบล็อกจริง"},
            {"cat": "QA", "icon": "🛡️", "text": "ทดสอบความปลอดภัยระบบไฟ: แรงดันไฟเลี้ยง, ตัดชาร์จ & ไฟสแตนด์บาย"}
        ]
    },
    {
        "week": 9,
        "week_label": "WEEK 09",
        "dates": "11/10/2026 - 17/10/2026",
        "milestone": "แฟลชบอร์ดจริง & แท่น Dock",
        "milestone_en": "Firmware Bring-up & Config Dock Test",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ตรวจสอบความต่อเนื่องลายวงจร & ระดับความเรียบของพินสปริง"},
            {"cat": "3D", "icon": "🧊", "text": "ติดตั้งแม่เหล็กเข้าเคสตามแนวขั้ว ดูดประกบแม่นยำไม่กลับด้าน"},
            {"cat": "FW", "icon": "💻", "text": "แฟลชโปรแกรมลง 4 Action Blocks & ทดสอบตั้งค่าผ่านแท่น Dock"},
            {"cat": "UX", "icon": "🎨", "text": "จัดทำแบบประเมินความสะดวกการใช้งาน (Usability Rubric)"},
            {"cat": "QA", "icon": "🛡️", "text": "ตรวจวัดสัญญาณข้อมูลด้วย Oscilloscope พร้อมทดสอบขยับโยกบล็อก"}
        ]
    },
    {
        "week": 10,
        "week_label": "WEEK 10",
        "dates": "18/10/2026 - 24/10/2026",
        "milestone": "🤖 ประกอบครบ 5 บล็อก & สั่งหุ่นยนต์",
        "milestone_en": "5-Block Integration & K1 Live Run",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ติดตั้งแบตเตอรี่และสวิตช์ปิด-เปิดเข้ากับ Master Block พร้อมระบบป้องกัน"},
            {"cat": "3D", "icon": "🧊", "text": "ประกอบวงจร, จอภาพ, ปุ่มหมุน, ช่องไฟเข้าเคสสมบูรณ์ครบทั้ง 5 บล็อก"},
            {"cat": "FW", "icon": "💻", "text": "ทดสอบครบวงจร: Dock -> ต่อบล็อก -> กด Run -> สั่งงานหุ่นสำเร็จ"},
            {"cat": "UX", "icon": "🎨", "text": "จัดเซตกล่องบล็อกครบ 5 ชิ้น พร้อมจัดทำคู่มือการใช้งานเบื้องต้น"},
            {"cat": "QA", "icon": "🛡️", "text": "ตรวจไฟแสดงผลวิ่งตามจังหวะหุ่นยนต์ & ยืนยันความแม่นยำ 100%"}
        ]
    },
    {
        "week": 11,
        "week_label": "WEEK 11",
        "dates": "25/10/2026 - 31/10/2026",
        "milestone": "Drop Test, E-Stop & ซ้อมใหญ่",
        "milestone_en": "Durability Test, Emergency E-Stop & Prep",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ตรวจวัดความร้อนขณะใช้งานต่อเนื่อง & แรงดันตกคร่อมเมื่อต่อบล็อกยาวสุด"},
            {"cat": "3D", "icon": "🧊", "text": "ทดสอบตกกระแทก Drop Test 1 ม.: เคสและพินขั้วสัมผัสไม่เสียหาย"},
            {"cat": "FW", "icon": "💻", "text": "ทดสอบความปลอดภัยเมื่อดึงบล็อกออกขณะทำงาน: หุ่นหยุดทันทีอัตโนมัติ"},
            {"cat": "UX", "icon": "🎨", "text": "ตรวจมาตรฐานความปลอดภัย: ขอบมนปลอดภัย, วัสดุไร้สารพิษ & แม่เหล็กแน่น"},
            {"cat": "QA", "icon": "🛡️", "text": "ซักซ้อมขั้นตอนทดสอบภาคสนามเสมือนจริง: เตรียมอุปกรณ์สำรอง & กล้อง"}
        ]
    },
    {
        "week": 12,
        "week_label": "WEEK 12",
        "dates": "01/11/2026 - 07/11/2026",
        "milestone": "🌟 ทดสอบกับผู้ใช้จริง (Pilot Test)",
        "milestone_en": "Weekend Field Pilot & User Experience",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "สแตนด์บายดูแลฮาร์ดแวร์: ติดตามแบตเตอรี่, ทำความสะอาดขั้ว & อะไหล่สำรอง"},
            {"cat": "3D", "icon": "🧊", "text": "ประเมินการใช้งานจริง: ความง่ายในการต่อแม่เหล็ก & ความถนัดลูกบิด"},
            {"cat": "FW", "icon": "💻", "text": "ติดตามระบบควบคุมและการสื่อสาร: ตรวจสอบความเสถียร BLE สด"},
            {"cat": "UX", "icon": "🎨", "text": "จัดกิจกรรมให้ผู้ใช้ทดลองต่อบล็อกสั่งงานหุ่นยนต์อิสระ & ประเมินความพึงพอใจ"},
            {"cat": "QA", "icon": "🛡️", "text": "บันทึกข้อมูลเชิงประจักษ์: เวลาประมวลผล, ไฟสถานะ & บันทึกปัญหา"}
        ]
    },
    {
        "week": 13,
        "week_label": "WEEK 13",
        "dates": "08/11/2026 - 14/11/2026",
        "milestone": "ปรับปรุงตามฟีดแบ็ก & จูนระบบ",
        "milestone_en": "Feedback Refinement & System Polish",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "ตรวจสภาพจุดต่อและแบตเตอรี่หลังผ่านงานหนัก & โหมดประหยัดพลังงาน"},
            {"cat": "3D", "icon": "🧊", "text": "ปรับปรุงเคส: เพิ่มลายกันลื่นลูกบิดหมุน & ปรับมุมลาดเอียงให้ต่อง่าย"},
            {"cat": "FW", "icon": "💻", "text": "ปรับแต่งโปรแกรม: ปรับความลื่นไหลลูกบิด & คอนทราสต์ไอคอนหน้าจอ"},
            {"cat": "UX", "icon": "🎨", "text": "วิเคราะห์ผลผู้ใช้: สรุปคะแนน SUS Usability & จัดทำแผนภูมิสรุป"},
            {"cat": "QA", "icon": "🛡️", "text": "ทดสอบรันคำสั่งผสมผสานต่อเนื่อง 50+ รอบ ยืนยันความเสถียรสูงสุด"}
        ]
    },
    {
        "week": 14,
        "week_label": "WEEK 14",
        "dates": "15/11/2026 - 21/11/2026",
        "milestone": "🏆 ส่งมอบสมบูรณ์ & สอบป้องกันโครงงาน",
        "milestone_en": "Final Release, Demo Reel & Project Defense",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "HW", "icon": "⚡", "text": "รวบรวมเอกสารวิศวกรรมฮาร์ดแวร์: Schematic, PCB Gerber, BOM ครบชุด"},
            {"cat": "3D", "icon": "🧊", "text": "ทำความสะอาดเคส, ติดสติกเกอร์สัญลักษณ์ & บรรจุลงกล่องจัดแสดง"},
            {"cat": "FW", "icon": "💻", "text": "จัดเก็บซอร์สโค้ดและโครงสร้างเวอร์ชันสมบูรณ์ (Release v1.0.0)"},
            {"cat": "UX", "icon": "🎨", "text": "จัดทำเล่มรายงานวิชาการฉบับสมบูรณ์ & สไลด์นำเสนอภาษาไทย/อังกฤษ"},
            {"cat": "MILESTONE", "icon": "🏆", "text": "【สอบป้องกันโครงงาน】: ฉายวิดีโอสาธิต & สมาชิกทุกคนร่วมสาธิตสด"}
        ]
    }
]

def build_horizontal_infographic_html():
    width = 5200
    height = 1580
    spine_y = 780
    
    # Node X positions
    start_x = 220
    step_x = 366
    card_w = 336
    card_h = 475
    stem_len = 65

    cards_html = ""
    svg_connectors = ""

    for idx, w in enumerate(weeks_data):
        node_x = start_x + (idx * step_x)
        is_upper = (w["week"] % 2 != 0)  # Odd = Upper, Even = Lower
        
        # Colors based on status
        if w["status_code"] == "done":
            theme_color = "#10B981"
            bg_color = "rgba(6, 78, 59, 0.45)"
            badge_bg = "#065F46"
            badge_text = "#34D399"
            glow_color = "rgba(16, 185, 129, 0.5)"
            border_css = "1px solid rgba(16, 185, 129, 0.55)"
        elif w["status_code"] == "progress":
            theme_color = "#F59E0B"
            bg_color = "rgba(120, 53, 15, 0.5)"
            badge_bg = "#92400E"
            badge_text = "#FCD34D"
            glow_color = "rgba(245, 158, 11, 0.7)"
            border_css = "2px solid #F59E0B"
        else:
            theme_color = "#38BDF8"
            bg_color = "rgba(15, 23, 42, 0.75)"
            badge_bg = "#0F172A"
            badge_text = "#7DD3FC"
            glow_color = "rgba(56, 189, 248, 0.4)"
            border_css = "1px solid rgba(56, 189, 248, 0.35)"

        if w["is_star"]:
            border_css = "2px solid #EC4899"
            star_pill = '<span class="star-pill">★ KEY MILESTONE</span>'
        else:
            star_pill = ''

        card_left = node_x - (card_w // 2)

        if is_upper:
            card_top = spine_y - stem_len - card_h
            stem_y1 = spine_y
            stem_y2 = spine_y - stem_len
            arrow_d = f"M {node_x-6} {stem_y2+8} L {node_x} {stem_y2} L {node_x+6} {stem_y2+8}"
        else:
            card_top = spine_y + stem_len
            stem_y1 = spine_y
            stem_y2 = spine_y + stem_len
            arrow_d = f"M {node_x-6} {stem_y2-8} L {node_x} {stem_y2} L {node_x+6} {stem_y2-8}"

        # SVG Stem & Node
        svg_connectors += f'''
        <!-- Branch Week {w["week"]} -->
        <line x1="{node_x}" y1="{stem_y1}" x2="{node_x}" y2="{stem_y2}" stroke="{theme_color}" stroke-width="3" stroke-dasharray="{"none" if w["status_code"] != "scheduled" else "6,4"}" />
        <path d="{arrow_d}" fill="none" stroke="{theme_color}" stroke-width="3" stroke-linecap="round" />
        <circle cx="{node_x}" cy="{spine_y}" r="18" fill="{glow_color}" opacity="0.35" />
        <circle cx="{node_x}" cy="{spine_y}" r="11" fill="#0F172A" stroke="{theme_color}" stroke-width="4" />
        <circle cx="{node_x}" cy="{spine_y}" r="4" fill="{theme_color}" />
        <text x="{node_x}" y="{spine_y + (4 if is_upper else -18)}" text-anchor="middle" font-size="11" font-weight="800" fill="#E2E8F0" font-family="monospace">W{w["week"]}</text>
        '''

        # Items HTML
        items_html = ""
        for itm in w["summary"]:
            items_html += f'''
            <div class="item-row">
                <span class="item-icon">{itm["icon"]}</span>
                <div class="item-body">
                    <span class="item-tag">[{itm["cat"]}]</span>
                    <span class="item-text">{itm["text"]}</span>
                </div>
            </div>
            '''

        cards_html += f'''
        <!-- CARD W{w["week"]} -->
        <div class="week-card status-{w["status_code"]}" style="left: {card_left}px; top: {card_top}px; width: {card_w}px; height: {card_h}px; {border_css};">
            <div class="card-head">
                <div style="display: flex; align-items: center; gap: 6px;">
                    <span class="week-badge" style="background:{badge_bg}; color:{badge_text};">{w["week_label"]}</span>
                    <span class="date-badge">{w["dates"]}</span>
                </div>
                <span class="status-badge" style="background:{badge_bg}; color:{badge_text}; border: 1px solid {theme_color};">
                    {w["status_code"].upper()}
                </span>
            </div>
            {star_pill}
            <div class="milestone-title">{w["milestone"]}</div>
            <div class="milestone-sub">{w["milestone_en"]}</div>
            <div class="items-list">
                {items_html}
            </div>
        </div>
        '''

    html_doc = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <title>Robosen K1 Modular Block — 14-Week Horizontal Master Timeline Infographic</title>
    <style>
        @page {{
            size: {width}px {height}px;
            margin: 0;
        }}
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        html, body {{
            width: {width}px;
            height: {height}px;
            overflow: hidden;
            background-color: #090D16;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Leelawadee UI", "Tahoma", sans-serif;
            color: #F8FAFC;
            position: relative;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }}
        
        /* High-tech Blueprint background */
        .bg-grid {{
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(30, 41, 59, 0.35) 1px, transparent 1px),
                linear-gradient(90deg, rgba(30, 41, 59, 0.35) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: 0;
        }}

        /* Header Canvas */
        header {{
            position: absolute;
            top: 25px;
            left: 50px;
            right: 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            z-index: 10;
            border-bottom: 1px solid rgba(51, 65, 85, 0.6);
            padding-bottom: 20px;
        }}
        .header-title-box {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .logo-box {{
            background: linear-gradient(135deg, #06B6D4, #3B82F6);
            width: 54px;
            height: 54px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: 900;
            box-shadow: 0 0 20px rgba(6, 182, 212, 0.5);
        }}
        .title-main {{
            font-size: 28px;
            font-weight: 900;
            letter-spacing: 0.5px;
            background: linear-gradient(90deg, #38BDF8, #818CF8, #EC4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .title-sub {{
            font-size: 14px;
            color: #94A3B8;
            margin-top: 3px;
        }}
        .legend-box {{
            display: flex;
            align-items: center;
            gap: 24px;
            background: rgba(15, 23, 42, 0.85);
            padding: 10px 24px;
            border-radius: 30px;
            border: 1px solid #334155;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            font-weight: 700;
        }}
        .dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }}

        /* SVG Spine Layer */
        .svg-canvas {{
            position: absolute;
            top: 0;
            left: 0;
            width: {width}px;
            height: {height}px;
            z-index: 1;
            pointer-events: none;
        }}

        /* Week Cards */
        .week-card {{
            position: absolute;
            background: linear-gradient(145deg, rgba(15, 23, 42, 0.94), rgba(30, 41, 59, 0.94));
            backdrop-filter: blur(16px);
            border-radius: 16px;
            padding: 16px 18px;
            z-index: 5;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.6);
            display: flex;
            flex-direction: column;
        }}
        .card-head {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            padding-bottom: 8px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.2);
        }}
        .week-badge {{
            font-size: 12px;
            font-weight: 800;
            padding: 3px 8px;
            border-radius: 6px;
            letter-spacing: 0.5px;
            font-family: monospace;
        }}
        .date-badge {{
            font-size: 11px;
            color: #94A3B8;
            font-family: monospace;
        }}
        .status-badge {{
            font-size: 10px;
            font-weight: 800;
            padding: 2px 7px;
            border-radius: 12px;
            letter-spacing: 0.5px;
        }}
        .star-pill {{
            display: inline-block;
            background: #EC4899;
            color: #FFFFFF;
            font-size: 10px;
            font-weight: 900;
            padding: 2px 7px;
            border-radius: 4px;
            margin-bottom: 6px;
            align-self: flex-start;
            box-shadow: 0 0 10px rgba(236, 72, 153, 0.6);
        }}
        .milestone-title {{
            font-size: 14.5px;
            font-weight: 800;
            color: #38BDF8;
            line-height: 1.3;
            margin-bottom: 3px;
        }}
        .milestone-sub {{
            font-size: 11px;
            color: #64748B;
            font-style: italic;
            margin-bottom: 10px;
        }}
        .items-list {{
            flex: 1;
            display: flex;
            flex-direction: column;
            gap: 7px;
            overflow: hidden;
        }}
        .item-row {{
            display: flex;
            align-items: flex-start;
            gap: 7px;
            font-size: 12px;
            line-height: 1.32;
            color: #CBD5E1;
        }}
        .item-icon {{
            font-size: 13px;
            flex-shrink: 0;
            margin-top: 1px;
        }}
        .item-tag {{
            color: #94A3B8;
            font-weight: 800;
            font-size: 10.5px;
            margin-right: 2px;
        }}

        /* Footer */
        footer {{
            position: absolute;
            bottom: 20px;
            left: 50px;
            right: 50px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(51, 65, 85, 0.6);
            padding-top: 15px;
            font-size: 13px;
            color: #64748B;
            z-index: 10;
        }}
    </style>
</head>
<body>
    <div class="bg-grid"></div>

    <header>
        <div class="header-title-box">
            <div class="logo-box">🤖</div>
            <div>
                <div class="title-main">ROBOSEN K1 MODULAR PROGRAMMING BLOCKS — 14-WEEK INFOGRAPHIC</div>
                <div class="title-sub">Physical Tangible Coding Blocks Project • Single Horizontal Spine (Left-to-Right Progression)</div>
            </div>
        </div>
        <div class="legend-box">
            <div class="legend-item"><div class="dot" style="background:#10B981;"></div><span style="color:#34D399;">DONE (เสร็จสิ้น): W1-W3</span></div>
            <div class="legend-item"><div class="dot" style="background:#F59E0B;"></div><span style="color:#FCD34D;">IN PROGRESS (กำลังดำเนินการ): W4</span></div>
            <div class="legend-item"><div class="dot" style="background:#38BDF8;"></div><span style="color:#7DD3FC;">SCHEDULED (ตามแผนงาน): W5-W14</span></div>
            <div class="legend-item"><div class="dot" style="background:#EC4899;"></div><span style="color:#F472B6;">★ KEY MILESTONES (W7, W10, W12, W14)</span></div>
        </div>
    </header>

    <!-- SVG Spine Layer -->
    <svg class="svg-canvas" viewBox="0 0 {width} {height}">
        <defs>
            <linearGradient id="spineGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stop-color="#10B981" />
                <stop offset="25%" stop-color="#10B981" />
                <stop offset="30%" stop-color="#F59E0B" />
                <stop offset="50%" stop-color="#38BDF8" />
                <stop offset="85%" stop-color="#818CF8" />
                <stop offset="100%" stop-color="#EC4899" />
            </linearGradient>
            <filter id="glowFilter" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="5" result="blur" />
                <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
        </defs>

        <!-- Main Horizontal Spine Line -->
        <line x1="80" y1="{spine_y}" x2="{width - 90}" y2="{spine_y}" stroke="url(#spineGrad)" stroke-width="8" stroke-linecap="round" />
        <line x1="80" y1="{spine_y}" x2="{width - 90}" y2="{spine_y}" stroke="#FFFFFF" stroke-width="2" stroke-opacity="0.4" stroke-linecap="round" />
        
        <!-- Forward Arrowhead -->
        <polygon points="{width - 80},{spine_y} {width - 105},{spine_y - 12} {width - 105},{spine_y + 12}" fill="#EC4899" />

        <!-- Milestone Connectors & Central Dots -->
        {svg_connectors}
    </svg>

    <!-- Week Cards -->
    {cards_html}

    <footer>
        <div>Capstone Senior Project 2026 • Department of Computer Engineering &amp; Robotics • Focus on System Deliverables &amp; Milestones</div>
        <div>Source: 14 Weeks Plan Google Spreadsheet • Generated High-Resolution Infographic PDF</div>
    </footer>
</body>
</html>
'''
    return html_doc

# Generate HTML file
os.makedirs("C:/Users/nnnn/Projects/robosen_block/docs/diagrams", exist_ok=True)
html_path = "C:/Users/nnnn/Projects/robosen_block/docs/diagrams/robosen_14_weeks_timeline_horizontal.html"
pdf_path = "C:/Users/nnnn/Projects/robosen_block/docs/diagrams/robosen_14_weeks_timeline_horizontal.pdf"
png_path = "C:/Users/nnnn/Projects/robosen_block/docs/diagrams/robosen_14_weeks_timeline_horizontal.png"

html_content = build_horizontal_infographic_html()
with open(html_path, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"1. Created HTML at: {html_path}")

# Run Edge headless to render PDF
edge_cmd = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "--headless",
    "--disable-gpu",
    "--no-pdf-header-footer",
    f"--print-to-pdf={pdf_path}",
    html_path
]

print("Rendering PDF via Edge headless...")
res_pdf = subprocess.run(edge_cmd, capture_output=True, text=True)
if os.path.exists(pdf_path):
    print(f"2. Successfully created PDF at: {pdf_path} (Size: {os.path.getsize(pdf_path)} bytes)")
else:
    print(f"Error rendering PDF: {res_pdf.stderr}")

# Also render PNG picture
png_cmd = [
    "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
    "--headless",
    "--disable-gpu",
    "--window-size=5200,1580",
    f"--screenshot={png_path}",
    html_path
]
print("Rendering PNG screenshot via Edge headless...")
res_png = subprocess.run(png_cmd, capture_output=True, text=True)
if os.path.exists(png_path):
    print(f"3. Successfully created PNG image at: {png_path} (Size: {os.path.getsize(png_path)} bytes)")

