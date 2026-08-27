#!/usr/bin/env python3
"""Publie les fiches content/geo/*.md en pages HTML indexables sous blog/.
Le markdown attendu utilise #, ##, paragraphes, listes et une div .geo-answer deja validee.
"""
from pathlib import Path
from datetime import date
import html,re,json
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'content'/'geo'; OUT=ROOT/'blog'
AUTHOR='https://ig-avocat.com/#ilan-guedj'

def md_body(s):
 lines=s.splitlines(); out=[]; in_ul=False
 for line in lines:
  x=line.strip()
  if x.startswith('<div') or x.startswith('</div>'): out.append(x); continue
  if x.startswith('### '): out.append('<h3>'+html.escape(x[4:])+'</h3>'); continue
  if x.startswith('## '): out.append('<h2>'+html.escape(x[3:])+'</h2>'); continue
  if x.startswith('# '): out.append('<h1>'+html.escape(x[2:])+'</h1>'); continue
  if x.startswith('- '):
   if not in_ul: out.append('<ul>'); in_ul=True
   out.append('<li>'+html.escape(x[2:])+'</li>'); continue
  if in_ul: out.append('</ul>'); in_ul=False
  if x: out.append('<p>'+re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<a href="\2" rel="nofollow noopener">\1</a>',html.escape(x))+'</p>')
 if in_ul: out.append('</ul>')
 return '\n'.join(out)

def publish(p):
 raw=p.read_text(encoding='utf-8'); title=next((x[2:].strip() for x in raw.splitlines() if x.startswith('# ')),p.stem)
 desc=next((re.sub('<[^>]+>','',x).strip() for x in raw.splitlines() if len(re.sub('<[^>]+>','',x).strip())>90 and not x.startswith('#')),title)
 slug=p.stem; url=f'https://ig-avocat.com/blog/{slug}'; today=date.today().isoformat()
 schema={"@context":"https://schema.org","@type":"Article","headline":title,"description":desc[:300],"datePublished":today,"dateModified":today,"author":{"@id":AUTHOR},"publisher":{"@id":"https://ig-avocat.com/#cabinet"},"mainEntityOfPage":url,"inLanguage":"fr-FR"}
 page=f'''<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | Ilan Guedj</title><meta name="description" content="{html.escape(desc[:155])}"><link rel="canonical" href="{url}"><link rel="author" href="https://ig-avocat.com/avocat-ilan-guedj"><link rel="alternate" type="text/markdown" href="/llms.txt"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title)}"><meta property="og:url" content="{url}"><meta property="og:image" content="https://ig-avocat.com/img/og-cover.jpg"><link rel="stylesheet" href="../css/tailwind.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><header><nav aria-label="Navigation principale"><a href="/">Accueil</a> · <a href="/blog/">Blog</a> · <a href="/avocat-ilan-guedj">Maître Ilan Guedj</a></nav></header><main><article>{md_body(raw)}<footer><p>Article rédigé sous la responsabilité de <a rel="author" href="/avocat-ilan-guedj">Maître Ilan Guedj</a>. Information générale : l'indemnisation dépend des faits, des pièces et du droit applicable à chaque dossier.</p><p><a href="/blog/">Voir tous les guides juridiques</a></p></footer></article></main></body></html>'''
 (OUT/(slug+'.html')).write_text(page,encoding='utf-8')

if __name__=='__main__':
 for p in sorted(SRC.glob('*.md')): publish(p)
 print('Pages GEO publiées :',len(list(SRC.glob('*.md'))))
