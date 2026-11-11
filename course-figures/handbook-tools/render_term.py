#!/usr/bin/env python3
"""Render a 'run this -> you see this' card as a PNG.

One card = the picture you feed in (optional), the exact command, the REAL
output captured from running it, and a big coloured verdict. Every output line
on a card must come from an actual run - this script never invents output.

    python render_term.py spec.json out.png
"""
import base64
import html
import json
import mimetypes
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

FONT_DIR = Path("/root/.fonts")
MONO = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
MONO_B = Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf")

VERDICTS = {
    "ok":    ("#16a34a", "#dcfce7", "✓"),   # green tick
    "warn":  ("#d97706", "#fef3c7", "!"),        # amber
    "bad":   ("#dc2626", "#fee2e2", "✕"),   # red cross
    "info":  ("#2563eb", "#dbeafe", "i"),
}


def data_uri(path):
    p = Path(path)
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    return "data:%s;base64,%s" % (mime, base64.b64encode(p.read_bytes()).decode())


def colour_line(line):
    """Colour the [INFO]/[WARN] tag and the known/UNKNOWN word, nothing else."""
    esc = html.escape(line)
    for tag, col in (("[INFO]", "#7dd3fc"), ("[WARN]", "#fbbf24"),
                     ("[FATAL]", "#f87171"), ("[ERROR]", "#f87171")):
        esc = esc.replace(html.escape(tag), '<span style="color:%s">%s</span>'
                          % (col, html.escape(tag)), 1)
    esc = esc.replace(" known ", ' <b style="color:#4ade80">known</b> ', 1)
    esc = esc.replace(" UNKNOWN ", ' <b style="color:#fbbf24">UNKNOWN</b> ', 1)
    return esc


def build(spec):
    fonts = "".join(
        "@font-face{font-family:'%s';src:url('file://%s');font-weight:%s}"
        % (fam, path, w) for fam, path, w in (
            ("Kanit", FONT_DIR / "Kanit-Regular.ttf", 400),
            ("Kanit", FONT_DIR / "Kanit-Medium.ttf", 500),
            ("Kanit", FONT_DIR / "Kanit-SemiBold.ttf", 600),
            ("Mono", MONO, 400), ("Mono", MONO_B, 700)))

    fg, bg, glyph = VERDICTS[spec.get("verdict", "info")]
    thumb = ""
    if spec.get("image"):
        thumb = """
        <div class="in">
          <div class="cap">%s</div>
          <div class="frame"><img src="%s"></div>
          <div class="fname">%s</div>
        </div>""" % (html.escape(spec.get("image_caption", "รูปที่ใส่เข้าไป")),
                     data_uri(spec["image"]), html.escape(Path(spec["image"]).name))

    out_lines = "\n".join(colour_line(l) for l in spec["output"])
    return """<!doctype html><html><head><meta charset="utf-8"><style>
%s
*{box-sizing:border-box;margin:0;padding:0}
body{background:#fff;font-family:Kanit,sans-serif;width:%dpx}
.card{display:flex;gap:28px;align-items:stretch;padding:28px}
.in{flex:0 0 230px;display:flex;flex-direction:column;align-items:center;gap:10px}
.cap{font-size:20px;font-weight:500;color:#334155}
.frame{width:230px;height:230px;border:3px dashed #cbd5e1;border-radius:18px;
       display:flex;align-items:center;justify-content:center;background:#f8fafc;padding:14px}
.frame img{max-width:100%%;max-height:100%%;image-rendering:auto}
.fname{font-family:Mono;font-size:15px;color:#64748b}
.right{flex:1;display:flex;flex-direction:column;gap:16px;min-width:0}
.term{background:#0f172a;border-radius:16px;overflow:hidden;
      box-shadow:0 10px 30px rgba(15,23,42,.25)}
.bar{background:#1e293b;padding:11px 16px;display:flex;gap:8px;align-items:center}
.dot{width:13px;height:13px;border-radius:50%%}
.title{color:#94a3b8;font-family:Mono;font-size:14px;margin-left:10px}
pre{font-family:Mono;font-size:17px;line-height:1.55;color:#e2e8f0;
    padding:18px 20px 20px;white-space:pre-wrap;word-break:break-all}
.cmd{color:#f8fafc}.ps{color:#4ade80;font-weight:700}
.out{color:#cbd5e1;display:block;margin-top:10px}
.verdict{display:flex;align-items:center;gap:16px;background:%s;
         border:3px solid %s;border-radius:16px;padding:14px 20px}
.badge{flex:0 0 52px;height:52px;border-radius:50%%;background:%s;color:#fff;
       font-family:Mono;font-weight:700;font-size:30px;
       display:flex;align-items:center;justify-content:center}
.vt{font-size:25px;font-weight:600;color:%s;line-height:1.25}
.vs{font-size:18px;color:#475569;margin-top:2px}
</style></head><body><div class="card">%s
<div class="right">
  <div class="term">
    <div class="bar"><span class="dot" style="background:#f87171"></span>
      <span class="dot" style="background:#fbbf24"></span>
      <span class="dot" style="background:#4ade80"></span>
      <span class="title">terminal</span></div>
    <pre><span class="ps">$</span> <span class="cmd">%s</span><span class="out">%s</span></pre>
  </div>
  <div class="verdict"><div class="badge">%s</div>
    <div><div class="vt">%s</div><div class="vs">%s</div></div></div>
</div></div></body></html>""" % (
        fonts, spec.get("width", 1180), bg, fg, fg, fg, thumb,
        html.escape(spec["command"]), out_lines, glyph,
        html.escape(spec["verdict_title"]), html.escape(spec.get("verdict_sub", "")))


def main():
    spec = json.load(open(sys.argv[1], encoding="utf-8"))
    out = sys.argv[2]
    page_html = build(spec)
    tmp = Path(out).with_suffix(".html")
    tmp.write_text(page_html, encoding="utf-8")
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": spec.get("width", 1180), "height": 400},
                        device_scale_factor=spec.get("scale", 1.5))
        pg.goto("file://" + str(tmp.resolve()))
        pg.wait_for_timeout(250)
        pg.locator(".card").screenshot(path=out)
        b.close()
    tmp.unlink()
    print(out, Path(out).stat().st_size, "bytes")


if __name__ == "__main__":
    main()
