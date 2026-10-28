#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extra part - QC with two AIs: find the object, then check the parts inside it
=============================================================================
TESR Academy - AI Vision Engineering for Edge AI

    AI #1  ssr_finder.onnx     the whole picture   ->  a box around each object (here: a Solid State Relay)
           cut the box out
    AI #2  screw_checker.onnx  the cut-out object  ->  a box around each part   (here: each screw head)
           compare with the slots taught from ONE good object
           every slot has its part  ->  OK      (green box on each part)
           any slot empty           ->  NG      (red box where a part should be)

Every object checked is kept as a numbered picture  records/0001_OK.jpg,
records/0002_NG.jpg ... plus one line in records/log.csv - a backup of every
verdict.

    python ssr_qc.py --demo                         download the demo models + samples, check every sample
    python ssr_qc.py --demo terminal                the same for a terminal block with 8 screws (30 photos)
    python ssr_qc.py --image samples/ng_1.jpg       one picture (or a folder of pictures)
    python ssr_qc.py --camera usb --source 0       live; each new object is recorded once, q stops
    python ssr_qc.py --teach good.jpg               learn the slots from ONE good object -> ssr_slots.json
    python ssr_qc.py --teach good.jpg --any-angle   ... for an object that may lie at any angle
    python ssr_qc.py --camera usb --source 0 --keep mydata   c keeps the picture + the object cut out
    python ssr_qc.py --finder my_obj.onnx --image photos --keep mydata   no --checker yet: only cut objects out
    python ssr_qc.py --finder my_obj.onnx --checker my_parts.onnx --slots my_slots.json --camera usb --source 0
    python ssr_qc.py --camera usb --source 2 --broker 192.168.1.50   every record also to Node-RED (MQTT)

Another product - a panel with 10 screws, a tray of 30 parts - is the same
program: train AI #1 on the product (one class), AI #2 on the part (one
class), then --teach on one good product. No code to change.

Models
------
Any detector exported to ONNX in the YOLO layout works for either AI:
Ultralytics YOLOv8/11 (.onnx) or the AI Vision Trainer's model.onnx. The input
size and class names are read from the model (Ultralytics metadata, or
classes.txt beside a Trainer model.onnx). AI #2 needs only ONE class - the
part (here "screw"); an empty slot is simply a slot where no part was found.

The demo models were trained on variations of ONE product photo. They show the
idea and they work on the samples; they are not a QC system. For your line,
photograph your own objects (good and bad) and train both - the guide in this
folder walks through it with the TESR web tools.

Minimum requirement : Python 3.8+, opencv-python, numpy
Recommended         : onnxruntime (faster; without it OpenCV's own DNN runs the models)
Optional            : paho-mqtt (only for --broker)

Author: TESR Co., Ltd. - Thai Embedded Systems and Robotics
License: MIT
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import os
import platform
import sys
import time
import urllib.request
from datetime import datetime

try:
    import cv2
    import numpy as np
except ImportError:
    sys.stderr.write("[FATAL] opencv-python / numpy not found - is venv active?\n")
    raise SystemExit(2)

HERE = os.path.dirname(os.path.abspath(__file__))
VERSION = "2.1.0"
DEMO_URL = ("https://raw.githubusercontent.com/TESR-Channel/image_processing_lab/"
            "course-figures/course-figures/extra_ssr/")
DEMO_MODELS = ["ssr_finder.onnx", "screw_checker.onnx"]
# the second product: a TB-2504 terminal block (8 screws), from 30 real phone photos
TERMINAL_MODELS = ["terminal_finder.onnx", "terminal_checker.onnx"]
DEMO_SAMPLES = ["ok_1.jpg", "ok_2.jpg", "ng_1.jpg", "ng_2.jpg", "ng_3.jpg", "real_front.jpg",
                "real_front_ng.jpg", "real_angle.jpg"]
def terminal_samples():
    """The 30 phone photos: 11 with all 8 screws, 19 with some missing (numbers as taken)."""
    return (["ok_%d.jpg" % n for n in range(3327, 3338)] +
            ["ng_%d.jpg" % n for n in (3338, 3339, 3340, 3341, 3342, 3343, 3344, 3345, 3347, 3348, 3349,
                                       3350, 3353, 3354, 3355, 3356, 3357, 3358, 3359)])


GREEN, RED, AMBER, WHITE = (60, 180, 60), (40, 40, 225), (0, 170, 255), (255, 255, 255)


def log(msg, level="INFO"):
    print("[%s] %s" % (level, msg), flush=True)


def fetch(names, folder, remote=None):
    """Download the demo files once; already there = nothing to do."""
    os.makedirs(folder, exist_ok=True)
    if remote is None:
        remote = os.path.basename(os.path.normpath(folder)) + "/"
    for n in names:
        path = os.path.join(folder, n)
        if os.path.isfile(path):
            continue
        log("downloading %s ..." % n)
        try:
            urllib.request.urlretrieve(DEMO_URL + remote + n, path + ".part")
            os.replace(path + ".part", path)
        except Exception as exc:
            if os.path.exists(path + ".part"):
                os.remove(path + ".part")
            log("could not download %s (%s) - check the internet, or copy the file into %s"
                % (n, exc, folder), "FATAL")
            raise SystemExit(2)


# ==========================================================================
#  A YOLO-layout detector (Ultralytics or AI Vision Trainer .onnx)
# ==========================================================================
class Detector:
    def __init__(self, path, names=None, conf=0.4):
        self.conf, self.names, self.stretch = conf, names, False
        side = os.path.join(os.path.dirname(os.path.abspath(path)), "classes.txt")
        try:
            import onnxruntime as ort
            self.sess = ort.InferenceSession(path, providers=["CPUExecutionProvider"])
            inp = self.sess.get_inputs()[0]
            self.inp, self.size = inp.name, int(inp.shape[2])
            outs = [o.name for o in self.sess.get_outputs()]
            self.out = "output0" if "output0" in outs else outs[0]
            meta = self.sess.get_modelmeta().custom_metadata_map
            # AI Vision Trainer models are stretched to the square, Ultralytics ones letterboxed
            self.stretch = "stretch" in meta.get("preprocess", "")
            if not self.names and "names" in meta:
                import ast
                d = ast.literal_eval(meta["names"])
                self.names = [d[k] for k in sorted(d, key=int)]
            self.net, self.backend = None, "onnxruntime"
        except ImportError:
            self.net = cv2.dnn.readNetFromONNX(path)
            self.size, self.backend = 640, "OpenCV DNN"
            self.stretch = os.path.isfile(side)               # the Trainer ships classes.txt beside its model
            for s in (640, 416, 320, 224):                 # find the input size the model accepts
                try:
                    self.net.setInput(np.zeros((1, 3, s, s), np.float32))
                    self.net.forward(self.net.getUnconnectedOutLayersNames())
                    self.size = s
                    break
                except cv2.error:
                    continue
        if not self.names and os.path.isfile(side):
            with open(side, encoding="utf-8") as f:
                self.names = f.read().split()

    def __call__(self, img):
        h, w = img.shape[:2]
        if self.stretch:                                      # plain resize to the square
            sx, sy, left, top = self.size / w, self.size / h, 0, 0
            pad = cv2.resize(img, (self.size, self.size))
        else:                                                 # letterbox: keep the shape, grey bars
            sx = sy = self.size / max(h, w)
            nw, nh = max(1, int(round(w * sx))), max(1, int(round(h * sy)))
            pad = np.full((self.size, self.size, 3), 114, np.uint8)
            top, left = (self.size - nh) // 2, (self.size - nw) // 2
            pad[top:top + nh, left:left + nw] = cv2.resize(img, (nw, nh))
        blob = cv2.dnn.blobFromImage(pad, 1 / 255.0, swapRB=True)
        if self.net is None:
            out = self.sess.run([self.out], {self.inp: blob})[0]
        else:
            self.net.setInput(blob)
            outs = self.net.forward(self.net.getUnconnectedOutLayersNames())
            out = next(o for o in outs if o.ndim == 3)          # output0 [1, 4+classes, N]
        out = out[0].T
        scores = out[:, 4:]
        cls = scores.argmax(1)
        conf = scores[np.arange(len(cls)), cls]
        keep = conf >= self.conf
        out, cls, conf = out[keep], cls[keep], conf[keep]
        boxes = [[int((cx - bw / 2 - left) / sx), int((cy - bh / 2 - top) / sy), int(bw / sx), int(bh / sy)]
                 for cx, cy, bw, bh in out[:, :4]]
        idx = cv2.dnn.NMSBoxes(boxes, conf.tolist(), self.conf, 0.45) if boxes else []
        names = self.names or [str(i) for i in range(scores.shape[1])]
        return [{"box": boxes[i], "cls": names[int(cls[i])], "conf": float(conf[i])}
                for i in np.array(idx).flatten()]



def drop_inner(dets, cover=0.6):
    """A box lying mostly inside a surer box is the same relay seen twice - keep the surer one."""
    kept = []
    for d in sorted(dets, key=lambda d: -d["conf"]):
        x, y, w, h = d["box"]
        inside = False
        for k in kept:
            kx, ky, kw, kh = k["box"]
            iw = max(0, min(x + w, kx + kw) - max(x, kx))
            ih = max(0, min(y + h, ky + kh) - max(y, ky))
            if iw * ih > cover * w * h:
                inside = True
                break
        if not inside:
            kept.append(d)
    return kept


# ==========================================================================
#  Stage 1 + stage 2, and the slots
# ==========================================================================
def find_objects(frame, finder, obj_name):
    """AI #1: boxes around each object, a little slack added, left to right."""
    H, W = frame.shape[:2]
    out = []
    dets = [d for d in finder(frame) if obj_name is None or d["cls"] == obj_name]
    for d in sorted(drop_inner(dets), key=lambda d: d["box"][0]):
        x, y, w, h = d["box"]
        px, py = int(w * 0.06), int(h * 0.06)
        x1, y1, x2, y2 = max(0, x - px), max(0, y - py), min(W, x + w + px), min(H, y + h + py)
        if x2 - x1 > 8 and y2 - y1 > 8:
            out.append({"box": (x, y, w, h), "conf": d["conf"], "crop": (x1, y1, x2, y2)})
    return out


def find_parts(crop, checker, part_name):
    """AI #2 on the cut-out object: one box per part found."""
    return [p for p in checker(crop) if p["cls"] == part_name]


def load_slots(path):
    with open(path, encoding="utf-8") as f:
        s = json.load(f)
    if not s.get("slots"):
        raise ValueError("no slots in %s" % path)
    return s


def teach_pattern(parts, cw, ch, obj_name, part_name, path):
    """Any angle: keep the parts' layout itself - turned so its long side lies flat,
    centred, and sized so the layout is 1 wide. Matching later turns it back."""
    c = np.array([[p["box"][0] + p["box"][2] / 2, p["box"][1] + p["box"][3] / 2] for p in parts], float)
    mu = c.mean(0)
    w, v = np.linalg.eigh(np.cov((c - mu).T)) if len(c) > 2 else (None, None)
    ax = v[:, 1] if v is not None else (c[1] - c[0]) / (np.linalg.norm(c[1] - c[0]) + 1e-9)
    ang = math.atan2(ax[1], ax[0])
    rot = np.array([[math.cos(-ang), -math.sin(-ang)], [math.sin(-ang), math.cos(-ang)]])
    q = (c - mu) @ rot.T
    span = float(q[:, 0].max() - q[:, 0].min()) or 1.0
    q /= span
    gaps = [math.hypot(*(a - b)) for i, a in enumerate(q) for b in q[i + 1:]]
    row = 0.5 * min(gaps) if gaps else 0.1
    order = sorted(range(len(q)), key=lambda i: (round(q[i][1] / row), q[i][0]))
    size = float(np.median([max(p["box"][2], p["box"][3]) for p in parts])) / span
    data = {"object": obj_name, "part": part_name, "expect": len(q), "frame": "pattern",
            "radius": round(0.45 * min(gaps), 4) if gaps else 0.1,
            "span": round(span / math.hypot(cw, ch), 4), "size": round(size, 4),
            "slots": [{"name": str(k + 1), "x": round(float(q[i][0]), 4), "y": round(float(q[i][1]), 4)}
                      for k, i in enumerate(order)],
            "_note": "frame pattern: x, y are the parts' layout, 1 = its width, any angle. span = layout width "
                     "/ object box diagonal when taught. radius = how far (layout widths) a part may sit from "
                     "its slot. The object may be turned any way, so slot names can swap ends."}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    log("taught   : %d slots (any angle) from one good %s -> %s" % (len(q), obj_name or "object", path))
    for sl in data["slots"]:
        log("  slot %-4s at x %+.2f  y %+.2f of the layout" % (sl["name"], sl["x"], sl["y"]))
    return 0


def fit_pattern(centres, slots, diag):
    """Lay the taught layout over the parts found: try each pair of parts against each pair of
    slots (turn + size + shift), keep the fit that covers the most parts. Returns where every
    slot is in the picture, and which part (if any) sits in it."""
    tm = np.array([[sl["x"], sl["y"]] for sl in slots["slots"]], float)
    pts = np.array(centres, float)
    if len(pts) < 2:
        return None
    s0 = slots.get("span", 0) * diag
    best = None
    for i in range(len(pts)):
        for j in range(i + 1, len(pts)):
            d = pts[j] - pts[i]
            dp = math.hypot(*d)
            for a in range(len(tm)):
                for b in range(len(tm)):
                    if a == b:
                        continue
                    e = tm[b] - tm[a]
                    dt = math.hypot(*e)
                    if dt < 1e-6:
                        continue
                    sc = dp / dt
                    if s0 and not 0.6 * s0 < sc < 1.6 * s0:
                        continue
                    th = math.atan2(d[1], d[0]) - math.atan2(e[1], e[0])
                    M = sc * np.array([[math.cos(th), -math.sin(th)], [math.sin(th), math.cos(th)]])
                    proj = tm @ M.T + (pts[i] - M @ tm[a])
                    dist = np.linalg.norm(proj[:, None, :] - pts[None, :, :], axis=2)
                    r = slots.get("radius", 0.1) * sc
                    taken, hit, res = set(), {}, 0.0
                    for k in np.argsort(dist.min(1)):
                        cand = [m for m in np.argsort(dist[k]) if m not in taken and dist[k, m] < r]
                        if cand:
                            taken.add(cand[0]); hit[int(k)] = int(cand[0]); res += dist[k, cand[0]]
                    key = (len(hit), -res)
                    if best is None or key > best[0]:
                        best = (key, proj, hit, sc)
    return best[1], best[2], best[3]


def teach(frame, finder, checker, obj_name, part_name, path, any_angle=False):
    """Learn where the parts sit, from ONE good object: positions are kept as fractions of the object box."""
    objs = find_objects(frame, finder, obj_name)
    if not objs:
        log("teach: AI #1 found no object in the picture", "FATAL")
        return 2
    o = max(objs, key=lambda o: o["conf"])
    x1, y1, x2, y2 = o["crop"]
    cw, ch = x2 - x1, y2 - y1
    parts = find_parts(frame[y1:y2, x1:x2], checker, part_name)
    if not parts:
        log("teach: AI #2 found no part inside the object", "FATAL")
        return 2
    if any_angle:
        return teach_pattern(parts, cw, ch, obj_name, part_name, path)
    pts = [((p["box"][0] + p["box"][2] / 2) / cw, (p["box"][1] + p["box"][3] / 2) / ch,
            p["box"][2] / cw, p["box"][3] / ch) for p in parts]
    # number them like reading a page: top row left to right, then the next row
    row_h = 0.5 * float(np.median([q[3] for q in pts]))
    pts.sort(key=lambda q: (round(q[1] / row_h), q[0]))
    gaps = [math.hypot(a[0] - b[0], a[1] - b[1]) for i, a in enumerate(pts) for b in pts[i + 1:]]
    radius = round(min(0.5 * min(gaps), 0.25) if gaps else 0.25, 3)
    data = {"object": obj_name, "part": part_name, "expect": len(pts), "radius": radius,
            "slots": [{"name": str(i + 1), "x": round(q[0], 4), "y": round(q[1], 4),
                       "w": round(q[2], 4), "h": round(q[3], 4)} for i, q in enumerate(pts)],
            "_note": "x, y, w, h are fractions of the object box. radius = how far (fraction of the box) a part "
                     "may sit from its slot. Rename the slots freely (e.g. as printed on the product)."}
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
    log("taught   : %d slots from one good %s -> %s" % (len(pts), obj_name or "object", path))
    for s in data["slots"]:
        log("  slot %-4s at x %.2f  y %.2f of the box" % (s["name"], s["x"], s["y"]))
    return 0


def inspect(frame, finder, checker, obj_name, part_name, slots, expect):
    """Every object in the picture: which slots have their part. OK only if all do."""
    results = []
    for o in find_objects(frame, finder, obj_name):
        x1, y1, x2, y2 = o["crop"]
        cw, ch = x2 - x1, y2 - y1
        parts = find_parts(frame[y1:y2, x1:x2], checker, part_name)
        for p in parts:
            p["box"] = [p["box"][0] + x1, p["box"][1] + y1, p["box"][2], p["box"][3]]
        empty = []
        if slots and slots.get("frame") == "pattern":
            centres = [(p["box"][0] + p["box"][2] / 2, p["box"][1] + p["box"][3] / 2) for p in parts]
            fit = fit_pattern(centres, slots, math.hypot(cw, ch))
            if fit is None:
                ok = False                                    # under 2 parts: nothing to lay the layout on
            else:
                proj, hit, sc = fit
                size = int(slots.get("size", 0.1) * sc)
                for k, sl in enumerate(slots["slots"]):
                    if k not in hit:
                        sx, sy = proj[k]
                        empty.append({"name": sl["name"], "box": [int(sx - size / 2), int(sy - size / 2), size, size]})
                ok = not empty and len(hit) == len(slots["slots"])
        elif slots:
            free = list(range(len(parts)))
            r = slots.get("radius", 0.2) * math.hypot(cw, ch) / math.sqrt(2)
            for s in slots["slots"]:
                sx, sy = x1 + s["x"] * cw, y1 + s["y"] * ch
                best, bd = None, r
                for i in free:
                    bx, by, bw, bh = parts[i]["box"]
                    dd = math.hypot(bx + bw / 2 - sx, by + bh / 2 - sy)
                    if dd < bd:
                        best, bd = i, dd
                if best is None:
                    w, h = s.get("w", 0.12) * cw, s.get("h", 0.12) * ch
                    empty.append({"name": s["name"], "box": [int(sx - w / 2), int(sy - h / 2), int(w), int(h)]})
                else:
                    free.remove(best)
            ok = not empty
        else:
            ok = len(parts) >= expect
        o.update({"ok": ok, "found": len(parts), "expect": expect, "parts": parts, "empty": empty})
        results.append(o)
    return results


# ==========================================================================
#  Pictures, records, messages
# ==========================================================================
def label(img, text, x, y, col, scale):
    (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, scale, 2)
    y = max(th + 12, y)
    cv2.rectangle(img, (x, y - th - 12), (x + tw + 12, y), col, -1)
    cv2.putText(img, text, (x + 6, y - 7), cv2.FONT_HERSHEY_SIMPLEX, scale, WHITE, 2, cv2.LINE_AA)


def draw(frame, results, obj_name):
    big = max(1.0, frame.shape[1] / 700.0)
    for r in results:
        for p in r["parts"]:                                       # found: green
            x, y, w, h = p["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), GREEN, 3)
        for e in r["empty"]:                                       # should be here, is not: red
            x, y, w, h = e["box"]
            cv2.rectangle(frame, (x, y), (x + w, y + h), RED, 3)
            label(frame, e["name"], x, y, RED, 0.6)
        x, y, w, h = r["box"]
        col = GREEN if r["ok"] else RED
        cv2.rectangle(frame, (x, y), (x + w, y + h), col, 4)
        tag = ("#%04d " % r["seq"] if r.get("seq") else "") + ("OK" if r["ok"] else "NG")
        label(frame, tag, x, y, col, big)
    if not results:
        cv2.putText(frame, "no %s in view" % (obj_name or "object"), (16, 40), cv2.FONT_HERSHEY_SIMPLEX,
                    1.0, AMBER, 2, cv2.LINE_AA)
    return frame


class Records:
    """records/0001_OK.jpg, 0002_NG.jpg ... and records/log.csv; numbering carries on across runs."""

    def __init__(self, folder):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.csv = os.path.join(folder, "log.csv")
        self.seq = 0
        if os.path.isfile(self.csv):
            with open(self.csv, encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    try:
                        self.seq = max(self.seq, int(row["seq"]))
                    except (KeyError, ValueError):
                        pass
        else:
            with open(self.csv, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["seq", "time", "result", "found", "expect", "empty_slots", "source", "picture"])

    def number(self, results):
        for r in results:
            self.seq += 1
            r["seq"] = self.seq
            r["time"] = datetime.now().isoformat(timespec="seconds")

    def save(self, picture, results, source):
        for r in results:
            name = "%04d_%s.jpg" % (r["seq"], "OK" if r["ok"] else "NG")
            r["picture"] = os.path.join(self.folder, name)
            cv2.imwrite(r["picture"], picture)                    # the whole labelled picture
            with open(self.csv, "a", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow([r["seq"], r["time"], "OK" if r["ok"] else "NG", r["found"], r["expect"],
                                        " ".join(e["name"] for e in r["empty"]), source, name])


def report(results, source=""):
    if not results:
        log("%sno object found" % (source + "  " if source else ""), "WARN")
    for r in results:
        seq = ("#%04d  " % r["seq"]) if r.get("seq") else ""
        line = "%s%sfound %d/%d" % (seq, source + "  " if source else "", r["found"], r["expect"])
        if r["empty"]:
            line += "  empty slot %s" % ", ".join(e["name"] for e in r["empty"])
        log(line, "OK" if r["ok"] else "NG")


def keep(frame, results, folder, stem):
    """Save the plain picture and each object cut out - photos for training your own two models."""
    for sub in ("frames", "crops"):
        os.makedirs(os.path.join(folder, sub), exist_ok=True)
    cv2.imwrite(os.path.join(folder, "frames", stem + ".jpg"), frame)
    for k, r in enumerate(results, 1):
        x1, y1, x2, y2 = r["crop"]
        cv2.imwrite(os.path.join(folder, "crops", "%s_obj%d.jpg" % (stem, k)), frame[y1:y2, x1:x2])
    log("kept     : %s - picture + %d object crop(s) in %s" % (stem, len(results), folder))


# ==========================================================================
#  Camera / video / stream - the same words as predict.py and the ROI runner:
#  --camera usb|csi|ip|file  --source 0 | rtsp://... | clip.mp4
# ==========================================================================
def is_jetson():
    return os.path.isfile("/etc/nv_tegra_release")


class PiCam:
    """A Raspberry Pi ribbon camera through Picamera2, read like a cv2.VideoCapture."""

    def __init__(self, index, width=1280, height=720):
        from picamera2 import Picamera2
        self.cam = Picamera2(index)
        self.cam.configure(self.cam.create_preview_configuration(
            main={"format": "RGB888", "size": (width, height)}))     # RGB888 is BGR to OpenCV
        self.cam.start()
        time.sleep(0.5)

    def isOpened(self):
        return True

    def read(self):
        return True, self.cam.capture_array()

    def get(self, prop):
        return 0

    def set(self, prop, value):
        return False

    def release(self):
        self.cam.stop()


def open_camera(kind, source):
    """(capture, what to call it, is_a_file). kind: usb | csi | ip | file."""
    src = source if source is not None else ("0" if kind in ("usb", "csi") else None)
    if kind in ("usb", "csi"):
        if not str(src).isdigit():
            log("--camera %s needs an index in --source: 0, 1, 2 ... (not %r)" % (kind, src), "FATAL")
            return None, str(src), False
        idx = int(src)
        if kind == "csi":
            if is_jetson():
                pipe = ("nvarguscamerasrc sensor-id=%d ! video/x-raw(memory:NVMM),width=1280,height=720,"
                        "framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! "
                        "video/x-raw,format=BGR ! appsink drop=1 max-buffers=1" % idx)
                return cv2.VideoCapture(pipe, cv2.CAP_GSTREAMER), "csi camera %d (Jetson)" % idx, False
            try:
                return PiCam(idx), "csi camera %d (Picamera2)" % idx, False
            except ImportError:
                log("a ribbon camera needs Picamera2: sudo apt install -y python3-picamera2 "
                    "(install_pi.sh makes the venv that can see it)", "FATAL")
                return None, "csi camera", False
        api = cv2.CAP_DSHOW if platform.system() == "Windows" else cv2.CAP_ANY
        return cv2.VideoCapture(idx, api), "usb camera %d" % idx, False
    if kind == "ip":
        if not src or str(src).isdigit():
            log("--camera ip needs a stream URL in --source, e.g. rtsp://user:pass@192.168.1.64:554/stream1",
                "FATAL")
            return None, str(src), False
        os.environ.setdefault("OPENCV_FFMPEG_CAPTURE_OPTIONS", "rtsp_transport;tcp")
        return cv2.VideoCapture(src, cv2.CAP_FFMPEG), str(src).split("@")[-1], False
    # file
    if not src or not os.path.isfile(src):
        log("no video at %s" % src, "FATAL")
        return None, str(src), True
    try:
        shown = os.path.relpath(src)
    except ValueError:                                     # another drive on Windows
        shown = src
    if shown.startswith(".."):                             # far away: the file name says enough
        shown = os.path.basename(src)
    return cv2.VideoCapture(src), shown, True


def camera_kind(text):
    """--camera usb|csi|ip|file; a bare number (the old --camera 0) still means a USB index."""
    t = str(text).strip().lower()
    if t in ("usb", "csi", "ip", "file"):
        return t
    if t.isdigit():
        return "usb:" + t
    raise argparse.ArgumentTypeError("use --camera usb, csi, ip or file (then --source ...)")


def resolve_source(args, default_file=None):
    """Turn --camera/--source (and the older --video/--stream) into (kind, source)."""
    kind, source = args.camera, args.source
    if kind and kind.startswith("usb:"):                    # --camera 2  ==  --camera usb --source 2
        kind, source = "usb", source or kind[4:]
    if getattr(args, "stream", None):
        kind, source = "ip", args.stream
    if getattr(args, "video", None):
        kind, source = "file", args.video
    if kind is None:
        if source is not None:                             # --source alone: guess from what it is
            s = str(source)
            kind = "usb" if s.isdigit() else "ip" if "://" in s else "file"
        elif default_file:
            kind, source = "file", default_file
        else:
            kind, source = "usb", "0"
    return kind, source


def has_screen():
    return not (platform.system() == "Linux" and not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")))


def keep_run(args, finder, obj_name):
    """--keep with AI #1 only: save each picture and every object cut out of it, nothing judged."""
    if args.image:
        files = sorted(glob.glob(os.path.join(args.image, "*"))) if os.path.isdir(args.image) else [args.image]
        n = 0
        for f in files:
            if not f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp")):
                continue
            frame = cv2.imread(f)
            if frame is None:
                log("cannot read %s" % f, "WARN")
                continue
            res = find_objects(frame, finder, obj_name)
            if not res:
                log("%s  no %s found - nothing cut out" % (os.path.basename(f), obj_name), "WARN")
            keep(frame, res, args.keep, os.path.splitext(os.path.basename(f))[0])
            n += len(res)
        log("done     : %d crop(s) in %s - label them for AI #2" % (n, os.path.join(args.keep, "crops")))
        return 0
    kind, src_ = resolve_source(args)
    cap, source, _ = open_camera(kind, src_)
    if cap is None or not cap.isOpened():
        log("cannot open %s" % source, "FATAL")
        return 2
    window = not args.headless and has_screen()
    if not window:
        log("--keep on a camera needs a window: press c to keep a picture", "FATAL")
        return 2
    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            res = find_objects(frame, finder, obj_name)
            pic = frame.copy()
            for r in res:
                x1, y1, x2, y2 = r["crop"]
                cv2.rectangle(pic, (x1, y1), (x2, y2), AMBER, 3)
            cv2.imshow("TESR QC - c keep for training, q stop", pic)
            k = cv2.waitKey(1) & 0xFF
            if k in (ord("q"), 27):
                break
            if k == ord("c"):
                keep(frame, res, args.keep, datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3])
    except KeyboardInterrupt:
        pass
    finally:
        cap.release()
        cv2.destroyAllWindows()
    return 0


def main():
    ap = argparse.ArgumentParser(description="QC with two AIs: find the object, then check the parts inside it.")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--image", help="a picture, or a folder of pictures")
    src.add_argument("--camera", type=camera_kind, metavar="{usb,csi,ip,file}",
                     help="live: usb webcam, csi ribbon camera, ip stream, or a video file")
    ap.add_argument("--source", help="usb/csi: an index 0, 1, 2 ... - ip: rtsp://... - file: a path")
    src.add_argument("--video", help=argparse.SUPPRESS)       # older spellings, still understood
    src.add_argument("--stream", help=argparse.SUPPRESS)
    src.add_argument("--demo", nargs="?", const="ssr", choices=["ssr", "terminal"],
                     help="download the demo models + samples and check every sample: ssr (default) or terminal")
    src.add_argument("--teach", help="a picture of ONE good object: learn its slots and write --slots")
    ap.add_argument("--finder", default=os.path.join(HERE, "models", "ssr_finder.onnx"), help="AI #1: the object")
    ap.add_argument("--checker", help="AI #2: the part (default models/screw_checker.onnx; "
                                      "leave it out with --keep to only cut objects out for training)")
    ap.add_argument("--finder-classes", help="AI #1 class names, comma separated (only if the file has none)")
    ap.add_argument("--checker-classes", help="AI #2 class names, comma separated (only if the file has none)")
    ap.add_argument("--object", help="which AI #1 class is the object (default: its first class)")
    ap.add_argument("--part", help="which AI #2 class is the part (default: 'screw' if there, else its first class)")
    ap.add_argument("--slots", default=os.path.join(HERE, "ssr_slots.json"), help="where the parts should be")
    ap.add_argument("--any-angle", action="store_true",
                    help="with --teach: the object may lie at any angle (keep the parts' layout, not box fractions)")
    ap.add_argument("--expect", type=int, help="parts per object when there is no slots file (default 4)")
    ap.add_argument("--conf", type=float, default=0.5, help="AI #1 threshold (default 0.5)")
    ap.add_argument("--conf2", type=float, default=0.4, help="AI #2 threshold (default 0.4)")
    ap.add_argument("--records", default="records", help="numbered pictures + log.csv go here (default records)")
    ap.add_argument("--no-records", action="store_true", help="do not keep pictures")
    ap.add_argument("--settle", type=int, default=5, help="live: frames the verdict must hold before it is recorded")
    ap.add_argument("--keep", help="folder for training photos: the plain picture + each object cut out "
                                   "(every picture with --image; key c on a live camera)")
    ap.add_argument("--headless", action="store_true", help="no window")
    ap.add_argument("--broker", help="also publish every record over MQTT to this broker (Node-RED)")
    ap.add_argument("--line", default="line1", help="line name in the MQTT topic (default line1)")
    args = ap.parse_args()

    models = os.path.join(HERE, "models")
    # --keep without --checker: AI #2 does not exist yet - only cut each object out (photos for training it)
    keep_only = bool(args.keep) and args.checker is None and not args.demo
    if args.checker is None:
        args.checker = os.path.join(models, "screw_checker.onnx")
    if args.demo == "terminal":                       # same program, second product: three things change
        if args.finder == ap.get_default("finder"):
            args.finder = os.path.join(models, TERMINAL_MODELS[0])
        if args.checker == os.path.join(models, "screw_checker.onnx"):
            args.checker = os.path.join(models, TERMINAL_MODELS[1])
        if args.slots == ap.get_default("slots"):
            args.slots = os.path.join(HERE, "terminal_slots.json")
        fetch(TERMINAL_MODELS, models)
        fetch(terminal_samples(), os.path.join(HERE, "samples_terminal"))
        if args.slots == os.path.join(HERE, "terminal_slots.json"):
            fetch(["terminal_slots.json"], HERE, remote="")      # the 8 slots, taught from ok_3327.jpg
        args.image = os.path.join(HERE, "samples_terminal")
    else:
        names = {os.path.basename(p) for p in ((args.finder,) if keep_only else (args.finder, args.checker))
                 if not os.path.isfile(p) and os.path.dirname(os.path.abspath(p)) == models}
        if args.demo or names & set(DEMO_MODELS):
            fetch(DEMO_MODELS, models)
        if names & set(TERMINAL_MODELS):
            fetch(TERMINAL_MODELS, models)
        if args.demo:
            fetch(DEMO_SAMPLES, os.path.join(HERE, "samples"))
            args.image = os.path.join(HERE, "samples")
    for p in (args.finder,) if keep_only else (args.finder, args.checker):
        if not os.path.isfile(p):
            log("model not found: %s" % p, "FATAL")
            return 2
    split = lambda s: [x.strip() for x in s.split(",")] if s else None
    finder = Detector(args.finder, split(args.finder_classes), args.conf)
    taught = load_slots(args.slots) if os.path.isfile(args.slots) else {}
    finder.names = finder.names or [taught.get("object") or "object"]     # a model without names: use the slots file's
    obj_name = args.object or finder.names[0]
    log("version  : ssr_qc v%s" % VERSION)
    log("AI #1    : %s (%s, %d px) - object = %s" % (os.path.basename(args.finder), finder.backend, finder.size, obj_name))
    if keep_only:
        log("AI #2    : none yet - only cutting each %s out into %s/crops" % (obj_name, args.keep))
        return keep_run(args, finder, obj_name)
    checker = Detector(args.checker, split(args.checker_classes), args.conf2)
    checker.names = checker.names or [taught.get("part") or "part"]
    part_name = args.part or ("screw" if "screw" in checker.names else checker.names[0])
    log("AI #2    : %s (%s, %d px) - part = %s" % (os.path.basename(args.checker), checker.backend, checker.size, part_name))

    if args.teach:
        frame = cv2.imread(args.teach)
        if frame is None:
            log("cannot read %s" % args.teach, "FATAL")
            return 2
        return teach(frame, finder, checker, obj_name, part_name, args.slots, args.any_angle)

    slots = taught or None
    if slots:
        expect = len(slots["slots"])
        log("slots    : %s - %d %s per %s" % (os.path.basename(args.slots), expect, part_name, obj_name))
    else:
        expect = args.expect or 4
        log("no slots file (%s) - counting only: %d %s = OK. Teach one good %s with --teach to also mark "
            "the empty slots" % (args.slots, expect, part_name, obj_name), "WARN")
    rec = None if args.no_records else Records(args.records)
    if rec:
        log("records  : %s/ (numbered pictures + log.csv, next #%04d)" % (args.records, rec.seq + 1))

    client = None
    if args.broker:
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            log("paho-mqtt not installed - pip install paho-mqtt (needed for --broker only)", "FATAL")
            return 2
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="tesr-qc-%d" % os.getpid())
        try:
            client.connect(args.broker, 1883, 30)
        except OSError as exc:
            log("cannot reach the broker at %s:1883 (%s) - is Node-RED running with a broker deployed?"
                % (args.broker, exc), "FATAL")
            return 2
        client.loop_start()
        log("mqtt     : publishing tesr/qc/%s/result on %s" % (args.line, args.broker))

    def record(frame, plain, results, source):
        """Number, keep and announce each object checked."""
        if rec:
            rec.number(results)
        pic = draw(frame, results, obj_name)
        if rec:
            rec.save(pic, results, source)
        report(results, source)
        if client:
            for r in results:
                info = client.publish("tesr/qc/%s/result" % args.line, json.dumps(
                    {"seq": r.get("seq"), "time": r.get("time", datetime.now().isoformat(timespec="seconds")),
                     "result": "OK" if r["ok"] else "NG", "found": r["found"], "expect": r["expect"],
                     "empty": [e["name"] for e in r["empty"]], "picture": r.get("picture")}))
                info.wait_for_publish(2)                           # sent before the next picture / before exit
        return pic

    window = not args.headless and has_screen()
    try:
        if args.image:                                             # one picture or a folder of them
            files = sorted(glob.glob(os.path.join(args.image, "*"))) if os.path.isdir(args.image) else [args.image]
            files = [f for f in files if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))]
            for f in files:
                frame = cv2.imread(f)
                if frame is None:
                    log("cannot read %s" % f, "WARN")
                    continue
                res = inspect(frame, finder, checker, obj_name, part_name, slots, expect)
                if args.keep:
                    keep(frame, res, args.keep, os.path.splitext(os.path.basename(f))[0])
                pic = record(frame, None, res, os.path.basename(f))
                if window:
                    cv2.imshow("TESR QC - any key: next, q: quit", pic)
                    if cv2.waitKey(0) & 0xFF in (ord("q"), 27):
                        break
            return 0

        kind, src_ = resolve_source(args)
        cap, source, _ = open_camera(kind, src_)
        if cap is None:
            return 2
        if not cap.isOpened():
            log("cannot open %s" % source, "FATAL")
            if kind == "usb":
                log("try another index: --camera usb --source 0 (then 1, 2) - and close any app using the camera",
                    "HINT")
            return 2
        # one record per object: wait until the verdict holds for --settle frames, record it once,
        # then wait for the view to be empty for --settle frames before the next one counts
        last, steady, done, gone = None, 0, False, 0
        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                plain = frame.copy()
                res = inspect(frame, finder, checker, obj_name, part_name, slots, expect)
                key = tuple((r["ok"], tuple(e["name"] for e in r["empty"])) for r in res)
                steady = steady + 1 if key == last and res else 0
                last = key
                gone = gone + 1 if not res else 0
                if gone >= args.settle:
                    done = False
                k = 255
                if res and not done and steady >= args.settle:
                    pic = record(frame, plain, res, source)
                    done = True
                else:
                    pic = draw(frame, res, obj_name)
                if window:
                    cv2.imshow("TESR QC - q stop, r record now, c keep for training", pic)
                    k = cv2.waitKey(1) & 0xFF
                    if k in (ord("q"), 27):
                        break
                    if k == ord("r") and res:                       # record this one again / by hand
                        record(plain.copy(), plain, inspect(plain.copy(), finder, checker, obj_name, part_name,
                                                            slots, expect), source)
                        done = True
                    if k == ord("c") and args.keep:
                        keep(plain, res, args.keep, datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3])
        except KeyboardInterrupt:
            pass
        finally:
            cap.release()
        return 0
    finally:
        cv2.destroyAllWindows()
        if client:
            client.loop_stop()
            client.disconnect()


if __name__ == "__main__":
    sys.exit(main())
