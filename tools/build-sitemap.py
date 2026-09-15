#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère sitemap.xml à partir des canonicals des pages indexables.

Le `lastmod` est la vraie date de dernière modification de chaque page (voir
tools/sitedates.py) : Google ignore ce champ dès qu'il est manifestement
identique partout ou rafraîchi artificiellement.
"""
from pathlib import Path
import html
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sitedates import page_dates  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
urls = {}
for p in sorted(list(ROOT.glob("*.html")) + list((ROOT / "blog").glob("*.html"))):
    s = p.read_text(encoding="utf-8")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', s, re.I):
        continue
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)', s, re.I)
    if not m:
        continue
    _, mod = page_dates(str(p), s)
    urls.setdefault(m.group(1), mod)

out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u, mod in urls.items():
    out.append(f"  <url><loc>{html.escape(u)}</loc><lastmod>{mod}</lastmod></url>")
out += ["</urlset>", ""]
(ROOT / "sitemap.xml").write_text("\n".join(out), encoding="utf-8")
print(len(urls), "URLs")
