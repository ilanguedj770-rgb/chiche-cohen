/* Suivi des prises de contact — dataLayer uniquement.
   Aucun traceur n'est chargé ici : GTM (GTM-WP82S37T) est déjà dans les pages
   et sera soumis au consentement par ailleurs.

   Événements à marquer comme conversions dans GTM / GA4 :
   - phone_click        clic sur un lien tel:
   - whatsapp_click     clic sur wa.me ou api.whatsapp.com
   - calendly_click     clic vers Calendly, ou bouton Calendly.initPopupWidget
   - email_click        clic sur un lien mailto:
   - form_submit        envoi abouti. form_name = article_lead (articles),
                        contact_form (page contact, déjà en place),
                        ou event lead_magnet_submit (guide de l'accueil, déjà en place).

   Paramètres : page_path, page_title, link_location, link_url.
   link_location : header, mobile_menu, mobile_bar, desktop_fab, footer,
   sidebar, article_mid, article_end, page_cta, exit_popup, content.
   Ne jamais y mettre le nom, le téléphone ou le message.
*/
(function (window, document) {
  if (window.__igConversions) return;
  window.__igConversions = true;

  function push(payload) {
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push(payload);
  }

  function linkLocation(el) {
    var node = el;
    while (node && node !== document.body) {
      if (node.getAttribute && node.getAttribute('data-cta-location')) {
        return node.getAttribute('data-cta-location');
      }
      node = node.parentElement;
    }
    if (el.closest('#exit-popup')) return 'exit_popup';
    if (el.closest('#mobile-menu')) return 'mobile_menu';
    var fixed = el.closest('.fixed');
    if (fixed && /\bbottom-/.test(fixed.className || '')) {
      var cls = fixed.className || '';
      if (/\bmd:hidden\b/.test(cls)) return 'mobile_bar';
      if (/\bhidden\b/.test(cls)) return 'desktop_fab';
      return 'fixed_bottom';
    }
    if (el.closest('footer')) return 'footer';
    if (el.closest('nav, header')) return 'header';
    if (el.closest('[class*="lg:col-span-1"]')) return 'sidebar';
    var section = el.closest('section');
    if (section && /\bbg-ink\b|\bbg-gray-900\b|\bbg-black\b/.test(section.className || '')) {
      return 'page_cta';
    }
    return 'content';
  }

  function classify(el) {
    var href = (el.getAttribute('href') || '').trim();
    var onclick = el.getAttribute('onclick') || '';
    if (/^tel:/i.test(href)) return { event: 'phone_click', link_url: href };
    if (/wa\.me|api\.whatsapp\.com|whatsapp\.com\/send/i.test(href)) {
      return { event: 'whatsapp_click', link_url: href };
    }
    if (/^mailto:/i.test(href)) return { event: 'email_click', link_url: href };
    if (/calendly\.com/i.test(href) || /calendly\.com/i.test(onclick) || /Calendly\.init/i.test(onclick)) {
      return { event: 'calendly_click', link_url: href || 'https://calendly.com/guedj-chiche-cohen' };
    }
    return null;
  }

  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('a, button') : null;
    if (!el) return;
    var kind = classify(el);
    if (!kind) return;
    push({
      event: kind.event,
      page_path: window.location.pathname,
      page_title: document.title,
      link_location: linkLocation(el),
      link_url: kind.link_url
    });
  }, true);

  var SPINNER = '<svg class="animate-spin w-4 h-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" aria-hidden="true"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>';

  document.addEventListener('submit', function (e) {
    var form = e.target;
    if (!form || !form.classList || !form.classList.contains('js-article-lead')) return;
    e.preventDefault();
    var btn = form.querySelector('.js-article-lead-submit');
    var success = form.querySelector('.js-article-lead-success');
    if (!btn) return;
    var idle = btn.getAttribute('data-idle-label') || btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = SPINNER + '<span>Envoi en cours…</span>';
    fetch(form.action, {
      method: 'POST',
      body: new FormData(form),
      headers: { 'Accept': 'application/json' }
    }).then(function (response) {
      if (!response.ok) throw new Error('form');
      form.reset();
      if (success) success.classList.remove('hidden');
      btn.classList.add('hidden');
      push({
        event: 'form_submit',
        form_name: 'article_lead',
        page_path: window.location.pathname,
        page_title: document.title,
        link_location: 'article_end'
      });
    }).catch(function () {
      btn.disabled = false;
      btn.innerHTML = idle;
      window.alert('L\'envoi n\'a pas abouti. Vous pouvez appeler le 06 63 46 59 84.');
    });
  });
})(window, document);
