# ig-avocat.com — carte SEO
<!-- Pour les humains : créé le 2026-11-02. Rester sous 200 lignes. Les procédures vont dans .claude/skills/, les règles par type de fichier dans .claude/rules/, les décisions dans seo/decisions.md. -->

## Objectif permanent
Être l'avocat en dommage corporel le mieux référencé de PACA, sur Google comme dans les moteurs de réponse IA (ChatGPT, Perplexity, Gemini, Claude, Le Chat, Copilot). Objectif d'acquisition : plus de 50 nouveaux dossiers par mois.

## Le site
- Avocat : Maître Ilan Guedj, barreau de Marseille. Défend uniquement des victimes, jamais une compagnie d'assurance.
- Lecteur : victime (ou proche) d'un accident de la route, d'une erreur médicale, d'une agression ou d'un accident de la vie, en PACA et Occitanie, souvent sur mobile, sans culture juridique.
- Promesse : première consultation gratuite, aucune avance de frais, rémunération au résultat.
- Site statique HTML. Dépôt GitHub `main` → déploiement Netlify automatique.

## Données de référence (NAP) — à reprendre à l'identique
- Maître Ilan Guedj, avocat au barreau de Marseille — 16 rue Breteuil, 13001 Marseille (jamais 13006)
- 06 63 46 59 84 — contact@ig-avocat.com — https://ig-avocat.com
- Horaires : 9h-19h du lundi au jeudi, 9h-17h le vendredi. Langues : français et anglais (pas l'hébreu).
- Zone : Marseille, Aix-en-Provence, Toulon, Nice, Avignon, Nîmes, Montpellier, toute la France.

## Pages d'argent — ne JAMAIS changer leur URL
`/`, `/accidents-route`, `/erreur-medicale`, `/agression`, `/accidents-vie`, `/accident-moto-marseille`, `/pieton-cycliste-marseille`, `/avocat-dommage-corporel-bouches-du-rhone`, `/avocat-aix-en-provence`, `/avocat-toulon`, `/avocat-nice`, `/avocat-avignon`, `/avocat-nimes`, `/avocat-montpellier`, `/honoraires`, `/contact`, `/avocat-ilan-guedj`.
Fiche par page (requête cible, cluster, état) : `seo/pages/`.

## Déontologie (contrôlée aussi par le hook .claude/hooks/protect.mjs)
- Jamais « spécialiste » ni « spécialisé » pour l'avocat : dire « activité exclusivement consacrée au dommage corporel ».
- Jamais « le meilleur », « n°1 », « leader », ni promesse de résultat.
- Jamais d'avis client rédigé ou inventé ; jamais d'élément de dossier dans une réponse à un avis.
- Pas de contenu sur la faute inexcusable de l'employeur au-delà de la page existante.

## Où vivent les choses
- `seo/strategy/now.md` : priorités du trimestre (importé ci-dessous)
- `seo/keywords/` : un cluster par fichier, avec sa page pivot
- `seo/pages/` : une fiche par page d'argent
- `seo/decisions.md` : chaque décision SEO, datée, avec sa raison
- `seo/reports/` : revues mensuelles (le 15) ; `seo/briefs/` : briefs en cours
- `content/geo/` : 52 réponses juridiques sourcées — à assembler en pages pivots, jamais publiées en masse
- `SOURCES-JURIDIQUES-VERIFIEES.md` : liens Légifrance vérifiés
- `GEO-EDITORIAL-STANDARD.md`, `GEO-PUBLISHING.md`, `CHARTE.md` : standards éditoriaux, publication, charte visuelle

## Fichiers générés — ne pas éditer à la main
Navigation et pied de page de toutes les pages : `tools/layout.py` (gabarits uniques, marqueurs LAYOUT:NAV / LAYOUT:FOOTER) — modifier le script, pas les pages.
Bloc commun du `<head>` (marqueurs LAYOUT:HEAD), repère `<main id="contenu">` : aussi `tools/layout.py`.
Interface commune (menu Domaines, recherche, sommaire et progression des guides, partage, calculateur d'échéances) : `js/ig-ui.js`, styles `.ig-*` dans `css/input.css` — le menu et la recherche sont rendus côté navigateur pour ne pas modifier le texte des pages.
`search-index.json` (tools/build-search.py, lancé par geo-build), `sitemap.xml` (tools/build-sitemap.py), `feed.xml`, `llms-full.txt`, `css/tailwind.css` (npm run build:css), `lexique-dommage-corporel.html` (tools/build-lexique.py), données d'entité JSON-LD (tools/geo-inject.py).

## Avant tout push
1. `python3 tools/geo-audit.py` → 0 erreur exigée
2. `python3 tools/check-internal-links.py` → OK
3. Si nouvelles classes Tailwind : `npm run build:css` et aligner sur la sortie Linux (piège Windows connu)
Sous Windows : `py` au lieu de `python3`, et `PYTHONUTF8=1`.

## Comment répondre
- Données avant opinions : Search Console (propriété `sc-domain:ig-avocat.com`) avant tout avis sur une page. Ne jamais deviner un volume ou une position.
- Citer le fichier utilisé. Si aucun fichier ne couvre le point, le dire.
- Une page = une intention = une requête cible. Vérifier `seo/keywords/` avant de créer une page (pas de doublon, ex. délais → `/blog/delai-prescription-accident-corporel`).
- Consigner chaque modification de page indexable dans `seo/decisions.md`.

## Toujours en tête
- Ce trimestre : @seo/strategy/now.md
