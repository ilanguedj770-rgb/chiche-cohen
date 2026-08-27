#!/usr/bin/env python3
"""Publie content/geo/*.md sous l'identité éditoriale unique Maître Ilan Guedj."""
from pathlib import Path
from datetime import date
import html,re,json
ROOT=Path(__file__).resolve().parents[1]; SRC=ROOT/'content'/'geo'; OUT=ROOT/'blog'; PERSON='https://ig-avocat.com/#ilan-guedj'
def md_body(s):
 out=[]; in_ul=False
 for line in s.splitlines():
  x=line.strip()
  if x.startswith('<div') or x.startswith('</div>'):out.append(x);continue
  if x.startswith('### '):out.append('<h3>'+html.escape(x[4:])+'</h3>');continue
  if x.startswith('## '):out.append('<h2>'+html.escape(x[3:])+'</h2>');continue
  if x.startswith('# '):out.append('<h1>'+html.escape(x[2:])+'</h1>');continue
  if x.startswith('- '):
   if not in_ul:out.append('<ul>');in_ul=True
   out.append('<li>'+html.escape(x[2:])+'</li>');continue
  if in_ul:out.append('</ul>');in_ul=False
  if x:out.append('<p>'+re.sub(r'\[([^]]+)\]\((https?://[^)]+)\)',r'<a href="\2" rel="nofollow noopener">\1</a>',html.escape(x))+'</p>')
 if in_ul:out.append('</ul>')
 return '\n'.join(out)
def publish(p):
 raw=p.read_text(encoding='utf-8');title=next((x[2:].strip() for x in raw.splitlines() if x.startswith('# ')),p.stem);desc=next((re.sub('<[^>]+>','',x).strip() for x in raw.splitlines() if len(re.sub('<[^>]+>','',x).strip())>90 and not x.startswith('#')),title);slug=p.stem;url=f'https://ig-avocat.com/blog/{slug}';today=date.today().isoformat()
 schema={"@context":"https://schema.org","@type":"Article","headline":title,"description":desc[:300],"datePublished":today,"dateModified":today,"author":{"@id":PERSON},"publisher":{"@id":PERSON},"mainEntityOfPage":url,"inLanguage":"fr-FR"}
 page=f'''<!DOCTYPE html><html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)} | Maître Ilan Guedj</title><meta name="description" content="{html.escape(desc[:155])}"><link rel="canonical" href="{url}"><link rel="author" href="/avocat-ilan-guedj"><link rel="alternate" type="text/markdown" href="/llms.txt"><meta property="og:type" content="article"><meta property="og:title" content="{html.escape(title)}"><meta property="og:url" content="{url}"><link rel="stylesheet" href="../css/tailwind.css"><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False)}</script></head><body><header><nav aria-label="Navigation principale"><a href="/">Accueil</a> · <a href="/blog/">Guides</a> · <a href="/avocat-ilan-guedj">Maître Ilan Guedj</a></nav></header><main><article>{md_body(raw)}<footer><p>Article rédigé sous la responsabilité de <a rel="author" href="/avocat-ilan-guedj">Maître Ilan Guedj</a>, avocat en dommage corporel. Information générale : chaque indemnisation dépend du dossier.</p></footer></article></main></body></html>''';(OUT/(slug+'.html')).write_text(page,encoding='utf-8')
if __name__=='__main__':
 for p in sorted(SRC.glob('*.md')):publish(p)
 print('Pages GEO publiées :',len(list(SRC.glob('*.md'))))