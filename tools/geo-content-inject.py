#!/usr/bin/env python3
"""Ajoute de facon idempotente les signaux editoriaux GEO utiles aux pages HTML.
Ne fabrique aucun fait juridique : il structure uniquement le contenu existant.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
START='<!-- GEO:ANSWER:START -->'; END='<!-- GEO:ANSWER:END -->'

def clean(s): return re.sub(r'<[^>]+>',' ',s).replace('&nbsp;',' ').strip()
def files(): return sorted(list(ROOT.glob('*.html'))+list((ROOT/'blog').glob('*.html')))
def process(p):
    s=p.read_text(encoding='utf-8'); old=s
    if START not in s:
        main=re.search(r'<main\b[^>]*>(.*?)</main>',s,re.S|re.I)
        scope=main.group(1) if main else s
        para=re.search(r'<p\b[^>]*>(.*?)</p>',scope,re.S|re.I)
        if para and len(clean(para.group(1)))>=80:
            block=f'{START}\n<div class="geo-answer" aria-label="Reponse essentielle">{para.group(0)}</div>\n{END}'
            pos=s.find(para.group(0)); s=s[:pos]+block+s[pos+len(para.group(0)):]
    if '/blog/' in str(p).replace('\\','/') and 'rel="author"' not in s:
        s=s.replace('</head>','<link rel="author" href="https://ig-avocat.com/avocat-ilan-guedj">\n</head>',1)
    if s!=old: p.write_text(s,encoding='utf-8'); return 1
    return 0
if __name__=='__main__':
    n=sum(process(p) for p in files()); print(f'{n} page(s) mises a jour')
