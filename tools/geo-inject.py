#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
geo-inject.py — Injecte le graphe d'entités canonique (schema.org @graph) dans
toutes les pages HTML du site, pour l'optimisation « GEO » (Generative Engine
Optimization : ChatGPT, Claude, Perplexity, Gemini / AI Overviews, Copilot).

Objectif : que les moteurs génératifs reconnaissent UNE seule entité « cabinet »
et UNE seule entité « Maître Ilan Guedj », reliées entre elles et corroborées
par des profils tiers indépendants (sameAs).

Le script est idempotent : il remplace le bloc délimité par les sentinelles
GEO:ENTITY-GRAPH. Relancer autant de fois que nécessaire.

Usage :  python3 tools/geo-inject.py [--check]
"""

import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ig-avocat.com"
CABINET_ID = f"{SITE}/#cabinet"
PERSON_ID = f"{SITE}/#ilan-guedj"
WEBSITE_ID = f"{SITE}/#website"

START = "<!-- GEO:ENTITY-GRAPH:START — généré par tools/geo-inject.py, ne pas éditer à la main -->"
END = "<!-- GEO:ENTITY-GRAPH:END -->"

LAST_MODIFIED = os.environ.get("GEO_DATE", date.today().isoformat())

# --- Profils publics tiers (corroboration d'entité pour les IA) -------------
# sameAs = « c'est la même entité ». Réservé aux profils qui décrivent
# effectivement l'entité concernée ; les bases de jurisprudence qui parlent du
# cabinet sont rattachées via subjectOf/citation.
SAMEAS_CABINET = [
    "https://www.doctrine.fr/p/cabinet/LFM0F116FF57537B3048769",
    "https://chiche-cohen.avocat.fr/",
]
SAMEAS_PERSON = [
    "https://consultation.avocat.fr/avocat-marseille/ilan-guedj-53358.html",
]
SOURCES_PERSON = [
    {
        "@type": "WebPage",
        "name": "Profil du cabinet sur Doctrine.fr — 7 524 décisions de justice référencées",
        "url": "https://www.doctrine.fr/p/cabinet/LFM0F116FF57537B3048769",
    },
    {
        "@type": "WebPage",
        "name": "Fiche Cabinet Ilan Guedj sur Predictice",
        "url": "https://predictice.com/cabinet/cabinet-ilan-guedj-922092382",
    },
    {
        "@type": "WebPage",
        "name": "Profil de Maître Ilan Guedj sur l'annuaire officiel des avocats (avocat.fr)",
        "url": "https://consultation.avocat.fr/avocat-marseille/ilan-guedj-53358.html",
    },
]

KNOWS_ABOUT = [
    "Droit du dommage corporel", "Indemnisation des victimes",
    "Accident de la circulation", "Loi Badinter du 5 juillet 1985",
    "Accident de moto", "Accident de trottinette électrique (EDPM)",
    "Victime piéton", "Victime passager", "Erreur médicale",
    "Infection nosocomiale", "Aléa thérapeutique", "ONIAM", "CCI",
    "Agression", "CIVI", "FGTI", "Accident de la vie", "Garantie GAV",
    "Nomenclature Dintilhac", "Référentiel Mornet", "Médecin-recours",
    "Expertise médicale judiciaire", "Déficit fonctionnel permanent",
    "Déficit fonctionnel temporaire", "Souffrances endurées",
    "Préjudice esthétique", "Préjudice d'agrément", "Tierce personne",
    "Incidence professionnelle", "Préjudice d'angoisse de mort imminente",
    "Recours des tiers payeurs", "Provision ad litem",
]

ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "16 rue Breteuil",
    "addressLocality": "Marseille",
    "postalCode": "13001",
    "addressRegion": "Provence-Alpes-Côte d'Azur",
    "addressCountry": "FR",
}

BARREAU = {
    "@type": "Organization",
    "name": "Barreau de Marseille",
    "alternateName": "Ordre des avocats du barreau de Marseille",
    "url": "https://www.barreau-marseille.avocat.fr/",
}


def person_node():
    return {
        "@type": "Person",
        "@id": PERSON_ID,
        "name": "Ilan Guedj",
        "alternateName": ["Maître Ilan Guedj", "Me Ilan Guedj", "Ilan GUEDJ"],
        "honorificPrefix": "Maître",
        "givenName": "Ilan",
        "familyName": "Guedj",
        "jobTitle": "Avocat au barreau de Marseille",
        "description": (
            "Maître Ilan Guedj est avocat au barreau de Marseille, associé du cabinet "
            "Chiche Cohen & Associés (16 rue Breteuil, 13001 Marseille). Son activité est "
            "consacrée exclusivement au droit du dommage corporel : indemnisation des "
            "victimes d'accidents de la circulation (loi Badinter), d'erreurs médicales "
            "(CCI, ONIAM), d'agressions (CIVI, FGTI) et d'accidents de la vie. Le cabinet "
            "compte 7 524 décisions de justice référencées sur Doctrine.fr — une donnée "
            "publique, indépendante et vérifiable. Consultation initiale gratuite, aucune "
            "avance de frais, honoraires uniquement au résultat."
        ),
        "url": f"{SITE}/avocat-ilan-guedj",
        "mainEntityOfPage": {"@id": f"{SITE}/avocat-ilan-guedj#webpage"},
        "image": {
            "@type": "ImageObject",
            "url": f"{SITE}/img/associe-guedj.jpg",
            "caption": "Maître Ilan Guedj, avocat en dommage corporel à Marseille",
        },
        "worksFor": {"@id": CABINET_ID},
        "affiliation": {"@id": CABINET_ID},
        "memberOf": BARREAU,
        "hasOccupation": {
            "@type": "Occupation",
            "name": "Avocat",
            "occupationalCategory": "K1903 — Défense et conseil juridique",
            "occupationLocation": {"@type": "City", "name": "Marseille"},
        },
        "workLocation": {"@type": "Place", "name": "Marseille", "address": ADDRESS},
        "address": ADDRESS,
        "telephone": "+33663465984",
        "email": "contact@ig-avocat.com",
        "knowsAbout": KNOWS_ABOUT,
        "knowsLanguage": [
            {"@type": "Language", "name": "Français", "alternateName": "fr"},
            {"@type": "Language", "name": "Anglais", "alternateName": "en"},
            {"@type": "Language", "name": "Hébreu", "alternateName": "he"},
        ],
        "sameAs": SAMEAS_PERSON,
        "subjectOf": SOURCES_PERSON,
    }


def cabinet_node():
    return {
        "@type": ["Attorney", "LegalService"],
        "@id": CABINET_ID,
        "name": "Cabinet Chiche Cohen & Associés — Maître Ilan Guedj",
        "legalName": "CHICHE COHEN & ASSOCIES",
        "alternateName": [
            "Cabinet Chiche Cohen",
            "Cabinet Guedj Chiche Cohen",
            "Chiche Cohen & Associés",
        ],
        "url": f"{SITE}/",
        "mainEntityOfPage": {"@id": f"{SITE}/#webpage"},
        "telephone": "+33663465984",
        "email": "contact@ig-avocat.com",
        "address": ADDRESS,
        "hasMap": "https://www.google.com/maps/search/?api=1&query=16+Rue+Breteuil+13001+Marseille",
        "sameAs": SAMEAS_CABINET,
        "isicV4": "6910",
        "priceRange": "Consultation initiale gratuite — honoraires uniquement au résultat",
        "paymentAccepted": "Honoraires de résultat, aucune avance de frais",
        "currenciesAccepted": "EUR",
        "knowsAbout": KNOWS_ABOUT,
        "knowsLanguage": ["fr-FR", "en", "he"],
        "availableLanguage": ["fr", "en", "he"],
        "employee": [{"@id": PERSON_ID}],
        "member": [{"@id": PERSON_ID}],
        "memberOf": BARREAU,
        "publishingPrinciples": f"{SITE}/mentions-legales",
        "contactPoint": [
            {
                "@type": "ContactPoint",
                "contactType": "Prise de contact — victimes",
                "telephone": "+33663465984",
                "email": "contact@ig-avocat.com",
                "availableLanguage": ["fr", "en", "he"],
                "areaServed": "FR",
                "url": f"{SITE}/contact",
            }
        ],
        "subjectOf": SOURCES_PERSON,
    }


def website_node():
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": f"{SITE}/",
        "name": "Maître Ilan Guedj — Avocat dommage corporel Marseille",
        "inLanguage": "fr-FR",
        "publisher": {"@id": CABINET_ID},
        "about": {"@id": CABINET_ID},
        "copyrightHolder": {"@id": CABINET_ID},
        "license": f"{SITE}/mentions-legales",
    }


def webpage_node(canonical, title, description, is_blog):
    node = {
        "@type": "WebPage",
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": title,
        "isPartOf": {"@id": WEBSITE_ID},
        "about": {"@id": CABINET_ID},
        "inLanguage": "fr-FR",
        "dateModified": LAST_MODIFIED,
        "publisher": {"@id": CABINET_ID},
        "reviewedBy": {"@id": PERSON_ID},
        "maintainer": {"@id": CABINET_ID},
        "speakable": {
            "@type": "SpeakableSpecification",
            "cssSelector": ["h1", "h2", ".geo-answer"],
        },
    }
    if description:
        node["description"] = description
    if is_blog:
        node["author"] = {"@id": PERSON_ID}
    return node


META_LLMS = '<link rel="alternate" type="text/markdown" href="/llms.txt" title="Version texte structurée pour les assistants IA">'
META_AUTHOR = '<link rel="author" href="https://ig-avocat.com/avocat-ilan-guedj">'


def get(pattern, text, group=1):
    m = re.search(pattern, text, re.S | re.I)
    return m.group(group).strip() if m else None


def process(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    src = open(path, encoding="utf-8").read()
    original = src

    canonical = get(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', src)
    if not canonical:
        print(f"  !! {rel}: pas de <link rel=canonical>, ignoré")
        return False
    title = get(r"<title>(.*?)</title>", src) or ""
    description = get(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', src) or ""
    is_blog = rel.startswith("blog/")

    graph = {
        "@context": "https://schema.org",
        "@graph": [
            website_node(),
            cabinet_node(),
            person_node(),
            webpage_node(canonical, title, description, is_blog),
        ],
    }
    payload = json.dumps(graph, ensure_ascii=False, indent=2)
    block = (
        f"    {START}\n"
        f'    <script type="application/ld+json">\n{payload}\n    </script>\n'
        f"    {END}\n"
    )

    # 1. Bloc @graph (idempotent)
    if START in src:
        src = re.sub(
            r"[ \t]*" + re.escape(START) + r".*?" + re.escape(END) + r"\n?",
            lambda _: block,
            src,
            flags=re.S,
        )
    else:
        src = src.replace("</head>", block + "</head>", 1)

    # 2. Rattacher les anciens noeuds LegalService au même @id (fusion d'entité)
    src = re.sub(
        r'("@type"\s*:\s*"LegalService"\s*,)(?!\s*\n?\s*"@id")',
        r'\1\n        "@id": "' + CABINET_ID + r'",',
        src,
    )

    # 3. Normaliser l'auteur des articles vers l'entité Personne canonique
    def _fix_author(m):
        body = m.group(0)
        if '"@id"' in body:
            return body
        return re.sub(
            r'"@type"\s*:\s*"(?:Person|Organization)"',
            '"@type": "Person",\n      "@id": "' + PERSON_ID + '"',
            body,
            count=1,
        )

    src = re.sub(
        r'"author"\s*:\s*\{[^{}]*"name"\s*:\s*"(?:Ma\u00eetre |Me )?Ilan Guedj"[^{}]*\}',
        _fix_author,
        src,
    )

    # 4. Découvrabilité de llms.txt + lien d'auteur
    if 'href="/llms.txt"' not in src:
        src = src.replace(
            '<link rel="canonical"',
            f"{META_LLMS}\n    {META_AUTHOR}\n    <link rel=\"canonical\"",
            1,
        )

    if src != original:
        open(path, "w", encoding="utf-8").write(src)
        return True
    return False


def main():
    check = "--check" in sys.argv
    files = sorted(
        [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
        + [
            os.path.join(ROOT, "blog", f)
            for f in os.listdir(os.path.join(ROOT, "blog"))
            if f.endswith(".html")
        ]
    )
    changed = 0
    for f in files:
        if check:
            src = open(f, encoding="utf-8").read()
            ok = START in src
            print(f"  {'OK ' if ok else 'MANQUANT'} {os.path.relpath(f, ROOT)}")
            continue
        if process(f):
            changed += 1
            print(f"  maj  {os.path.relpath(f, ROOT)}")
    if not check:
        print(f"\n{changed} fichier(s) mis à jour sur {len(files)} — date : {LAST_MODIFIED}")


if __name__ == "__main__":
    main()
