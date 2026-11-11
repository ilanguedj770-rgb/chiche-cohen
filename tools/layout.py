#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Navigation et pied de page communs à tout le site — ig-avocat.com.

Script idempotent : la barre de navigation (<nav id="navbar">) et le pied de page
(<footer>) de chaque page sont remplacés par les gabarits ci-dessous, encadrés par
<!-- LAYOUT:NAV:START/END --> et <!-- LAYOUT:FOOTER:START/END -->.
Les blocs CTA (cookies) restent gérés par tools/cta-inject.py : le marqueur
CTA:FOOTER-COOKIES est repris tel quel dans le pied de page.

Usage : python3 tools/layout.py   (puis npm run build:css)
Liens toujours absolus (« /contact ») : les mêmes gabarits servent au blog.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

TEL = "tel:+33663465984"
WA = "https://wa.me/33663465984"
MAIL = "contact@ig-avocat.com"

NAV_LINKS = [
    ("/#expertises", "Domaines", "__domaines__"),
    ("/honoraires", "Honoraires", "honoraires"),
    ("/avocat-ilan-guedj", "L'avocat", "avocat-ilan-guedj"),
    ("/blog/", "Guides", "blog"),
    ("/contact", "Contact", "contact"),
]

DOMAINES = [
    ("/accidents-route", "Accident de la route"),
    ("/accident-moto-marseille", "Accident de moto"),
    ("/pieton-cycliste-marseille", "Piéton et cycliste"),
    ("/erreur-medicale", "Erreur médicale"),
    ("/agression", "Agression"),
    ("/accidents-vie", "Accident de la vie"),
]
VILLES = [
    ("/avocat-dommage-corporel-bouches-du-rhone", "Marseille et Bouches-du-Rhône"),
    ("/avocat-aix-en-provence", "Aix-en-Provence"),
    ("/avocat-toulon", "Toulon"),
    ("/avocat-nice", "Nice"),
    ("/avocat-avignon", "Avignon"),
    ("/avocat-nimes", "Nîmes"),
    ("/avocat-montpellier", "Montpellier"),
]
RESSOURCES = [
    ("/dossier-en-ligne", "Ouvrir son dossier en ligne"),
    ("/honoraires", "Honoraires"),
    ("/blog/", "Guides pour les victimes"),
    ("/blog/simulateur-dfp-capitalisation", "Simulateur d'indemnisation"),
    ("/lexique-dommage-corporel", "Lexique"),
    ("/avocat-ilan-guedj", "Maître Ilan Guedj"),
    ("/contact", "Contact"),
    ("/mentions-legales", "Mentions légales"),
]

I_PHONE = ('<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 '
           '19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 '
           '1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 '
           '12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
I_ARROW = ('<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14"/><path d="m12 5 7 7-7 7"/></svg>')
I_SEARCH = ('<svg class="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>')
I_X = ('<svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.244 2.25h3.308l-7.227 '
       '8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>')
I_IN = ('<svg class="w-[18px] h-[18px]" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.447 20.452h-3.554v-5.569c0-1.328'
        '-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 '
        '2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 1 1 0-4.124 2.062 2.062 0 0 1 0 4.124zM7.119 20.452H3.555V9h3.564v11.452z"/></svg>')
I_MENU = ('<svg class="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" '
          'aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg>')


def slug_of(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("blog/"):
        return "blog"
    return rel[:-5]


def nav(slug: str) -> str:
    def lien(href, label, s):
        actif = s is not None and s == slug
        cls = "text-gray-900" if actif else "text-gray-500 hover:text-gray-900"
        cur = ' aria-current="page"' if actif else ""
        # Le lien « Domaines » devient un menu déroulant côté navigateur (js/ig-ui.js).
        extra = " data-ig-domaines" if s == "__domaines__" else ""
        return f'<a href="{href}" class="text-[15px] font-semibold {cls} transition"{cur}{extra}>{label}</a>'

    desk = "\n                ".join(lien(*l) for l in NAV_LINKS)
    mob = "\n        ".join(
        f'<a href="{h}" class="block py-3.5 text-lg font-semibold text-gray-800 border-b border-gray-100">{t}</a>'
        for h, t, _ in NAV_LINKS)
    return f'''<!-- LAYOUT:NAV:START --><nav id="navbar" class="fixed w-full z-50 bg-white/90 backdrop-blur-xl border-b border-gray-100 transition-all duration-300" aria-label="Navigation principale">
    <div class="max-w-7xl mx-auto px-5 lg:px-8">
        <div class="flex justify-between items-center h-20">
            <a href="/" class="flex-shrink-0 group" aria-label="Maître Ilan Guedj, accueil">
                <span class="font-display text-2xl font-bold tracking-tight uppercase text-gray-900 group-hover:opacity-80 transition">ILAN GUEDJ<span class="text-blue-600">.</span></span>
            </a>
            <div class="hidden lg:flex items-center gap-8">
                {desk}
            </div>
            <div class="hidden lg:flex items-center gap-5">
                <button type="button" data-ig-search class="p-2 -mr-2 text-gray-500 hover:text-gray-900 transition" aria-label="Rechercher dans le site" title="Rechercher (touche /)">{I_SEARCH}</button>
                <a href="{TEL}" class="inline-flex items-center gap-2 text-[15px] font-semibold text-gray-900 hover:text-blue-600 transition">{I_PHONE}06 63 46 59 84</a>
                <a href="/dossier-en-ligne" data-cta="nav_dossier" class="inline-flex items-center gap-2 bg-gray-900 text-white px-5 py-3 rounded-full text-sm font-bold hover:bg-gray-800 transition">Ouvrir mon dossier{I_ARROW}</a>
            </div>
            <div class="lg:hidden flex items-center gap-1">
                <button type="button" data-ig-search class="p-3 text-gray-900" aria-label="Rechercher dans le site">{I_SEARCH.replace("w-5 h-5", "w-6 h-6")}</button>
                <a href="{TEL}" class="p-3 text-gray-900" aria-label="Appeler le 06 63 46 59 84">{I_PHONE.replace("w-4 h-4", "w-6 h-6")}</a>
                <button id="mobile-menu-btn" class="text-gray-900 p-3 -mr-3" aria-label="Ouvrir le menu" aria-controls="mobile-menu" aria-expanded="false">{I_MENU}</button>
            </div>
        </div>
    </div>
    <div id="mobile-menu" class="hidden lg:hidden bg-paper border-b border-gray-100 absolute w-full px-6 pb-6 pt-2 shadow-xl">
        {mob}
        <a href="/dossier-en-ligne" data-cta="nav_dossier" class="mt-5 flex items-center justify-center gap-2 bg-gray-900 text-white py-4 rounded-full font-bold">Ouvrir mon dossier en ligne{I_ARROW}</a>
        <div class="mt-3 grid grid-cols-2 gap-3">
            <a href="{TEL}" class="flex items-center justify-center gap-2 py-3.5 rounded-full border border-gray-300 font-bold text-gray-900">{I_PHONE}Appeler</a>
            <a href="{WA}" class="flex items-center justify-center py-3.5 rounded-full bg-[#25D366] text-white font-bold">WhatsApp</a>
        </div>
    </div>
</nav><!-- LAYOUT:NAV:END -->'''


def colonne(titre, liens):
    items = "".join(f'<li><a href="{h}" class="hover:text-white transition">{t}</a></li>' for h, t in liens)
    return (f'<div><p class="text-sm font-bold uppercase tracking-wider text-gray-400">{titre}</p>'
            f'<ul class="mt-4 space-y-2.5 text-[15px] text-gray-300">{items}</ul></div>')


def footer(cookies: str) -> str:
    return f'''<!-- LAYOUT:FOOTER:START --><footer class="bg-ink text-white pt-16 pb-36 md:pb-16 border-t border-gray-900">
        <div class="max-w-7xl mx-auto px-6 lg:px-8">
            <div class="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-5 lg:gap-12">
                <div class="col-span-2">
                    <p class="font-display font-bold text-3xl tracking-tight">ILAN GUEDJ<span class="text-blue-300">.</span></p>
                    <p class="mt-4 max-w-sm text-gray-300 leading-relaxed">Avocat au barreau de Marseille. Activité exclusivement consacrée à l'indemnisation des victimes de dommage corporel. Jamais pour une compagnie d'assurance.</p>
                    <address class="not-italic mt-6 space-y-2 text-[15px] text-gray-300">
                        <p><a href="{TEL}" class="font-bold text-white hover:text-blue-300 transition">06 63 46 59 84</a></p>
                        <p><a href="mailto:{MAIL}" class="hover:text-white transition">{MAIL}</a></p>
                        <p><a href="https://www.google.com/maps/search/?api=1&amp;query=16+rue+Breteuil+13001+Marseille" target="_blank" rel="noopener" class="hover:text-white transition">16 rue Breteuil, 13001 Marseille</a></p>
                        <p class="text-gray-400">Lundi au jeudi 9 h – 19 h, vendredi 9 h – 17 h</p>
                    </address>
                    <p class="mt-5 flex items-center gap-2">
                        <a href="https://x.com/Guedj_" target="_blank" rel="noopener me" aria-label="Maître Ilan Guedj sur X" class="inline-flex items-center justify-center w-10 h-10 rounded-full border border-white/10 text-gray-300 hover:text-white hover:border-white/40 transition">{I_X}</a>
                        <a href="https://www.linkedin.com/in/ilan-guedj/" target="_blank" rel="noopener me" aria-label="Maître Ilan Guedj sur LinkedIn" class="inline-flex items-center justify-center w-10 h-10 rounded-full border border-white/10 text-gray-300 hover:text-white hover:border-white/40 transition">{I_IN}</a>
                    </p>
                    <a href="/dossier-en-ligne" data-cta="footer_dossier" class="mt-7 inline-flex items-center gap-2 bg-white text-gray-900 px-5 py-3 rounded-full text-sm font-bold hover:bg-gray-100 transition">Ouvrir mon dossier en ligne{I_ARROW}</a>
                </div>
                {colonne("Domaines", DOMAINES)}
                {colonne("Où j'interviens", VILLES)}
                {colonne("Ressources", RESSOURCES)}
            </div>
            <div class="mt-14 pt-8 border-t border-white/10 flex flex-col md:flex-row md:justify-between gap-3 text-sm text-gray-400">
                <p>© 2026 Maître Ilan Guedj, avocat au barreau de Marseille. Intervention dans toute la France.</p>
                <p><a href="/llms.txt" class="hover:text-white transition">Version pour les assistants IA</a></p>
            </div>
        </div>
    {cookies}</footer><!-- LAYOUT:FOOTER:END -->'''


# Bloc commun du <head> : icônes, couleur de thème, préchargement des pages au
# survol (Speculation Rules) et interface commune. Idempotent via ses marqueurs.
HEAD = '''<!-- LAYOUT:HEAD:START -->
    <meta name="theme-color" content="#FAF7F2">
    <link rel="manifest" href="/site.webmanifest">
    <link rel="apple-touch-icon" href="/img/apple-touch-icon.png">
    <script type="speculationrules">{"prefetch":[{"where":{"and":[{"href_matches":"/*"},{"not":{"href_matches":"/*.pdf"}},{"not":{"selector_matches":"[rel~=nofollow],[target=_blank],[download]"}}]},"eagerness":"moderate"}]}</script>
    <script src="/js/ig-ui.js" defer></script>
    <!-- LAYOUT:HEAD:END -->'''
HEAD_RE = re.compile(r"[ \t]*<!-- LAYOUT:HEAD:START -->.*?<!-- LAYOUT:HEAD:END -->\n?", re.S)
# Calendly est chargé à la demande par js/ig-tracking.js : plus de feuille de
# style ni de script tiers bloquants dans le <head>.
CALENDLY_RE = re.compile(r"[ \t]*(?:<!-- Calendly[^>]*-->\s*)?<(?:link|script)[^>]+assets\.calendly\.com[^>]*>(?:</script>)?\n?", re.I)
MAIN_OPEN = '<main id="contenu">'


def head(s: str) -> str:
    s = HEAD_RE.sub("", s)
    s = CALENDLY_RE.sub("", s)
    return s.replace("</head>", "    " + HEAD + "\n</head>", 1)


def main_landmark(s: str) -> str:
    """Un seul repère <main> par page, entre la navigation et le pied de page."""
    if re.search(r"<main\b", s):
        if 'id="contenu"' not in s:
            s = re.sub(r"<main\b(?![^>]*\bid=)", '<main id="contenu"', s, count=1)
        return s
    a, b = "<!-- LAYOUT:NAV:END -->", "<!-- LAYOUT:FOOTER:START -->"
    if a in s and b in s:
        s = s.replace(a, a + "\n" + MAIN_OPEN, 1).replace(b, "</main>\n" + b, 1)
    return s


COOKIES_RE = re.compile(r"<!-- CTA:FOOTER-COOKIES:START -->.*?<!-- CTA:FOOTER-COOKIES:END -->", re.S)
DEFAULT_COOKIES = ('<!-- CTA:FOOTER-COOKIES:START --><p class="mt-10 text-center text-xs text-gray-500"><a href="/mentions-legales#cookies" '
                   'data-consent-open class="underline hover:text-white">Gestion des cookies</a></p><!-- CTA:FOOTER-COOKIES:END -->')


def apply(path: Path) -> bool:
    s = path.read_text(encoding="utf-8")
    avant = s
    slug = slug_of(path)
    # Navigation
    if "<!-- LAYOUT:NAV:START -->" in s:
        s = re.sub(r"<!-- LAYOUT:NAV:START -->.*?<!-- LAYOUT:NAV:END -->", lambda m: nav(slug), s, count=1, flags=re.S)
    else:
        m = re.search(r'<nav id="navbar".*?</nav>', s, re.S)
        if not m:
            return False
        s = s[:m.start()] + nav(slug) + s[m.end():]
    # Pied de page
    m = re.search(r"<!-- LAYOUT:FOOTER:START -->.*?<!-- LAYOUT:FOOTER:END -->", s, re.S) or re.search(r"<footer\b.*?</footer>", s, re.S)
    if m:
        c = COOKIES_RE.search(m.group(0))
        s = s[:m.start()] + footer(c.group(0) if c else DEFAULT_COOKIES) + s[m.end():]
    s = main_landmark(head(s))
    # Les anciens appels directs à Calendly passent par le chargement à la demande.
    s = re.sub(r"""onclick="Calendly\.initPopupWidget\(\{url: 'https://calendly\.com/guedj-chiche-cohen'\}\);""", 'data-calendly onclick="', s)
    s = s.replace(' onclick="return false;"', "")
    # Le bouton du menu mobile indique son état aux lecteurs d'écran.
    s = s.replace("menu.classList.toggle('hidden');", "menu.classList.toggle('hidden'); btn.setAttribute('aria-expanded', String(!menu.classList.contains('hidden')));")
    if s != avant:
        path.write_text(s, encoding="utf-8")
    return True


def main():
    pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "blog").glob("*.html"))
    faits, ignores = 0, []
    for p in pages:
        if apply(p):
            faits += 1
        else:
            ignores.append(p.name)
    print(f"layout: {faits} pages, sans navigation standard : {ignores}")


if __name__ == "__main__":
    main()
