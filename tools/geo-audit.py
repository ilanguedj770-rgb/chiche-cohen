#!/usr/bin/env python3
"""Audit GEO/SEO statique du site ig-avocat.com.

Usage: python3 tools/geo-audit.py
Retourne 1 si une erreur bloquante est detectee.
"""
from pathlib import Path
import re, sys, json

ROOT = Path(__file__).resolve().parents[1]
HTML = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html"))
errors=[]; warnings=[]
seen_titles={}; seen_canonicals={}

def one(pattern, text):
    m=re.search(pattern,text,re.I|re.S); return m.group(1).strip() if m else None

for p in HTML:
    s=p.read_text(encoding="utf-8")
    rel=p.relative_to(ROOT).as_posix()
    title=one(r"<title>(.*?)</title>",s)
    canonical=one(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',s)
    h1=re.findall(r"<h1\b",s,re.I)
    if not title: errors.append(f"{rel}: title manquant")
    if not canonical: errors.append(f"{rel}: canonical manquant")
    if len(h1)!=1: warnings.append(f"{rel}: {len(h1)} H1")
    if 'name="robots"' in s and re.search(r'noindex',s,re.I): warnings.append(f"{rel}: noindex")
    if 'GEO:ENTITY-GRAPH:START' not in s: errors.append(f"{rel}: graphe GEO manquant")
    if '/llms.txt' not in s: warnings.append(f"{rel}: lien llms.txt manquant")
    if title:
        if title in seen_titles: warnings.append(f"{rel}: title duplique avec {seen_titles[title]}")
        seen_titles[title]=rel
    if canonical:
        if canonical in seen_canonicals: errors.append(f"{rel}: canonical duplique avec {seen_canonicals[canonical]}")
        seen_canonicals[canonical]=rel
    # JSON-LD: parse chaque script pour reperer les JSON invalides.
    for i, raw in enumerate(re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',s,re.I|re.S),1):
        try: json.loads(raw)
        except Exception as e: errors.append(f"{rel}: JSON-LD #{i} invalide ({e})")
    if rel.startswith("blog/"):
        if 'ilan-guedj' not in s.lower(): warnings.append(f"{rel}: auteur canonique non detectable")
        if 'geo-answer' not in s: warnings.append(f"{rel}: pas de bloc geo-answer")

print(f"GEO audit: {len(HTML)} pages, {len(errors)} erreurs, {len(warnings)} avertissements")
for x in errors: print("ERROR",x)
for x in warnings: print("WARN ",x)
sys.exit(1 if errors else 0)
