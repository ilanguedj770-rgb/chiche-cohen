#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Index de la recherche du site (search-index.json) — ig-avocat.com.

Une entrée par page indexable (titre, description, intertitres) et une entrée
par définition du lexique. Lu par js/ig-ui.js à la première ouverture de la
recherche. Fichier généré : ne pas l'éditer à la main.

Usage : python3 tools/build-search.py
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
DOMAINES = {"accidents-route", "erreur-medicale", "agression", "accidents-vie",
            "accident-moto-marseille", "pieton-cycliste-marseille"}
OUTILS = {"blog/simulateur-dfp-capitalisation", "dossier-en-ligne"}
TAG = re.compile(r"<[^>]+>")


def text(fragment: str) -> str:
    fragment = re.sub(r"<(script|style|svg)\b.*?</\1>", " ", fragment, flags=re.S | re.I)
    return " ".join(html.unescape(TAG.sub(" ", fragment)).split())


def kind(slug: str) -> str:
    if slug in OUTILS:
        return "Outil"
    if slug in DOMAINES:
        return "Domaine"
    if slug.startswith("avocat-") and slug != "avocat-ilan-guedj":
        return "Ville"
    if slug.startswith("blog/") and slug != "blog/index":
        return "Guide"
    return "Page"


entries = []
for p in sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html")):
    s = p.read_text(encoding="utf-8")
    if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', s, re.I):
        continue
    m = re.search(r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']https://ig-avocat\.com([^"\']*)', s, re.I)
    if not m:
        continue
    slug = p.relative_to(ROOT).as_posix()[:-5]
    url = m.group(1) or "/"
    h1 = re.search(r"<h1\b[^>]*>(.*?)</h1>", s, re.S | re.I)
    title = text(h1.group(1)) if h1 else text(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
    title = title.rstrip(". ")
    if slug == "index":
        title = "Accueil — avocat en dommage corporel à Marseille"
    d = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', s)
    body = s[s.find("<!-- LAYOUT:NAV:END -->"):s.find("<!-- LAYOUT:FOOTER:START -->")]
    heads = [text(h) for h in re.findall(r"<h2\b[^>]*>(.*?)</h2>", body, re.S | re.I)]
    heads = [re.sub(r"^\d+[.)]\s*", "", h) for h in heads if h and not re.match(r"(?i)articles? li|questions? fr", h)][:24]
    entries.append({"u": url, "t": title, "d": html.unescape(d.group(1)) if d else "", "k": kind(slug), "h": heads})

    if slug == "lexique-dommage-corporel":
        for a in re.finditer(r'<article id="([^"]+)"[^>]*>(.*?)</article>', s, re.S):
            term = re.search(r"<h[23]\b[^>]*>(.*?)</h[23]>", a.group(2), re.S)
            first = re.search(r"<p\b[^>]*>(.*?)</p>", a.group(2), re.S)
            if not term:
                continue
            desc = text(first.group(1)) if first else ""
            if len(desc) > 150:
                desc = desc[:147].rsplit(" ", 1)[0] + "…"
            entries.append({"u": f"{url}#{a.group(1)}", "t": text(term.group(1)), "d": desc, "k": "Lexique", "h": []})

out = ROOT / "search-index.json"
out.write_text(json.dumps(entries, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
print(f"search-index.json : {len(entries)} entrées, {out.stat().st_size // 1024} Ko")
