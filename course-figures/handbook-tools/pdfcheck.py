"""Local stand-in for the Doc: markers -> page breaks, Letter, 1 in margins; pages per step."""
import sys, re, subprocess
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
h = open(src, encoding='utf-8').read()
h = h.replace('https://raw.githubusercontent.com/TESR-Channel/image_processing_lab/course-figures/course-figures/handbook14/v7/', 'file:///home/claude/ch14/out/')
h = re.sub(r'<p style="margin:0;line-height:1"><span[^>]*>PGBRK</span></p>', '<div style="page-break-before:always"></div>', h)
h = h.replace('<head>', '<head><style>img{max-width:100%} @page{size:Letter;margin:1in} table{page-break-inside:auto}</style>')
open('/tmp/claude-0/local.html', 'w').write(h)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(); pg.goto('file:///tmp/claude-0/local.html'); pg.wait_for_timeout(1500)
    pg.pdf(path=out, format='Letter', margin={'top': '1in', 'bottom': '1in', 'left': '1in', 'right': '1in'}); b.close()
print(subprocess.run(['pdfinfo', out], capture_output=True, text=True).stdout.split('Pages:')[1].split('\n')[0].strip(), 'pages')
