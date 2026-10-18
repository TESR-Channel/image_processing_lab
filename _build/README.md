# `_build/` — source and proof for the inlined encoders

`index.html` is deliberately a single self-contained file, so the QR and
barcode encoders are **inlined** into its `<script>` block. This folder holds
the readable source of that block and the harness that proves it correct.

## Why these encoders exist at all

OpenCV can *read* QR codes and barcodes, and can *draw* ArUco markers, but the
browser build ships **no QR or barcode encoder**. `cv2.QRCodeEncoder` exists on
the Python side only. So the drawing of the codes on the page is ours, written
from ISO/IEC 18004 (QR), ISO/IEC 15420 (EAN/UPC), ISO/IEC 15417 (Code 128) and
ISO/IEC 16388 (Code 39).

## Files

| File | What it is |
|---|---|
| `encoders.js` | The source of the inlined block. Six globals: `qrEncode(text, ecLevel)`, `ean13Encode(digits)`, `ean8Encode(digits)`, `upcaEncode(digits)`, `code128Encode(text)` and `code39Encode(text)`. No imports, no npm, no build step. |
| `gen.js` | Node script that runs the encoders over the test cases and writes `cases.json` / `sweep.json`. |
| `verify.py` | Decodes everything `gen.js` produced and asserts an exact match. Needs `cv2` and `pyzbar`. |
| `crosscheck.py` | Optional, deeper: compares against `zxing-cpp` and `python-qrcode`. Skips cleanly if those are absent. |

All five 1D encoders return the same `{ code, bits }` shape — `bits` is a
string of `'0'`/`'1'` with `'1'` = a dark module and no quiet zone — so one
renderer draws all of them. `code128Encode` adds a `checksum` field as well.

## Which decoder checks what

| Symbology | Decoder used |
|---|---|
| QR | `cv2.QRCodeDetector` |
| EAN-13 | `cv2.barcode.BarcodeDetector` |
| EAN-8, UPC-A | `pyzbar` (verdict) plus `cv2.barcode` as a second opinion |
| Code 128, Code 39 | `pyzbar` only |

OpenCV 5.0's barcode module reads EAN-8/EAN-13/UPC-A/UPC-E and nothing else —
it has **no Code 128 or Code 39 reader**, so its silence on those two says
nothing about the encoder and the harness does not count it as a failure.

Two symmetrical quirks in how the decoders name a 0-prefixed symbol, both
accepted deliberately by `verify.py` because both are correct readings of the
same bars:

* An EAN-13 starting with 0 is bit-for-bit a UPC-A symbol, and OpenCV reports
  it as `UPC_A` with 12 digits.
* This build of zbar has the UPC-A symbology switched off, so it reports a
  UPC-A symbol as the `EAN13` it literally is, with a leading 0.

Rendering settings that matter: a 2–4 px module, 150–200 px of bar height, a
quiet zone of at least 10 modules, and `cv2.GaussianBlur(img, (5, 5), 0)`
before decoding. OpenCV's gradient-based detector fails on pixel-perfect
synthetic bars without that blur, and 3×3 is not enough. pyzbar is far less
fussy, but the blur does not hurt it.

## Re-verifying after a change

```bash
cd _build
node gen.js && python3 verify.py
```

## Keeping the two copies in step

**If you edit `encoders.js`, the change does nothing until it is re-inlined into
`index.html`.** The inlined copy sits under the comment
`/* ---------------- QR and barcode encoders ---------------- */`, immediately
before the `codes & markers` section, and runs from the `/* ====` banner down to
the IIFE's closing `}(typeof globalThis !== 'undefined' ? globalThis : this));`.
Replace that block with the new file contents verbatim — the two copies are meant
to be byte-identical, so `grep -c` of a distinctive line should find it twice.
Then re-run the verification above, and repack `deploy/`:

```bash
cd ..
xz -9 -c index.html | base64 -w0 > /tmp/idx.b64
rm -f deploy/index.part*
split -n 4 -d /tmp/idx.b64 deploy/index.part
sha256sum index.html | cut -d' ' -f1 > deploy/index.sha256
# confirm the workflow's own rebuild reproduces it byte for byte
cat deploy/index.part* | tr -d '\n' | base64 -d | xz -d | cmp - index.html && echo OK
```

`deploy/` is what GitHub Pages builds from — `index.html` alone is not enough.
`split -d` gives two-digit suffixes (`index.part00`, `index.part01`, …), which
keeps the workflow's `deploy/index.part*` glob in the right order if the file
ever needs more than ten parts. Do not drop the `-d`.

The exported Python carries its own, independent implementation of the same
symbologies — a learner has to be able to read the script end to end and run it
with nothing but `opencv-python` and `numpy`. That copy lives in
`barcodeTables()` / `barcodeEncoderPy()` in `index.html` and is not covered by
`verify.py`; it is checked by generating each symbology in the page, running the
script it exports, and decoding the PNG it writes.

## One known limitation, recorded honestly

Over an 80-symbol sweep of every version/EC combination, OpenCV's QR *detector*
fails to localise 13 symbols. All 13 use mask 0 or 1 over a highly repetitive
`"AAAA…"` payload, which defeats OpenCV's finder-pattern search. The encoder is
not at fault: `zxing-cpp` reads all 13, and `python-qrcode` forced to the same
mask produces a byte-identical matrix. Mask selection is deliberately left
spec-compliant rather than biased away from 0 and 1 to flatter one decoder.
Realistic payloads are unaffected.
