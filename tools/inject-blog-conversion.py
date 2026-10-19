#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ajoute, de façon idempotente, sur chaque article de blog :

- un appel à l'action au milieu de l'article ;
- un formulaire court en fin d'article (même endpoint Formspree que le contact) ;
- un maillage contextuel (domaine, articles proches, simulateur, guide, villes).

Le script de suivi js/conversions.js est inclus sur toutes les pages HTML.
La barre mobile du blog reprend le gabarit Appeler / WhatsApp des autres pages,
avec une marge pour ne pas couvrir le formulaire.
"""
import html
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
FORM_ACTION = "https://formspree.io/f/meelzkzw"
TEL = "tel:+33663465984"
WA = "https://wa.me/33663465984"
CAL = "https://calendly.com/guedj-chiche-cohen"

OPTIONS = [
    ("", "Choisir…"),
    ("Accident de la route", "Accident de la route"),
    ("Erreur médicale", "Erreur médicale"),
    ("Agression", "Agression"),
    ("Accident de la vie", "Accident de la vie"),
    ("Accident du travail", "Accident du travail"),
    ("Autre", "Autre"),
]

COPY = {
    "route": {
        "kicker": "Accident de la route",
        "title": "Faire le point sur un accident de la route",
        "body": "Maître Ilan Guedj examine les circonstances et les pièces déjà réunies, puis les démarches envisageables. Cet échange ne préjuge pas de l'issue du dossier, et aucun montant n'est annoncé à ce stade.",
        "select": "Accident de la route",
    },
    "medical": {
        "kicker": "Dossier médical",
        "title": "Faire le point sur un dossier médical",
        "body": "Faute, aléa thérapeutique ou infection : Maître Ilan Guedj situe les voies possibles, devant la commission ou le tribunal. Rien n'est promis avant l'examen des pièces.",
        "select": "Erreur médicale",
    },
    "agression": {
        "kicker": "Agression",
        "title": "Faire le point après une agression",
        "body": "Maître Ilan Guedj peut examiner la situation au regard de la CIVI et du FGTI. L'indemnisation dépend des faits et de la procédure : elle n'est pas acquise d'avance.",
        "select": "Agression",
    },
    "vie": {
        "kicker": "Accident de la vie",
        "title": "Faire le point sur un accident de la vie",
        "body": "Accident domestique, sportif ou scolaire : Maître Ilan Guedj regarde quelles garanties et quels recours peuvent être étudiés, sans engagement sur le résultat.",
        "select": "Accident de la vie",
    },
    "travail": {
        "kicker": "Accident du travail",
        "title": "Faire le point sur un accident du travail",
        "body": "Rente, faute inexcusable, préjudices laissés de côté par la Sécurité sociale : Maître Ilan Guedj peut relire la situation. L'issue dépend du dossier.",
        "select": "Accident du travail",
    },
    "prejudice": {
        "kicker": "Indemnisation",
        "title": "Faire le point sur l'indemnisation",
        "body": "Le chiffrage d'un poste dépend de l'expertise et de la situation personnelle. Maître Ilan Guedj peut examiner les éléments déjà réunis, sans annoncer de montant.",
        "select": "",
    },
    "expertise": {
        "kicker": "Expertise médicale",
        "title": "Préparer l'expertise médicale",
        "body": "Le rapport d'expertise sert ensuite de base à la discussion. Maître Ilan Guedj peut aider à rassembler les pièces et les doléances. Le résultat de l'examen ne se promet pas.",
        "select": "",
    },
}

DOMAIN = {
    "accident-bus-tramway-indemnisation.html": "route",
    "accident-delit-fuite-indemnisation.html": "route",
    "accident-moto-indemnisation.html": "route",
    "accident-route-indemnisation.html": "route",
    "accident-travail-faute-inexcusable.html": "travail",
    "accident-trottinette-electrique-indemnisation.html": "route",
    "accident-velo-indemnisation.html": "route",
    "agression-victime-droits-recours.html": "agression",
    "capitalisation-prejudice-euro-de-rente.html": "prejudice",
    "carambolage-indemnisation.html": "route",
    "coup-du-lapin-indemnisation.html": "route",
    "deces-accident-indemnisation-proches.html": "prejudice",
    "deficit-fonctionnel-permanent-dfp.html": "prejudice",
    "delai-prescription-accident-corporel.html": "prejudice",
    "enfant-victime-accident-indemnisation.html": "route",
    "erreur-medicale-droits-victime.html": "medical",
    "expertise-medicale-judiciaire.html": "expertise",
    "faute-conducteur-victime-indemnisation.html": "route",
    "fonds-garantie-conducteur-non-assure.html": "route",
    "incidence-professionnelle.html": "prejudice",
    "indemnisation-accident-corporel.html": "prejudice",
    "indemnisation-accident-grave.html": "route",
    "indemnisation-victime-passagere-accident.html": "route",
    "infection-nosocomiale-indemnisation.html": "medical",
    "medecin-recours-victime.html": "expertise",
    "oniam-referentiel-tribunal-alea-therapeutique.html": "medical",
    "pieton-indemnisation-accident.html": "route",
    "preparer-expertise-medicale-accident-grave.html": "expertise",
    "que-faire-apres-accident-route.html": "route",
    "refuser-offre-assurance-accident.html": "route",
    "simulateur-dfp-capitalisation.html": "prejudice",
    "souffrances-endurees.html": "prejudice",
    "tierce-personne-indemnisation.html": "prejudice",
    "traumatisme-cranien-indemnisation.html": "prejudice",
}

OVERRIDE = {
    "enfant-victime-accident-indemnisation.html": {
        "kicker": "Enfant victime",
        "title": "Faire le point sur le dossier d'un enfant",
        "body": "Les règles de protection et les préjudices d'un enfant ne sont pas ceux d'un adulte. Maître Ilan Guedj peut examiner la situation, sans annoncer d'indemnisation.",
    },
    "deces-accident-indemnisation-proches.html": {
        "kicker": "Proches d'une victime",
        "title": "Faire le point sur les droits des proches",
        "body": "Préjudice d'affection, frais d'obsèques, perte de revenus du foyer : chaque proche a sa propre situation. Maître Ilan Guedj peut l'examiner, sans annoncer de montant.",
    },
    "delai-prescription-accident-corporel.html": {
        "kicker": "Délais",
        "title": "Vérifier si un délai court encore",
        "body": "La prescription dépend du type d'accident et de la date de consolidation. À partir de vos dates, Maître Ilan Guedj peut dire si une action reste ouverte. Cela ne préjuge pas du résultat.",
        "select": "",
    },
    "refuser-offre-assurance-accident.html": {
        "kicker": "Offre d'indemnisation",
        "title": "Faire relire une offre d'indemnisation",
        "body": "Maître Ilan Guedj peut regarder une offre déjà reçue, poste par poste. Cette relecture ne garantit ni une somme différente, ni l'issue d'une discussion.",
        "select": "",
    },
    "traumatisme-cranien-indemnisation.html": {
        "kicker": "Traumatisme crânien",
        "title": "Faire le point sur un traumatisme crânien",
        "body": "Les séquelles ne se voient pas toujours tout de suite. Maître Ilan Guedj peut examiner les éléments déjà réunis, sans annoncer de montant.",
    },
}

# (href, ancre, phrase contenant {a}). Les liens déjà présents dans la colonne
# d'article sont ignorés pour ne pas doubler le maillage existant.
LINKS = {
    "accident-bus-tramway-indemnisation.html": [
        ("../accidents-route", "accidents de la circulation", "Le passager d'un bus relève du régime des {a}."),
        ("coup-du-lapin-indemnisation", "coup du lapin", "Un freinage brutal laisse parfois un {a}, qui se discute à l'expertise."),
        ("../guide-5-erreurs", "cinq erreurs après un accident", "Les réflexes qui évitent de fermer le dossier trop tôt sont rappelés dans les {a}."),
    ],
    "accident-delit-fuite-indemnisation.html": [
        ("../accidents-route", "accident de la route", "Le cadre reste celui d'un {a}, même si le conducteur a pris la fuite."),
        ("fonds-garantie-conducteur-non-assure", "conducteur non assuré", "Si le véhicule est retrouvé mais non assuré, l'indemnisation passe aussi par le cas du {a}."),
        ("../guide-5-erreurs", "guide des cinq erreurs", "En attendant l'identification, le {a} rappelle ce qu'il vaut mieux ne pas signer."),
    ],
    "accident-moto-indemnisation.html": [
        ("../accidents-route", "page des accidents de la route", "Le motard est un conducteur au sens de la {a}."),
        ("accident-trottinette-electrique-indemnisation", "trottinette électrique", "L'utilisateur d'une {a} est, lui aussi, conducteur d'un véhicule terrestre à moteur."),
        ("../accidents-vie", "garantie des accidents de la vie", "À défaut de tiers, la garantie du conducteur ou la {a} dépend du contrat souscrit."),
        ("../guide-5-erreurs", "erreurs qui pèsent ensuite", "Avant tout accord, les {a} méritent d'être relues."),
    ],
    "accident-route-indemnisation.html": [
        ("../accidents-route", "présentation des accidents de la route", "Les situations les plus courantes sont regroupées sur la {a}."),
        ("accident-travail-faute-inexcusable", "faute inexcusable de l'employeur", "Sur un trajet domicile-travail, la {a} peut s'ajouter au recours contre le tiers."),
        ("../accidents-vie", "garantie des accidents de la vie", "Sans autre véhicule impliqué, il reste parfois la {a}, dans les limites du contrat."),
        ("../guide-5-erreurs", "cinq erreurs à éviter après l'accident", "Le repère des {a} complète ce guide."),
    ],
    "accident-travail-faute-inexcusable.html": [
        ("../accidents-route", "accident de trajet", "Lorsque le trajet est aussi un {a}, le recours contre un tiers responsable reste ouvert."),
        ("deficit-fonctionnel-permanent-dfp", "déficit fonctionnel permanent", "La rente ne tient pas lieu de {a}, qui se discute à part."),
        ("simulateur-dfp-capitalisation", "simulateur de capitalisation", "Pour un besoin qui se projette dans le temps, le {a} donne un ordre de grandeur, pas un montant dû."),
        ("incidence-professionnelle", "incidence professionnelle", "La dévalorisation du parcours se retrouve au poste d'{a}."),
    ],
    "accident-trottinette-electrique-indemnisation.html": [
        ("../accidents-route", "accidents de la route", "La trottinette électrique est traitée avec les {a}, dans la catégorie des conducteurs."),
        ("accident-velo-indemnisation", "cycliste", "À l'inverse, un {a} renversé par une voiture n'est pas un conducteur."),
        ("../guide-5-erreurs", "cinq erreurs fréquentes", "Les {a} concernent aussi un accident en trottinette."),
    ],
    "accident-velo-indemnisation.html": [
        ("../accidents-route", "page accidents de la route", "Le cycliste est une victime non conductrice, comme l'explique la {a}."),
        ("accident-bus-tramway-indemnisation", "bus ou un tramway", "Heurté par un {a}, il relève en principe du même régime protecteur, sous réserve de la voie propre du tramway."),
        ("../guide-5-erreurs", "pièces à conserver dès les premiers jours", "Le guide des {a} s'applique aussi au cycliste."),
    ],
    "agression-victime-droits-recours.html": [
        ("../agression", "agressions", "La procédure devant la CIVI est reprise sur la page {a}."),
        ("delai-prescription-accident-corporel", "délais pour agir", "Les {a} ne sont pas les mêmes que ceux d'un accident de la route."),
        ("../guide-5-erreurs", "cinq erreurs après un dommage corporel", "Certaines des {a} se retrouvent aussi après une agression, surtout au moment de signer."),
    ],
    "capitalisation-prejudice-euro-de-rente.html": [
        ("simulateur-dfp-capitalisation", "simulateur de capitalisation", "Le {a} applique cette formule à titre indicatif : il ne lie pas le juge."),
        ("tierce-personne-indemnisation", "tierce personne", "Une {a} nécessaire à vie est l'exemple type d'un poste à capitaliser."),
        ("incidence-professionnelle", "incidence professionnelle", "L'{a} future se projette en général jusqu'à l'âge de départ à la retraite."),
        ("../accidents-route", "accident de la route", "Le même calcul sert après un {a} ou un autre fait générateur."),
    ],
    "carambolage-indemnisation.html": [
        ("../accidents-route", "accident de la route", "Le carambolage reste un {a} : la victime n'a pas à désigner elle-même le responsable."),
        ("accident-bus-tramway-indemnisation", "accident de bus ou de tramway", "Si un transport en commun est dans la file, l'{a} suit des règles proches, avec une réserve pour le tramway sur voie propre."),
        ("../guide-5-erreurs", "erreurs qui compliquent ensuite le dossier", "Au milieu de plusieurs interlocuteurs, les {a} sont utiles à relire avant de signer."),
    ],
    "coup-du-lapin-indemnisation.html": [
        ("../accidents-route", "accident de la route", "Le coup du lapin suit le plus souvent un {a}, en particulier un choc arrière."),
        ("souffrances-endurees", "souffrances endurées", "Les douleurs des premières semaines se retrouvent au poste des {a}."),
        ("simulateur-dfp-capitalisation", "simulateur du déficit fonctionnel permanent", "Un taux modeste ne correspond pas à une somme fixe : le {a} le montre, à titre indicatif."),
        ("../guide-5-erreurs", "cinq erreurs après l'accident", "Une offre rapide se lit mieux avec les {a} en tête."),
    ],
    "deces-accident-indemnisation-proches.html": [
        ("../accidents-route", "accident de la circulation", "Lorsque le décès fait suite à un {a}, les proches conservent leurs préjudices personnels."),
        ("accident-travail-faute-inexcusable", "faute inexcusable de l'employeur", "S'il s'agit d'un accident du travail, la {a} ouvre une indemnisation complémentaire aux ayants droit."),
        ("../erreur-medicale", "accident médical", "Après un {a}, les proches peuvent aussi avoir des droits propres."),
    ],
    "deficit-fonctionnel-permanent-dfp.html": [
        ("simulateur-dfp-capitalisation", "simulateur de la valeur du point", "Le {a} donne un ordre de grandeur à partir d'un taux et d'un âge. Il ne fixe pas l'indemnisation."),
        ("../accidents-route", "accident de la route", "Le taux se discute après un {a} comme après tout autre fait générateur."),
        ("accident-travail-faute-inexcusable", "accident du travail", "En {a}, la rente de la Sécurité sociale ne tient pas lieu de déficit fonctionnel permanent."),
        ("souffrances-endurees", "souffrances endurées", "Ce poste ne se confond pas avec les {a}."),
    ],
    "delai-prescription-accident-corporel.html": [
        ("../accidents-route", "accident de la route", "Après un {a}, le délai de droit commun court en principe depuis la consolidation."),
        ("accident-travail-faute-inexcusable", "faute inexcusable", "La {a} obéit à un délai plus court, qu'il ne faut pas confondre avec le délai de dix ans."),
        ("infection-nosocomiale-indemnisation", "infection nosocomiale", "Une {a} se prescrit selon les règles du dommage médical, pas selon celles de la route."),
        ("../guide-5-erreurs", "cinq erreurs qui font perdre du temps", "Attendre sans se renseigner est l'une des {a}."),
    ],
    "enfant-victime-accident-indemnisation.html": [
        ("../accidents-route", "accidents de la route", "L'enfant piéton, cycliste ou passager est protégé par le régime des {a}."),
        ("traumatisme-cranien-indemnisation", "traumatisme crânien", "Un {a} chez l'enfant se consolide souvent tard, après la croissance."),
        ("../guide-5-erreurs", "erreurs à éviter lorsque l'on signe", "Les {a} concernent aussi les parents qui engagent l'enfant."),
    ],
    "erreur-medicale-droits-victime.html": [
        ("../erreur-medicale", "erreur médicale", "Le cadre d'ensemble est repris sur la page {a}."),
        ("preparer-expertise-medicale-accident-grave", "préparer l'expertise", "La page pour {a} détaille les pièces à réunir avant l'examen."),
        ("delai-prescription-accident-corporel", "délai pour agir", "Le {a} en matière médicale ne court pas toujours depuis le jour de l'acte."),
    ],
    "expertise-medicale-judiciaire.html": [
        ("../erreur-medicale", "erreur médicale", "Devant la commission comme devant le tribunal, l'expertise structure un dossier d'{a}."),
        ("infection-nosocomiale-indemnisation", "infection nosocomiale", "C'est souvent à ce stade que se discute une {a}."),
        ("../accidents-route", "accident de la route", "La même exigence de contradictoire vaut après un {a}."),
    ],
    "faute-conducteur-victime-indemnisation.html": [
        ("../accidents-route", "accidents de la route", "L'article 4 est présenté plus largement sur la page des {a}."),
        ("accident-moto-indemnisation", "accident de moto", "La question de la faute de conduite se pose souvent après un {a}."),
        ("../guide-5-erreurs", "cinq erreurs", "Un constat imprécis est l'une des {a} qui reviennent ensuite dans la discussion sur la faute."),
    ],
    "fonds-garantie-conducteur-non-assure.html": [
        ("../accidents-route", "accident de la route", "Le fonds intervient dans le cadre d'un {a}, lorsque l'assurance obligatoire fait défaut."),
        ("accident-delit-fuite-indemnisation", "délit de fuite", "Le véhicule non identifié après un {a} relève d'un autre volet du même fonds."),
        ("../guide-5-erreurs", "délais et pièces à ne pas négliger", "Les {a} comptent ici aussi : la déclaration est attentive aux dates."),
    ],
    "incidence-professionnelle.html": [
        ("simulateur-dfp-capitalisation", "prix de l'euro de rente", "La perte future se capitalise. Le {a} illustre le calcul, sans lier le juge."),
        ("../accidents-route", "accident de la route", "Ce poste est fréquent après un {a} qui empêche de reprendre le même métier."),
        ("accident-travail-faute-inexcusable", "faute inexcusable", "Après un accident du travail, il se discute en plus de la rente lorsque la {a} est reconnue."),
    ],
    "indemnisation-accident-corporel.html": [
        ("../accidents-route", "accident de la route", "La nomenclature se lit de la même façon après un {a}, un accident médical ou une agression."),
        ("simulateur-dfp-capitalisation", "simulateur de DFP et de capitalisation", "Pour situer un taux ou un poste futur, le {a} donne un ordre de grandeur indicatif."),
        ("../guide-5-erreurs", "cinq erreurs fatales", "Les {a} expliquent pourquoi une première offre se vérifie poste par poste."),
        ("coup-du-lapin-indemnisation", "coup du lapin", "Même un {a}, parfois présenté comme bénin, ouvre ces postes."),
    ],
    "indemnisation-accident-grave.html": [
        ("../accidents-route", "accident de la circulation", "Les blessures les plus lourdes suivent souvent un {a}."),
        ("tierce-personne-indemnisation", "tierce personne", "L'aide d'une {a} est en général le poste qui pèse le plus sur la durée."),
        ("traumatisme-cranien-indemnisation", "traumatisme crânien", "Un {a} en est l'illustration, y compris lorsque la personne semble aller bien."),
        ("simulateur-dfp-capitalisation", "simulateur de capitalisation", "Le coût annuel de l'aide se projette, à titre indicatif, avec le {a}."),
    ],
    "indemnisation-victime-passagere-accident.html": [
        ("../accidents-route", "accidents de la route", "Le passager bénéficie de la protection prévue pour les non-conducteurs, détaillée sur la page des {a}."),
        ("accident-bus-tramway-indemnisation", "bus ou un tramway", "Elle vaut aussi dans un {a}, avec une règle particulière si le tramway circule sur une voie propre."),
        ("coup-du-lapin-indemnisation", "coup du lapin", "Un choc arrière laisse souvent un {a}, même sans blessure visible le jour même."),
        ("../guide-5-erreurs", "cinq erreurs", "Les {a} rappellent de ne pas signer une quittance avant d'avoir lu chaque poste."),
    ],
    "infection-nosocomiale-indemnisation.html": [
        ("../erreur-medicale", "dossier médical", "L'infection nosocomiale est un cas particulier du {a}, avec une responsabilité souvent sans faute de l'établissement."),
        ("oniam-referentiel-tribunal-alea-therapeutique", "référentiel de l'ONIAM", "Lorsque l'ONIAM propose une somme, son {a} ne s'impose pas au juge."),
        ("expertise-medicale-judiciaire", "expertise judiciaire", "Le débat médical se joue souvent à l'{a}."),
        ("delai-prescription-accident-corporel", "délai pour saisir la juridiction", "Le {a} court selon les règles du dommage médical."),
    ],
    "medecin-recours-victime.html": [
        ("../erreur-medicale", "dossier médical", "Son rôle est particulièrement net dans un {a}, en face du médecin mandaté par l'assureur du professionnel."),
        ("infection-nosocomiale-indemnisation", "infection nosocomiale", "Une {a} se discute souvent grâce à ce contradictoire."),
        ("../accidents-route", "accident de la route", "Il est tout aussi utile après un {a}, lorsque le médecin est missionné par l'assureur du véhicule."),
    ],
    "oniam-referentiel-tribunal-alea-therapeutique.html": [
        ("../erreur-medicale", "erreur médicale et l'aléa thérapeutique", "La distinction entre faute et aléa est reprise sur la page {a}."),
        ("expertise-medicale-judiciaire", "expertise ordonnée par le tribunal", "Le jugement commenté ici est parti d'une {a}."),
        ("infection-nosocomiale-indemnisation", "infection nosocomiale", "Une {a} peut relever de l'établissement ou de l'ONIAM, selon le taux d'atteinte."),
    ],
    "pieton-indemnisation-accident.html": [
        ("../accidents-route", "accidents de la route", "Le piéton bénéficie de la protection la plus forte des {a}."),
        ("accident-bus-tramway-indemnisation", "bus ou à proximité d'un tramway", "La même protection joue s'il est heurté par un {a}, sous réserve du régime du tramway sur voie propre."),
        ("../guide-5-erreurs", "cinq erreurs", "Les {a} portent sur les pièces et les signatures, pas sur le seul fait d'avoir traversé hors d'un passage."),
    ],
    "preparer-expertise-medicale-accident-grave.html": [
        ("../guide-5-erreurs", "erreurs commises avant l'expertise", "Plusieurs des {a} se jouent dans les semaines qui précèdent l'examen."),
        ("infection-nosocomiale-indemnisation", "infection contractée à l'hôpital", "Le dossier médical doit aussi permettre de discuter une {a}, lorsqu'elle est en cause."),
        ("../accidents-route", "accident de la route", "La préparation vaut après un {a} comme après un accident médical."),
        ("medecin-recours-victime", "médecin-recours", "Être accompagné d'un {a} fait partie de cette préparation."),
    ],
    "que-faire-apres-accident-route.html": [
        ("../accidents-route", "droits après un accident de la route", "Une fois les premiers constats faits, la page des {a} situe le régime applicable."),
        ("../guide-5-erreurs", "cinq erreurs fatales", "Ce que cette page décrit en gestes concrets, les {a} le reprennent sous l'angle de ce qu'il vaut mieux ne pas faire."),
        ("accident-trottinette-electrique-indemnisation", "trottinette électrique", "Les mêmes réflexes valent après une chute en {a}."),
        ("coup-du-lapin-indemnisation", "coup du lapin", "Les douleurs cervicales des jours suivants peuvent être un {a} : elles se notent, même si l'on a pu rentrer chez soi."),
    ],
    "refuser-offre-assurance-accident.html": [
        ("../guide-5-erreurs", "cinq erreurs", "Accepter trop vite est au cœur des {a}."),
        ("simulateur-dfp-capitalisation", "simulateur indicatif", "Un poste de déficit fonctionnel ou une rente peut être resitué avec le {a}, qui ne remplace pas l'expertise."),
        ("../accidents-route", "délais après un accident de la route", "Les {a} encadrent le moment où une offre doit être présentée."),
        ("expertise-medicale-judiciaire", "expertise judiciaire", "Si le rapport qui fonde l'offre est incomplet, une {a} peut être demandée."),
    ],
    "simulateur-dfp-capitalisation.html": [
        ("deficit-fonctionnel-permanent-dfp", "déficit fonctionnel permanent", "Le mode de calcul du {a} est expliqué à part : le simulateur n'en est qu'une illustration."),
        ("capitalisation-prejudice-euro-de-rente", "prix de l'euro de rente", "La méthode de capitalisation est détaillée dans l'article sur le {a}."),
        ("tierce-personne-indemnisation", "aide humaine sur plusieurs années", "Une {a} est l'un des postes que la capitalisation éclaire."),
        ("../guide-5-erreurs", "guide des cinq erreurs", "Ces ordres de grandeur aident à relire une proposition, avec le {a}, sans chiffrer le dossier à la place du juge."),
    ],
    "souffrances-endurees.html": [
        ("simulateur-dfp-capitalisation", "valeur du point de DFP", "Une cotation de souffrances n'est pas un taux de déficit : pour le taux, le {a} reste indicatif."),
        ("coup-du-lapin-indemnisation", "coup du lapin", "Un {a} est un exemple fréquent de souffrances discutées alors que l'imagerie est pauvre."),
        ("../accidents-route", "accident de la route", "Le poste existe après un {a} comme après une agression ou un accident médical."),
        ("../agression", "agression", "Il est aussi central après une {a}."),
    ],
    "tierce-personne-indemnisation.html": [
        ("simulateur-dfp-capitalisation", "capitalisation d'un coût annuel", "Les heures à vie se projettent par la {a}, selon un barème qui ne lie pas le juge."),
        ("indemnisation-accident-grave", "blessures les plus lourdes", "Le besoin est souvent au centre des {a}."),
        ("../accidents-route", "accident de la circulation", "Il apparaît dès que les gestes du quotidien ne peuvent plus être faits seul, par exemple après un {a}."),
        ("traumatisme-cranien-indemnisation", "traumatisme crânien", "Un {a} est l'une des situations où le besoin d'aide ne se voit pas toujours au premier regard."),
    ],
    "traumatisme-cranien-indemnisation.html": [
        ("../accidents-route", "accident de la route", "Beaucoup de traumatismes crâniens suivent un {a}."),
        ("tierce-personne-indemnisation", "tierce personne", "L'aide d'une {a} est souvent le poste le plus lourd, y compris lorsque la personne marche et parle."),
        ("preparer-expertise-medicale-accident-grave", "préparer l'expertise", "L'examen décide de la suite : la page pour {a} liste les points à ne pas laisser de côté."),
        ("simulateur-dfp-capitalisation", "simulateur de capitalisation", "Le coût futur de l'aide se situe, à titre indicatif, avec le {a}."),
    ],
}

CITY_A = [
    ("../avocat-aix-en-provence", "Aix-en-Provence"),
    ("../avocat-toulon", "Toulon"),
    ("../avocat-nice", "Nice"),
    ("../avocat-avignon", "Avignon"),
    ("../avocat-nimes", "Nîmes"),
    ("../avocat-montpellier", "Montpellier"),
]
CITY_B = [
    ("../avocat-aix-en-provence", "l'accompagnement à Aix-en-Provence"),
    ("../avocat-toulon", "le déplacement à Toulon"),
    ("../avocat-nice", "le suivi à Nice"),
    ("../avocat-avignon", "l'audience à Avignon"),
    ("../avocat-nimes", "l'expertise à Nîmes"),
    ("../avocat-montpellier", "le rendez-vous à Montpellier"),
]
CITY_LEADS = {
    "route": "Pour un accident de la circulation, Maître Ilan Guedj part de Marseille et se déplace aussi à {cities}.",
    "medical": "Pour un dossier médical, Maître Ilan Guedj se déplace depuis Marseille vers {cities}.",
    "agression": "Après une agression, Maître Ilan Guedj reçoit à Marseille et se déplace à {cities}.",
    "vie": "Pour un accident de la vie, Maître Ilan Guedj reçoit à Marseille et se déplace à {cities}.",
    "travail": "Un accident du travail ou de trajet se suit depuis Marseille, avec déplacement à {cities}.",
    "prejudice": "Maître Ilan Guedj étudie ces préjudices depuis Marseille et se déplace à {cities}.",
    "expertise": "Maître Ilan Guedj prépare ces expertises depuis Marseille et se déplace à {cities}.",
}
CITY_LEADS_B = {
    "route": "Selon le lieu de l'expertise ou de l'audience après un accident de la route, Maître Ilan Guedj assure aussi {cities}.",
    "medical": "Pour une expertise médicale hors Marseille, Maître Ilan Guedj assure aussi {cities}.",
    "agression": "Lorsque la procédure ou l'expertise a lieu hors Marseille, Maître Ilan Guedj assure aussi {cities}.",
    "vie": "Pour un accident de la vie suivi hors Marseille, Maître Ilan Guedj assure aussi {cities}.",
    "travail": "Pour l'expertise ou l'audience d'un accident du travail, Maître Ilan Guedj assure aussi {cities}.",
    "prejudice": "Lorsque l'expertise a lieu hors Marseille, Maître Ilan Guedj assure aussi {cities}.",
    "expertise": "Lorsque l'examen se tient hors Marseille, Maître Ilan Guedj assure aussi {cities}.",
}
CITY_KEYS = (
    "avocat-aix-en-provence",
    "avocat-toulon",
    "avocat-nice",
    "avocat-avignon",
    "avocat-nimes",
    "avocat-montpellier",
)

LINK_CLASS = "text-blue-600 hover:underline"
BANNED = re.compile(
    r"gratuit|meilleur avocat|n°\s*1|sous-évalu|arnaqu|cabinet|nous intervenons|100\s*%",
    re.I,
)


def norm_key(href):
    href = href.split("#")[0].split("?")[0].strip()
    href = href.rstrip("/").split("/")[-1]
    if href.endswith(".html"):
        href = href[:-5]
    return href


def column_bounds(src):
    start = src.find('lg:col-span-2')
    if start < 0:
        return None
    end = src.find("<!-- SIDEBAR -->", start)
    if end < 0:
        return None
    return start, end


def column_has(column, href):
    key = norm_key(href)
    for found in re.findall(r'href=["\']([^"\']+)', column):
        if norm_key(found) == key:
            return True
    return False


def esc(text):
    return html.escape(text, quote=False)


def a_tag(href, label):
    return f'<a href="{html.escape(href, quote=True)}" class="{LINK_CLASS}">{esc(label)}</a>'


def join_fr(parts):
    if len(parts) == 1:
        return parts[0]
    return ", ".join(parts[:-1]) + " et " + parts[-1]


def profile(name):
    data = dict(COPY[DOMAIN[name]])
    data.update(OVERRIDE.get(name, {}))
    return data


def h2_text(fragment):
    match = re.match(r"<h2\b[^>]*>(.*?)</h2>", fragment, re.S | re.I)
    if not match:
        return ""
    text = re.sub(r"<[^>]+>", "", match.group(1))
    return re.sub(r"\s+", " ", text).strip()


def indent_at(src, pos):
    line = src.rfind("\n", 0, pos) + 1
    return re.match(r"[ \t]*", src[line:]).group(0)


def indented(block, indent):
    lines = block.strip("\n").split("\n")
    return "\n".join((indent + line) if line else "" for line in lines)


def options_html(selected):
    rows = []
    for value, label in OPTIONS:
        sel = " selected" if value == selected else ""
        rows.append(
            f'<option value="{html.escape(value, quote=True)}"{sel}>{esc(label)}</option>'
        )
    return "\n".join("                  " + row for row in rows)


def contact_actions(location):
    return f"""<div class="flex flex-col sm:flex-row flex-wrap gap-3">
              <a href="{TEL}" data-cta-location="{location}" class="inline-flex items-center justify-center w-full sm:w-auto px-5 py-3 bg-white border border-gray-200 text-gray-900 rounded-xl font-bold text-sm hover:bg-gray-50 transition">Appeler</a>
              <a href="{WA}" data-cta-location="{location}" target="_blank" rel="noopener" class="inline-flex items-center justify-center w-full sm:w-auto px-5 py-3 bg-[#25D366] text-white rounded-xl font-bold text-sm hover:bg-green-600 transition">WhatsApp</a>
              <a href="{CAL}" data-cta-location="{location}" target="_blank" rel="noopener" class="inline-flex items-center justify-center w-full sm:w-auto px-5 py-3 bg-white border border-gray-200 text-gray-900 rounded-xl font-bold text-sm hover:bg-gray-50 transition">Prendre rendez-vous</a>
            </div>"""


def mid_block(info):
    return f"""          <!-- ARTICLE-CTA-MID:START -->
          <aside class="article-lead-mid my-10 bg-sand border border-gray-200 rounded-2xl p-6 lg:p-8" data-cta-location="article_mid">
            <p class="text-copper-600 text-xs font-bold uppercase tracking-widest mb-2">{esc(info["kicker"])}</p>
            <p class="font-display text-2xl font-bold mb-3">{esc(info["title"])}</p>
            <p class="text-gray-600 text-sm leading-relaxed mb-5">{esc(info["body"])}</p>
            <a href="#evaluer-mon-dossier" class="inline-flex items-center justify-center w-full sm:w-auto px-5 py-3 bg-blue-600 text-white rounded-xl font-bold text-sm hover:bg-blue-700 transition">Évaluer mon dossier</a>
            <p class="text-sm text-gray-500 mt-4">Ou joindre Maître Ilan Guedj au <a href="{TEL}" data-cta-location="article_mid" class="font-bold text-gray-900 hover:text-blue-700">06&nbsp;63&nbsp;46&nbsp;59&nbsp;84</a>, par <a href="{WA}" data-cta-location="article_mid" target="_blank" rel="noopener" class="{LINK_CLASS}">WhatsApp</a> ou <a href="{CAL}" data-cta-location="article_mid" target="_blank" rel="noopener" class="{LINK_CLASS}">en prenant rendez-vous</a>.</p>
          </aside>
          <!-- ARTICLE-CTA-MID:END -->"""


def end_block(info, name, title):
    slug = name[:-5]
    subject = html.escape(f"Demande d'évaluation — {title}"[:160], quote=True)
    actions = "\n".join("              " + line for line in contact_actions("article_end").split("\n"))
    return f"""          <!-- ARTICLE-CTA-END:START -->
          <aside id="evaluer-mon-dossier" class="article-lead-end scroll-mt-28 mt-12 mb-10 bg-white border border-gray-200 rounded-2xl p-6 lg:p-8 shadow-sm" data-cta-location="article_end" aria-labelledby="article-lead-title">
            <p class="text-copper-600 text-xs font-bold uppercase tracking-widest mb-2">{esc(info["kicker"])}</p>
            <h2 id="article-lead-title" class="text-2xl font-bold mb-3">Évaluer mon dossier</h2>
            <p class="text-gray-600 text-sm leading-relaxed mb-6">{esc(info["body"])}</p>
            <form class="js-article-lead space-y-3" action="{FORM_ACTION}" method="POST">
              <input type="hidden" name="_subject" value="{subject}">
              <input type="hidden" name="page" value="/blog/{slug}">
              <input type="hidden" name="source" value="article">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-1" for="article-lead-nom">Nom</label>
                  <input id="article-lead-nom" type="text" name="nom" required autocomplete="name" placeholder="Votre nom" class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition">
                </div>
                <div>
                  <label class="block text-xs font-bold text-gray-600 mb-1" for="article-lead-tel">Téléphone</label>
                  <input id="article-lead-tel" type="tel" name="telephone" required autocomplete="tel" inputmode="tel" placeholder="06 XX XX XX XX" class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition">
                </div>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-600 mb-1" for="article-lead-type">Type d'accident ou de préjudice</label>
                <select id="article-lead-type" name="type_accident" required class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition bg-white">
{options_html(info["select"])}
                </select>
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-600 mb-1" for="article-lead-message">Message <span class="font-medium text-gray-400">(facultatif)</span></label>
                <textarea id="article-lead-message" name="message" rows="3" placeholder="Date, circonstances, pièces déjà réunies…" class="w-full px-3 py-2.5 text-sm border border-gray-200 rounded-lg focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition resize-none"></textarea>
              </div>
              <div class="flex items-start gap-2">
                <input type="checkbox" name="consentement" id="article-lead-consent" required class="mt-0.5 rounded border-gray-300 text-blue-600 focus:ring-blue-500">
                <label for="article-lead-consent" class="text-[11px] text-gray-500 leading-tight">J'accepte que ces informations soient utilisées pour répondre à ma demande.</label>
              </div>
              <button type="submit" class="js-article-lead-submit w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 transition flex items-center justify-center gap-2">
                <span>Envoyer ma demande</span>
              </button>
              <p class="js-article-lead-success hidden bg-green-50 border border-green-200 rounded-xl p-4 text-center" role="status">
                <span class="text-green-800 font-bold text-sm">Demande envoyée.</span>
                <span class="block text-green-700 text-xs mt-1">Un retour vous sera fait pour convenir d'un échange.</span>
              </p>
            </form>
            <p class="text-[11px] text-gray-500 leading-relaxed mt-3">Ces informations servent uniquement à répondre à votre demande. Elles sont couvertes par le secret professionnel. <a href="/politique-confidentialite" class="underline hover:text-blue-700">Politique de confidentialité</a>.</p>
            <div class="mt-5">
{actions}
            </div>
            <p class="text-xs text-gray-500 mt-4">Les honoraires sont fixés par une convention écrite avant toute intervention. Le détail est sur la page <a href="../honoraires" class="{LINK_CLASS}">honoraires</a>.</p>
          </aside>
          <!-- ARTICLE-CTA-END:END -->"""


def city_paragraph(name, domain):
    style_b = sum(ord(c) for c in name) % 2 == 1
    cities = CITY_B if style_b else CITY_A
    # Rotation légère pour que la première ville ne soit pas toujours la même.
    shift = sum(ord(c) for c in name) % len(cities)
    cities = cities[shift:] + cities[:shift]
    rendered = [a_tag(href, label) for href, label in cities]
    if style_b:
        template = CITY_LEADS_B[domain]
        # « au déplacement » : on répète la préposition via les ancres déjà nominales.
        sentence = template.format(cities=join_fr(rendered))
    else:
        sentence = CITY_LEADS[domain].format(cities=join_fr(rendered))
    return f'<p class="text-sm text-gray-500 leading-relaxed">{sentence}</p>'


def maillage_block(name, column):
    parts = []
    for href, label, sentence in LINKS.get(name, []):
        if norm_key(href) == norm_key(name):
            continue
        if column_has(column, href):
            continue
        if "{a}" not in sentence:
            raise SystemExit(f"phrase sans {{a}} dans {name}")
        parts.append("<p class=\"text-gray-700 leading-relaxed\">" + sentence.replace("{a}", a_tag(href, label)) + "</p>")
    city = ""
    if not any(column_has(column, key) for key in CITY_KEYS):
        city = city_paragraph(name, DOMAIN[name])
    if not parts and not city:
        return ""
    inner = "\n            ".join(parts)
    if city:
        inner = (inner + "\n            " if inner else "") + city
    return f"""          <!-- MAILLAGE:START -->
          <div class="article-maillage mt-10 space-y-3">
            {inner}
          </div>
          <!-- MAILLAGE:END -->"""


def page_title(src):
    match = re.search(r"<h1\b[^>]*>(.*?)</h1>", src, re.S | re.I)
    if not match:
        return "article"
    text = re.sub(r"<[^>]+>", "", match.group(1))
    return re.sub(r"\s+", " ", html.unescape(text)).strip()


def insert_mid(src):
    if "ARTICLE-CTA-MID:START" in src:
        return src, None
    bounds = column_bounds(src)
    if not bounds:
        raise SystemExit("colonne article introuvable")
    start, end = bounds
    faq = src.find("<!-- FAQ -->", start, end)
    if faq < 0:
        raise SystemExit("FAQ introuvable")
    region = src[start:faq]
    positions = [m.start() for m in re.finditer(r"<h2\b", region, re.I)]
    if not positions:
        pos = faq
    else:
        idx = max(1, len(positions) // 2)
        if idx >= len(positions):
            idx = len(positions) - 1
        skip = ("textes et sources", "sources", "questions fréquentes", "articles liés", "pour aller plus loin")
        while idx > 0 and h2_text(region[positions[idx]:]).lower() in skip:
            idx -= 1
        while idx < len(positions) - 1:
            window = region[max(0, positions[idx] - 900):positions[idx]]
            if "CTA mi-article" in window or "ARTICLE-CTA-MID" in window:
                idx += 1
                continue
            break
        pos = start + positions[idx]
    info = None  # filled by caller via closure — set below
    return src, pos


def choose_mid_pos(src):
    start, end = column_bounds(src)
    faq = src.find("<!-- FAQ -->", start, end)
    region = src[start:faq]
    positions = [m.start() for m in re.finditer(r"<h2\b", region, re.I)]
    if not positions:
        return faq, "(avant la FAQ)"
    idx = max(1, len(positions) // 2)
    if idx >= len(positions):
        idx = len(positions) - 1
    skip = ("textes et sources", "sources", "questions fréquentes", "articles liés", "pour aller plus loin")
    while idx > 0 and h2_text(region[positions[idx]:]).lower() in skip:
        idx -= 1
    while idx < len(positions) - 1:
        window = region[max(0, positions[idx] - 900):positions[idx]]
        if "CTA mi-article" in window:
            idx += 1
            continue
        break
    return start + positions[idx], h2_text(region[positions[idx]:])


def insert_before(src, pos, block):
    line_start = src.rfind("\n", 0, pos) + 1
    indent = re.match(r"[ \t]*", src[line_start:]).group(0)
    lines = block.strip("\n").split("\n")
    nonempty = [line for line in lines if line.strip()]
    base = min(len(line) - len(line.lstrip(" ")) for line in nonempty)
    rebuilt = []
    for line in lines:
        if not line.strip():
            rebuilt.append("")
            continue
        rebuilt.append(indent + line[base:])
    return src[:line_start] + "\n".join(rebuilt) + "\n\n" + src[line_start:]


MOBILE_BAR = """  <div class="js-mobile-bar fixed bottom-6 left-4 right-4 z-50 md:hidden" data-cta-location="mobile_bar">
    <div class="bg-ink/90 backdrop-blur-xl p-2 rounded-2xl shadow-2xl flex gap-3 border border-white/10">
      <a href="https://wa.me/33663465984" class="flex-1 bg-[#25D366] text-white py-3 rounded-xl font-bold flex justify-center items-center gap-2 text-sm">WhatsApp</a>
      <a href="tel:+33663465984" class="flex-1 bg-white text-gray-900 py-3 rounded-xl font-bold flex justify-center items-center gap-2 text-sm">Appeler</a>
    </div>
  </div>
"""

SCRIPT = '  <script src="/js/conversions.js" defer></script>\n'


def add_chrome(src, blog_page):
    changed = False
    if "/js/conversions.js" not in src:
        if "</body>" not in src:
            raise SystemExit("balise body manquante")
        src = src.replace("</body>", SCRIPT + "</body>", 1)
        changed = True
    if blog_page and "js-mobile-bar" not in src:
        src = src.replace(SCRIPT, MOBILE_BAR + SCRIPT, 1)
        changed = True
    return src, changed


def check_block(name, block):
    if BANNED.search(block):
        raise SystemExit(f"wording à revoir dans {name} : {BANNED.search(block).group(0)}")


def process_article(path):
    name = path.name
    src = path.read_text(encoding="utf-8")
    original = src
    info = profile(name)
    notes = []
    if "ARTICLE-CTA-MID:START" not in src:
        pos, heading = choose_mid_pos(src)
        block = mid_block(info)
        check_block(name, block)
        src = insert_before(src, pos, block)
        notes.append(f"milieu avant « {heading} »")
    bounds = column_bounds(src)
    column = src[bounds[0]:bounds[1]]
    if "MAILLAGE:START" not in src:
        block = maillage_block(name, column)
        if block:
            check_block(name, block)
            faq = src.find("<!-- FAQ -->", bounds[0])
            src = insert_before(src, faq, block)
            notes.append("maillage")
    if "ARTICLE-CTA-END:START" not in src:
        block = end_block(info, name, page_title(src))
        check_block(name, block)
        related = src.find("<!-- Related articles -->")
        if related < 0:
            raise SystemExit(f"articles liés introuvables : {name}")
        src = insert_before(src, related, block)
        notes.append("formulaire")
    src, chrome = add_chrome(src, True)
    if src != original:
        path.write_text(src, encoding="utf-8")
    return notes


def main():
    articles = sorted(p for p in BLOG.glob("*.html") if p.name != "index.html")
    missing = sorted(set(DOMAIN) ^ {p.name for p in articles})
    if missing:
        raise SystemExit(f"écart domaine / fichiers : {missing}")
    for name in articles:
        if name.name not in LINKS:
            raise SystemExit(f"maillage absent : {name.name}")
    print(f"Articles : {len(articles)}")
    for path in articles:
        notes = process_article(path)
        print(f"  {path.name}: {', '.join(notes) if notes else 'inchangé'}")
    pages = sorted(ROOT.glob("*.html")) + sorted(BLOG.glob("*.html"))
    chrome_n = 0
    for path in pages:
        src = path.read_text(encoding="utf-8")
        updated, changed = add_chrome(src, path.parent.name == "blog")
        if changed:
            path.write_text(updated, encoding="utf-8")
            chrome_n += 1
    print(f"Script / barre ajoutés sur {chrome_n} page(s) encore sans inclusion.")


if __name__ == "__main__":
    main()
