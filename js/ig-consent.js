/*
 * Bandeau de consentement aux cookies + Google Consent Mode v2 — ig-avocat.com
 * ---------------------------------------------------------------------------
 * Le consentement par défaut (tout « denied ») est posé par un petit script
 * inline placé AVANT le conteneur GTM dans chaque page (marqueur
 * CONSENT:DEFAULT). Ce fichier affiche le bandeau, enregistre le choix et
 * envoie gtag('consent','update',…).
 *
 * Choix conservé 6 mois (recommandation CNIL), puis redemandé.
 * Refuser est aussi simple qu'accepter (deux boutons de même niveau).
 * Lien « Gestion des cookies » : tout élément [data-consent-open].
 * Événement dataLayer : consent_update (analytics, ads, personalization).
 */
(function () {
  'use strict';
  if (window.__igConsent) return;
  window.__igConsent = true;

  var KEY = 'ig_consent';
  var MAX_AGE = 1000 * 60 * 60 * 24 * 182; // ~6 mois
  window.dataLayer = window.dataLayer || [];
  var gtag = window.gtag || function () { window.dataLayer.push(arguments); };

  function read() {
    try {
      var c = JSON.parse(localStorage.getItem(KEY) || 'null');
      if (c && c.v === 1 && Date.now() - c.t < MAX_AGE) return c;
    } catch (e) {}
    return null;
  }
  function save(a, m, p) {
    var c = { v: 1, t: Date.now(), a: !!a, m: !!m, p: !!p };
    try { localStorage.setItem(KEY, JSON.stringify(c)); } catch (e) {}
    var s = function (b) { return b ? 'granted' : 'denied'; };
    gtag('consent', 'update', {
      analytics_storage: s(c.a),
      ad_storage: s(c.m),
      ad_user_data: s(c.m),
      ad_personalization: s(c.p)
    });
    window.dataLayer.push({ event: 'consent_update', consent_analytics: c.a, consent_ads: c.m, consent_personalization: c.p });
    return c;
  }

  // Bandeau compact : sur mobile il ne doit jamais masquer les boutons d'appel
  // du haut de page (refonte de novembre 2026). Refuser reste aussi simple qu'accepter.
  var css =
    '.igc{position:fixed;z-index:2147483000;left:12px;right:12px;bottom:12px;max-width:520px;margin:0 auto;' +
    'background:#fff;color:#38352E;border:1px solid rgba(27,36,48,.12);border-radius:18px;box-shadow:0 20px 50px -12px rgba(27,36,48,.35);' +
    'padding:14px 16px;font:13px/1.45 Inter,system-ui,-apple-system,"Segoe UI",sans-serif}' +
    '@media(min-width:768px){.igc{left:24px;right:auto;bottom:24px;margin:0;padding:20px;font-size:14px;line-height:1.5}}' +
    '.igc h2{display:none;font-family:Fraunces,Georgia,serif;font-size:17px;font-weight:600;margin:0 0 6px;color:#1B2430}' +
    '@media(min-width:768px){.igc h2{display:block}}.igc.igc-open h2{display:block}' +
    '.igc p{margin:0 0 10px;color:#5C574E;line-height:inherit}' +
    '@media(min-width:768px){.igc p{margin-bottom:14px}}' +
    '.igc a{color:#1E40AF;text-decoration:underline}' +
    '.igc-row{display:flex;flex-wrap:wrap;gap:8px;align-items:center}' +
    '.igc-b{flex:1 1 0;min-height:44px;padding:8px 8px;border-radius:999px;font-weight:700;font-size:13px;white-space:nowrap;cursor:pointer;' +
    'border:1px solid #1B2430;background:#1B2430;color:#fff}' +
    '@media(min-width:768px){.igc-b{font-size:14px;padding:8px 14px}}' +
    '.igc-b.igc-l{flex:0 0 auto;min-height:44px;background:transparent;color:#38352E;border-color:transparent;text-decoration:underline;' +
    'text-underline-offset:3px;font-weight:600;padding:8px 6px}' +
    '.igc.igc-open .igc-b.igc-l{flex:1 1 100%;background:#fff;border-color:#C9C2B5;text-decoration:none;font-weight:700}' +
    '.igc-b:focus-visible,.igc-t input:focus-visible{outline:3px solid #1E40AF;outline-offset:2px}' +
    '.igc-opts{margin:4px 0 14px;display:none}.igc.igc-open .igc-opts{display:block}' +
    '.igc-t{display:flex;gap:12px;align-items:flex-start;padding:10px 0;border-top:1px solid #F1ECE3}' +
    '.igc-t input{margin-top:3px;width:18px;height:18px;flex:none;accent-color:#1B2430}' +
    '.igc-t strong{display:block;color:#1B2430}.igc-t span{color:#5C574E;font-size:13px}' +
    '.igc .igc-save{display:none}.igc.igc-open .igc-save{display:block}.igc.igc-open .igc-more{display:none}' +
    '.igc.igc-open{max-height:calc(100dvh - 24px);overflow-y:auto}';

  var box = null;
  function build() {
    if (box) return box;
    var st = document.createElement('style');
    st.textContent = css;
    document.head.appendChild(st);
    box = document.createElement('div');
    box.className = 'igc';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-modal', 'false');
    box.setAttribute('aria-labelledby', 'igc-title');
    box.innerHTML =
      '<h2 id="igc-title">Cookies de mesure</h2>' +
      '<p>Avec votre accord, ce site utilise des cookies Google (Analytics et Ads) pour mesurer sa fréquentation et ses annonces. ' +
      'Vous pouvez refuser : rien ne change pour vous. <a href="/mentions-legales#cookies">En savoir plus</a></p>' +
      '<div class="igc-opts" id="igc-opts">' +
      '<label class="igc-t"><input type="checkbox" checked disabled><span><strong>Nécessaires</strong>Mémorisation de votre choix. Toujours actifs.</span></label>' +
      '<label class="igc-t"><input type="checkbox" data-k="a"><span><strong>Mesure d\'audience</strong>Google Analytics : pages vues, contacts, statistiques anonymisées.</span></label>' +
      '<label class="igc-t"><input type="checkbox" data-k="m"><span><strong>Mesure des annonces</strong>Google Ads : savoir si une annonce a conduit à une prise de contact.</span></label>' +
      '<label class="igc-t"><input type="checkbox" data-k="p"><span><strong>Personnalisation publicitaire</strong>Google Ads : afficher des annonces du cabinet aux personnes ayant visité le site.</span></label>' +
      '</div>' +
      '<div class="igc-row">' +
      '<button type="button" class="igc-b" data-act="refuse">Tout refuser</button>' +
      '<button type="button" class="igc-b" data-act="accept">Tout accepter</button>' +
      '<button type="button" class="igc-b igc-l igc-more" data-act="more" aria-controls="igc-opts" aria-expanded="false">Personnaliser</button>' +
      '<button type="button" class="igc-b igc-l igc-save" data-act="save">Enregistrer mes choix</button>' +
      '</div>';
    box.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]');
      if (!b) return;
      var act = b.getAttribute('data-act');
      if (act === 'accept') { save(1, 1, 1); hide(); }
      else if (act === 'refuse') { save(0, 0, 0); hide(); }
      else if (act === 'more') { box.classList.add('igc-open'); b.setAttribute('aria-expanded', 'true'); }
      else if (act === 'save') {
        var v = {};
        box.querySelectorAll('input[data-k]').forEach(function (i) { v[i.getAttribute('data-k')] = i.checked; });
        save(v.a, v.m, v.p); hide();
      }
    });
    document.body.appendChild(box);
    return box;
  }
  function show(detailed) {
    build();
    var c = read();
    box.querySelectorAll('input[data-k]').forEach(function (i) { i.checked = !!(c && c[i.getAttribute('data-k')]); });
    box.classList.toggle('igc-open', !!detailed);
    box.style.display = '';
    if (detailed) {
      var first = box.querySelector('input[data-k]');
      if (first) try { first.focus({ preventScroll: true }); } catch (e) {}
    }
  }
  function hide() { if (box) box.style.display = 'none'; }

  document.addEventListener('click', function (e) {
    var o = e.target.closest && e.target.closest('[data-consent-open]');
    if (o) { e.preventDefault(); show(true); }
  });

  function init() { if (!read()) show(false); }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
