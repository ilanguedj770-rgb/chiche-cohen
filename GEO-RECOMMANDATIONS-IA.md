# Référencement dans les recommandations IA (GEO) — ig-avocat.com

> **Note de mise à jour (août 2026).** Le site a été harmonisé autour d'une entité
> unique, Maître Ilan Guedj. Les recommandations de ce document qui portent sur
> l'identité collective du cabinet (dénomination Chiche Cohen, associés, effectif,
> volumes d'activité, décisions Doctrine, page « Notre bilan ») sont caduques et ne
> doivent plus être appliquées. Le reste du document reste valable.

> GEO = *Generative Engine Optimization* : être lu, compris et **cité** par ChatGPT,
> Claude, Perplexity, Google AI Overviews / AI Mode, Copilot, Le Chat, Apple Intelligence
> quand quelqu'un demande « quel avocat en dommage corporel à Marseille ? ».
>
> Dernière mise à jour : 15 septembre 2026 (voir la section 5, qui prime sur le reste en cas de contradiction).

Un moteur de réponse ne « classe » pas des pages : il construit une **entité** (une fiche
mentale sur vous), la corrobore avec des **sources tierces**, puis reprend des **passages
directement citables**. Les trois chantiers ci-dessous suivent exactement cette logique.

---

## 1. Ce qui a été fait sur le site

### 1.1 Une seule entité, identifiée partout de la même façon

Auparavant, chaque page déclarait son propre bloc `LegalService` anonyme, sans identifiant
stable et sans jamais décrire **la personne** « Maître Ilan Guedj ». Un moteur y voyait
28 cabinets anonymes plutôt qu'un cabinet et un avocat.

Un **graphe d'entités canonique** (`@graph` schema.org) est désormais injecté sur les
30 pages, avec des identifiants stables :

| Identifiant | Type | Rôle |
|---|---|---|
| `https://ig-avocat.com/#cabinet` | `Attorney` + `LegalService` | le cabinet |
| `https://ig-avocat.com/#ilan-guedj` | `Person` | l'avocat |
| `https://ig-avocat.com/#website` | `WebSite` | le site |
| `<url de la page>#webpage` | `WebPage` | la page courante, datée |

Conséquences concrètes :

- les anciens blocs `LegalService` de chaque page reçoivent le même `@id` : ils
  **fusionnent** avec l'entité cabinet au lieu de la dupliquer ;
- l'entité `Person` porte le métier, le barreau, les langues, les 30+ sujets de compétence
  (`knowsAbout`), l'adresse et les profils publics ;
- cabinet et personne sont reliés (`employee`, `worksFor`, `member`, `affiliation`) ;
- les **13 articles du blog** ont un auteur normalisé pointant vers `#ilan-guedj`
  (3 d'entre eux déclaraient jusqu'ici une `Organization` comme auteur — signal E-E-A-T
  perdu) ;
- chaque page déclare une `dateModified` et un bloc `speakable`.

### 1.2 Une page d'identité : `/avocat-ilan-guedj`

C'est la page qu'un assistant IA va chercher quand on lui demande « qui est cet avocat ? ».
Elle n'existait pas. Elle contient :

- un résumé « En bref » **rédigé pour être cité tel quel** (classe `.geo-answer`) ;
- un **tableau de faits vérifiables**, chaque ligne adossée à une source publique
  extérieure au cabinet (Doctrine.fr, annuaire officiel des avocats, Predictice, Google Maps) ;
- les quatre domaines, la méthode de travail, les honoraires ;
- 7 questions/réponses en `FAQPage`, formulées comme des requêtes réelles ;
- un schéma `ProfilePage` dont l'entité principale est `#ilan-guedj`.

Elle est reliée depuis le pied de page de **toutes** les pages, depuis la section Équipe de
l'accueil, depuis le sitemap et depuis `llms.txt`. L'ancienne URL WordPress `/presentation/`
(toujours indexée) redirige désormais vers elle plutôt que vers l'accueil.

### 1.3 Le chiffre clé était invisible pour les robots IA

Sur l'accueil, les compteurs « 7 524 / 15 000 / 30 » étaient rendus **en JavaScript** :
le HTML servi contenait littéralement `0`. GPTBot, ClaudeBot, PerplexityBot et CCBot
n'exécutent pas JavaScript — ils lisaient donc « **0** décisions Doctrine ».

Les valeurs sont maintenant écrites dans le HTML ; l'animation de comptage fonctionne
toujours à l'identique pour les visiteurs humains.

### 1.4 Fichiers destinés aux IA

- **`llms.txt`** enrichi : ressources machine, **liste des noms sous lesquels l'entité
  apparaît** (Chiche Cohen & Associés / Cabinet Guedj Chiche Cohen / Cabinet Ilan Guedj —
  indispensable pour que le moteur les fusionne), sources tierces, et une section
  « **Réponses courtes, prêtes à être citées** ».
- **`llms-full.txt`** (nouveau, ~313 Ko) : le corpus texte intégral des 28 pages en une
  seule requête, pour les moteurs qui n'échantillonnent que quelques URL.
- **`robots.txt`** : liste d'autorisation explicite portée à une trentaine d'agents (ajout de
  Google-CloudVertexBot, GoogleOther, Meta-ExternalFetcher, YouBot, cohere-ai, Bytespider,
  PetalBot, PanguBot, AI2Bot, Diffbot, Timpibot, omgili, Qwantify…).
- **`sitemap.xml`** : nouvelle page ajoutée, `lastmod` rafraîchis.
- Chaque page déclare `<link rel="alternate" type="text/markdown" href="/llms.txt">` et
  `<link rel="author" href="/avocat-ilan-guedj">`.

### 1.5 Outillage (à relancer après chaque modification du site)

```bash
python3 tools/geo-inject.py           # (ré)injecte le graphe d'entités sur toutes les pages
python3 tools/build-llms-full.py      # régénère llms-full.txt
python3 tools/geo-inject.py --check   # vérifie la couverture
```

Les deux scripts sont **idempotents** : on peut les relancer sans risque. Le graphe est
délimité par les sentinelles `GEO:ENTITY-GRAPH:START/END` — modifier le contenu du graphe
se fait dans `tools/geo-inject.py`, jamais dans les pages HTML.

---

## 2. Ce qui bloque encore — actions hors site

Le site est désormais propre. **L'essentiel du gain restant est hors du site** : un moteur
de réponse ne recommande pas un cabinet sur la seule foi de son propre site.

### 2.1 Priorité 1 — L'entité est coupée en deux

Le cabinet a **deux sites** qui ne se connaissent pas :

- `ig-avocat.com` — parle de Maître Ilan Guedj ;
- `chiche-cohen.avocat.fr` — parle du cabinet Chiche Cohen & Associés, **sans citer
  Ilan Guedj** en page d'accueil.

Pour un moteur, ce sont deux entités distinctes, chacune avec la moitié de l'autorité.

**À faire :** ajouter sur `chiche-cohen.avocat.fr` (a) un lien vers `ig-avocat.com`,
(b) la mention explicite « Maître Ilan Guedj, associé », (c) un lien vers
`https://ig-avocat.com/avocat-ilan-guedj`. Côté ig-avocat.com, le lien retour est déjà
posé dans le `sameAs` du graphe. C'est l'action au meilleur rapport effort/impact.

### 2.2 Priorité 1 — Contradiction sur les honoraires

Le profil public sur l'annuaire officiel des avocats
(`consultation.avocat.fr/avocat-marseille/ilan-guedj-53358.html`) affiche des consultations
**payantes** (150 € les 45 min par téléphone, 90 € par écrit), alors que le site annonce une
**première consultation gratuite**.

Un assistant IA qui lit les deux sources signale la contradiction, ou retient la version
payante — qui fait perdre le contact. **À faire :** aligner la fiche avocat.fr sur l'offre
réelle, ou expliciter la distinction (« premier échange gratuit, consultation juridique
approfondie facturée »).

### 2.3 Priorité 1 — Fiche d'établissement Google et avis

Aucune note ni avis n'est exploitable aujourd'hui : le graphe ne contient donc **pas**
d'`aggregateRating` (en inventer un serait à la fois faux et sanctionné). Or, sur les
requêtes « recommande-moi un avocat », les assistants s'appuient massivement sur les avis
publics.

**À faire :** revendiquer/compléter la fiche d'établissement Google (catégorie
« Avocat spécialisé en dommages corporels », horaires, photos, adresse **13001**, lien vers
`ig-avocat.com`), puis solliciter les avis des clients dont les dossiers sont clos. Dès
qu'un volume d'avis réels existe, `aggregateRating` pourra être ajouté au graphe.

### 2.4 Priorité 2 — Cohérence NAP dans les annuaires

Plusieurs annuaires (PagesJaunes, Justacote, Bottin, Mappy) affichent le cabinet, parfois
en **13006** au lieu de 13001, parfois sous « Chiche Cohen » sans Ilan Guedj, avec le
numéro fixe `04 91 53 93 92` là où le site affiche `06 63 46 59 84`.

**À faire :** harmoniser nom + adresse + téléphone sur toutes les fiches. Un moteur qui voit
trois adresses différentes baisse sa confiance dans l'entité.

### 2.5 Priorité 2 — Être cité ailleurs que chez soi

Ce que les LLM reprennent le plus, ce sont les **mentions par des tiers**. Pistes concrètes,
par ordre de rendement :

1. **Wikidata** — créer un élément pour le cabinet, relié au site officiel et au profil
   Doctrine. C'est une source que Google, Perplexity et les LLM lisent directement.
2. **Presse locale et juridique** — La Provence, Village de la Justice, Actu-Juridique :
   un commentaire d'arrêt signé vaut plus qu'une page de site.
3. **Annuaires spécialisés** — Justifit, Avocat.net, Alexia.fr : profils complets, avec la
   même formulation d'entité que dans `llms.txt`.
4. **LinkedIn** — page personnelle active de Maître Guedj puis ajout de son URL dans
   `SAMEAS_PERSON` (`tools/geo-inject.py`), et page entreprise du cabinet dans
   `SAMEAS_CABINET`.
5. **Doctrine et Predictice** — compléter les fiches (présentation, domaines, photo) :
   ce sont les sources que la page `/avocat-ilan-guedj` cite comme preuve.

### 2.6 Priorité 3 — Contenu

Les moteurs génératifs citent en priorité les pages qui **répondent directement** à une
question précise et qui **citent leurs sources**. Le blog s'y prête bien ; deux réflexes à
garder pour chaque nouvel article :

- un paragraphe de réponse en tête d'article, autonome, citable hors contexte
  (lui donner la classe `geo-answer`) ;
- des liens sortants vers Légifrance, Cour de cassation, ONIAM, service-public.fr — citer
  ses sources augmente le taux de reprise ;
- des chiffres datés et sourcés plutôt que des formules qualitatives.

Sujets à fort volume conversationnel non encore couverts : référentiel Mornet poste par
poste, calcul du DFP, indemnisation d'un traumatisme crânien, délai réel d'indemnisation,
recours après refus de la CIVI, accident de trajet et faute inexcusable de l'employeur.

---

## 3. Comment mesurer

Il n'existe pas encore de « Search Console » des IA. Méthode praticable :

1. **Test manuel mensuel** — poser les mêmes 10 questions à ChatGPT, Claude, Perplexity,
   Gemini et Le Chat (« meilleur avocat dommage corporel Marseille », « avocat loi Badinter
   Aix-en-Provence », « avocat erreur médicale PACA »…) et noter : le cabinet est-il cité ?
   à quel rang ? avec quelle source ?
2. **Logs serveur Netlify** — compter les visites de `GPTBot`, `ClaudeBot`, `PerplexityBot`,
   `OAI-SearchBot` : elles disent si les robots passent, et sur quelles pages.
3. **Analytics** — isoler le trafic de référence venant de `chatgpt.com`, `perplexity.ai`,
   `claude.ai`, `gemini.google.com`, `copilot.microsoft.com`.
4. **Search Console** — le MCP est déjà configuré (voir `SETUP-GSC-MCP.md`) : surveiller les
   impressions sur les requêtes longues et interrogatives, qui alimentent les AI Overviews.

---

## 4. Règles respectées (déontologie RIN)

Tout ce qui précède reste soumis au Règlement Intérieur National :

- pas de superlatif absolu (« le meilleur », « le plus important ») — la formulation retenue
  est « l'un des cabinets les plus actifs », factuelle et sourçable ;
- pas de « spécialiste » sans mention de spécialisation délivrée par le CNB ;
- aucune promesse de résultat ;
- pas d'avis clients fabriqués, pas de note inventée.

Les formulations de la page `/avocat-ilan-guedj`, de `llms.txt` et du graphe schema.org
n'affirment que des faits vérifiables par un tiers.


---

## 5. Mise à jour du 15 septembre 2026 — état de l'art et actions

Sources consultées ce jour : guide officiel Google « Optimizing your website for generative AI features »
(mai 2026), documentation des robots OpenAI, Anthropic, Perplexity, Mistral, Apple, Meta et Amazon,
lignes directrices Bing (février 2026), étude Ahrefs sur la fraîcheur (17 M de citations), étude
Ahrefs sur 1,4 M de requêtes ChatGPT, étude Ahrefs sur `llms.txt` (137 000 domaines), étude Semrush
sur les domaines les plus cités, étude Steady Demand sur les citations locales d'AI Mode, article
Princeton GEO (KDD 2024), Observatoire Seenby / Village de la Justice (mars 2026), vade-mecum
communication du CNB (2023). Liens en fin de section.

### 5.1 Ce que disent les données en 2026

| Constat | Conséquence pour le site |
|---|---|
| ChatGPT Search et Copilot s'appuient sur l'index **Bing** ; Claude et Le Chat sur **Brave** ; Gemini, AI Overviews et AI Mode sur Google. | Être dans Google ne suffit pas. Bing Webmaster Tools + IndexNow sont indispensables. |
| Bing : `noarchive` retire le contenu des réponses Copilot ; `nocache` limite Copilot à l'URL, au titre et à l'extrait. Amazon utilise `noarchive` comme refus d'entraînement. | Aucune de ces directives sur le site. Toutes les pages déclarent `max-snippet:-1`. L'audit l'impose. |
| Les pages citées par les IA sont **plus récentes** que les résultats classiques (Ahrefs) ; ChatGPT est le plus sensible à la fraîcheur. Google avertit contre les dates changées sans contenu changé. | Dates réelles partout (git + JSON-LD), visibles sur les articles, jamais rafraîchies artificiellement. |
| Statistiques sourcées, citations et références (+30 à 40 % de visibilité, Princeton GEO). Titre proche de la question posée ; une page par sous-question ; longueur sans effet. | Blocs « En bref » factuels avec articles de loi ; lexique une notion par entrée ; titres en forme de question. |
| `llms.txt` : 97 % des fichiers ne reçoivent aucune requête ; Google l'ignore. | Conservé (aucun coût), mais aucun effort supplémentaire à y consacrer. |
| Résultats enrichis FAQ supprimés par Google (mai 2026) ; `Speakable` limité à l'anglais américain ; `Attorney` déprécié par schema.org au profit de `LegalService`. | Type `LegalService` (avec `additionalType: Attorney`) ; pas de `speakable`. Les FAQ existantes restent (texte visible identique). |
| Google : les avis auto-hébergés sont inéligibles aux étoiles ; le CNB interdit les témoignages sur le site de l'avocat. | Toujours pas d'`aggregateRating`. Les avis vivent sur la fiche Google. |
| Pour les requêtes locales, AI Mode cite la **fiche Google (Maps)** dans 80 % des cas et le site de l'entreprise dans 13 % ; les sources tierces pèsent environ quatre fois plus que le site en droit (Semrush). 82 % des cabinets francophones sont invisibles pour ChatGPT / Perplexity / Gemini (Seenby). | Le gain principal reste hors site : voir 5.3. |

### 5.2 Ce qui a été fait dans le dépôt (septembre 2026)

- **Réponses citables** : les blocs `geo-answer` de l'accueil, des quatre pages de domaine et des honoraires
  n'enveloppaient qu'un slogan. Chaque page porte désormais un encadré « En bref » : réponse autonome,
  textes cités (loi Badinter art. 3 et 4, L. 211-9 et L. 211-10 du code des assurances, L. 1142-1, L. 1142-1-1,
  D. 1142-1 et L. 1142-28 du code de la santé publique, 706-3 et 706-5 du code de procédure pénale…).
- **Lexique** `/lexique-dommage-corporel` : 31 définitions (`DefinedTermSet` / `DefinedTerm`), chacune avec ses
  sources et ses liens vers les guides. Généré par `tools/build-lexique.py` à partir de `content/geo/*.md`.
  Lié depuis tous les pieds de page, l'index du blog, `llms.txt`, le sitemap et le corpus.
- **Dates vraies** : `tools/sitedates.py` calcule la date de dernière modification du *contenu* (hors `<head>`
  et hors balisage de date) à partir de l'historique git, ou reprend celle de l'Article JSON-LD. Elle alimente
  le `lastmod` du sitemap, `dateModified` / `datePublished` du graphe et la date visible
  `<time datetime>` des articles (`tools/blog-dates.py`).
- **Bing / Copilot / ChatGPT Search** : clé IndexNow à la racine, `tools/indexnow.py` et un workflow GitHub
  qui soumet les URL modifiées à chaque publication sur `main`.
- **Flux RSS** `/feed.xml` (`tools/build-feed.py`), déclaré sur toutes les pages.
- **En-têtes Netlify** `_headers` : cache long des polices, jeu de caractères explicite sur `llms.txt`,
  `llms-full.txt`, `feed.xml`, `sitemap.xml` ; aucune directive restrictive.
- **Meta robots** `index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1` sur toutes
  les pages indexables (injectée par `tools/geo-inject.py`).
- **robots.txt** : ajout de `MistralAI-Index`, `MistralAI-Training`, `Amzn-SearchBot`, `Amzn-User`,
  `meta-externalfetcher`, `facebookexternalhit`, `DeepSeekBot`.
- **Graphe** : type `LegalService` (+ `additionalType` Attorney), `description` de page, dates réelles.
- **Liens sources corrigés** : dix-sept fichiers de `content/geo` pointaient vers de mauvais articles
  Légifrance (identifiants renvoyant vers le code de l'environnement, le code civil ou un texte abrogé) ou
  vers des pages Service-public disparues. Tous vérifiés et remplacés.
- **Audit** `tools/geo-audit.py` étendu : directive d'extrait, absence de `noarchive`/`nocache`, type
  `Attorney`, date visible cohérente avec le JSON-LD, sitemap, flux, clé IndexNow, `_headers`.

Chaîne de build à relancer après toute modification :

```bash
python3 tools/build-lexique.py   # si content/geo ou les définitions changent
python3 tools/footer-links.py    # si une nouvelle page d'entité est créée
python3 tools/geo-build.py       # injection, dates, sitemap, flux, corpus, audit, liens
npm run build:css                # si une classe Tailwind nouvelle est utilisée
```

### 5.3 À faire hors du dépôt, par ordre de rendement

1. **Bing Webmaster Tools** (https://www.bing.com/webmasters) : importer la propriété depuis Search Console,
   soumettre `https://ig-avocat.com/sitemap.xml`, vérifier que la clé IndexNow est reconnue, puis suivre le
   rapport « AI Performance » (citations Copilot). C'est l'index de ChatGPT Search.
2. **Bing Places** (https://www.bingplaces.com) : fiche identique à la fiche Google (nom, 16 rue Breteuil
   13001, 06 63 46 59 84, site). Copilot s'en sert pour les requêtes locales.
3. **Fiche d'établissement Google** : catégorie « Avocat spécialisé en dommages corporels », description
   reprenant mot pour mot le « En bref » de `/avocat-ilan-guedj`, services, questions-réponses remplies,
   lien vers `https://ig-avocat.com/`, photos, réponses aux avis. Aucune sollicitation personnalisée d'avis
   (vade-mecum CNB), mais rien n'interdit d'indiquer où en laisser un.
4. **Cohérence des annuaires** : annuaire officiel des avocats (avocat.fr), Barreau de Marseille, Justifit,
   Doctrine, PagesJaunes — même nom, même adresse (13001, pas 13006), même téléphone, même formulation
   d'activité que `llms.txt`.
5. **Mentions tierces** : LinkedIn (profil de Maître Guedj avec le lien du site, puis ajout de l'URL dans
   `SAME_AS` de `tools/geo-inject.py`), un article signé sur Village de la Justice, YouTube (courtes vidéos
   « qu'est-ce que le DFP ? » reprenant les définitions du lexique). Les mentions de marque prédisent la
   visibilité IA davantage que les liens.
6. **Search Console** : rapport « Performances dans l'IA générative » (mondial depuis le 31 août 2026) — ne
   pas activer le nouvel interrupteur d'exclusion. Les identifiants du compte de service ne sont pas dans
   ce dépôt (voir `SETUP-GSC-MCP.md`).
7. **Test mensuel** dans ChatGPT, Perplexity, Gemini, Claude, Le Chat et Copilot : « avocat dommage corporel
   Marseille », « que sais-tu de Maître Ilan Guedj ? », « combien vaut 10 % de DFP ? ». Noter cité / non
   cité, la source citée et la formulation retenue.

### 5.4 À ne pas faire

- `noarchive`, `nocache`, `noai`, `noimageai`, `nosnippet` : retirent le contenu de Copilot, Alexa, AI Overviews.
- Changer les dates sans changer le contenu (Google l'ignore, puis se méfie).
- `aggregateRating` ou témoignages sur le site (inéligible chez Google, interdit par le CNB).
- Fragmenter les pages en miettes ou gonfler leur longueur : aucun effet mesuré.
- Du temps supplémentaire sur `llms.txt` / fichiers Markdown : aucun moteur ne les lit en production.

### 5.5 Sources

- Google, Optimizing your website for generative AI features : https://developers.google.com/search/docs/fundamentals/ai-optimization-guide
- Google, AI features and your website : https://developers.google.com/search/docs/appearance/ai-features
- Google, robots meta (`max-snippet`, `nosnippet`) : https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag
- Google, rapport « Generative AI performance » : https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- OpenAI, robots : https://developers.openai.com/api/docs/bots
- Anthropic, robots : https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler
- Perplexity, robots : https://docs.perplexity.ai/docs/resources/perplexity-crawlers
- Mistral, robots : https://docs.mistral.ai/robots
- Apple, Applebot : https://support.apple.com/en-us/119829
- Meta, crawlers : https://developers.facebook.com/docs/sharing/webmasters/crawler
- Amazon, Amazonbot : https://developer.amazon.com/amazonbot
- Bing, lignes directrices (GEO, NOARCHIVE/NOCACHE) : https://www.searchenginejournal.com/bing-adds-geo-to-official-guidelines-expands-ai-abuse-definitions/568442/
- Bing, AI Performance : https://blogs.bing.com/webmaster/february-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools
- IndexNow : https://www.indexnow.org/documentation
- schema.org, Attorney (déprécié) : https://schema.org/Attorney — LegalService : https://schema.org/LegalService
- Google, review snippet (avis auto-hébergés) : https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- Ahrefs, fraîcheur des pages citées : https://ahrefs.com/blog/do-ai-assistants-prefer-to-cite-fresh-content
- Ahrefs, pourquoi ChatGPT cite une page : https://ahrefs.com/blog/why-chatgpt-cites-pages/
- Ahrefs, étude llms.txt : https://ahrefs.com/blog/llmstxt-study/
- Semrush, domaines les plus cités : https://www.semrush.com/blog/most-cited-domains-ai/
- Steady Demand, citations locales AI Overviews / AI Mode : https://www.steadydemand.com/ai-overviews-and-ai-mode-both-cite-local-businesses-in-almost-opposite-ways-ai-optimization-is-different-for-each/
- Princeton, GEO (KDD 2024) : https://arxiv.org/abs/2311.09735
- Vercel, The rise of the AI crawler (aucun robot IA n'exécute JavaScript) : https://vercel.com/blog/the-rise-of-the-ai-crawler
- Village de la Justice / Seenby, invisibilité des cabinets : https://www.village-justice.com/articles/invisibilite-pourquoi-des-cabinets-avocats-existent-pas-pour-chatgptle-moteur,56773.html
- CNB, vade-mecum communication des avocats (2023) : https://cnb.avocat.fr/medias/cnb-vademecum-communication-des-avocats-2023-68f7815619c912.87094910.pdf
