#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Génère /lexique-dommage-corporel : le lexique du dommage corporel.

Pourquoi : les moteurs de réponse construisent leurs réponses à partir de
définitions courtes, autonomes et attribuées à un auteur identifié. Une page
« entité par entité » (DFP, DFT, consolidation, tierce personne…) est le format
le plus repris pour les requêtes « qu'est-ce que … ».

Source des définitions : content/geo/*.md (bloc `.geo-answer`, relu par
Maître Ilan Guedj) ou, pour quelques notions de cadrage, le texte ci-dessous.
La navigation et le pied de page sont repris de honoraires.html pour rester
alignés sur le reste du site.

Usage : python3 tools/build-lexique.py
"""
import html
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sitedates import ROOT  # noqa: E402

SITE = "https://ig-avocat.com"
URL = f"{SITE}/lexique-dommage-corporel"
OUT = os.path.join(ROOT, "lexique-dommage-corporel.html")
GEO = os.path.join(ROOT, "content", "geo")
PERSON = f"{SITE}/#ilan-guedj"

DINTILHAC = ("Rapport du groupe de travail chargé d'élaborer une nomenclature des "
             "préjudices corporels (rapport Dintilhac, 2005)",
             "https://www.vie-publique.fr/rapport/28092-rapport-du-groupe-de-travail-charge-delaborer-une-nomenclature-des-prej")
LEGI = "https://www.legifrance.gouv.fr/codes/article_lc/"

# (ancre, terme, fichier md ou None, définition manuelle ou None, sources, liens internes, sameAs)
SECTIONS = [
 ("Le cadre", [
  ("nomenclature-dintilhac", "Nomenclature Dintilhac", "nomenclature-dintilhac-definition.md", None,
   [DINTILHAC], [("blog/indemnisation-accident-corporel", "Comment calculer votre indemnisation")], []),
  ("loi-badinter", "Loi Badinter", None,
   "La loi n° 85-677 du 5 juillet 1985, dite loi Badinter, organise l'indemnisation des victimes "
   "d'accidents de la circulation dans lesquels est impliqué un véhicule terrestre à moteur. Les victimes "
   "non conductrices (piétons, cyclistes, passagers) sont indemnisées de leurs dommages corporels sans que "
   "leur faute puisse leur être opposée, sauf faute inexcusable ayant été la cause exclusive de l'accident "
   "(article 3) ; la faute du conducteur peut limiter ou exclure sa propre indemnisation (article 4). La loi "
   "impose aussi à l'assureur une procédure d'offre encadrée par des délais (articles L. 211-9 et suivants "
   "du code des assurances).",
   [("Loi n° 85-677 du 5 juillet 1985, article 3", "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006839422"),
    ("Loi n° 85-677 du 5 juillet 1985, article 4", "https://www.legifrance.gouv.fr/loda/article_lc/LEGIARTI000006839431")],
   [("accidents-route", "Accident de la circulation"), ("blog/faute-conducteur-victime-indemnisation", "Conducteur en faute : quelle indemnisation ?")],
   ["https://fr.wikipedia.org/wiki/Loi_Badinter", "https://www.wikidata.org/wiki/Q3258145"]),
  ("consolidation", "Consolidation", "consolidation-definition.md", None,
   [DINTILHAC], [("blog/preparer-expertise-medicale-accident-grave", "Préparer l'expertise médicale")], []),
 ]),
 ("Les postes de préjudice", [
  ("dft", "Déficit fonctionnel temporaire (DFT)", "dft-definition.md", None, [DINTILHAC],
   [("blog/indemnisation-accident-corporel", "Les postes de préjudice temporaires")], []),
  ("dfp", "Déficit fonctionnel permanent (DFP)", "dfp-definition.md", None, [DINTILHAC],
   [("blog/deficit-fonctionnel-permanent-dfp", "DFP : comment est-il indemnisé ?"), ("blog/indemnisation-accident-grave", "Indemnisation d'un accident grave")], []),
  ("souffrances-endurees", "Souffrances endurées (pretium doloris)", None,
   "Les souffrances endurées désignent les souffrances physiques et psychiques subies par la victime "
   "entre l'accident et la consolidation : douleurs liées aux lésions, aux interventions, aux soins et "
   "à la rééducation, ainsi que le retentissement psychologique de cette période. L'expert les cote "
   "habituellement sur une échelle de 1 à 7 ; cette cotation n'est pas un montant et doit être justifiée "
   "par les éléments du dossier (hospitalisations, opérations, traitements). Après consolidation, les "
   "douleurs permanentes relèvent du déficit fonctionnel permanent.",
   [DINTILHAC], [("blog/souffrances-endurees", "Souffrances endurées : la cotation sur 7"), ("blog/indemnisation-accident-corporel", "Les postes de préjudice")], []),
  ("prejudice-esthetique", "Préjudice esthétique", "prejudice-esthetique-definition.md", None, [DINTILHAC], [], []),
  ("prejudice-agrement", "Préjudice d'agrément", "prejudice-agrement-definition.md", None, [DINTILHAC], [], []),
  ("prejudice-sexuel", "Préjudice sexuel", "prejudice-sexuel-definition.md", None, [DINTILHAC], [], []),
  ("prejudice-etablissement", "Préjudice d'établissement", "prejudice-etablissement-definition.md", None, [DINTILHAC], [], []),
  ("tierce-personne", "Assistance par tierce personne", "03-tierce-personne.md", None, [DINTILHAC],
   [("blog/tierce-personne-indemnisation", "Tierce personne : comment l'aide humaine est indemnisée"), ("blog/indemnisation-accident-grave", "Tierce personne et accident grave")], []),
  ("pgpa", "Pertes de gains professionnels actuels (PGPA)", "pertes-gains-professionnels-actuels.md", None, [DINTILHAC], [], []),
  ("pgpf", "Pertes de gains professionnels futurs (PGPF)", "pertes-gains-professionnels-futurs.md", None, [DINTILHAC], [("blog/capitalisation-prejudice-euro-de-rente", "Capitaliser un préjudice futur : l'euro de rente")], []),
  ("incidence-professionnelle", "Incidence professionnelle", "incidence-professionnelle-definition.md", None, [DINTILHAC], [("blog/incidence-professionnelle", "Incidence professionnelle : ce qu'elle indemnise")], []),
  ("prejudice-scolaire", "Préjudice scolaire, universitaire ou de formation", "prejudice-scolaire-universitaire-formation.md", None, [DINTILHAC], [], []),
  ("logement-adapte", "Frais de logement adapté", "frais-logement-adapte-indemnisation.md", None, [DINTILHAC], [], []),
  ("vehicule-adapte", "Frais de véhicule adapté", "vehicule-adapte-indemnisation.md", None, [DINTILHAC], [], []),
  ("prejudice-affection", "Préjudice d'affection", "prejudice-affection-definition.md", None, [DINTILHAC],
   [("blog/deces-accident-indemnisation-proches", "Décès d'un proche : les droits de la famille")], []),
 ]),
 ("L'expertise médicale", [
  ("expertise-medicale", "Expertise médicale", "05-expertise-medicale.md", None,
   [("Code des assurances, article L. 211-10", LEGI + "LEGIARTI000006795457")],
   [("blog/preparer-expertise-medicale-accident-grave", "Préparer l'expertise après un accident grave"),
    ("blog/expertise-medicale-judiciaire", "L'expertise médicale judiciaire")], []),
  ("medecin-recours", "Médecin-recours (médecin-conseil de victime)", "medecin-recours-role.md", None,
   [("Code des assurances, article L. 211-10", LEGI + "LEGIARTI000006795457")],
   [("blog/medecin-recours-victime", "Le médecin-recours, allié de la victime")], []),
  ("expertise-amiable-judiciaire", "Expertise amiable et expertise judiciaire", "expertise-judiciaire-ou-amiable.md", None,
   [("Code de procédure civile, articles 263 à 284-1 (l'expertise)", "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070716/LEGISCTA000006165192/")],
   [("blog/expertise-medicale-judiciaire", "Pourquoi demander une expertise judiciaire")], []),
 ]),
 ("Procédures, organismes et régimes", [
  ("offre-assureur", "Offre d'indemnisation de l'assureur", "04-offre-assureur.md", None,
   [("Code des assurances, article L. 211-9", LEGI + "LEGIARTI000006795447")],
   [("blog/refuser-offre-assurance-accident", "Refuser l'offre de l'assurance")], []),
  ("provision", "Provision", "provision-indemnisation-accident.md", None,
   [("Code des assurances, article L. 211-9", LEGI + "LEGIARTI000006795447")], [], []),
  ("fgao", "FGAO (Fonds de garantie des assurances obligatoires de dommages)", "fonds-garantie-conducteur-non-assure.md", None,
   [("Code des assurances, article L. 421-1", LEGI + "LEGIARTI000033460248"),
    ("Site du FGAO", "https://www.fondsdegarantie.fr/")],
   [("accidents-route", "Accident de la circulation")], []),
  ("civi", "CIVI (Commission d'indemnisation des victimes d'infractions)", "07-civi.md", None,
   [("Code de procédure pénale, article 706-3", LEGI + "LEGIARTI000038312693"),
    ("Code de procédure pénale, article 706-5", LEGI + "LEGIARTI000048442334")],
   [("agression", "Victime d'agression"), ("blog/agression-victime-droits-recours", "Agression : droits et recours")], []),
  ("fgti", "FGTI (Fonds de garantie des victimes)", None,
   "Le Fonds de garantie des victimes des actes de terrorisme et d'autres infractions (FGTI) est "
   "l'organisme qui verse l'indemnité accordée par la CIVI, puis se retourne contre l'auteur de "
   "l'infraction. Il indemnise donc la victime même lorsque l'auteur est inconnu, insolvable ou n'a pas "
   "été condamné. Pour les infractions ne relevant pas de la CIVI, il gère aussi le service d'aide au "
   "recouvrement (SARVI), qui avance à la victime tout ou partie des dommages-intérêts alloués par la "
   "juridiction pénale.",
   [("Site du FGTI", "https://www.fondsdegarantie.fr/"),
    ("Code de procédure pénale, article 706-15-1 (SARVI)", LEGI + "LEGIARTI000038313645")],
   [("agression", "Victime d'agression")], []),
  ("cci-oniam", "CCI et ONIAM", "cci-oniam-difference.md", None,
   [("Code de la santé publique, article L. 1142-1", LEGI + "LEGIARTI000020628252"),
    ("Site de l'ONIAM", "https://www.oniam.fr/")],
   [("erreur-medicale", "Erreur médicale"), ("blog/erreur-medicale-droits-victime", "Erreur médicale : vos droits")], []),
  ("alea-therapeutique", "Aléa thérapeutique", "alea-therapeutique-indemnisation-oniam.md", None,
   [("Code de la santé publique, article L. 1142-1", LEGI + "LEGIARTI000020628252"),
    ("Code de la santé publique, article D. 1142-1", LEGI + "LEGIARTI000023458773")],
   [("erreur-medicale", "Erreur médicale")], []),
  ("infection-nosocomiale", "Infection nosocomiale", "08-infection-nosocomiale.md", None,
   [("Code de la santé publique, article L. 1142-1", LEGI + "LEGIARTI000020628252"),
    ("Code de la santé publique, article L. 1142-1-1", LEGI + "LEGIARTI000020628248")],
   [("erreur-medicale", "Erreur médicale"),
    ("blog/infection-nosocomiale-indemnisation", "Infection nosocomiale : qui indemnise ?")], []),
  ("gav", "Garantie des accidents de la vie (GAV)", None,
   "La garantie des accidents de la vie (GAV) est un contrat d'assurance facultatif qui indemnise "
   "l'assuré des dommages corporels subis lors d'un accident de la vie privée (accident domestique, de "
   "sport, de loisir, de bricolage, accident médical, agression, catastrophe naturelle), y compris "
   "lorsqu'aucun tiers n'est responsable. L'indemnisation obéit aux conditions du contrat : seuil de "
   "gravité, plafond, exclusions et évaluation par le médecin de l'assureur, que la victime peut discuter "
   "avec l'aide d'un médecin-recours et d'un avocat.",
   [("La finance pour tous (IEFP), la garantie des accidents de la vie", "https://www.lafinancepourtous.com/pratique/assurance/assurances-famille-loisirs/la-garantie-des-accidents-de-la-vie/")],
   [("accidents-vie", "Accidents de la vie")], ["https://fr.wikipedia.org/wiki/Garantie_des_accidents_de_la_vie"]),
  ("faute-inexcusable", "Faute inexcusable de l'employeur", "faute-inexcusable-employeur.md", None,
   [("Code de la sécurité sociale, articles L. 452-1 à L. 452-5", "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006073189/LEGISCTA000006156141/")],
   [("blog/accident-travail-faute-inexcusable", "Accident du travail et faute inexcusable")], []),
 ]),
]


def md_definition(name):
    src = open(os.path.join(GEO, name), encoding="utf-8").read()
    m = re.search(r'<div class="geo-answer">(.*?)</div>', src, re.S)
    assert m, name
    return re.sub(r"\s+", " ", m.group(1)).strip()


def chrome():
    """Navigation et pied de page repris de honoraires.html (chemins racine)."""
    src = open(os.path.join(ROOT, "honoraires.html"), encoding="utf-8").read()
    nav = src[src.index("<body"):src.index("</nav>") + len("</nav>")]
    foot = src[src.index("<footer"):src.index("</body>")]
    return nav, foot


def build():
    terms = []
    for section, items in SECTIONS:
        for anchor, term, md, manual, sources, links, same in items:
            definition = manual or md_definition(md)
            terms.append((section, anchor, term, definition, sources, links, same))

    graph_terms = []
    for _, anchor, term, definition, sources, links, same in terms:
        node = {"@type": "DefinedTerm", "@id": f"{URL}#{anchor}", "name": term,
                "description": definition, "url": f"{URL}#{anchor}",
                "inDefinedTermSet": {"@id": f"{URL}#lexique"}, "inLanguage": "fr-FR"}
        if same:
            node["sameAs"] = same
        graph_terms.append(node)
    graph = {"@context": "https://schema.org", "@graph": [
        {"@type": "DefinedTermSet", "@id": f"{URL}#lexique",
         "name": "Lexique du dommage corporel",
         "description": "Définitions des notions clés de l'indemnisation des victimes de dommage corporel "
                        "(nomenclature Dintilhac, DFP, DFT, consolidation, tierce personne, CIVI, ONIAM…), "
                        "rédigées par Maître Ilan Guedj, avocat au barreau de Marseille.",
         "url": URL, "inLanguage": "fr-FR",
         "author": {"@id": PERSON}, "publisher": {"@id": PERSON},
         "hasDefinedTerm": [{"@id": t["@id"]} for t in graph_terms],
         "citation": [{"@type": "CreativeWork", "name": DINTILHAC[0], "url": DINTILHAC[1]}]},
        *graph_terms,
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Lexique du dommage corporel", "item": URL}]},
    ]}

    description = ("Lexique du dommage corporel : DFP, DFT, consolidation, souffrances endurées, tierce "
                   "personne, CIVI, ONIAM, loi Badinter. Définitions sourcées.")
    nav, foot = chrome()
    E = html.escape

    body = []
    body.append(f'''
    <section class="relative pt-40 pb-16 bg-gradient-to-b from-gray-50 to-sand">
        <div class="max-w-4xl mx-auto px-6 lg:px-8">
            <nav aria-label="Fil d'Ariane" class="text-sm text-gray-500 mb-6">
                <a href="/" class="hover:text-gray-900">Accueil</a> <span aria-hidden="true">›</span> <span>Lexique du dommage corporel</span>
            </nav>
            <h1 class="text-4xl md:text-6xl font-black tracking-tighter leading-[1.05] mb-6 text-balance">Lexique du dommage corporel</h1>
            <p class="text-xl text-gray-600 leading-relaxed max-w-3xl">Les notions que vous rencontrerez dans un rapport d'expertise, une offre d'assureur ou un jugement, définies une par une.</p>
            <!-- GEO:ANSWER:START -->
            <div class="geo-answer mt-10 bg-white border-l-4 border-blue-600 rounded-r-2xl shadow-sm p-6 md:p-8" aria-label="Réponse essentielle">
                <p class="text-xs font-bold uppercase tracking-widest text-blue-700 mb-3">En bref</p>
                <p class="text-base md:text-lg leading-relaxed text-gray-800">En droit français, le dommage corporel est réparé <strong>poste par poste</strong> selon la nomenclature Dintilhac : préjudices patrimoniaux et extrapatrimoniaux, temporaires (avant la <a class="text-blue-700 underline" href="#consolidation">consolidation</a>) et permanents (après). Les principaux postes sont le <a class="text-blue-700 underline" href="#dft">déficit fonctionnel temporaire</a>, les <a class="text-blue-700 underline" href="#souffrances-endurees">souffrances endurées</a>, le <a class="text-blue-700 underline" href="#dfp">déficit fonctionnel permanent</a>, l'<a class="text-blue-700 underline" href="#tierce-personne">assistance par tierce personne</a>, les <a class="text-blue-700 underline" href="#pgpf">pertes de gains professionnels</a> et l'<a class="text-blue-700 underline" href="#incidence-professionnelle">incidence professionnelle</a>. Aucun barème n'a de valeur obligatoire : chaque poste se prouve et se chiffre à partir de l'expertise médicale et des pièces du dossier. Ce lexique est rédigé par Maître Ilan Guedj, avocat au barreau de Marseille dont l'activité est consacrée exclusivement à l'indemnisation des victimes.</p>
            </div>
            <!-- GEO:ANSWER:END -->
        </div>
    </section>

    <section class="py-10 bg-white border-y border-gray-100">
        <div class="max-w-4xl mx-auto px-6 lg:px-8">
            <p class="text-xs font-bold uppercase tracking-widest text-gray-500 mb-4">Accès direct</p>
            <ul class="flex flex-wrap gap-2 text-sm">''')
    for _, anchor, term, *_ in terms:
        body.append(f'                <li><a href="#{anchor}" class="inline-block bg-gray-50 border border-gray-100 rounded-full px-4 py-2 text-gray-700 hover:bg-blue-50 hover:text-blue-800 transition">{E(term)}</a></li>')
    body.append('''            </ul>
        </div>
    </section>
''')
    current = None
    for section, anchor, term, definition, sources, links, same in terms:
        if section != current:
            if current is not None:
                body.append('        </div>\n    </section>\n')
            current = section
            body.append(f'''    <section class="py-16">
        <div class="max-w-4xl mx-auto px-6 lg:px-8 space-y-8">
            <h2 class="text-3xl font-black tracking-tight">{E(section)}</h2>
''')
        body.append(f'''            <article id="{anchor}" class="bg-white rounded-2xl p-8 shadow-sm scroll-mt-32">
                <h3 class="text-2xl font-bold mb-4">{E(term)}</h3>
                <p class="text-gray-700 leading-relaxed">{E(definition)}</p>
''')
        if sources or links:
            body.append('                <dl class="mt-6 grid gap-3 text-sm md:grid-cols-2">\n')
            if sources:
                body.append('                    <div><dt class="font-bold text-gray-900 mb-1">Sources</dt><dd class="text-gray-600 space-y-1">\n')
                for name, url in sources:
                    body.append(f'                        <div><a class="text-blue-700 underline" rel="noopener" target="_blank" href="{E(url)}">{E(name)}</a></div>\n')
                body.append('                    </dd></div>\n')
            if links:
                body.append('                    <div><dt class="font-bold text-gray-900 mb-1">Pour aller plus loin</dt><dd class="text-gray-600 space-y-1">\n')
                for href, name in links:
                    body.append(f'                        <div><a class="text-blue-700 underline" href="{E(href)}">{E(name)}</a></div>\n')
                body.append('                    </dd></div>\n')
            body.append('                </dl>\n')
        body.append('            </article>\n')
    body.append('        </div>\n    </section>\n')

    body.append('''    <section class="py-16 bg-white border-t border-gray-100">
        <div class="max-w-4xl mx-auto px-6 lg:px-8">
            <p class="text-gray-600 leading-relaxed">Lexique rédigé et tenu à jour par <a class="text-blue-700 underline" rel="author" href="avocat-ilan-guedj">Maître Ilan Guedj</a>, avocat au barreau de Marseille. Information générale : la qualification et le chiffrage de chaque poste dépendent des pièces de votre dossier. <a class="text-blue-700 underline" href="contact">Première consultation gratuite</a>, aucune avance de frais.</p>
        </div>
    </section>
''')

    head = f'''<!DOCTYPE html>
<html lang="fr" class="scroll-smooth bg-sand">
<head>
    <!-- Google Tag Manager -->
    <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
    new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    }})(window,document,'script','dataLayer','GTM-WP82S37T');</script>
    <!-- End Google Tag Manager -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="{E(description)}">
    <title>Lexique du dommage corporel : définitions | Ilan Guedj</title>
    <link rel="alternate" type="text/markdown" href="/llms.txt" title="Version texte structurée pour les assistants IA">
    <link rel="author" href="{SITE}/avocat-ilan-guedj">
    <link rel="canonical" href="{URL}">
    <meta property="og:title" content="Lexique du dommage corporel | Maître Ilan Guedj">
    <meta property="og:description" content="{E(description)}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{URL}">
    <meta property="og:image" content="{SITE}/img/og-cover.jpg">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">
    <meta property="og:image:alt" content="Maître Ilan Guedj — Avocat dommage corporel à Marseille">
    <meta property="og:locale" content="fr_FR">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Lexique du dommage corporel | Maître Ilan Guedj">
    <meta name="twitter:description" content="{E(description)}">
    <meta name="twitter:image" content="{SITE}/img/og-cover.jpg">
    <link rel="icon" type="image/svg+xml" href="img/favicon.svg">
    <link rel="stylesheet" href="css/tailwind.css">
    <link rel="preload" href="fonts/fraunces-latin.woff2" as="font" type="font/woff2" crossorigin>
    <link rel="preload" href="fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
    <style>
        .glass {{
            background-color: rgba(255, 255, 255, 0.9);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        }}
    </style>
    <!-- Lexique : DefinedTermSet -->
    <script type="application/ld+json">
{json.dumps(graph, ensure_ascii=False, indent=2)}
</script>
</head>
'''
    page = head + nav + "\n<main>\n" + "".join(body) + "</main>\n\n    " + foot + "</body>\n</html>\n"
    # Les blocs injectés par la chaîne de build (graphe d'entités, meta robots,
    # flux) sont réappliqués par geo-inject.py après cette génération.
    open(OUT, "w", encoding="utf-8").write(page)
    print(f"lexique-dommage-corporel.html écrit — {len(terms)} définitions")


if __name__ == "__main__":
    build()
