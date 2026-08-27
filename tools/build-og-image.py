#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère l'image de partage (Open Graph) aux couleurs de la charte.

L'image est composée en HTML puis capturée en 1200x630 : elle reste alignée
sur la typographie et la palette du site, et se régénère d'une commande.

    python3 tools/build-og-image.py
"""
import base64
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "img" / "og-cover.jpg"

TEMPLATE = """<!doctype html>
<html lang="fr"><head><meta charset="utf-8">
<style>
  @font-face {{ font-family:'Inter'; font-weight:300 700; font-display:block;
    src:url(data:font/woff2;base64,{inter}) format('woff2'); }}
  @font-face {{ font-family:'Fraunces'; font-weight:400 700; font-display:block;
    src:url(data:font/woff2;base64,{fraunces}) format('woff2'); }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ width:1200px; height:630px; display:flex; background:#1B2430;
         font-family:'Inter',sans-serif; overflow:hidden; }}
  .left {{ flex:1; padding:64px 56px; display:flex; flex-direction:column;
          justify-content:space-between; position:relative; z-index:2; }}
  .mark {{ font-family:'Fraunces',serif; font-weight:700; font-size:26px;
          letter-spacing:.06em; text-transform:uppercase; color:#FDFBF8; }}
  .mark span {{ color:#7FA0DC; }}
  .rule {{ width:56px; height:3px; margin-top:14px;
          background:linear-gradient(90deg,#C2761F,#1E40AF); }}
  h1 {{ font-family:'Fraunces',serif; font-weight:700; font-size:74px;
       line-height:1.03; letter-spacing:-0.02em; color:#FDFBF8; }}
  h1 em {{ font-style:normal; color:#7FA0DC; display:block; }}
  .sub {{ margin-top:18px; font-size:25px; color:#C6BFB2; font-weight:400; }}
  .foot {{ font-size:19px; color:#ABA396; display:flex; gap:14px; align-items:center; }}
  .dot {{ width:5px; height:5px; border-radius:50%; background:#C2761F; }}
  .right {{ width:430px; position:relative; }}
  .right img {{ width:100%; height:100%; object-fit:cover; object-position:center 18%;
               filter:saturate(.78) contrast(1.04) brightness(.94); }}
  .fade {{ position:absolute; inset:0;
          background:linear-gradient(90deg,#1B2430 0%,rgba(27,36,48,.62) 40%,rgba(27,36,48,.20) 100%); }}
  .glow {{ position:absolute; width:520px; height:520px; border-radius:50%;
          right:300px; top:-190px; background:radial-gradient(circle,rgba(30,64,175,.30),transparent 68%); }}
</style></head>
<body>
  <div class="glow"></div>
  <div class="left">
    <div>
      <div class="mark">Ilan Guedj<span>.</span></div>
      <div class="rule"></div>
    </div>
    <div>
      <h1>Avocat<em>Dommage corporel</em></h1>
      <p class="sub">Indemnisation des victimes</p>
    </div>
    <div class="foot">
      <span>Marseille</span><span class="dot"></span>
      <span>Toute la France</span><span class="dot"></span>
      <span>0&nbsp;€ d'avance</span>
    </div>
  </div>
  <div class="right"><img src="data:image/jpeg;base64,{portrait}"><div class="fade"></div></div>
</body></html>"""


def b64(path):
    return base64.b64encode(path.read_bytes()).decode()


def main():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Playwright requis : pip install playwright", file=sys.stderr)
        return 1

    html = TEMPLATE.format(
        inter=b64(ROOT / "fonts" / "inter-latin.woff2"),
        fraunces=b64(ROOT / "fonts" / "fraunces-latin.woff2"),
        portrait=b64(ROOT / "img" / "associe-guedj.jpg"),
    )
    tmp = ROOT / "img" / "_og-cover.html"
    tmp.write_text(html, encoding="utf-8")
    # Certains environnements fournissent déjà un Chromium : on l'utilise.
    preinstalled = Path("/opt/pw-browsers/chromium")
    launch = {"executable_path": str(preinstalled)} if preinstalled.exists() else {}
    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(**launch)
            page = browser.new_page(viewport={"width": 1200, "height": 630},
                                    device_scale_factor=1)
            page.goto(tmp.as_uri())
            page.wait_for_timeout(600)
            page.screenshot(path=str(OUT), type="jpeg", quality=88)
            browser.close()
    finally:
        tmp.unlink(missing_ok=True)
    print(f"{OUT.relative_to(ROOT)} écrite — {OUT.stat().st_size // 1024} Ko")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
