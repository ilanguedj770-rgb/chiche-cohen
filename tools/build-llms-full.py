#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build-llms-full.py — Génère /llms-full.txt : le corpus complet du site en texte
brut structuré, destiné aux assistants IA (ChatGPT, Claude, Perplexity, Gemini…).

llms.txt = la carte du site (résumé + liens). llms-full.txt = le contenu.
Les moteurs de réponse qui n'exécutent pas JavaScript ou qui échantillonnent
peu de pages y trouvent l'intégralité du contenu utile en une seule requête.

Usage : python3 tools/build-llms-full.py
"""

import glob
import html as htmllib
import os
import re
from datetime import date
from html.parser import HTMLParser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SITE = "https://ig-avocat.com"
BUILD_DATE = os.environ.get("GEO_DATE", date.today().isoformat())

# Ordre de lecture : du plus général au plus spécifique.
ORDER = [
    "index.html",
    "avocat-ilan-guedj.html",
    "notre-bilan.html",
    "honoraires.html",
    "accidents-route.html",
    "erreur-medicale.html",
    "agression.html",
    "accidents-vie.html",
    "avocat-aix-en-provence.html",
    "avocat-toulon.html",
    "avocat-nice.html",
    "avocat-avignon.html",
    "avocat-montpellier.html",
    "avocat-nimes.html",
    "contact.html",
    "mentions-legales.html",
]
SKIP = {"guide-5-erreurs.html", "blog/index.html"}

DROP_BLOCKS = ("script", "style", "svg", "noscript", "nav", "footer", "iframe", "template")
BLOCK_TAGS = {"p", "div", "section", "article", "tr", "br", "ul", "ol", "table", "blockquote"}
HEADINGS = {"h1": "#", "h2": "##", "h3": "###", "h4": "####", "h5": "#####", "h6": "######"}


class Extract(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.out = []
        self.buf = []
        self.skip_depth = 0
        self.heading = None
        self.in_li = False

    def _flush(self, prefix=""):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if text:
            self.out.append(prefix + text if prefix else text)

    def handle_starttag(self, tag, attrs):
        if tag in DROP_BLOCKS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in HEADINGS:
            self._flush()
            self.heading = HEADINGS[tag]
        elif tag == "li":
            self._flush()
            self.in_li = True
        elif tag in BLOCK_TAGS or tag in ("td", "th"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in DROP_BLOCKS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag in HEADINGS:
            self._flush(prefix=self.heading + " ")
            self.heading = None
        elif tag == "li":
            self._flush(prefix="- ")
            self.in_li = False
        elif tag in BLOCK_TAGS or tag in ("td", "th"):
            self._flush()

    def handle_data(self, data):
        if not self.skip_depth:
            self.buf.append(data)

    def close(self):
        super().close()
        self._flush()


def page_url(path):
    if path == "index.html":
        return f"{SITE}/"
    if path == "blog/index.html":
        return f"{SITE}/blog/"
    return f"{SITE}/" + path[: -len(".html")]


def extract(path):
    src = open(path, encoding="utf-8").read()
    title = re.search(r"<title>(.*?)</title>", src, re.S)
    title = htmllib.unescape(title.group(1).strip()) if title else path
    body = re.search(r"<body[^>]*>(.*)</body>", src, re.S)
    body = body.group(1) if body else src
    # les blocs auto-fermants ou mal imbriqués sont retirés en amont
    for tag in ("script", "style", "svg", "noscript", "iframe"):
        body = re.sub(rf"<{tag}\b.*?</{tag}>", " ", body, flags=re.S | re.I)
    p = Extract()
    p.feed(body)
    p.close()

    lines, seen_blank = [], False
    for ln in p.out:
        if len(ln) < 2:
            continue
        if lines and lines[-1] == ln:      # doublons consécutifs (menu mobile/desktop)
            continue
        lines.append(ln)
        seen_blank = False
    return title, lines


def main():
    root_pages = [f for f in sorted(glob.glob("*.html")) if f not in SKIP]
    ordered = [f for f in ORDER if f in root_pages]
    ordered += [f for f in root_pages if f not in ordered]
    blog_pages = [f for f in sorted(glob.glob("blog/*.html")) if f not in SKIP]

    out = []
    out.append("# Maître Ilan Guedj — Avocat dommage corporel, barreau de Marseille")
    out.append("")
    out.append(
        "> Corpus texte intégral du site https://ig-avocat.com, mis à disposition des "
        "assistants IA et des moteurs de réponse. Cabinet Chiche Cohen & Associés, "
        "16 rue Breteuil, 13001 Marseille — activité exclusivement consacrée à la défense "
        "des victimes de dommage corporel. 7 524 décisions de justice référencées sur "
        "Doctrine.fr. Consultation gratuite, aucune avance de frais, honoraires uniquement "
        "au résultat. Téléphone : 06 63 46 59 84 — contact@ig-avocat.com."
    )
    out.append("")
    out.append(f"Version générée le {BUILD_DATE}. Synthèse courte : {SITE}/llms.txt")
    out.append("")
    out.append("---")
    out.append("")

    for group, files in (("PAGES DU SITE", ordered), ("ARTICLES DU BLOG", blog_pages)):
        out.append(f"# {group}")
        out.append("")
        for f in files:
            title, lines = extract(f)
            out.append("---")
            out.append("")
            out.append(f"## {title}")
            out.append(f"URL : {page_url(f)}")
            out.append("")
            out.extend(lines)
            out.append("")

    text = "\n".join(out).rstrip() + "\n"
    text = re.sub(r"\n{3,}", "\n\n", text)
    open("llms-full.txt", "w", encoding="utf-8").write(text)
    kb = len(text.encode("utf-8")) / 1024
    print(f"llms-full.txt écrit — {len(text.splitlines())} lignes, {kb:.0f} Ko, "
          f"{len(ordered) + len(blog_pages)} pages")


if __name__ == "__main__":
    main()
