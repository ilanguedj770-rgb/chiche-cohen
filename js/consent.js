/* Bandeau de consentement — ig-avocat.com
   Consent Mode v2, défaut refusé. Google Tag Manager (GTM-WP82S37T)
   n'est injecté qu'après un accord pour la mesure d'audience.
   Aucune dépendance tierce. Le choix est mémorisé 6 mois (localStorage). */
(function () {
  var GTM_ID = "GTM-WP82S37T";
  var STORAGE_KEY = "ig_consent_v1";
  var SIX_MONTHS = 183 * 24 * 60 * 60 * 1000;
  var gtmLoaded = false;

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = window.gtag || gtag;

  gtag("consent", "default", {
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    analytics_storage: "denied",
    functionality_storage: "denied",
    personalization_storage: "denied",
    security_storage: "granted",
    wait_for_update: 500
  });
  gtag("set", "ads_data_redaction", true);
  gtag("set", "url_passthrough", false);

  function read() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      if (!raw) return null;
      var choice = JSON.parse(raw);
      if (!choice || typeof choice.ts !== "string") return null;
      var age = Date.now() - Date.parse(choice.ts);
      if (!(age >= 0 && age < SIX_MONTHS)) return null;
      return choice;
    } catch (e) {
      return null;
    }
  }

  function loadGTM() {
    if (gtmLoaded) return;
    gtmLoaded = true;
    window.dataLayer.push({ "gtm.start": new Date().getTime(), event: "gtm.js" });
    var j = document.createElement("script");
    j.async = true;
    j.src = "https://www.googletagmanager.com/gtm.js?id=" + GTM_ID;
    document.head.appendChild(j);
  }

  function apply(choice) {
    var analytics = choice.analytics === true;
    gtag("consent", "update", {
      analytics_storage: analytics ? "granted" : "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      functionality_storage: "denied",
      personalization_storage: "denied",
      security_storage: "granted"
    });
    if (analytics) loadGTM();
    try {
      document.dispatchEvent(new CustomEvent("ig-consent-change", { detail: choice }));
    } catch (e) { /* navigateurs anciens */ }
  }

  function save(analytics) {
    var choice = { v: 1, analytics: !!analytics, ts: new Date().toISOString() };
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(choice)); } catch (e) { /* mode privé */ }
    apply(choice);
    return choice;
  }

  var current = read();
  if (current) apply(current);

  function enableCalendly() {
    if (window.__igCalendlyLoading) return window.__igCalendlyLoading;
    window.__igCalendlyLoading = new Promise(function (resolve) {
      document.querySelectorAll('link[data-requires-consent="calendly"]').forEach(function (link) {
        var href = link.getAttribute("data-href");
        if (href && !link.getAttribute("href")) link.setAttribute("href", href);
      });
      var pending = document.querySelectorAll('script[data-requires-consent="calendly"]');
      if (!pending.length) { resolve(); return; }
      var left = pending.length;
      Array.prototype.forEach.call(pending, function (old) {
        var s = document.createElement("script");
        s.src = old.getAttribute("data-src");
        s.async = true;
        function done() { if (--left === 0) resolve(); }
        s.onload = done;
        s.onerror = done;
        old.parentNode.insertBefore(s, old);
        old.parentNode.removeChild(old);
      });
    });
    return window.__igCalendlyLoading;
  }

  document.addEventListener("click", function (e) {
    var manage = e.target.closest && e.target.closest("[data-consent-manage]");
    if (manage) {
      e.preventDefault();
      openBanner(true);
      return;
    }
    var btn = e.target.closest && e.target.closest("button, a");
    if (!btn) return;
    var oc = btn.getAttribute("onclick") || "";
    if (oc.indexOf("Calendly") === -1) return;
    if (window.Calendly && window.Calendly.initPopupWidget) return;
    e.preventDefault();
    e.stopPropagation();
    var match = oc.match(/https:\/\/calendly\.com\/[^'")\s]+/);
    enableCalendly().then(function () {
      if (match && window.Calendly && window.Calendly.initPopupWidget) {
        window.Calendly.initPopupWidget({ url: match[0] });
      }
      if (oc.indexOf("exit-popup") !== -1) {
        var pop = document.getElementById("exit-popup");
        if (pop) pop.classList.add("hidden");
      }
      if (oc.indexOf("exit_popup_cta") !== -1 && window.dataLayer) {
        window.dataLayer.push({ event: "exit_popup_cta", action: "calendly" });
      }
    });
  }, true);

  function onReady(fn) {
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", fn);
    else fn();
  }

  function injectStyles() {
    if (document.getElementById("ig-consent-style")) return;
    var css = [
      "#ig-consent{position:fixed;z-index:1000;left:0;right:0;bottom:0;padding:0.75rem;font-family:Inter,system-ui,sans-serif;color:#1B2430}",
      "#ig-consent .ig-card{max-width:46rem;margin:0 auto;background:#FDFBF8;border:1px solid rgba(27,36,48,.14);border-radius:1.25rem;box-shadow:0 18px 50px rgba(27,36,48,.16);padding:1.15rem 1.2rem 1.05rem}",
      "#ig-consent h2{font-family:Fraunces,Georgia,serif;font-size:1.15rem;font-weight:700;letter-spacing:-.015em;margin:0 0 .4rem}",
      "#ig-consent p{margin:0;font-size:.875rem;line-height:1.55;color:#3d4654}",
      "#ig-consent a{color:#1E40AF;text-underline-offset:2px}",
      "#ig-consent .ig-actions{display:flex;gap:.6rem;margin-top:.9rem}",
      "#ig-consent .ig-actions button,#ig-consent .ig-save{flex:1 1 0;min-height:2.75rem;border-radius:999px;font-weight:700;font-size:.875rem;cursor:pointer;padding:.55rem .9rem}",
      "#ig-consent .ig-refuse{background:#FDFBF8;color:#1B2430;border:2px solid #1B2430}",
      "#ig-consent .ig-accept{background:#1E40AF;color:#fff;border:2px solid #1E40AF}",
      "#ig-consent .ig-refuse:hover{background:#F4EFE5}",
      "#ig-consent .ig-accept:hover{background:#1d4ed8}",
      "#ig-consent .ig-more{display:inline-block;margin-top:.75rem;background:none;border:0;padding:0;color:#1E40AF;font-weight:700;font-size:.875rem;cursor:pointer;text-decoration:underline;text-underline-offset:2px}",
      "#ig-consent .ig-panel{display:none;margin-top:.85rem;padding-top:.85rem;border-top:1px solid rgba(27,36,48,.12)}",
      "#ig-consent .ig-panel.is-open{display:block}",
      "#ig-consent .ig-choice{display:flex;gap:.7rem;align-items:flex-start;font-size:.875rem;line-height:1.45}",
      "#ig-consent .ig-choice input{margin-top:.2rem;width:1.05rem;height:1.05rem;accent-color:#1E40AF}",
      "#ig-consent .ig-save{display:block;width:100%;margin-top:.75rem;background:#1B2430;color:#fff;border:2px solid #1B2430}",
      "#ig-consent .ig-note{margin-top:.55rem;font-size:.75rem;color:#6b645b}",
      ".ig-calendly-hold,.ig-map-hold{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:.75rem;text-align:center;background:#F4EFE5;color:#1B2430;border:1px solid rgba(27,36,48,.12);border-radius:1rem;padding:1.25rem;min-height:12rem}",
      ".ig-calendly-hold p,.ig-map-hold p{margin:0;font-size:.875rem;line-height:1.5;max-width:28rem}",
      ".ig-calendly-hold button,.ig-map-hold button{background:#1E40AF;color:#fff;border:2px solid #1E40AF;border-radius:999px;font-weight:700;font-size:.875rem;padding:.65rem 1.1rem;cursor:pointer}",
      ".ig-map-hold.is-fill{position:absolute;inset:0;border-radius:0;min-height:0;height:100%}",
      "@media (max-width:640px){#ig-consent .ig-actions{flex-direction:column}}",
      "@media (prefers-reduced-motion:reduce){#ig-consent *{transition:none!important}}"
    ].join("");
    var style = document.createElement("style");
    style.id = "ig-consent-style";
    style.textContent = css;
    document.head.appendChild(style);
  }

  var root = null;

  function closeBanner() {
    if (root && root.parentNode) root.parentNode.removeChild(root);
    root = null;
  }

  function openBanner(fromFooter) {
    injectStyles();
    closeBanner();
    var stored = read();
    root = document.createElement("div");
    root.id = "ig-consent";
    root.setAttribute("role", "dialog");
    root.setAttribute("aria-labelledby", "ig-consent-title");
    root.setAttribute("aria-describedby", "ig-consent-text");
    root.innerHTML =
      '<div class="ig-card">' +
        '<h2 id="ig-consent-title">Cookies et mesure d’audience</h2>' +
        '<p id="ig-consent-text">Ce site n’active Google Analytics (via Google Tag Manager) que si vous l’acceptez. Refuser n’empêche pas de consulter les pages ni de nous écrire. ' +
        '<a href="/politique-confidentialite">Politique de confidentialité</a> · <a href="/cookies">Cookies</a></p>' +
        '<div class="ig-actions">' +
          '<button type="button" class="ig-refuse" data-act="refuse">Refuser</button>' +
          '<button type="button" class="ig-accept" data-act="accept">Accepter</button>' +
        '</div>' +
        '<button type="button" class="ig-more" aria-expanded="false" data-act="customize">Personnaliser</button>' +
        '<div class="ig-panel" id="ig-consent-panel">' +
          '<label class="ig-choice"><input type="checkbox" data-analytics> <span><strong>Mesure d’audience</strong> — Google Analytics, déposé par le conteneur GTM-WP82S37T. Aucun autre traceur publicitaire n’est autorisé par ce choix.</span></label>' +
          '<button type="button" class="ig-save" data-act="save">Enregistrer</button>' +
          '<p class="ig-note">Votre choix est mémorisé 6 mois sur cet appareil. Vous pouvez le modifier à tout moment depuis « Gérer les cookies » en pied de page.</p>' +
        '</div>' +
      '</div>';
    var box = root.querySelector("[data-analytics]");
    if (stored && stored.analytics) box.checked = true;
    root.addEventListener("click", function (e) {
      var act = e.target.getAttribute && e.target.getAttribute("data-act");
      if (act === "accept") { save(true); closeBanner(); }
      else if (act === "refuse") { save(false); closeBanner(); }
      else if (act === "save") { save(box.checked); closeBanner(); }
      else if (act === "customize") {
        var panel = document.getElementById("ig-consent-panel");
        var open = !panel.classList.contains("is-open");
        panel.classList.toggle("is-open", open);
        e.target.setAttribute("aria-expanded", open ? "true" : "false");
      }
    });
    document.body.appendChild(root);
    if (fromFooter) {
      var first = root.querySelector("button");
      if (first) first.focus();
    }
  }

  function holdCalendly() {
    Array.prototype.forEach.call(document.querySelectorAll(".calendly-inline-widget"), function (el) {
      if (el.getAttribute("data-consent-held")) return;
      el.setAttribute("data-consent-held", "1");
      el.style.display = "none";
      var hold = document.createElement("div");
      hold.className = "ig-calendly-hold";
      hold.innerHTML = '<p>Le calendrier est affiché par Calendly, un service situé aux États-Unis. Il ne se charge que lorsque vous le demandez.</p>' +
        '<button type="button">Afficher le calendrier</button>' +
        '<p><a href="/politique-confidentialite">Politique de confidentialité</a></p>';
      hold.querySelector("button").addEventListener("click", function () {
        hold.parentNode.removeChild(hold);
        el.style.display = "";
        enableCalendly();
      });
      el.parentNode.insertBefore(hold, el);
    });
  }

  function holdMaps() {
    Array.prototype.forEach.call(document.querySelectorAll("iframe[data-map-src]"), function (frame) {
      if (frame.getAttribute("data-consent-held")) return;
      frame.setAttribute("data-consent-held", "1");
      var src = frame.getAttribute("data-map-src");
      var hold = document.createElement("div");
      hold.className = "ig-map-hold";
      var abs = (frame.className || "").indexOf("absolute") !== -1;
      if (abs) hold.className += " is-fill";
      else {
        hold.style.width = "100%";
        hold.style.minHeight = "20rem";
        hold.style.border = "0";
        hold.style.borderRadius = "0";
      }
      frame.style.display = "none";
      hold.innerHTML = '<p>Le plan Google Maps n’est chargé qu’à votre demande.</p><button type="button">Afficher le plan</button>';
      hold.querySelector("button").addEventListener("click", function () {
        frame.style.display = "";
        frame.setAttribute("src", src);
        hold.parentNode.removeChild(hold);
      });
      frame.parentNode.insertBefore(hold, frame);
    });
  }

  onReady(function () {
    injectStyles();
    holdCalendly();
    holdMaps();
    if (!read()) openBanner(false);
  });

  window.igConsent = {
    granted: function () {
      var c = read();
      return { analytics: !!(c && c.analytics) };
    },
    open: function () { openBanner(true); }
  };
})();
