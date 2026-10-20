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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitedates import page_dates  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://ig-avocat.com"
PERSON_ID = f"{SITE}/#ilan-guedj"
PRACTICE_ID = f"{SITE}/#practice"
WEBSITE_ID = f"{SITE}/#website"
START = "<!-- GEO:ENTITY-GRAPH:START -->"
END = "<!-- GEO:ENTITY-GRAPH:END -->"
LEGACY = re.compile(r"<!-- GEO:ENTITY-GRAPH:START.*?GEO:ENTITY-GRAPH:END -->\n?", re.S)
# Directives d'extrait : sans limite de longueur, les moteurs (Google AI
# Overviews / AI Mode, Bing/Copilot) peuvent reprendre un passage complet.
ROBOTS_META = ('<meta name="robots" content="index, follow, max-snippet:-1, '
               'max-image-preview:large, max-video-preview:-1">')
FEED_LINK = ('<link rel="alternate" type="application/rss+xml" '
             'title="Guides de Maître Ilan Guedj — flux RSS" href="/feed.xml">')

PHONE = "+33663465984"
# Coordonnées BAN (api-adresse.data.gouv.fr) du 16 rue Breteuil, 13001 Marseille.
# Nominatim place le même numéro à quelques mètres, avec un code postal OSM erroné (13006).
GEO = {
    "@type": "GeoCoordinates",
    "latitude": 43.291994,
    "longitude": 5.375058,
}
# Serment prêté le 6 janvier 2023. Ne pas republier un foundingDate 1996.
FOUNDING_DATE = "2023-01-06"
ADDRESS = {
    "@type": "PostalAddress",
    "streetAddress": "16 rue Breteuil",
    "addressLocality": "Marseille",
    "postalCode": "13001",
    "addressRegion": "Provence-Alpes-Côte d'Azur",
    "addressCountry": "FR",
}
# Profil Google : lundi–jeudi 09:00–19:00, vendredi 09:00–17:00,
# samedi et dimanche fermés. 00:00–00:00 marque un jour fermé.
OPENING_HOURS = ["Mo-Th 09:00-19:00", "Fr 09:00-17:00"]
OPENING_HOURS_SPEC = [{
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday"],
    "opens": "09:00",
    "closes": "19:00",
}, {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": "Friday",
    "opens": "09:00",
    "closes": "17:00",
}, {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": "Saturday",
    "opens": "00:00",
    "closes": "00:00",
}, {
    "@type": "OpeningHoursSpecification",
    "dayOfWeek": "Sunday",
    "opens": "00:00",
    "closes": "00:00",
}]
OFFER_CATALOG = {
    "@type": "OfferCatalog",
    "name": "Services juridiques en dommage corporel",
    "itemListElement": [
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Indemnisation accident de la route"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Indemnisation accident de la vie (GAV)"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Indemnisation victime d'agression (CIVI/FGTI)"}},
        {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Recours pour erreur médicale (CCI/ONIAM)"}},
    ],
}
ENTITY_TYPES = {"LegalService", "LocalBusiness", "Attorney"}
LDJSON_SCRIPT = re.compile(
    r"[ \t]*<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>\s*(.*?)\s*</script>[ \t]*\n?",
    re.S | re.I,
)
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
    {"@type": "AdministrativeArea", "name": "Bouches-du-Rhône"},
    {"@type": "AdministrativeArea", "name": "Var"},
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
# Profils publics tenus par l'avocat lui-même (identité), en tête de sameAs.
PROFILES = ["https://www.linkedin.com/in/ilan-guedj/", "https://x.com/Guedj_"]
SAME_AS = PROFILES + [s["url"] for s in SOURCES]


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
        "telephone": PHONE,
        "email": "contact@ig-avocat.com",
        "knowsAbout": KNOWS,
        "knowsLanguage": [
            {"@type": "Language", "name": "Français", "alternateName": "fr"},
            {"@type": "Language", "name": "Anglais", "alternateName": "en"},
        ],
        "sameAs": SAME_AS,
        "subjectOf": SOURCES,
    }


def practice():
    return {
        # schema.org marque Attorney comme déprécié au profit de LegalService ;
        # l'ancien type reste déclaré en additionalType pour la continuité.
        "@type": "LegalService",
        "additionalType": "https://schema.org/Attorney",
        "@id": PRACTICE_ID,
        "name": "Maître Ilan Guedj — Avocat en dommage corporel",
        "alternateName": [
            "Maître Ilan GUEDJ - Avocat dommage corporel",
            "Cabinet Ilan Guedj",
            "Ilan Guedj Avocat",
        ],
        "url": f"{SITE}/",
        "founder": {"@id": PERSON_ID},
        "employee": [{"@id": PERSON_ID}],
        "telephone": PHONE,
        "email": "contact@ig-avocat.com",
        "image": f"{SITE}/img/og-cover.jpg",
        "logo": f"{SITE}/img/favicon.svg",
        "address": ADDRESS,
        "geo": GEO,
        "foundingDate": FOUNDING_DATE,
        "hasMap": MAP,
        "isicV4": "6910",
        "priceRange": "Consultation initiale gratuite — honoraires uniquement au résultat",
        "paymentAccepted": "Honoraires de résultat, aucune avance de frais",
        "currenciesAccepted": "EUR",
        "areaServed": AREAS,
        "knowsAbout": KNOWS,
        "knowsLanguage": ["fr-FR", "en"],
        "availableLanguage": ["fr", "en"],
        "memberOf": BARREAU,
        "publishingPrinciples": f"{SITE}/mentions-legales",
        "hasOfferCatalog": OFFER_CATALOG,
        # Horaires du profil Google : lun–jeu 9 h–19 h, vendredi 9 h–17 h,
        # samedi et dimanche fermés.
        "openingHours": OPENING_HOURS,
        "openingHoursSpecification": OPENING_HOURS_SPEC,
        "contactPoint": [{
            "@type": "ContactPoint",
            "contactType": "Prise de contact — victimes",
            "telephone": PHONE,
            "email": "contact@ig-avocat.com",
            "availableLanguage": ["fr", "en"],
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


def _types(node):
    t = node.get("@type")
    if isinstance(t, str):
        return {t}
    if isinstance(t, list):
        return set(t)
    return set()


def _entity_nodes(data):
    if not isinstance(data, dict):
        return []
    found = []
    if _types(data) & ENTITY_TYPES:
        found.append(data)
    for node in data.get("@graph") or []:
        if isinstance(node, dict) and _types(node) & ENTITY_TYPES:
            found.append(node)
    return found


def service_id(canonical):
    base = canonical.split("#")[0]
    if base.rstrip("/") == SITE:
        return f"{SITE}/#service"
    return base.rstrip("/") + "#service"


def _is_page_service(node):
    if not isinstance(node, dict) or "Service" not in _types(node):
        return False
    provider = node.get("provider")
    if isinstance(provider, dict) and provider.get("@id") == PRACTICE_ID:
        return True
    node_id = node.get("@id") or ""
    return node_id.endswith("#service") and node.get("serviceType")


def harvest_graph_services(src):
    """Reprend les Service de page déjà dans le graphe GEO.

    geo-inject remplace tout le bloc : sans cette reprise, un second passage
    effacerait le service propre à la page (le catalogue du cabinet, imbriqué
    sous hasOfferCatalog, n'est pas un service de page).
    """
    block = LEGACY.search(src)
    if not block:
        return []
    found = []
    for raw in LDJSON_SCRIPT.findall(block.group(0)):
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        for node in data.get("@graph") or []:
            if _is_page_service(node):
                found.append(node)
    return found


def strip_duplicate_entities(src, canonical):
    """Retire les blocs LegalService/LocalBusiness/Attorney hors graphe GEO.

    Un second nœud avec le même @id que le cabinet contredit le graphe.
    Le service propre à la page est conservé, rattaché au cabinet par @id.
    """
    services = harvest_graph_services(src)
    masked = []

    def mask(m):
        masked.append(m.group(0))
        return f"@@GEO{len(masked) - 1}@@"

    def repl(m):
        try:
            data = json.loads(m.group(1))
        except json.JSONDecodeError:
            return m.group(0)
        nodes = _entity_nodes(data)
        if not nodes:
            return m.group(0)
        for node in nodes:
            if not node.get("serviceType"):
                continue
            svc = {
                "@type": "Service",
                "@id": service_id(canonical),
                "name": node.get("name"),
                "serviceType": node["serviceType"],
                "provider": {"@id": PRACTICE_ID},
                "url": node.get("url") or canonical,
            }
            if node.get("description"):
                svc["description"] = node["description"]
            if node.get("areaServed"):
                svc["areaServed"] = node["areaServed"]
            if node.get("knowsAbout"):
                svc["knowsAbout"] = node["knowsAbout"]
            services.append(svc)
        return ""

    src = LEGACY.sub(mask, src)
    src = LDJSON_SCRIPT.sub(repl, src)
    src = re.sub(r"@@GEO(\d+)@@", lambda m: masked[int(m.group(1))], src)
    seen = set()
    unique = []
    for svc in services:
        key = svc.get("@id") or json.dumps(svc, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        unique.append(svc)
    return src, unique


def process(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
    src = open(path, encoding="utf-8").read()
    original = src
    canonical = get(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"', src)
    if not canonical:
        return False
    src, services = strip_duplicate_entities(src, canonical)
    published, modified = page_dates(path, src)
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
        "dateModified": modified,
    }
    description = get(r'<meta[^>]+name="description"[^>]+content="([^"]*)"', src)
    if description:
        page["description"] = description
    if rel.startswith("blog/"):
        page["author"] = {"@id": PERSON_ID}
        page["datePublished"] = published
    if services:
        page["mainEntity"] = {"@id": services[0]["@id"]}
        page["about"] = {"@id": services[0]["@id"]}
    if 'name="robots"' not in src:
        src = src.replace("</head>", ROBOTS_META + "\n</head>", 1)
    if 'type="application/rss+xml"' not in src:
        src = src.replace("</head>", FEED_LINK + "\n</head>", 1)
    graph = {"@context": "https://schema.org",
             "@graph": [website(), practice(), person(), page, *services]}
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
