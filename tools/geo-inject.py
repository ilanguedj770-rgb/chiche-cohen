#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injecte le graphe schema.org du site, centré sur la seule entité Maître Ilan Guedj.

Le graphe décrit trois nœuds stables (site, cabinet, avocat) plus le nœud de la
page courante. Aucune structure collective ni indicateur chiffré d'activité n'y
figure : l'entité éditoriale du site est l'avocat.
"""
import json
import os
import re
import sys
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ig-avocat.com"
PERSON_ID = f"{SITE}/#ilan-guedj"
PRACTICE_ID = f"{SITE}/#practice"
WEBSITE_ID = f"{SITE}/#website"
START = "<!-- GEO:ENTITY-GRAPH:START -->"
END = "<!-- GEO:ENTITY-GRAPH:END -->"
LEGACY = re.compile(r"<!-- GEO:ENTITY-GRAPH:START.*?GEO:ENTITY-GRAPH:END -->\n?", re.S)
LAST_MODIFIED = os.environ.get("GEO_DATE", date.today().isoformat())

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
MAP = ("https://www.google.com/maps/search/?api=1"
       "&query=16+Rue+Breteuil+13001+Marseille")
KNOWS = [
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
AREAS = [
    {"@type": "City", "name": c} for c in
    ["Marseille", "Aix-en-Provence", "Toulon", "Nice", "Avignon",
     "Montpellier", "Nîmes", "Cannes"]
] + [
    {"@type": "AdministrativeArea", "name": "Provence-Alpes-Côte d'Azur"},
    {"@type": "AdministrativeArea", "name": "Occitanie"},
    {"@type": "Country", "name": "France"},
]
# Sources publiques attachées à l'avocat lui-même, vérifiables par des tiers.
SOURCES = [
    {"@type": "WebPage",
     "name": "Profil de Maître Ilan Guedj sur l'annuaire officiel des avocats (avocat.fr)",
     "url": "https://consultation.avocat.fr/avocat-marseille/ilan-guedj-53358.html"},
    {"@type": "WebPage",
     "name": "Fiche Cabinet Ilan Guedj sur Predictice",
     "url": "https://predictice.com/cabinet/cabinet-ilan-guedj-922092382"},
]
SAME_AS = [s["url"] for s in SOURCES]


def person():
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
            "Maître Ilan Guedj est avocat au barreau de Marseille (16 rue Breteuil, "
            "13001 Marseille). Son activité est consacrée exclusivement au droit du "
            "dommage corporel : indemnisation des victimes d'accidents de la circulation "
            "(loi Badinter), d'erreurs médicales (CCI, ONIAM), d'agressions (CIVI, FGTI) "
            "et d'accidents de la vie. Il n'intervient jamais pour une compagnie "
            "d'assurance. Consultation initiale gratuite, aucune avance de frais, "
            "honoraires uniquement au résultat."
        ),
        "url": f"{SITE}/avocat-ilan-guedj",
        "mainEntityOfPage": {"@id": f"{SITE}/avocat-ilan-guedj#webpage"},
        "image": {
            "@type": "ImageObject",
            "url": f"{SITE}/img/associe-guedj.jpg",
            "caption": "Maître Ilan Guedj, avocat en dommage corporel à Marseille",
        },
        "worksFor": {"@id": PRACTICE_ID},
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
        "knowsAbout": KNOWS,
        "knowsLanguage": [
            {"@type": "Language", "name": "Français", "alternateName": "fr"},
            {"@type": "Language", "name": "Anglais", "alternateName": "en"},
            {"@type": "Language", "name": "Hébreu", "alternateName": "he"},
        ],
        "sameAs": SAME_AS,
        "subjectOf": SOURCES,
    }


def practice():
    return {
        "@type": ["Attorney", "LegalService"],
        "@id": PRACTICE_ID,
        "name": "Maître Ilan Guedj — Avocat en dommage corporel",
        "alternateName": ["Cabinet Ilan Guedj", "Ilan Guedj Avocat"],
        "url": f"{SITE}/",
        "founder": {"@id": PERSON_ID},
        "employee": [{"@id": PERSON_ID}],
        "telephone": "+33663465984",
        "email": "contact@ig-avocat.com",
        "address": ADDRESS,
        "hasMap": MAP,
        "isicV4": "6910",
        "priceRange": "Consultation initiale gratuite — honoraires uniquement au résultat",
        "paymentAccepted": "Honoraires de résultat, aucune avance de frais",
        "currenciesAccepted": "EUR",
        "areaServed": AREAS,
        "knowsAbout": KNOWS,
        "knowsLanguage": ["fr-FR", "en", "he"],
        "availableLanguage": ["fr", "en", "he"],
        "memberOf": BARREAU,
        "publishingPrinciples": f"{SITE}/mentions-legales",
        "openingHoursSpecification": [{
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
            "opens": "09:00",
            "closes": "19:00",
        }],
        "contactPoint": [{
            "@type": "ContactPoint",
            "contactType": "Prise de contact — victimes",
            "telephone": "+33663465984",
            "email": "contact@ig-avocat.com",
            "availableLanguage": ["fr", "en", "he"],
            "areaServed": "FR",
            "url": f"{SITE}/contact",
        }],
    }


def website():
    return {
        "@type": "WebSite",
        "@id": WEBSITE_ID,
        "url": f"{SITE}/",
        "name": "Maître Ilan Guedj — Avocat dommage corporel Marseille",
        "inLanguage": "fr-FR",
        "publisher": {"@id": PERSON_ID},
        "about": {"@id": PERSON_ID},
        "copyrightHolder": {"@id": PERSON_ID},
        "license": f"{SITE}/mentions-legales",
    }


def get(pattern, text):
    m = re.search(pattern, text, re.S | re.I)
    return m.group(1).strip() if m else ""


def process(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    src = open(path, encoding="utf-8").read()
    original = src
    canonical = get(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', src)
    if not canonical:
        return False
    page = {
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": get(r"<title>(.*?)</title>", src),
        "isPartOf": {"@id": WEBSITE_ID},
        "about": {"@id": PERSON_ID},
        "publisher": {"@id": PERSON_ID},
        "reviewedBy": {"@id": PERSON_ID},
        "inLanguage": "fr-FR",
        "dateModified": LAST_MODIFIED,
    }
    if rel.startswith("blog/"):
        page["author"] = {"@id": PERSON_ID}
    graph = {"@context": "https://schema.org",
             "@graph": [website(), practice(), person(), page]}
    block = (f"{START}\n<script type=\"application/ld+json\">\n"
             f"{json.dumps(graph, ensure_ascii=False, indent=2)}\n</script>\n{END}\n")
    if LEGACY.search(src):
        src = LEGACY.sub(lambda _: block, src)
    else:
        src = src.replace("</head>", block + "</head>", 1)
    if src != original:
        open(path, "w", encoding="utf-8").write(src)
        return True
    return False


def main():
    files = [os.path.join(ROOT, f) for f in os.listdir(ROOT) if f.endswith(".html")]
    blog = os.path.join(ROOT, "blog")
    if os.path.isdir(blog):
        files += [os.path.join(blog, f) for f in os.listdir(blog) if f.endswith(".html")]
    if "--check" in sys.argv:
        bad = [os.path.relpath(f, ROOT) for f in files
               if re.search(r"Chiche\s+Cohen|CHICHE\s+COHEN",
                            open(f, encoding="utf-8").read(), re.I)]
        print("Références legacy restantes:", len(bad))
        for x in bad:
            print(" -", x)
        return 1 if bad else 0
    print("Pages GEO mises à jour:", sum(process(f) for f in files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
