#!/usr/bin/env python3
"""Migration éditoriale du site vers la marque unique Maître Ilan Guedj.
Conserve mentions-legales.html hors remplacement automatique afin de ne pas supprimer une dénomination légalement nécessaire.
"""
from pathlib import Path
import re,sys
ROOT=Path(__file__).resolve().parents[1]
EXCLUDE={'mentions-legales.html'}
REPLACEMENTS=[
 (r'Cabinet Chiche Cohen\s*&\s*Associés\s*[—–-]\s*Maître Ilan Guedj','Maître Ilan Guedj — Avocat en dommage corporel'),
 (r'Cabinet Chiche Cohen\s*&\s*Associés','Maître Ilan Guedj'),
 (r'Chiche Cohen\s*&\s*Associés','Maître Ilan Guedj'),
 (r'Cabinet Chiche Cohen','Cabinet Ilan Guedj'),
 (r'Cabinet Guedj Chiche Cohen','Cabinet Ilan Guedj'),
 (r'CHICHE COHEN\s*&\s*ASSOCIES','ILAN GUEDJ'),
]
def files():
 for p in ROOT.rglob('*'):
  if p.is_file() and p.suffix.lower() in {'.html','.txt','.md','.py','.xml'} and '.git' not in p.parts and p.name not in EXCLUDE and p.name!='brand-ilan-guedj.py': yield p
def migrate(p):
 s=p.read_text(encoding='utf-8');o=s
 for pat,repl in REPLACEMENTS:s=re.sub(pat,repl,s,flags=re.I)
 if s!=o:p.write_text(s,encoding='utf-8');return True
 return False
def check():
 bad=[]
 for p in files():
  if re.search(r'Chiche\s+Cohen|CHICHE\s+COHEN',p.read_text(encoding='utf-8'),re.I):bad.append(str(p.relative_to(ROOT)))
 print('Références Chiche Cohen hors mentions légales :',len(bad));[print(' -',x) for x in bad];return 1 if bad else 0
if __name__=='__main__':
 if '--check' in sys.argv:raise SystemExit(check())
 print('Fichiers harmonisés :',sum(migrate(p) for p in files()));raise SystemExit(check())