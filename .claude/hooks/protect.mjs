// Hook PreToolUse (Edit / Write / MultiEdit) — ig-avocat.com
// Code de sortie 2 = écriture bloquée, le message part vers Claude.
// Les générateurs (tools/*.py) lancés en Bash ne sont pas concernés.
import { readFileSync } from "node:fs";
import path from "node:path";

const input = JSON.parse(readFileSync(0, "utf8") || "{}");
const ti = input.tool_input || {};
const root = process.env.CLAUDE_PROJECT_DIR || process.cwd();
const rel = path.relative(root, ti.file_path || "").split(path.sep).join("/");

const block = (msg) => { process.stderr.write(msg + "\n"); process.exit(2); };

// 1. Fichiers générés ou sensibles : jamais à la main
const generated = {
  "sitemap.xml": "tools/build-sitemap.py (ou tools/geo-build.py)",
  "feed.xml": "tools/build-feed.py (ou tools/geo-build.py)",
  "llms-full.txt": "tools/build-llms-full.py (ou tools/geo-build.py)",
  "css/tailwind.css": "npm run build:css",
  "lexique-dommage-corporel.html": "tools/build-lexique.py",
};
if (generated[rel]) block(`Bloqué : ${rel} est généré. Utiliser ${generated[rel]}.`);
if (rel === "robots.txt") block("Bloqué : robots.txt ne se modifie qu'avec l'accord explicite d'Ilan, à la main.");

// 2. Déontologie sur le contenu publié
const published = /\.html$/.test(rel) || rel.startsWith("content/geo/") || rel === "llms.txt";
if (published) {
  const texts = [ti.content, ti.new_string, ...(ti.edits || []).map((e) => e.new_string)].filter(Boolean).join("\n");
  // Visent l'avocat ou le cabinet, pas un « médecin spécialisé » ni une « juridiction spécialisée ».
  const SUJET = String.raw`(?:avocats?|cabinet|ma[iî]tre\s+(?:ilan\s+)?guedj|ilan\s+guedj|me\s+guedj)`;
  const ENTRE = String.raw`(?:\s+[\p{L}'’-]+){0,3}\s+`;
  const rules = [
    [new RegExp(SUJET + ENTRE + String.raw`sp[ée]cialis\p{L}*`, "iu"), "« spécialiste / spécialisé » (dire « activité exclusivement consacrée au dommage corporel »)"],
    [new RegExp(String.raw`sp[ée]cialiste\s+(?:en|du)\s+dommage\s+corporel`, "iu"), "« spécialiste du dommage corporel »"],
    [new RegExp(SUJET + ENTRE + String.raw`(?:n°\s?1|numéro\s+un)(?![\p{L}\d])|(?:n°\s?1|numéro\s+un)\s+(?:en|du)\s+dommage`, "iu"), "« n°1 »"],
    [/meilleurs?\s+(?:avocats?|cabinets?)/iu, "« le meilleur avocat »"],
    [new RegExp(SUJET + ENTRE + String.raw`leaders?(?!\p{L})|leaders?\s+(?:en|du)\s+dommage`, "iu"), "« leader »"],
  ];
  for (const [re, label] of rules) {
    const m = texts.match(re);
    if (m) block(`Bloqué (déontologie) : ${label} dans ${rel} — « ${m[0]} ». Reformuler.`);
  }
}
process.exit(0);
