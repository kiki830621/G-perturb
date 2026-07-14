#!/usr/bin/env python3
"""build_slides.py  —  inline the 5 figures into slides_template.html → self-contained demo/slides.html."""
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
        print(f"  (PIL skip: {e})")
    return "data:image/png;base64," + base64.b64encode(raw).decode()

# The template is already a complete standalone HTML doc (<!DOCTYPE> + <meta charset>),
# so this just inlines the figures and writes it back as UTF-8. Explicit encoding keeps
# the special glyphs (→ · × ρ ² −) intact regardless of the shell locale.
html = open(os.path.join(here, "slides_template.html"), encoding="utf-8").read()
for tok, fn in FIGS.items():
    if tok in html:
        html = html.replace(tok, data_uri(os.path.join(FIGDIR, fn))); print(f"  {tok} <- {fn}")
out = os.path.join(here, "slides.html")
open(out, "w", encoding="utf-8").write(html)
print(f"wrote {out}  ({len(html)//1024} KB)")
