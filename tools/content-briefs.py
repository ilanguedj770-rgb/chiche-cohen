#!/usr/bin/env python3
"""Genere des briefs editoriaux source-first depuis GEO-CONTENT-PLAN-100.md.
Le script ne publie jamais automatiquement de texte juridique.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'GEO-CONTENT-PLAN-100.md'; OUT=ROOT/'content-briefs'
text=SRC.read_text(encoding='utf-8'); OUT.mkdir(exist_ok=True)
questions=re.findall(r'^\d+\. (.+?)$',text,re.M)
def slug(s):
 import unicodedata
 s=unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower()
 return re.sub(r'[^a-z0-9]+','-',s).strip('-')
for q in questions:
 p=OUT/(slug(q)+'.md')
 if p.exists(): continue
 p.write_text(f'''# {q}\n\n## Intention\nRépondre précisément à : « {q} » sans transformer un référentiel indicatif en barème obligatoire et sans promettre un résultat.\n\n## Réponse essentielle\nÀ rédiger après vérification des sources primaires. 80 à 150 mots, autonome, nuancée et directement citable.\n\n## Points à traiter\n- Règle applicable et champ d'application.\n- Conditions et exceptions.\n- Conséquences pratiques pour la victime.\n- Procédure et pièces utiles si pertinent.\n- Exemple pédagogique uniquement s'il est juridiquement sûr.\n\n## Sources obligatoires avant publication\n- Légifrance : texte ou jurisprudence directement applicable.\n- Source institutionnelle compétente selon le sujet (Cour de cassation, Service-Public, ONIAM, Fonds de garantie).\n- Toute donnée chiffrée doit avoir une source, une date et un périmètre.\n\n## Maillage\nAjouter 3 à 6 liens vers les pages du même cluster et un lien vers /avocat-ilan-guedj lorsque pertinent.\n\n## QA\n- [ ] Canonical\n- [ ] H1 unique\n- [ ] .geo-answer\n- [ ] Auteur\n- [ ] dateModified réelle\n- [ ] Sources primaires\n- [ ] Pas de chiffre non sourcé\n- [ ] Pas de promesse de résultat\n- [ ] Liens internes\n''',encoding='utf-8')
print(len(questions),'briefs disponibles dans',OUT)
