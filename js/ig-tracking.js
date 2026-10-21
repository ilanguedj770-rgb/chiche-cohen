/*
 * Suivi des prises de contact — ig-avocat.com
 * -------------------------------------------------------------
 * Pousse dans le dataLayer (GTM-WP82S37T) un événement par contact.
 * Noms d'événements STABLES — documentés dans TRACKING.md :
 *   clic_telephone      clic sur un lien tel:            (+ emplacement) — historique GTM / Ads
 *   clic_whatsapp       clic sur un lien WhatsApp        (+ emplacement) — historique GTM / Ads
 *   clic_calendly       ouverture du module Calendly     (+ emplacement) — intention, pas une conversion
 *   calendly_rdv        rendez-vous Calendly CONFIRMÉ (postMessage calendly.event_scheduled)
 *   form_submit         poussé par contact.html, après réponse OK de Formspree
 *   lead_magnet_submit  poussé par index.html, après réponse OK de Formspree
 *   exit_popup_cta      poussé par la popup de sortie (index.html), inchangé
 *
 * Événements GA4 (mêmes clics, noms à déclarer comme événements clés) :
 *   click_phone, click_whatsapp, click_email, generate_lead
 *   paramètres : page_path, link_location (header | footer | corps | bouton flottant)
 *   generate_lead ajoute form_id. Poussés en objets dataLayer (pas un second
 *   gtag('event'), qui doublerait). Aucun cookie n'est posé ici : le Consent Mode
 *   (défaut « denied », posé avant GTM) décide si GA4 écrit un cookie.
 *
 * Un seul écouteur de clic (phase de capture) pour tout le site ; le script
 * se protège contre un double chargement et contre les doubles déclenchements.
 * Les noms historiques ne sont pas retirés : des balises GTM peuvent déjà les écouter.
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

  // Quatre emplacements demandés pour GA4. Le détail reste dans `emplacement`.
  function linkLocation(place) {
    if (place === 'header' || place === 'menu_mobile') return 'header';
    if (place === 'footer') return 'footer';
    if (place === 'bouton_fixe_mobile' || place === 'bouton_flottant') return 'bouton flottant';
    return 'corps';
  }

  function pagePath() {
    return location.pathname + location.search;
  }

  // Un seul objet dataLayer, le même format que clic_telephone : GTM le prend
  // comme événement personnalisé. gtag() ici n'est que le stub du Consent Mode ;
  // un second gtag('event') doublerait le hit si une balise écoute les deux.
  function sendGa4(eventName, params) {
    params = params || {};
    var loc = params.link_location || 'corps';
    var key = 'ga4|' + eventName + '|' + loc + '|' + (params.form_id || '');
    var now = Date.now();
    if (lastPush[key] && now - lastPush[key] < 1500) return false;
    lastPush[key] = now;
    var row = { event: eventName, page_path: pagePath(), link_location: loc };
    if (params.form_id) row.form_id = params.form_id;
    dataLayer.push(row);
    return true;
  }
  window.igLead = function (formId, el) {
    var place = el ? placeOf(el) : 'contenu';
    return sendGa4('generate_lead', { form_id: formId || 'contact-form', link_location: linkLocation(place) });
  };

  function kindOf(el) {
    var href = (el.getAttribute('href') || '').toLowerCase();
    if (href.indexOf('tel:') === 0) return 'tel';
    if (href.indexOf('mailto:') === 0) return 'email';
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
    // Un visiteur qui prend contact ne doit plus voir la fenêtre « Attention avant de partir ».
    try { sessionStorage.setItem('cc_popup_dismissed', '1'); } catch (err) {}
    var where = linkLocation(place);
    if (kind === 'tel') {
      push('clic_telephone', { emplacement: place });
      sendGa4('click_phone', { link_location: where });
    } else if (kind === 'whatsapp') {
      push('clic_whatsapp', { emplacement: place });
      sendGa4('click_whatsapp', { link_location: where });
    } else if (kind === 'email') {
      sendGa4('click_email', { link_location: where });
    } else if (kind === 'calendly') {
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

  // Formulaire de contact (Formspree) : le succès retire la classe « hidden ».
  function watchContactForm() {
    var form = document.getElementById('contact-form');
    var success = document.getElementById('form-success');
    if (!form || !success || success.getAttribute('data-ig-lead')) return;
    success.setAttribute('data-ig-lead', '1');
    var obs = new MutationObserver(function () {
      if (success.classList.contains('hidden')) return;
      window.igLead(form.id || 'contact-form', form);
      obs.disconnect();
    });
    obs.observe(success, { attributes: true, attributeFilter: ['class'] });
  }

  // ---- Barre d'appel mobile, seulement s'il n'y en a pas déjà une ----
  function classNameOf(node) {
    var cls = node && node.className;
    return typeof cls === 'string' ? cls : '';
  }
  function isDesktopOnlyFloat(node) {
    var cls = classNameOf(node);
    return /(^|\s)hidden(\s|$)/.test(cls) && /(^|\s)md:flex(\s|$)/.test(cls) && !/(^|\s)md:hidden(\s|$)/.test(cls);
  }
  function isSiteChrome(node) {
    if (!node) return false;
    var tag = (node.tagName || '').toLowerCase();
    if (tag === 'header' || tag === 'footer' || tag === 'nav') return true;
    return node.id === 'navbar' || node.id === 'mobile-menu';
  }
  function hasMobileFloat(matchHref) {
    if (document.querySelector('[data-cta="bouton_fixe_mobile"]')) return true;
    var links = document.querySelectorAll('a[href]');
    for (var i = 0; i < links.length; i++) {
      var href = (links[i].getAttribute('href') || '').toLowerCase();
      if (!matchHref(href)) continue;
      for (var n = links[i]; n && n !== document.body; n = n.parentElement) {
        if (isSiteChrome(n)) break;
        var cls = classNameOf(n);
        var fixed = /\bfixed\b/.test(cls);
        if (!fixed) {
          try { fixed = window.getComputedStyle(n).position === 'fixed'; } catch (err) {}
        }
        if (!fixed) continue;
        if (isDesktopOnlyFloat(n)) continue;
        return true;
      }
    }
    return false;
  }
  function isMobileViewport() {
    try { return window.matchMedia('(max-width: 767px)').matches; } catch (err) { return false; }
  }
  function placeCallbar(bar) {
    if (!bar) return;
    var lift = 0;
    var banner = document.querySelector('.igc');
    var bannerOpen = false;
    if (banner && banner.style.display !== 'none' && isMobileViewport()) {
      try {
        var rect = banner.getBoundingClientRect();
        bannerOpen = rect.height > 8 && rect.width > 8;
        if (bannerOpen) lift = Math.ceil(rect.height) + 24;
      } catch (err) { lift = 0; }
    }
    var bottom = lift ? lift + 'px' : '0px';
    if (bar.style.bottom !== bottom) bar.style.bottom = bottom;
    var pad = '0px';
    if (isMobileViewport()) {
      var barH = 72;
      try { barH = Math.ceil(bar.getBoundingClientRect().height) || 72; } catch (err2) {}
      pad = (barH + lift + 12) + 'px';
    }
    if (document.documentElement.style.getPropertyValue('--ig-callbar-pad') !== pad) {
      document.documentElement.style.setProperty('--ig-callbar-pad', pad);
    }
  }
  function ensureCallbar() {
    if (document.getElementById('ig-callbar')) return;
    var phone = hasMobileFloat(function (h) { return h.indexOf('tel:') === 0; });
    var wa = hasMobileFloat(function (h) { return /(^|\/\/)(wa\.me|api\.whatsapp\.com|web\.whatsapp\.com)\b|^whatsapp:/.test(h); });
    if (phone) return;
    var css = document.createElement('style');
    css.textContent =
      '.ig-callbar{display:none}' +
      '@media(max-width:767px){' +
      'body.ig-callbar-on{padding-bottom:var(--ig-callbar-pad,5.5rem)}' +
      '.ig-callbar{display:flex;position:fixed;z-index:40;left:12px;right:12px;bottom:0;' +
      'gap:8px;padding:8px;padding-bottom:calc(8px + env(safe-area-inset-bottom,0px));' +
      'background:rgba(255,255,255,.97);border:1px solid #e5e7eb;border-radius:16px;' +
      'box-shadow:0 12px 32px rgba(17,24,39,.14)}' +
      '.ig-callbar a{flex:1;min-height:48px;display:flex;align-items:center;justify-content:center;gap:8px;' +
      'border-radius:12px;padding:10px 12px;font:700 14px/1.2 Inter,system-ui,-apple-system,"Segoe UI",sans-serif;' +
      'text-decoration:none;text-align:center}' +
      '.ig-callbar a:focus-visible{outline:3px solid #2563eb;outline-offset:2px}' +
      '.ig-callbar .ig-call{background:#111827;color:#fff}' +
      '.ig-callbar .ig-wa{background:#075E54;color:#fff}' +
      '.ig-callbar svg{width:18px;height:18px;flex:none}' +
      '}';
    document.head.appendChild(css);
    var bar = document.createElement('div');
    bar.id = 'ig-callbar';
    bar.className = 'ig-callbar';
    bar.setAttribute('data-cta', 'bouton_flottant');
    bar.setAttribute('role', 'region');
    bar.setAttribute('aria-label', 'Contacter le cabinet');
    var phoneIcon = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></svg>';
    var html = '<a class="ig-call" href="tel:+33663465984" aria-label="Appeler le cabinet au 06 63 46 59 84">' + phoneIcon + '<span>Appeler le cabinet</span></a>';
    if (!wa) {
      html += '<a class="ig-wa" href="https://wa.me/33663465984" target="_blank" rel="noopener" aria-label="Écrire au cabinet sur WhatsApp">' +
        '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M20.5 3.5A11 11 0 0 0 2.1 17.2L1 23l5.9-1.1A11 11 0 0 0 20.5 3.5zM12 20.2a8.2 8.2 0 0 1-4.2-1.1l-.3-.2-3.1.6.6-3-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.4-.7-1.6-.8s-.4-.1-.5.1-.6.8-.7.9-.3.2-.5.1a6.7 6.7 0 0 1-2-1.2 7.4 7.4 0 0 1-1.4-1.7c-.1-.2 0-.4.1-.5l.4-.4.2-.3a.5.5 0 0 0 0-.5c0-.1-.5-1.2-.7-1.6s-.4-.4-.5-.4h-.4a.8.8 0 0 0-.6.3 2.4 2.4 0 0 0-.8 1.8 4.2 4.2 0 0 0 .9 2.2 9.6 9.6 0 0 0 3.6 3.2 4 4 0 0 0 2.5.7 2.1 2.1 0 0 0 1.4-.7 1.7 1.7 0 0 0 .4-1.2c0-.1 0-.3-.2-.4z"/></svg>' +
        '<span>WhatsApp</span></a>';
    }
    bar.innerHTML = html;
    document.body.appendChild(bar);
    document.body.classList.add('ig-callbar-on');
    placeCallbar(bar);
    window.addEventListener('resize', function () { placeCallbar(bar); });
    function bindBanner() {
      var banner = document.querySelector('.igc');
      if (!banner || banner.getAttribute('data-ig-bound')) return;
      banner.setAttribute('data-ig-bound', '1');
      var mo = new MutationObserver(function () { placeCallbar(bar); });
      mo.observe(banner, { attributes: true, attributeFilter: ['style', 'class'] });
      placeCallbar(bar);
    }
    bindBanner();
    var rootMo = new MutationObserver(function () { bindBanner(); });
    rootMo.observe(document.body, { childList: true, subtree: true });
  }

  function bootUi() {
    watchContactForm();
    ensureCallbar();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', bootUi);
  else bootUi();
})();
