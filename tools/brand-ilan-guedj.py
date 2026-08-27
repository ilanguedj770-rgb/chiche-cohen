#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Harmonisation éditoriale du site autour de la seule entité Maître Ilan Guedj.

Le site ne doit plus présenter de structure collective (cabinet Chiche Cohen,
associés, collaborateurs) ni d'indicateurs chiffrés attachés à cette structure
(décisions Doctrine, victimes accompagnées, ancienneté du cabinet).

Le script agit sur deux couches :
  * les blocs JSON-LD, analysés puis réécrits (suppression des entités et des
    références externes propres au cabinet) ;
  * le texte visible et les métadonnées, nettoyés phrase par phrase.

Usage :
    python3 tools/brand-ilan-guedj.py           # applique la migration
    python3 tools/brand-ilan-guedj.py --check   # signale les résidus
"""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

# URLs fonctionnelles : elles pointent vers des services tiers réellement
# utilisés (prise de rendez-vous, adresse historique) et ne doivent pas être
# réécrites par les règles de marque.
FROZEN = [
    "calendly.com/guedj-chiche-cohen",
]

# Ressources publiques décrivant le cabinet et non l'avocat : elles sortent du
# site.
CABINET_URLS = (
    "doctrine.fr/p/cabinet/",
    "chiche-cohen.avocat.fr",
)

FIGURES = re.compile(
    r"7[\s ]*524|7&nbsp;524|7524|plus de 7[\s ]*500"
    r"|15[\s ]*000\+?\s*(?:victimes|depuis)|15&nbsp;000"
    r"|décisions? (?:de justice )?référencées?|décisions Doctrine"
    r"|Doctrine\.fr",
    re.I,
)

NAMING = [
    (r"Cabinet Chiche Cohen\s*&(?:amp;)?\s*Associés\s*[—–-]\s*Maître Ilan Guedj",
     "Maître Ilan Guedj — Avocat en dommage corporel"),
    (r"Le cabinet de Maître Ilan Guedj \(associé à Patrice Chiche, Stéphane Cohen et Daniel Amar\)",
     "Maître Ilan Guedj"),
    (r"\s*\((?:Patrice Chiche, Stéphane Cohen, Daniel Amar et )?Maître Ilan Guedj\)", ""),
    (r"\s*\(associé à Patrice Chiche, Stéphane Cohen et Daniel Amar\)", ""),
    (r"\s*[—–-]\s*Patrice Chiche, Stéphane Cohen, Daniel Amar et Maître Ilan Guedj\s*[—–-]?", " "),
    (r",?\s*(?:et\s+)?associés?\s+du\s+cabinet\s+Chiche\s+Cohen(?:\s*&(?:amp;)?\s*Associés)?", ""),
    (r"cabinet\s+Chiche\s+Cohen\s*&(?:amp;)?\s*Associés", "cabinet de Maître Ilan Guedj"),
    (r"Chiche\s+Cohen\s*&(?:amp;)?\s*Associés", "Maître Ilan Guedj"),
    (r"Cabinet\s+Guedj\s+Chiche\s+Cohen", "Cabinet Ilan Guedj"),
    (r"[Cc]abinet\s+Chiche\s+Cohen", "cabinet de Maître Ilan Guedj"),
    (r"CHICHE\s+COHEN\s*&(?:amp;)?\s*ASSOCIES", "ILAN GUEDJ"),
    (r"SELARL\s+Chiche\s+Cohen", "cabinet de Maître Ilan Guedj"),
    (r"Chiche\s+Cohen", "Ilan Guedj"),
]

SENTENCE_SPLIT = re.compile(r"(?<=[.!?])[\s ]+")


def freeze(text):
    """Neutralise les URLs fonctionnelles avant application des règles."""
    for i, needle in enumerate(FROZEN):
        text = text.replace(needle, f"\x00FROZEN{i}\x00")
    return text


def thaw(text):
    for i, needle in enumerate(FROZEN):
        text = text.replace(f"\x00FROZEN{i}\x00", needle)
    return text


def rename(text):
    for pattern, replacement in NAMING:
        text = re.sub(pattern, replacement, text)
    return text


def scrub_prose(text):
    """Applique les règles de marque puis retire les phrases chiffrées."""
    text = rename(text)
    kept = [s for s in SENTENCE_SPLIT.split(text) if not FIGURES.search(s)]
    text = " ".join(kept)
    return re.sub(r"\s{2,}", " ", text).strip()


def prune_json(node):
    """Retire récursivement les entités et chaînes propres au cabinet."""
    if isinstance(node, dict):
        if any(isinstance(v, str) and any(u in v for u in CABINET_URLS)
               for v in node.values()):
            return None
        out = {}
        for key, value in node.items():
            pruned = prune_json(value)
            if pruned in (None, [], ""):
                continue
            out[key] = pruned
        return out or None
    if isinstance(node, list):
        out = [x for x in (prune_json(v) for v in node) if x not in (None, [], "")]
        return out or None
    if isinstance(node, str):
        if any(u in node for u in CABINET_URLS):
            return None
        return scrub_prose(node) or None
    return node


JSONLD = re.compile(
    r'(<script[^>]+type="application/ld\+json"[^>]*>)(.*?)</script>',
    re.S,
)


def migrate_jsonld(html):
    def repl(match):
        try:
            data = json.loads(match.group(2))
        except ValueError:
            return match.group(0)
        body = json.dumps(prune_json(data) or {}, ensure_ascii=False, indent=2)
        return f"{match.group(1)}\n{body}\n</script>"

    return JSONLD.sub(repl, html)


META = re.compile(
    r'(<meta[^>]+(?:name|property)="(?:description|keywords|og:description|twitter:description)"'
    r'[^>]+content=")([^"]*)(")',
    re.I,
)


def migrate_meta(html):
    return META.sub(lambda m: m.group(1) + scrub_prose(m.group(2)) + m.group(3), html)


def migrate(path):
    src = path.read_text(encoding="utf-8")
    original = src
    src = freeze(src)
    if path.suffix == ".html":
        src = migrate_jsonld(src)
        src = migrate_meta(src)
    src = rename(src)
    src = thaw(src)
    if src != original:
        path.write_text(src, encoding="utf-8")
        return True
    return False


def targets():
    paths = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html"))
    paths += sorted((ROOT / "content" / "geo").glob("*.md"))
    paths += [p for p in (ROOT / "llms.txt", ROOT / "llms-full.txt") if p.exists()]
    return paths


def check():
    residues = []
    for path in targets():
        text = path.read_text(encoding="utf-8")
        for i, line in enumerate(text.splitlines(), 1):
            if any(f in line for f in FROZEN):
                continue
            if re.search(r"Chiche[\s ]+Cohen", line, re.I) or FIGURES.search(line):
                residues.append(f"{path.relative_to(ROOT)}:{i}")
    print(f"Résidus cabinet : {len(residues)}")
    for r in residues[:80]:
        print("  -", r)
    return 1 if residues else 0


def main():
    if "--check" in sys.argv:
        return check()
    changed = sum(migrate(p) for p in targets())
    print(f"Fichiers harmonisés : {changed}")
    return check()


if __name__ == "__main__":
    raise SystemExit(main())
