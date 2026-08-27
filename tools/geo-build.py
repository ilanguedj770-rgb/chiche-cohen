#!/usr/bin/env python3
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
for step in ['geo-content-inject.py','geo-inject.py','build-sitemap.py','build-llms-full.py','geo-audit.py','check-internal-links.py']:
 print('==',step); r=subprocess.run([sys.executable,str(ROOT/'tools'/step)],cwd=ROOT)
 if r.returncode: raise SystemExit(r.returncode)
