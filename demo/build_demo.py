#!/usr/bin/env python3
"""build_demo.py  —  inline the 5 figures into demo_template.html as base64 data URIs (Artifact CSP
blocks external assets) and write a self-contained demo/index.html.

Figures are downscaled to max-width 1200px for the web (the printed PDFs stay full-res).
"""
import os, base64, io
here = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(here, "..", "analysis", "resolution", "realdata", "figures")
FIGS = {"__FIG1__": "fig1_me_removal.png", "__FIG2__": "fig2_dstudy_surface.png",
        "__FIG3__": "fig3_ranking_reshuffle.png", "__FIG4__": "fig4_context_tcr.png",
        "__FIG5__": "fig5_sol_hardening.png"}
MAXW = 1200

def data_uri(path):
    raw = open(path, "rb").read()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        if im.width > MAXW:
            im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
            buf = io.BytesIO(); im.save(buf, format="PNG", optimize=True); raw = buf.getvalue()
    except Exception as e:
        print(f"  (PIL unavailable / skip downscale: {e}) — using raw {os.path.basename(path)}")
    return "data:image/png;base64," + base64.b64encode(raw).decode()

html = open(os.path.join(here, "demo_template.html"), encoding="utf-8").read()
total = 0
for tok, fn in FIGS.items():
    uri = data_uri(os.path.join(FIGDIR, fn))
    total += len(uri); html = html.replace(tok, uri)
    print(f"  {tok} <- {fn}  ({len(uri)//1024} KB)")
# Wrap the Artifact fragment in a standalone HTML5 shell so it renders correctly when
# opened directly in a browser (a UTF-8 file with no <meta charset> is mis-guessed as
# Big5 on a Traditional-Chinese system, mojibaking → · — × ρ).
DOC = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
       '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
       '<title>G-perturb — reliability-weighted target ranking</title>\n</head>\n<body>\n')
out = os.path.join(here, "index.html")
doc = DOC + html + "\n</body>\n</html>\n"
open(out, "w", encoding="utf-8").write(doc)
print(f"wrote {out}  ({len(doc)//1024} KB total, figures {total//1024} KB)")
