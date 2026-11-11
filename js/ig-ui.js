/*
 * Interface commune — ig-avocat.com
 * ---------------------------------------------------------------------------
 * Chargé en différé sur toutes les pages (injecté par tools/layout.py).
 * Tout est une amélioration progressive : sans ce fichier, le site reste
 * entièrement lisible et navigable.
 *
 *   1. lien d'évitement « Aller au contenu »
 *   2. barre de navigation : état au défilement, menu « Domaines », menu mobile
 *   3. recherche dans le site (bouton loupe, touche « / » ou Ctrl/Cmd + K)
 *   4. guides : barre de progression, sommaire, partage
 *   5. retour en haut de page
 *   6. calculateur d'échéances ([data-ig-echeances])
 *   7. module Calendly intégré, chargé à l'approche (page contact)
 *
 * Les styles vivent dans css/input.css (classes .ig-*), jamais ici.
 */
(function () {
  'use strict';
  if (window.__igUi) return;
  window.__igUi = true;

  var d = document;
  var push = function (o) { (window.dataLayer = window.dataLayer || []).push(o); };
  var $ = function (s, r) { return (r || d).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || d).querySelectorAll(s)); };
  function el(tag, attrs, html) {
    var n = d.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html != null) n.innerHTML = html;
    return n;
  }
  function esc(s) {
    return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; });
  }
  function svg(paths, cls) {
    return '<svg class="' + (cls || 'ig-i') + '" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" ' +
      'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + paths + '</svg>';
  }
  // Tracés Lucide (licence ISC), comme dans le reste du site.
  var I = {
    chevron: '<path d="m6 9 6 6 6-6"/>',
    arrow: '<path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>',
    up: '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
    search: '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    car: '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"/><circle cx="7" cy="17" r="2"/><path d="M9 17h6"/><circle cx="17" cy="17" r="2"/>',
    bike: '<circle cx="18.5" cy="17.5" r="3.5"/><circle cx="5.5" cy="17.5" r="3.5"/><circle cx="15" cy="5" r="1"/><path d="M12 17.5V14l-3-3 4-3 2 3h2"/>',
    walk: '<circle cx="13" cy="4" r="1.5"/><path d="m7 21 3-7"/><path d="m10 14 3 2 1 5"/><path d="M10 14 9 9l4-1 3 3 3 1"/><path d="M9 9 6 11l-1 3"/>',
    steth: '<path d="M11 2v2"/><path d="M5 2v2"/><path d="M5 3H4a2 2 0 0 0-2 2v4a6 6 0 0 0 12 0V5a2 2 0 0 0-2-2h-1"/><path d="M8 15a6 6 0 0 0 12 0v-3"/><circle cx="20" cy="10" r="2"/>',
    shield: '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/>',
    home: '<path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"/><path d="M3 10a2 2 0 0 1 .709-1.528l7-5.999a2 2 0 0 1 2.582 0l7 5.999A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>',
    pin: '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"/><circle cx="12" cy="10" r="3"/>',
    list: '<path d="M3 12h.01"/><path d="M3 18h.01"/><path d="M3 6h.01"/><path d="M8 12h13"/><path d="M8 18h13"/><path d="M8 6h13"/>',
    link: '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    share: '<path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/><path d="m16 6-4-4-4 4"/><path d="M12 2v13"/>',
    doc: '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    book: '<path d="M12 7v14"/><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"/>',
    x: '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>'
  };

  var DOMAINES = [
    ['/accidents-route', 'Accident de la route', 'Conducteur, passager, loi Badinter', 'car'],
    ['/accident-moto-marseille', 'Accident de moto', 'Motard conducteur ou passager', 'bike'],
    ['/pieton-cycliste-marseille', 'Piéton et cycliste', 'Victime non conductrice', 'walk'],
    ['/erreur-medicale', 'Erreur médicale', 'Faute, aléa, infection nosocomiale', 'steth'],
    ['/agression', 'Agression', 'CIVI, Fonds de garantie', 'shield'],
    ['/accidents-vie', 'Accident de la vie', 'Chute, accident domestique, sport', 'home']
  ];
  var VILLES = [
    ['/avocat-dommage-corporel-bouches-du-rhone', 'Marseille et Bouches-du-Rhône'],
    ['/avocat-aix-en-provence', 'Aix-en-Provence'], ['/avocat-toulon', 'Toulon'], ['/avocat-nice', 'Nice'],
    ['/avocat-avignon', 'Avignon'], ['/avocat-nimes', 'Nîmes'], ['/avocat-montpellier', 'Montpellier']
  ];

  var nav = d.getElementById('navbar');
  var reduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* 1. Lien d'évitement ---------------------------------------------------- */
  (function () {
    var target = d.getElementById('contenu') || $('main');
    if (!target) return;
    if (!target.id) target.id = 'contenu';
    target.setAttribute('tabindex', '-1');
    var a = el('a', { href: '#' + target.id, 'class': 'ig-skip' }, 'Aller au contenu');
    d.body.insertBefore(a, d.body.firstChild);
  })();

  /* 2. Navigation ---------------------------------------------------------- */
  if (nav) {
    var onScroll = function () { nav.toggleAttribute('data-scrolled', window.scrollY > 12); };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    // Menu « Domaines » (ordinateur) : le lien simple devient un bouton à panneau.
    var trigger = $('a[data-ig-domaines]', nav);
    if (trigger) {
      var wrap = el('div', { 'class': 'ig-dd' });
      var btn = el('button', { type: 'button', 'class': trigger.className + ' ig-dd-btn', 'aria-expanded': 'false', 'aria-controls': 'ig-dd-panel' },
        'Domaines' + svg(I.chevron, 'ig-i ig-dd-chev'));
      var panel = el('div', { id: 'ig-dd-panel', 'class': 'ig-dd-panel', hidden: '' },
        '<div class="ig-dd-grid"><div><p class="ig-dd-title">Votre situation</p><ul class="ig-dd-list">' +
        DOMAINES.map(function (x) {
          return '<li><a href="' + x[0] + '" class="ig-dd-item"><span class="ig-dd-ico">' + svg(I[x[3]]) + '</span><span><strong>' + x[1] +
            '</strong><small>' + x[2] + '</small></span></a></li>';
        }).join('') + '</ul></div><div class="ig-dd-side"><p class="ig-dd-title">Près de chez vous</p><ul>' +
        VILLES.map(function (x) { return '<li><a href="' + x[0] + '">' + x[1] + '</a></li>'; }).join('') +
        '</ul></div></div><a href="/dossier-en-ligne" data-cta="nav_menu_dossier" class="ig-dd-foot"><span><strong>Accident de la route ?</strong> ' +
        'Ouvrez votre dossier en ligne, en 15 minutes depuis votre téléphone.</span>' + svg(I.arrow) + '</a>');
      trigger.parentNode.replaceChild(wrap, trigger);
      wrap.appendChild(btn);
      wrap.appendChild(panel);
      var closeTimer = null;
      var setOpen = function (open) {
        clearTimeout(closeTimer);
        panel.hidden = !open;
        btn.setAttribute('aria-expanded', String(open));
        wrap.classList.toggle('ig-dd-open', open);
      };
      btn.addEventListener('click', function () { setOpen(panel.hidden); });
      if (window.matchMedia('(hover: hover)').matches) {
        wrap.addEventListener('mouseenter', function () { setOpen(true); });
        wrap.addEventListener('mouseleave', function () { closeTimer = setTimeout(function () { setOpen(false); }, 180); });
      }
      wrap.addEventListener('focusout', function (e) { if (!wrap.contains(e.relatedTarget)) setOpen(false); });
      d.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && !panel.hidden) { setOpen(false); btn.focus(); }
      });
      d.addEventListener('click', function (e) { if (!wrap.contains(e.target)) setOpen(false); });
    }

    // Menu mobile : les domaines sont accessibles sans passer par l'accueil.
    var menu = d.getElementById('mobile-menu');
    var mbtn = d.getElementById('mobile-menu-btn');
    if (menu) {
      var first = $('a[href="/#expertises"]', menu);
      if (first) {
        var det = el('details', { 'class': 'ig-mm' },
          '<summary>Domaines' + svg(I.chevron, 'ig-i ig-dd-chev') + '</summary><ul>' +
          DOMAINES.map(function (x) { return '<li><a href="' + x[0] + '">' + svg(I[x[3]]) + x[1] + '</a></li>'; }).join('') + '</ul>');
        first.parentNode.replaceChild(det, first);
      }
      var closeMenu = function () {
        if (menu.classList.contains('hidden')) return;
        menu.classList.add('hidden');
        if (mbtn) mbtn.setAttribute('aria-expanded', 'false');
      };
      d.addEventListener('keydown', function (e) { if (e.key === 'Escape') closeMenu(); });
      d.addEventListener('click', function (e) { if (!nav.contains(e.target)) closeMenu(); });
    }
  }

  /* 3. Recherche ----------------------------------------------------------- */
  (function () {
    var triggers = $$('[data-ig-search]');
    var dlg = null, input = null, list = null, index = null, loading = null, active = -1, results = [];
    var SUGGESTIONS = ['/dossier-en-ligne', '/blog/simulateur-dfp-capitalisation', '/blog/refuser-offre-assurance-accident',
      '/blog/delai-prescription-accident-corporel', '/blog/que-faire-apres-accident-route', '/honoraires'];
    var TYPE_ICON = { Guide: 'book', Domaine: 'shield', Ville: 'pin', Lexique: 'list', Page: 'doc', Outil: 'doc' };

    function norm(s) {
      return String(s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[’']/g, ' ').replace(/œ/g, 'oe');
    }
    function load() {
      if (index) return Promise.resolve(index);
      if (loading) return loading;
      loading = fetch('/search-index.json').then(function (r) { return r.json(); }).then(function (data) {
        index = data.map(function (p) {
          return { p: p, t: norm(p.t), d: norm(p.d), h: norm((p.h || []).join(' · ')), k: norm(p.k) };
        });
        return index;
      }).catch(function () { loading = null; index = null; throw new Error('index'); });
      return loading;
    }
    function search(q) {
      var words = norm(q).split(/[^a-z0-9]+/).filter(function (w) { return w.length > 1; });
      if (!words.length) return null;
      var out = [];
      index.forEach(function (e) {
        var score = 0;
        for (var i = 0; i < words.length; i++) {
          var w = words[i], s = 0;
          if (e.t.indexOf(w) !== -1) s += 10 + (e.t.indexOf(w) === 0 ? 4 : 0);
          if (e.h.indexOf(w) !== -1) s += 4;
          if (e.d.indexOf(w) !== -1) s += 2;
          if (e.k.indexOf(w) !== -1) s += 1;
          if (!s) return;
          score += s;
        }
        if (e.p.k === 'Domaine' || e.p.k === 'Outil') score += 3;
        out.push({ e: e, s: score });
      });
      out.sort(function (a, b) { return b.s - a.s; });
      return out.slice(0, 8).map(function (x) { return x.e.p; });
    }
    function render(items, label) {
      results = items;
      active = items.length ? 0 : -1;
      if (!items.length) {
        list.innerHTML = '<li class="ig-s-empty">Aucun résultat. Posez votre question directement : ' +
          '<a href="tel:+33663465984">06 63 46 59 84</a> ou <a href="/contact">contact</a>.</li>';
        return;
      }
      list.innerHTML = (label ? '<li class="ig-s-label" role="presentation">' + label + '</li>' : '') + items.map(function (p, i) {
        return '<li role="option" id="ig-s-' + i + '"' + (i === 0 ? ' aria-selected="true"' : '') + '><a href="' + esc(p.u) + '" tabindex="-1">' +
          '<span class="ig-s-ico">' + svg(I[TYPE_ICON[p.k] || 'doc']) + '</span><span class="ig-s-txt"><strong>' + esc(p.t) + '</strong>' +
          '<small>' + esc(p.d || '') + '</small></span><span class="ig-s-type">' + esc(p.k) + '</span></a></li>';
      }).join('');
    }
    function suggestions() {
      var items = SUGGESTIONS.map(function (u) {
        for (var i = 0; i < index.length; i++) if (index[i].p.u === u) return index[i].p;
        return null;
      }).filter(Boolean);
      render(items, 'Les plus consultés');
    }
    function setActive(i) {
      var opts = $$('[role="option"]', list);
      if (!opts.length) return;
      active = (i + opts.length) % opts.length;
      opts.forEach(function (o, k) { if (k === active) o.setAttribute('aria-selected', 'true'); else o.removeAttribute('aria-selected'); });
      input.setAttribute('aria-activedescendant', opts[active].id);
      opts[active].scrollIntoView({ block: 'nearest' });
    }
    function build() {
      dlg = el('dialog', { 'class': 'ig-search', 'aria-label': 'Rechercher dans le site' },
        '<form method="dialog" class="ig-s-head">' + svg(I.search) +
        '<input type="search" name="q" autocomplete="off" spellcheck="false" enterkeyhint="search" placeholder="Rechercher : délai, expertise, provision…" ' +
        'aria-label="Rechercher dans le site" role="combobox" aria-expanded="true" aria-controls="ig-s-list" aria-autocomplete="list">' +
        '<button type="submit" class="ig-s-close" aria-label="Fermer la recherche">' + svg(I.x) + '</button></form>' +
        '<ul id="ig-s-list" class="ig-s-list" role="listbox" aria-label="Résultats"></ul>' +
        '<p class="ig-s-foot">Guides, domaines d\'intervention et lexique du dommage corporel.</p>');
      d.body.appendChild(dlg);
      input = $('input', dlg);
      list = $('.ig-s-list', dlg);
      var timer = null, tracked = false;
      input.addEventListener('input', function () {
        clearTimeout(timer);
        timer = setTimeout(function () {
          if (!index) return;
          var r = search(input.value);
          if (r === null) suggestions(); else {
            render(r);
            if (!tracked) { tracked = true; push({ event: 'recherche_site' }); }
          }
        }, 60);
      });
      input.addEventListener('keydown', function (e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); setActive(active + 1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); setActive(active - 1); }
        else if (e.key === 'Enter') {
          e.preventDefault();
          if (active >= 0 && results[active]) location.href = results[active].u;
        }
      });
      dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    }
    function open() {
      if (!dlg) build();
      if (dlg.open) return;
      if (typeof dlg.showModal !== 'function') { location.href = '/blog/'; return; }
      dlg.showModal();
      input.value = '';
      list.innerHTML = '<li class="ig-s-empty">Chargement…</li>';
      load().then(suggestions).catch(function () {
        list.innerHTML = '<li class="ig-s-empty">Recherche indisponible. <a href="/blog/">Voir tous les guides</a></li>';
      });
      input.focus();
    }
    triggers.forEach(function (b) { b.addEventListener('click', open); });
    d.addEventListener('keydown', function (e) {
      var t = e.target, typing = t && (t.isContentEditable || /^(INPUT|TEXTAREA|SELECT)$/.test(t.tagName));
      if ((e.key === 'k' && (e.metaKey || e.ctrlKey)) || (e.key === '/' && !typing)) {
        if (!triggers.length) return;
        e.preventDefault();
        open();
      }
    });
  })();

  /* 4. Guides : progression, sommaire, partage ----------------------------- */
  (function () {
    var path = location.pathname.replace(/\.html$/, '');
    if (!/^\/blog\/[^/]+/.test(path)) return;

    // Colonne de l'article : le parent direct qui porte le plus d'intertitres.
    var best = null, bestN = 0;
    $$('h2').forEach(function (h) {
      var p = h.parentNode;
      if (!p || p === best) return;
      var n = $$(':scope > h2', p).length;
      if (n > bestN) { best = p; bestN = n; }
    });
    if (!best || bestN < 3) return;
    best.classList.add('ig-article');

    var heads = $$(':scope > h2', best);
    var used = {};
    heads.forEach(function (h) {
      if (!h.id) {
        var s = h.textContent.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/^\s*\d+[.)]\s*/, '')
          .replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60) || 'section';
        while (used[s] || d.getElementById(s)) s += '-2';
        h.id = s;
      }
      used[h.id] = true;
    });

    // Sommaire repliable, ouvert d'emblée sur grand écran.
    if (heads.length >= 4 && !$('.ig-toc')) {
      var toc = el('details', { 'class': 'ig-toc' },
        '<summary>' + svg(I.list) + '<span>Sommaire</span><small>' + heads.length + ' parties</small>' + svg(I.chevron, 'ig-i ig-dd-chev') + '</summary><ol>' +
        heads.map(function (h) {
          return '<li><a href="#' + h.id + '">' + esc(h.textContent.replace(/^\s*\d+[.)]\s*/, '').trim()) + '</a></li>';
        }).join('') + '</ol>');
      if (window.matchMedia('(min-width: 1024px)').matches) toc.open = true;
      best.insertBefore(toc, heads[0]);
      toc.addEventListener('click', function (e) {
        if (e.target.closest('a') && !window.matchMedia('(min-width: 1024px)').matches) toc.open = false;
      });
    }

    // Barre de progression de lecture sous la navigation.
    var bar = el('div', { 'class': 'ig-progress', 'aria-hidden': 'true' }, '<span></span>');
    d.body.appendChild(bar);
    var fill = bar.firstChild, ticking = false;
    var update = function () {
      ticking = false;
      var r = best.getBoundingClientRect();
      var total = r.height - window.innerHeight * 0.6;
      var done = Math.min(1, Math.max(0, (-r.top + 96) / (total > 0 ? total : 1)));
      fill.style.transform = 'scaleX(' + done.toFixed(4) + ')';
    };
    window.addEventListener('scroll', function () { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();

    // Partage en fin d'article.
    var title = (d.querySelector('h1') || {}).textContent || d.title;
    title = title.replace(/\s+/g, ' ').trim();
    var url = (d.querySelector('link[rel="canonical"]') || {}).href || location.href;
    var share = el('div', { 'class': 'ig-share' },
      '<p>Ce guide peut aider un proche ?</p><div>' +
      '<a href="https://wa.me/?text=' + encodeURIComponent(title + ' — ' + url) + '" target="_blank" rel="noopener" data-share="whatsapp">WhatsApp</a>' +
      '<a href="https://x.com/intent/post?text=' + encodeURIComponent(title) + '&url=' + encodeURIComponent(url) + '&via=Guedj_" target="_blank" rel="noopener" data-share="x">X</a>' +
      '<a href="mailto:?subject=' + encodeURIComponent(title) + '&body=' + encodeURIComponent(url) + '" data-share="email">E-mail</a>' +
      '<button type="button" data-share="copie">' + svg(I.link) + '<span>Copier le lien</span></button></div>');
    // Placé avant les « Articles liés » s'ils existent, sinon en fin de colonne.
    var lies = null;
    heads.forEach(function (h) { if (/articles? li[ée]s|pour approfondir/i.test(h.textContent)) lies = h; });
    if (lies) best.insertBefore(share, lies); else best.appendChild(share);
    share.addEventListener('click', function (e) {
      var b = e.target.closest('[data-share]');
      if (!b) return;
      push({ event: 'partage_guide', canal: b.getAttribute('data-share') });
      if (b.tagName !== 'BUTTON') return;
      var done = function () {
        var s = $('span', b), old = s.textContent;
        s.textContent = 'Lien copié';
        setTimeout(function () { s.textContent = old; }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(url).then(done, function () {});
    });
  })();

  /* 5. Retour en haut ------------------------------------------------------ */
  (function () {
    if (d.documentElement.scrollHeight < window.innerHeight * 3) return;
    var b = el('button', { type: 'button', 'class': 'ig-top', 'aria-label': 'Revenir en haut de la page', hidden: '' }, svg(I.up));
    d.body.appendChild(b);
    b.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: reduced ? 'auto' : 'smooth' }); });
    var shown = false;
    window.addEventListener('scroll', function () {
      var s = window.scrollY > window.innerHeight * 1.5;
      if (s !== shown) { shown = s; b.hidden = !s; }
    }, { passive: true });
  })();

  /* Module Calendly intégré (page contact) : chargé à l'approche, pas au premier rendu. */
  (function () {
    var w = $('.calendly-inline-widget');
    if (!w) return;
    var load = function () {
      if (window.Calendly || $('script[src*="assets.calendly.com"]')) return;
      var s = el('script', { src: 'https://assets.calendly.com/assets/external/widget.js' });
      s.async = true;
      s.onload = function () {
        setTimeout(function () {
          if (!$('iframe', w) && window.Calendly && w.getAttribute('data-url')) {
            window.Calendly.initInlineWidget({ url: w.getAttribute('data-url'), parentElement: w });
          }
        }, 300);
      };
      d.head.appendChild(s);
    };
    if (!('IntersectionObserver' in window)) { load(); return; }
    var io = new IntersectionObserver(function (en) {
      if (en.some(function (e) { return e.isIntersecting; })) { io.disconnect(); load(); }
    }, { rootMargin: '800px 0px' });
    io.observe(w);
  })();

  /* 6. Calculateur d'échéances --------------------------------------------- */
  (function () {
    var box = $('[data-ig-echeances]');
    if (!box) return;
    var acc = $('[name="accident"]', box), cons = $('[name="consolidation"]', box), out = $('[data-ech-out]', box);
    if (!acc || !out) return;
    var today = new Date(); today.setHours(0, 0, 0, 0);
    var iso = function (x) { return x.getFullYear() + '-' + ('0' + (x.getMonth() + 1)).slice(-2) + '-' + ('0' + x.getDate()).slice(-2); };
    acc.max = iso(today);
    if (cons) cons.max = iso(today);
    var fmt = new Intl.DateTimeFormat('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' });
    function parse(v) {
      var m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(v || '');
      if (!m) return null;
      var x = new Date(+m[1], +m[2] - 1, +m[3]);
      return isNaN(x) ? null : x;
    }
    // Ajout de mois « de quantième à quantième » : le 31 août + 6 mois donne le dernier jour de février.
    function addMonths(x, n) {
      var r = new Date(x.getFullYear(), x.getMonth() + n, 1);
      var last = new Date(r.getFullYear(), r.getMonth() + 1, 0).getDate();
      r.setDate(Math.min(x.getDate(), last));
      return r;
    }
    function row(titre, date, texte, etat) {
      var badge = etat === 'passe' ? '<span class="ig-ech-b ig-ech-late">Date dépassée</span>'
        : etat === 'avenir' ? '<span class="ig-ech-b">À venir</span>' : '';
      return '<li><div><strong>' + titre + '</strong>' + badge + '</div>' +
        (date ? '<p class="ig-ech-date">' + date + '</p>' : '') + '<p>' + texte + '</p></li>';
    }
    function compute() {
      var a = parse(acc.value), c = cons ? parse(cons.value) : null;
      if (!a || a > today) { out.hidden = true; return; }
      if (c && c < a) c = null;
      var offre = addMonths(a, 8), h = '';
      h += row('Offre d\'indemnité de l\'assureur', 'Au plus tard le ' + fmt.format(offre),
        offre < today
          ? 'Ce délai de huit mois est écoulé. Si aucune offre ne vous a été faite, l\'indemnité peut produire des intérêts au double du taux légal : c\'est un point à faire vérifier.'
          : 'L\'assureur doit vous présenter une offre dans les huit mois de l\'accident. Elle est provisionnelle tant que votre état n\'est pas consolidé.',
        offre < today ? 'passe' : 'avenir');
      if (c) {
        var def = addMonths(c, 5), presc = addMonths(c, 120);
        h += row('Offre définitive', 'Environ le ' + fmt.format(def),
          'Elle doit intervenir dans les cinq mois suivant la date à laquelle l\'assureur a été informé de votre consolidation. La date affichée suppose qu\'il l\'a su le jour même.',
          def < today ? 'passe' : 'avenir');
        h += row('Prescription de l\'action', fmt.format(presc),
          presc < today
            ? 'Dix ans se sont écoulés depuis la consolidation. Des causes de report existent (minorité, aggravation) : ne renoncez pas sans avis.'
            : 'Vous disposez de dix ans à compter de la consolidation pour agir en justice. Une aggravation fait courir un nouveau délai.',
          presc < today ? 'passe' : 'avenir');
      } else {
        h += row('Offre définitive', '', 'Dans les cinq mois suivant la date à laquelle l\'assureur est informé de votre consolidation. Indiquez-la ci-dessus si vous la connaissez.', '');
        h += row('Prescription de l\'action', '', 'Dix ans à compter de la consolidation. Tant que votre état n\'est pas consolidé, ce délai n\'a pas commencé à courir.', '');
      }
      $('ol', out).innerHTML = h;
      if (out.hidden) push({ event: 'calcul_echeances' });
      out.hidden = false;
    }
    acc.addEventListener('change', compute);
    if (cons) cons.addEventListener('change', compute);
    var form = $('form', box);
    if (form) form.addEventListener('submit', function (e) { e.preventDefault(); compute(); });
  })();
})();
