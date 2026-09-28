import os
import json

# Data definition for the 14-week timeline without personal assignments
weeks_data = [
    {
        "week": 1,
        "week_label": "WEEK 01",
        "dates": "16/08/2026 - 22/08/2026",
        "milestone": "วางรากฐานระบบ, โครงสร้างบล็อกคำสั่ง & เชื่อมต่อบลูทูธเบื้องต้น",
        "milestone_en": "System Foundation, Modular Architecture & Baseline BLE Protocol",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ร่างโครงสร้างระบบจ่ายไฟ & กำหนดสัญญาณหน้าสัมผัสเชื่อมต่อระหว่างบล็อก"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "กำหนดขนาดและสัดส่วนตัวบล็อกให้จับถือถนัดมือ & วางตำแหน่งจุดเชื่อมต่อ"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ถอดรหัสคำสั่งบลูทูธเบื้องต้นของหุ่นยนต์ K1 (เดินหน้า ถอยหลัง หันเลี้ยว)"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ศึกษาหลักสรีรศาสตร์ในการจับถือ: ความโค้งมนที่ปลอดภัย และการใช้สี/รูปทรง"},
            {"cat": "ความปลอดภัย & มาตรฐาน", "icon": "🛡️", "text": "กำหนดเกณฑ์ความปลอดภัย: แรงยึดแม่เหล็ก, ระบบกันไฟลัดวงจร & ความทนต่อการตก"}
        ]
    },
    {
        "week": 2,
        "week_label": "WEEK 02",
        "dates": "23/08/2026 - 29/08/2026",
        "milestone": "ถอดรหัสคำสั่งหุ่นยนต์ครบวงจร, สร้างโปรแกรมสื่อสาร & ระบบจำลองการทำงาน",
        "milestone_en": "Advanced Protocol Decoding, Control Engine & Logic Simulation",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "วิเคราะห์ฮาร์ดแวร์หุ่นยนต์, วงจรชาร์จไฟ & จัดเตรียมชุดไฟล์เสียงสำหรับคำสั่ง"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "สรุปรายการชิ้นส่วนต้นแบบ & วัดขนาดจริงของแผงวงจรเพื่อเตรียมออกแบบเคส"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ถอดรหัสคำสั่งขั้นสูงกว่า 25 รูปแบบ, ระบบตอบกลับ (ACK) & โปรแกรมควบคุมการเคลื่อนไหว"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "วางลำดับขั้นตอนการใช้งาน: เสียบตั้งค่าแท่น -> ต่อเรียงบล็อกแม่เหล็ก -> ไฟบอกสถานะ"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "พัฒนาระบบจำลองการสื่อสารเพื่อทดสอบการรับส่งข้อมูลและความถูกต้องของคำสั่ง"}
        ]
    },
    {
        "week": 3,
        "week_label": "WEEK 03",
        "dates": "30/08/2026 - 05/09/2026",
        "milestone": "พัฒนาโครงสร้างโปรแกรมควบคุมหลัก & สรุปรายการอุปกรณ์ฮาร์ดแวร์",
        "milestone_en": "Master Controller Core Engine & Final Hardware BOM",
        "status": "เสร็จสิ้น (DONE)",
        "status_code": "done",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "สรุปรายการอุปกรณ์หลัก (BOM): ไมโครคอนโทรลเลอร์, ไฟสถานะ, จอภาพ, ปุ่มปรับค่า & แบตเตอรี่"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ร่างแบบโครงสร้างยึดอุปกรณ์สำหรับชุดทดลองต้นแบบ & วางตำแหน่งพอร์ตเชื่อมต่อ"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "พัฒนาโปรแกรมหลักบน Master Block: ค้นหาและเชื่อมต่อหุ่นยนต์อัตโนมัติ พร้อมระบบความปลอดภัย"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดทำแผนภาพสรุปโฟลว์ขั้นตอนการทำงานและการส่งผ่านคำสั่งของระบบบล็อก"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ทดสอบความแม่นยำของปุ่มหมุนปรับค่า พร้อมระบบตัดสัญญาณรบกวนและจำกัดขอบเขตค่า"}
        ]
    },
    {
        "week": 4,
        "week_label": "WEEK 04",
        "dates": "06/09/2026 - 12/09/2026",
        "milestone": "ออกแบบแผนผังวงจรไฟฟ้าครบชุด & ขึ้นโมเดลสามมิติตัวบล็อกคำสั่ง",
        "milestone_en": "Complete Electrical Schematics & 3D Enclosure CAD Modeling",
        "status": "กำลังดำเนินการ (IN PROGRESS)",
        "status_code": "progress",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ออกแบบวงจรไฟฟ้าครบ 3 ส่วน: Master Block, Action Block และ End Block"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ออกแบบโมเดล 3D: แม่เหล็กป้องกันต่อกลับด้าน, ท่อนำแสงไฟแสดงผล & เคสบล็อกหลัก"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ทดสอบเชื่อมต่อบล็อกจำลองเข้ากับหุ่นยนต์จริง เพื่อยืนยันการส่งคำสั่งไร้สายผ่าน BLE"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ออกแบบกราฟิกบนตัวบล็อกและหน้าจอ: ไอคอนคำสั่งอ่านง่าย, แถบสีแบ่งหมวด & ลูกศรทิศทาง"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ตรวจสอบความปลอดภัยทางไฟฟ้าและวงจรควบคุมการชาร์จแบตเตอรี่บนชุดทดลอง"}
        ]
    },
    {
        "week": 5,
        "week_label": "WEEK 05",
        "dates": "13/09/2026 - 19/09/2026",
        "milestone": "ออกแบบแผ่นวงจรพิมพ์ (PCB), พัฒนาโปรแกรมประจำบล็อก & พิมพ์ชิ้นงานสามมิติทดสอบ",
        "milestone_en": "PCB Routing, Action Block Firmware & 3D Test Print Fit Checks",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ออกแบบลายวงจรแผ่น PCB ให้มีขนาดกะทัดรัดและลงตัวกับโครงสร้างบล็อกทั้ง 3 รูปแบบ"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "พิมพ์ชิ้นงาน 3D ทดสอบ: ตรวจสอบความกระชับของชิ้นส่วน, แรงดูดแม่เหล็ก & การมองเห็นแสงไฟ"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "พัฒนาโปรแกรมประจำ Action Block: บันทึกค่าลงหน่วยความจำ, ควบคุมไฟสถานะ & ประมวลผล"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ออกแบบสัญลักษณ์บนบล็อก: เครื่องหมายจุดต่อ, สเกลรอบปุ่มหมุน & สัญลักษณ์ปิดท้าย"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "รันชุดทดสอบการสื่อสารอัตโนมัติ: รับมือกรณีต่อบล็อกไม่แน่น & ตรวจความถูกต้องข้อมูล"}
        ]
    },
    {
        "week": 6,
        "week_label": "WEEK 06",
        "dates": "20/09/2026 - 26/09/2026",
        "milestone": "สั่งผลิตแผ่นวงจรและจัดซื้ออุปกรณ์ & พัฒนากราฟิกหน้าจอแสดงผล",
        "milestone_en": "PCB Manufacturing Dispatch, Parts Procurement & OLED UI Graphics",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ตรวจสอบความถูกต้องของแบบวงจร & ส่งสั่งผลิตแผ่นวงจรพิมพ์ (PCB) และสั่งซื้อชิ้นส่วน"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "จัดซื้อชิ้นส่วนโครงสร้าง: แม่เหล็กแรงสูง N52, ขั้วพินสปริง (Pogo), ปุ่มหมุน, สวิตช์ & แบตเตอรี่"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "พัฒนาระบบแสดงผล OLED: ไอคอนคำสั่งขนาดใหญ่ชัดเจน, ขีดแถบพารามิเตอร์ & สัญญาณบลูทูธ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ผลิตตัวอย่างสติกเกอร์สัญลักษณ์: ตรวจสอบความคมชัด ความทนทานต่อการขูดขีด & แสงไฟ"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ทดสอบความเสถียรของหน่วยประมวลผล: รันประมวลผลคำสั่งต่อเนื่องกว่า 100 รอบโดยไม่สะดุด"}
        ]
    },
    {
        "week": 7,
        "week_label": "WEEK 07",
        "dates": "27/09/2026 - 03/10/2026",
        "milestone": "🎯 ประเมินผลกลางภาค (Midterm), สั่งพิมพ์เคสบล็อกชุดจริง & เตรียมอุปกรณ์ประกอบ",
        "milestone_en": "Midterm Progress Evaluation, Production 3D Cases & Assembly Preparation",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "จัดเตรียมเครื่องมือ อุปกรณ์บัดกรี และโต๊ะปฏิบัติการสำหรับประกอบบอร์ดอิเล็กทรอนิกส์"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "พิมพ์ชิ้นงาน 3D เคสชุดจริงความแข็งแรงสูงครบเซต: บล็อกหลัก 1 + บล็อกคำสั่ง 3 + บล็อกปิดท้าย 1"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "เชื่อมโยงระบบแสดงผลกับระบบควบคุม: สลับหน้าจอเมนู, โหมดตั้งค่าบล็อก & โหมดเชื่อมต่อหุ่นยนต์"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ประเมินความสะดวกในการใช้งาน: ขอบมุมโค้งมนไม่บาดมือ, ความหนืดของลูกบิด & ความชัดของจอ"},
            {"cat": "หมุดหมายสำคัญ", "icon": "🎯", "text": "【ประเมินผลกลางภาค】: ส่งรายงานความก้าวหน้าโครงการ, นำเสนอผลงาน & สอบประเมินกลางภาค"}
        ]
    },
    {
        "week": 8,
        "week_label": "WEEK 08",
        "dates": "04/10/2026 - 10/10/2026",
        "milestone": "ประกอบและบัดกรีแผ่นวงจร & ทดสอบความปลอดภัยระบบจ่ายไฟ",
        "milestone_en": "PCB Assembly & Soldering, Power Safety & Bring-up Verification",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ประกอบบัดกรีชิ้นส่วนอิเล็กทรอนิกส์, ขั้วสัมผัสเชื่อมต่อ, ปุ่มปรับค่า & หน้าจอแสดงผล"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ขัดเก็บผิวสัมผัสเคส 3D ให้เรียบเนียน & ทดลองติดตั้งแผงวงจรจริงลงในตัวบล็อก (Dry Fit)"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ติดตั้งโปรแกรมทดสอบลงบล็อกหลัก: ตรวจสอบการทำงานของจอแสดงผลและปุ่มหมุนปรับค่า"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดทำสติกเกอร์สัญลักษณ์คำสั่งเคลือบผิวทนทานพิเศษ พร้อมติดตั้งลงบนเคสบล็อกจริง"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ทดสอบความปลอดภัยทางไฟฟ้า: วัดแรงดันไฟเลี้ยง, ระบบชาร์จตัดไฟ & กระแสไฟสแตนด์บาย"}
        ]
    },
    {
        "week": 9,
        "week_label": "WEEK 09",
        "dates": "11/10/2026 - 17/10/2026",
        "milestone": "ติดตั้งโปรแกรมลงบอร์ดจริง, ทดสอบแท่นตั้งค่าบล็อก & ตรวจสอบการสื่อสารข้อมูล",
        "milestone_en": "Firmware Flashing, Configuration Dock Integration & Signal Integrity",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ตรวจสอบความสมบูรณ์ของลายวงจร & วัดระดับความเรียบเสมอกันของขั้วพินสปริงหน้าสัมผัส"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ติดตั้งแม่เหล็กเข้ากับเคสบล็อกตามแนวขั้วที่กำหนด ดูดประกบแน่นหนาและต่อถูกด้านเสมอ"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ติดตั้งโปรแกรมลง Action Block ทั้ง 4 ชิ้น & ทดสอบตั้งค่าพารามิเตอร์ผ่าน Dock พร้อมไฟตอบรับ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดทำแบบประเมินความสะดวกการใช้งาน: แรงดูดแม่เหล็ก, ความง่ายในการต่อ & การเข้าใจไฟสถานะ"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ตรวจวัดสัญญาณข้อมูลด้วย Oscilloscope พร้อมทดสอบการขยับ/โยกบล็อกขณะส่งข้อมูล"}
        ]
    },
    {
        "week": 10,
        "week_label": "WEEK 10",
        "dates": "18/10/2026 - 24/10/2026",
        "milestone": "🤖 ประกอบตัวบล็อกสมบูรณ์ครบชุด & ทดสอบการทำงานร่วมกับหุ่นยนต์ครบวงจร",
        "milestone_en": "Full 5-Block Integration & End-to-End Execution with K1 Robot",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ติดตั้งชุดแบตเตอรี่และสวิตช์เปิด-ปิดเข้ากับ Master Block พร้อมระบบป้องกันไฟ"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ประกอบวงจร, จอภาพ, ปุ่มหมุน, ปุ่มกด และช่องไฟเข้าเคสตัวบล็อกสมบูรณ์ครบทั้ง 5 บล็อก"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ทดสอบครบวงจร: ตั้งค่าที่แท่น -> ต่อบล็อกเรียงคำสั่ง -> กด Run -> หุ่นยนต์เคลื่อนไหวสำเร็จ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดเซตกล่องบล็อกคำสั่งครบ 5 ชิ้น พร้อมจัดทำคู่มือแนะนำการใช้งานเบื้องต้นแบบเข้าใจง่าย"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ตรวจสอบไฟแสดงผลวิ่งตามจังหวะหุ่นยนต์ & ยืนยันความแม่นยำในการประมวลผลคำสั่ง 100%"}
        ]
    },
    {
        "week": 11,
        "week_label": "WEEK 11",
        "dates": "25/10/2026 - 31/10/2026",
        "milestone": "ทดสอบความแข็งแรงทนทาน, ระบบหยุดทำงานฉุกเฉิน & ซ้อมใหญ่การทำงาน",
        "milestone_en": "Drop Durability Testing, Emergency Disconnect Failsafe & Rehearsal",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ตรวจวัดอุณหภูมิความร้อนขณะใช้งานต่อเนื่อง & วัดแรงดันไฟเลี้ยงเมื่อต่อบล็อกยาวสูงสุด"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ทดสอบการตกกระแทก (Drop Test): ตรวจสอบว่าเคสและขั้วสัมผัสไม่แตกหักเสียหาย"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ทดสอบความปลอดภัยเมื่อดึงบล็อกออกขณะทำงาน: หุ่นยนต์หยุดทำงานทันทีพร้อมสัญญาณเตือน"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "ตรวจมาตรฐานความปลอดภัย: ทุกเหลี่ยมมุมโค้งมน, วัสดุไร้สารพิษ & แม่เหล็กฝังแน่นไม่หลุด"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ซักซ้อมขั้นตอนทดสอบภาคสนามเสมือนจริง: เตรียมอุปกรณ์สำรอง, มุมกล้อง & เกณฑ์ประเมิน"}
        ]
    },
    {
        "week": 12,
        "week_label": "WEEK 12",
        "dates": "01/11/2026 - 07/11/2026",
        "milestone": "🌟 ทดสอบการใช้งานระบบบล็อกจริงกับผู้ใช้ในวันหยุดสุดสัปดาห์ (Usability Pilot)",
        "milestone_en": "Weekend Field Pilot & Usability Testing with Real Users",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ดูแลฮาร์ดแวร์ระหว่างการทดสอบ: ติดตามระดับแบตเตอรี่, ตรวจหน้าสัมผัสขั้วบล็อก & อุปกรณ์สำรอง"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ประเมินการใช้งานจริง: ความง่ายในการต่อ/ถอดบล็อกแม่เหล็ก, ความถนัดในการหมุนลูกบิด & ความทนทาน"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ติดตามระบบควบคุมและการสื่อสาร: ตรวจสอบความเสถียรในการส่งคำสั่งบลูทูธ & จังหวะไฟสถานะ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดกิจกรรมทดสอบกับผู้ใช้จริง: ให้ต่อบล็อกสั่งงานหุ่นยนต์อย่างอิสระ & ประเมินความพึงพอใจ"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "บันทึกข้อมูลเชิงประจักษ์: เวลาที่ใช้ประมวลผล, ความถูกต้องของไฟสถานะ & ปัญหาที่พบเพื่อปรับปรุง"}
        ]
    },
    {
        "week": 13,
        "week_label": "WEEK 13",
        "dates": "08/11/2026 - 14/11/2026",
        "milestone": "ปรับปรุงตามผลตอบรับของผู้ใช้, ปรับแต่งหน้าจอแสดงผลและระบบ & ทดสอบความเสถียร",
        "milestone_en": "Post-Pilot Feedback Refinements, UI/Firmware Polish & Endurance Testing",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": False,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "ตรวจสอบสภาพจุดเชื่อมต่อและแบตเตอรี่หลังผ่านการทดสอบหนัก & ปรับปรุงโหมดประหยัดพลังงาน"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ปรับปรุงเคสตามฟีดแบ็ก: เพิ่มลายกันลื่นที่ลูกบิดหมุน & ปรับมุมลาดเอียงให้ต่อบล็อกได้ง่ายยิ่งขึ้น"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "ปรับแต่งโปรแกรม: ปรับความลื่นไหลของการหมุนค่า, เพิ่มความคมชัดของไอคอน & จังหวะไฟหายใจ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "วิเคราะห์ผลตอบรับจากผู้ใช้: สรุปคะแนนความสะดวกในการจับถือ, ความเข้าใจคำสั่ง & กราฟสรุป"},
            {"cat": "การทดสอบ & QA", "icon": "🛡️", "text": "ทดสอบการทำงานซ้ำแบบผสมผสานต่อเนื่องกว่า 50 รอบ ยืนยันระบบทำงานเสถียรสูงสุดโดยไม่สะดุด"}
        ]
    },
    {
        "week": 14,
        "week_label": "WEEK 14",
        "dates": "15/11/2026 - 21/11/2026",
        "milestone": "🏆 ประกอบชุดบล็อกฉบับสมบูรณ์, ถ่ายวิดีโอสาธิต, จัดทำรายงานวิชาการ & สอบป้องกันโครงงาน",
        "milestone_en": "Final Assembly, Demonstration Video, Technical Report & Final Project Defense",
        "status": "ตามแผนงาน (SCHEDULED)",
        "status_code": "scheduled",
        "is_star": True,
        "summary": [
            {"cat": "ฮาร์ดแวร์ & วงจร", "icon": "⚡", "text": "รวบรวมเอกสารวิศวกรรมฮาร์ดแวร์ฉบับสมบูรณ์: ผังวงจร (Schematic), แบบ PCB, BOM & ผลการทดสอบ"},
            {"cat": "โครงสร้าง & 3D", "icon": "🧊", "text": "ตรวจสอบความเรียบร้อยขั้นสุดท้าย: ทำความสะอาดเคส, ติดสติกเกอร์สัญลักษณ์ & บรรจุลงกล่องจัดแสดง"},
            {"cat": "เฟิร์มแวร์ & โปรโตคอล", "icon": "💻", "text": "จัดเก็บซอร์สโค้ดและโครงสร้างโปรเจกต์เวอร์ชันสมบูรณ์ (Release v1.0.0) พร้อมเอกสารกำกับ"},
            {"cat": "การออกแบบ & สรีรศาสตร์", "icon": "🎨", "text": "จัดทำเล่มรายงานวิชาการฉบับสมบูรณ์: สรุปผลการออกแบบสรีรศาสตร์, รายงานผลการทดสอบ & สไลด์"},
            {"cat": "หมุดหมายสำคัญ", "icon": "🏆", "text": "【สอบป้องกันโครงงาน】: ถ่ายทำวิดีโอสาธิตผลิตภัณฑ์ & สมาชิกทุกคนร่วมสาธิตสดในการสอบป้องกันโครงงาน"}
        ]
    }
]

def generate_svg():
    # Width and height calculations
    width = 1700
    top_offset = 260
    card_height = 255
    y_step = 275
    height = top_offset + (14 * y_step) + 160
    center_x = 850

    # Color palette
    colors = {
        "done": {
            "bg": "#064E3B",
            "border": "#10B981",
            "badge_bg": "#065F46",
            "badge_text": "#34D399",
            "node_glow": "#10B981",
            "node_inner": "#059669",
            "label": "DONE (เสร็จสิ้น)"
        },
        "progress": {
            "bg": "#78350F",
            "border": "#F59E0B",
            "badge_bg": "#92400E",
            "badge_text": "#FCD34D",
            "node_glow": "#F59E0B",
            "node_inner": "#D97706",
            "label": "IN PROGRESS (กำลังดำเนินการ)"
        },
        "scheduled": {
            "bg": "#1E293B",
            "border": "#38BDF8",
            "badge_bg": "#0F172A",
            "badge_text": "#7DD3FC",
            "node_glow": "#38BDF8",
            "node_inner": "#0284C7",
            "label": "SCHEDULED (ตามแผนงาน)"
        }
    }

    svg_lines = [
        f'<svg xmlns="http://www.w3.org/200svg" viewBox="0 0 {width} {height}" width="100%" height="100%" style="background-color: #0B1120; font-family: system-ui, -apple-system, \'Segoe UI\', Roboto, Helvetica, Arial, sans-serif;">',
        '  <defs>',
        '    <linearGradient id="trunkGrad" x1="0%" y1="0%" x2="0%" y2="100%">',
        '      <stop offset="0%" stop-color="#10B981" />',
        '      <stop offset="25%" stop-color="#10B981" />',
        '      <stop offset="30%" stop-color="#F59E0B" />',
        '      <stop offset="45%" stop-color="#38BDF8" />',
        '      <stop offset="100%" stop-color="#818CF8" />',
        '    </linearGradient>',
        '    <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">',
        '      <stop offset="0%" stop-color="#06B6D4" />',
        '      <stop offset="50%" stop-color="#3B82F6" />',
        '      <stop offset="100%" stop-color="#8B5CF6" />',
        '    </linearGradient>',
        '    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feGaussianBlur stdDeviation="4" result="blur" />',
        '      <feComposite in="SourceGraphic" in2="blur" operator="over" />',
        '    </filter>',
        '    <filter id="cardShadow" x="-10%" y="-10%" width="120%" height="120%">',
        '      <feDropShadow dx="0" dy="8" stdDeviation="12" flood-color="#000000" flood-opacity="0.6"/>',
        '    </filter>',
        '  </defs>',
        '',
        '  <!-- Background Grid Pattern -->',
        '  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
        '    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1E293B" stroke-width="0.75" stroke-opacity="0.4"/>',
        '  </pattern>',
        f'  <rect width="{width}" height="{height}" fill="url(#grid)" />',
        '',
        '  <!-- HEADER SECTION -->',
        '  <g transform="translate(0, 45)">',
        f'    <text x="{center_x}" y="35" text-anchor="middle" font-size="14" font-weight="700" letter-spacing="3" fill="#38BDF8">ROBOSEN PHYSICAL MODULAR BLOCK SYSTEM</text>',
        f'    <text x="{center_x}" y="75" text-anchor="middle" font-size="34" font-weight="900" letter-spacing="1" fill="url(#headerGrad)">14-WEEK PROJECT MASTER TIMELINE</text>',
        f'    <text x="{center_x}" y="110" text-anchor="middle" font-size="16" fill="#94A3B8">แผนภาพสรุปความก้าวหน้าและเป้าหมายประจำสัปดาห์ (Focusing on Project Deliverables &amp; Milestones)</text>',
        '',
        '    <!-- Status Legend -->',
        f'    <g transform="translate({center_x - 320}, 140)">',
        '      <circle cx="0" cy="0" r="7" fill="#10B981" />',
        '      <text x="14" y="4" font-size="13" font-weight="600" fill="#34D399">เสร็จสิ้น (DONE): W1-W3</text>',
        '      <circle cx="210" cy="0" r="7" fill="#F59E0B" />',
        '      <text x="224" y="4" font-size="13" font-weight="600" fill="#FCD34D">กำลังดำเนินการ (IN PROGRESS): W4</text>',
        '      <circle cx="470" cy="0" r="7" fill="#38BDF8" />',
        '      <text x="484" y="4" font-size="13" font-weight="600" fill="#7DD3FC">ตามแผนงาน (SCHEDULED): W5-W14</text>',
        '    </g>',
        '  </g>',
        '',
        '  <!-- CENTRAL TIMELINE SPINE (TRUNK) -->',
        f'  <line x1="{center_x}" y1="{top_offset - 20}" x2="{center_x}" y2="{height - 100}" stroke="url(#trunkGrad)" stroke-width="6" stroke-linecap="round" />',
        f'  <line x1="{center_x}" y1="{top_offset - 20}" x2="{center_x}" y2="{height - 100}" stroke="#FFFFFF" stroke-width="1.5" stroke-opacity="0.3" stroke-linecap="round" />',
        ''
    ]

    # Render weeks
    for idx, w in enumerate(weeks_data):
        y_node = top_offset + (idx * y_step)
        cfg = colors[w["status_code"]]
        is_left = (w["week"] % 2 != 0)  # Odd = Left, Even = Right

        card_w = 690
        card_h = card_height

        if is_left:
            card_x = center_x - 70 - card_w
            conn_x1 = center_x
            conn_x2 = center_x - 70
        else:
            card_x = center_x + 70
            conn_x1 = center_x
            conn_x2 = center_x + 70

        # Branch line
        svg_lines.append(f'  <!-- ===== WEEK {w["week"]} BRANCH ===== -->')
        svg_lines.append(f'  <g id="week-{w["week"]}">' )
        # Branch line
        svg_lines.append(f'    <path d="M {conn_x1} {y_node} L {conn_x2} {y_node}" stroke="{cfg["border"]}" stroke-width="3" stroke-dasharray="{"none" if w["status_code"] != "scheduled" else "6,4"}" stroke-linecap="round" />')
        
        # Central Node on the trunk
        node_radius = 12 if not w["is_star"] else 15
        svg_lines.append(f'    <circle cx="{center_x}" cy="{y_node}" r="{node_radius + 4}" fill="{cfg["node_glow"]}" opacity="0.3" filter="url(#glow)" />')
        svg_lines.append(f'    <circle cx="{center_x}" cy="{y_node}" r="{node_radius}" fill="#0F172A" stroke="{cfg["border"]}" stroke-width="3" />')
        svg_lines.append(f'    <circle cx="{center_x}" cy="{y_node}" r="5" fill="{cfg["border"]}" />')

        # Card container with ForeignObject for clean multi-line HTML formatting
        border_glow = f'border: 2px solid {cfg["border"]}; box-shadow: 0 0 15px {cfg["border"]}33;' if (w["is_star"] or w["status_code"] == "progress") else f'border: 1px solid {cfg["border"]}66;'
        star_badge = '<span style="background:#F59E0B; color:#000; font-size:11px; font-weight:800; padding:2px 6px; border-radius:4px; margin-left:6px;">KEY MILESTONE 🌟</span>' if w["is_star"] else ''

        items_html = ""
        for itm in w["summary"]:
            items_html += f'''
            <div style="display: flex; align-items: flex-start; gap: 8px; margin-bottom: 5px; font-size: 12.5px; line-height: 1.35; color: #E2E8F0;">
                <span style="font-size: 14px; flex-shrink: 0; margin-top: 1px;">{itm["icon"]}</span>
                <div>
                    <strong style="color: #94A3B8; font-size: 11.5px; text-transform: uppercase;">[{itm["cat"]}]</strong>
                    <span> {itm["text"]}</span>
                </div>
            </div>
            '''

        fo_html = f'''
        <div xmlns="http://www.w3.org/1999/xhtml" style="
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
            border-radius: 14px;
            {border_glow}
            padding: 14px 18px;
            box-sizing: border-box;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            font-family: system-ui, -apple-system, sans-serif;
            color: #F8FAFC;
        ">
            <!-- Header bar of card -->
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid rgba(148, 163, 184, 0.2);">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="background: {cfg['badge_bg']}; color: {cfg['badge_text']}; font-weight: 800; font-size: 12px; padding: 3px 8px; border-radius: 6px; letter-spacing: 0.5px;">
                        {w['week_label']}
                    </span>
                    <span style="font-size: 12px; color: #94A3B8; font-family: monospace;">📅 {w['dates']}</span>
                    {star_badge}
                </div>
                <div>
                    <span style="background: {cfg['badge_bg']}; color: {cfg['badge_text']}; border: 1px solid {cfg['border']}; font-size: 10.5px; font-weight: 700; padding: 2px 7px; border-radius: 12px;">
                        {cfg['label']}
                    </span>
                </div>
            </div>

            <!-- Milestone Title -->
            <div style="margin-bottom: 8px;">
                <div style="font-size: 14px; font-weight: 700; color: #38BDF8; line-height: 1.3;">
                    {w['milestone']}
                </div>
                <div style="font-size: 11px; color: #64748B; font-style: italic;">
                    {w['milestone_en']}
                </div>
            </div>

            <!-- Deliverables List -->
            <div style="flex: 1; overflow: hidden;">
                {items_html}
            </div>
        </div>
        '''

        svg_lines.append(f'    <foreignObject x="{card_x}" y="{y_node - (card_h // 2)}" width="{card_w}" height="{card_h}" filter="url(#cardShadow)">')
        svg_lines.append(fo_html)
        svg_lines.append('    </foreignObject>')
        svg_lines.append('  </g>\n')

    # Footer section
    svg_lines.extend([
        '  <!-- FOOTER BANNER -->',
        f'  <g transform="translate(0, {height - 80})">',
        f'    <rect x="{center_x - 450}" y="0" width="900" height="50" rx="25" fill="#1E293B" stroke="#334155" stroke-width="1.5" />',
        f'    <text x="{center_x}" y="30" text-anchor="middle" font-size="14" font-weight="600" fill="#94A3B8">',
        '      🎯 Senior Capstone Project 2026 | Physical Modular Tangible Programming Blocks for Robosen K1 Robot',
        '    </text>',
        '  </g>',
        '</svg>'
    ])

    return "\n".join(svg_lines)

def generate_html():
    html_content = f'''<!DOCTYPE html>
<html lang="th">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Robosen Block Project — 14-Week Master Timeline Infographic</title>
    <style>
        :root {{
            --bg-color: #0B1120;
            --card-bg: rgba(15, 23, 42, 0.85);
            --card-border: #334155;
            --text-main: #F8FAFC;
            --text-sub: #94A3B8;
            --done-color: #10B981;
            --done-bg: rgba(6, 78, 59, 0.4);
            --progress-color: #F59E0B;
            --progress-bg: rgba(120, 53, 15, 0.4);
            --scheduled-color: #38BDF8;
            --scheduled-bg: rgba(14, 116, 144, 0.3);
            --star-color: #EC4899;
        }}

        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            padding: 40px 20px;
            line-height: 1.5;
            background-image: radial-gradient(rgba(56, 189, 248, 0.05) 1px, transparent 0);
            background-size: 32px 32px;
        }}

        .container {{
            max-width: 1440px;
            margin: 0 auto;
        }}

        /* Header */
        header {{
            text-align: center;
            margin-bottom: 50px;
        }}

        .project-badge {{
            display: inline-block;
            background: rgba(56, 189, 248, 0.15);
            color: #38BDF8;
            padding: 6px 16px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 2px;
            margin-bottom: 12px;
            border: 1px solid rgba(56, 189, 248, 0.3);
            text-transform: uppercase;
        }}

        h1 {{
            font-size: 38px;
            font-weight: 900;
            background: linear-gradient(135deg, #38BDF8, #818CF8, #C084FC);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 12px;
        }}

        p.subtitle {{
            font-size: 16px;
            color: var(--text-sub);
            max-width: 760px;
            margin: 0 auto 24px;
        }}

        /* Controls / Filter Bar */
        .controls {{
            display: flex;
            justify-content: center;
            gap: 12px;
            margin-bottom: 40px;
            flex-wrap: wrap;
        }}

        .filter-btn {{
            background: #1E293B;
            border: 1px solid #334155;
            color: var(--text-sub);
            padding: 8px 18px;
            border-radius: 8px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: #38BDF8;
            color: #0F172A;
            border-color: #38BDF8;
        }}

        /* Central Timeline Container */
        .timeline {{
            position: relative;
            padding: 20px 0;
            margin: 0 auto;
        }}

        /* Central Spine Line */
        .timeline::before {{
            content: '';
            position: absolute;
            top: 0;
            bottom: 0;
            left: 50%;
            width: 4px;
            transform: translateX(-50%);
            background: linear-gradient(to bottom, #10B981 0%, #10B981 25%, #F59E0B 32%, #38BDF8 60%, #818CF8 100%);
            border-radius: 2px;
            box-shadow: 0 0 12px rgba(56, 189, 248, 0.3);
        }}

        /* Timeline Items (Nodes & Cards) */
        .timeline-item {{
            position: relative;
            width: 50%;
            margin-bottom: 40px;
            box-sizing: border-box;
        }}

        .timeline-item.left {{
            left: 0;
            padding-right: 55px;
        }}

        .timeline-item.right {{
            left: 50%;
            padding-left: 55px;
        }}

        /* Central Node Dots */
        .timeline-node {{
            position: absolute;
            top: 28px;
            width: 22px;
            height: 22px;
            border-radius: 50%;
            background: #0F172A;
            border: 4px solid var(--scheduled-color);
            box-shadow: 0 0 10px rgba(56, 189, 248, 0.5);
            z-index: 2;
        }}

        .timeline-item.left .timeline-node {{
            right: -11px;
        }}

        .timeline-item.right .timeline-node {{
            left: -11px;
        }}

        .timeline-item.status-done .timeline-node {{
            border-color: var(--done-color);
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.6);
        }}

        .timeline-item.status-progress .timeline-node {{
            border-color: var(--progress-color);
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.8);
            animation: pulse 1.8s infinite;
        }}

        @keyframes pulse {{
            0% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0.7); }}
            70% {{ transform: scale(1.15); box-shadow: 0 0 0 10px rgba(245, 158, 11, 0); }}
            100% {{ transform: scale(1); box-shadow: 0 0 0 0 rgba(245, 158, 11, 0); }}
        }}

        /* Connecting Horizontal Branch */
        .timeline-branch {{
            position: absolute;
            top: 37px;
            height: 2px;
            background: var(--card-border);
            z-index: 1;
        }}

        .timeline-item.left .timeline-branch {{
            right: 0;
            width: 55px;
            background: linear-gradient(to left, var(--scheduled-color), transparent);
        }}

        .timeline-item.right .timeline-branch {{
            left: 0;
            width: 55px;
            background: linear-gradient(to right, var(--scheduled-color), transparent);
        }}

        .timeline-item.status-done.left .timeline-branch {{ background: linear-gradient(to left, var(--done-color), transparent); }}
        .timeline-item.status-done.right .timeline-branch {{ background: linear-gradient(to right, var(--done-color), transparent); }}
        .timeline-item.status-progress.left .timeline-branch {{ background: linear-gradient(to left, var(--progress-color), transparent); }}
        .timeline-item.status-progress.right .timeline-branch {{ background: linear-gradient(to right, var(--progress-color), transparent); }}

        /* Card Style */
        .timeline-card {{
            background: var(--card-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--card-border);
            border-radius: 16px;
            padding: 22px 24px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease;
        }}

        .timeline-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 35px -5px rgba(0, 0, 0, 0.7);
        }}

        .timeline-item.status-done .timeline-card {{
            border-color: rgba(16, 185, 129, 0.35);
        }}
        .timeline-item.status-done .timeline-card:hover {{
            border-color: var(--done-color);
        }}

        .timeline-item.status-progress .timeline-card {{
            border: 2px solid var(--progress-color);
            box-shadow: 0 0 20px rgba(245, 158, 11, 0.2);
        }}

        .timeline-item.is-milestone .timeline-card {{
            border: 2px solid #818CF8;
            box-shadow: 0 0 20px rgba(129, 140, 248, 0.25);
        }}

        /* Card Header */
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding-bottom: 10px;
            border-bottom: 1px solid rgba(148, 163, 184, 0.15);
        }}

        .week-pill {{
            font-size: 12px;
            font-weight: 800;
            letter-spacing: 1px;
            padding: 4px 10px;
            border-radius: 6px;
            background: #1E293B;
            color: #38BDF8;
        }}

        .date-badge {{
            font-size: 12px;
            color: var(--text-sub);
            font-family: ui-monospace, SFMono-Regular, monospace;
        }}

        .status-tag {{
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
        }}

        .status-tag.done {{
            background: var(--done-bg);
            color: var(--done-color);
            border: 1px solid var(--done-color);
        }}

        .status-tag.progress {{
            background: var(--progress-bg);
            color: var(--progress-color);
            border: 1px solid var(--progress-color);
        }}

        .status-tag.scheduled {{
            background: var(--scheduled-bg);
            color: var(--scheduled-color);
            border: 1px solid rgba(56, 189, 248, 0.4);
        }}

        /* Milestone Focus Title */
        .milestone-title {{
            font-size: 16px;
            font-weight: 700;
            color: #38BDF8;
            margin-bottom: 4px;
            line-height: 1.4;
        }}

        .milestone-en {{
            font-size: 12px;
            color: var(--text-sub);
            font-style: italic;
            margin-bottom: 14px;
        }}

        /* Deliverables Checklist */
        .deliverables-list {{
            list-style: none;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .deliverable-item {{
            display: flex;
            align-items: flex-start;
            gap: 10px;
            font-size: 13px;
            color: #CBD5E1;
            line-height: 1.4;
        }}

        .deliverable-icon {{
            font-size: 14px;
            flex-shrink: 0;
            margin-top: 1px;
        }}

        .deliverable-cat {{
            color: #94A3B8;
            font-size: 11px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-right: 4px;
        }}

        /* Responsive Layout for Mobile / Tablet */
        @media (max-width: 900px) {{
            .timeline::before {{
                left: 30px;
            }}

            .timeline-item {{
                width: 100%;
                left: 0 !important;
                padding-left: 70px !important;
                padding-right: 0 !important;
            }}

            .timeline-node {{
                left: 19px !important;
                right: auto !important;
            }}

            .timeline-branch {{
                left: 30px !important;
                right: auto !important;
                width: 40px !important;
                background: linear-gradient(to right, var(--scheduled-color), transparent) !important;
            }}
        }}

        /* Print optimization */
        @media print {{
            body {{
                background: #FFFFFF !important;
                color: #000000 !important;
            }}
            .timeline-card {{
                background: #FFFFFF !important;
                border: 1px solid #CCCCCC !important;
                box-shadow: none !important;
            }}
            .controls {{ display: none; }}
        }}
    </style>
</head>
<body>

<div class="container">
    <header>
        <div class="project-badge">Robosen K1 Physical Modular Blocks</div>
        <h1>14-Week Project Master Timeline</h1>
        <p class="subtitle">Single-line Spine with Weekly Deliverable Branches (โฟกัสตัวงานและผลลัพธ์ของแต่ละสัปดาห์ ไม่ระบุชื่อบุคคลตามแผนงาน 14 สัปดาห์)</p>
        <div class="controls">
            <button class="filter-btn active" onclick="filterTimeline('all')">ทั้งหมด (All 14 Weeks)</button>
            <button class="filter-btn" onclick="filterTimeline('done')">✅ เสร็จสิ้นแล้ว (W1 - W3)</button>
            <button class="filter-btn" onclick="filterTimeline('progress')">⚡ กำลังดำเนินการ (W4)</button>
            <button class="filter-btn" onclick="filterTimeline('scheduled')">📅 แผนงานถัดไป (W5 - W14)</button>
            <button class="filter-btn" onclick="window.print()">🖨️ พิมพ์ / บันทึก PDF</button>
        </div>
    </header>

    <div class="timeline">
'''
    for idx, w in enumerate(weeks_data):
        side = "left" if (w["week"] % 2 != 0) else "right"
        status_class = f"status-{w['status_code']}"
        milestone_class = "is-milestone" if w["is_star"] else ""

        items_li = ""
        for itm in w["summary"]:
            items_li += f'''
                <li class="deliverable-item">
                    <span class="deliverable-icon">{itm["icon"]}</span>
                    <div>
                        <span class="deliverable-cat">[{itm["cat"]}]</span>
                        <span>{itm["text"]}</span>
                    </div>
                </li>
            '''

        star_tag = '<span style="background:#EC4899; color:#fff; font-size:10px; font-weight:800; padding:2px 6px; border-radius:4px; margin-left:6px;">STAR MILESTONE 🌟</span>' if w["is_star"] else ''

        html_content += f'''
        <!-- WEEK {w["week"]} -->
        <div class="timeline-item {side} {status_class} {milestone_class}" data-status="{w["status_code"]}">
            <div class="timeline-node"></div>
            <div class="timeline-branch"></div>
            <div class="timeline-card">
                <div class="card-header">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span class="week-pill">{w["week_label"]}</span>
                        <span class="date-badge">📅 {w["dates"]}</span>
                        {star_tag}
                    </div>
                    <span class="status-tag {w["status_code"]}">{w["status"]}</span>
                </div>
                <div class="milestone-title">{w["milestone"]}</div>
                <div class="milestone-en">{w["milestone_en"]}</div>
                <ul class="deliverables-list">
                    {items_li}
                </ul>
            </div>
        </div>
        '''

    html_content += '''
    </div>
</div>

<script>
    function filterTimeline(filter) {
        document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
        if (event && event.target) {
            event.target.classList.add('active');
        }
        const items = document.querySelectorAll('.timeline-item');
        items.forEach(item => {
            if (filter === 'all' || item.getAttribute('data-status') === filter) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }
</script>

</body>
</html>
'''
    return html_content

def generate_markdown_timeline():
    md = [
        "# Robosen Block Project — 14-Week Master Timeline Infographic",
        "",
        "> **Project Focus**: Physical Modular Programming Blocks for Robosen K1 Robot  ",
        "> **Source Plan**: [14 Weeks Plan Google Spreadsheet](https://docs.google.com/spreadsheets/u/1/d/1kW47Z_EtlDmrVkeLjoNJkVM2ukwHJniR2-91o9h_9HM/htmlview)  ",
        "> **Format**: Single-Line Central Spine with Weekly Deliverable Branches (Strictly task & deliverable focused, excluding individual member assignments)  ",
        "",
        "---",
        "",
        "## 1. Visual Flowchart / Diagram (Mermaid)",
        "",
        "```mermaid",
        "flowchart TD",
        "    classDef done fill:#064E3B,stroke:#10B981,stroke-width:2px,color:#fff;",
        "    classDef progress fill:#78350F,stroke:#F59E0B,stroke-width:3px,color:#fff;",
        "    classDef scheduled fill:#1E293B,stroke:#38BDF8,stroke-width:2px,color:#fff;",
        "    classDef star fill:#831843,stroke:#EC4899,stroke-width:3px,color:#fff;",
        "    classDef spine fill:#0F172A,stroke:#38BDF8,stroke-width:4px,color:#38BDF8;",
        "",
        "    START([🎯 Project Kickoff: 16/08/2026]):::spine --> W1_NODE((W1)):::done",
        "    W1_NODE --> W1_CARD[\"<b>Week 1</b> (16/08 - 22/08)<br/><b>วางรากฐานระบบ & BLE</b><br/>• โครงสร้างจ่ายไฟ & หน้าสัมผัส<br/>• ถอดรหัส BLE เบื้องต้น<br/>• สัดส่วนเคส & สรีรศาสตร์เด็ก\"]:::done",
        "",
        "    W1_NODE --> W2_NODE((W2)):::done",
        "    W2_NODE --> W2_CARD[\"<b>Week 2</b> (23/08 - 29/08)<br/><b>ถอดรหัสคำสั่งหุ่นยนต์ครบวงจร</b><br/>• 25+ คำสั่งขั้นสูง & ACK<br/>• BOM ต้นแบบ & ขนาดจริง<br/>• โฟลว์ Dock-to-Chain-to-Run\"]:::done",
        "",
        "    W2_NODE --> W3_NODE((W3)):::done",
        "    W3_NODE --> W3_CARD[\"<b>Week 3</b> (30/08 - 05/09)<br/><b>โปรแกรมควบคุมหลัก & สรุป BOM</b><br/>• Master Auto-BLE Scan<br/>• Rotary Debounce & Clamping<br/>• แผนภาพโฟลว์ระบบสมบูรณ์\"]:::done",
        "",
        "    W3_NODE --> W4_NODE((W4)):::progress",
        "    W4_NODE --> W4_CARD[\"<b>Week 4</b> (06/09 - 12/09)<br/><b>ผังวงจรไฟฟ้า & โมเดล 3D</b><br/>• วงจร Master, Action, End<br/>• 3D Polarized Keying & Light Pipe<br/>• ทดสอบสั่งงานหุ่นยนต์จริง BLE\"]:::progress",
        "",
        "    W4_NODE --> W5_NODE((W5)):::scheduled",
        "    W5_NODE --> W5_CARD[\"<b>Week 5</b> (13/09 - 19/09)<br/><b>แผ่นวงจรพิมพ์ PCB & ชิ้นงานทดสอบ</b><br/>• PCB Layout ทั้ง 3 บล็อก<br/>• Action Block Flash Firmware<br/>• พิมพ์ 3D เคสทดสอบความกระชับ\"]:::scheduled",
        "",
        "    W5_NODE --> W6_NODE((W6)):::scheduled",
        "    W6_NODE --> W6_CARD[\"<b>Week 6</b> (20/09 - 26/09)<br/><b>สั่งผลิต PCB & กราฟิก OLED</b><br/>• ส่งผลิต PCB & ซื้อแม่เหล็ก N52/Pogo<br/>• กราฟิกไอคอนขนาดใหญ่บนจอ OLED<br/>• สเตรสเทสโปรเซสเซอร์ 100 รอบ\"]:::scheduled",
        "",
        "    W6_NODE --> W7_NODE((W7 🎯)):::star",
        "    W7_NODE --> W7_CARD[\"<b>Week 7</b> (27/09 - 03/10) ⭐<br/><b>ประเมินผลกลางภาค (Midterm)</b><br/>• พิมพ์เคส 3D ชุดจริง 5 บล็อก<br/>• รวม State Machine UI & Dock<br/>• สอบและนำเสนอประเมินผลกลางภาค\"]:::star",
        "",
        "    W7_NODE --> W8_NODE((W8)):::scheduled",
        "    W8_NODE --> W8_CARD[\"<b>Week 8</b> (04/10 - 10/10)<br/><b>ประกอบ บัดกรี & ระบบไฟ</b><br/>• SMT/THT Soldering ครบชิ้นส่วน<br/>• ขัดผิวเคส & Dry-fit แผงวงจร<br/>• ทดสอบความปลอดภัยระบบจ่ายไฟ\"]:::scheduled",
        "",
        "    W8_NODE --> W9_NODE((W9)):::scheduled",
        "    W9_NODE --> W9_CARD[\"<b>Week 9</b> (11/10 - 17/10)<br/><b>แฟลชบอร์ดจริง & แท่นตั้งค่า Dock</b><br/>• แฟลชเฟิร์มแวร์ลง 4 บล็อกคำสั่ง<br/>• ทดสอบแท่นตั้งค่า Dock + LED ACK<br/>• ตรวจวัด Signal Integrity ด้วย Scope\"]:::scheduled",
        "",
        "    W9_NODE --> W10_NODE((W10 🤖)):::star",
        "    W10_NODE --> W10_CARD[\"<b>Week 10</b> (18/10 - 24/10) ⭐<br/><b>ประกอบ 5 บล็อก & สั่งหุ่นยนต์ครบวงจร</b><br/>• ติดตั้งแบตเตอรี่ & สวิตช์ปิด-เปิด<br/>• ประกอบเสร็จสมบูรณ์ทั้ง 5 บล็อก<br/>• ทดสอบ Dock->Chain->Run สั่ง K1 สำเร็จ\"]:::star",
        "",
        "    W10_NODE --> W11_NODE((W11)):::scheduled",
        "    W11_NODE --> W11_CARD[\"<b>Week 11</b> (25/10 - 31/10)<br/><b>Drop Test, E-Stop & ซ้อมใหญ่</b><br/>• ทดสอบตกกระแทก Drop Test 1 ม.<br/>• E-Stop ปลดบล็อกแล้วหุ่นหยุดทันที<br/>• ซักซ้อมขั้นตอนทดสอบภาคสนาม\"]:::scheduled",
        "",
        "    W11_NODE --> W12_NODE((W12 🌟)):::star",
        "    W12_NODE --> W12_CARD[\"<b>Week 12</b> (01/11 - 07/11) 🌟<br/><b>ทดสอบกับผู้ใช้จริง (Usability Pilot)</b><br/>• จัดกิจกรรมให้เด็กลองต่อบล็อกอิสระ<br/>• เก็บสถิติเวลา ความเข้าใจ & ความพึงพอใจ<br/>• ติดตาม telemetry & สัญญาณ BLE สด\"]:::star",
        "",
        "    W12_NODE --> W13_NODE((W13)):::scheduled",
        "    W13_NODE --> W13_CARD[\"<b>Week 13</b> (08/11 - 14/11)<br/><b>ปรับปรุงตามฟีดแบ็ก & ความเสถียร</b><br/>• เพิ่มลายกันลื่นลูกบิด & มุมต่อเคส<br/>• จูนความลื่นไหลลูกบิด & คอนทราสต์ไอคอน<br/>• รันผสมผสาน 50+ รอบไร้ความผิดพลาด\"]:::scheduled",
        "",
        "    W13_NODE --> W14_NODE((W14 🏆)):::star",
        "    W14_NODE --> W14_CARD[\"<b>Week 14</b> (15/11 - 21/11) 🏆<br/><b>ส่งมอบสมบูรณ์, วิดีโอ & สอบป้องกัน</b><br/>• Release v1.0.0 Code & Hardware Pack<br/>• ถ่ายทำวิดีโอสาธิตผลิตภัณฑ์ครบวงจร<br/>• สาธิตสดและสอบป้องกันโครงงานปริญญานิพนธ์\"]:::star",
        "",
        "    W14_NODE --> FINISH([🏁 Project Completion & Defense: 21/11/2026]):::spine",
        "```",
        "",
        "---",
        "",
        "## 2. Week-by-Week Executive Deliverables Breakdown",
        "",
        "| สัปดาห์ (Week) | ช่วงวันที่ (Date Range) | สถานะ (Status) | เป้าหมายหลัก (Weekly Focus) | ผลงาน & กิจกรรมสำคัญ (Deliverables) |",
        "| :--- | :--- | :--- | :--- | :--- |"
    ]

    for w in weeks_data:
        deliv_lines = "<br/>".join([f"• <b>[{item['cat']}]</b> {item['text']}" for item in w['summary']])
        star = " 🌟" if w['is_star'] else ""
        md.append(f"| **{w['week_label']}{star}** | `{w['dates']}` | `{w['status']}` | **{w['milestone']}**<br/>*{w['milestone_en']}* | {deliv_lines} |")

    md.extend([
        "",
        "---",
        "",
        "## 3. Dedicated Deliverable Assets",
        "- **Vector Infographic (SVG)**: [`docs/diagrams/project_timeline_infographic.svg`](file:///C:/Users/nnnn/Projects/robosen_block/docs/diagrams/project_timeline_infographic.svg)",
        "- **Interactive Web Infographic (HTML)**: [`docs/diagrams/project_timeline_infographic.html`](file:///C:/Users/nnnn/Projects/robosen_block/docs/diagrams/project_timeline_infographic.html)",
        "- **Project Plan Document (Markdown)**: [`plans/TIMELINE_INFOGRAPHIC.md`](file:///C:/Users/nnnn/Projects/robosen_block/plans/TIMELINE_INFOGRAPHIC.md)"
    ])

    return "\n".join(md)

# Run generator
os.makedirs("C:/Users/nnnn/Projects/robosen_block/docs/diagrams", exist_ok=True)
os.makedirs("C:/Users/nnnn/Projects/robosen_block/plans", exist_ok=True)

svg_str = generate_svg()
with open("C:/Users/nnnn/Projects/robosen_block/docs/diagrams/project_timeline_infographic.svg", "w", encoding="utf-8") as f:
    f.write(svg_str)

html_str = generate_html()
with open("C:/Users/nnnn/Projects/robosen_block/docs/diagrams/project_timeline_infographic.html", "w", encoding="utf-8") as f:
    f.write(html_str)

md_str = generate_markdown_timeline()
with open("C:/Users/nnnn/Projects/robosen_block/plans/TIMELINE_INFOGRAPHIC.md", "w", encoding="utf-8") as f:
    f.write(md_str)

print("Generated all files successfully:")
print("1. docs/diagrams/project_timeline_infographic.svg")
print("2. docs/diagrams/project_timeline_infographic.html")
print("3. plans/TIMELINE_INFOGRAPHIC.md")
