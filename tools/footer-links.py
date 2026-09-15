#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Garantit, dans le pied de page de toutes les pages, un lien vers les pages
« entité » du site (profil de l'avocat, lexique). Idempotent : n'ajoute un lien
que s'il est absent. Les liens de pied de page sont ce qu'un robot suit sur
chaque page : c'est le maillage minimal pour qu'aucune page clé ne soit orpheline.
"""
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (slug, libellé) — insérés juste après le lien vers le profil de l'avocat.
LINKS = [("lexique-dommage-corporel", "Lexique")]
ANCHOR = re.compile(r'(<a href="(\.\./)?avocat-ilan-guedj"([^>]*)>Maître Ilan Guedj</a>)')


def process(path):
    src = open(path, encoding="utf-8").read()
    out = src
    for slug, label in LINKS:
        if re.search(rf'href="(\.\./)?{re.escape(slug)}"', out):
            continue
        m = None
        # Le dernier lien « Maître Ilan Guedj » de la page est celui du pied de page.
        for m in ANCHOR.finditer(out):
            pass
        if not m:
            print(f"  -- {os.path.relpath(path, ROOT)} : pied de page non reconnu")
            continue
        prefix, attrs = m.group(2) or "", m.group(3)
        sep = "\n" + " " * (len(out[:m.start()]) - len(out[:m.start()].rstrip(" ")))
        out = out[:m.end()] + sep + f'<a href="{prefix}{slug}"{attrs}>{label}</a>' + out[m.end():]
    if out != src:
        open(path, "w", encoding="utf-8").write(out)
        return 1
    return 0


if __name__ == "__main__":
    files = sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                   glob.glob(os.path.join(ROOT, "blog", "*.html")))
    print("Pieds de page mis à jour :", sum(process(f) for f in files))
