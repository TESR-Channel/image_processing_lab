#!/usr/bin/env python3
"""Round-trip the JavaScript encoders through independent decoders.

Reads cases.json (written by gen.js), renders each symbol to a NumPy image and
decodes it back, asserting the payload survives exactly.

QR and EAN-13 go through OpenCV. EAN-8, UPC-A, Code 128 and Code 39 go through
pyzbar (zbar) as the primary decoder, with OpenCV as a second opinion on the
two of the four it supports - OpenCV's barcode detector has no Code 128 or
Code 39 reader at all, so those two get pyzbar only.

Run with:  python3 /home/claude/image_processing_lab/_build/verify.py
"""

import json
import os
import sys

import cv2
import numpy as np
from pyzbar import pyzbar

HERE = os.path.dirname(os.path.abspath(__file__))
CASES = os.path.join(HERE, "cases.json")

# --- render settings -------------------------------------------------------
# QR: generous module size and the mandatory 4-module quiet zone.
QR_SCALE = 8
QR_QUIET = 4

# EAN-13: OpenCV's barcode detector is gradient-based and fails on
# pixel-perfect synthetic renders, so we render wide bars with a big quiet zone
# and soften the edges with a Gaussian blur before decoding.
EAN_MODULE_W = 3
EAN_HEIGHT = 200
EAN_QUIET = 12
EAN_BLURS = [(3, 3), (5, 5)]

# EAN-8 / UPC-A / Code 128 / Code 39 share the EAN-13 render settings: a 3 px
# module, 200 px of bar height and a 12-module quiet zone on each side, which
# is comfortably over the 10 modules the specs ask for. pyzbar is far less
# fussy than OpenCV, but the same 5x5 blur is applied anyway - it costs
# nothing and it is what OpenCV needs for the two symbologies it can read.
LINEAR_BLUR = (5, 5)

# What each symbology is called by each decoder.
#   zbar      - pyzbar's `.type` string
#   opencv    - cv2.barcode's type string, or None when it has no reader
# This build of zbar has the UPC-A symbology switched off, so it reports a
# UPC-A symbol as the EAN-13 it literally is; see the note in check_linear.
LINEAR_TYPES = {
    "EAN8": {"zbar": "EAN8", "opencv": "EAN_8"},
    "UPCA": {"zbar": "EAN13", "opencv": "UPC_A"},
    "CODE128": {"zbar": "CODE128", "opencv": None},
    "CODE39": {"zbar": "CODE39", "opencv": None},
}


def render_qr(size, modules, scale=QR_SCALE, quiet=QR_QUIET):
    """modules: flat list, row-major, 1 = dark. Returns uint8 grayscale."""
    grid = np.array(modules, dtype=np.uint8).reshape(size, size)
    # 1 (dark) -> 0 (black), 0 (light) -> 255 (white)
    img = np.where(grid == 1, 0, 255).astype(np.uint8)
    img = np.kron(img, np.ones((scale, scale), dtype=np.uint8))
    pad = quiet * scale
    return cv2.copyMakeBorder(
        img, pad, pad, pad, pad, cv2.BORDER_CONSTANT, value=255
    )


def render_ean(bits, module_w=EAN_MODULE_W, height=EAN_HEIGHT, quiet=EAN_QUIET):
    """bits: string of '0'/'1', 1 = dark bar. Any length - all five 1D
    symbologies render identically, only the bit count differs."""
    row = np.array([0 if b == "1" else 255 for b in bits], dtype=np.uint8)
    row = np.repeat(row, module_w)
    quiet_px = quiet * module_w
    row = np.concatenate(
        [
            np.full(quiet_px, 255, dtype=np.uint8),
            row,
            np.full(quiet_px, 255, dtype=np.uint8),
        ]
    )
    img = np.tile(row, (height, 1))
    # White margin above/below as well, so the detector sees a clean field.
    return cv2.copyMakeBorder(img, 30, 30, 0, 0, cv2.BORDER_CONSTANT, value=255)


def qr_decode(img):
    det = cv2.QRCodeDetector()
    data, points, _ = det.detectAndDecode(img)
    return data


def check_linear(case):
    """Decode one EAN-8 / UPC-A / Code 128 / Code 39 case. Returns (ok, note).

    pyzbar is the verdict. OpenCV runs too, but only counts for the two
    symbologies it has a reader for.
    """
    kind = case["kind"]
    expect = case["expect"]
    names = LINEAR_TYPES[kind]
    img = cv2.GaussianBlur(render_ean(case["bits"]), LINEAR_BLUR, 0)

    # ---- pyzbar, the primary check ----------------------------------------
    results = pyzbar.decode(img)
    if not results:
        return False, "zbar: no detection"
    if len(results) != 1:
        return False, "zbar: %d symbols found, expected 1" % len(results)
    sym = results[0]
    got = sym.data.decode("utf-8")
    zbar_expect = expect

    # A UPC-A symbol *is* an EAN-13 symbol whose leading digit is 0 - that is
    # the whole reason upcaEncode can be built on the EAN-13 path. This build
    # of zbar has the separate UPC-A symbology disabled, so it reports the
    # 13-digit EAN-13 reading. That is a correct reading of these bars, not a
    # mismatch, so accept it - but only in the one direction, 0 + the 12
    # digits we asked for.
    note_extra = ""
    if kind == "UPCA" and sym.type == "EAN13":
        zbar_expect = "0" + expect
        note_extra = " (EAN-13 reading of UPC-A)"
    elif sym.type != names["zbar"]:
        return False, "zbar: reported type %s, expected %s" % (sym.type, names["zbar"])

    if got != zbar_expect:
        return False, "zbar: got %r, expected %r" % (got, zbar_expect)
    note = "zbar=%s%s" % (sym.type, note_extra)

    # ---- OpenCV, the second opinion ---------------------------------------
    if names["opencv"] is None:
        # Established and expected: OpenCV 5.0's barcode module reads EAN-8,
        # EAN-13 and UPC-A/E only. No Code 128 or Code 39 reader exists, so
        # silence from it here says nothing about the encoder.
        return True, note + "; cv2 n/a for " + kind

    bd = cv2.barcode.BarcodeDetector()
    ok_flag, infos, types, _ = bd.detectAndDecodeWithType(img)
    cv_got, cv_type = "", ""
    if ok_flag and infos:
        for info, typ in zip(infos, types):
            if info:
                cv_got, cv_type = info, typ
                break
    if not cv_got:
        return False, note + "; cv2: no detection"
    if cv_type != names["opencv"]:
        return False, note + "; cv2: reported type %s, expected %s" % (
            cv_type, names["opencv"]
        )
    if cv_got != expect:
        return False, note + "; cv2: got %r, expected %r" % (cv_got, expect)
    return True, note + "; cv2=" + cv_type


def normalise_decoded(decoded, expected):
    """OpenCV hands back a Python str built from the raw QR byte stream.

    If the bindings reinterpreted the UTF-8 bytes as Latin-1 we recover the
    original by re-encoding. Returns (matched, how).
    """
    if decoded == expected:
        return True, "exact"
    try:
        recovered = decoded.encode("latin-1").decode("utf-8")
        if recovered == expected:
            return True, "latin1->utf8"
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return False, "mismatch"


def main():
    with open(CASES, "r", encoding="utf-8") as fh:
        cases = json.load(fh)

    rows = []
    failures = 0

    # ---------------- QR ----------------
    for c in cases["qr"]:
        img = render_qr(c["size"], c["modules"])
        decoded = qr_decode(img)
        if decoded == "":
            ok, how = False, "no detection"
        else:
            ok, how = normalise_decoded(decoded, c["text"])
        # For the Thai case also confirm the UTF-8 byte sequence matches.
        byte_note = ""
        if c["name"] == "thai-utf8" and ok:
            got = decoded if how == "exact" else decoded.encode("latin-1").decode("utf-8")
            if got.encode("utf-8") == c["text"].encode("utf-8"):
                byte_note = " utf8-bytes-ok"
            else:
                ok = False
                byte_note = " utf8-bytes-DIFFER"
        if not ok:
            failures += 1
        rows.append(
            (
                "QR",
                c["id"],
                "v%d m%d %dx%d" % (c["version"], c["mask"], c["size"], c["size"]),
                "PASS" if ok else "FAIL",
                how + byte_note,
            )
        )
        if not ok:
            print(
                "  [debug] %s expected %r got %r"
                % (c["id"], c["text"][:60], decoded[:60]),
                file=sys.stderr,
            )

    # ---------------- EAN-13 ----------------
    bd = cv2.barcode.BarcodeDetector()
    for c in cases["ean"]:
        base = render_ean(c["bits"])
        decoded = ""
        dtype = ""
        used = ""
        for k in EAN_BLURS:
            img = cv2.GaussianBlur(base, k, 0)
            ok_flag, infos, types, _ = bd.detectAndDecodeWithType(img)
            if ok_flag and infos:
                # Take the first non-empty result.
                for info, typ in zip(infos, types):
                    if info:
                        decoded = info
                        dtype = typ
                        used = "blur%dx%d type=%s" % (k[0], k[1], typ)
                        break
            if decoded:
                break

        # An EAN-13 whose leading digit is 0 is bit-for-bit identical to the
        # UPC-A symbol of its remaining 12 digits: lead digit 0 selects the
        # parity pattern LLLLLL, which is exactly UPC-A's left half. OpenCV
        # recognises that and reports type UPC_A with the 12-digit form, which
        # is the correct reading of those bars - not a loss of information.
        # Accept it, but only when the leading digit really is 0.
        expected = c["code"]
        if dtype == "UPC_A":
            assert expected[0] == "0", (
                "decoder reported UPC_A for %s, which does not start with 0" % expected
            )
            expected = expected[1:]
            used += " (UPC-A form of 0-prefixed EAN-13)"

        ok = decoded == expected
        if not ok:
            failures += 1
        rows.append(
            ("EAN13", c["id"], "input %s" % c["input"], "PASS" if ok else "FAIL",
             used or "no detection")
        )
        if not ok:
            print(
                "  [debug] %s expected %r got %r" % (c["id"], expected, decoded),
                file=sys.stderr,
            )

    # ------- EAN-8 / UPC-A / Code 128 / Code 39 -------
    for c in cases["linear"]:
        ok, note = check_linear(c)
        if not ok:
            failures += 1
        detail = "%d modules" % len(c["bits"])
        if c["checksum"] is not None:
            detail += ", checksum %d" % c["checksum"]
        rows.append(
            (c["kind"], c["id"], detail, "PASS" if ok else "FAIL", note)
        )
        if not ok:
            print(
                "  [debug] %s expected %r - %s" % (c["id"], c["expect"], note),
                file=sys.stderr,
            )

    # ---------------- throw behaviour (checked in Node, reported here) -------
    tc = cases["throwChecks"]
    throw_rows = [
        ("throw", "qr 2000 bytes @ H", "must throw", tc["qrTooLong"]["threw"]),
        ("throw", "qr bad ec level 'Z'", "must throw", tc["qrBadLevel"]["threw"]),
        (
            "throw",
            "ean wrong check digit %s" % tc["eanBadCheckDigit"]["input"],
            "must throw",
            tc["eanBadCheckDigit"]["threw"],
        ),
    ]
    for n in tc["eanNegatives"]:
        throw_rows.append(
            ("throw", "ean bad input %r" % n["input"], "must throw", n["threw"])
        )
    for n in tc["linearNegatives"]:
        throw_rows.append(("throw", n["label"], "must throw", n["threw"]))
    for kind, name, detail, threw in throw_rows:
        if not threw:
            failures += 1
        rows.append((kind, name, detail, "PASS" if threw else "FAIL", ""))

    # ---------------- mask variety ----------------
    masks = sorted({c["mask"] for c in cases["qr"]})
    mask_ok = len(masks) >= 2
    if not mask_ok:
        failures += 1
    rows.append(
        (
            "check",
            "mask varies across inputs",
            "masks seen: %s" % ",".join(str(m) for m in masks),
            "PASS" if mask_ok else "FAIL",
            "",
        )
    )

    # ---------------- table ----------------
    w = [max(len(str(r[i])) for r in rows) for i in range(5)]
    hdr = ("KIND", "CASE", "DETAIL", "RESULT", "NOTE")
    w = [max(w[i], len(hdr[i])) for i in range(5)]
    line = "  ".join("-" * x for x in w)
    print()
    print("  ".join(hdr[i].ljust(w[i]) for i in range(5)))
    print(line)
    for r in rows:
        print("  ".join(str(r[i]).ljust(w[i]) for i in range(5)))
    print(line)
    total = len(rows)
    print("%d/%d passed, %d failed" % (total - failures, total, failures))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
