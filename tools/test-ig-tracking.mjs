/**
 * Vérifie le suivi GA4 et la barre d'appel sans navigateur.
 * Usage : node tools/test-ig-tracking.mjs
 */
import { createRequire } from 'node:module';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
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
  window.__gc = [];
  window.goatcounter = {
    count: function (vars) { window.__gc.push(vars); }
  };
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
  const gc = w.__gc;
  const gcPhones = gc.filter((e) => e.path === 'clic-telephone');
  assert(gcPhones.length === 2, 'goatcounter : deux clic-telephone, pas le double-tap');
  assert(gcPhones[0].title === 'header' && gcPhones[0].event === true, 'goatcounter title = emplacement header');
  assert(gcPhones[1].title === 'bouton_flottant', 'goatcounter title du flottant');
  const gcWa = gc.filter((e) => e.path === 'clic-whatsapp');
  assert(gcWa.length === 1 && gcWa[0].title === 'contenu', 'goatcounter clic-whatsapp : title = emplacement contenu');
  assert(!gc.some((e) => e.path === 'clic-email' || /mailto|@/.test(JSON.stringify(e))), 'pas d\'événement e-mail vers goatcounter');
  assert(JSON.stringify(gc).indexOf('33663465984') === -1, 'aucun numéro transmis à goatcounter');
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
  const gcForms = w.__gc.filter((e) => e.path === 'formulaire-contact');
  assert(gcForms.length === 1 && gcForms[0].title === 'contenu' && gcForms[0].event === true, 'formulaire-contact au succès, title = emplacement');
  success.className = 'hidden';
  success.classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  assert(eventsOf(w.dataLayer).filter((e) => e.event === 'generate_lead').length === 1, 'pas de second generate_lead');
  assert(w.__gc.filter((e) => e.path === 'formulaire-contact').length === 1, 'pas de second formulaire-contact');
}

// --- le formulaire du guide 5 erreurs n'est pas formulaire-contact ---
{
  const w = boot(
    '<form id="contact-form"><div id="form-success" class="hidden">OK</div></form>',
    '/guide-5-erreurs'
  );
  w.document.getElementById('form-success').classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  assert(!w.__gc.some((e) => e.path === 'formulaire-contact'), 'formulaire-contact réservé à contact.html');
}

// --- guide gratuit ---
{
  const w = boot(
    '<form id="guide-form"><div id="guide-success" class="hidden">OK</div></form>',
    '/'
  );
  const success = w.document.getElementById('guide-success');
  success.classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  const guides = w.__gc.filter((e) => e.path === 'guide-gratuit');
  assert(guides.length === 1 && guides[0].event === true && guides[0].title === 'contenu', 'guide-gratuit une fois');
  success.classList.remove('hidden');
  await new Promise((r) => setTimeout(r, 20));
  assert(w.__gc.filter((e) => e.path === 'guide-gratuit').length === 1, 'pas de second guide-gratuit');
}

// --- Calendly : ouverture puis confirmation, sans identifiant ---
{
  const w = boot(
    '<a id="rdv" href="https://calendly.com/guedj-chiche-cohen" data-calendly data-cta="hero">RDV</a>',
    '/avocat-nice'
  );
  click(w, w.document.getElementById('rdv'));
  click(w, w.document.getElementById('rdv'));
  const open = w.__gc.filter((e) => e.path === 'clic-calendly');
  assert(open.length === 1 && open[0].title === 'hero' && open[0].event === true, 'clic-calendly dédoublonné, title hero');
  const payload = {
    event: 'calendly.event_scheduled',
    payload: {
      invitee: { uri: 'https://api.calendly.com/invitees/SECRET-INVITEE' },
      event: { uri: 'https://api.calendly.com/scheduled_events/SECRET-EVENT' }
    }
  };
  w.dispatchEvent(new w.MessageEvent('message', { origin: 'https://evil.example', data: payload }));
  w.dispatchEvent(new w.MessageEvent('message', { origin: 'https://calendly.com', data: payload }));
  w.dispatchEvent(new w.MessageEvent('message', { origin: 'https://calendly.com', data: payload }));
  const rdv = w.__gc.filter((e) => e.path === 'rdv-calendly');
  assert(rdv.length === 1 && rdv[0].title === 'hero' && rdv[0].event === true, 'rdv-calendly une fois');
  const blob = JSON.stringify(w.__gc);
  assert(blob.indexOf('SECRET') === -1 && blob.indexOf('invitees') === -1, 'aucun identifiant Calendly transmis');
  assert(eventsOf(w.dataLayer).filter((e) => e.event === 'calendly_rdv').length === 1, 'calendly_rdv dataLayer inchangé');
}

// --- script absent ou en erreur : pas de plantage, pas de file d'attente ---
{
  const w = boot(
    '<header id="navbar"><a id="tel" href="tel:+33663465984">Appeler</a>' +
    '<a id="wa" href="https://wa.me/33663465984">WA</a></header>',
    '/'
  );
  w.goatcounter = undefined;
  click(w, w.document.getElementById('tel'));
  w.__gc = [];
  w.goatcounter = { count: function (vars) { w.__gc.push(vars); } };
  assert(w.__gc.length === 0, 'pas de file d\'attente si goatcounter charge après le clic');
  assert(eventsOf(w.dataLayer).some((e) => e.event === 'clic_telephone'), 'dataLayer part même sans goatcounter');
  w.goatcounter = { count: function () { throw new Error('gc down'); } };
  let threw = false;
  try { click(w, w.document.getElementById('wa')); } catch (err) { threw = true; }
  assert(!threw, 'une erreur goatcounter ne casse pas le clic');
  assert(eventsOf(w.dataLayer).some((e) => e.event === 'clic_whatsapp'), 'dataLayer part même si goatcounter lève');
}

// --- une inclusion du script local par page publiée ---
{
  const root = new URL('..', import.meta.url);
  const pages = readdirSync(root).filter((n) => n.endsWith('.html'))
    .concat(readdirSync(new URL('../blog/', import.meta.url)).map((n) => 'blog/' + n).filter((n) => n.endsWith('.html')));
  const tag = '<script data-goatcounter="https://ig-avocat.goatcounter.com/count" async src="/js/goatcounter-count.js"></script>';
  assert(pages.length >= 54, 'au moins 54 pages HTML');
  for (const page of pages) {
    const html = readFileSync(new URL('../' + page, import.meta.url), 'utf8');
    const n = html.split(tag).length - 1;
    assert(n === 1, page + ' : script GoatCounter exactement une fois (' + n + ')');
    assert(html.indexOf('<!-- GOATCOUNTER:START -->') !== -1 && html.indexOf('<!-- GOATCOUNTER:END -->') !== -1, page + ' : marqueurs');
    const start = html.indexOf('<!-- GOATCOUNTER:START -->');
    const end = html.indexOf('<!-- GOATCOUNTER:END -->');
    assert(start < end && html.indexOf('<!-- GOATCOUNTER:START -->', start + 1) === -1, page + ' : un seul bloc');
    assert(html.indexOf('gc.zgo.at') === -1, page + ' : pas de script tiers GoatCounter');
  }
  const vendor = readFileSync(new URL('../js/goatcounter-count.js', import.meta.url), 'utf8');
  assert(vendor.indexOf('ISC license') !== -1, 'en-tête de licence ISC conservé');
  assert(vendor.indexOf('window.goatcounter.count') !== -1, 'count.js officiel vendorisé');
}

if (failed) {
  console.error(failed + ' échec(s)');
  process.exit(1);
}
console.log('OK — événements GA4, GoatCounter sans donnée personnelle, barre mobile sans doublon');
