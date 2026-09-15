#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère /feed.xml : flux RSS 2.0 des guides du blog.

Un flux daté est l'un des moyens les plus simples d'annoncer une nouvelle
page aux agrégateurs, à Bing et aux robots des moteurs de réponse qui
surveillent les sources d'un site. Les dates proviennent de tools/sitedates.py.
"""
import glob
import html
import os
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitedates import ROOT, page_dates  # noqa: E402

SITE = "https://ig-avocat.com"


def rfc822(iso):
    return format_datetime(datetime(*map(int, iso[:10].split("-")), 9, 0,
                                    tzinfo=timezone.utc))


def get(pattern, text):
    m = re.search(pattern, text, re.S | re.I)
    return html.unescape(m.group(1).strip()) if m else ""


def items():
    out = []
    for path in glob.glob(os.path.join(ROOT, "blog", "*.html")):
        if path.endswith("index.html"):
            continue
        src = open(path, encoding="utf-8").read()
        if re.search(r'<meta[^>]+name=["\']robots["\'][^>]+noindex', src, re.I):
            continue
        link = get(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', src)
        title = get(r"<title>(.*?)</title>", src)
        desc = get(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', src)
        pub, mod = page_dates(path, src)
        if link and title:
            out.append((pub, mod, link, title, desc))
    return sorted(out, key=lambda x: (x[0], x[2]), reverse=True)


def main():
    rows = items()
    last = max((m for _, m, *_ in rows), default="1970-01-01")
    x = ['<?xml version="1.0" encoding="UTF-8"?>',
         '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" '
         'xmlns:dc="http://purl.org/dc/elements/1.1/">',
         "  <channel>",
         "    <title>Guides de Maître Ilan Guedj — avocat en dommage corporel à Marseille</title>",
         f"    <link>{SITE}/blog/</link>",
         '    <atom:link href="https://ig-avocat.com/feed.xml" rel="self" type="application/rss+xml"/>',
         "    <description>Réponses juridiques sourcées pour les victimes d'accidents de la "
         "circulation, d'erreurs médicales, d'agressions et d'accidents de la vie, "
         "par Maître Ilan Guedj, avocat au barreau de Marseille.</description>",
         "    <language>fr-FR</language>",
         f"    <lastBuildDate>{rfc822(last)}</lastBuildDate>",
         "    <managingEditor>contact@ig-avocat.com (Maître Ilan Guedj)</managingEditor>",
         f"    <image><url>{SITE}/img/og-cover.jpg</url><title>Maître Ilan Guedj</title>"
         f"<link>{SITE}/</link></image>"]
    for pub, mod, link, title, desc in rows:
        x += ["    <item>",
              f"      <title>{html.escape(title)}</title>",
              f"      <link>{html.escape(link)}</link>",
              f'      <guid isPermaLink="true">{html.escape(link)}</guid>',
              f"      <description>{html.escape(desc)}</description>",
              "      <dc:creator>Maître Ilan Guedj</dc:creator>",
              f"      <pubDate>{rfc822(pub)}</pubDate>",
              f"      <dc:date>{mod}</dc:date>",
              "    </item>"]
    x += ["  </channel>", "</rss>", ""]
    open(os.path.join(ROOT, "feed.xml"), "w", encoding="utf-8").write("\n".join(x))
    print(f"feed.xml écrit — {len(rows)} articles")


if __name__ == "__main__":
    main()
