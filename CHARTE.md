# Charte visuelle du site

Registre recherché : **chaleureux et humain**, du côté de la victime plutôt que
de l'institution. Papier sable, encre bleu-nuit, un bleu profond et une touche
de cuivre. Titres en serif, texte en sans, formes généreuses, ombres diffuses.

## Où vivent les décisions

| Quoi | Où |
|---|---|
| Palette, typographies, rayons, ombres | `tailwind.config.js` |
| Fonds de page, titres, focus, reprises sur fond sombre | `css/input.css` |
| Feuille livrée (générée, ne pas éditer) | `css/tailwind.css` |
| Polices auto-hébergées | `fonts/` |
| Image de partage | `tools/build-og-image.py` → `img/og-cover.jpg` |

Les échelles `gray`, `blue`, `green`… de Tailwind sont **redéfinies**, pas
complétées : les classes déjà posées dans les pages (`text-gray-500`,
`bg-blue-600`…) adoptent la charte sans réécriture du HTML. Une couleur ajoutée
au site passe donc par la config, jamais par une valeur en dur dans une page.

## Reconstruire

```bash
npm ci
npm run build:css          # css/input.css -> css/tailwind.css
python3 tools/build-og-image.py   # image de partage (nécessite Playwright)
```

La CI vérifie que `css/tailwind.css` correspond bien à sa source : toute
modification de la palette ou de `css/input.css` doit être recompilée et
commitée.

## Repères

- **Papier** `#FDFBF8` pour les sections claires, **sable** `#FAF7F2` pour le
  fond de page, **sable profond** `#F4EFE5` pour les sections alternées.
  Les cartes restent en blanc pur pour se détacher.
- **Encre** `#1B2430` pour les bandes sombres (classe `bg-ink`) et les titres.
- **Bleu** `#1E40AF` en accent principal, **cuivre** `#B45309` en accent
  secondaire (filets, petites accroches).
- **Titres** en Fraunces : appliqué automatiquement à `h1`, `h2`, `h3` et à la
  classe `font-display`. Inutile de le déclarer dans les pages.
- **Graisses** : `font-black` et `font-extrabold` sont plafonnées à 700 — une
  serif ne se porte pas en 900.
- Les titres **héritent** de la couleur de leur contexte. Sur un bloc sombre
  (`bg-ink`, `bg-gray-900`, `bg-black`), le texte sans classe de couleur passe
  automatiquement en clair.

## Règles à tenir

- Pas d'emoji en guise d'icône : SVG inline (tracés Lucide, licence ISC). Le site
  ne charge aucune bibliothèque d'icônes — les tracés sont posés dans le HTML.
- Pas de dépendance tierce au premier rendu : polices et icônes sont servies
  par le site.
- Tout bloc animé au défilement doit rester lisible sans animation — la
  préférence « mouvement réduit » du système est respectée.
- Contraste : viser 4,5:1 sur le texte courant. Les gris de la charte sont
  calibrés pour le papier ; sur l'encre, `css/input.css` les remonte.
