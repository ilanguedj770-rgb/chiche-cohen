# Référencement dans les recommandations IA (GEO) — ig-avocat.com

> GEO = *Generative Engine Optimization* : être lu, compris et **cité** par ChatGPT,
> Claude, Perplexity, Google AI Overviews / AI Mode, Copilot, Le Chat, Apple Intelligence
> quand quelqu'un demande « quel avocat en dommage corporel à Marseille ? ».
>
> Dernière mise à jour : 27 août 2026.

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
