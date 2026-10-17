# `_build/` — source and proof for the inlined encoders

`index.html` is deliberately a single self-contained file, so the QR and EAN-13
encoders are **inlined** into its `<script>` block. This folder holds the
readable source of that block and the harness that proves it correct.

## Why these encoders exist at all

OpenCV can *read* QR codes and barcodes, and can *draw* ArUco markers, but the
browser build ships **no QR or barcode encoder**. `cv2.QRCodeEncoder` exists on
the Python side only. So the drawing of QR and EAN-13 on the page is ours,
written from ISO/IEC 18004 (QR) and ISO/IEC 15420 (EAN/UPC).

## Files

| File | What it is |
|---|---|
| `encoders.js` | The source of the inlined block. Two globals: `qrEncode(text, ecLevel)` and `ean13Encode(digits)`. No imports, no npm, no build step. |
| `gen.js` | Node script that runs the encoders over the test cases and writes `cases.json` / `sweep.json`. |
| `verify.py` | Decodes everything `gen.js` produced back through OpenCV and asserts an exact match. Needs only `cv2`. |
| `crosscheck.py` | Optional, deeper: compares against `zxing-cpp` and `python-qrcode`. Skips cleanly if those are absent. |

## Re-verifying after a change

```bash
cd _build
node gen.js && python3 verify.py
```

## Keeping the two copies in step

**If you edit `encoders.js`, the change does nothing until it is re-inlined into
`index.html`.** The inlined copy sits under the comment
`/* ---------------- QR and EAN-13 encoders ---------------- */`, immediately
before the `codes & markers` section. Replace that block with the new file
contents, then re-run the verification above, then repack `deploy/`:

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

## One known limitation, recorded honestly

Over an 80-symbol sweep of every version/EC combination, OpenCV's QR *detector*
fails to localise 13 symbols. All 13 use mask 0 or 1 over a highly repetitive
`"AAAA…"` payload, which defeats OpenCV's finder-pattern search. The encoder is
not at fault: `zxing-cpp` reads all 13, and `python-qrcode` forced to the same
mask produces a byte-identical matrix. Mask selection is deliberately left
spec-compliant rather than biased away from 0 and 1 to flatter one decoder.
Realistic payloads are unaffected.
