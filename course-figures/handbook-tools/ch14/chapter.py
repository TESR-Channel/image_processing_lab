# Chapter 14 handbook v4 - QC with two AIs, done with the TESR tools only:
# AI Vision Trainer (label + crop) -> yolo-trainer (train) -> ROI Studio (two AIs, count -> OK/NG)
# -> runner on the PC / Pi / Jetson -> Node-RED. Every picture of output is a real run
# (ROI Studio v1.9.1, AI Vision Trainer v3.3.0, runner v1.9.1, 2026-11-11).

IMG = ("https://raw.githubusercontent.com/TESR-Channel/image_processing_lab/"
       "course-figures/course-figures/handbook14/v7/")
TRAINER = "https://tesr-channel.github.io/AI_vision_Trainer/"
STUDIO = "https://tesr-channel.github.io/AI_ROI_Designer/"

# measured on all 30 photos (11 OK, 19 NG); "right" = OK/NG right AND the screw count = hand count
RESULT_ROWS = [
    ["ของสำเร็จ `terminal_qc/`", "YOLO 2 ตัว (ตัวอย่าง)", "**30/30**", "**30/30**"],
    ["เทรนเองจาก 2 โปรเจกต์ใน `from_web/`", "yolo-trainer ตามขั้นที่ 8", "**30/30**", "**30/30**"],
    ["AI #2 ด้วย 🧠 Train Now บนเว็บ", "Trainer v3.2.0 (ตาราง 7×7)", "นับถูก **0 จาก 10**", "—"],
]


def link(url, label):
    """A real hyperlink: the label, then the address so it also works on paper."""
    return ('<a href="%s"><span style="color:#2563eb;font-weight:700;text-decoration:underline">%s</span></a>'
            ' (%s)' % (url, label, url.replace("https://", "").rstrip("/")))


def build(b):
    p = []
    p.append(b.header("พิเศษ", "QC ด้วย AI 2 ชั้น: นับน็อตเทอร์มินัล",
                      "<b>AI #1</b> หาเทอร์มินัล → ตัดกรอบ → <b>AI #2</b> นับหัวน็อตข้างใน → "
                      "ครบ 8 = <b style='color:#15803d'>OK</b> · ขาด = <b style='color:#b91c1c'>NG</b> "
                      "· ใช้เครื่องมือ TESR 2 ตัว ไม่ต้องเขียนโค้ด"))
    p.append(b.image(IMG + "tb2_problem.jpg", "OK กับ NG", width=560))
    p.append(b.para("🧠 " + link(TRAINER, "AI Vision Trainer") + " — ตีกรอบ + ✂ ตัดรูปตามกรอบ (ขั้นที่ 5–7)",
                    space_after=2))
    p.append(b.para("🎯 " + link(STUDIO, "ROI Studio") + " — AI 2 ชั้น นับแล้วตัดสิน OK / NG (ขั้นที่ 3, 9–12)",
                    space_after=6))
    p.append(b.image(IMG + "tb2_route.png", "เส้นทางของบทนี้"))

    # ------------------------------------------------------------------ concept
    p.append(b.step("1", "แนวคิด: หาวัตถุก่อน แล้วนับชิ้นส่วนข้างใน"))
    p.append(b.image(IMG + "tb2_concept.png", "4 ขั้นของ AI 2 ชั้น"))
    p.append(b.table(["ทำไมต้อง 2 ชั้น", "เพราะ"], [
        ["หัวน็อตเล็กมากในรูปเต็ม", "ตัดเฉพาะเทอร์มินัลออกมาก่อน AI #2 จะเห็นหัวน็อตชัด"],
        ["ชิ้นงานวางตรงไหนก็ได้", "AI #1 ตามหาให้ ไม่ต้องมีจิ๊ก"],
        ["งานอื่นใช้วิธีเดิม", "รีเลย์ 4 น็อต · แผง 10 น็อต · ถาด 30 ช่อง — เปลี่ยนแค่ 2 โมเดลกับตัวเลข"],
    ]))

    # ------------------------------------------------------------------ folder + install
    p.append(b.step("2", "เตรียมโฟลเดอร์ และติดตั้ง"))
    p.append(b.image(IMG + "tb2_folder.png", "โฟลเดอร์บทนี้", width=560))
    p.append(b.table(["เครื่อง", "ดับเบิลคลิก / พิมพ์"], [
        ["Windows", "`install\\install_windows.bat`"],
        ["Mac / Linux", "`bash install/install_linux.sh`"],
        ["Raspberry Pi", "`bash install/install_pi.sh`"],
        ["Jetson", "`bash install/install_jetson.sh`"],
    ]))
    p.append(b.code_block([
        ("source venv/bin/activate", "# Mac / Linux / Pi / Jetson"),
        ("venv\\Scripts\\activate", "# Windows"),
    ]))
    p.append(b.callout("ขั้นที่ 3–11 ทำบนเว็บ ไม่ต้องติดตั้งอะไร · ติดตั้งไว้ใช้ตอนรันจริง (ขั้นที่ 12–14)"))

    # ------------------------------------------------------------------ try the finished one
    p.append(b.step("3", "ลองของสำเร็จก่อน บน ROI Studio"))
    p.append(b.table(["ทำ", "บนหน้าเว็บ ROI Studio"], [
        ["① เปิดโปรเจกต์", "**นำเข้า config** → เข้าโฟลเดอร์ `terminal_qc` → **Ctrl+A** เลือกทุกไฟล์ → Open"],
        ["② ใส่รูป", "**โหลดรูปจากเครื่อง** → `image/Terminal/ng` → **Ctrl+A** (เลือกได้หลายรูป)"],
        ["③ ไล่ดู", "กด **▶** หรือปุ่มลูกศร → ทุกกรอบอ่านใหม่ให้เอง"],
    ]))
    p.append(b.image(IMG + "tb2_step_ng.jpg", "รูปที่ 19 จาก 30: NG 5/8", width=520))
    p.append(b.callout("กรอบ **แดง = NG** · **เขียว = OK** · วงกลมเขียว = หัวน็อตที่ AI #2 เจอ · ผลบนเว็บคือค่าประมาณ "
                       "ตัวเลขจริงคือที่ runner พิมพ์ (ขั้นที่ 12)"))

    # ------------------------------------------------------------------ photos
    p.append(b.step("4", "ถ่ายรูปชิ้นงาน"))
    p.append(b.para("ในบทนี้มีให้แล้ว 30 รูปใน <b>image/Terminal</b> (ok 11 · ng 19) — งานของคุณเองถ่ายตามตารางนี้"))
    p.append(b.table(["ถ่ายแบบนี้", "เพราะ"], [
        ["ชิ้น **ดี** และชิ้น **เสีย** ทุกแบบที่เจอจริง", "AI #2 ต้องเคยเห็นรูว่างทุกตำแหน่ง"],
        ["หลายมุม หลายตำแหน่ง หลายแสง", "AI #1 หาชิ้นงานได้ทุกที่ที่มันวาง"],
        ["กล้องตัวเดียวกับตอนใช้งาน", "ภาพตอนเทรนต้องเหมือนภาพตอนใช้"],
        ["โต๊ะเปล่า มือ ของอื่น", "ใส่เป็น **+ Background** ในขั้นที่ 5"],
    ]))
    p.append(b.callout("ถ่ายจากกล้องเว็บแคมได้เลยในหน้า AI Vision Trainer: กดค้าง **📸 Hold to Capture** แล้วขยับชิ้นงาน"))

    # ------------------------------------------------------------------ Trainer project 1
    p.append(b.step("5", "AI Vision Trainer โปรเจกต์ 1: กรอบ terminal"))
    p.append(b.image(IMG + "tb2_trainer1.jpg", "AI #1 บนเว็บ", width=560))
    p.append(b.table(["ทำ", "บนหน้าเว็บ"], [
        ["① ใส่รูป", "**Object Detection** → **+ Add Class** `terminal` → **Upload files** · "
                     "หรือ **📂 Load Project** `from_web/terminal_finder_project.zip` (ตีกรอบไว้แล้ว)"],
        ["② ตีกรอบ", "คลิกรูปขอบแดง → ลากกรอบรอบชิ้นงาน → **Enter**"],
        ["③ ไม่สนใจอะไร", "**+ Background** → รูปโต๊ะเปล่า มือ ของอื่น"],
        ["④ เก็บไว้", "**💾 Save Project**"],
    ]))
    p.append(b.callout("อย่าหมุนกรอบ (Q / E) — กรอบหมุนทำให้ชุดข้อมูลเป็น OBB ซึ่งขั้นถัดไปไม่ใช้", kind="warn"))

    # ------------------------------------------------------------------ crop
    p.append(b.step("6", "✂ ตัดรูปตามกรอบ → โปรเจกต์ใหม่"))
    p.append(b.para("ปุ่ม <b>✂ ตัดรูปตามกรอบ</b> อยู่ข้าง <b>Download Dataset (YOLO)</b> — "
                    "ตัดทุกกรอบ terminal ออกมาเป็นรูปใหม่ ไม่ต้องรันโปรแกรมเอง", space_after=4))
    p.append(b.image(IMG + "tb2_crop_dialog.png", "หน้าต่างตัดรูปตามกรอบ", width=420))
    p.append(b.table(["เลือก", "ค่า"], [
        ["คลาสที่จะตัด", "`terminal`"],
        ["ขอบเผื่อรอบกรอบ", "**10%** — ใช้ค่าเดียวกันใน ROI Studio (ขั้นที่ 10)"],
        ["กดปุ่ม", "**▶ เริ่มโปรเจกต์ใหม่จากรูปที่ตัด** → **💾 บันทึกโปรเจกต์ 1 แล้วเริ่มใหม่**"],
    ]))

    # ------------------------------------------------------------------ Trainer project 2
    p.append(b.step("7", "AI Vision Trainer โปรเจกต์ 2: กรอบหัวน็อตทุกตัว"))
    p.append(b.image(IMG + "tb2_new_project.png", "รูปที่ตัดแล้ว รอใส่คลาส", width=520))
    p.append(b.table(["ทำ", "บนหน้าเว็บ"], [
        ["① ตั้งชื่อคลาส", "พิมพ์ `screw` → **+ Add Class** → รูปที่ตัดทั้งหมดเข้าคลาสนี้"],
        ["② ตีกรอบ **ทุกหัวน็อต**", "ลากกรอบ → ลากอีกที่ **ที่ว่าง** = กรอบถัดไป · ครบแล้ว **Enter** · รูว่าง **ไม่ต้อง** ตี"],
        ["③ Background", "รูปซูมรูว่าง + พื้นโต๊ะ"],
        ["④ เก็บไว้", "**💾 Save Project** · ทางลัด: `from_web/terminal_screws_project.zip` ตีกรอบไว้แล้ว"],
    ]))
    p.append(b.image(IMG + "tb2_label_screw.png", "8 กรอบในรูปเดียว", width=300))

    # ------------------------------------------------------------------ train
    p.append(b.step("8", "เทรน 2 โมเดลด้วย yolo-trainer"))
    p.append(b.para("ทั้ง 2 โปรเจกต์: <b>⬇ Download Dataset (YOLO)</b> → แตก zip → เอา <b>dataset/</b> "
                    "ไปไว้ข้าง <b>train.py</b> ในโฟลเดอร์ <b>yolo-trainer</b> (ลิงก์อยู่ใน START_HERE.md ใน zip)",
                    space_after=4))
    p.append(b.code_block([
        ("pip install -r requirements.txt \"onnx<2\" onnxslim", "# ครั้งแรก"),
        ("python train.py --imgsz 416 --epochs 100", "# โปรเจกต์ 1"),
        ("python train.py --imgsz 320", "# โปรเจกต์ 2"),
        ("python export.py --target onnx", "# ได้ best.onnx"),
    ]))
    p.append(b.table(["โปรเจกต์", "เปลี่ยนชื่อ best.onnx เป็น"], [
        ["1 · terminal", "`my_finder.onnx`"],
        ["2 · screw", "`my_checker.onnx`"],
    ]))
    p.append(b.callout("ทำไมไม่กด **🧠 Train Now**? ลองแล้ว: AI #2 นับถูก **0 จาก 10 รูป** — ตาราง 7×7 ของเว็บ "
                       "แยกหัวน็อตที่ชิดกันไม่ได้ · ทาง YOLO นับถูกทุกรูป (ตารางในขั้นที่ 11) · CPU 2 คอร์: โปรเจกต์ 1 ~9 นาที · โปรเจกต์ 2 ~7 นาที", kind="warn"))

    # ------------------------------------------------------------------ Studio: models
    p.append(b.step("9", "ROI Studio: เพิ่มโมเดล 2 ตัว"))
    p.append(b.para("แถบซ้าย <b>+ เพิ่มโมเดลที่เทรนแล้ว</b> → เลือก <b>my_finder.onnx</b> → <b>บันทึกโมเดล</b> "
                    "· ทำซ้ำกับ <b>my_checker.onnx</b>", space_after=4))
    p.append(b.image(IMG + "tb2_addmodel.png", "หน้าต่างเพิ่มโมเดล", width=520))
    p.append(b.callout("ชื่อคลาส ขนาดภาพ (416 / 320) อ่านจากไฟล์โมเดลให้เอง ไม่ต้องพิมพ์"))

    # ------------------------------------------------------------------ Studio: the region
    p.append(b.step("10", "ROI Studio: กรอบ “AI 2 ชั้น”"))
    p.append(b.table(["ทำ", "บนหน้าเว็บ"], [
        ["① สร้างกรอบ", "ช่องชนิดงานบนแถบเครื่องมือ → **AI 2 ชั้น: หาวัตถุ → นับชิ้นส่วน → OK/NG** → ลากบนรูป → **ใช้ทั้งภาพ**"],
        ["② AI #1", "โมเดล `my_finder` · คลาส `terminal`"],
        ["③ AI #2", "โมเดล `my_checker` · คลาส `screw`"],
        ["④ ครบกี่ชิ้น", "`8` · OK เมื่อนับได้ **พอดีเท่านี้** · conf 0.5 / 0.4 · เผื่อขอบ 0.1"],
    ]))
    p.append(b.image(IMG + "tb2_panel.jpg", "ตั้งค่ากรอบ AI 2 ชั้น", width=420))

    # ------------------------------------------------------------------ check all photos
    p.append(b.step("11", "ไล่ดูทุกรูป และผลจริง"))
    p.append(b.para("<b>โหลดรูปจากเครื่อง</b> → เลือกหลายรูป → <b>◀ ▶</b> — "
                    "รูปที่ผิดคือรูปที่ต้องถ่ายเพิ่มแล้วเทรนใหม่", space_after=4))
    p.append(b.image(IMG + "tb2_ng_ok.jpg", "NG 5/8 กับ OK 8/8", width=470))
    p.append(b.table(["AI #1 + AI #2", "เทรนแบบไหน", "บนเว็บ", "runner"], RESULT_ROWS))
    p.append(b.para("30 รูปใน image/Terminal · “ถูก” = OK/NG ถูก <b>และ</b> นับหัวน็อตตรงกับที่นับด้วยตา · "
                    "โปรเจกต์ใน from_web ใช้ 20 รูป อีก 10 รูป AI ไม่เคยเห็น", size=11, color="#475569"))

    # ------------------------------------------------------------------ export + run
    p.append(b.step("12", "ส่งออก แล้วรันบนคอม: ทั้งโฟลเดอร์"))
    p.append(b.para("ตั้งชื่อโปรเจกต์บนสุด → <b>ส่งออก config + Python</b> → ได้ zip: config + 2 โมเดล + "
                    "tesr_vision_runner.py → แตกไว้ในโฟลเดอร์บทนี้ (ของสำเร็จคือ <b>terminal_qc/</b>)", space_after=4))
    p.append(b.code_block([
        ("cd terminal_qc", ""),
        ("python tesr_vision_runner.py --config terminal_qc_config.json --image ../image/Terminal/ng", ""),
    ]))
    p.append(b.image(IMG + "tb2_run.png", "รัน 19 รูป", width=540))
    p.append(b.image(IMG + "tb2_records.jpg", "ภาพใน records/", width=400))

    # ------------------------------------------------------------------ live
    p.append(b.step("13", "กล้องสด / วิดีโอ / Pi / Jetson"))
    p.append(b.code_block([
        "python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0",
        "python tesr_vision_runner.py --config terminal_qc_config.json --camera file --source my_clip.mp4",
        "python3 tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0 --headless",
    ]))
    p.append(b.table(["อยากได้", "ใส่"], [
        ["กล้อง USB ตัวอื่น", "`--source 1` หรือ `--source 2`"],
        ["กล้องแพบน Pi / Jetson", "`--camera csi --source 0`"],
        ["กล้อง IP", "`--camera ip --source rtsp://...`"],
        ["ไม่มีจอ (SSH)", "`--headless`"],
        ["หน้าต่าง", "**q** = ออก · **s** = เก็บภาพ · **p** = ซ่อน/แสดงแผงผล"],
    ]))
    p.append(b.callout("บน Pi / Jetson ก๊อปทั้งโฟลเดอร์ `terminal_qc/` ไป แล้วรันคำสั่งเดิมด้วย `python3` "
                       "(ติดตั้งด้วย `install_pi.sh` / `install_jetson.sh`) · กล้องสดส่งผลเมื่อผลเปลี่ยน"))

    # ------------------------------------------------------------------ Node-RED
    p.append(b.step("14", "ส่งผลไป Node-RED"))
    p.append(b.para("Node-RED ที่มี broker อยู่แล้ว (flow บทที่ 12 หรือ 13) → <b>Import</b> "
                    "<b>node-red/qc_two_ai_flow.json</b> → <b>Deploy</b> แล้วรันพร้อม <b>--broker</b>", space_after=4))
    p.append(b.code_block([
        "python tesr_vision_runner.py --config terminal_qc_config.json --image ../image/Terminal/ng --broker localhost",
        "python tesr_vision_runner.py --config terminal_qc_config.json --camera usb --source 0 --broker 192.168.1.50",
    ]))
    p.append(b.para("ทุกผลมาที่ topic <b>tesr/vision/cam1/terminal_qc</b> (ข้อความจริง):", space_after=4))
    p.append(b.code_block([
        '{"roi": "terminal_qc", "value": {"result": "NG", "objects": 1,',
        ' "ok": 0, "ng": 1, "found": [7], "expect": 8}, "conf": 0.864}',
    ]))
    p.append(b.callout("โหนด **count OK / NG** นับให้ใต้โหนด เช่น `OK 11 · NG 19 (last NG 5 of 8)` · "
                       "กด **reset counts** เพื่อเริ่มนับใหม่"))

    # ------------------------------------------------------------------ SSR
    p.append(b.step("15", "รีเลย์ SSR: วิธีเดิม ตัวเลขใหม่"))
    p.append(b.table(["", "เทอร์มินัล", "รีเลย์ SSR"], [
        ["AI #1 หา", "`terminal`", "`ssr`"],
        ["AI #2 นับ", "`screw`", "`screw`"],
        ["ครบ = OK", "`8`", "`4`"],
        ["ของสำเร็จ", "`terminal_qc/`", "`ssr_qc/`"],
    ]))
    p.append(b.code_block([
        "cd ../ssr_qc",
        "python tesr_vision_runner.py --config ssr_qc_config.json --image ../image/SSR",
    ]))
    p.append(b.image(IMG + "tb2_ssr_run.png", "รัน 8 รูป", width=500))
    p.append(b.image(IMG + "tb2_ssr.jpg", "OK 4/4 · NG 3/4 · real_angle", width=540))

    # ------------------------------------------------------------------ limits + troubleshooting
    p.append(b.step("16", "ข้อจำกัด และติดปัญหา?"))
    p.append(b.table(["เห็นอะไร", "ทำอะไร"], [
        ["ไม่มีกรอบ (`none` / ไม่เจอวัตถุ)", "AI #1 ไม่รู้จักฉากนี้ → ลด conf AI #1 หรือถ่ายฉากนี้เพิ่มในโปรเจกต์ 1"],
        ["นับน็อตเกิน / ขาด ทั้งที่ครบ", "ถ่ายมุมนั้นเพิ่ม → ✂ ตัด → ตีกรอบ → เทรน AI #2 ใหม่"],
        ["ชิ้นเดียวมีกรอบซ้อน 2 กรอบ", "ตัดกรอบที่อยู่ข้างในกรอบที่มั่นใจกว่าทิ้งให้เอง · ถ้ายังซ้อน เพิ่ม conf AI #1"],
        ["บนเว็บกับ runner นับต่างกัน 1", "เชื่อตัวเลข runner · เว็บคือค่าประมาณ"],
        ["`model file not found`", "รันในโฟลเดอร์ `terminal_qc/` (ไฟล์ .onnx อยู่ข้าง config)"],
        ["`onnxruntime not installed`", "ยังไม่เปิด venv (ขั้นที่ 2)"],
        ["`MQTT disabled`", "Node-RED / broker ไม่ได้รัน หรือ IP ผิด"],
    ]))
    p.append(b.callout("ตัวอย่างนี้: เทอร์มินัล 1 รุ่น โต๊ะเดียว แสงเดียว โทรศัพท์เครื่องเดียว — ของจริงต้องถ่ายจากกล้อง"
                       "หน้างาน · NG ปลอม (ชิ้นดีถูกตีตก) ปลอดภัยกว่าแต่ยังมีต้นทุน", kind="warn"))

    p.append(b.step("✓", "จำแค่นี้", newpage=False))
    p.append(b.para("ถ่ายรูป → <b>Trainer</b>: กรอบวัตถุ → <b>✂ ตัด</b> → กรอบชิ้นส่วน → เทรน 2 โมเดล → "
                    "<b>ROI Studio</b>: AI 2 ชั้น ครบ N = OK → ส่งออก → รัน + Node-RED", size=13))
    return p
