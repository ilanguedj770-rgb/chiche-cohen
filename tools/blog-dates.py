#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Affiche sur chaque article du blog une date lisible ET machine (<time datetime>)
alignée sur les dates déclarées dans son JSON-LD Article.

Les moteurs de réponse privilégient les contenus datés de façon visible et
cohérente entre le HTML et les données structurées. Idempotent.
"""
import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitedates import ROOT, page_dates, fr_date  # noqa: E402

# Le <span> de la ligne « méta » qui porte l'icône calendrier (tracé Lucide).
SPAN = re.compile(
    r'(<span class="flex items-center gap-2">\s*<svg[^>]*>(?:(?!</svg>).)*<path d="M8 2v4"/>(?:(?!</svg>).)*</svg>)(.*?)(</span>)',
    re.S)


def render(pub, mod):
    out = f' <time datetime="{pub}">Publié le {fr_date(pub)}</time>'
    if mod != pub:
        out += f' · <time datetime="{mod}">Mis à jour le {fr_date(mod)}</time>'
    return out


def process(path):
    src = open(path, encoding="utf-8").read()
    pub, mod = page_dates(path, src)
    m = SPAN.search(src)
    if not m:
        return False
    new = m.group(1) + render(pub, mod) + m.group(3)
    if new == m.group(0):
        return False
    src = src[:m.start()] + new + src[m.end():]
    open(path, "w", encoding="utf-8").write(src)
    return True


if __name__ == "__main__":
    files = [f for f in sorted(glob.glob(os.path.join(ROOT, "blog", "*.html")))
             if not f.endswith("index.html")]
    print("Dates visibles mises à jour :", sum(process(f) for f in files))
