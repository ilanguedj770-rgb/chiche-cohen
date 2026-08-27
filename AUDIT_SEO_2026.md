# AUDIT SEO 2026 — ig-avocat.com

> **Note de mise à jour (août 2026).** Le site a été harmonisé autour d'une entité
> unique, Maître Ilan Guedj. Les recommandations de ce document qui portent sur
> l'identité collective du cabinet (dénomination Chiche Cohen, associés, effectif,
> volumes d'activité, décisions Doctrine, page « Notre bilan ») sont caduques et ne
> doivent plus être appliquées. Le reste du document reste valable.

> Audit complet réalisé le 2026-05-14 sur la branche `claude/seo-audit-phase-1-10S7x`.
> Périmètre : 28 pages HTML (17 racine + 11 blog) + sitemap, robots, llms.txt, assets.

---

## ⚠️ AVERTISSEMENT PRÉALABLE — DIVERGENCE DE STACK

Le brief annonce une stack **Next.js 14 App Router + TypeScript + Tailwind**.
**La réalité du dépôt est différente** : le site est un ensemble de **fichiers HTML statiques** servis directement par Netlify, avec Tailwind compilé via `npm run build:css` (cf. `package.json`). Aucun `app/`, `pages/`, ni `next.config.*` n'est présent.

**Conséquence pour les phases suivantes** : tous les composants Next (`<JsonLd>`, `components/blog/ArticleLayout.tsx`, `app/sitemap.ts`, `next/image`, `next/font`, server components…) demandés en Phase 3, 5 et 6 ne peuvent **pas** être livrés tels quels. Trois options à arbitrer avec toi avant Phase 2 :

| Option | Description | Effort | Risque |
|---|---|---|---|
| **A — Migrer vers Next.js 14** comme prévu au brief | Reconstruire tout le site en Next.js, conserver design et contenu | Élevé (3-4 semaines) | Régression visuelle possible, refonte du build |
| **B — Rester en HTML statique** et adapter le plan | Schémas, sitemap, breadcrumbs, etc. en HTML/JS pur | Moyen | Pas de DX moderne, duplication entre pages |
| **C — Hybride : ajouter un build statique** (Eleventy, Astro) pour mutualiser layouts & schemas | Conserver les URLs actuelles, regénérer le HTML à partir de templates | Élevé (2 semaines) | Migration du contenu vers MDX/Nunjucks |

**Recommandation** : Option **C avec Astro** — proche de la stack annoncée (TS, composants, MDX pour le blog), génère du HTML pur identique à l'existant, déployable sur Netlify sans changement, et permet de livrer les composants `<JsonLd>`, `<Breadcrumbs>`, `<ArticleLayout>` demandés au brief. **À valider avant Phase 2.**

À défaut de décision, l'audit ci-dessous s'applique à la stack actuelle (HTML statique).

---

## 1.1 — Inventaire des pages & métadonnées

### Pages racine

| URL | Title (longueur) | Meta description (longueur) | H1 | Mots | Canonical |
|---|---|---|---|---|---|
| `/` (index) | « Avocat Dommage Corporel Marseille \| 7 524 décisions Doctrine \| Maître Ilan Guedj » (82 c) ⚠️ | 229 c ❌ | Votre préjudice. Notre combat. | 3 780 | ✅ `https://ig-avocat.com` |
| `/accidents-route` | « Avocat Accident de la Circulation Marseille \| Préjudices Graves \| Ilan Guedj » (77 c) ⚠️ | 234 c ❌ | Accident de la Circulation | 3 395 | ✅ |
| `/accidents-vie` | « Avocat Accidents de la Vie à Marseille \| GAV \| Ilan Guedj » (58 c) ✅ | 176 c ⚠️ | Accidents de la Vie | 1 815 | ✅ |
| `/agression` | « Avocat Victime d'Agression à Marseille \| FGTI, CIVI \| Ilan Guedj » (65 c) ⚠️ | 148 c ✅ | Agression & Violence | 1 777 | ✅ |
| `/agressions` (legacy) | « Redirection… » | absente | — | 13 | ⚠️ doublon → suppression recommandée |
| `/erreur-medicale` | « Avocat Erreur Médicale à Marseille \| ONIAM, CCI \| Ilan Guedj » (62 c) ⚠️ | 169 c ⚠️ | Erreur Médicale | 1 843 | ✅ |
| `/notre-bilan` | « Notre bilan — Cabinet Chiche Cohen \| Maître Ilan Guedj » (57 c) ✅ | 252 c ❌ | Notre bilan, à livre ouvert. | 1 480 | ✅ |
| `/honoraires` | « Honoraires Avocat Dommage Corporel Marseille \| 0€ d'avance \| Ilan Guedj » (73 c) ⚠️ | 158 c ✅ | Une rémunération transparente, liée à votre succès. | 990 | ✅ |
| `/contact` | « Contacter Maître Ilan Guedj \| Avocat Marseille » (47 c) ✅ | 109 c ⚠️ | Contactez-nous | 940 | ✅ |
| `/mentions-legales` | « Mentions Légales \| Maître Ilan Guedj » (38 c) ✅ | **absente** ❌ | Mentions Légales | 1 146 | ✅ |
| `/guide-5-erreurs` | « Les 5 Erreurs à Éviter Après un Accident Corporel \| Guide Maître Ilan Guedj » (79 c) ⚠️ | **absente** ❌ | Les 5 erreurs fatales après un accident corporel | 2 131 | ❌ **manquant** |
| `/avocat-aix-en-provence` | 95 c ❌ | 271 c ❌ | Avocat dommage corporel à Aix-en-Provence | 2 421 | ✅ |
| `/avocat-toulon` | 86 c ⚠️ | 280 c ❌ | Avocat dommage corporel à Toulon | 2 396 | ✅ |
| `/avocat-nice` | 84 c ⚠️ | 299 c ❌ | Avocat dommage corporel à Nice | 2 471 | ✅ |
| `/avocat-avignon` | 87 c ⚠️ | 298 c ❌ | Avocat dommage corporel à Avignon | 2 515 | ✅ |
| `/avocat-montpellier` | 91 c ⚠️ | 298 c ❌ | Avocat dommage corporel à Montpellier | 2 454 | ✅ |
| `/avocat-nimes` | 86 c ⚠️ | 322 c ❌ | Avocat dommage corporel à Nîmes | 2 440 | ✅ |

### Pages blog (`/blog/*`)

| URL | Title (longueur) | Meta desc (longueur) | Mots | H2/H3 |
|---|---|---|---|---|
| `/blog/` | 48 c ✅ | 142 c ✅ | 785 | 12/5 |
| `/blog/que-faire-apres-accident-route` | 61 c ⚠️ | 150 c ✅ | 2 052 | 9/4 |
| `/blog/indemnisation-accident-corporel` | 64 c ⚠️ | 157 c ✅ | 2 124 | 10/8 |
| `/blog/refuser-offre-assurance-accident` | 60 c ✅ | 158 c ✅ | 2 072 | 10/6 |
| `/blog/erreur-medicale-droits-victime` | 66 c ⚠️ | 163 c ⚠️ | 4 136 | 14/24 |
| `/blog/delai-prescription-accident-corporel` | 61 c ⚠️ | 158 c ✅ | 2 310 | 10/4 |
| `/blog/agression-victime-droits-recours` | 60 c ✅ | 161 c ⚠️ | 2 102 | 10/7 |
| `/blog/expertise-medicale-judiciaire` | 51 c ✅ | 133 c ⚠️ | 2 937 | 11/15 |
| `/blog/indemnisation-victime-passagere-accident` | 72 c ⚠️ | 138 c ✅ | 2 421 | 10/7 |
| `/blog/medecin-recours-victime` | 78 c ❌ | 149 c ✅ | 1 766 | 9/8 |
| `/blog/faute-conducteur-victime-indemnisation` | 73 c ⚠️ | 179 c ❌ | 2 410 | 10/11 |
| `/blog/indemnisation-accident-grave` | 77 c ⚠️ | 207 c ❌ | 7 146 | 15/51 |

**Légende** — ✅ conforme · ⚠️ acceptable mais sous-optimal · ❌ à corriger
- Title : cible 50-60 c
- Description : cible 140-160 c

### Synthèse 1.1

- **17 / 28 titles dépassent 60 caractères** → tronqués dans la SERP.
- **13 / 28 meta descriptions dépassent 160 caractères** → tronquées.
- **2 pages (`mentions-legales`, `guide-5-erreurs`) n'ont aucune meta description.**
- **`guide-5-erreurs` n'a pas de canonical** → risque de duplication.
- **`agressions.html` est une page de redirection HTML inutile** (déjà couverte par `_redirects` → à supprimer du dépôt).
- Le H1 sur **5 pages domaines** (`accidents-route`, `accidents-vie`, `agression`, `erreur-medicale`, `index`) est très court et n'inclut pas le mot-clé principal complet (ex. « Accident de la Circulation » au lieu de « Avocat accident de la circulation à Marseille »).

---

## 1.2 — Fichiers techniques

| Fichier | État | Commentaires |
|---|---|---|
| `sitemap.xml` | ✅ présent | 26 URLs. Manque toutefois `/` racine de blog cohérente (présent : `/blog/` ✅). `lastmod` figé à 2026-05-14 partout. |
| `robots.txt` | ✅ présent | Disallow `/nov-apijson/`, `/embed/`. Sitemap déclaré. |
| `_redirects` (Netlify) | ✅ présent | Canonicalisation `.html` → URLs propres, ancien WordPress redirigé. |
| `llms.txt` | ✅ présent | Excellente initiative IA-SEO ; à enrichir au fil des nouvelles pages. |
| `schema markup` | ⚠️ partiel | `LegalService`, `FAQPage`, `BreadcrumbList`, `Article`, `Organization` présents — détaillé en 1.2 bis. |
| `breadcrumbs visibles` | ❌ absents | Schema `BreadcrumbList` présent dans le JSON-LD mais **aucun fil d'Ariane visuel** dans le DOM. |
| `Open Graph` | ✅ présent | OG + Twitter Card sur la plupart des pages. |
| `hreflang` | n/a | Site monolangue (fr-FR). OK. |

### 1.2 bis — Inventaire schema.org

Occurrences de `@type` agrégées sur l'ensemble du site :

- `Organization` × 19 (présent sur quasi toutes les pages, mais redondant — un Organization global suffirait)
- `LegalService` × 14
- `FAQPage` × 12
- `BreadcrumbList` × 12 (mais **non rendu visuellement**)
- `Article` × 9 ; `BlogPosting` × 2 (incohérence — tout devrait être `Article` ou tout `BlogPosting`)
- `OpeningHoursSpecification` × 2 (uniquement sur index + 1 autre) ❌ à propager
- `Person` × 3 → l'équipe (6 avocats annoncés au brief) n'est pas modélisée en `Attorney`/`Person` partout ❌
- ❌ **Pas de `LocalBusiness` distinct** avec geo coordinates (seul `LegalService` + `GeoCoordinates` existe — acceptable mais perfectible)
- ❌ **Pas de `Service` granulaire par domaine d'expertise** (Badinter, ONIAM, GAV, CIVI…)

### 1.3 — Duplication entre pages géo

Test rapide sur les 6 pages géo (~2 400 mots chacune) :
- **Mention « 7 524 décisions référencées sur Doctrine.fr » présente dans les 6** → factuelle mais identique mot pour mot.
- Chaque page possède pourtant **un paragraphe spécifique par ville** (TJ compétent, CA, axes routiers, particularités locales — étudiants Montpellier, autoroutes Nîmes, montagne Nice, militaires Toulon, etc.).
- **Verdict** : duplication acceptable (< 30 % du contenu). Les sections « FAQ », « Tribunal compétent », « Particularités locales » sont bien différenciées. ✅
- **Mais** : la section « Pourquoi nous choisir » (« Ensuite la **connaissance fine des juridictions du Sud**… ») est quasi identique entre Aix, Nice, Toulon — à diversifier.

### 1.4 — Images

| Indicateur | Constat |
|---|---|
| Format | `.webp` présent (équipe, associés). `.jpg` pour collaborateurs/juristes (Carosso, Walas, Abikhzir, Biosse Duplan). |
| Alt | ✅ Toutes les `<img>` du site ont un `alt` (index : 9/9, contact : 1/1). |
| Lazy loading | ❌ Présent uniquement sur `index.html` (4 occurrences) et `contact.html` (2). **Aucune autre page n'utilise `loading="lazy"`** car aucune autre page ne contient de `<img>` HTML. |
| `<picture>` / srcset | ❌ Aucune utilisation. Risque CLS / LCP sur mobile. |
| Dimensions explicites | À vérifier au Phase 1.4 (Core Web Vitals). |

**Remarque** : les pages domaines & géo n'utilisent **aucune image** — uniquement des SVG inline et icônes. Pas de problème d'alt, mais opportunité ratée de visuel pour le SEO image (préjudice perçu, équipe, locaux).

---

## 1.2 — Audit SEO on-page (résumé)

### Maillage interne — liens entrants par cible

| Cible | Pages qui linkent vers elle | Verdict |
|---|---|---|
| `/contact` | 16 | ✅ |
| `/notre-bilan` | 15 | ✅ |
| `/honoraires` | 15 | ✅ |
| `/blog/` | 15 | ✅ |
| `/mentions-legales` | 15 | ✅ |
| `/agression` | 9 | ✅ |
| `/accidents-route` | 8 | ⚠️ |
| `/accidents-vie` | 8 | ⚠️ |
| `/erreur-medicale` | 8 | ⚠️ |
| `/avocat-aix-en-provence` | **1** | ❌ orpheline |
| `/avocat-toulon` | **1** | ❌ orpheline |
| `/avocat-nice` | **1** | ❌ orpheline |
| `/avocat-avignon` | **1** | ❌ orpheline |
| `/avocat-montpellier` | **1** | ❌ orpheline |
| `/avocat-nimes` | **1** | ❌ orpheline |
| `/guide-5-erreurs` | **1** | ❌ orpheline |

→ **6 pages géo + le guide ne sont quasiment liées que depuis le sitemap.** Le maillage est l'une des trois priorités absolues de la Phase 2/3.

### Liens internes sortants

- `/blog/indemnisation-accident-grave` (page la plus longue, 7 146 mots) : **6 liens internes seulement** vers d'autres pages du site (footer + ressources). 0 lien contextuel inline vers articles connexes ou pages domaines.
- Toutes les pages blog : **1 seul lien interne** vers d'autres articles ou pages domaines en analyse rapide (footer/menu compris).
- `index.html` : ne pointe vers aucune des 6 pages géo, ni vers `guide-5-erreurs`.

### Pages orphelines

- `agressions.html` (page de redirection HTML 13 mots) → à supprimer du dépôt.
- Pas d'autres pages orphelines détectées au niveau filesystem ; les pages géo sont liées **depuis le sitemap** mais peu depuis les autres pages, ce qui dilue leur transmission de jus.

---

## 1.3 — Audit déontologique RIN

**Méthode** : recherche regex insensible à la casse sur les 16 racines + 11 blog.

### Occurrences à corriger en priorité

| Mot/expression | Localisation | Verdict |
|---|---|---|
| **« le meilleur cabinet »** | `index.html:1170` (témoignage client) | ⚠️ RIN : éviter même cité, ou contextualiser avec mention « Témoignages clients » + disclaimer. |
| **« connus pour être les meilleurs »** | `index.html:1157` (témoignage client) | ⚠️ idem. |
| **« nous obtenons la meilleure indemnisation »** | `index.html:618` | ❌ formulation comparative implicite → reformuler « nous visons l'indemnisation la plus complète conforme aux barèmes en vigueur ». |
| **« nous négocions une meilleure offre »** | `accidents-vie.html:428` | ⚠️ ambigu — « nous négocions une revalorisation de l'offre » est plus prudent. |
| **« l'expertise judiciaire garantit une meilleure indemnisation »** | `blog/expertise-medicale-judiciaire.html` (3 occurrences dont meta description + og + twitter) | ❌ « garantit » → reformuler « offre un cadre plus protecteur de l'indemnisation ». |
| **« cabinet d'avocats… le plus actif »** | `index.html:155, 1220` (FAQ + JSON-LD `FAQPage`) | ⚠️ « parmi les cabinets les plus actifs » est plus prudent (factuel et sourçable via Doctrine), supprime le superlatif absolu. |
| **« l'un des cabinets en dommage corporel les plus actifs du Sud »** | `llms.txt`, plusieurs pages géo | ✅ acceptable (« l'un des… ») — à conserver, factuellement sourçable. |
| **« Un avocat en dommage corporel peut obtenir 5 à 10 fois plus »** | FAQ géo « Mon assureur GAV propose une offre… » | ❌ promesse de résultat chiffrée → reformuler « peut conduire à une revalorisation significative, dont l'ampleur dépend du dossier ». |

### Termes apparemment problématiques mais en réalité OK (faux positifs)

- **`spécialiste` / `spécialistes`** : **0 occurrence** dans le contenu rédactionnel ✅
- **`leader`, `n°1`, `numéro 1`, `100 % de réussite`, `garantie de résultat`** : **0 occurrence** ✅
- **`expert(s)`** : nombreuses occurrences, mais toutes au sens de **« médecin expert / expert judiciaire »** (terme juridique normal). Aucune utilisation pour qualifier le cabinet lui-même. ✅
- **`garanti`** : toutes les occurrences se réfèrent au **FGTI (Fonds de Garantie)**, à la **GAV** ou à la mention disclaimer « les résultats passés ne garantissent pas les résultats futurs ». ✅
- **`le premier rendez-vous est gratuit`** : factuel, conforme RIN. ✅
- **`n°1`** sur `mentions-legales.html:169` : c'est en réalité le **numéro de contrat MMA n°118 263 720** — faux positif. ✅

### Disclaimers/mentions de précaution déjà présents (à conserver)

- ✅ « Les résultats passés ne garantissent pas les résultats futurs. Chaque dossier est unique. » (présent sur `accidents-vie`, `accidents-route`, `erreur-medicale`, `agression`)
- ✅ « Notre intervention vise à obtenir une indemnisation conforme aux barèmes en vigueur » — déjà présent dans la formulation cible du brief.

### Recommandations Phase 2.2

1. Réécrire les 4 occurrences ❌ ci-dessus en priorité (avant tout SEO).
2. Sur **chaque page contenant des témoignages** (`index.html`), ajouter une mention groupée :
   > *Témoignages recueillis avec le consentement écrit des clients. Les résultats individuels sont variables. Aucun engagement de résultat n'est pris.*
3. Reformuler les 3 occurrences de « le plus actif » au superlatif absolu en « parmi les plus actifs ».

---

## 1.3 bis — Identité juridique (audit)

**Constat majeur — à arbitrer en Phase 2.1** :

- Le fichier `mentions-legales.html` actuel mentionne :
  > Dénomination : **ILAN GUEDJ** · Représentée par : Ilan Guedj · SIRET : 481 038 321 00024 · Hébergement : **OVH**
- Le brief demande que l'entité juridique soit la **SELARL Chiche Cohen & Associés** et l'hébergeur **Netlify** :
  > « Hébergeur : Netlify Inc., 44 Montgomery Street, Suite 300, San Francisco, CA 94104 »
- Le footer du site ne mentionne ni SELARL, ni Chiche Cohen, ni associés — seulement « ILAN GUEDJ. » et « Cabinet d'Avocats au Barreau de Marseille ».
- `notre-bilan.html` et `llms.txt` mentionnent « le cabinet Chiche Cohen » et « Maître Ilan Guedj (associé à Patrice Chiche, Stéphane Cohen et Daniel Amar) ».
- ⚠️ **Le brief lui-même contient une incohérence** : Phase 2.1 mentionne d'abord **« SELARL »** puis **« SELAS »** plus bas. Il faut clarifier laquelle est exacte.

**À confirmer avec Ilan avant Phase 2.1** :
1. Forme juridique exacte : SELARL ou SELAS ?
2. SIRET de la SELARL/SELAS (différent du SIRET personnel `481 038 321 00024` actuel) ?
3. RCS de la structure (le RCS Lille apparaissant en mentions est en réalité celui d'**OVH** — faux positif).
4. Numéro de TVA intra-communautaire de la structure ?
5. Médiateur de la consommation effectivement saisi (CNB, ANCAA, autre) ?
6. Numéro et compagnie de RCP de la SELARL (le contrat MMA 118 263 720 est-il celui de la SELARL ou personnel ?).
7. Hébergement actuel : **OVH (mentionné dans `mentions-legales`)** ou **Netlify (mentionné dans le brief)** ? La doc Netlify d'`_redirects` confirme Netlify côté technique — il y a très probablement un reliquat OVH dans les mentions.

---

## 1.4 — Audit Core Web Vitals (statique)

**Note** : pas de Next.js → pas de bundle analysis JS. Audit basé sur le DOM, le CSS Tailwind, et les ressources externes chargées.

### Ressources externes chargées (extraits visibles dans le HEAD)

- `fonts.googleapis.com` (Inter weights 300-900) → **bloque le rendu**, pas de `display: swap` ni de `preload` détecté → recommander `font-display: swap` minimum, idéalement self-host.
- GTM `GTM-WP82S37T` ✅ présent dans tous les `<head>` et `<noscript>`.
- Calendly / Tally (à vérifier au prochain pass).
- WhatsApp deep-link `wa.me/33663465984` ✅ (pas d'iframe lourd).
- Tailwind compilé localement (`css/tailwind.css`) — ✅ pas de CDN.

### Risques CWV identifiés

1. **CLS** : aucune `<img>` ne déclare `width`/`height` explicites côté HTML (Tailwind classes seulement). Risque sur les vignettes équipe de `index.html`.
2. **LCP** : sur `index.html`, le hero est texte + dégradés CSS = bon ✅. Mais Google Fonts non-préchargées = LCP retardé.
3. **INP** : présence probable de scripts inline (à scanner phase 1.4 bis). Le widget de diagnostic — non encore audité — peut être un coupable.
4. **Taille des pages** : `index.html = 137 KB` (HTML brut), `accidents-route.html = 75 KB`. Avec gzip Netlify, OK. Mais beaucoup de classes Tailwind dans le DOM → JIT activé ?
5. **Pas de `Cache-Control` configuré** dans `_redirects` ou `_headers` (à vérifier).

### Quick wins CWV recommandés (Phase 6)

- Self-host Inter ou ajouter `<link rel="preload" as="font" type="font/woff2" crossorigin>` + `display: swap`.
- Ajouter `width`/`height` sur toutes les `<img>` (équipe sur index).
- Créer un fichier `_headers` Netlify avec `Cache-Control: public, max-age=31536000, immutable` pour `/img/*`, `/css/*`.
- Audit Lighthouse à exécuter post-déploiement pour mesurer baseline (à faire avec un outil externe — pas possible dans le shell ici).

---

## SYNTHÈSE & PRIORITÉS

### Score actuel estimé : 6.4 / 10 — concordant avec le brief

| Axe | Note | Justification |
|---|---|---|
| Technique (sitemap, robots, redirects, canonical) | 7,5/10 | Bien construit, manque breadcrumbs visuels, canonical absent sur 1 page |
| Schema markup | 7/10 | LegalService + FAQ + Article OK ; manque Attorney/Person équipe complète + LocalBusiness dédié |
| Métadonnées | 5/10 | 17/28 titles trop longs, 13/28 descriptions trop longues, 2 absentes |
| Contenu rédactionnel | 8/10 | Volume très bon (2 000-7 000 mots/page), qualité juridique élevée, faible duplication |
| Maillage interne | 4/10 | **Pages géo orphelines de fait**, 1 lien sortant moyen par article blog, pas de related content |
| Déontologie RIN | 7/10 | Quelques reformulations à faire mais le gros est conforme |
| Identité juridique | 4/10 | **Mentions légales incohérentes** (SIRET personnel, hébergeur OVH alors qu'on est sur Netlify, pas de mention SELARL) |
| Core Web Vitals | non mesuré | Lighthouse non exécutable depuis ce shell |
| Images / médias | 6/10 | Alt OK, mais peu de pages utilisent des images, lazy loading partiel |

### Top 10 actions classées par impact / effort

1. **[HAUT IMPACT / FAIBLE EFFORT]** Réécrire `mentions-legales.html` avec la vraie entité juridique (SELARL/SELAS Chiche Cohen) + Netlify comme hébergeur — *bloquant légal* — **Phase 2.1**
2. **[HAUT/FAIBLE]** Corriger les 4 occurrences déontologiques ❌ identifiées en 1.3 — *bloquant RIN* — **Phase 2.2**
3. **[HAUT/MOYEN]** Ajouter des liens internes contextuels depuis `index.html` et les 4 pages domaines vers les 6 pages géo (sortir ces pages de l'orphelinat) — **Phase 3.1 / 6.2**
4. **[HAUT/MOYEN]** Raccourcir les 17 titles trop longs et les 13 descriptions trop longues — **Phase 3.4**
5. **[MOYEN/FAIBLE]** Ajouter meta description sur `mentions-legales` et `guide-5-erreurs`, canonical sur `guide-5-erreurs` — **Phase 3.4**
6. **[MOYEN/MOYEN]** Créer la page hub `/avocat-dommage-corporel-marseille` annoncée au brief — **Phase 3.1**
7. **[MOYEN/MOYEN]** Mutualiser le schema `Organization` (1 seul global au lieu de 19 doublons) et ajouter `Attorney` pour les 6 avocats — **Phase 3.2**
8. **[MOYEN/FAIBLE]** Ajouter breadcrumbs visuels dans le DOM (le schema est déjà là) — **Phase 6.3**
9. **[MOYEN/FAIBLE]** Supprimer `agressions.html` (redirection 301 déjà en place dans `_redirects`) — **Phase 2/3**
10. **[FAIBLE/FAIBLE]** Ajouter `<link rel="preload">` pour Inter + `_headers` Netlify avec cache long — **Phase 6.1**

---

## QUESTIONS BLOQUANTES POUR ILAN — avant Phase 2

1. **Stack** : on migre vers Astro / Next.js / on reste en HTML statique ? (cf. Avertissement préalable)
2. **Forme juridique** : SELARL ou SELAS Chiche Cohen & Associés ? Quels sont le SIRET, RCS, n° TVA, RCP, médiateur ?
3. **Hébergeur réel** : Netlify confirmé (les mentions actuelles parlent d'OVH — héritage WordPress ?) ?
4. **Témoignages clients** : le consentement écrit existe-t-il pour chaque témoignage présent sur `index.html` ? Si oui, on ajoute juste le disclaimer. Sinon, anonymiser et neutraliser.
5. **Chiffres factuels** : la mention « 15 000+ victimes défendues » (présente dans l'OG description de `index.html`) est-elle bien le cumul historique de la SELARL ? Source consultable ?
6. **Équipe complète** : confirmation des 6 avocats à modéliser en `Attorney` schema → Patrice Chiche, Stéphane Cohen, Ilan Guedj, Daniel Amar, [prénom] Carosso, [prénom] Walas. Date d'inscription au barreau et n° toque de chacun ?
7. **Page hub `/avocat-dommage-corporel-marseille`** : à créer ex-nihilo ou enrichir une page existante ? (Je recommande une nouvelle URL distincte de l'accueil pour ne pas diluer l'autorité de la home.)

---

**Fin du rapport.** En attente de validation pour démarrer la Phase 2.
