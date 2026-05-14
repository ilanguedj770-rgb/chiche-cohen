# Configurer Claude pour accéder à Google Search Console

Ce guide installe un serveur MCP qui permet à Claude de lire/manipuler tes données Google Search Console (GSC) — vérifier la performance, soumettre le sitemap, demander l'indexation d'URLs.

**Temps total : ~20 min** (à faire une seule fois).

## Vue d'ensemble

```
┌──────────────┐         ┌──────────────────┐         ┌──────────────────────┐
│ Claude Code  │ ──MCP──▶│ mcp-server-gsc   │ ──API──▶│ Google Search Console│
│ (chez toi)   │         │ (sur ta machine) │         │                      │
└──────────────┘         └──────────────────┘         └──────────────────────┘
                                  │
                                  ▼
                          credentials.json
                          (service account)
```

Tu vas créer un **compte de service Google** (= un robot Google), lui donner accès à ton GSC, et fournir sa clé à Claude.

---

## Étape 1 — Créer un projet Google Cloud

1. Va sur https://console.cloud.google.com
2. Connecte-toi avec le compte Google qui possède Google Search Console
3. En haut, clique sur le sélecteur de projet → **Nouveau projet**
4. Nom : `ig-avocat-gsc` (peu importe), pas d'organisation
5. **Créer**

## Étape 2 — Activer l'API Search Console

1. Dans le menu burger ☰ → **APIs et services** → **Bibliothèque**
2. Cherche `Search Console API`
3. Clique sur la carte → **Activer**

## Étape 3 — Créer un compte de service

1. ☰ → **APIs et services** → **Identifiants**
2. **+ CRÉER DES IDENTIFIANTS** → **Compte de service**
3. Nom du compte : `claude-gsc-reader` (peu importe)
4. **Créer et continuer** → **Continuer** (skip "Accorder un rôle") → **OK**
5. Tu reviens à la liste — clique sur l'email du compte de service que tu viens de créer
6. Onglet **Clés** → **AJOUTER UNE CLÉ** → **Créer une clé** → **JSON** → **Créer**
7. Un fichier JSON est téléchargé. **Garde-le précieusement** : c'est la clé.
8. **Note** l'adresse email du compte (de la forme `claude-gsc-reader@ig-avocat-gsc.iam.gserviceaccount.com`)

## Étape 4 — Donner accès au compte de service dans GSC

1. Va sur https://search.google.com/search-console
2. Sélectionne ta propriété `ig-avocat.com`
3. Roue dentée ⚙ en bas à gauche → **Utilisateurs et autorisations**
4. **AJOUTER UN UTILISATEUR**
5. Email = l'adresse du compte de service notée à l'étape 3 (`claude-gsc-reader@...iam.gserviceaccount.com`)
6. Autorisation = **Propriétaire** (pour pouvoir soumettre sitemap et demander indexation) ou **Plein** (lecture seule)
7. **Ajouter**

## Étape 5 — Placer la clé sur ta machine

```bash
# Crée le dossier de stockage des credentials
mkdir -p ~/.gsc

# Déplace le JSON téléchargé (adapte le nom du fichier)
mv ~/Downloads/ig-avocat-gsc-xxxxxx.json ~/.gsc/credentials.json

# Sécurise les permissions
chmod 600 ~/.gsc/credentials.json
```

⚠️ **Ne commit jamais ce fichier dans Git.** Il est déjà ignoré par `.gitignore`.

## Étape 6 — Redémarrer Claude Code

Ferme et rouvre ta session Claude Code sur le projet `chiche-cohen`. Le fichier `.mcp.json` du repo sera automatiquement détecté et Claude te demandera l'autorisation d'utiliser le serveur MCP `gsc`.

## Étape 7 — Vérifier que ça marche

Dans Claude, dis simplement :

> Liste les sites de mon Google Search Console

Ou :

> Quels sont mes top 10 requêtes sur les 28 derniers jours pour ig-avocat.com ?

Si l'auth fonctionne, Claude appelle le MCP et te retourne les données.

---

## Indexation (option avancée)

Le MCP `ahonn/mcp-server-gsc` (config par défaut) est en **lecture seule** : il sait afficher les performances, pas soumettre de sitemap ni demander d'indexation.

Pour avoir aussi les outils d'**indexation** (`submit_sitemap`, `submit_url`, `inspect_url`, etc.), il faut installer le MCP `Suganthans-GSC-MCP` :

```bash
cd ~
git clone https://github.com/Suganthan-Mohanadasan/Suganthans-GSC-MCP
cd Suganthans-GSC-MCP
npm install
npm run build
```

Puis, dans `.mcp.json`, copie le bloc `gsc-full` depuis la section `_alternatives` vers `mcpServers` et adapte le chemin si besoin.

⚠️ Ce MCP nécessite en plus que ton compte de service ait :
1. Le rôle **Propriétaire** dans GSC (pas seulement Plein)
2. L'API **Web Search Indexing** activée dans Google Cloud Console (Bibliothèque → "Web Search Indexing API")

---

## Que pourras-tu demander à Claude une fois branché ?

Avec `gsc` (lecture seule, config par défaut) :
- "Montre-moi les pages les plus cliquées sur les 90 derniers jours"
- "Quels mots-clés génèrent du trafic vers `accidents-route.html` ?"
- "Quelle est la position moyenne sur 'avocat dommage corporel marseille' ?"
- "Quelles pages ont chuté de position dans les 30 derniers jours ?"
- "Détecte les opportunités de quick wins (positions 4-10 sur des requêtes à fort volume)"

Avec `gsc-full` (lecture + écriture, config avancée), en plus :
- "Soumets le sitemap https://ig-avocat.com/sitemap.xml"
- "Demande l'indexation de https://ig-avocat.com/notre-bilan.html"
- "Inspecte le statut d'indexation de https://ig-avocat.com/blog/faute-conducteur-victime-indemnisation.html"

---

## Problèmes courants

**"PERMISSION_DENIED" lors d'un appel** → vérifie que l'email du compte de service est bien dans GSC > Utilisateurs et autorisations avec le bon niveau d'accès.

**"Search Console API not enabled"** → retourne dans Google Cloud Console → Bibliothèque → active "Google Search Console API".

**Claude ne voit pas le MCP** → vérifie que `~/.gsc/credentials.json` existe, que `.mcp.json` est bien à la racine du projet, et redémarre Claude Code complètement.

**Domaine non trouvé** → le format dépend de comment tu as vérifié ta propriété GSC. Si propriété "Domaine" : `sc-domain:ig-avocat.com`. Si propriété "URL préfixe" : `https://www.ig-avocat.com/`.

---

## Sécurité

- Le fichier `~/.gsc/credentials.json` est l'équivalent d'un mot de passe : ne le partage jamais.
- Il est gitignored par défaut.
- Pour révoquer l'accès : supprime le compte de service dans Google Cloud Console (ou retire-le de GSC > Utilisateurs et autorisations).
