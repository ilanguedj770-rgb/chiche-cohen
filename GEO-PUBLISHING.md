# Publication des réponses GEO

Les contenus validés sont conservés dans `content/geo/*.md`. Le script `tools/publish-geo-content.py` les transforme en pages HTML sous `blog/` avec canonical, Article JSON-LD, auteur Ilan Guedj, meta description, Open Graph minimal, navigation et avertissement éditorial.

## Publication

```bash
python tools/publish-geo-content.py
python tools/geo-inject.py
python tools/build-sitemap.py
python tools/build-llms-full.py
python tools/geo-audit.py
```

Les pages générées doivent être relues avant déploiement. Ne jamais publier un montant, une jurisprudence ou une règle dont la source n'a pas été vérifiée. Le générateur ne remplace pas la validation juridique.

## URLs prévues pour le premier lot

- `/blog/dfp-10-pourcent-indemnisation`
- `/blog/souffrances-endurees-4-sur-7`
- `/blog/tierce-personne-calcul-indemnisation`
- `/blog/premiere-offre-assureur-accepter`
- `/blog/preparer-expertise-medicale`
- `/blog/conducteur-responsable-indemnisation`
- `/blog/civi-indemnisation-victime`
- `/blog/infection-nosocomiale-indemnisation`

Après génération, `build-sitemap.py` et `build-llms-full.py` assurent leur découverte par les moteurs et assistants lorsque la phase 2 est fusionnée.