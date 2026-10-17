#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the sample images for the Codes & markers tab.

These are GENERATED illustrations, not photographs - stated plainly in the
README so nobody mistakes them for a field capture. They are deliberately not
pixel-perfect: each code is warped slightly, lit unevenly, softened and saved
as JPEG, because that is what a camera does to a printed code and because
OpenCV's barcode detector will not decode a razor-sharp synthetic render.

Run:  python3 _build/make_samples.py
Every image is verified by decoding it back before it is written.
"""
import os
import sys

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "samples")
RNG = np.random.RandomState(20261018)

ARUCO_DICT = cv2.aruco.DICT_4X4_50


# --------------------------------------------------------------- the codes
def aruco(marker_id, px=200, border=1):
    d = cv2.aruco.getPredefinedDictionary(ARUCO_DICT)
    m = cv2.aruco.generateImageMarker(d, marker_id, px, borderBits=border)
    pad = int(px * 0.18)
    return cv2.copyMakeBorder(m, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)


def qr(text, px=220, level=cv2.QRCodeEncoder_CORRECT_LEVEL_M):
    params = cv2.QRCodeEncoder_Params()
    params.correction_level = level
    small = cv2.QRCodeEncoder.create(params).encode(text)
    k = max(1, px // small.shape[0])
    big = cv2.resize(small, None, fx=k, fy=k, interpolation=cv2.INTER_NEAREST)
    pad = 4 * k
    return cv2.copyMakeBorder(big, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255)


EAN_L = ["0001101", "0011001", "0010011", "0111101", "0100011",
         "0110001", "0101111", "0111011", "0110111", "0001011"]
EAN_G = ["0100111", "0110011", "0011011", "0100001", "0011101",
         "0111001", "0000101", "0010001", "0001001", "0010111"]
EAN_R = ["1110010", "1100110", "1101100", "1000010", "1011100",
         "1001110", "1010000", "1000100", "1001000", "1110100"]
EAN_P = ["LLLLLL", "LLGLGG", "LLGGLG", "LLGGGL", "LGLLGG",
         "LGGLLG", "LGGGLL", "LGLGLG", "LGLGGL", "LGGLGL"]


def ean13(twelve, module=3):
    total = sum((3 if i % 2 else 1) * int(c) for i, c in enumerate(twelve))
    code = twelve + str((10 - total % 10) % 10)
    parity = EAN_P[int(code[0])]
    bits = "101"
    for i, ch in enumerate(code[1:7]):
        bits += (EAN_L if parity[i] == "L" else EAN_G)[int(ch)]
    bits += "01010"
    for ch in code[7:]:
        bits += EAN_R[int(ch)]
    bits += "101"
    quiet = 11
    w = (95 + 2 * quiet) * module
    h = int(w * 0.40)
    img = np.full((h, w), 255, np.uint8)
    for i, bit in enumerate(bits):
        if bit == "1":
            x = (quiet + i) * module
            img[: int(h * 0.86), x:x + module] = 0
    # the human-readable line, the way a real label carries it
    cv2.putText(img, code, (quiet * module, h - 2), cv2.FONT_HERSHEY_SIMPLEX,
                module * 0.16, 0, max(1, module // 3), cv2.LINE_AA)
    return cv2.copyMakeBorder(img, module * 6, module * 6, module * 6, module * 6,
                              cv2.BORDER_CONSTANT, value=255), code


# -------------------------------------------------------------- the scene
def surface(w, h, base=(206, 203, 198)):
    """A plain work surface with gentle, uneven lighting."""
    img = np.zeros((h, w, 3), np.float32)
    img[:] = base
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    # one soft light from the upper left, so the scene is not flat
    fall = 1.06 - 0.30 * (((xx / w) - 0.25) ** 2 + ((yy / h) - 0.2) ** 2)
    img *= fall[:, :, None]
    img += RNG.normal(0, 1.6, img.shape)
    return np.clip(img, 0, 255).astype(np.uint8)


def paste(scene, code, cx, cy, scale=1.0, angle=0.0, skew=0.0, label=None):
    """Drop a code onto the scene as a slightly tilted piece of paper."""
    g = code if code.ndim == 2 else cv2.cvtColor(code, cv2.COLOR_BGR2GRAY)
    g = cv2.resize(g, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    h, w = g.shape
    card = np.full((h, w, 3), 252, np.uint8)
    card[:, :, 0] = g; card[:, :, 1] = g; card[:, :, 2] = g

    if label:
        strip = np.full((26, w, 3), 252, np.uint8)
        cv2.putText(strip, label, (6, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (70, 70, 72), 1, cv2.LINE_AA)
        card = np.vstack([card, strip])
        h += 26

    pad = 14
    card = cv2.copyMakeBorder(card, pad, pad, pad, pad, cv2.BORDER_CONSTANT,
                              value=(250, 249, 247))
    h, w = card.shape[:2]

    # a small perspective tilt, as if the paper is not exactly face-on
    d = skew * w
    src = np.float32([[0, 0], [w, 0], [w, h], [0, h]])
    dst = np.float32([[d * RNG.uniform(0.3, 1.0), d * RNG.uniform(0.3, 1.0)],
                      [w - d * RNG.uniform(0.3, 1.0), d * RNG.uniform(0.0, 0.7)],
                      [w - d * RNG.uniform(0.0, 0.7), h - d * RNG.uniform(0.3, 1.0)],
                      [d * RNG.uniform(0.0, 0.7), h - d * RNG.uniform(0.3, 1.0)]])
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(card, M, (w, h), borderValue=(0, 0, 0))
    mask = cv2.warpPerspective(np.full((h, w), 255, np.uint8), M, (w, h))

    if angle:
        R = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
        warped = cv2.warpAffine(warped, R, (w, h), borderValue=(0, 0, 0))
        mask = cv2.warpAffine(mask, R, (w, h))

    H, W = scene.shape[:2]
    x0, y0 = int(cx - w / 2), int(cy - h / 2)
    x1, y1 = x0 + w, y0 + h
    if x0 < 0 or y0 < 0 or x1 > W or y1 > H:
        raise ValueError(f"card at ({cx},{cy}) size {w}x{h} falls outside {W}x{H}")

    # a soft shadow so the paper sits on the surface instead of floating
    sh = cv2.GaussianBlur(mask, (31, 31), 0).astype(np.float32) / 255.0
    region = scene[y0 + 6:y1 + 6, x0 + 5:x1 + 5] if (y1 + 6 <= H and x1 + 5 <= W) else None
    if region is not None:
        scene[y0 + 6:y1 + 6, x0 + 5:x1 + 5] = (region * (1 - 0.22 * sh[:, :, None])).astype(np.uint8)

    m3 = (mask.astype(np.float32) / 255.0)[:, :, None]
    scene[y0:y1, x0:x1] = (scene[y0:y1, x0:x1] * (1 - m3) + warped * m3).astype(np.uint8)
    return scene


def finish(scene, blur=3, noise=2.0, quality=90):
    """What a camera adds: a little defocus, a little sensor noise, JPEG."""
    out = cv2.GaussianBlur(scene, (blur, blur), 0)
    out = np.clip(out.astype(np.float32) + RNG.normal(0, noise, out.shape), 0, 255).astype(np.uint8)
    return out, quality


# ------------------------------------------------------------- verification
def verify(path, want_aruco=(), want_qr=(), want_bar=()):
    img = cv2.imread(path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ok = True
    notes = []

    det = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(ARUCO_DICT),
                                  cv2.aruco.DetectorParameters())
    corners, ids, _ = det.detectMarkers(gray)
    got_ids = sorted(ids.flatten().tolist()) if ids is not None else []
    if sorted(want_aruco) != got_ids:
        ok = False
    notes.append(f"aruco want={sorted(want_aruco)} got={got_ids}")

    # Multi first, then single - the same two-step the tool ships, because
    # detectAndDecodeMulti quietly returns nothing on a busy scene where the
    # single-code path reads the very same symbol.
    got_qr = []
    qd = cv2.QRCodeDetector()
    found, texts, pts, _ = qd.detectAndDecodeMulti(gray)
    if found:
        got_qr = sorted([t for t in texts if t])
    if not got_qr:
        one = qd.detectAndDecode(gray)[0]
        if one:
            got_qr = [one]
    if sorted(want_qr) != got_qr:
        ok = False
    notes.append(f"qr want={sorted(want_qr)} got={got_qr}")

    got_bar = []
    for k in (0, 5, 7):
        source = cv2.GaussianBlur(gray, (k, k), 0) if k else gray
        okb, vals, types, _ = cv2.barcode.BarcodeDetector().detectAndDecodeWithType(source)
        if okb and any(vals):
            got_bar = sorted([v for v in vals if v])
            notes.append(f"barcode decoded at blur={k}")
            break
    if sorted(want_bar) != got_bar:
        ok = False
    notes.append(f"barcode want={sorted(want_bar)} got={got_bar}")
    return ok, notes


# ------------------------------------------------------------------- build
def build_mixed():
    s = surface(1280, 820)
    s = paste(s, aruco(7), 300, 250, scale=1.15, angle=-5, skew=0.05, label="ArUco  DICT_4X4_50  id 7")
    s = paste(s, qr("https://tesracademy.com"), 880, 240, scale=1.0, angle=4, skew=0.04, label="QR")
    bar, code = ean13("885012341234", module=3)
    s = paste(s, bar, 620, 640, scale=1.0, angle=-1.5, skew=0.012, label="EAN-13")
    return s, dict(want_aruco=[7], want_qr=["https://tesracademy.com"], want_bar=[code])


def build_aruco():
    # Deliberately generous: big markers, gentle tilts, light compression.
    # A browser decodes JPEG through its own colour management, which shifts
    # pixel values just enough that borderline markers identify in Python but
    # not in the page - and the page is where learners actually use this.
    s = surface(1340, 860, base=(198, 199, 203))
    s = paste(s, aruco(0), 300, 250, scale=1.15, angle=-6, skew=0.030)
    s = paste(s, aruco(7), 740, 225, scale=1.00, angle=4, skew=0.025)
    s = paste(s, aruco(13), 1090, 320, scale=1.05, angle=-3, skew=0.030)
    s = paste(s, aruco(23), 420, 630, scale=1.10, angle=7, skew=0.020)
    s = paste(s, aruco(41), 900, 650, scale=1.00, angle=-8, skew=0.028)
    return s, dict(want_aruco=[0, 7, 13, 23, 41])


def build_barcode():
    s = surface(1100, 700, base=(212, 210, 205))
    bar, code = ean13("885099912345", module=4)
    s = paste(s, bar, 550, 300, scale=1.0, angle=-1.0, skew=0.008, label="PART A-2140   LOT 26-10")
    qrc = qr("TESR-2140")
    s = paste(s, qrc, 880, 560, scale=0.55, angle=3, skew=0.03)
    return s, dict(want_qr=["TESR-2140"], want_bar=[code])


def main():
    # blur/quality per scene: a barcode needs softening to decode at all, an
    # ArUco sheet only suffers from it
    jobs = [("codes_mixed.jpg", build_mixed, dict(blur=3, noise=2.0, quality=92)),
            ("codes_aruco.jpg", build_aruco, dict(blur=1, noise=1.2, quality=96)),
            ("codes_barcode.jpg", build_barcode, dict(blur=3, noise=2.0, quality=92))]
    failures = 0
    for name, fn, opts in jobs:
        scene, want = fn()
        out, q = finish(scene, **opts)
        path = os.path.join(OUT, name)
        cv2.imwrite(path, out, [cv2.IMWRITE_JPEG_QUALITY, q])
        ok, notes = verify(path, **want)
        size = os.path.getsize(path)
        print(f"{'PASS' if ok else 'FAIL'}  {name}  {out.shape[1]}x{out.shape[0]}  {size//1024} KB")
        for n in notes:
            print("        ", n)
        if not ok:
            failures += 1
    if failures:
        print(f"\n{failures} sample(s) did not decode - not shipping these")
        sys.exit(1)
    print("\nall samples decode")


if __name__ == "__main__":
    main()
