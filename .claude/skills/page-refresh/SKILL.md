---
name: page-refresh
description: À utiliser quand on demande de rafraîchir une page d'ig-avocat.com, ou quelles pages perdent des clics.
---
1. Récupérer dans Search Console (`sc-domain:ig-avocat.com`) les 90 derniers jours et les 90 précédents pour la page : clics, impressions, CTR, position, par requête. Sources possibles : MCP `gsc` (voir `SETUP-GSC-MCP.md`), Windsor.ai, ou l'interface Search Console dans le navigateur. Sans donnée, s'arrêter et le dire.
2. Lister les requêtes qui perdent des clics, et celles qui ont des impressions sans clic (position 4 à 20 en priorité).
3. Lire `seo/pages/<page>.md` ou le cluster de `seo/keywords/`, et les règles de `.claude/rules/` avant de changer quoi que ce soit.
4. Proposer les modifications : nouvelles sections ou FAQ pour les requêtes manquantes (en réutilisant `content/geo/` quand une réponse existe), liens internes depuis les pages du cluster ; title et meta seulement si le CTR est sous la moyenne du site pour cette position. Ne jamais toucher l'URL.
5. Après accord : appliquer, lancer `python3 tools/geo-build.py`, `python3 tools/geo-audit.py` (0 erreur) et `python3 tools/check-internal-links.py`.
6. Consigner la modification et la date dans `seo/decisions.md` et mettre à jour la fiche de la page (chiffres 90 j, date).
