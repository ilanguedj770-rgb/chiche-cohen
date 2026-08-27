#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Injecte un graphe schema.org centré exclusivement sur Maître Ilan Guedj."""
import json, os, re, sys
from datetime import date
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SITE="https://ig-avocat.com"
PERSON_ID=f"{SITE}/#ilan-guedj"; PRACTICE_ID=f"{SITE}/#practice"; WEBSITE_ID=f"{SITE}/#website"
START="<!-- GEO:ENTITY-GRAPH:START -->"; END="<!-- GEO:ENTITY-GRAPH:END -->"; LAST_MODIFIED=os.environ.get("GEO_DATE",date.today().isoformat())
ADDRESS={"@type":"PostalAddress","streetAddress":"16 rue Breteuil","addressLocality":"Marseille","postalCode":"13001","addressCountry":"FR"}
BARREAU={"@type":"Organization","name":"Barreau de Marseille","url":"https://www.barreau-marseille.avocat.fr/"}
KNOWS=["Droit du dommage corporel","Indemnisation des victimes","Accident de la circulation","Loi Badinter","Erreur médicale","ONIAM","CCI","Agression","CIVI","FGTI","Nomenclature Dintilhac","Expertise médicale","Tierce personne","Incidence professionnelle"]
def person(): return {"@type":"Person","@id":PERSON_ID,"name":"Ilan Guedj","alternateName":["Maître Ilan Guedj","Me Ilan Guedj"],"honorificPrefix":"Maître","jobTitle":"Avocat au barreau de Marseille — dommage corporel","description":"Maître Ilan Guedj est avocat au barreau de Marseille. Son activité est consacrée à la défense et à l'indemnisation des victimes de dommages corporels.","url":f"{SITE}/avocat-ilan-guedj","image":f"{SITE}/img/associe-guedj.jpg","memberOf":BARREAU,"worksFor":{"@id":PRACTICE_ID},"address":ADDRESS,"telephone":"+33663465984","email":"contact@ig-avocat.com","knowsAbout":KNOWS,"sameAs":["https://consultation.avocat.fr/avocat-marseille/ilan-guedj-53358.html","https://predictice.com/cabinet/cabinet-ilan-guedj-922092382"]}
def practice(): return {"@type":["Attorney","LegalService"],"@id":PRACTICE_ID,"name":"Maître Ilan Guedj — Avocat en dommage corporel","alternateName":["Cabinet Ilan Guedj","Ilan Guedj Avocat"],"url":f"{SITE}/","employee":{"@id":PERSON_ID},"telephone":"+33663465984","email":"contact@ig-avocat.com","address":ADDRESS,"areaServed":"FR","knowsAbout":KNOWS,"memberOf":BARREAU}
def website(): return {"@type":"WebSite","@id":WEBSITE_ID,"url":f"{SITE}/","name":"Maître Ilan Guedj — Avocat dommage corporel","publisher":{"@id":PERSON_ID},"about":{"@id":PERSON_ID},"copyrightHolder":{"@id":PERSON_ID},"inLanguage":"fr-FR"}
def get(p,t):
 m=re.search(p,t,re.S|re.I); return m.group(1).strip() if m else ""
def process(path):
 rel=os.path.relpath(path,ROOT).replace(os.sep,"/"); src=open(path,encoding="utf-8").read(); original=src; canonical=get(r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"',src)
 if not canonical:return False
 page={"@type":"WebPage","@id":canonical+"#webpage","url":canonical,"name":get(r'<title>(.*?)</title>',src),"isPartOf":{"@id":WEBSITE_ID},"about":{"@id":PERSON_ID},"publisher":{"@id":PERSON_ID},"reviewedBy":{"@id":PERSON_ID},"inLanguage":"fr-FR","dateModified":LAST_MODIFIED}
 if rel.startswith('blog/'):page['author']={"@id":PERSON_ID}
 block=f'{START}\n<script type="application/ld+json">\n{json.dumps({"@context":"https://schema.org","@graph":[website(),practice(),person(),page]},ensure_ascii=False,indent=2)}\n</script>\n{END}\n'
 if START in src:src=re.sub(re.escape(START)+r'.*?'+re.escape(END)+r'\n?',block,src,flags=re.S)
 else:src=src.replace('</head>',block+'</head>',1)
 if src!=original:open(path,'w',encoding='utf-8').write(src);return True
 return False
def main():
 files=[os.path.join(ROOT,f) for f in os.listdir(ROOT) if f.endswith('.html')]; blog=os.path.join(ROOT,'blog')
 if os.path.isdir(blog):files += [os.path.join(blog,f) for f in os.listdir(blog) if f.endswith('.html')]
 if '--check' in sys.argv:
  bad=[os.path.relpath(f,ROOT) for f in files if re.search(r'Chiche\s+Cohen|CHICHE\s+COHEN',open(f,encoding='utf-8').read(),re.I)];print('Références legacy restantes:',len(bad));[print(' -',x) for x in bad];return 1 if bad else 0
 print('Pages GEO mises à jour:',sum(process(f) for f in files));return 0
if __name__=='__main__':raise SystemExit(main())