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
