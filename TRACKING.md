# Suivi des contacts (dataLayer → GTM → GA4 / Google Ads)

Conteneur : **GTM-WP82S37T** · GA4 : **G-FPFB23GW4P**
Script : `/js/ig-tracking.js`, chargé (`defer`) sur toutes les pages.
Appels à l'action : `tools/cta-inject.py` (idempotent, marqueurs `<!-- CTA:…:START/END -->`).

## Événements — noms stables, ne pas renommer

| Événement | Quand il part | Paramètres | Usage Google Ads |
|---|---|---|---|
| `clic_telephone` | clic sur un lien `tel:` | `emplacement`, `page_type` | **Conversion principale** |
| `clic_whatsapp` | clic sur un lien WhatsApp (`wa.me`) | `emplacement`, `page_type` | **Conversion principale** |
| `form_submit` | formulaire de contact Formspree envoyé **avec succès** (contact.html) | `form_name: contact_form` | **Conversion principale** |
| `calendly_rdv` | rendez-vous Calendly **confirmé** (`postMessage calendly.event_scheduled`) | `emplacement` (bouton qui a ouvert Calendly), `page_type` | **Conversion principale** (la plus qualifiée) |
| `lead_magnet_submit` | formulaire du guide gratuit envoyé avec succès (index.html) | — | Conversion secondaire |
| `clic_calendly` | ouverture du module Calendly (intention, pas un RDV) | `emplacement`, `page_type` | Ne pas importer comme conversion |
| `exit_popup_cta` | clic dans la popup de sortie (inchangé) | `action: whatsapp / calendly` | Ne pas importer (le clic WhatsApp de la popup envoie aussi `clic_whatsapp`, `emplacement: exit_popup`) |
| `exit_popup_shown` | affichage de la popup de sortie (inchangé) | — | Analyse seulement |

### Valeurs de `emplacement`
`header`, `menu_mobile`, `hero`, `milieu`, `sidebar`, `fin_de_page`, `footer`,
`bouton_fixe_mobile`, `bouton_flottant`, `exit_popup`, `diagnostic`, `contenu`,
`calendly_integre` (widget Calendly de la page contact).
Un bloc peut forcer sa valeur avec l'attribut `data-cta="…"` ; sinon elle est déduite du DOM.

### `page_type`
`accueil`, `service`, `ville`, `article`, `blog_accueil`, `contact`, `autre`.

## Événements GA4 à déclarer comme événements clés

Le même script pousse aussi dans le dataLayer (le canal déjà utilisé par GTM ; le `gtag()` de la page ne sert qu'au Consent Mode) des noms destinés à GA4. Paramètres : `page_path` (chemin + query) et `link_location`.

| Événement clé | Quand il part | `link_location` | Autre paramètre |
|---|---|---|---|
| `click_phone` | clic sur un lien `tel:` | `header`, `footer`, `corps` ou `bouton flottant` | — |
| `click_whatsapp` | clic sur un lien `wa.me` | idem | — |
| `click_email` | clic sur un lien `mailto:` | idem | — |
| `generate_lead` | formulaire de contact Formspree envoyé avec succès (`#contact-form`) | emplacement du formulaire (en pratique `corps`) | `form_id` (`contact-form`) |

`header` regroupe l'en-tête et le menu mobile. `bouton flottant` regroupe la barre fixe mobile et le bouton WhatsApp desktop. Tout le reste (hero, milieu, fin de page, barre latérale) est `corps`.

Aucun cookie n'est écrit par ce script. `analytics_storage` reste `denied` tant que le visiteur n'a pas accepté ; le Consent Mode laisse partir un ping sans cookie.

Le guide gratuit (`lead_magnet_submit`) n'est pas un `generate_lead` : ce n'est pas le formulaire de contact.

### Doublon possible dans GTM (conteneur non lisible depuis le dépôt)

Les clics téléphone et WhatsApp envoient **aussi** `clic_telephone` et `clic_whatsapp`. Le succès du formulaire envoie **aussi** `form_submit`. Si le conteneur GTM-WP82S37T a déjà une balise GA4 sur ces noms historiques, elle comptera deux fois la même action dès qu'une balise écoutera `click_phone`, `click_whatsapp` ou `generate_lead`.

À faire dans GTM, une seule fois : une balise GA4 « Événement » par nom clé (`click_phone`, `click_whatsapp`, `click_email`, `generate_lead`), paramètres `page_path`, `link_location` et `form_id`. Ne pas laisser en plus une balise GA4 sur `clic_telephone`, `clic_whatsapp` ou `form_submit`. Les balises Google Ads branchées sur les noms historiques, si elles existent déjà, peuvent rester : ce ne sont pas des événements GA4. `clic_calendly` ne doit pas être un événement clé.

## Garde-fous contre les doublons
- Un seul écouteur de clic pour tout le site ; le script ne s'exécute qu'une fois même s'il est inclus deux fois.
- Même événement + même emplacement dans un intervalle de 1,5 s : compté une seule fois (double tap).
- `calendly_rdv` : dédoublonné par l'identifiant de l'invité (sessionStorage), origine `calendly.com` vérifiée.
- `form_submit` / `lead_magnet_submit` restent poussés par le code des formulaires, **après** la réponse OK de Formspree — le script ne les pousse pas une seconde fois.
- Dans GTM, ne pas ajouter en plus des déclencheurs « Clic – liens » sur `tel:` / `wa.me` : ils doubleraient les conversions.

## Configuration GTM à faire (une fois)
1. Variables de couche de données : `emplacement`, `page_type`, `form_name`.
2. Déclencheurs « Événement personnalisé » : `clic_telephone`, `clic_whatsapp`, `form_submit`, `calendly_rdv`, `lead_magnet_submit`.
3. Balises GA4 « Événement » (ID G-FPFB23GW4P) sur chacun, avec les paramètres `emplacement` et `page_type` ; marquer les 4 conversions principales comme événements clés dans GA4.
4. Google Ads : créer une action de conversion par événement principal, puis une balise « Suivi des conversions Google Ads » par déclencheur (+ balise « Linker de conversion » sur toutes les pages). Comptage recommandé : « Une » conversion par clic.
5. Tester en mode Aperçu GTM (desktop et mobile), puis publier.

## Calendly
Les boutons `[data-calendly]` chargent le widget Calendly à la demande et l'ouvrent en popup.
Si le widget ne charge pas, le visiteur est envoyé sur la page Calendly (le RDV n'est alors pas mesuré).

## Consentement (Consent Mode v2)
- `js/ig-consent.js` affiche le bandeau (Tout refuser / Tout accepter / Personnaliser) et mémorise le choix 6 mois (`localStorage` « ig_consent »).
- Un script inline placé avant GTM (marqueur `CONSENT-DEFAULT`) pose par défaut `ad_storage`, `ad_user_data`, `ad_personalization` et `analytics_storage` à `denied`, puis rejoue le choix déjà enregistré. Il fixe aussi `ads_data_redaction`, `url_passthrough` et `cookie_expires` (13 mois).
- Les balises Google de GTM respectent ces signaux d'elles-mêmes : sans accord, elles envoient des pings sans cookie et Google modélise les conversions.
- Événement `consent_update` (consent_analytics, consent_ads, consent_personalization) à chaque choix.
- Lien « Gestion des cookies » dans chaque pied de page (`[data-consent-open]`) ; rubrique 7 des mentions légales (`/mentions-legales#cookies`).

## GoatCounter (mesure sans cookie)

Complément de GA4, **hors** du bandeau de consentement et du Consent Mode. Compte hébergé : `https://ig-avocat.goatcounter.com` (serveurs Hetzner, Finlande et Allemagne). Le script officiel `count.js` (licence ISC, en-tête conservé) est copié dans `/js/goatcounter-count.js` : aucune page ne charge ce fichier depuis un domaine tiers.

Inclusion unique, marqueurs `<!-- GOATCOUNTER:START -->` / `<!-- GOATCOUNTER:END -->`, posée par `tools/cta-inject.py` (et par les gabarits `tools/publish-geo-content.py` et `tools/build-lexique.py`) :

```html
<script data-goatcounter="https://ig-avocat.goatcounter.com/count" async src="/js/goatcounter-count.js"></script>
```

### Réglages du compte

- Rétention : **760 jours** (25 mois au maximum, comme indiqué dans la rubrique 7 des mentions légales).
- Sessions **sans stockage** : pas de cookie, rien n'est écrit sur l'appareil pour la mesure.
- Pas de pageviews individuelles : seules des statistiques agrégées sont conservées.
- Aucune donnée personnelle n'est envoyée : pas de numéro de téléphone, pas d'adresse e-mail, pas d'identifiant Calendly, pas de contenu de formulaire.
- La mesure elle-même n'écrit rien sur l'appareil. La seule écriture locale du script officiel est l'opt-out explicite du visiteur qui ouvre une page avec l'ancre `#toggle-goatcounter`.

### Événements

`js/ig-tracking.js` appelle `window.goatcounter.count({ path, title, event: true })` au même moment que l'événement dataLayer correspondant. `path` est le nom ci-dessous. `title` est **uniquement** la valeur `emplacement` déjà calculée (`header`, `footer`, `hero`…). Le dédoublonnage de 1,5 s (même événement, même emplacement) est celui de `clic_telephone` / `clic_whatsapp` / `clic_calendly`. `rdv-calendly` reprend le dédoublonnage de `calendly_rdv` (l'identifiant de l'invité sert à ne pas compter deux fois ; il n'est pas transmis). Si `goatcounter.count` n'est pas encore disponible, l'appel est ignoré dans un `try/catch` : aucune file d'attente.

| `path` | Quand il part | `title` |
|---|---|---|
| `clic-telephone` | clic sur un lien `tel:` | `emplacement` |
| `clic-whatsapp` | clic sur un lien `wa.me` | `emplacement` |
| `clic-calendly` | ouverture du module Calendly | `emplacement` |
| `rdv-calendly` | rendez-vous confirmé (`calendly.event_scheduled`) | `emplacement` du bouton |
| `formulaire-contact` | succès Formspree de `contact.html`, au même moment que `form_submit` | `emplacement` du formulaire |
| `guide-gratuit` | succès du guide gratuit sur `index.html`, au même moment que `lead_magnet_submit` | `emplacement` du formulaire |

Les noms dataLayer (`clic_telephone`, `form_submit`, etc.) et les événements GA4 ne changent pas. Cette mesure est exemptée de consentement (article 82 de la loi Informatique et Libertés et lignes directrices CNIL sur les traceurs de mesure d'audience).
