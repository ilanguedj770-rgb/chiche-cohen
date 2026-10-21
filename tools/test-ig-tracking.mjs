/**
 * Vérifie le suivi GA4 et la barre d'appel sans navigateur.
 * Usage : node tools/test-ig-tracking.mjs
 */
import { createRequire } from 'node:module';
import { existsSync, readFileSync } from 'node:fs';

const jsdomRoot = existsSync('/tmp/igtest/node_modules/jsdom/package.json')
  ? '/tmp/igtest/package.json'
  : import.meta.url;
const { JSDOM } = createRequire(jsdomRoot)('jsdom');

const source = readFileSync(new URL('../js/ig-tracking.js', import.meta.url), 'utf8');
let failed = 0;

function assert(cond, msg) {
  if (!cond) {
    failed += 1;
    console.error('ÉCHEC : ' + msg);
  }
}

function eventsOf(dataLayer) {
  const out = [];
  for (const item of dataLayer) {
    if (item && typeof item === 'object' && typeof item.event === 'string' && !item[0]) {
      out.push(item);
      continue;
    }
    if (item && item[0] === 'event') {
      out.push(Object.assign({ event: item[1] }, item[2] || {}));
    }
  }
  return out;
}

function boot(html, path) {
  const dom = new JSDOM('<!DOCTYPE html><html><head></head><body>' + html + '</body></html>', {
    url: 'https://ig-avocat.com' + path,
    pretendToBeVisual: true,
    runScripts: 'dangerously'
  });
  const { window } = dom;
  window.matchMedia = function (q) {
    return {
      matches: String(q).indexOf('max-width') !== -1,
      media: q,
      addEventListener: function () {},
      removeEventListener: function () {},
      addListener: function () {},
      removeListener: function () {}
    };
  };
  window.dataLayer = [];
  window.gtag = function () { window.dataLayer.push(arguments); };
  const tag = window.document.createElement('script');
  tag.textContent = source;
  window.document.body.appendChild(tag);
  window.document.dispatchEvent(new window.Event('DOMContentLoaded'));
  return window;
}

function click(window, el) {
  el.dispatchEvent(new window.MouseEvent('click', { bubbles: true, cancelable: true }));
}

// --- clics ---
{
  const w = boot(
    '<header id="navbar"><a id="tel" href="tel:+33663465984">06 63 46 59 84</a></header>' +
    '<main><a id="wa" href="https://wa.me/33663465984">WhatsApp</a></main>' +
    '<footer><a id="mail" href="mailto:contact@ig-avocat.com">Email</a></footer>' +
    '<div data-cta="bouton_flottant" class="fixed"><a id="float" href="tel:+33663465984">Appeler</a></div>' +
    '<div data-cta="bouton_fixe_mobile" class="fixed md:hidden"></div>',
    '/contact?utm_source=test'
  );
  const before = w.document.cookie;
  click(w, w.document.getElementById('tel'));
  click(w, w.document.getElementById('tel'));
  click(w, w.document.getElementById('wa'));
  click(w, w.document.getElementById('mail'));
  click(w, w.document.getElementById('float'));
  const ev = eventsOf(w.dataLayer);
  const phones = ev.filter((e) => e.event === 'click_phone');
  assert(phones.length === 2, 'deux click_phone (header + flottant), pas le double-tap');
  assert(phones[0].link_location === 'header', 'header → link_location header');
  assert(phones[0].page_path === '/contact?utm_source=test', 'page_path conserve la query');
  assert(phones[1].link_location === 'bouton flottant', 'barre fixe → bouton flottant');
  const wa = ev.filter((e) => e.event === 'click_whatsapp');
  assert(wa.length === 1 && wa[0].link_location === 'corps', 'wa.me dans le corps');
  const mail = ev.filter((e) => e.event === 'click_email');
  assert(mail.length === 1 && mail[0].link_location === 'footer', 'mailto dans le footer');
  assert(ev.some((e) => e.event === 'clic_telephone'), 'le nom historique clic_telephone part aussi');
  assert(w.document.cookie === before, 'aucun cookie posé par le script');
  assert(!w.document.getElementById('ig-callbar'), 'pas de seconde barre si bouton_fixe_mobile existe');
}

// --- barre absente : on l'ajoute, avec WhatsApp ---
{
  const w = boot(
    '<nav id="navbar" class="fixed"><a href="tel:+33663465984">06</a></nav>' +
    '<a id="fab" class="fixed hidden md:flex" href="https://wa.me/33663465984">WA</a>' +
    '<p>contenu</p>',
    '/guide-5-erreurs'
  );
  const bar = w.document.getElementById('ig-callbar');
  assert(!!bar, 'barre ajoutée quand seul le FAB desktop existe');
  assert(bar.querySelector('a[href="tel:+33663465984"]'), 'lien tel:+33663465984');
  assert(bar.querySelector('a[href="https://wa.me/33663465984"]'), 'WhatsApp ajouté : pas de flottant mobile');
  assert(/Appeler le cabinet/.test(bar.textContent), 'libellé Appeler le cabinet');
  assert(bar.querySelector('.ig-call').getAttribute('aria-label').indexOf('Appeler le cabinet') === 0, 'aria-label téléphone');
  assert(w.document.body.classList.contains('ig-callbar-on'), 'classe de padding sur le body');
  assert(w.document.head.textContent.indexOf('max-width:767px') !== -1 || w.document.head.innerHTML.indexOf('max-width:767px') !== -1, 'affichage limité au mobile');
}

// --- WhatsApp mobile déjà flottant : pas de second bouton ---
{
  const w = boot(
    '<div class="fixed" style="position:fixed"><a href="https://wa.me/33663465984">WA</a></div>',
    '/accident-moto-marseille'
  );
  const bar = w.document.getElementById('ig-callbar');
  assert(!!bar, 'le bouton d\'appel est ajouté');
  assert(!bar.querySelector('a[href*="wa.me"]'), 'pas de second WhatsApp flottant');
  assert(bar.querySelector('a[href^="tel:"]'), 'le téléphone est bien là');
}

// --- formulaire de contact ---
{
  const w = boot(
    '<main><form id="contact-form"><div id="form-success" class="hidden">OK</div></form></main>',
    '/contact'
  );
  const success = w.document.getElementById('form-success');
  success.classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  const leads = eventsOf(w.dataLayer).filter((e) => e.event === 'generate_lead');
  assert(leads.length === 1, 'generate_lead une fois');
  assert(leads[0] && leads[0].form_id === 'contact-form', 'form_id contact-form');
  assert(leads[0] && leads[0].link_location === 'corps', 'formulaire dans le corps');
  success.className = 'hidden';
  success.classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  assert(eventsOf(w.dataLayer).filter((e) => e.event === 'generate_lead').length === 1, 'pas de second generate_lead');
}

if (failed) {
  console.error(failed + ' échec(s)');
  process.exit(1);
}
console.log('OK — événements GA4, consentement (pas de cookie), barre mobile sans doublon');
