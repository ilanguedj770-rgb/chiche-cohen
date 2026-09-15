#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Soumet les URL du site au protocole IndexNow (Bing, Yandex, Naver, Seznam).

Bing est la couche de recherche de Copilot et de ChatGPT Search : une URL
qu'il ne connaît pas ne peut pas y être citée. IndexNow lui signale chaque
page nouvelle ou modifiée en une requête, sans attendre son passage.

La clé est publique par conception (le fichier <clé>.txt à la racine du site
prouve seulement que l'expéditeur contrôle le domaine).

Usage :
  python3 tools/indexnow.py --all                 # toutes les URL du sitemap
  python3 tools/indexnow.py --since <commit>      # pages HTML modifiées depuis
  python3 tools/indexnow.py https://ig-avocat.com/blog/...   # URL explicites
  python3 tools/indexnow.py --dry-run --all       # n'envoie rien, affiche
"""
import glob
import json
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ig-avocat.com"
HOST = "ig-avocat.com"
ENDPOINT = "https://api.indexnow.org/IndexNow"


def key():
    files = [f for f in glob.glob(os.path.join(ROOT, "*.txt"))
             if re.fullmatch(r"[0-9a-f]{8,128}\.txt", os.path.basename(f))]
    if not files:
        sys.exit("Aucun fichier de clé IndexNow (<clé hexadécimale>.txt) à la racine.")
    k = os.path.basename(files[0])[:-4]
    assert open(files[0], encoding="utf-8").read().strip() == k, "clé ≠ nom du fichier"
    return k


def sitemap_urls():
    xml = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
    return re.findall(r"<loc>([^<]+)</loc>", xml)


def url_for(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return f"{SITE}/{rel[:-len('index.html')]}"
    if rel.endswith(".html"):
        return f"{SITE}/{rel[:-5]}"
    return None


def changed_since(ref):
    r = subprocess.run(["git", "diff", "--name-only", f"{ref}..HEAD", "--"],
                       cwd=ROOT, capture_output=True, text=True)
    if r.returncode or set(ref) <= {"0"}:      # référence inconnue (premier push)
        print("Référence git inconnue : soumission de tout le sitemap.")
        return sitemap_urls()
    out = r.stdout.split()
    valid = set(sitemap_urls())
    urls = set()
    for f in out:
        u = url_for(os.path.join(ROOT, f))
        if u in valid:
            urls.add(u)
        if f in ("sitemap.xml", "llms.txt", "llms-full.txt", "feed.xml", "robots.txt"):
            urls.add(f"{SITE}/{f}")
    return sorted(urls)


def submit(urls, dry_run=False):
    if not urls:
        print("IndexNow : rien à soumettre.")
        return 0
    k = key()
    payload = {"host": HOST, "key": k, "keyLocation": f"{SITE}/{k}.txt",
               "urlList": urls[:10000]}
    print(f"IndexNow : {len(payload['urlList'])} URL")
    for u in payload["urlList"]:
        print("  -", u)
    if dry_run:
        return 0
    req = urllib.request.Request(
        ENDPOINT, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            print("Réponse :", r.status)
            return 0
    except urllib.error.HTTPError as e:
        print("Réponse :", e.code, e.read().decode("utf-8", "replace")[:300])
        # 200 accepté, 202 accepté (clé à valider) ; le reste est une erreur.
        return 0 if e.code in (200, 202) else 1


def main(argv):
    dry = "--dry-run" in argv
    argv = [a for a in argv if a != "--dry-run"]
    if "--all" in argv:
        urls = sitemap_urls() + [f"{SITE}/llms.txt", f"{SITE}/llms-full.txt",
                                 f"{SITE}/feed.xml"]
    elif "--since" in argv:
        urls = changed_since(argv[argv.index("--since") + 1])
    else:
        urls = [a for a in argv if a.startswith("http")]
        if not urls:
            print(__doc__)
            return 2
    return submit(urls, dry)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
