#!/usr/bin/env python3
"""Structure le contenu HTML existant pour la citabilite GEO, sans inventer de faits."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
START='<!-- GEO:ANSWER:START -->'; END='<!-- GEO:ANSWER:END -->'
def text(x): return re.sub(r'<[^>]+>',' ',x).replace('&nbsp;',' ').strip()
def pages(): return sorted(list(ROOT.glob('*.html'))+list((ROOT/'blog').glob('*.html')))
def process(p):
 s=p.read_text(encoding='utf-8'); old=s
 if START not in s:
  scope=(re.search(r'<main\b[^>]*>(.*?)</main>',s,re.S|re.I) or re.search(r'<body\b[^>]*>(.*?)</body>',s,re.S|re.I))
  if scope:
   para=re.search(r'<p\b[^>]*>(.*?)</p>',scope.group(1),re.S|re.I)
   if para and len(text(para.group(1)))>=80:
    block=f'{START}\n<div class="geo-answer" aria-label="Reponse essentielle">{para.group(0)}</div>\n{END}'
    pos=s.find(para.group(0)); s=s[:pos]+block+s[pos+len(para.group(0)):]
 if '/blog/' in str(p).replace('\\','/') and 'rel="author"' not in s:
  s=s.replace('</head>','<link rel="author" href="https://ig-avocat.com/avocat-ilan-guedj">\n</head>',1)
 if s!=old: p.write_text(s,encoding='utf-8'); return 1
 return 0
if __name__=='__main__': print(sum(process(p) for p in pages()),'page(s) mises a jour')
