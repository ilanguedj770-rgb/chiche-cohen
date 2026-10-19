#!/usr/bin/env python3
"""Appels à l'action et suivi des contacts — ig-avocat.com.

Script idempotent : chaque bloc injecté est encadré par des marqueurs
<!-- CTA:<NOM>:START --> ... <!-- CTA:<NOM>:END --> et remplacé à chaque
exécution. Les retouches ponctuelles (attributs data-cta, barre mobile,
inclusion du script de suivi) sont protégées par des tests de présence.

Usage : py tools/cta-inject.py   (puis npm run build:css)

Ton : sobre, rassurant, sans promesse de résultat (déontologie).
Les 3 options sont toujours proposées : appeler, WhatsApp, rendez-vous
Calendly ; le formulaire reste accessible pour ceux qui préfèrent écrire.
Le suivi des clics est fait par /js/ig-tracking.js (voir TRACKING.md).
"""
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

TEL = "tel:+33663465984"
TEL_LABEL = "06 63 46 59 84"
WA = "https://wa.me/33663465984"
CAL = "https://calendly.com/guedj-chiche-cohen"
TRACKING_TAG = '<script src="/js/ig-tracking.js" defer></script>'
GTM_HEAD = ("  <!-- Google Tag Manager -->\n  <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':\n"
            "  new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],\n"
            "  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=\n"
            "  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);\n"
            "  })(window,document,'script','dataLayer','GTM-WP82S37T');</script>\n  <!-- End Google Tag Manager -->")
GTM_BODY = ('  <!-- Google Tag Manager (noscript) -->\n  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-WP82S37T"\n'
            '  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n  <!-- End Google Tag Manager (noscript) -->')

ICON_PHONE = ('<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 '
              '19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 '
              '1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 '
              '12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>')
ICON_WA = ('<svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path d="M17.472 '
           '14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347'
           '.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.13'
           '4-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207'
           '-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 '
           '2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 '
           '1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.34'
           '7m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.'
           '51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 '
           '5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.'
           '547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11'
           '.893a11.821 11.821 0 00-3.48-8.413z"/></svg>')
ICON_CAL = ('<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 2v4"/><path d="M16 2v4"/>'
            '<rect width="18" height="18" x="3" y="4" rx="2"/><path d="M3 10h18"/></svg>')
ICON_CHECK = ('<svg class="w-4 h-4 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" '
              'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 6 9 17l-5-5"/></svg>')

REASSURANCE = ["Consultation gratuite", "0&nbsp;€ d'avance de frais", "Honoraires au résultat", "Réponse rapide"]


# --------------------------------------------------------------------------
# Composants
# --------------------------------------------------------------------------
def buttons(dark=False, compact=False, center=False):
    pad = "px-5 py-3" if compact else "px-6 py-3.5"
    base = f"inline-flex items-center justify-center gap-2 {pad} rounded-full text-sm font-bold transition active:scale-95"
    if dark:
        tel = f"{base} bg-white text-gray-900 hover:bg-gray-100"
        rdv = f"{base} border border-white/30 text-white hover:bg-white/10"
    else:
        tel = f"{base} bg-gray-900 text-white hover:bg-gray-800"
        rdv = f"{base} bg-white text-gray-900 border border-gray-300 hover:border-gray-400"
    wa = f"{base} bg-[#25D366] text-white hover:bg-green-500"
    justify = " sm:justify-center" if center else ""
    return (
        f'<div class="flex flex-col sm:flex-row sm:flex-wrap gap-3{justify}">'
        f'<a href="{TEL}" class="{tel}">{ICON_PHONE}<span>Appeler le {TEL_LABEL}</span></a>'
        f'<a href="{WA}" target="_blank" rel="noopener" class="{wa}">{ICON_WA}<span>WhatsApp</span></a>'
        f'<a href="{CAL}" target="_blank" rel="noopener" data-calendly class="{rdv}">{ICON_CAL}<span>Prendre rendez-vous</span></a>'
        '</div>'
    )


def reassurance(dark=False, center=False):
    color = "text-gray-300" if dark else "text-gray-600"
    check = "text-green-400" if dark else "text-green-600"
    justify = " justify-center" if center else ""
    items = "".join(
        f'<li class="flex items-center gap-1.5"><span class="{check}">{ICON_CHECK}</span>{t}</li>' for t in REASSURANCE
    )
    return f'<ul class="mt-4 flex flex-wrap gap-x-5 gap-y-2 text-sm {color}{justify}" aria-label="Nos engagements">{items}</ul>'


def write_link(dark=False, center=False):
    color = "text-gray-400" if dark else "text-gray-500"
    link = "text-white" if dark else "text-blue-700"
    align = " text-center" if center else ""
    return (f'<p class="mt-3 text-sm {color}{align}">Vous préférez écrire&nbsp;? '
            f'<a href="/contact" class="font-semibold underline {link}">Formulaire de contact</a></p>')


def hero_block(lead, center=False):
    align = " text-center" if center else ""
    return (
        f'<div class="mt-8" data-cta="hero">'
        f'<p class="text-base font-semibold text-gray-900 mb-3{align}">{lead}</p>'
        f'{buttons(compact=True, center=center)}{reassurance(center=center)}</div>'
    )


def card(title, text, cta="milieu"):
    return (
        f'<aside class="my-12 rounded-2xl border border-blue-100 bg-blue-50/60 p-6 md:p-8" data-cta="{cta}" '
        f'aria-label="Prendre contact avec le cabinet">'
        f'<p class="text-xl font-black tracking-tight text-gray-900">{title}</p>'
        f'<p class="mt-2 mb-5 text-gray-700 leading-relaxed">{text}</p>'
        f'{buttons(compact=True)}{reassurance()}{write_link()}</aside>'
    )


def band(title, text, cta="milieu"):
    return (
        f'<section class="py-12 bg-white" data-cta="{cta}"><div class="max-w-5xl mx-auto px-6 lg:px-8">'
        + card(title, text, cta).replace(' data-cta="%s"' % cta, "").replace("my-12 ", "")
        + "</div></section>"
    )


def end_row(dark=True):
    return (f'<div data-cta="fin_de_page">{buttons(dark=dark, center=True)}'
            f'{reassurance(dark=dark, center=True)}{write_link(dark=dark, center=True)}</div>')


MOBILE_BAR = (
    '<div class="fixed bottom-6 left-4 right-4 z-50 md:hidden" data-cta="bouton_fixe_mobile">'
    '<div class="bg-ink/90 backdrop-blur-xl p-2 rounded-2xl shadow-2xl flex gap-3 border border-white/10">'
    f'<a href="{WA}" class="flex-1 bg-[#25D366] text-white py-3 rounded-xl font-bold flex justify-center items-center gap-2 text-sm active:scale-95 transition">{ICON_WA}WhatsApp</a>'
    f'<a href="{TEL}" class="flex-1 bg-white text-gray-900 py-3 rounded-xl font-bold flex justify-center items-center gap-2 text-sm active:scale-95 transition">{ICON_PHONE}Appeler</a>'
    '</div></div>'
)
MOBILE_RDV = (f'<!-- CTA:BARRE-RDV:START --><a href="{CAL}" target="_blank" rel="noopener" data-calendly '
              'class="flex-1 bg-white/10 text-white py-3 rounded-xl font-bold flex justify-center items-center gap-1.5 text-sm '
              f'active:scale-95 transition">{ICON_CAL}RDV</a><!-- CTA:BARRE-RDV:END -->')


# --------------------------------------------------------------------------
# Textes contextuels
# --------------------------------------------------------------------------
CITIES = {
    "avocat-aix-en-provence": "à Aix-en-Provence",
    "avocat-avignon": "à Avignon",
    "avocat-montpellier": "à Montpellier",
    "avocat-nice": "à Nice",
    "avocat-nimes": "à Nîmes",
    "avocat-toulon": "à Toulon",
}

SERVICES = {
    "accidents-route": ("Victime d'un accident de la route&nbsp;?",
                        "Piéton, passager, cycliste, motard ou conducteur&nbsp;: faites le point gratuitement sur le régime qui s'applique à vous et sur ce que l'assureur doit indemniser."),
    "accidents-vie": ("Chute, accident domestique, de sport ou de loisir&nbsp;?",
                      "Votre contrat Garantie des accidents de la vie mérite d'être lu en détail. Faites vérifier gratuitement l'offre ou la démarche en cours."),
    "agression": ("Victime d'une agression&nbsp;?",
                  "La CIVI et le FGTI ont leurs propres règles et leurs propres délais. Un premier échange gratuit permet d'examiner votre dossier avant toute démarche."),
    "erreur-medicale": ("Vous pensez avoir été victime d'une erreur médicale&nbsp;?",
                        "CCI, ONIAM ou tribunal&nbsp;: faites examiner gratuitement votre situation avant de choisir la procédure."),
}

BLOG = {
    "accident-bus-tramway-indemnisation": ("Blessé dans un bus, un car ou un tramway&nbsp;?", "Passager ou piéton, vos droits relèvent de la loi Badinter. Faites le point gratuitement avec un avocat qui défend uniquement les victimes."),
    "accident-delit-fuite-indemnisation": ("Le responsable a pris la fuite&nbsp;?", "Les démarches auprès du Fonds de garantie obéissent à des délais stricts. Un premier échange gratuit permet de savoir par où commencer."),
    "accident-moto-indemnisation": ("Motard blessé dans un accident&nbsp;?", "La faute qu'on vous oppose se discute, comme le chiffrage de vos préjudices. Faites examiner votre dossier gratuitement."),
    "accident-route-indemnisation": ("Victime d'un accident de la route&nbsp;?", "Piéton, passager, cycliste, motard ou conducteur&nbsp;: faites vérifier gratuitement le régime qui s'applique à vous et ce que l'assureur doit indemniser."),
    "accident-travail-faute-inexcusable": ("Blessé au travail&nbsp;?", "La rente de la Sécurité sociale ne répare pas tous les préjudices. Faites le point gratuitement sur les recours possibles."),
    "accident-trottinette-electrique-indemnisation": ("Accident de trottinette électrique&nbsp;?", "Conducteur ou piéton renversé, l'assureur à solliciter n'est pas toujours celui qu'on croit. Faites le point gratuitement sur votre situation."),
    "accident-velo-indemnisation": ("Cycliste renversé&nbsp;?", "Faites vérifier gratuitement l'offre de l'assureur ou la démarche en cours, avec un avocat qui défend uniquement les victimes."),
    "agression-victime-droits-recours": ("Victime d'une agression&nbsp;?", "La CIVI et le FGTI ont leurs propres règles et leurs propres délais. Un premier échange gratuit permet d'examiner votre dossier avant toute démarche."),
    "capitalisation-prejudice-euro-de-rente": ("L'offre capitalise un préjudice futur&nbsp;?", "Barème, taux, âge retenu&nbsp;: chaque paramètre change le montant. Faites vérifier gratuitement le calcul de l'assureur."),
    "carambolage-indemnisation": ("Blessé dans un carambolage&nbsp;?", "Plusieurs véhicules, plusieurs assureurs&nbsp;: faites le point gratuitement sur celui qui doit vous indemniser."),
    "coup-du-lapin-indemnisation": ("Entorse cervicale après un accident&nbsp;?", "Une blessure qualifiée de légère doit tout de même être évaluée poste par poste. Faites vérifier gratuitement l'offre de l'assureur."),
    "deces-accident-indemnisation-proches": ("Vous avez perdu un proche dans un accident&nbsp;?", "Chaque membre de la famille peut avoir ses propres droits. Le cabinet vous reçoit gratuitement pour faire le point, à votre rythme."),
    "deficit-fonctionnel-permanent-dfp": ("Un taux de DFP vous a été proposé&nbsp;?", "Le taux retenu et la valeur du point se discutent. Faites vérifier gratuitement l'évaluation qui vous est proposée."),
    "delai-prescription-accident-corporel": ("Vous craignez d'être hors délai&nbsp;?", "Les délais varient selon le type d'accident et certains peuvent être interrompus. Faites vérifier gratuitement où en est votre dossier."),
    "enfant-victime-accident-indemnisation": ("Votre enfant a été blessé dans un accident&nbsp;?", "Son indemnisation doit tenir compte de toute sa vie future. Faites le point gratuitement avec un avocat qui défend uniquement les victimes."),
    "erreur-medicale-droits-victime": ("Vous pensez avoir été victime d'une erreur médicale&nbsp;?", "CCI, ONIAM ou tribunal&nbsp;: faites examiner gratuitement votre situation avant de choisir la procédure."),
    "expertise-medicale-judiciaire": ("Vous êtes convoqué à une expertise médicale&nbsp;?", "Amiable ou judiciaire, une expertise se prépare en amont. Parlons-en gratuitement avant la date."),
    "faute-conducteur-victime-indemnisation": ("L'assureur invoque votre faute de conducteur&nbsp;?", "Une faute ne prive pas automatiquement de toute indemnisation. Faites vérifier gratuitement la position de l'assureur."),
    "fonds-garantie-conducteur-non-assure": ("Le responsable n'était pas assuré&nbsp;?", "Le Fonds de garantie peut prendre le relais, sous conditions et dans des délais précis. Faites le point gratuitement."),
    "incidence-professionnelle": ("L'accident a changé votre vie professionnelle&nbsp;?", "Pénibilité, reclassement, dévalorisation sur le marché du travail&nbsp;: faites vérifier gratuitement que ce poste est bien pris en compte."),
    "indemnisation-accident-corporel": ("Vous voulez savoir ce que doit couvrir votre indemnisation&nbsp;?", "Chaque poste de préjudice compte. Faites vérifier gratuitement l'évaluation de votre dossier."),
    "indemnisation-accident-grave": ("Accident grave&nbsp;: une offre, une expertise, une décision à prendre&nbsp;?", "Dans les dossiers lourds, chaque poste (tierce personne, frais futurs, pertes de revenus) pèse. Faites examiner gratuitement votre situation."),
    "indemnisation-victime-passagere-accident": ("Passager blessé dans un accident&nbsp;?", "Faites vérifier gratuitement l'offre qui vous est faite, avec un avocat qui défend uniquement les victimes."),
    "infection-nosocomiale-indemnisation": ("Une infection contractée à l'hôpital&nbsp;?", "Établissement, ONIAM ou CCI&nbsp;: le bon interlocuteur dépend de la gravité des séquelles. Faites examiner gratuitement votre dossier."),
    "medecin-recours-victime": ("Une expertise médicale approche&nbsp;?", "Le cabinet travaille avec des médecins-recours indépendants. Parlons gratuitement de votre expertise à venir."),
    "oniam-referentiel-tribunal-alea-therapeutique": ("Vous avez reçu une offre de l'ONIAM&nbsp;?", "Vous n'êtes pas tenu de l'accepter. Faites-la comparer gratuitement avant de signer."),
    "pieton-indemnisation-accident": ("Piéton renversé&nbsp;?", "Le droit à indemnisation est rarement contesté&nbsp;: tout se joue sur le chiffrage. Faites vérifier gratuitement l'offre de l'assureur."),
    "preparer-expertise-medicale-accident-grave": ("Une expertise médicale est prévue&nbsp;?", "Les jours qui la précèdent comptent. Parlons-en gratuitement avant la date pour la préparer ensemble."),
    "que-faire-apres-accident-route": ("Vous venez d'avoir un accident&nbsp;?", "Avant de répondre à l'assureur ou de signer quoi que ce soit, faites le point gratuitement sur vos droits."),
    "refuser-offre-assurance-accident": ("Vous avez reçu une offre d'indemnisation&nbsp;?", "Faites-la vérifier gratuitement avant de signer&nbsp;: une fois acceptée, une transaction est difficile à remettre en cause."),
    "simulateur-dfp-capitalisation": ("Vous voulez confronter ce résultat à votre dossier&nbsp;?", "Le simulateur donne un ordre de grandeur. Faites vérifier gratuitement le calcul appliqué à votre situation."),
    "souffrances-endurees": ("Une cotation des souffrances endurées vous paraît basse&nbsp;?", "Elle se discute, d'abord pendant l'expertise. Faites vérifier gratuitement votre rapport."),
    "tierce-personne-indemnisation": ("Vous avez besoin d'aide au quotidien depuis l'accident&nbsp;?", "Le nombre d'heures et le taux horaire retenus font toute la différence. Faites vérifier gratuitement l'évaluation."),
    "traumatisme-cranien-indemnisation": ("Un proche a subi un traumatisme crânien&nbsp;?", "Les séquelles invisibles doivent être documentées tôt. Faites le point gratuitement avec un avocat qui défend uniquement les victimes."),
}

# Formulations des fins d'articles qui sonnaient comme une promesse de résultat.
DEONTOLOGY_FIXES = [
    ("WhatsApp — Réponse immédiate", "WhatsApp"),
    ("L'offre de l'assurance<br><span class=\"text-orange-400\">n'est jamais suffisante</span>",
     "L'offre de l'assurance<br><span class=\"text-orange-400\">mérite d'être vérifiée</span>"),
    (" Cette consultation peut changer radicalement votre indemnisation.", " Vous saurez si elle couvre bien chacun de vos préjudices."),
    ("identifie le bon responsable et obtient votre juste indemnisation.", "identifie le bon responsable et défend votre indemnisation."),
    ("conteste les refus abusifs et obtient votre juste indemnisation.", "conteste les refus injustifiés et défend votre indemnisation."),
    ("Obtenez un premier avis immédiat sur votre dossier.", "Obtenez un premier avis gratuit sur votre dossier."),
]


# --------------------------------------------------------------------------
# Outils de manipulation HTML
# --------------------------------------------------------------------------
def marked(name, html):
    return f"<!-- CTA:{name}:START -->{html}<!-- CTA:{name}:END -->"


def strip_block(src, name):
    return re.sub(rf"<!-- CTA:{name}:START -->.*?<!-- CTA:{name}:END -->", "", src, flags=re.S)


def has_block(src, name):
    return f"<!-- CTA:{name}:START -->" in src


def replace_block(src, name, html):
    return re.sub(rf"<!-- CTA:{name}:START -->.*?<!-- CTA:{name}:END -->", lambda m: marked(name, html), src, flags=re.S)


def match_tag(src, start, tag="div"):
    """Index juste après la balise fermante qui équilibre la balise ouvrante en `start`."""
    pat = re.compile(rf"<{tag}\b|</{tag}>")
    depth = 0
    for m in pat.finditer(src, start):
        depth += 1 if m.group(0).startswith(f"<{tag}") else -1
        if depth == 0:
            return m.end()
    raise ValueError("balise non équilibrée")


def put(src, name, html, anchor_pos):
    """Insère (ou remplace) le bloc `name` à la position donnée."""
    if has_block(src, name):
        return replace_block(src, name, html)
    return src[:anchor_pos] + marked(name, html) + src[anchor_pos:]


def swap_region(src, name, html, start, end):
    """Remplace src[start:end] par le bloc marqué (première exécution)."""
    if has_block(src, name):
        return replace_block(src, name, html)
    return src[:start] + marked(name, html) + src[end:]


def first_section_bounds(src):
    s = src.index("<section", src.index("</nav>"))
    return s, src.index("</section>", s)


def last_section_before_footer(src):
    f = src.index("<footer")
    s = src.rindex("<section", 0, f)
    return s, src.index("</section>", s)


# --------------------------------------------------------------------------
# Retouches communes à toutes les pages
# --------------------------------------------------------------------------
def common(src, add_mobile_bar):
    # Script de suivi
    if TRACKING_TAG not in src:
        src = src.replace("</head>", f"    {TRACKING_TAG}\n</head>", 1)
    # Barre mobile existante : emplacement explicite
    src = src.replace('<div class="fixed bottom-6 left-4 right-4 z-50 md:hidden animate-fade-in-up">',
                      '<div class="fixed bottom-6 left-4 right-4 z-50 md:hidden animate-fade-in-up" data-cta="bouton_fixe_mobile">')
    for fab in ('<a href="https://wa.me/33663465984" id="fab"',
                '<a href="https://wa.me/33663465984" target="_blank" class="fixed bottom-8 right-8'):
        src = src.replace(fab, fab.replace("<a ", '<a data-cta="bouton_flottant" ', 1))
    if add_mobile_bar and 'data-cta="bouton_fixe_mobile"' not in src:
        src = src.replace("</body>", marked("BARRE-MOBILE", MOBILE_BAR) + "\n</body>", 1)
        # Le pied de page doit rester lisible au-dessus de la barre fixe.
        src = re.sub(r'<footer class="bg-ink text-white py-16 ', '<footer class="bg-ink text-white pt-16 pb-36 md:py-16 ', src, count=1)
    # Barre mobile : 3e option « rendez-vous » à côté de WhatsApp et Appeler
    if "CTA:BARRE-RDV:START" not in src and 'data-cta="bouton_fixe_mobile"' in src:
        bar = src.index('data-cta="bouton_fixe_mobile"')
        inner = src.index("<div", bar)
        inner_end = match_tag(src, inner) - len("</div>")
        src = src[:inner_end] + MOBILE_RDV + src[inner_end:]
    for old, new in DEONTOLOGY_FIXES:
        src = src.replace(old, new)
    return src


# --------------------------------------------------------------------------
# Par type de page
# --------------------------------------------------------------------------
def do_blog_article(src, slug):
    title, text = BLOG[slug]
    # 1. Hero : sous la ligne de méta (date, temps de lecture, auteur)
    hs, he = first_section_bounds(src)
    h1 = src.index("<h1", hs)
    wrap = src.rindex('<div class="max-w-3xl">', hs, h1)
    end = match_tag(src, wrap) - len("</div>")
    src = put(src, "HERO", hero_block("Une question sur votre situation&nbsp;? Premier échange gratuit et confidentiel."), end)

    # 2. Encadré contextuel au milieu de l'article
    if not has_block(src, "MILIEU"):
        a0 = src.index("<!-- ARTICLE -->")
        a1 = src.index("<!-- SIDEBAR -->")
        body = src[a0:a1]
        h2s = [m for m in re.finditer(r"\n([ \t]*)<h2\b[^>]*>(.*?)</h2>", body, re.S)
               if not re.search(r"Questions fréquentes|Articles liés|Sources", m.group(2))]
        if h2s:
            indent = h2s[0].group(1)
            h2s = [m for m in h2s if m.group(1) == indent]
            target = h2s[len(h2s) // 2] if len(h2s) > 1 else h2s[0]
            pos = a0 + target.start() + 1
        else:  # article sans H2 de contenu : avant la FAQ
            pos = a0 + body.index("<h2")
        src = src[:pos] + marked("MILIEU", card(title, text)) + "\n" + src[pos:]
    else:
        src = replace_block(src, "MILIEU", card(title, text))

    # 3. Barre latérale : bouton rendez-vous + emplacement
    side = src.index("<!-- SIDEBAR -->")
    plain = '<div class="bg-gray-900 text-white p-6 rounded-2xl">'
    tagged = '<div class="bg-gray-900 text-white p-6 rounded-2xl" data-cta="sidebar">'
    if src.find(plain, side) != -1:
        i = src.index(plain, side)
        src = src[:i] + tagged + src[i + len(plain):]
    box = src.index(tagged, side)
    box_end = match_tag(src, box)
    if "data-calendly" not in src[box:box_end]:
        rdv = (f'<a href="{CAL}" target="_blank" rel="noopener" data-calendly class="block w-full py-3 mt-3 border border-white/20 '
               f'text-white rounded-xl font-bold text-center hover:bg-white/10 transition">Prendre rendez-vous</a>'
               '<p class="text-xs text-gray-400 mt-4 text-center">Consultation gratuite · Honoraires au résultat</p>')
        src = src[:box_end - len("</div>")] + rdv + src[box_end - len("</div>"):]

    # 4. Fin d'article : 3 options + réassurance
    cs = src.index("<!-- CTA SECTION -->")
    sec_end = src.index("</section>", cs)
    if has_block(src[cs:sec_end], "FIN"):
        src = replace_block(src, "FIN", end_row())
    else:
        row = src.index('<div class="flex flex-col sm:flex-row gap-4 justify-center">', cs)
        row_end = match_tag(src, row)
        p = re.compile(r'\s*<p class="text-gray-500 text-sm mt-6">.*?</p>', re.S).match(src, row_end)
        src = swap_region(src, "FIN", end_row(), row, p.end() if p else row_end)
    return src


def do_blog_index(src):
    hs, he = first_section_bounds(src)
    wrap = src.index('<div class="max-w-3xl">', hs)
    end = match_tag(src, wrap) - len("</div>")
    src = put(src, "HERO", hero_block("Votre situation n'est pas dans un article&nbsp;? Premier échange gratuit et confidentiel."), end)
    grid = src.index('<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">')
    mid = ('<div class="md:col-span-2 lg:col-span-3" data-cta="milieu">'
           + card("Vous avez une question précise sur votre dossier&nbsp;?",
                  "Offre de l'assureur, expertise, délais&nbsp;: un avocat qui défend uniquement les victimes vous répond gratuitement.").replace("my-12 ", "")
           + "</div>")
    first_article_end = src.index("</article>", grid)
    if has_block(src, "MILIEU"):
        src = replace_block(src, "MILIEU", mid)
    else:
        pos = first_article_end + len("</article>")
        src = src[:pos] + marked("MILIEU", mid) + src[pos:]
    # Le tri automatique des articles replace l'encadré au milieu de la grille.
    old = "      articles.forEach(a => grid.insertBefore(a, cta));\n"
    new = (old + "      const mid = grid.querySelector('[data-cta=\"milieu\"]');\n"
           "      if (mid) grid.insertBefore(mid, articles[9] || cta);\n")
    if "grid.querySelector('[data-cta=\"milieu\"]')" not in src:
        src = src.replace(old, new)
    # Fin de page
    f = src.index("<footer")
    endband = band("Une question sur votre dossier&nbsp;?",
                   "Premier échange gratuit et confidentiel avec Maître Ilan Guedj, avocat au barreau de Marseille.", "fin_de_page")
    src = put(src, "FIN", endband, src.rindex("<!-- FOOTER -->", 0, f) if "<!-- FOOTER -->" in src[:f] else f)
    return src


def lead_paragraph_end(src, hs, he):
    """Fin du paragraphe d'accroche du hero (après le marqueur GEO s'il l'entoure)."""
    p = src.index('<p class="text-2xl md:text-3xl', hs, he)
    pe = src.index("</p>", p) + len("</p>")
    tail = src[pe:pe + 60]
    m = re.match(r"\s*</div>\s*<!-- GEO:ANSWER:END -->", tail)
    return pe + m.end() if m else pe


def do_city(src, slug):
    where = CITIES[slug]
    hs, he = first_section_bounds(src)
    src = put(src, "HERO", hero_block(f"Victime d'un accident {where}&nbsp;? Consultation gratuite."), lead_paragraph_end(src, hs, he))
    anchor = src.index("<!-- ===== NOS 4 DOMAINES")
    src = put(src, "MILIEU", band(f"Blessé {where}&nbsp;: accident, erreur médicale, agression&nbsp;?",
                                  f"Le cabinet accompagne les victimes {where}, en visioconférence ou sur place pour les expertises et les audiences. "
                                  "Faites le point gratuitement sur votre dossier."), anchor)
    return do_end_section(src)


def do_service(src, slug):
    title, text = SERVICES[slug]
    hs, he = first_section_bounds(src)
    src = put(src, "HERO", hero_block("Premier échange gratuit et confidentiel avec Maître Ilan Guedj."), lead_paragraph_end(src, hs, he))
    anchor = src.index("<!-- ===== PROCÉDURE DÉTAILLÉE")
    src = put(src, "MILIEU", band(title, text), anchor)
    return do_end_section(src)


def do_end_section(src):
    if has_block(src, "FIN"):
        return replace_block(src, "FIN", end_row())
    s, e = last_section_before_footer(src)
    row = src.rindex('<div class="flex flex-col sm:flex-row gap-4 justify-center">', s, e)
    return swap_region(src, "FIN", end_row(), row, match_tag(src, row))


def do_home(src):
    # Hero : les options WhatsApp et rendez-vous à côté du téléphone, plus la réassurance
    c = src.index("<!-- CTAs -->")
    row = src.index("<div", c)
    row_end = match_tag(src, row)
    extra = (
        '<div data-cta="hero">'
        '<p class="text-sm text-gray-600 flex flex-wrap items-center gap-x-4 gap-y-2">'
        f'<a href="{WA}" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 font-semibold text-gray-900 hover:text-green-600 transition"><span class="text-[#25D366]">{ICON_WA}</span>Écrire sur WhatsApp</a>'
        '<span class="w-px h-4 bg-gray-300" aria-hidden="true"></span>'
        f'<a href="{CAL}" target="_blank" rel="noopener" data-calendly class="inline-flex items-center gap-1.5 font-semibold text-gray-900 hover:text-blue-600 transition">{ICON_CAL}Prendre rendez-vous</a>'
        '</p>' + reassurance() + "</div>"
    )
    src = put(src, "HERO", extra, row_end)
    # Sections existantes : emplacements explicites
    src = src.replace('<section id="diagnostic-widget" class=', '<section id="diagnostic-widget" data-cta="diagnostic" class=', 1) \
        if 'data-cta="diagnostic"' not in src else src
    src = src.replace('<section class="bg-ink py-24">', '<section class="bg-ink py-24" data-cta="milieu">', 1) \
        if 'data-cta="milieu"' not in src else src
    # Fin de page : bandeau sobre avant le pied de page
    f = src.index("<footer")
    endband = band("Une question sur votre dossier&nbsp;?",
                   "Premier échange gratuit et confidentiel. Le cabinet vous répond par téléphone, sur WhatsApp ou lors d'un rendez-vous.", "fin_de_page")
    return put(src, "FIN", endband, src.rindex("\n", 0, f) + 1)


def do_honoraires(src):
    hs, he = first_section_bounds(src)
    pos = src.index("<!-- GEO:ANSWER:END -->", hs) + len("<!-- GEO:ANSWER:END -->")
    src = put(src, "HERO", hero_block("Parlons de votre dossier&nbsp;: le premier échange est gratuit.", center=True), pos)
    anchor = src.index('<section class="py-24 bg-white">')
    src = put(src, "MILIEU", band("Une question sur la convention d'honoraires&nbsp;?",
                                  "Le cabinet vous l'explique avant toute intervention, lors d'un premier échange gratuit et sans engagement."), anchor)
    if has_block(src, "FIN"):
        return replace_block(src, "FIN", end_row(dark=False))
    s = src.index('<h2 class="text-3xl md:text-4xl font-black mb-6">Convaincu par notre transparence ?</h2>')
    row = src.index('<div class="flex flex-col sm:flex-row justify-center gap-4">', s)
    fin = end_row(dark=False) + ('<p class="mt-4 text-sm text-gray-500 text-center"><a href="/#diagnostic-widget" '
                                 'class="font-semibold text-blue-700 underline">Estimer mon indemnisation</a></p>')
    return swap_region(src, "FIN", fin, row, match_tag(src, row))


def do_avocat(src):
    hs, he = first_section_bounds(src)
    container_end = src.rindex("</div>", hs, he)
    src = put(src, "HERO", hero_block("Parler de votre dossier&nbsp;: premier échange gratuit et confidentiel."), container_end)
    anchor = src.rindex("<section", 0, src.index(">La méthode de travail</h2>"))
    src = put(src, "MILIEU", band("Vous souhaitez lui exposer votre situation&nbsp;?",
                                  "Maître Ilan Guedj vous répond lui-même lors d'un premier échange gratuit, par téléphone, sur WhatsApp ou en rendez-vous."), anchor)
    return do_end_section_flex(src)


def do_end_section_flex(src):
    if has_block(src, "FIN"):
        return replace_block(src, "FIN", end_row())
    s, e = last_section_before_footer(src)
    row = src.rindex('<div class="flex flex-col sm:flex-row gap-4 justify-center">', s, e)
    return swap_region(src, "FIN", end_row(), row, match_tag(src, row))


def do_lexique(src):
    hs, he = first_section_bounds(src)
    pos = src.index("<!-- GEO:ANSWER:END -->", hs) + len("<!-- GEO:ANSWER:END -->")
    src = put(src, "HERO", hero_block("Un terme de votre dossier vous échappe&nbsp;? Posez la question, le premier échange est gratuit."), pos)
    anchor = src.rindex("<section", 0, src.index("L&#x27;expertise médicale</h2>"))
    src = put(src, "MILIEU", band("Un rapport d'expertise ou une offre à décrypter&nbsp;?",
                                  "Faites-les relire gratuitement par un avocat qui défend uniquement les victimes."), anchor)
    endband = band("Une question sur votre dossier&nbsp;?",
                   "Premier échange gratuit et confidentiel avec Maître Ilan Guedj, avocat au barreau de Marseille.", "fin_de_page")
    return put(src, "FIN", endband, src.index("</main>"))


def main():
    os.chdir(ROOT)
    changed = []
    pages = sorted(glob.glob("*.html") + glob.glob("blog/*.html"))
    for path in pages:
        slug = os.path.basename(path)[:-5]
        src = open(path, encoding="utf-8").read()
        orig = src
        if path == "guide-5-erreurs.html":
            src = common(src, add_mobile_bar=False)
            if "GTM-WP82S37T" not in src:  # le guide n'avait pas le conteneur GTM
                src = src.replace("<head>", "<head>\n" + GTM_HEAD, 1)
                src = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + GTM_BODY, src, count=1)
        elif path.startswith("blog/"):
            src = common(src, add_mobile_bar=True)
            src = do_blog_index(src) if slug == "index" else do_blog_article(src, slug)
        elif slug in CITIES:
            src = do_city(common(src, False), slug)
        elif slug in SERVICES:
            src = do_service(common(src, False), slug)
        elif slug == "index":
            src = do_home(common(src, False))
        elif slug == "honoraires":
            src = do_honoraires(common(src, False))
        elif slug == "avocat-ilan-guedj":
            src = do_avocat(common(src, True))
        elif slug == "lexique-dommage-corporel":
            src = do_lexique(common(src, False))
        else:  # contact, mentions légales : suivi + barre mobile seulement
            src = common(src, add_mobile_bar=True)
        if src != orig:
            open(path, "w", encoding="utf-8", newline="\n").write(src)
            changed.append(path)
    print(f"{len(changed)} page(s) modifiée(s)")
    for p in changed:
        print("  ", p)


if __name__ == "__main__":
    sys.exit(main())
