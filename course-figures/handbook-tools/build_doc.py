#!/usr/bin/env python3
"""Build a handbook chapter as HTML that Google Docs imports cleanly.

Every trap recorded in the project notes is enforced here by construction or
by assertion, so a chapter cannot ship with a known defect:

  * monospace spans carry their complete style inline
  * no whitespace-only span ever sits inside a code cell (padding is absorbed
    into the preceding text span, because the importer strips formatting
    from a whitespace-only run whatever it declares)
  * no literal U+00A0; padding uses &nbsp; entities
  * lists are never used, so the list-flattening trap cannot occur
  * images go by public URL, so the payload stays small

    python build_doc.py chapter.py out.html
"""
import html
import importlib.util
import re
import sys

MONO = "font-family:&quot;Roboto Mono&quot;;font-size:10pt"
BODY = "font-family:&quot;Noto Sans Thai&quot;;font-size:12pt;color:#1e293b;line-height:1.5"
TXT = "font-family:&quot;Noto Sans Thai&quot;"
HEAD = "font-family:Kanit"

C_CMD, C_PROMPT, C_COMMENT = "#f8fafc", "#4ade80", "#94a3b8"

# css v1 API on purpose: its URL has no ';' (css2's "wght@400;700" would end
# the @import statement early)
FONT_IMPORT = ("https://fonts.googleapis.com/css?family="
               "Kanit:400,600,700|Noto+Sans+Thai:400,700|Roboto+Mono:400,700")


def esc(s):
    return html.escape(s, quote=False)


def nb(n):
    return "&nbsp;" * n


def code_block(lines, title=None):
    """lines: list of (command, comment) or str. Comments align in a column."""
    rows = [(l, "") if isinstance(l, str) else l for l in lines]
    width = max(len(c) for c, _ in rows)
    out = []
    for cmd, comment in rows:
        prompt = '<span style="%s;color:%s;font-weight:700">$%s</span>' % (MONO, C_PROMPT, nb(1))
        # the command span carries its own padding - never a span of spaces
        pad = nb(width - len(cmd) + 3) if comment else ""
        body = '<span style="%s;color:%s">%s%s</span>' % (MONO, C_CMD, esc(cmd), pad)
        tail = ('<span style="%s;color:%s">%s</span>' % (MONO, C_COMMENT, esc(comment))) if comment else ""
        out.append('<p style="margin:0;line-height:1.6">%s%s%s</p>' % (prompt, body, tail))
    cap = ""
    if title:
        cap = ('<p style="margin:0 0 4pt 0"><span style="%s;font-size:9pt;color:#64748b">%s</span></p>'
               % (HEAD, esc(title)))
    return (cap + '<table style="border-collapse:collapse;width:100%%"><tr>'
            '<td bgcolor="#0f172a" style="background-color:#0f172a;padding:9pt 12pt">%s</td>'
            '</tr></table>' % "".join(out))


def para(text, size=12, color="#1e293b", bold=False, space_after=8):
    style = TXT + ";font-size:%dpt;color:%s;line-height:1.5" % (size, color)
    if bold:
        style += ";font-weight:700"
    return '<p style="margin:0 0 %dpt 0"><span style="%s">%s</span></p>' % (space_after, style, text)


def rich(text):
    """**bold** and `code` inside a sentence."""
    t = esc(text)
    t = re.sub(r"\*\*(.+?)\*\*", r'<span style="font-weight:700">\1</span>', t)
    t = re.sub(r"`(.+?)`", lambda m: '<span style="%s;color:#0f172a;background-color:#eef1f4">%s</span>'
               % (MONO, m.group(1)), t)
    return t


def header(chapter_no, title, intro, word="บทที่"):
    """Top of page 1: label, H1 title (shows in the Doc outline), one-line intro."""
    return ('<p style="margin:0"><span style="%s;font-size:11pt;color:#2563eb;font-weight:600">'
            'TESR ACADEMY · STEPS · %s %s</span></p>'
            '<h1 style="margin:2pt 0 4pt 0"><span style="%s;font-size:26pt;font-weight:700;color:#0f172a">'
            '%s %s · %s</span></h1>' % (HEAD, word, chapter_no, HEAD, word, chapter_no, esc(title))
            + para(intro, size=13, color="#334155"))


MARK = ('<p style="margin:0;line-height:1"><span style="%s;font-size:2pt;color:#ffffff">PGBRK</span></p>'
        % TXT)


def step(n, title, newpage=True):
    """H2 (clickable in the Doc outline). newpage: a PGBRK marker before it, replaced
    by a real page break in the browser after upload (no page-break markup survives)."""
    h = ('<h2 style="margin:0 0 6pt 0"><span style="%s;font-size:19pt;font-weight:700;color:#2563eb">%s</span>'
         '<span style="%s;font-size:19pt;font-weight:700;color:#0f172a">%s%s</span></h2>'
         % (HEAD, n, HEAD, nb(2), esc(title)))
    return (MARK if newpage else '<p style="margin:14pt 0 0 0"></p>') + h


def image(url, alt, width=624):
    return '<p style="margin:4pt 0 10pt 0"><img src="%s" alt="%s" width="%d"></p>' % (url, esc(alt), width)


def callout(text, kind="tip"):
    fg, bg = {"tip": ("#1d4ed8", "#eff6ff"), "warn": ("#b45309", "#fffbeb"),
              "honest": ("#b91c1c", "#fef2f2")}[kind]
    return ('<table style="border-collapse:collapse;width:100%%;margin:6pt 0"><tr>'
            '<td bgcolor="%s" style="background-color:%s;border-left:4pt solid %s;padding:8pt 12pt">'
            '<p style="margin:0"><span style="%s;font-size:12pt;color:%s">%s</span></p>'
            '</td></tr></table>' % (bg, bg, fg, TXT, fg, rich(text)))


def table(header, rows):
    th = "".join('<td bgcolor="#1e3a5f" style="background-color:#1e3a5f;padding:7pt 10pt">'
                 '<p style="margin:0"><span style="%s;font-size:12pt;color:#ffffff;font-weight:700">%s</span></p></td>'
                 % (HEAD, esc(h)) for h in header)
    body = ""
    for i, r in enumerate(rows):
        bg = "#f8fafc" if i % 2 else "#ffffff"
        cells = "".join(('<td bgcolor="%s" style="background-color:%s;padding:7pt 10pt;border-bottom:1pt solid #e2e8f0">' % (bg, bg) if bg != "#ffffff"
                         else '<td style="padding:7pt 10pt;border-bottom:1pt solid #e2e8f0">')
                        + '<p style="margin:0"><span style="%s;font-size:12pt;color:#1e293b">%s</span></p></td>' % (TXT, rich(c))
                        for c in r)
        body += "<tr>%s</tr>" % cells
    return '<table style="border-collapse:collapse;width:100%%;margin:4pt 0 10pt 0"><tr>%s</tr>%s</table>' % (th, body)


def check(doc):
    # code cells are the only #0f172a cells; table headers use #1e3a5f, so the
    # mono check below cannot mistake a header for code
    assert " " not in doc, "literal U+00A0 in output"
    for td in re.findall(r'<td bgcolor="#0f172a".*?</td>', doc, re.S):
        for span in re.findall(r"<span[^>]*>(.*?)</span>", td, re.S):
            text = re.sub(r"&nbsp;|\s", "", span)
            assert text, "whitespace-only span inside a code cell"
        for span in re.findall(r'<span style="([^"]*)"', td):
            assert "Roboto Mono" in span, "non-mono span inside a code cell: " + span
    assert not re.search(r"<(ul|ol|li)\b", doc), "a list slipped in"


def main():
    spec = importlib.util.spec_from_file_location("chapter", sys.argv[1])
    ch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ch)
    parts = ch.build(sys.modules[__name__])
    # Without this @import, ANY table in the upload makes the importer drop
    # every non-default font in the whole document (measured 2026-10-25:
    # probe F1 table-only -> all Arial; probe G same + @import -> all kept).
    doc = ('<html><head><meta charset="utf-8"><style>@import url(%s);</style></head>'
           '<body style="%s">%s</body></html>' % (FONT_IMPORT, BODY, "".join(parts)))
    check(doc)
    open(sys.argv[2], "w", encoding="utf-8").write(doc)
    print(sys.argv[2], len(doc.encode()), "bytes; checks passed")


if __name__ == "__main__":
    main()
