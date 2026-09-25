#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dates réelles des pages, partagées par les générateurs (sitemap, graphe, flux).

Règle : une date de mise à jour n'est un signal utile pour Google et les
moteurs de réponse que si elle est vraie. On ne « rafraîchit » donc jamais
toutes les pages à la date du jour. Pour chaque page :

- datePublished : la valeur déclarée dans l'Article JSON-LD de la page si elle
  existe, sinon la date du premier commit du fichier ;
- dateModified  : la valeur déclarée dans l'Article JSON-LD si elle existe,
  sinon la date du dernier commit du fichier, ou la date du jour si le fichier
  a des modifications non commitées.

`GEO_DATE=AAAA-MM-JJ` force la date « du jour » (builds reproductibles).
"""
import json
import os
import re
import subprocess
from datetime import date
from functools import lru_cache

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = os.environ.get("GEO_DATE", date.today().isoformat())
_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}")

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def _git(*args):
    try:
        out = subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                             text=True, check=False).stdout.strip()
    except OSError:
        return ""
    return out


_TIME = re.compile(r"<time\b[^>]*>.*?</time>", re.S)
_HEAD = re.compile(r"<head\b.*?</head>", re.S | re.I)
_WS = re.compile(r"\s+")
_SCRIPT = re.compile(r"<(script|style|svg)\b.*?</\1>", re.S | re.I)
_TAG = re.compile(r"<[^>]+>")


def _body_fingerprint(src):
    """Contenu comparable : hors <head> (graphe, meta injectés), hors dates
    visibles et hors espaces. Un changement de balisage technique ne doit pas
    passer pour une mise à jour éditoriale."""
    src = _HEAD.sub("", src)
    src = _TIME.sub("", src)
    # Seul le texte visible compte : une classe CSS ou un changement de
    # balisage (retour à la ligne mobile, <span> d'habillage) n'est pas une
    # mise à jour du contenu.
    src = _SCRIPT.sub(" ", src)
    src = _TAG.sub(" ", src)
    return _WS.sub(" ", src).strip()


@lru_cache(maxsize=None)
def git_dates(path):
    """(date du premier commit, date du dernier changement du CONTENU) du fichier."""
    rel = os.path.relpath(os.path.abspath(path), ROOT)
    log = _git("log", "--format=%H %cs", "--", rel).splitlines()
    if not log:
        return None, None
    first = log[-1].split()[1]
    try:
        current = _body_fingerprint(open(path, encoding="utf-8").read())
    except OSError:
        return first, log[0].split()[1]
    last = None
    for line in log:                       # du plus récent au plus ancien
        h, d = line.split()
        body = _body_fingerprint(_git("show", f"{h}:{rel}"))
        if body != current:
            break
        last = d
    if last is None:                       # contenu modifié, non commité
        last = TODAY
    return first, last


def _article_dates(src):
    for raw in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                          src, re.S | re.I):
        try:
            data = json.loads(raw)
        except ValueError:
            continue
        nodes = data.get("@graph", [data]) if isinstance(data, dict) else []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            t = node.get("@type")
            types = t if isinstance(t, list) else [t]
            if any(x in ("Article", "BlogPosting", "NewsArticle") for x in types):
                pub = node.get("datePublished")
                mod = node.get("dateModified") or pub
                pub = pub[:10] if pub and _ISO.match(pub) else None
                mod = mod[:10] if mod and _ISO.match(mod) else None
                return pub, mod
    return None, None


def page_dates(path, src=None):
    """Retourne (datePublished, dateModified) au format AAAA-MM-JJ."""
    if src is None:
        src = open(path, encoding="utf-8").read()
    pub, mod = _article_dates(src)
    first, last = git_dates(path)
    pub = pub or first or last or TODAY
    mod = mod or last or TODAY
    if mod < pub:
        mod = pub
    return pub, mod


def fr_date(iso):
    """'2026-08-27' -> '27 août 2026' (1er pour le premier jour)."""
    y, m, d = (int(x) for x in iso[:10].split("-"))
    day = "1er" if d == 1 else str(d)
    return f"{day} {MOIS[m - 1]} {y}"


if __name__ == "__main__":
    import glob
    for f in sorted(glob.glob(os.path.join(ROOT, "*.html")) +
                    glob.glob(os.path.join(ROOT, "blog", "*.html"))):
        print(os.path.relpath(f, ROOT), *page_dates(f))
