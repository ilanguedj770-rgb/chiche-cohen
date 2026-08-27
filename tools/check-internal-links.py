#!/usr/bin/env python3
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]; errors=[]
for p in list(ROOT.glob('*.html'))+list((ROOT/'blog').glob('*.html')):
 s=p.read_text(encoding='utf-8')
 for href in re.findall(r'href=["\']([^"\']+)',s,re.I):
  if not href.startswith('/') or href.startswith('//') or href.startswith('/#'): continue
  x=href.split('#')[0].split('?')[0].strip('/')
  if not x: target=ROOT/'index.html'
  else:
   target=ROOT/(x+'.html')
   if not target.exists(): target=ROOT/x/'index.html'
  if not target.exists() and not x.startswith(('img/','css/','js/','fonts/','llms','sitemap','robots')): errors.append(f'{p.relative_to(ROOT)} -> {href}')
print('\n'.join(errors) if errors else 'Liens internes: OK'); sys.exit(bool(errors))
