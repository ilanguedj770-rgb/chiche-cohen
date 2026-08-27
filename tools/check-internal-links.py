#!/usr/bin/env python3
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
files=list(ROOT.glob('*.html'))+list((ROOT/'blog').glob('*.html'))
for p in files:
 s=p.read_text(encoding='utf-8')
 for href in re.findall(r'href=["\']([^"\']+)',s,re.I):
  if not href.startswith('/') or href.startswith('//') or href.startswith('/#'): continue
  path=href.split('#')[0].split('?')[0].strip('/')
  if not path: target=ROOT/'index.html'
  else:
   target=ROOT/(path+'.html')
   if not target.exists(): target=ROOT/path/'index.html'
  if not target.exists() and not path.startswith(('img/','css/','js/','fonts/','llms','sitemap','robots')): errors.append(f'{p.relative_to(ROOT)} -> {href}')
print('\n'.join(errors) if errors else 'Liens internes: OK'); sys.exit(1 if errors else 0)
