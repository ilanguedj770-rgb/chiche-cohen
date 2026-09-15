#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit GEO/SEO statique du site ig-avocat.com.

Usage: python3 tools/geo-audit.py
Retourne 1 si une erreur bloquante est detectee.

Contrôles (état de l'art 2026 des moteurs de réponse) :
- chaque page : title, canonical unique, H1 unique, graphe d'entités, JSON-LD valide ;
- pages indexables : meta robots sans limite d'extrait (max-snippet:-1), jamais de
  noarchive / nocache / noai (retirent le contenu de Copilot, Alexa, AI Overviews) ;
- type schema.org Attorney (déprécié) absent des @type ;
- blog : auteur canonique, bloc de réponse, date visible <time datetime> cohérente
  avec le JSON-LD Article ;
- sitemap : lastmod réels (pas tous identiques), feed.xml, clé IndexNow, _headers.
"""
from pathlib import Path
import re, sys, json

ROOT = Path(__file__).resolve().parents[1]
HTML = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html"))
errors=[]; warnings=[]
seen_titles={}; seen_canonicals={}

def one(pattern, text):
    m=re.search(pattern,text,re.I|re.S); return m.group(1).strip() if m else None

def jsonld(text):
    for i, raw in enumerate(re.findall(r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',text,re.I|re.S),1):
        yield i, raw

for p in HTML:
    s=p.read_text(encoding="utf-8")
    rel=p.relative_to(ROOT).as_posix()
    title=one(r"<title>(.*?)</title>",s)
    canonical=one(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',s)
    h1=re.findall(r"<h1\b",s,re.I)
    robots=one(r'<meta[^>]+name=["\']robots["\'][^>]+content=["\']([^"\']+)',s) or ""
    noindex=bool(re.search(r'noindex',robots,re.I))
    if not title: errors.append(f"{rel}: title manquant")
    if not canonical: errors.append(f"{rel}: canonical manquant")
    if len(h1)!=1: warnings.append(f"{rel}: {len(h1)} H1")
    if noindex: warnings.append(f"{rel}: noindex")
    if re.search(r'noarchive|nocache|noai|noimageai',robots,re.I): errors.append(f"{rel}: directive robots '{robots}' bloque les moteurs de réponse")
    if not noindex and 'max-snippet:-1' not in robots: errors.append(f"{rel}: meta robots max-snippet:-1 manquante")
    if 'GEO:ENTITY-GRAPH:START' not in s: errors.append(f"{rel}: graphe GEO manquant")
    if '/llms.txt' not in s: warnings.append(f"{rel}: lien llms.txt manquant")
    if not noindex and 'type="application/rss+xml"' not in s: warnings.append(f"{rel}: lien vers feed.xml manquant")
    if not noindex and 'class="geo-answer' not in s: warnings.append(f"{rel}: pas de bloc geo-answer")
    if title:
        if title in seen_titles: warnings.append(f"{rel}: title duplique avec {seen_titles[title]}")
        seen_titles[title]=rel
    if canonical:
        if canonical in seen_canonicals: errors.append(f"{rel}: canonical duplique avec {seen_canonicals[canonical]}")
        seen_canonicals[canonical]=rel
    article=None
    for i, raw in jsonld(s):
        try: data=json.loads(raw)
        except Exception as e: errors.append(f"{rel}: JSON-LD #{i} invalide ({e})"); continue
        if '"Attorney"' in raw and '"additionalType"' not in raw:
            errors.append(f"{rel}: JSON-LD #{i} utilise le type Attorney (déprécié, utiliser LegalService)")
        nodes = data.get("@graph",[data]) if isinstance(data,dict) else []
        for n in nodes:
            if isinstance(n,dict) and n.get("@type") in ("Article","BlogPosting","NewsArticle"): article=n
    if rel.startswith("blog/") and rel!="blog/index.html":
        if 'ilan-guedj' not in s.lower(): warnings.append(f"{rel}: auteur canonique non detectable")
        if not article: warnings.append(f"{rel}: pas de JSON-LD Article")
        times=re.findall(r'<time datetime="(\d{4}-\d{2}-\d{2})"',s)
        if not times: errors.append(f"{rel}: pas de date visible <time datetime>")
        elif article:
            pub=(article.get("datePublished") or "")[:10]; mod=(article.get("dateModified") or pub)[:10]
            if pub and pub not in times: errors.append(f"{rel}: date visible {times} ≠ datePublished {pub}")
            if mod and mod!=pub and mod not in times: errors.append(f"{rel}: dateModified {mod} non affichée")

# Fichiers globaux
sitemap=(ROOT/"sitemap.xml")
if not sitemap.exists(): errors.append("sitemap.xml manquant")
else:
    mods=re.findall(r"<lastmod>([^<]+)</lastmod>",sitemap.read_text(encoding="utf-8"))
    if mods and len(set(mods))==1: warnings.append("sitemap.xml: tous les lastmod sont identiques (signal de fraîcheur ignoré par Google)")
    locs=re.findall(r"<loc>([^<]+)</loc>",sitemap.read_text(encoding="utf-8"))
    for c in seen_canonicals:
        if c not in locs and not re.search(r'noindex',(ROOT/seen_canonicals[c]).read_text(encoding="utf-8").split("</head>")[0],re.I):
            errors.append(f"sitemap.xml: {c} absent")
if not (ROOT/"feed.xml").exists(): errors.append("feed.xml manquant (python3 tools/build-feed.py)")
if not list(ROOT.glob("[0-9a-f]"*8+"*.txt")) or not any(re.fullmatch(r"[0-9a-f]{8,128}\.txt",f.name) for f in ROOT.glob("*.txt")):
    errors.append("clé IndexNow (<clé>.txt) manquante à la racine")
if not (ROOT/"_headers").exists(): warnings.append("_headers manquant")
else:
    h=(ROOT/"_headers").read_text(encoding="utf-8")
    if re.search(r'X-Robots-Tag:.*(noarchive|nocache|noai)',h,re.I): errors.append("_headers: X-Robots-Tag bloque les moteurs de réponse")
robots_txt=(ROOT/"robots.txt").read_text(encoding="utf-8") if (ROOT/"robots.txt").exists() else ""
for ua in ("OAI-SearchBot","Claude-SearchBot","PerplexityBot","MistralAI-Index","Googlebot","bingbot","Applebot"):
    if ua not in robots_txt: warnings.append(f"robots.txt: agent {ua} non listé explicitement")
for f in ("llms.txt",):
    if not (ROOT/f).exists(): errors.append(f"{f} manquant")

print(f"GEO audit: {len(HTML)} pages, {len(errors)} erreurs, {len(warnings)} avertissements")
for x in errors: print("ERROR",x)
for x in warnings: print("WARN ",x)
sys.exit(1 if errors else 0)
