# Backlog GEO code-first

Ce document transforme l'audit GEO en plan de production sans intervention sur chiche-cohen.avocat.fr ni sur des plateformes tierces.

## Regle de publication
Chaque nouvelle ressource doit avoir : title unique, canonical, H1 unique, reponse directe visible en HTML (`.geo-answer`), auteur Ilan Guedj lorsque pertinent, date de mise a jour reelle, sources primaires, maillage vers le pilier et ressources connexes, JSON-LD valide, sitemap et llms-full regeneres.

## Priorite 1 - postes de prejudice
- Calcul et valeur du DFP
- Souffrances endurees
- Tierce personne
- Deficit fonctionnel temporaire
- Prejudice esthetique
- Prejudice d'agrement
- Prejudice sexuel
- Incidence professionnelle
- Pertes de gains professionnels
- Frais futurs
- Referentiel Mornet : usage, limites et exemples

## Priorite 2 - expertise et procedure
- Expertise medicale : preparation
- Contester une expertise medicale
- Medecin-recours
- Expertise amiable vs judiciaire
- Provision apres accident
- Delais reels d'indemnisation
- Offre de l'assureur : accepter ou refuser

## Priorite 3 - route
- Conducteur responsable
- Accident sans tiers
- Accident moto
- Accident velo et trottinette
- Pieton renverse
- Passager victime

## Priorite 4 - CIVI / medical / travail
- CIVI : saisine
- Refus CIVI : recours
- FGTI
- CCI
- ONIAM
- Infection nosocomiale
- Alea therapeutique
- Accident du travail et dommage corporel
- Accident de trajet
- Faute inexcusable
- Traumatisme cranien

## Glossaire
Creer un glossaire HTML indexable reliant DFP, DFT, SE, ATP/tierce personne, PGPF, incidence professionnelle, prejudice d'agrement, prejudice esthetique et autres postes Dintilhac aux guides approfondis.

## Observatoire de l'indemnisation
Architecture cible : `/observatoire-indemnisation` puis pages d'etudes permanentes. Ne publier que des donnees dont le cabinet dispose licitement et dont la methodologie est reproductible.

Chaque etude doit exposer en HTML : periode, juridictions, taille d'echantillon, criteres d'inclusion/exclusion, statistiques agregees, limites, date de mise a jour et provenance des donnees. Ajouter `Dataset` uniquement lorsqu'un vrai jeu de donnees est publie et correspond a Schema.org/Dataset.

Etudes candidates : DFP, souffrances endurees, taux de tierce personne, prejudice esthetique, incidence professionnelle, evolutions annuelles et comparaisons par juridiction lorsque l'echantillon est suffisant.

## CI / controle
Executer apres chaque modification :

```bash
python3 tools/geo-inject.py
python3 tools/build-llms-full.py
python3 tools/geo-audit.py
python3 tools/geo-inject.py --check
```

Le build doit etre considere non publiable en presence d'une erreur `geo-audit`. Les avertissements doivent etre examines mais peuvent etre justifies.
