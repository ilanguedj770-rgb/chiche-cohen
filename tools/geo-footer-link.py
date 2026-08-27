#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute (une seule fois) le lien vers la page d'entité /avocat-ilan-guedj
dans le pied de page de toutes les pages du site. Idempotent."""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)

PAT = re.compile(
    r'(\n(\s*)<a href="(\.\./)?mentions-legales"([^>]*)>Mentions Légales</a>)'
)
changed = 0
for f in sorted(glob.glob("*.html") + glob.glob("blog/*.html")):
    s = open(f, encoding="utf-8").read()
    if 'href="avocat-ilan-guedj"' in s or 'href="../avocat-ilan-guedj"' in s:
        continue
    m = PAT.search(s)
    if not m:
        print(f"  -- {f}: pas de lien 'Mentions Légales' en pied de page")
        continue
    indent, prefix, attrs = m.group(2), m.group(3) or "", m.group(4)
    link = f'\n{indent}<a href="{prefix}avocat-ilan-guedj"{attrs}>Maître Ilan Guedj</a>'
    s = s[: m.start(1)] + link + s[m.start(1) :]
    open(f, "w", encoding="utf-8").write(s)
    changed += 1
    print(f"  maj  {f}")

# Second gabarit de pied de page (pages piliers et pages villes)
PAT2 = '<div class="flex gap-8 font-bold mb-6"><a href="mentions-legales"'
NEW2 = ('<div class="flex gap-8 font-bold mb-6">'
        '<a href="avocat-ilan-guedj" class="hover:text-white transition">Maître Ilan Guedj</a>'
        '<a href="mentions-legales"')
for f in sorted(glob.glob("*.html")):
    s2 = open(f, encoding="utf-8").read()
    if 'href="avocat-ilan-guedj"' in s2 or PAT2 not in s2:
        continue
    open(f, "w", encoding="utf-8").write(s2.replace(PAT2, NEW2, 1))
    changed += 1
    print(f"  maj  {f}")

print(f"\n{changed} pied(s) de page mis à jour")
