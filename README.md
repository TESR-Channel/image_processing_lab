<div align="center">

<img src="assets/logo.png" width="130" alt="TESR — Thai Embedded System and Robotics" />

# TESR Image Processing Lab

**Tune OpenCV in the browser, then take the Python code straight to your edge device**

Thai Embedded System and Robotics (TESR) · MIT License

### 🔗 เปิดใช้งานได้เลย · Open the Lab

**[https://tesr-channel.github.io/image_processing_lab/](https://tesr-channel.github.io/image_processing_lab/)**

ไม่ต้องติดตั้งอะไร เปิดในเบราว์เซอร์ได้ทันที · Nothing to install — runs right in the browser

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
| **Find defects** | New — rule-based inspection with no model at all. A machined part: missing hole (a *count*), scratch (a *shape* — `minAreaRect` long/short), stain (an *area*). A PCB: `connectedComponents` on the copper against the design count, where an open circuit pushes it up and a short pulls it down |
| **Lines (Hough)** | `Canny_Edge.py`, `CannyEdge_With_GUI.py`, `HoughLine(.py/__GUI.py)`, `HoughLineP(.py/__GUI.py)` |
| **Draw & text** | `Drawing_Line.py`, `Drawing_Rectangle.py`, `Drawing_Circle.py`, `Put_Text.py` |
| **Haar Cascade** | `EyesDetectionusingHaarCascades.py`, `EyesDetectionWithWebcam.py`, `EyesDetectionWithKinect.py` |
| **Face Recognition** | Builds on Haar — enrol faces, train LBPH, recognise |
| **Codes & markers** | New — ArUco, QR and five 1-D barcodes (EAN-13, EAN-8, UPC-A, Code 128, Code 39): make one to print, then read it back |

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
- **Codes & markers** — two modes in one tab. *Make* draws an ArUco marker (nine dictionaries, any id), a QR code (any UTF-8 text including Thai, four error-correction levels) or one of five 1-D barcodes - EAN-13, EAN-8 and UPC-A from digits with the check digit worked out for you, Code 128 and Code 39 from text. Each type carries a one-line note saying where you would actually meet it: EAN-13 on supermarket products, Code 128 on parcel and pallet labels, Code 39 on older asset tags, and so on. One button sends it straight back into the main image so the whole loop — make it, read it, export the Python — happens on one screen. *Read* finds all three in an image or a live frame, reports ids, decoded text, positions and corners, and converts pixels to millimetres when you give it the printed marker size. The exported Python matches: a reader script, or a generator script that can also lay out a printable sheet of markers. OpenCV's barcode reader covers the EAN/UPC family only, so for Code 128 and Code 39 the page says so plainly and the reader you export switches to `pyzbar`.
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

`assets/opencv.js` is already the **first** source the page tries, ahead of the
two CDNs, so making the Lab work without internet is one download and no code
change:

1. Download `opencv.js` from https://docs.opencv.org/4.10.0/opencv.js into `assets/opencv.js` (about 10 MB).
2. That is all. If the file is absent the request 404s immediately and the CDNs are used instead, so the page works either way.
3. Optionally vendor the Kanit/Sarabun fonts and adjust the Google Fonts `<link>`.

Why the local copy matters on a Raspberry Pi: a filtered or saturated network
does not refuse the CDN request, it simply stops answering it. The loader gives
each **remote** source 15 seconds and then moves on, so a stall now falls
through to the next source and ends with a readable error rather than leaving
the page on "loading OpenCV.js" for ever. The local file is not put on that
clock — it cannot stall on the network, and a slow device parsing 10 MB must
not be cut off part-way.

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
- The ArUco **dictionary must match the printed markers exactly**. Pick the wrong set and nothing is found at all, however sharp the marker is — this is the number one reason for "it sees nothing".
- Every code needs its **white quiet zone**. Cropping it off, or printing onto glossy or laminated stock, is what breaks most real installations.
- `MARKER_MM` turns pixels into millimetres only while the marker lies flat and parallel to the sensor. Tilt it and the number is wrong — a marker gives you scale, not a full pose, unless you calibrate the camera.

### About the Codes & markers tab

- **OpenCV can read these codes but cannot draw QR or barcodes in the browser.** `objdetect` ships detectors plus an ArUco *generator*, and `cv2.QRCodeEncoder` exists in Python — but the browser build has no QR or barcode encoder at all. So the QR and barcode drawing on this page is ours, written from ISO/IEC 18004 (QR), 15420 (EAN/UPC), 15417 (Code 128) and 16388 (Code 39) and kept in `_build/encoders.js`. Every symbol it produces is round-tripped back through OpenCV and pyzbar before release; see `_build/verify.py`.
- **OpenCV's barcode reader covers the EAN/UPC family only.** Measured: it decodes EAN-13, EAN-8, UPC-A and UPC-E, and has no Code 128 or Code 39 reader at all. A Code 128 you generate here therefore cannot be read back by the Lab's own reader - the page says so beside those two types rather than letting it look broken, and the exported reader switches to `pyzbar`, which reads all of them.
- **OpenCV's barcode detector works on edge gradients, so it dislikes pixel-perfect images.** Measured on this page's own output: with no blur it decodes nothing; with a 3×3 blur it *finds* the bars but still fails to decode; at 5×5 it decodes. That is why "soften edges" exists and why it tries 5×5 then 7×7. A photographed barcode usually needs none of this — the camera does the softening for you. The same two-step is written into the exported Python.
- For the same reason the generator holds every barcode's module width to 2–4 px however large the export is: thin bars read far more reliably than thick ones. Scale it up in the print dialog, not in the pixels.
- ArUco and QR have no such quirk — both round-trip cleanly at every size tested, Thai text included.
- `detectAndDecodeMulti` finds several QR codes at once, but on a busy scene it can quietly return nothing where the single-code `detectAndDecode` reads the very same symbol. Both the page and the exported Python try multi first and fall back to single rather than trusting either alone.
- Three sample scenes ship for this tab: `codes_mixed.jpg` (one of each), `codes_aruco.jpg` (five markers, good for the mm/px lesson) and `codes_barcode.jpg`. They are **generated illustrations, not photographs** — built by `_build/make_samples.py`, which tilts, shades, softens and JPEGs each code the way a camera would, and refuses to write any image it cannot decode back.

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
| **หาตำหนิ** | ของใหม่ — ตรวจตำหนิด้วยกฎล้วน ๆ ไม่ใช้โมเดลเลย ชิ้นงาน: รูหาย (*นับ*), รอยขีด (*รูปทรง* — `minAreaRect` ยาว/สั้น), คราบ (*พื้นที่*) แผ่น PCB: `connectedComponents` นับลายทองแดงเทียบกับแบบ ลายขาดนับได้มากขึ้น ลายช็อตนับได้น้อยลง |
| **เส้นตรง (Hough)** | `Canny_Edge.py`, `CannyEdge_With_GUI.py`, `HoughLine`, `HoughLineP` ทั้งชุด |
| **วาด & ข้อความ** | `Drawing_Line/Rectangle/Circle.py`, `Put_Text.py` |
| **Haar Cascade** | `EyesDetection` ทั้ง 3 ไฟล์ |
| **Face Recognition** | ต่อยอดจาก Haar — ลงทะเบียน เทรน LBPH แล้วรู้จำ |
| **โค้ด & มาร์กเกอร์** | ของใหม่ — ArUco, QR และบาร์โค้ด 1 มิติ 5 ชนิด (EAN-13, EAN-8, UPC-A, Code 128, Code 39): สร้างไว้พิมพ์ แล้วอ่านกลับได้ในหน้าเดียว |

สคริปต์ต้นฉบับทั้ง 19 ไฟล์เก็บไว้ที่ `python/` เพื่ออ้างอิงระหว่างสอน

### ความสามารถหลัก

- **Live Streaming** — เปิดกล้องแล้วทุกเฟรมวิ่งผ่านแท็บที่เลือกอยู่แบบเรียลไทม์ มีปุ่ม "พักภาพ" ไว้หยุดภาพคลิกดูดสี และ "จับภาพนิ่ง" ไว้เก็บเฟรมมาปรับละเอียด
- **ดูดสีด้วยการคลิก** — คลิกจุดไหนก็ได้บนภาพผลลัพธ์ ระบบตั้ง H, S, V ให้อัตโนมัติ ไม่ต้องนั่งไล่ปรับเอง
- รองรับ **hue wrap-around** สำหรับสีแดงที่ช่วง H คร่อมค่า 0
- **วาดรูปทรง/ข้อความ** ด้วยการคลิก พิกัดเก็บเป็นสัดส่วน 0–1 ย้ายความละเอียดกล้องได้
- **Canny + Hough Lines** พร้อม**กรองตามมุมเส้น** สำหรับงานเส้นตีพื้นโรงงาน
- **Haar Cascade** พร้อมโหมด face ROI ตัด false positive
- **Face Recognition** — ลงทะเบียนในเบราว์เซอร์ แล้ว generate สคริปต์ LBPH ครบ enroll → train → recognize
- **โค้ด & มาร์กเกอร์** — แท็บเดียวมีสองโหมด *สร้าง* วาด ArUco (เลือกได้ 9 dictionary ทุก id), QR (ข้อความ UTF-8 ใส่ภาษาไทยได้ เลือกระดับกู้คืนได้ 4 ระดับ) หรือบาร์โค้ด 1 มิติ 5 ชนิด — EAN-13, EAN-8 และ UPC-A ใส่เป็นตัวเลขแล้วคำนวณหลักตรวจสอบให้ ส่วน Code 128 และ Code 39 ใส่เป็นข้อความ · ทุกชนิดมีคำอธิบายหนึ่งบรรทัดว่าเจอที่ไหนในชีวิตจริง เช่น EAN-13 บนสินค้าในห้าง Code 128 บนใบปิดกล่องพาร์เซลและป้ายพาเลท Code 39 บนป้ายครุภัณฑ์รุ่นเก่า กดปุ่มเดียวส่งกลับเข้าภาพหลักเพื่ออ่านซ้ำ ครบวงจร สร้าง → อ่าน → ออกเป็นโค้ด Python ในจอเดียว · *อ่าน* หาได้ทั้งสามแบบจากภาพนิ่งหรือกล้องสด บอก id ข้อความที่ถอดได้ ตำแหน่งและมุมทั้งสี่ และแปลงพิกเซลเป็นมิลลิเมตรให้เมื่อใส่ขนาดมาร์กเกอร์ที่พิมพ์จริง โค้ด Python ที่ได้ก็มีทั้งตัวอ่านและตัวสร้าง (สร้างแผ่นมาร์กเกอร์หลายตัวไว้พิมพ์ทีเดียวได้ด้วย) · ตัวอ่านบาร์โค้ดของ OpenCV รู้จักแค่ตระกูล EAN/UPC หน้าเว็บจึงบอกตรง ๆ สำหรับ Code 128 และ Code 39 และตัวอ่านที่ export ออกไปจะเปลี่ยนไปใช้ `pyzbar` ให้
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

ใช้แบบออฟไลน์: ดาวน์โหลด `opencv.js` จาก https://docs.opencv.org/4.10.0/opencv.js มาไว้ที่ `assets/opencv.js` (ประมาณ 10 MB) เท่านั้น ไม่ต้องแก้โค้ด เพราะหน้าเว็บลองโหลดจาก `assets/opencv.js` เป็นอันดับแรกอยู่แล้ว ถ้าไม่มีไฟล์ก็จะตกไปใช้ CDN ให้เอง และถ้า CDN ค้างไม่ตอบ ระบบจะรอ 15 วินาทีแล้วเปลี่ยนไปแหล่งถัดไป ไม่ค้างอยู่ที่ "กำลังโหลด OpenCV.js" ตลอดไปเหมือนเดิม

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
- **dictionary ของ ArUco ต้องตรงกับที่พิมพ์เป๊ะ ๆ** เลือกผิดชุดจะไม่เจออะไรเลยแม้มาร์กเกอร์จะคมมาก — เป็นสาเหตุอันดับหนึ่งของอาการ "มันไม่เจอ"
- โค้ดทุกชนิดต้องมี**ขอบขาว** รอบตัว ตัดขอบทิ้งหรือพิมพ์ลงกระดาษเคลือบเงาคือสาเหตุที่หน้างานจริงพังบ่อยที่สุด
- `MARKER_MM` แปลงพิกเซลเป็นมิลลิเมตรได้เฉพาะตอนมาร์กเกอร์วางราบขนานกับเซนเซอร์ ถ้าเอียงตัวเลขจะผิด — มาร์กเกอร์ให้ "สเกล" ไม่ได้ให้ pose เต็ม นอกจากจะ calibrate กล้องก่อน

### เกี่ยวกับแท็บโค้ด & มาร์กเกอร์

- **OpenCV อ่านโค้ดพวกนี้ได้ แต่วาด QR กับบาร์โค้ดในเบราว์เซอร์ไม่ได้** ตัว build สำหรับเว็บมีแต่ตัวอ่าน กับตัวสร้าง ArUco เท่านั้น (ฝั่ง Python มี `cv2.QRCodeEncoder` ให้) ตัววาด QR และบาร์โค้ดบนหน้านี้จึงเขียนขึ้นเอง อ้างอิง ISO/IEC 18004 (QR), 15420 (EAN/UPC), 15417 (Code 128) และ 16388 (Code 39) เก็บไว้ที่ `_build/encoders.js` และทุกสัญลักษณ์ที่สร้างถูกทดสอบอ่านกลับด้วย OpenCV และ pyzbar ก่อนปล่อยเสมอ (ดู `_build/verify.py`)
- **ตัวอ่านบาร์โค้ดของ OpenCV รู้จักแค่ตระกูล EAN/UPC** วัดมาแล้ว: อ่านได้ EAN-13, EAN-8, UPC-A และ UPC-E เท่านั้น ไม่มีตัวอ่าน Code 128 หรือ Code 39 เลย · Code 128 ที่สร้างจากหน้านี้จึงอ่านกลับด้วยตัวอ่านของ Lab เองไม่ได้ หน้าเว็บจึงเขียนบอกไว้ตรง ๆ ข้างสองชนิดนั้น แทนที่จะปล่อยให้งง ส่วนตัวอ่านที่ export จะเปลี่ยนไปใช้ `pyzbar` ซึ่งอ่านได้ครบทุกชนิด
- **ตัวอ่านบาร์โค้ดของ OpenCV ดูการไล่ระดับของขอบ จึงไม่ถูกกับภาพที่คมเป๊ะ** วัดจากผลลัพธ์ของหน้านี้เอง: ไม่เบลอเลย = อ่านไม่ออก, เบลอ 3x3 = "เจอ" แท่งแต่ถอดรหัสไม่ได้, เบลอ 5x5 = ถอดได้ จึงมีตัวเลือก "เบลอเล็กน้อยก่อนอ่าน" และระบบจะลอง 5x5 ก่อนแล้วค่อย 7x7 · ถ้าถ่ายจากกล้องจริงมักไม่ต้องใช้เลยเพราะกล้องเบลอให้อยู่แล้ว และโค้ด Python ที่ export ก็ทำสองขั้นเดียวกัน
- ด้วยเหตุผลเดียวกัน ตัวสร้างบาร์โค้ดทุกชนิดจะกดความกว้างแท่งไว้ที่ 2–4 พิกเซลเสมอไม่ว่าจะสั่งขนาดใหญ่แค่ไหน เพราะแท่งบางอ่านง่ายกว่าแท่งหนามาก ถ้าต้องการใหญ่ขึ้นให้ไปขยายตอนสั่งพิมพ์
- ArUco กับ QR ไม่มีอาการนี้ ทดสอบแล้วอ่านกลับได้ครบทุกขนาด รวมถึงข้อความภาษาไทย
- `detectAndDecodeMulti` อ่าน QR ได้หลายอันในเฟรมเดียว แต่บนฉากที่รกมันคืนค่าว่างเงียบ ๆ ทั้งที่ `detectAndDecode` อ่านอันเดียวกันได้ ทั้งหน้าเว็บและโค้ด Python ที่ export จึงลอง multi ก่อนแล้วค่อย fallback ไป single
- แท็บนี้มีภาพตัวอย่างให้ 3 ภาพ: `codes_mixed.jpg` (มีครบสามแบบ), `codes_aruco.jpg` (ห้ามาร์กเกอร์ เหมาะกับบทเรียน มม./พิกเซล) และ `codes_barcode.jpg` — ทั้งหมดเป็น**ภาพที่สร้างขึ้น ไม่ใช่ภาพถ่ายจริง** สร้างด้วย `_build/make_samples.py` ซึ่งเอียง ใส่แสงไม่สม่ำเสมอ เบลอ และบันทึกเป็น JPEG เลียนแบบสิ่งที่กล้องทำ และจะไม่ยอมเขียนไฟล์ที่อ่านกลับไม่ได้

### License

MIT © TESR Co., Ltd. (Thai Embedded System and Robotics)
ชื่อและโลโก้ TESR เป็นเครื่องหมายการค้าของบริษัท ไม่รวมอยู่ในสัญญาอนุญาต MIT