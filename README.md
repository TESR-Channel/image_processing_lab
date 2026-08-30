<div align="center">

<img src="assets/logo.png" width="130" alt="TESR — Thai Embedded System and Robotics" />

# TESR Image Processing Lab

**Tune OpenCV in the browser, then take the Python code straight to your edge device**

Thai Embedded System and Robotics (TESR) · MIT License

[English](#english) · [ภาษาไทย](#ภาษาไทย)

</div>

---

## English

### What is this?

A **single HTML file** that packs the core Image Processing labs of the TESR curriculum into one page. Learners drag sliders and see the result instantly in the browser, then press one button to get a ready-to-run `.py` file that uses the exact same parameters — targeting PC, Raspberry Pi 5, NVIDIA Jetson, or Kinect v1.

Everything is processed by **OpenCV.js (WebAssembly) on the user's machine** — no image ever leaves the browser.

| Tab | Replaces the original course scripts |
|---|---|
| **Circles (Hough)** | `CircleDetectionFromImageEX1/2/3.py`, `CircleDetectionFromImage_GUI.py` |
| **Colour (HSV)** | `ColorDetection.py`, `ColorDetection2.py`, `ColorDetection3.py`, `ColorDetection_with_GUI.py` |
| **Image basics** | Gray → Blur → Threshold → Morphology → Canny → Contour |
| **Lines (Hough)** | `Canny_Edge.py`, `CannyEdge_With_GUI.py`, `HoughLine(.py/__GUI.py)`, `HoughLineP(.py/__GUI.py)` |
| **Draw & text** | `Drawing_Line.py`, `Drawing_Rectangle.py`, `Drawing_Circle.py`, `Put_Text.py` |
| **Haar Cascade** | `EyesDetectionusingHaarCascades.py`, `EyesDetectionWithWebcam.py`, `EyesDetectionWithKinect.py` |
| **Face Recognition** | Builds on Haar — enrol faces, train LBPH, recognise |

All 19 original scripts are kept in `python/` for classroom reference.

### Features

- **Live streaming** — open the camera and every frame runs through the active tab in real time (circles, colour, lines, Haar, face recognition — all of them). Shows the browser fps, with a **Pause** button to freeze the frame for comfortable colour picking and a **Freeze frame** button to keep a still for fine tuning.
- **Click-to-pick colour (eyedropper)** — click anywhere on the result image to sample that pixel; H, S and V sliders are set automatically, replacing `mouseClickRGB` from the original scripts.
- **Hue wrap-around** handled for red, whose H band crosses 0 — something a plain `HSV ± thresh` cannot do.
- Side-by-side original/result view, per-object result table (x, y, radius, area, angle…), and object counting.
- **Draw shapes and text** by clicking points on the image. Coordinates are stored as 0–1 fractions of the frame, so they land correctly at any camera resolution.
- **Canny + Hough lines** with an **angle filter** (0 = horizontal, 90 = vertical) for factory floor markings and conveyor edges.
- **Haar Cascade** for eyes, faces and smiles, with a **face-ROI mode** — find the face first, then search only inside it, which removes most false positives.
- **Face Recognition** — enrol faces in the browser (LBP histogram + chi-square, live-tunable threshold), then generate a full Python script using the real `cv2.face.LBPHFaceRecognizer` with three modes: `--mode enroll` → `--mode train` → `--mode recognize`.
- **Python code shown in full on the same page**, updating live as you tune. Press **Copy** or **Download .py**, plus `requirements.txt` and result-image download.
- Generated code targets: PC (`cv2.VideoCapture`) · Raspberry Pi 5 (`Picamera2`) · NVIDIA Jetson (GStreamer `nvarguscamerasrc`, USB fallback) · Kinect v1 (`freenect`). Input source: image file / live camera / video file. Options: FPS overlay, saving result frames, **MQTT** publishing for Node-RED dashboards, Thai or English comments.
- Bilingual UI (TH/EN toggle in the header).

### How to run

#### Locally

The page must be served over HTTP (not double-clicked), because browsers block pixel access from `file://`:

```bash
git clone https://github.com/TESR-Channel/image_processing_lab.git
cd image_processing_lab
python -m http.server 8000
# open http://localhost:8000
```

Drag-and-drop of your own images works in every case, even from `file://`.

#### GitHub Pages

1. Push this folder to the repository **root** (see layout below).
2. Go to **Settings → Pages → Build and deployment → Source: GitHub Actions**.
3. The workflow in `.github/workflows/deploy.yml` deploys automatically on every push to `main`.
4. The site appears at `https://tesr-channel.github.io/image_processing_lab/`.

#### Fully offline (training rooms without internet)

By default the page loads `opencv.js` and Google Fonts from CDNs. For offline use:

1. Download `opencv.js` from https://docs.opencv.org/4.10.0/opencv.js into `assets/opencv.js`.
2. In `index.html`, change:

```js
const CDNS = ['assets/opencv.js'];
```

3. Optionally vendor the Kanit/Sarabun fonts and adjust the Google Fonts `<link>`.

### Repository layout

> **Important:** `index.html`, `assets/`, `samples/` and `README.md` must all sit together at the repository root. If `index.html` or `README.md` are separated from `assets/`, the logo and the sample images will 404 (broken logo on the repo page is exactly this symptom).

```
image_processing_lab/
├── index.html              the entire tool, one file
├── assets/
│   ├── logo.png            TESR logo (used by this README and the page header)
│   └── cascades/           Haar cascade XMLs for OpenCV.js in the browser
├── samples/                sample images from the course
├── python/                 the 19 original scripts for classroom reference
├── .github/workflows/      GitHub Pages deployment
├── LICENSE
└── README.md
```

### Camera on Raspberry Pi (live mode)

If "Go live" cannot find a camera on the Pi while it works on a PC, check these in order:

1. **Secure context** - browsers only allow cameras over **https or localhost**. Opening `http://<another-machine>:8000` over the LAN silently blocks the camera. Either use the GitHub Pages https URL, or run the server on the Pi itself and open `http://localhost:8000`.
2. **USB webcam** - works out of the box. Verify the device exists: `ls /dev/video*` and `v4l2-ctl --list-devices` (package `v4l-utils`).
3. **CSI camera module (ribbon cable)** - Chromium talks V4L2 and cannot see the libcamera stack directly. Start the browser through the libcamera shim:
   ```bash
   sudo apt install libcamera-tools
   libcamerify chromium        # Raspberry Pi OS Bookworm; older releases use: libcamerify chromium-browser
   ```
   First check the module itself works: `rpicam-hello -t 3000`.
4. **Camera busy** - close anything else using it (`rpicam-hello`, VLC, another tab).
5. **Permission denied earlier** - click the camera/lock icon in the address bar, allow, retry.
6. If several `/dev/video*` nodes exist, the page now shows a **"Choose camera"** dropdown after the first permission grant - try each entry; on the Pi the first node is not always the capture node.

7. **USB cam exists in `v4l2-ctl --list-devices` but Chromium says "No camera available"** — almost always one of:
   - Chromium was opened **before** the camera was plugged in. Close every window (`pkill chromium`) and reopen — do NOT use libcamerify for USB cameras.
   - Another program is holding the device (a Python script left running in Thonny, rpicam, VLC). Check with `sudo fuser -v /dev/video0` and close it.
   - Sanity-check the camera captures outside the browser: `v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=3 --stream-to=/dev/null` (three `<` marks = frames captured). If this fails, try another USB port.
   - The user must be in the `video` group (`groups` should list it).

The page also tries multiple fallback strategies automatically (relaxed constraints, then every detected device) and prints the exact reason in the top message bar when it still fails.

### Things to tell learners every time

- **The time shown on the page is OpenCV.js on the viewer's machine — it is not a Raspberry Pi or Jetson benchmark.** Always measure again on the real hardware.
- Parameters tuned on a still image will not transfer perfectly to a real camera. Lighting, distance, lens and white balance all shift — re-tune on site.
- Hough circles/lines and HSV thresholds are rule-based methods for controlled scenes. Overlapping objects, cluttered backgrounds or changing light call for a deep-learning model such as YOLO.
- OpenCV HSV ranges are **H 0–179, S 0–255, V 0–255**, not the usual 0–360.
- `cv2.HoughCircles` returns `(x, y, radius)` — the third value is the **radius**, not the diameter.
- `cv2.Canny` accepts `apertureSize` of **3, 5 or 7 only**; anything else raises immediately (a 1–10 trackbar will crash the program).
- `cv2.HoughLines` returns `(rho, theta)` — an infinite line you must convert to two points before drawing; `cv2.HoughLinesP` returns real end points so segment length can be measured.
- `cv2.putText` cannot render Thai. For Thai text, draw through PIL and convert back to a NumPy array.
- Haar cascades are sensitive to lighting, pose and glasses; even a high `minNeighbors` leaves some false hits. Accuracy-critical work should use YOLO, SSD or MediaPipe.

### About Face Recognition

- The browser mode uses LBP histograms compared with chi-square — a **different implementation** from `cv2.face.LBPHFaceRecognizer`, so distances will not match. Use the browser to understand behaviour, then tune the real threshold on the target machine.
- Faces enrolled on the page live only in that tab's memory and vanish on close — nothing is uploaded or written to disk.
- LBPH `confidence` is a **distance: lower means more similar**. It is not a percentage — the single most common misunderstanding.
- Requires `opencv-contrib-python` (`cv2.face` lives in contrib) and must **not** be installed alongside `opencv-python` — uninstall one first.
- LBPH suits demos and proofs of concept in controlled environments. Real attendance/access systems should use face embeddings such as ArcFace or InsightFace.

### About face images and PDPA

This repository ships **no face photos** — portraits carry both copyright and PDPA obligations. In class, use the camera capture button or each learner's own image. Face data is **biometric data under Thai PDPA**: any real deployment needs explicit consent, a stated purpose and a retention period.

### Haar cascade files

The XMLs in `assets/cascades/` come from the OpenCV project (`opencv/data/haarcascades`) under the Intel/OpenCV licence stated in each file's header — do not strip those headers. The generated Python instead reads cascades from `cv2.data.haarcascades`, which ships with `opencv-python`, so no path edits are needed when moving machines.

### Where to take it next

- Use as the opening lab of TESR Academy courses before moving into YOLO and deep learning.
- Live customer demos: tune on the spot, then hand the generated `.py` to the customer's team.
- Wire results into MQTT → Node-RED → dashboard as a proof of concept for counting or colour-sorting stations.

### License

MIT © TESR Co., Ltd. (Thai Embedded System and Robotics)
The TESR name and logo are trademarks of TESR Co., Ltd. and are not covered by the MIT License.

---

## ภาษาไทย

### เครื่องมือนี้คืออะไร

ไฟล์ HTML **ไฟล์เดียว** ที่รวมแลบ Image Processing พื้นฐานของหลักสูตร TESR ไว้ในหน้าเดียว ผู้เรียนเลื่อน slider ดูผลทันทีในเบราว์เซอร์ แล้วกดปุ่มเดียวเพื่อได้ไฟล์ `.py` ที่ใช้ค่าเดียวกัน พร้อมรันบน PC, Raspberry Pi 5, NVIDIA Jetson หรือ Kinect v1

ประมวลผลด้วย **OpenCV.js (WebAssembly) ในเครื่องผู้ใช้ทั้งหมด** — ไม่มีการอัปโหลดภาพขึ้นเซิร์ฟเวอร์

| แท็บ | ครอบคลุมสคริปต์เดิม |
|---|---|
| **วงกลม (Hough)** | `CircleDetectionFromImageEX1/2/3.py`, `CircleDetectionFromImage_GUI.py` |
| **สี (HSV)** | `ColorDetection.py`, `2`, `3`, `_with_GUI.py` |
| **ภาพพื้นฐาน** | Gray → Blur → Threshold → Morphology → Canny → Contour |
| **เส้นตรง (Hough)** | `Canny_Edge.py`, `CannyEdge_With_GUI.py`, `HoughLine`, `HoughLineP` ทั้งชุด |
| **วาด & ข้อความ** | `Drawing_Line/Rectangle/Circle.py`, `Put_Text.py` |
| **Haar Cascade** | `EyesDetection` ทั้ง 3 ไฟล์ |
| **Face Recognition** | ต่อยอดจาก Haar — ลงทะเบียน เทรน LBPH แล้วรู้จำ |

สคริปต์ต้นฉบับทั้ง 19 ไฟล์เก็บไว้ที่ `python/` เพื่ออ้างอิงระหว่างสอน

### ความสามารถหลัก

- **Live Streaming** — เปิดกล้องแล้วทุกเฟรมวิ่งผ่านแท็บที่เลือกอยู่แบบเรียลไทม์ มีปุ่ม "พักภาพ" ไว้หยุดภาพคลิกดูดสี และ "จับภาพนิ่ง" ไว้เก็บเฟรมมาปรับละเอียด
- **ดูดสีด้วยการคลิก** — คลิกจุดไหนก็ได้บนภาพผลลัพธ์ ระบบตั้ง H, S, V ให้อัตโนมัติ ไม่ต้องนั่งไล่ปรับเอง
- รองรับ **hue wrap-around** สำหรับสีแดงที่ช่วง H คร่อมค่า 0
- **วาดรูปทรง/ข้อความ** ด้วยการคลิก พิกัดเก็บเป็นสัดส่วน 0–1 ย้ายความละเอียดกล้องได้
- **Canny + Hough Lines** พร้อม**กรองตามมุมเส้น** สำหรับงานเส้นตีพื้นโรงงาน
- **Haar Cascade** พร้อมโหมด face ROI ตัด false positive
- **Face Recognition** — ลงทะเบียนในเบราว์เซอร์ แล้ว generate สคริปต์ LBPH ครบ enroll → train → recognize
- **โค้ด Python โชว์เต็มในหน้าเดียวกัน** อัปเดตตามค่าที่ปรับ กด**คัดลอก**หรือ**ดาวน์โหลด .py** ได้ทันที พร้อม `requirements.txt`
- UI สลับไทย/อังกฤษได้ที่มุมขวาบน

### วิธีใช้งาน

ต้องเปิดผ่าน HTTP server (ไม่ใช่ดับเบิลคลิกไฟล์):

```bash
git clone https://github.com/TESR-Channel/image_processing_lab.git
cd image_processing_lab
python -m http.server 8000
# เปิด http://localhost:8000
```

Deploy ขึ้น GitHub Pages: **Settings → Pages → Source: GitHub Actions** แล้ว workflow ใน `.github/workflows/deploy.yml` จะจัดการให้ทุกครั้งที่ push เข้า `main`

ใช้แบบออฟไลน์: ดาวน์โหลด `opencv.js` มาไว้ที่ `assets/opencv.js` แล้วแก้ `const CDNS = ['assets/opencv.js'];` ใน `index.html`

### โครงสร้างที่ถูกต้อง

> **สำคัญ:** `index.html`, `assets/`, `samples/` และ `README.md` ต้องอยู่ระดับเดียวกันที่ root ของ repo ถ้าแยกกัน โลโก้ใน README และภาพตัวอย่างจะหาย (อาการโลโก้แตกบนหน้า repo คือเรื่องนี้)

### การใช้กล้องบน Raspberry Pi (โหมด Live)

ถ้ากด "เปิดกล้อง Live" บน Pi แล้วหากล้องไม่เจอ (ทั้งที่บนคอมทำงานปกติ) ให้ไล่ตามนี้:

1. **เปิดผ่าน https หรือ localhost เท่านั้น** — เบราว์เซอร์บล็อกกล้องเงียบ ๆ ถ้าเปิดผ่าน `http://<เครื่องอื่น>:8000` ข้าม LAN ให้ใช้ URL https ของ GitHub Pages หรือรันเซิร์ฟเวอร์บนตัว Pi เองแล้วเปิด `http://localhost:8000`
2. **กล้อง USB** ใช้ได้ทันที เช็คว่าเครื่องเห็นด้วย `ls /dev/video*` และ `v4l2-ctl --list-devices`
3. **กล้อง CSI (สายแพ)** — Chromium คุยผ่าน V4L2 มองไม่เห็น libcamera โดยตรง ต้องเปิดเบราว์เซอร์ผ่านตัวกลาง:
   ```bash
   sudo apt install libcamera-tools
   libcamerify chromium        # Pi OS Bookworm ชื่อ chromium เฉย ๆ (รุ่นเก่าใช้ chromium-browser)
   ```
   ทดสอบตัวกล้องก่อนด้วย `rpicam-hello -t 3000`
4. **กล้องถูกใช้งานอยู่** — ปิด rpicam-hello, VLC หรือแท็บอื่นที่ใช้กล้องค้างไว้
5. **เคยกดปฏิเสธสิทธิ์** — กดไอคอนกล้อง/กุญแจในแถบ address อนุญาตใหม่
6. ถ้ามี `/dev/video*` หลายตัว หน้าเว็บจะมี **dropdown "เลือกกล้อง"** โผล่หลังอนุญาตครั้งแรก ให้ลองไล่ทีละตัว — บน Pi ตัวแรกไม่ใช่ตัวจับภาพเสมอไป

7. **`v4l2-ctl --list-devices` เห็นกล้อง USB แต่ Chromium ขึ้น "No camera available"** — เกือบทั้งหมดคือ:
   - เปิด Chromium **ก่อน**เสียบกล้อง → ปิดทุกหน้าต่างให้สนิท (`pkill chromium`) แล้วเปิดใหม่ (กล้อง USB **ไม่ต้อง** libcamerify)
   - มีโปรแกรมถือกล้องค้าง (สคริปต์ Python ใน Thonny, rpicam, VLC) → เช็คด้วย `sudo fuser -v /dev/video0` แล้วปิด
   - ทดสอบว่ากล้องจับภาพได้จริงนอกเบราว์เซอร์: `v4l2-ctl -d /dev/video0 --stream-mmap --stream-count=3 --stream-to=/dev/null` (ขึ้น `<` สามตัว = จับเฟรมได้) ถ้า fail ลองย้ายพอร์ต USB
   - ผู้ใช้ต้องอยู่ในกลุ่ม `video` (สั่ง `groups` ต้องเห็นคำว่า video)

หน้าเว็บจะลองเปิดกล้องหลายวิธีให้อัตโนมัติอยู่แล้ว (ผ่อนเงื่อนไข → ไล่ทุก device) และถ้ายังไม่ได้จะบอกสาเหตุที่แท้จริงในแถบข้อความบนสุด

### ข้อจำกัดที่ต้องบอกผู้เรียนทุกครั้ง

- เวลาที่แสดงบนหน้าเว็บคือเวลาของ OpenCV.js บนเครื่องที่เปิด **ไม่ใช่ benchmark ของ Pi หรือ Jetson** ต้องวัดซ้ำบนอุปกรณ์จริง
- ค่าที่จูนจากภาพนิ่งใช้กับกล้องจริงได้ไม่ตรงเสมอ แสง ระยะ เลนส์เปลี่ยนต้องจูนใหม่
- Hough และ HSV threshold เป็นวิธีเชิงกฎ เหมาะกับฉากควบคุมได้ งานยากให้ขยับไป YOLO
- HSV ของ OpenCV คือ H 0–179, S 0–255, V 0–255
- `HoughCircles` คืนค่า**รัศมี**ไม่ใช่เส้นผ่านศูนย์กลาง · `Canny` รับ apertureSize เฉพาะ 3, 5, 7 · `putText` วาดภาษาไทยไม่ได้
- `confidence` ของ LBPH คือ**ระยะห่าง ยิ่งน้อยยิ่งเหมือน** ไม่ใช่เปอร์เซ็นต์ และต้องใช้ `opencv-contrib-python` (ห้ามลงคู่กับ `opencv-python`)
- รีโพนี้ไม่แถมภาพใบหน้า — ภาพบุคคลมีเรื่องลิขสิทธิ์และ PDPA ระบบจริงที่เก็บใบหน้าต้องขอความยินยอมโดยชัดแจ้งเสมอ

### License

MIT © TESR Co., Ltd. (Thai Embedded System and Robotics)
ชื่อและโลโก้ TESR เป็นเครื่องหมายการค้าของบริษัท ไม่รวมอยู่ในสัญญาอนุญาต MIT
