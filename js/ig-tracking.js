/*
 * Suivi des prises de contact — ig-avocat.com
 * -------------------------------------------------------------
 * Pousse dans le dataLayer (GTM-WP82S37T) un événement par contact.
 * Noms d'événements STABLES — documentés dans TRACKING.md :
 *   clic_telephone      clic sur un lien tel:            (+ emplacement)
 *   clic_whatsapp       clic sur un lien WhatsApp        (+ emplacement)
 *   clic_calendly       ouverture du module Calendly     (+ emplacement) — intention, pas une conversion
 *   calendly_rdv        rendez-vous Calendly CONFIRMÉ (postMessage calendly.event_scheduled)
 *   form_submit         poussé par contact.html, après réponse OK de Formspree
 *   lead_magnet_submit  poussé par index.html, après réponse OK de Formspree
 *   exit_popup_cta      poussé par la popup de sortie (index.html), inchangé
 *
 * Un seul écouteur de clic (phase de capture) pour tout le site ; le script
 * se protège contre un double chargement et contre les doubles déclenchements.
 */
(function () {
  'use strict';
  if (window.__igTracking) return;
  window.__igTracking = true;

  var dataLayer = (window.dataLayer = window.dataLayer || []);
  var CALENDLY_URL = 'https://calendly.com/guedj-chiche-cohen';
  var lastPush = {};
  var lastCalendlyPlace = '';

  function pageType() {
    var p = location.pathname.replace(/\.html$/, '').replace(/\/+$/, '') || '/';
    if (p === '/' || p === '/index') return 'accueil';
    if (p === '/contact') return 'contact';
    if (/^\/avocat-(aix-en-provence|avignon|montpellier|nice|nimes|toulon)$/.test(p)) return 'ville';
    if (/^\/(accidents-route|accidents-vie|agression|erreur-medicale)$/.test(p)) return 'service';
    if (p.indexOf('/blog') === 0) return p === '/blog' || p === '/blog/index' ? 'blog_accueil' : 'article';
    return 'autre';
  }

  // Évite qu'un même clic (ou un double tap) compte deux fois.
  function push(eventName, params) {
    params = params || {};
    var key = eventName + '|' + (params.emplacement || '');
    var now = Date.now();
    if (lastPush[key] && now - lastPush[key] < 1500) return false;
    lastPush[key] = now;
    var payload = { event: eventName, page_type: pageType() };
    for (var k in params) if (Object.prototype.hasOwnProperty.call(params, k)) payload[k] = params[k];
    dataLayer.push(payload);
    return true;
  }
  window.igTrack = push;

  function isFixed(node) {
    try { return window.getComputedStyle(node).position === 'fixed'; } catch (e) { return false; }
  }

  // Emplacement du bouton : attribut data-cta s'il existe, sinon déduit du DOM.
  function placeOf(el) {
    var tagged = el.closest('[data-cta]');
    if (tagged) return tagged.getAttribute('data-cta');
    if (el.closest('#exit-popup')) return 'exit_popup';
    if (el.closest('#mobile-menu')) return 'menu_mobile';
    if (el.closest('#navbar, header')) return 'header';
    if (el.closest('footer')) return 'footer';
    for (var n = el; n && n !== document.body; n = n.parentElement) {
      if (isFixed(n)) return /(^|\s)md:hidden(\s|$)/.test(n.className || '') ? 'bouton_fixe_mobile' : 'bouton_flottant';
    }
    var sections = document.querySelectorAll('body > section, main > section');
    var sec = el.closest('section');
    if (sec && sections.length) {
      if (sec === sections[0]) return 'hero';
      if (sec === sections[sections.length - 1]) return 'fin_de_page';
    }
    if (el.closest('aside, .sticky')) return 'sidebar';
    return 'contenu';
  }

  function kindOf(el) {
    var href = (el.getAttribute('href') || '').toLowerCase();
    if (href.indexOf('tel:') === 0) return 'tel';
    if (/(^|\/\/)(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)\b|^whatsapp:/.test(href)) return 'whatsapp';
    if (el.hasAttribute('data-calendly') || href.indexOf('calendly.com') !== -1 ||
        /initPopupWidget/.test(el.getAttribute('onclick') || '')) return 'calendly';
    return '';
  }

  // ---- Calendly chargé à la demande pour les boutons [data-calendly] ----
  var calendlyLoading = null;
  function loadCalendly() {
    if (window.Calendly) return Promise.resolve();
    if (calendlyLoading) return calendlyLoading;
    calendlyLoading = new Promise(function (resolve, reject) {
      if (!document.querySelector('link[href*="assets.calendly.com/assets/external/widget.css"]')) {
        var css = document.createElement('link');
        css.rel = 'stylesheet';
        css.href = 'https://assets.calendly.com/assets/external/widget.css';
        document.head.appendChild(css);
      }
      var s = document.createElement('script');
      s.src = 'https://assets.calendly.com/assets/external/widget.js';
      s.async = true;
      s.onload = function () { window.Calendly ? resolve() : reject(); };
      s.onerror = reject;
      document.head.appendChild(s);
      setTimeout(reject, 6000);
    });
    return calendlyLoading;
  }
  function openCalendly(url) {
    loadCalendly().then(function () {
      window.Calendly.initPopupWidget({ url: url });
    }, function () {
      window.location.href = url; // repli : page Calendly classique
    });
  }

  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('a[href], button, [data-calendly]') : null;
    if (!el) return;
    var kind = kindOf(el);
    if (!kind) return;
    var place = placeOf(el);
    if (kind === 'tel') push('clic_telephone', { emplacement: place });
    else if (kind === 'whatsapp') push('clic_whatsapp', { emplacement: place });
    else if (kind === 'calendly') {
      lastCalendlyPlace = place;
      push('clic_calendly', { emplacement: place });
      if (el.hasAttribute('data-calendly')) {
        e.preventDefault();
        openCalendly(el.getAttribute('data-calendly-url') || el.getAttribute('href') || CALENDLY_URL);
      }
    }
  }, true);

  // ---- Rendez-vous Calendly réellement confirmé ----
  var seenKey = 'ig_calendly_rdv';
  function alreadySeen(id) {
    try {
      var list = JSON.parse(sessionStorage.getItem(seenKey) || '[]');
      if (list.indexOf(id) !== -1) return true;
      list.push(id);
      sessionStorage.setItem(seenKey, JSON.stringify(list));
    } catch (err) { /* stockage indisponible : on garde le dédoublonnage en mémoire */ }
    return false;
  }
  var seenInMemory = {};
  window.addEventListener('message', function (e) {
    if (!/^https:\/\/([a-z0-9-]+\.)?calendly\.com$/.test(e.origin || '')) return;
    var data = e.data;
    if (!data || data.event !== 'calendly.event_scheduled') return;
    var p = data.payload || {};
    var id = (p.invitee && p.invitee.uri) || (p.event && p.event.uri) || 'rdv';
    if (seenInMemory[id] || alreadySeen(id)) return;
    seenInMemory[id] = true;
    push('calendly_rdv', { emplacement: lastCalendlyPlace || (document.querySelector('.calendly-inline-widget') ? 'calendly_integre' : 'calendly') });
  });
})();
