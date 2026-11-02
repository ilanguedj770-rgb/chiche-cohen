---
paths:
  - "blog/**"
  - "content/geo/**"
  - "*.html"
---
# Pages et contenus juridiques

- Avant de créer une page : lire `seo/keywords/` et vérifier qu'aucune page ne couvre déjà l'intention. Une page = une intention = un H1.
- Réponse essentielle autonome en tête de page (bloc `.geo-answer`), puis détail, limites et exceptions, sources, liens vers le pivot du cluster.
- Ne jamais inventer un montant, un taux, une statistique ou une jurisprudence. Règles de droit sourcées sur Légifrance, Cour de cassation ou organismes publics ; tout identifiant LEGIARTI ouvert sur Légifrance avant publication et ajouté à `SOURCES-JURIDIQUES-VERIFIEES.md`.
- Toute page indexable : meta robots `index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1`, canonical sans `.html` ni `/` final, auteur Ilan Guedj, dates gérées par `tools/sitedates.py` (jamais à la main).
- Les réponses de `content/geo/` (120 à 150 mots) ne se publient pas une par une : on les assemble en pages pivots.
- Données d'entité (langues, sameAs) : corriger dans `tools/geo-inject.py`, pas dans la page.
- Couleurs et styles : via `tailwind.config.js` / `css/input.css`, jamais de valeur en dur ; icônes SVG inline, pas d'emoji.
- Après modification : régénérer sitemap, feed et corpus via `python3 tools/geo-build.py`, puis contrôles de CLAUDE.md, puis une ligne dans `seo/decisions.md`.
