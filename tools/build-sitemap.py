#!/usr/bin/env python3
from pathlib import Path
from datetime import date
import re, html
ROOT=Path(__file__).resolve().parents[1]
items=[]
for p in sorted(list(ROOT.glob('*.html'))+list((ROOT/'blog').glob('*.html'))):
    s=p.read_text(encoding='utf-8')
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex',s,re.I): continue
    m=re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',s,re.I)
    if m: items.append(m.group(1))
today=date.today().isoformat()
out=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in dict.fromkeys(items): out += [f'  <url><loc>{html.escape(u)}</loc><lastmod>{today}</lastmod></url>']
out+=['</urlset>','']
(ROOT/'sitemap.xml').write_text('\n'.join(out),encoding='utf-8'); print(len(items),'URLs')
