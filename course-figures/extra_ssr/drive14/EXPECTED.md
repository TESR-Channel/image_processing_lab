# Chapter 14 — QC with two AIs: find the object, then check the parts inside it

`ssr_qc.py` v2.1.0. One program, two products:

| | Part 1: terminal block TB-2504 | Part 2: Solid State Relay |
|---|---|---|
| pictures | 30 real phone photos (`image/`, copies in `samples_terminal/`) | 8 samples + a live camera |
| AI #1 / AI #2 | `terminal` / `screw` | `ssr` / `screw` |
| slots | 8, taught with `--any-angle` (`terminal_slots.json`) | 4, upright (`ssr_slots.json`) |
| demo | `python ssr_qc.py --demo terminal` | `python ssr_qc.py --demo` |

```
picture ─► AI #1 finds each terminal block      (class "terminal")
           cut the box out
        ─► AI #2 finds each screw head inside    (class "screw" - the only class)
           lay the 8-slot layout taught from ONE good block over the heads found
           every slot has a screw = OK  (green boxes)
           any slot without one   = NG  (red box + slot number where the screw should be)
           every block checked → records/0001_OK.jpg, 0002_NG.jpg ... + records/log.csv
```

Measured 2026-10-28: Python 3.13, onnxruntime 1.31.0, opencv 5.0.0, paho-mqtt 2.1.0.

## Part 1 — the terminal block, from photos

### Run the demo

```
python ssr_qc.py --demo terminal
```
```
[INFO] downloading terminal_finder.onnx ...
[INFO] downloading terminal_checker.onnx ...
[INFO] downloading ok_3327.jpg ...
  ... (30 photos + terminal_slots.json)
[INFO] version  : ssr_qc v2.1.0
[INFO] AI #1    : terminal_finder.onnx (onnxruntime, 416 px) - object = terminal
[INFO] AI #2    : terminal_checker.onnx (onnxruntime, 320 px) - part = screw
[INFO] slots    : terminal_slots.json - 8 screw per terminal
[INFO] records  : records/ (numbered pictures + log.csv, next #0001)
[NG] #0001  ng_3338.jpg  found 7/8  empty slot 8
[NG] #0002  ng_3339.jpg  found 7/8  empty slot 1
  ...
[NG] #0019  ng_3359.jpg  found 5/8  empty slot 2, 3, 7
[OK] #0020  ok_3327.jpg  found 8/8
  ...
[OK] #0030  ok_3337.jpg  found 8/8
```

All 30 verdicts match the folders the photos came from (11 OK, 19 NG), the
number of screws found matches a hand count on every photo, and every red box
sits on a hole that really is empty (checked against hand-marked positions).

The block is symmetric: turned 180° it looks the same, so slot numbers can swap
ends between photos (`ng_3338` says slot 8, the same hole on another photo may
be slot 1). The red box is always on the right hole.

### How the demo models were made — and what that means

- 20 photos trained the models; **10 photos never trained them**
  (ok_3335–3337, ng_3339, 3343, 3345, 3349, 3355, 3357, 3359). Those 10 were
  the validation set that picked the best epoch, so they are unseen by the
  weights but not completely independent.
- AI #1 and AI #2 are YOLOv8n trained with Ultralytics (the YOLO route), on the
  20 photos plus copies made by a script: blocks pasted on other parts of the
  table, crops turned to every angle. finder mAP50 0.995, checker mAP50 0.982
  on the 10.
- One block, one table, one light, one phone. A different block, table, light
  or camera needs its own photos and training.

### Do it yourself — the TESR tools, step by step

1. **Image Processing Lab** → 🛠 ปรับแต่งภาพ → threshold: check the empty
   holes and the screw heads look different under your light. (One fixed
   threshold found the 2 empty holes on ng_3343 but miscounted 4 other photos:
   3, 2, 1, 10 blobs where 0, 0, 3, 3 holes were empty — the reason we use AI.)
2. **AI Vision Trainer**, AI #1: Object Detection → Load Project
   `from_web/terminal_finder_project.zip` (20 photos boxed + 20 background) →
   Download Dataset (YOLO) → put `dataset/` next to `train.py` in `yolo-trainer`
   (link in the zip's START_HERE.md), then:
   ```
   pip install -r requirements.txt "onnx<2" onnxslim     # once
   python train.py --imgsz 416 --epochs 100
   python export.py --target onnx                        # best.onnx -> copy to my_finder/
   ```
   Keep boxes upright (no Q/E): a rotated box makes the export YOLO OBB,
   which `ssr_qc.py` does not read. Train Now on the page (needs 2 classes:
   `terminal` + `background`) is for a quick live look only.
3. Cut the blocks out for AI #2 — no `--checker` = only cut, no verdict:
   ```
   python ssr_qc.py --finder my_finder/best.onnx --image samples_terminal --keep mydata
   ```
   ```
   [INFO] AI #2    : none yet - only cutting each terminal out into mydata/crops
   [INFO] kept     : ng_3338 - picture + 1 object crop(s) in mydata
   ...
   [INFO] done     : 30 crop(s) in mydata/crops - label them for AI #2
   ```
4. **AI Vision Trainer**, AI #2: Load Project `from_web/terminal_screws_project.zip`
   (20 crops, a box on every screw head, 137 boxes; background = 43 close-ups of
   empty holes and table). Several boxes per photo: drag again on empty space.
   Download Dataset (YOLO) → new `dataset/` in `yolo-trainer`, then:
   ```
   python train.py --imgsz 320
   python export.py --target onnx                        # best.onnx -> copy to my_checker/
   ```
5. Teach the 8 slots from one good block:
   ```
   python ssr_qc.py --finder my_finder/best.onnx --checker my_checker/best.onnx --slots my_slots.json --teach samples_terminal/ok_3327.jpg --any-angle
   ```
6. Check a folder of photos:
   ```
   python ssr_qc.py --finder my_finder/best.onnx --checker my_checker/best.onnx --slots my_slots.json --image my_photos
   ```

### Measured (ssr_qc.py on all 30 photos; "right" = OK/NG right and every red box on a really empty hole)

| AI #1 + AI #2 | trained how | 10 unseen photos | all 30 |
|---|---|---|---|
| demo (`models/`) | YOLO, 20 photos + script-made moved/turned copies | 10/10 | 30/30 |
| AI #1 + AI #2 from the two `from_web/` projects only | yolo-trainer: AI #1 `train.py --imgsz 416 --epochs 100` (13 min), AI #2 `train.py --imgsz 320` (80 epochs, 9 min), 2-core CPU | 10/10 | 30/30 |
| same, AI #1 with only `--epochs 40` | yolo-trainer | 4/10 | 6/30 (several false boxes per photo) |
| AI #2 with **Train Now** in the browser | web trainer v3.2.0, 20 crops + 43 background, 1,070 s | screw count right on 0/10 | — |

Why the browser model fails AI #2: its detector is a 7×7 grid over the picture
and neighbouring screw heads are only about one cell apart, so it merges or
misses them (counts 2–8 for blocks with 5–8 screws). It is fine for one big
object per picture; for many small parts use the YOLO route.
AI #1 with Train Now (20 photos + 20 background) trained in 843 s; its
accuracy on these photos was **not measured** (the test page stopped
responding) — the YOLO route above is the measured one.

`export.py --target onnx` stops with *Missing packages: onnxslim* unless you
install `"onnx<2" onnxslim` once (`requirements.txt` has only ultralytics and
opencv).


## Part 2 — the Solid State Relay (camera / video)

### Run the demo

```
python ssr_qc.py --demo
```
```
[INFO] downloading ssr_finder.onnx ...
  ... (screw_checker.onnx and 8 sample pictures)
[INFO] AI #1    : ssr_finder.onnx (onnxruntime, 416 px) - object = ssr
[INFO] AI #2    : screw_checker.onnx (onnxruntime, 320 px) - part = screw
[INFO] slots    : ssr_slots.json - 4 screw per ssr
[INFO] records  : records/ (numbered pictures + log.csv, next #0001)
[NG] #0001  ng_1.jpg  found 3/4  empty slot 4
[NG] #0002  ng_2.jpg  found 2/4  empty slot 3, 4
[NG] #0003  ng_3.jpg  found 3/4  empty slot 2
[OK] #0004  ok_1.jpg  found 4/4
[OK] #0005  ok_2.jpg  found 4/4
[NG] #0006  real_angle.jpg  found 2/4  empty slot 1, 2, 3, 4
[OK] #0007  real_front.jpg  found 4/4
[NG] #0008  real_front_ng.jpg  found 3/4  empty slot 3
```

A window shows each picture (any key = next, q = quit); `--headless` for no
window. Run it again and the numbering carries on (#0009 ...): `records/` is
the backup of every verdict. `--records other_folder` or `--no-records`.

Seven of the eight are right. **`real_angle.jpg` is wrong on purpose to look
at**: a different model (SSR-75 DA), photographed at an angle, all four screws
present. AI #2 finds two screws, and not where the slots taught from a front
view are → NG. See the limits below.

| Sample | What it is | Truth |
|---|---|---|
| `ok_1`, `ok_2` | the front photo placed on a made-up table | OK |
| `ng_1`, `ng_2`, `ng_3` | same, screws removed by program | NG at 4 / 3+4 / 2 |
| `real_front` | the product photo itself | OK |
| `real_front_ng` | the product photo, terminal 3 screw removed by program | NG at 3 |
| `real_angle` | a second product photo: SSR-75 DA, angled | OK (demo says NG) |

On 200 more scenes made the same way but never used in training, the verdict
and the empty slots were right 200 times out of 200 — the same single photo
underneath, so this says the pipeline works, not that it works on your line.

### records/

```
records/0001_NG.jpg   the labelled picture: #0001 NG, green = screw found, red = empty slot
records/log.csv       seq,time,result,found,expect,empty_slots,source,picture
                      1,2026-10-27T08:47:46,NG,3,4,4,ng_1.jpg,0001_NG.jpg
```

Live (`--camera usb|csi|ip|file --source ...`): each relay is recorded **once**, when
the verdict has held for 5 frames (`--settle`). Take it away until no relay is
in view for 5 frames, put the next one in → the next number. Key `r` records
again by hand, `c` keeps training photos (with `--keep`), `q` stops.

### Camera and broker - the same words as every chapter

```
python ssr_qc.py --camera usb --source 0              USB webcam (next ones: --source 1, 2)
python ssr_qc.py --camera csi --source 0              ribbon camera (Raspberry Pi / Jetson)
python ssr_qc.py --camera ip --source rtsp://user:pass@192.168.1.64:554/stream1
python ssr_qc.py --camera file --source my_clip.mp4   a video file
python ssr_qc.py --camera usb --source 2 --broker 192.168.1.50   + every record to Node-RED there
```

### Teach the slots from one good object

```
python ssr_qc.py --teach samples/real_front.jpg --slots ssr_slots_taught.json
```
```
[INFO] taught   : 4 slots from one good ssr -> ssr_slots_taught.json
[INFO]   slot 1    at x 0.23  y 0.17 of the box
[INFO]   slot 2    at x 0.74  y 0.17 of the box
[INFO]   slot 3    at x 0.24  y 0.82 of the box
[INFO]   slot 4    at x 0.73  y 0.83 of the box
```

Slots are numbered like reading a page (top row left → right, then the next
row) and kept as fractions of the object box, so the object may move and
change size in the picture. Rename them in the JSON as you like — the shipped
`ssr_slots.json` is this file with 3 and 4 swapped to match the relay's print.
Without a slots file the program only counts (`--expect 4`) and cannot mark
which slot is empty.

### Your own product: 4 screws, 10 screws, a tray of 30

Same program; change three things:

| | AI #1 (object) | AI #2 (part) | teach from |
|---|---|---|---|
| this relay | `ssr` | `screw` | a relay with all 4 screws |
| a panel with 10 screws | `panel` | `screw` | a panel with all 10 |
| a tray of 30 parts | `tray` | `part` | a full tray |

```
python ssr_qc.py --camera usb --source 0 --keep mydata       1. photos: c = keep frame + object cut out
   (AI Vision Trainer: AI #1 on mydata/frames, AI #2 on mydata/crops, one class each, Detection)
python ssr_qc.py --finder tray.onnx --checker part.onnx --slots tray_slots.json --teach full_tray.jpg
python ssr_qc.py --finder tray.onnx --checker part.onnx --slots tray_slots.json --camera usb --source 0
```

(file names in these three lines are examples.) Both AIs take any YOLO-layout
detector in ONNX: the AI Vision Trainer's `model.onnx` + `classes.txt` (browser
route, read as the Trainer resizes: stretch) or an Ultralytics `best.onnx`
(Download Dataset (YOLO) → `yolo-trainer/` `python train.py` →
`python export.py --target onnx` — the demo models were made this way). AI #2
is labelled with **only the part**: draw a box around every screw you see; an
empty slot gets no box.

For many small parts close together (a tray), look straight down, keep the tray
square to the camera, and teach with the same camera and height you will use.

### Fixed jig: ROI Studio instead of AI #1

If the object always sits in the same place, so do its slots — four ROI boxes
replace AI #1. `ssr_jig.json` is that config (made for the product photo; in
ROI Studio import it, load a picture of your jig, drag the boxes onto your
terminals, add your AI #2, expect `screw`). Run `--demo` once first so
`models/screw_checker.onnx` exists:

```
python tesr_vision_runner.py --config ssr_jig.json --image samples/real_front_ng.jpg --once
```
```
terminal_1 = ['screw']  (conf 0.88)  [ok]
terminal_2 = ['screw']  (conf 0.85)  [ok]
terminal_3 = []  (conf 0.00)  [empty]
terminal_4 = ['screw']  (conf 0.89)  [ok]
```

Any terminal not `[ok]` = NG. On `real_front.jpg` all four are `[ok]`.

### Node-RED

Node-RED with the chapter 12 or 13 flow (it has the broker) → Import
`ssr_qc_flow.json` → Deploy. Then:

```
python ssr_qc.py --image samples --broker localhost --headless
```

Every record arrives on `tesr/qc/line1/result`:

```json
{"seq": 8, "time": "2026-10-27T08:50:53", "result": "NG", "found": 3, "expect": 4,
 "empty": ["3"], "picture": "records/0008_NG.jpg"}
```

The node `count OK / NG` shows the running total under it —
`OK 3 · NG 5 (last #8 NG empty 3)` after the eight samples.

### Honest limits (relay demo)

- The demo models were trained on **variations of one product photo** (moved,
  turned up to ±14°, resized, other light and backgrounds, screws removed by
  program). They have seen one relay, from the front. They show the idea; they
  are **not a QC system**.
- Slots are positions in the object box seen from the taught view. A tilted or
  rotated object moves its screws away from the slots (`real_angle.jpg`). Fix
  the camera, keep the object upright, teach from the real camera.
- A false NG (good part rejected) is the safer mistake in QC, but it still
  costs. The cure is real photos of every model and angle you will meet —
  good **and** bad.
- Not tested here: a real camera on a real line, Windows, Raspberry Pi,
  Jetson, and the ROI Studio web page importing `ssr_jig.json` (the runner
  reads it). Measure speed on your own device.

### If it does not work

| You see | Do |
|---|---|
| `no slots file ... counting only` | teach one good object (`--teach`), or point `--slots` at your file |
| `could not download ...` | no internet — copy `models/` and `samples/` from someone who has them |
| `model not found` | `--demo` once, or point `--finder` / `--checker` at your files |
| `no object found` | AI #1 does not know your object / scene — `--conf 0.3`, or train AI #1 on your camera's pictures |
| red box beside a screw that is there | teach again from the real camera and angle |
| OK although a part is missing / NG although all are there | AI #2 has not seen this — keep such pictures (`--keep`), label, train again |
| shiny screw heads look white | move the light, diffuse it, tilt the camera — try it in Image Processing Lab first |
| `cannot reach the broker` | Node-RED not running, no broker flow deployed (chapter 12/13), or wrong IP |
| `paho-mqtt not installed` | `pip install paho-mqtt` (only `--broker` needs it) |