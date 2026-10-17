#!/usr/bin/env python3
"""Deeper, optional validation of encoders.js beyond the OpenCV round-trip.

verify.py proves the symbols decode. This script proves they are *the right
symbols*, which is a stronger claim, using three independent references:

  1. zxing-cpp          - an independent decoder. Reads every symbol, including
                          the ones OpenCV's detector cannot localise.
  2. python-qrcode       - an independent encoder. Forced to the same mask, its
                          matrix must be byte-for-byte identical to ours. That
                          covers mode/count/payload/terminator/padding, Reed-
                          Solomon, block split, interleaving, finder, timing
                          and alignment patterns, format and version info, and
                          the module placement path - everything except the
                          mask *choice*.
  3. a spec-derived penalty scorer written here from ISO/IEC 18004 clause
                          7.8.3.1 - judges the mask choice itself.

Optional dependencies:  pip install zxing-cpp qrcode
Missing ones are skipped with a notice rather than failing the run.

Run with:  python3 /home/claude/image_processing_lab/_build/crosscheck.py
"""

import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# Reuse the renderers from verify.py so both scripts rasterise identically.
_spec = importlib.util.spec_from_file_location("verify", os.path.join(HERE, "verify.py"))
_verify = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_verify)

try:
    import zxingcpp
except ImportError:
    zxingcpp = None

try:
    import qrcode
    import qrcode.util
    from qrcode.constants import (
        ERROR_CORRECT_H,
        ERROR_CORRECT_L,
        ERROR_CORRECT_M,
        ERROR_CORRECT_Q,
    )

    QRC_EC = {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }
except ImportError:
    qrcode = None
    QRC_EC = {}


# ---------------------------------------------------------------------------
# The four penalty rules, written straight from ISO/IEC 18004 clause 7.8.3.1.
# Deliberately a separate implementation from the one in encoders.js, so that
# agreement between the two means something.
# ---------------------------------------------------------------------------
def rule1(m):
    """N1 = 3: every run of 5 or more same-colour modules in a row or column
    scores 3 for the first five plus 1 for each module beyond five."""
    s = 0
    for mat in (m, m.T):
        for row in mat:
            run, colour = 1, row[0]
            for x in row[1:]:
                if x == colour:
                    run += 1
                else:
                    if run >= 5:
                        s += 3 + run - 5
                    run, colour = 1, x
            if run >= 5:
                s += 3 + run - 5
    return s


def rule2(m):
    """N2 = 3: every 2x2 block of a single colour scores 3."""
    a, b, c, d = m[:-1, :-1], m[:-1, 1:], m[1:, :-1], m[1:, 1:]
    return 3 * int(np.sum((a == b) & (a == c) & (a == d)))


def rule3(m):
    """N3 = 40: the 1:1:3:1:1 finder-like pattern with a four-module light run
    immediately before or after it."""
    pa = np.array([1, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0], dtype=np.uint8)
    pb = pa[::-1]
    s = 0
    for mat in (m, m.T):
        n = mat.shape[1]
        for row in mat:
            for i in range(n - 10):
                w = row[i : i + 11]
                if np.array_equal(w, pa):
                    s += 40
                if np.array_equal(w, pb):
                    s += 40
    return s


def rule4(m):
    """N4 = 10: ten points for every full 5% the dark-module proportion
    deviates from 50%."""
    pct = int(m.sum()) * 100.0 / m.size
    return int(abs(pct - 50) / 5) * 10


def penalty(m):
    return rule1(m) + rule2(m) + rule3(m) + rule4(m)


# ---------------------------------------------------------------------------
def qrc_matrix(text, ec_level, version, mask):
    """python-qrcode's matrix for the same payload, forced to byte mode,
    this version and this mask."""
    q = qrcode.QRCode(
        version=version,
        error_correction=QRC_EC[ec_level],
        box_size=1,
        border=0,
        mask_pattern=mask,
    )
    q.add_data(qrcode.util.QRData(text.encode("utf-8"), mode=qrcode.util.MODE_8BIT_BYTE))
    q.make(fit=False)
    return np.array(q.get_matrix(), dtype=np.uint8)


def main():
    cases = []
    for fname in ("cases.json", "sweep.json"):
        p = os.path.join(HERE, fname)
        if not os.path.exists(p):
            print("missing %s - run gen.js first" % fname)
            return 2
        with open(p, "r", encoding="utf-8") as fh:
            cases.extend(json.load(fh)["qr"])

    print("cross-checking %d QR symbols\n" % len(cases))

    zx_ok = zx_fail = 0
    cv_ok = cv_fail = 0
    cv_failed_ids = []
    enc_ok = enc_fail = 0
    enc_failed = []
    mask_ok = mask_fail = 0
    mask_failed = []

    for c in cases:
        mine = np.array(c["modules"], dtype=np.uint8).reshape(c["size"], c["size"])
        img = _verify.render_qr(c["size"], c["modules"])

        # --- OpenCV, for information only (verify.py is the gate) ----------
        if _verify.qr_decode(img) == c["text"]:
            cv_ok += 1
        else:
            cv_fail += 1
            cv_failed_ids.append("%s(mask%d)" % (c["id"], c["mask"]))

        # --- 1. independent decoder ----------------------------------------
        if zxingcpp is not None:
            r = zxingcpp.read_barcode(img)
            if r is not None and r.text == c["text"]:
                zx_ok += 1
            else:
                zx_fail += 1
                print("  zxing-cpp FAILED on %s" % c["id"])

        if qrcode is None:
            continue

        # --- 2. independent encoder, forced to our mask --------------------
        ref = qrc_matrix(c["text"], c["ecLevel"], c["version"], c["mask"])
        if ref.shape == mine.shape and np.array_equal(ref, mine):
            enc_ok += 1
        else:
            enc_fail += 1
            enc_failed.append(c["id"])

        # --- 3. independent penalty scorer judges the mask choice ----------
        scores = [
            penalty(qrc_matrix(c["text"], c["ecLevel"], c["version"], mk))
            for mk in range(8)
        ]
        best = min(scores)
        chosen = scores.index(best)  # lowest penalty, lowest mask wins a tie
        if chosen == c["mask"]:
            mask_ok += 1
        else:
            mask_fail += 1
            mask_failed.append((c["id"], c["mask"], chosen, scores))

    print("OpenCV QRCodeDetector  : %3d read, %3d not localised" % (cv_ok, cv_fail))
    if cv_failed_ids:
        print("    not localised by OpenCV: %s" % ", ".join(cv_failed_ids))
    if zxingcpp is None:
        print("zxing-cpp              : SKIPPED (pip install zxing-cpp)")
    else:
        print("zxing-cpp decoder      : %3d read, %3d failed" % (zx_ok, zx_fail))
    if qrcode is None:
        print("python-qrcode          : SKIPPED (pip install qrcode)")
    else:
        print(
            "matrix == python-qrcode at same mask : %3d identical, %3d differing"
            % (enc_ok, enc_fail)
        )
        for i in enc_failed[:10]:
            print("    matrix differs: %s" % i)
        print(
            "mask choice == spec penalty scorer   : %3d agree,     %3d differ"
            % (mask_ok, mask_fail)
        )
        for f in mask_failed[:10]:
            print("    mask differs: %s mine=%d spec=%d scores=%s" % f)

    # The gate: the independent decoder and the independent encoder/scorer.
    # OpenCV localisation failures are reported but do not fail this script -
    # see the note in the report. verify.py is where the required cases gate.
    hard_failures = zx_fail + enc_fail + mask_fail
    print("\n%s" % ("CROSS-CHECK PASSED" if hard_failures == 0 else "CROSS-CHECK FAILED"))
    return 1 if hard_failures else 0


if __name__ == "__main__":
    sys.exit(main())
