# 🔒 Rapport d'Audit Sécuritaire — Claude Skills

**Date** : 2026-03-10 11:13:54
**Répertoire** : `Claude Skills Ultimate Bundle`
**VirusTotal** : ❌ Désactivé (analyse locale uniquement)

---

## 📊 Résumé Global

| Métrique | Valeur |
|----------|--------|
| **Skills scannées** | 501 |
| 🔴 Critique | 1 |
| 🟡 Suspect | 21 |
| 🔵 Info | 34 |
| 🟢 Clean | 445 |

> [!CAUTION]
> **1 skill(s) avec des findings critiques détectés !** Examiner en priorité.

---

## 🌐 VirusTotal API — Guide d'Utilisation pour l'Inspection de Skills

### Présentation

[VirusTotal](https://www.virustotal.com/) est un service gratuit qui analyse des fichiers, URLs, domaines et IP avec **70+ moteurs antivirus** et **10+ sandboxes d'analyse dynamique**. Son API v3 (REST + JSON) permet d'automatiser ces vérifications.

> **Note** : Les fichiers SKILL.md étant du texte Markdown, VirusTotal retournera généralement "clean" car il est optimisé pour les binaires et exécutables. L'analyse statique locale (patterns suspects) reste la méthode principale pour inspecter des skills.

### Authentification

1. Créer un compte gratuit sur [virustotal.com](https://www.virustotal.com/)
2. Récupérer votre clé API depuis [My API Key](https://www.virustotal.com/gui/my-apikey)
3. Inclure la clé dans chaque requête via le header `x-apikey`

```bash
# Exemple d'authentification
curl --request GET \
  --url "https://www.virustotal.com/api/v3/files/{sha256}" \
  --header "x-apikey: VOTRE_CLE_API"
```

### Limites de l'API gratuite

| Limite | Valeur |
|--------|--------|
| Requêtes par minute | 4 |
| Requêtes par jour | 500 |
| Taille max upload | 32 MB |
| Upload étendu | 650 MB (via `/files/upload_url`) |

### Endpoints principaux pour l'inspection de fichiers

#### 1. Vérifier un fichier par hash (sans upload)

```bash
# GET /files/{id} — Vérifier si un fichier est déjà connu de VT
SHA256=$(shasum -a 256 monFichier.md | awk '{print $1}')
curl --request GET \
  --url "https://www.virustotal.com/api/v3/files/$SHA256" \
  --header "x-apikey: $VT_API_KEY"
```

**Réponse** : Objet `File` avec `last_analysis_stats` contenant :
- `malicious` — nombre de moteurs détectant le fichier comme malveillant
- `suspicious` — nombre de moteurs le trouvant suspect
- `undetected` — nombre de moteurs ne détectant rien
- `harmless` — nombre de moteurs le considérant comme sûr

#### 2. Uploader un fichier pour scan

```bash
# POST /files — Soumettre un fichier pour analyse
curl --request POST \
  --url "https://www.virustotal.com/api/v3/files" \
  --header "x-apikey: $VT_API_KEY" \
  --form "file=@monFichier.md"
```

**Réponse** : Un `analysis_id` pour suivre la progression du scan.

#### 3. Scanner une URL

```bash
# POST /urls — Soumettre une URL pour analyse
curl --request POST \
  --url "https://www.virustotal.com/api/v3/urls" \
  --header "x-apikey: $VT_API_KEY" \
  --form "url=https://example.com"
```

#### 4. Récupérer le rapport d'une URL

```bash
# GET /urls/{id} — Récupérer le rapport d'analyse d'une URL
URL_ID=$(echo -n "https://example.com" | base64 | tr -d '=')
curl --request GET \
  --url "https://www.virustotal.com/api/v3/urls/$URL_ID" \
  --header "x-apikey: $VT_API_KEY"
```

### Intégration avec le script d'audit

Pour activer la vérification VirusTotal dans `skill_security_audit.py` :

```bash
# Audit avec VirusTotal activé
python3 skill_security_audit.py \
  --dir "Claude Skills Ultimate Bundle" \
  --vt-key "VOTRE_CLE_API"

# Audit avec VirusTotal + scan des URLs trouvées dans les skills
python3 skill_security_audit.py \
  --dir "Claude Skills Ultimate Bundle" \
  --vt-key "VOTRE_CLE_API" \
  --scan-urls

# Audit local uniquement (sans VirusTotal)
python3 skill_security_audit.py \
  --dir "Claude Skills Ultimate Bundle" \
  --no-vt
```

Le script effectue automatiquement :
1. **Hash lookup** (`GET /files/{sha256}`) pour chaque SKILL.md
2. Respect du **rate limiting** (4 req/min) avec attente automatique
3. Intégration des résultats VT dans le rapport final

### Exemple de réponse VT pour un fichier

```json
{
  "data": {
    "attributes": {
      "last_analysis_stats": {
        "malicious": 0,
        "suspicious": 0,
        "undetected": 62,
        "harmless": 0,
        "timeout": 0,
        "type-unsupported": 9,
        "failure": 0
      },
      "sha256": "e3b0c44298fc1c149afb...",
      "meaningful_name": "SKILL.md",
      "type_description": "Text"
    }
  }
}
```

---

## 🔍 Détails par Skill

### 🔴 Critique

#### `Legal & Compliance/terms-of-use-app/SKILL.md`
- **SHA-256** : `351206a314d41254...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 26 | 🔴 Prompt Injection | CRITICAL | Tentative d'override système → `OVERRIDE YOUR` |

### 🟡 Suspect

#### `Ads & Paid Media/discount-strategy/SKILL.md`
- **SHA-256** : `e801084ffd1f4c53...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Content & Copywriting/professional-bio/SKILL.md`
- **SHA-256** : `f8ed4c87d2c28fa5...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 209 | 🟡 Accès fichiers suspects | WARNING | Accès à des credentials → `credentials:` |

#### `Content & Copywriting/tutorial-writer/SKILL.md`
- **SHA-256** : `a8a20df4f839eb5f...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Grep Glob Bash` |
| 134 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://stripe.com` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls:*)' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Courses & Education/nutrition-content-plan/SKILL.md`
- **SHA-256** : `d0ce5c0b9b0d8985...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 192 | 🟡 Accès fichiers suspects | WARNING | Accès à des credentials → `credentials:` |

#### `Courses & Education/workshop-builder/SKILL.md`
- **SHA-256** : `87e5880d0921ff9c...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Email Marketing & Automation/welcome-sequence/SKILL.md`
- **SHA-256** : `11e1353744407711...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 79 | 🟡 Accès fichiers suspects | WARNING | Mot de passe défini en clair → `password:` |

#### `Finance & Pricing/financial-dashboard/SKILL.md`
- **SHA-256** : `7545afa415fe3fc7...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Finance & Pricing/profit-loss-report/SKILL.md`
- **SHA-256** : `2858f3129a0f5331...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash(ls:*) Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls:*)' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(python3:*)' |

#### `Finance & Pricing/tax-deduction-finder/SKILL.md`
- **SHA-256** : `b8b1c83094092b83...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Legal & Compliance/licensing-agreement/SKILL.md`
- **SHA-256** : `0d223294659e7188...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Legal & Compliance/nda-template/SKILL.md`
- **SHA-256** : `7b9639927c4737db...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Operations & Systems/delegation-framework/SKILL.md`
- **SHA-256** : `c599a28f3fecdc14...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Operations & Systems/retrospective/SKILL.md`
- **SHA-256** : `8e07e66954df38da...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Operations & Systems/time-audit/SKILL.md`
- **SHA-256** : `3dcd88351621fe3c...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Operations & Systems/workflow-mapper/SKILL.md`
- **SHA-256** : `9ae00f3bba9d179b...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `SEO & Search/checkout-optimizer/SKILL.md`
- **SHA-256** : `0ef8acaa88ceb064...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'WebFetch' |

#### `Sales & Funnels/coaching-framework/SKILL.md`
- **SHA-256** : `49aeb16f715ee20c...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Sales & Funnels/customer-journey-map/SKILL.md`
- **SHA-256** : `1668a166dd39df82...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(mkdir:*)' |

#### `Sales & Funnels/membership-site-plan/SKILL.md`
- **SHA-256** : `cd1ec7fe6cf15c47...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Sales & Funnels/partnership-proposal/SKILL.md`
- **SHA-256** : `dc35c25f3abd3d50...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

#### `Social Media/influencer-outreach/SKILL.md`
- **SHA-256** : `9c1220a23a05d278...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 4 | 🟡 Élévation de privilèges | WARNING | Accès terminal dans allowed-tools → `allowed-tools: Read Write Bash` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Bash(ls)' |

### 🔵 Info

#### `Ads & Paid Media/ad-copy/SKILL.md`
- **SHA-256** : `8ae80ecd054c7ee4...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 45 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://taskflow.app/start` |
| 317 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://fitproacademy.com/launch` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__resize-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Ads & Paid Media/affiliate-program/SKILL.md`
- **SHA-256** : `9af04af2786f3735...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 148 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://freelancemastery.com/?ref=alex-chen` |

#### `Ads & Paid Media/bundle-creator/SKILL.md`
- **SHA-256** : `2314cdef5666094c...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Branding & Design/brand-refresh/SKILL.md`
- **SHA-256** : `8e9a74b7fe2304fa...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__search-designs' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-content' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__start-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__perform-editing-operations' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__commit-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__cancel-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |

#### `Client & Consulting/survey-builder/SKILL.md`
- **SHA-256** : `4fd37a20e5cfd5b5...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |

#### `Content & Copywriting/content-calendar/SKILL.md`
- **SHA-256** : `144015c1bb4d2f94...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__create-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__move-item-to-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Content & Copywriting/faq-generator/SKILL.md`
- **SHA-256** : `e0b8a8a858a5ea95...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 161 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://schema.org` |
| 226 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://schema.org` |

#### `Content & Copywriting/newsletter-builder/SKILL.md`
- **SHA-256** : `1968cfbb3fd533bf...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Content & Copywriting/youtube-thumbnail/SKILL.md`
- **SHA-256** : `7b8b5c4b03054222...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__start-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__perform-editing-operations' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__commit-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__cancel-editing-transaction' |

#### `Courses & Education/course-outline/SKILL.md`
- **SHA-256** : `48f60e4de3d00e55...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Courses & Education/webinar-planner/SKILL.md`
- **SHA-256** : `f669aeb2890a521a...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Email Marketing & Automation/seasonal-campaign/SKILL.md`
- **SHA-256** : `930cb2af7d7720f1...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Email Marketing & Automation/thank-you-campaign/SKILL.md`
- **SHA-256** : `0bdacf471c267ddd...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Events & Speaking/event-planner/SKILL.md`
- **SHA-256** : `02bb68f4bf67d22e...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |

#### `Events & Speaking/launch-assets/SKILL.md`
- **SHA-256** : `25a7e8c588bb402e...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__resize-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__create-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__move-item-to-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Events & Speaking/launch-checklist/SKILL.md`
- **SHA-256** : `6725bd260834aea8...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Finance & Pricing/expense-tracker/SKILL.md`
- **SHA-256** : `cced0974fc840bfb...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Industry-Specific/api-documentation/SKILL.md`
- **SHA-256** : `230e046381c63c5b...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 122 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://api.example.com/v1/resource` |
| 213 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://api.invoicebot.com/v1/invoices` |

#### `Legal & Compliance/cookie-policy/SKILL.md`
- **SHA-256** : `844a352fb5229ecf...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 148 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://policies.google.com/privacy` |
| 149 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://www.facebook.com/privacy/policy` |

#### `Legal & Compliance/shipping-policy/SKILL.md`
- **SHA-256** : `b1756457e5ca2dff...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 113 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://usps.com` |
| 113 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://ups.com` |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Operations & Systems/client-crm/SKILL.md`
- **SHA-256** : `f4040820bc5259e1...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Operations & Systems/meeting-notes/SKILL.md`
- **SHA-256** : `edafd8775e69cf06...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Operations & Systems/project-tracker/SKILL.md`
- **SHA-256** : `c2ca1192e32f4ca1...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Operations & Systems/sop-builder/SKILL.md`
- **SHA-256** : `588fd92e3a3f7b7c...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Operations & Systems/vendor-evaluation/SKILL.md`
- **SHA-256** : `6b8685894f5813d8...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |

#### `SEO & Search/schema-markup-guide/SKILL.md`
- **SHA-256** : `3639b1910107abaf...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 87 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://schema.org` |
| 115 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://schema.org` |
| 143 | 🔵 URLs externes | INFO | URL externe (non-standard) → `https://schema.org` |

#### `Sales & Funnels/competitor-analysis/SKILL.md`
- **SHA-256** : `c1e64dd3359dd3fa...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Sales & Funnels/pitch-deck/SKILL.md`
- **SHA-256** : `29f4ab9251a5e794...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__request-outline-review' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-content' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__start-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__perform-editing-operations' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__commit-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__cancel-editing-transaction' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

#### `Sales & Funnels/product-comparison/SKILL.md`
- **SHA-256** : `00bee7c6ab32c715...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Sales & Funnels/product-roadmap/SKILL.md`
- **SHA-256** : `668b45143fe031f6...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-database' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-create-pages' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-search' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Notion__notion-fetch' |

#### `Social Media/brand-photography-brief/SKILL.md`
- **SHA-256** : `12606e9b94c5e334...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Social Media/hashtag-strategy/SKILL.md`
- **SHA-256** : `61ad814360320fe9...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Social Media/product-photography-brief/SKILL.md`
- **SHA-256** : `33a548178684b7e4...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'Edit' |

#### `Social Media/social-media-graphics/SKILL.md`
- **SHA-256** : `a2fcb5b76ae903fc...`
- **VT** : non vérifié

| Ligne | Catégorie | Sévérité | Détail |
|-------|-----------|----------|--------|
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__generate-design-structured' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__resize-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__export-design' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-export-formats' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__list-brand-kits' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__create-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__move-item-to-folder' |
| 0 | 🟡 Frontmatter YAML | INFO | Outil non-standard dans allowed-tools : 'mcp__claude_ai_Canva__get-design-thumbnail' |

### 🟢 Clean

- `AI & Technology/ai-content-policy/SKILL.md` — ✅ Aucun finding
- `AI & Technology/ai-ethics-policy/SKILL.md` — ✅ Aucun finding
- `AI & Technology/ai-use-case-finder/SKILL.md` — ✅ Aucun finding
- `AI & Technology/automation-workflow/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/ad-creative-brief/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/ad-performance-report/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/ad-spend-calculator/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/affiliate-recruitment/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/affiliate-terms/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/cross-sell-strategy/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/facebook-ad-campaign/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/google-ads-campaign/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/high-ticket-sales-page/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/linkedin-ad-campaign/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/lookalike-audience-plan/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/media-buy-plan/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/podcast-ad-script/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/retargeting-strategy/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/sales-page/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/tiktok-ad-script/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/tripwire-offer/SKILL.md` — ✅ Aucun finding
- `Ads & Paid Media/youtube-ad-script/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/ab-test-plan/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/analytics-setup-guide/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/attribution-model/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/benchmarking-report/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/cohort-analysis/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/conversion-funnel-analysis/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/customer-lifetime-value/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/data-collection-plan/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/data-dashboard-design/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/feedback-analysis/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/grant-report/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/impact-report/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/kpi-dashboard/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/marketplace-fee-structure/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/marketplace-metrics/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/metric-definition-guide/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/nonprofit-board-packet/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/prompt-library/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/saas-metrics-dashboard/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/sentiment-analysis/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/social-impact-measurement/SKILL.md` — ✅ Aucun finding
- `Analytics & Data/survey-analysis/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-architecture/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-audit/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-identity-guide/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-positioning-statement/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-tagline/SKILL.md` — ✅ Aucun finding
- `Branding & Design/brand-voice-guide/SKILL.md` — ✅ Aucun finding
- `Branding & Design/color-palette-generator/SKILL.md` — ✅ Aucun finding
- `Branding & Design/executive-resume/SKILL.md` — ✅ Aucun finding
- `Branding & Design/expert-positioning/SKILL.md` — ✅ Aucun finding
- `Branding & Design/icon-set-brief/SKILL.md` — ✅ Aucun finding
- `Branding & Design/merch-design-brief/SKILL.md` — ✅ Aucun finding
- `Branding & Design/mission-statement/SKILL.md` — ✅ Aucun finding
- `Branding & Design/naming-workshop/SKILL.md` — ✅ Aucun finding
- `Branding & Design/packaging-brief/SKILL.md` — ✅ Aucun finding
- `Branding & Design/portfolio-page/SKILL.md` — ✅ Aucun finding
- `Branding & Design/presentation-template-guide/SKILL.md` — ✅ Aucun finding
- `Branding & Design/rebrand-plan/SKILL.md` — ✅ Aucun finding
- `Branding & Design/signage-brief/SKILL.md` — ✅ Aucun finding
- `Branding & Design/signature-talk/SKILL.md` — ✅ Aucun finding
- `Branding & Design/speaking-one-sheet/SKILL.md` — ✅ Aucun finding
- `Branding & Design/style-tile/SKILL.md` — ✅ Aucun finding
- `Branding & Design/unboxing-experience/SKILL.md` — ✅ Aucun finding
- `Branding & Design/visual-identity-brief/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/agency-onboarding/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/client-feedback-system/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/client-intake-form/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/client-report-template/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/client-transformation-story/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/cohort-program/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/consulting-framework/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/consulting-proposal-template/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/diagnostic-assessment/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/group-program-design/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/industry-association-plan/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/mastermind-group/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/project-scope-change/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/quiz-generator/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/service-guarantee/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/service-productization/SKILL.md` — ✅ Aucun finding
- `Client & Consulting/skill-assessment/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/about-page/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/article-rewriter/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/authority-content-strategy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/blog-post/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/book-outline/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/book-proposal/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/brand-story/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/caption-writer/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/case-study/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/collection-page-copy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/comparison-article/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-audit/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-brief/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-cluster-plan/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-gap-finder/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-pillar-strategy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-repurpose/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/content-style-guide/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/donation-page-copy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/ebook-outline/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/expert-roundup-pitch/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/feature-announcement/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/ghostwriter-brief/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/headline-generator/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/help-center-article/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/hook-generator/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/landing-page-copy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/linkedin-article/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/listicle-generator/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/microcopy-writer/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/newsletter-strategy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/pillar-page/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/podcast-one-sheet/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/podcast-show-notes/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/press-kit/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/press-release/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/pricing-page-copy/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/product-changelog/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/product-description/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/product-faq/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/recipe-card/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/release-notes/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/script-to-blog/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/seo-content-brief/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/speech-writer/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/thought-leader-content-plan/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/thought-leadership/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/video-script/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/viral-content-formula/SKILL.md` — ✅ Aucun finding
- `Content & Copywriting/white-paper/SKILL.md` — ✅ Aucun finding
- `Courses & Education/certification-program/SKILL.md` — ✅ Aucun finding
- `Courses & Education/class-schedule-planner/SKILL.md` — ✅ Aucun finding
- `Courses & Education/continuing-education/SKILL.md` — ✅ Aucun finding
- `Courses & Education/curriculum-review/SKILL.md` — ✅ Aucun finding
- `Courses & Education/fitness-program-outline/SKILL.md` — ✅ Aucun finding
- `Courses & Education/homework-assignment/SKILL.md` — ✅ Aucun finding
- `Courses & Education/learning-path/SKILL.md` — ✅ Aucun finding
- `Courses & Education/lesson-plan/SKILL.md` — ✅ Aucun finding
- `Courses & Education/micro-course/SKILL.md` — ✅ Aucun finding
- `Courses & Education/podcast-launch/SKILL.md` — ✅ Aucun finding
- `Courses & Education/student-feedback-form/SKILL.md` — ✅ Aucun finding
- `Courses & Education/study-guide/SKILL.md` — ✅ Aucun finding
- `Courses & Education/ted-talk-outline/SKILL.md` — ✅ Aucun finding
- `Courses & Education/wellness-assessment/SKILL.md` — ✅ Aucun finding
- `Courses & Education/wellness-workshop-plan/SKILL.md` — ✅ Aucun finding
- `Courses & Education/workshop-handout/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/cross-border-selling/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/dropshipping-supplier-brief/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/exchange-policy/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/food-delivery-strategy/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/food-truck-business-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/gift-guide/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/investment-property-analysis/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/lease-agreement-checklist/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/marketplace-listing/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/neighborhood-guide/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/open-house-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/product-recall-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/product-sourcing-brief/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/property-listing/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/property-management-sop/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/real-estate-crm-setup/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/real-estate-newsletter/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/rental-listing/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/seasonal-inventory-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/seller-onboarding/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/size-guide/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/store-launch-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/subscription-box-plan/SKILL.md` — ✅ Aucun finding
- `E-commerce & Products/wholesale-catalog/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/abandoned-cart-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/ambassador-program/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/black-friday-emails/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/cart-recovery-sms/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/cause-marketing-campaign/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/cold-outreach/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/customer-review-strategy/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/downsell-sequence/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/drip-campaign/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-ab-test-plan/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-deliverability-audit/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-design-system/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-list-cleanup/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-newsletter-template/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-preference-center/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-sequence/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/email-subject-line-tester/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/engagement-playbook/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/flash-sale-campaign/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/launch-email-sequence/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/loyalty-program/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/milestone-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/order-bump-copy/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/payment-plan-offer/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/price-increase-notice/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/product-launch-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/re-engagement-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/referral-program/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/renewal-campaign/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/social-proof-collector/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/testimonial-collector/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/transactional-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/trial-to-paid-email/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/two-sided-email-strategy/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/upsell-sequence/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/user-generated-content/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/waitlist-builder/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/webinar-email-sequence/SKILL.md` — ✅ Aucun finding
- `Email Marketing & Automation/win-back-campaign/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/award-application/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/beta-launch-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/catering-proposal/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/conference-planner/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/digital-product-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-budget-planner/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-follow-up/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-marketing-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-registration-page/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-run-of-show/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/event-sponsorship-proposal/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/hybrid-event-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/marketplace-launch-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/networking-event-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/product-hunt-launch/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/product-launch-plan/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/retreat-planner/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/speaker-outreach/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/speaking-proposal/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/sponsor-thank-you/SKILL.md` — ✅ Aucun finding
- `Events & Speaking/virtual-event-platform/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/bookkeeping-setup/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/breakeven-analysis/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/budget-planner/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/cash-flow-forecast/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/commission-structure/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/compensation-plan/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/cost-analysis/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/financial-model/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/financial-projection/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/freelance-rate-card/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/fundraising-tracker/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/grant-application/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/investor-update/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/invoice-template/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/pricing-analysis/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/pricing-calculator/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/pricing-strategy/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/quarterly-review/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/rate-negotiation-script/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/revenue-forecast/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/roi-calculator/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/subscription-metrics/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/tax-prep-checklist/SKILL.md` — ✅ Aucun finding
- `Finance & Pricing/unit-economics/SKILL.md` — ✅ Aucun finding
- `HR & Team/annual-review/SKILL.md` — ✅ Aucun finding
- `HR & Team/benefits-guide/SKILL.md` — ✅ Aucun finding
- `HR & Team/contractor-brief/SKILL.md` — ✅ Aucun finding
- `HR & Team/culture-document/SKILL.md` — ✅ Aucun finding
- `HR & Team/diversity-policy/SKILL.md` — ✅ Aucun finding
- `HR & Team/employee-handbook/SKILL.md` — ✅ Aucun finding
- `HR & Team/employee-survey/SKILL.md` — ✅ Aucun finding
- `HR & Team/exit-interview-template/SKILL.md` — ✅ Aucun finding
- `HR & Team/freelancer-management/SKILL.md` — ✅ Aucun finding
- `HR & Team/hiring-scorecard/SKILL.md` — ✅ Aucun finding
- `HR & Team/interview-question-bank/SKILL.md` — ✅ Aucun finding
- `HR & Team/job-posting/SKILL.md` — ✅ Aucun finding
- `HR & Team/mentorship-program/SKILL.md` — ✅ Aucun finding
- `HR & Team/offboarding-checklist/SKILL.md` — ✅ Aucun finding
- `HR & Team/offer-letter/SKILL.md` — ✅ Aucun finding
- `HR & Team/okr-builder/SKILL.md` — ✅ Aucun finding
- `HR & Team/onboarding-checklist/SKILL.md` — ✅ Aucun finding
- `HR & Team/one-on-one-template/SKILL.md` — ✅ Aucun finding
- `HR & Team/performance-review/SKILL.md` — ✅ Aucun finding
- `HR & Team/pip-template/SKILL.md` — ✅ Aucun finding
- `HR & Team/referral-bonus-plan/SKILL.md` — ✅ Aucun finding
- `HR & Team/remote-team-handbook/SKILL.md` — ✅ Aucun finding
- `HR & Team/remote-work-policy/SKILL.md` — ✅ Aucun finding
- `HR & Team/succession-plan/SKILL.md` — ✅ Aucun finding
- `HR & Team/team-building-plan/SKILL.md` — ✅ Aucun finding
- `HR & Team/team-charter/SKILL.md` — ✅ Aucun finding
- `HR & Team/training-manual/SKILL.md` — ✅ Aucun finding
- `HR & Team/training-plan/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/health-disclaimer/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/no-code-app-plan/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/platform-help-center/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/platform-partnership/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/platform-trust-system/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/restaurant-marketing-plan/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/restaurant-review-response/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/restaurant-sop/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/saas-evaluation/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/seasonal-menu-plan/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/supplement-disclaimer/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/tech-stack-recommendation/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/tenant-screening-checklist/SKILL.md` — ✅ Aucun finding
- `Industry-Specific/tool-stack-audit/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/annual-report-writer/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/chatbot-script/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/churn-analysis/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/churn-prevention-playbook/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/complaint-resolution/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/customer-advisory-board/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/customer-health-score/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/customer-success-playbook/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/customer-support-kb/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/customer-win-story/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/feature-request-system/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/nps-survey/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/onboarding-flow/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/product-feedback-loop/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/review-response/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/saas-cancellation-flow/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/saas-onboarding-flow/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/satisfaction-survey/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/self-service-portal/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/service-level-agreement/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/service-recovery-plan/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/support-response-templates/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/user-research-plan/SKILL.md` — ✅ Aucun finding
- `Launch & Growth/voice-of-customer/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/accessibility-policy/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/cease-and-desist/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/client-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/compliance-checklist/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/contract-writer/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/copyright-notice/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/data-processing-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/disclaimer-generator/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/expense-policy/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/gdpr-compliance-checklist/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/independent-contractor-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/intellectual-property-audit/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/letter-of-intent/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/non-compete-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/partnership-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/payment-terms-policy/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/privacy-policy/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/retainer-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/return-policy/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/saas-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/subcontractor-agreement/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/terms-of-service/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/trademark-application/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/waiver-release/SKILL.md` — ✅ Aucun finding
- `Legal & Compliance/workplace-policy/SKILL.md` — ✅ Aucun finding
- `Nonprofit & Community/nonprofit-fundraising-letter/SKILL.md` — ✅ Aucun finding
- `Nonprofit & Community/volunteer-recruitment/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/annual-planning/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/batch-processing-system/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/business-continuity-plan/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/change-management-plan/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/decision-matrix/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/energy-management/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/escalation-procedure/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/fulfillment-sop/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/inventory-management/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/knowledge-base-builder/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/meeting-agenda/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/morning-routine-builder/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/process-automation-audit/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/quality-assurance-checklist/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/report-automation/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/risk-assessment/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/scope-of-work/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/status-update-template/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/task-prioritization/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/vendor-onboarding/SKILL.md` — ✅ Aucun finding
- `Operations & Systems/weekly-report/SKILL.md` — ✅ Aucun finding
- `SEO & Search/featured-snippet-optimizer/SKILL.md` — ✅ Aucun finding
- `SEO & Search/google-business-profile/SKILL.md` — ✅ Aucun finding
- `SEO & Search/keyword-research/SKILL.md` — ✅ Aucun finding
- `SEO & Search/landing-page-audit/SKILL.md` — ✅ Aucun finding
- `SEO & Search/link-building-plan/SKILL.md` — ✅ Aucun finding
- `SEO & Search/local-seo-plan/SKILL.md` — ✅ Aucun finding
- `SEO & Search/marketplace-seo/SKILL.md` — ✅ Aucun finding
- `SEO & Search/meta-tag-optimizer/SKILL.md` — ✅ Aucun finding
- `SEO & Search/platform-migration/SKILL.md` — ✅ Aucun finding
- `SEO & Search/product-listing-optimizer/SKILL.md` — ✅ Aucun finding
- `SEO & Search/seo-audit/SKILL.md` — ✅ Aucun finding
- `SEO & Search/seo-competitor-analysis/SKILL.md` — ✅ Aucun finding
- `SEO & Search/seo-migration-plan/SKILL.md` — ✅ Aucun finding
- `SEO & Search/seo-reporting-template/SKILL.md` — ✅ Aucun finding
- `SEO & Search/site-architecture-plan/SKILL.md` — ✅ Aucun finding
- `SEO & Search/store-page-audit/SKILL.md` — ✅ Aucun finding
- `SEO & Search/technical-seo-checklist/SKILL.md` — ✅ Aucun finding
- `SEO & Search/youtube-seo/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/business-plan/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/collaboration-agreement/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/customer-persona/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/customer-segmentation/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/discovery-call-script/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/joint-venture-proposal/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/lead-magnet/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/market-research/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/market-sizing/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/objection-handler/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/proposal-writer/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/revenue-model/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/sales-battlecard/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/sales-deck/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/sales-email-template/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/sales-funnel-builder/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/sales-script/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/strategic-alliance-plan/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/swot-analysis/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/value-proposition-canvas/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/webinar-sales-script/SKILL.md` — ✅ Aucun finding
- `Sales & Funnels/win-loss-analysis/SKILL.md` — ✅ Aucun finding
- `Social Media/author-platform-plan/SKILL.md` — ✅ Aucun finding
- `Social Media/co-marketing-plan/SKILL.md` — ✅ Aucun finding
- `Social Media/community-launch/SKILL.md` — ✅ Aucun finding
- `Social Media/community-moderation/SKILL.md` — ✅ Aucun finding
- `Social Media/crisis-comms/SKILL.md` — ✅ Aucun finding
- `Social Media/facebook-group-plan/SKILL.md` — ✅ Aucun finding
- `Social Media/food-photography-brief/SKILL.md` — ✅ Aucun finding
- `Social Media/guest-post-pitch/SKILL.md` — ✅ Aucun finding
- `Social Media/influencer-campaign-brief/SKILL.md` — ✅ Aucun finding
- `Social Media/instagram-carousel/SKILL.md` — ✅ Aucun finding
- `Social Media/linkedin-profile-optimizer/SKILL.md` — ✅ Aucun finding
- `Social Media/linkedin-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/media-kit/SKILL.md` — ✅ Aucun finding
- `Social Media/meme-content-brief/SKILL.md` — ✅ Aucun finding
- `Social Media/menu-design-brief/SKILL.md` — ✅ Aucun finding
- `Social Media/networking-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/personal-brand-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/pinterest-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/platform-community-guidelines/SKILL.md` — ✅ Aucun finding
- `Social Media/podcast-guest-pitch/SKILL.md` — ✅ Aucun finding
- `Social Media/pr-pitch/SKILL.md` — ✅ Aucun finding
- `Social Media/reddit-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/short-form-video-plan/SKILL.md` — ✅ Aucun finding
- `Social Media/social-listening-plan/SKILL.md` — ✅ Aucun finding
- `Social Media/social-media-audit/SKILL.md` — ✅ Aucun finding
- `Social Media/social-media-calendar/SKILL.md` — ✅ Aucun finding
- `Social Media/social-media-policy/SKILL.md` — ✅ Aucun finding
- `Social Media/social-media-strategy/SKILL.md` — ✅ Aucun finding
- `Social Media/sponsor-pitch/SKILL.md` — ✅ Aucun finding
- `Social Media/thread-hook-writer/SKILL.md` — ✅ Aucun finding
- `Social Media/tiktok-script/SKILL.md` — ✅ Aucun finding
- `Social Media/twitter-thread/SKILL.md` — ✅ Aucun finding
- `Social Media/youtube-strategy/SKILL.md` — ✅ Aucun finding

---

## 💡 Recommandations

1. **Examiner les skills critiques** — Vérifier manuellement chaque finding 🔴 pour déterminer s'il s'agit d'un vrai risque ou d'un faux positif
2. **Ne pas installer aveuglément** — Toute skill avec des findings critiques doit être revue avant utilisation
3. **Revue des suspects** — Les findings 🟡 méritent une attention mais sont souvent des faux positifs (ex: `curl` mentionné dans de la documentation)
4. **Auditer régulièrement** — Relancer ce script après chaque mise à jour du bundle
5. **Principe de moindre privilège** — Préférer les skills avec des `allowed-tools` restreints
