#!/usr/bin/env python3
"""Screenshot a small HTML figure (the element with class "fig") to PNG.

    python render_fig.py figure.html out.png [width]

The figure HTML is a body fragment. This wraps it with the shared fonts and
base styles so every figure in a handbook looks like it belongs to one set.
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

F = Path("/root/.fonts")
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

HEAD = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Kanit;src:url('file://%s');font-weight:400}
@font-face{font-family:Kanit;src:url('file://%s');font-weight:500}
@font-face{font-family:Kanit;src:url('file://%s');font-weight:600}
@font-face{font-family:Kanit;src:url('file://%s');font-weight:700}
@font-face{font-family:Mono;src:url('file://%s');font-weight:400}
@font-face{font-family:Mono;src:url('file://%s');font-weight:700}
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;font-family:Kanit,sans-serif;color:#0f172a}
.fig{padding:26px;display:inline-block}
.mono{font-family:Mono}
</style></head><body>""" % (F / "Kanit-Regular.ttf", F / "Kanit-Medium.ttf",
                            F / "Kanit-SemiBold.ttf", F / "Kanit-Bold.ttf", MONO, MONO_B)


def main():
    src, out = sys.argv[1], sys.argv[2]
    width = int(sys.argv[3]) if len(sys.argv) > 3 else 1180
    page = Path(out).with_suffix(".page.html")
    page.write_text(HEAD + Path(src).read_text(encoding="utf-8") + "</body></html>",
                    encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": width, "height": 600}, device_scale_factor=1.5)
        pg.goto("file://" + str(page.resolve()))
        pg.wait_for_timeout(250)
        pg.locator(".fig").screenshot(path=out)
        b.close()
    page.unlink()
    print(out, Path(out).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
