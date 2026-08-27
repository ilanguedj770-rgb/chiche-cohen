#!/usr/bin/env python3
"""Pipeline GEO local. Les etapes modifiant les pages restent idempotentes."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
steps=['geo-content-inject.py','geo-inject.py','build-sitemap.py','build-llms-full.py','geo-audit.py','check-internal-links.py']
for x in steps:
 print('==',x); r=subprocess.run([sys.executable,str(ROOT/'tools'/x)],cwd=ROOT)
 if r.returncode: raise SystemExit(r.returncode)
