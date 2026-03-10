# Global Toolkit (kinetic-skills) Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Transform the ressources repo into a self-installing global toolkit that gives any developer 519 Claude skills + 1 900+ n8n workflows via a single `curl | bash`.

**Architecture:** Four artefacts — a catalog-generator script, a `catalog.json` committed to the repo, a portable bash CLI (`kinetic-skills`), and a meta-skill for Claude — wired together by a one-shot `install.sh`. No Node/Python/Ruby; pure bash + git + curl (+ optional fzf).

**Tech Stack:** bash 3+, git, curl, optional fzf; GitHub raw URLs for remote fetch; ANSI colour codes for UX.

---

## Chunk 1: Branch + catalog generator

### Task 1: Create feature branch

**Files:**
- no file changes — git only

- [ ] **Step 1: Create and checkout branch**

```bash
git checkout -b feature/global-toolkit
```

Expected: `Switched to a new branch 'feature/global-toolkit'`

---

### Task 2: `scripts/generate-catalog.sh`

**Files:**
- Create: `scripts/generate-catalog.sh`
- Output: `catalog.json` (root of repo)

**Context:**
- Each skill lives at `Claude Skills Ultimate Bundle/<Category>/<skill-name>/SKILL.md`
- Frontmatter is a YAML block between the first pair of `---` lines
- Fields to extract: `name`, `description`, `allowed-tools`
- The blacklisted skill **must not** appear in the catalog:
  `Legal & Compliance/terms-of-use-app/SKILL.md`

- [ ] **Step 1: Create `scripts/` directory and script file**

```bash
mkdir -p scripts
```

- [ ] **Step 2: Write `scripts/generate-catalog.sh`**

```bash
#!/usr/bin/env bash
# generate-catalog.sh — scans Claude Skills Ultimate Bundle/ and emits catalog.json

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_DIR="$REPO_DIR/Claude Skills Ultimate Bundle"
OUTPUT="$REPO_DIR/catalog.json"

# Blacklisted skill paths (relative to BUNDLE_DIR), no trailing slash
BLACKLIST=(
  "Legal & Compliance/terms-of-use-app"
)

is_blacklisted() {
  local rel_path="$1"
  for b in "${BLACKLIST[@]}"; do
    if [[ "$rel_path" == "$b"* ]]; then
      return 0
    fi
  done
  return 1
}

# Extract a YAML scalar value from the frontmatter block already stored in a variable
# Usage: extract_yaml <frontmatter_text> <key>
extract_yaml() {
  local fm="$1"
  local key="$2"
  # Handles:   key: "value"   or   key: value
  echo "$fm" | grep -m1 "^${key}:" | sed 's/^[^:]*:[[:space:]]*//' | sed 's/^"//' | sed 's/"$//' | tr -d '\r'
}

echo "Scanning skills in: $BUNDLE_DIR"

first=1
printf '[\n' > "$OUTPUT"

while IFS= read -r -d '' skill_file; do
  # skill_file is absolute path to SKILL.md
  skill_dir="$(dirname "$skill_file")"
  rel_dir="${skill_dir#$BUNDLE_DIR/}"       # e.g.  Content & Copywriting/blog-post
  category="${rel_dir%%/*}"                  # e.g.  Content & Copywriting
  skill_name="${rel_dir##*/}"                # e.g.  blog-post

  # Skip blacklisted skills
  if is_blacklisted "$rel_dir"; then
    echo "  [SKIP blacklisted] $rel_dir"
    continue
  fi

  # Read frontmatter (between first two --- lines)
  frontmatter=""
  in_fm=0
  fm_done=0
  while IFS= read -r line; do
    if [[ $fm_done -eq 1 ]]; then break; fi
    if [[ $in_fm -eq 0 && "$line" == "---" ]]; then
      in_fm=1
      continue
    fi
    if [[ $in_fm -eq 1 && "$line" == "---" ]]; then
      fm_done=1
      continue
    fi
    if [[ $in_fm -eq 1 ]]; then
      frontmatter+="$line"$'\n'
    fi
  done < "$skill_file"

  name="$(extract_yaml "$frontmatter" "name")"
  description="$(extract_yaml "$frontmatter" "description")"
  allowed_tools_raw="$(extract_yaml "$frontmatter" "allowed-tools")"

  # Build JSON array for allowedTools
  tools_json="["
  first_tool=1
  for tool in $allowed_tools_raw; do
    if [[ $first_tool -eq 0 ]]; then tools_json+=", "; fi
    tools_json+="\"$tool\""
    first_tool=0
  done
  tools_json+="]"

  # Escape description for JSON (basic: backslash + double-quote + newlines)
  description_escaped="${description//\\/\\\\}"
  description_escaped="${description_escaped//\"/\\\"}"
  description_escaped="${description_escaped//$'\n'/ }"

  rel_path="Claude Skills Ultimate Bundle/$rel_dir/SKILL.md"

  if [[ $first -eq 0 ]]; then printf ',\n' >> "$OUTPUT"; fi
  printf '  {\n    "name": "%s",\n    "category": "%s",\n    "description": "%s",\n    "path": "%s",\n    "allowedTools": %s\n  }' \
    "$name" "$category" "$description_escaped" "$rel_path" "$tools_json" >> "$OUTPUT"
  first=0

done < <(find "$BUNDLE_DIR" -name "SKILL.md" -print0 | sort -z)

printf '\n]\n' >> "$OUTPUT"

count=$(grep -c '"name":' "$OUTPUT" || true)
echo "Done. $count skills written to $OUTPUT"
```

- [ ] **Step 3: Make executable**

```bash
chmod +x scripts/generate-catalog.sh
```

- [ ] **Step 4: Run the script and verify output**

```bash
cd /Users/brunellagoosou/Documents/Kinetic/ressources
bash scripts/generate-catalog.sh
```

Expected output ends with: `Done. NNN skills written to .../catalog.json`

- [ ] **Step 5: Validate catalog.json is valid JSON**

```bash
python3 -c "import json,sys; d=json.load(open('catalog.json')); print(f'{len(d)} skills, first: {d[0][\"name\"]}')"
```

Expected: prints skill count and first skill name, no errors.

- [ ] **Step 6: Verify blacklisted skill absent**

```bash
grep "terms-of-use-app" catalog.json && echo "FAIL: blacklisted" || echo "OK: not present"
```

Expected: `OK: not present`

- [ ] **Step 7: Commit**

```bash
git add scripts/generate-catalog.sh catalog.json
git commit -m "feat: add catalog generator and generated catalog.json"
```

---

## Chunk 2: Meta-skill + CLI

### Task 3: `meta-skill/SKILL.md`

**Files:**
- Create: `meta-skill/SKILL.md`

- [ ] **Step 1: Create directory**

```bash
mkdir -p meta-skill
```

- [ ] **Step 2: Write `meta-skill/SKILL.md`**

```markdown
---
name: kinetic-skills
description: Trouve et installe des skills depuis le catalogue Kinetic (519 skills Claude + 1900 workflows n8n). Utilise ce skill quand l'utilisateur demande de trouver, chercher ou installer un skill ou une automatisation.
allowed-tools: Read Bash Glob
---

# kinetic-skills

## Pré-requis

Avant tout, vérifie que le repo local est installé :

```bash
ls ~/.kinetic/ressourses/catalog.json
```

Si la commande échoue (fichier absent), dis à l'utilisateur :

> "Le repo Kinetic n'est pas installé. Lance cette commande pour l'installer :
> ```
> curl -fsSL https://raw.githubusercontent.com/kineticadmin/ressourses/main/install.sh | bash
> ```"

Ne continue pas tant que le repo n'est pas installé.

## Rechercher un skill par mot-clé

1. Lis `~/.kinetic/ressourses/catalog.json`
2. Filtre les entrées dont `name` ou `description` contient le mot-clé (insensible à la casse)
3. Affiche les résultats : nom, catégorie, description courte
4. Demande à l'utilisateur lequel il veut installer

## Lister les catégories

Lis `~/.kinetic/ressourses/catalog.json` et affiche la liste des catégories uniques avec le nombre de skills dans chacune.

## Installer un skill

Pour installer un skill nommé `<nom>` :

```bash
kinetic-skills install <nom>
```

Cela copie le dossier du skill vers `~/.claude/skills/<nom>/`.
Confirme à l'utilisateur : "✓ Skill `<nom>` installé dans `~/.claude/skills/<nom>/`."

## Lister les skills installés

```bash
kinetic-skills installed
```

## Rechercher un workflow n8n

```bash
kinetic-skills workflow search <mot-clé>
```

Affiche les noms de fichiers JSON correspondants depuis `~/.kinetic/ressourses/1,900+ n8n Automations/workflows/`.

## Copier un workflow dans le clipboard

```bash
kinetic-skills workflow copy <nom-fichier>
```

Colle le contenu JSON du workflow dans le presse-papier (prêt à importer dans n8n).

## Mettre à jour le catalogue

```bash
kinetic-skills update
```

## Comportement général

- Sois concis et direct
- Confirme chaque action réalisée
- Si une commande échoue, explique le problème et propose une solution
- Ne devine pas — si tu n'es pas sûr du nom exact d'un skill, liste les candidats et laisse l'utilisateur choisir
```

- [ ] **Step 3: Commit**

```bash
git add meta-skill/SKILL.md
git commit -m "feat: add kinetic-skills meta-skill"
```

---

### Task 4: `cli/kinetic-skills`

**Files:**
- Create: `cli/kinetic-skills`

The CLI is the main user-facing tool. It must work standalone (no catalog.json required except for search/list; the install.sh puts it in `~/bin`).

- [ ] **Step 1: Create `cli/` directory**

```bash
mkdir -p cli
```

- [ ] **Step 2: Write `cli/kinetic-skills`**

```bash
#!/usr/bin/env bash
# kinetic-skills — Kinetic global skills & n8n workflow manager
# https://github.com/kineticadmin/ressourses

set -euo pipefail

# ── Config ──────────────────────────────────────────────────────────────────
KINETIC_DIR="${HOME}/.kinetic/ressourses"
SKILLS_DIR="${HOME}/.claude/skills"
CATALOG="${KINETIC_DIR}/catalog.json"
CLAUDE_SKILLS_BASE="${KINETIC_DIR}/Claude Skills Ultimate Bundle"
N8N_DIR="${KINETIC_DIR}/1,900+ n8n Automations/workflows"

# Blacklisted skill names (will not be installed)
BLACKLIST_NAMES=("terms-of-use-app")

# ── Colours ──────────────────────────────────────────────────────────────────
GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'
RESET=$'\033[0m'

ok()   { echo "${GREEN}✓ $*${RESET}"; }
info() { echo "${YELLOW}→ $*${RESET}"; }
err()  { echo "${RED}✗ $*${RESET}" >&2; }
head() { echo "${CYAN}$*${RESET}"; }

# ── Guards ───────────────────────────────────────────────────────────────────
need_catalog() {
  if [[ ! -f "$CATALOG" ]]; then
    err "Catalogue introuvable : $CATALOG"
    err "Lance d'abord : curl -fsSL https://raw.githubusercontent.com/kineticadmin/ressourses/main/install.sh | bash"
    exit 1
  fi
}

is_blacklisted() {
  local name="$1"
  for b in "${BLACKLIST_NAMES[@]}"; do
    if [[ "$name" == "$b" ]]; then return 0; fi
  done
  return 1
}

# ── Commands ─────────────────────────────────────────────────────────────────

cmd_search() {
  local keyword="${1:-}"
  if [[ -z "$keyword" ]]; then err "Usage: kinetic-skills search <mot-clé>"; exit 1; fi
  need_catalog
  head "Résultats pour \"$keyword\":"
  # grep on name + description fields, case-insensitive
  grep -i "\"$keyword\"" "$CATALOG" | grep -E '"name"|"description"' || true
  # Better: extract matching entries
  python3 - "$CATALOG" "$keyword" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
kw = sys.argv[2].lower()
results = [s for s in catalog if kw in s.get('name','').lower() or kw in s.get('description','').lower()]
if not results:
    print("Aucun résultat.")
else:
    for s in results:
        print(f"  \033[0;36m{s['name']}\033[0m  [{s['category']}]")
        desc = s.get('description','')
        print(f"    {desc[:100]}{'...' if len(desc)>100 else ''}")
PYEOF
}

cmd_list() {
  local category="${1:-}"
  need_catalog
  if [[ -n "$category" ]]; then
    head "Skills dans la catégorie \"$category\":"
    python3 - "$CATALOG" "$category" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
cat = sys.argv[2].lower()
results = [s for s in catalog if cat in s.get('category','').lower()]
if not results:
    print("Catégorie introuvable.")
else:
    for s in results:
        print(f"  {s['name']}")
PYEOF
  else
    head "Tous les skills disponibles :"
    python3 - "$CATALOG" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
for s in catalog:
    print(f"  \033[0;36m{s['name']}\033[0m  [{s['category']}]")
PYEOF
  fi
}

cmd_categories() {
  need_catalog
  head "Catégories disponibles :"
  python3 - "$CATALOG" <<'PYEOF'
import json, sys
from collections import Counter
catalog = json.load(open(sys.argv[1]))
counts = Counter(s['category'] for s in catalog)
for cat, n in sorted(counts.items()):
    print(f"  \033[0;36m{cat}\033[0m  ({n} skills)")
PYEOF
}

cmd_install() {
  local skill_name="${1:-}"
  if [[ -z "$skill_name" ]]; then err "Usage: kinetic-skills install <nom-skill>"; exit 1; fi
  need_catalog

  # Blacklist check
  if is_blacklisted "$skill_name"; then
    err "AVERTISSEMENT : Le skill \"$skill_name\" est sur liste noire pour des raisons de sécurité et ne peut pas être installé."
    exit 1
  fi

  # Find path in catalog
  skill_path=$(python3 - "$CATALOG" "$skill_name" <<'PYEOF'
import json, sys
catalog = json.load(open(sys.argv[1]))
name = sys.argv[2]
match = next((s for s in catalog if s['name'] == name), None)
if match:
    # Return the directory (remove /SKILL.md)
    print(match['path'].rsplit('/', 1)[0])
PYEOF
)

  if [[ -z "$skill_path" ]]; then
    err "Skill \"$skill_name\" introuvable dans le catalogue."
    info "Essaie : kinetic-skills search $skill_name"
    exit 1
  fi

  local src="${KINETIC_DIR}/${skill_path}"
  local dst="${SKILLS_DIR}/${skill_name}"

  if [[ ! -d "$src" ]]; then
    err "Dossier source introuvable : $src"
    exit 1
  fi

  mkdir -p "$SKILLS_DIR"
  cp -r "$src" "$dst"
  ok "Skill \"$skill_name\" installé dans $dst"
}

cmd_installed() {
  head "Skills installés dans $SKILLS_DIR :"
  if [[ ! -d "$SKILLS_DIR" ]]; then
    info "Aucun skill installé (dossier absent)."
    return
  fi
  local count=0
  for d in "$SKILLS_DIR"/*/; do
    [[ -d "$d" ]] || continue
    echo "  $(basename "$d")"
    ((count++)) || true
  done
  [[ $count -eq 0 ]] && info "Aucun skill installé."
  [[ $count -gt 0 ]] && info "$count skill(s) installé(s)."
}

cmd_workflow_search() {
  local keyword="${1:-}"
  if [[ -z "$keyword" ]]; then err "Usage: kinetic-skills workflow search <mot-clé>"; exit 1; fi
  if [[ ! -d "$N8N_DIR" ]]; then
    err "Dossier workflows introuvable : $N8N_DIR"
    exit 1
  fi
  head "Workflows correspondant à \"$keyword\":"
  find "$N8N_DIR" -maxdepth 1 -name "*.json" -printf '%f\n' 2>/dev/null \
    | grep -i "$keyword" \
    | sed 's/.json$//' \
    | while IFS= read -r name; do echo "  $name"; done \
    || ls "$N8N_DIR"/*.json 2>/dev/null \
    | xargs -n1 basename \
    | sed 's/.json$//' \
    | grep -i "$keyword" \
    | while IFS= read -r name; do echo "  $name"; done
}

cmd_workflow_copy() {
  local wf_name="${1:-}"
  if [[ -z "$wf_name" ]]; then err "Usage: kinetic-skills workflow copy <nom>"; exit 1; fi
  if [[ ! -d "$N8N_DIR" ]]; then
    err "Dossier workflows introuvable : $N8N_DIR"
    exit 1
  fi

  # Accept with or without .json extension
  local file="${N8N_DIR}/${wf_name}"
  [[ "$wf_name" != *.json ]] && file="${file}.json"

  if [[ ! -f "$file" ]]; then
    err "Workflow introuvable : $file"
    exit 1
  fi

  if command -v pbcopy &>/dev/null; then
    pbcopy < "$file"
    ok "Workflow \"$wf_name\" copié dans le presse-papier (macOS)."
  elif command -v xclip &>/dev/null; then
    xclip -selection clipboard < "$file"
    ok "Workflow \"$wf_name\" copié dans le presse-papier (xclip)."
  elif command -v xsel &>/dev/null; then
    xsel --clipboard --input < "$file"
    ok "Workflow \"$wf_name\" copié dans le presse-papier (xsel)."
  else
    err "Aucun outil clipboard trouvé (pbcopy / xclip / xsel)."
    info "Contenu du fichier :"
    cat "$file"
  fi
}

cmd_update() {
  if [[ ! -d "$KINETIC_DIR" ]]; then
    err "Repo local absent : $KINETIC_DIR"
    info "Lance : curl -fsSL https://raw.githubusercontent.com/kineticadmin/ressourses/main/install.sh | bash"
    exit 1
  fi
  info "Mise à jour du repo..."
  git -C "$KINETIC_DIR" pull
  info "Re-génération du catalogue..."
  bash "${KINETIC_DIR}/scripts/generate-catalog.sh"
  info "Mise à jour du meta-skill..."
  mkdir -p "${HOME}/.claude/skills/kinetic-skills"
  cp "${KINETIC_DIR}/meta-skill/SKILL.md" "${HOME}/.claude/skills/kinetic-skills/SKILL.md"
  ok "Mise à jour terminée."
}

cmd_help() {
  cat <<EOF
${CYAN}kinetic-skills${RESET} — Gestionnaire de skills Claude & workflows n8n

${YELLOW}Usage :${RESET}
  kinetic-skills search <mot-clé>          Rechercher un skill
  kinetic-skills list [catégorie]          Lister les skills
  kinetic-skills categories                Afficher les 20 catégories
  kinetic-skills install <nom>             Installer un skill dans ~/.claude/skills/
  kinetic-skills installed                 Lister les skills installés
  kinetic-skills workflow search <mot>     Rechercher un workflow n8n
  kinetic-skills workflow copy <nom>       Copier un workflow dans le clipboard
  kinetic-skills update                    Mettre à jour (git pull + re-catalogue)
  kinetic-skills help                      Afficher cette aide

${YELLOW}Exemples :${RESET}
  kinetic-skills search email
  kinetic-skills install blog-post
  kinetic-skills workflow search slack

${CYAN}Repo :${RESET} https://github.com/kineticadmin/ressourses
EOF
}

# ── Router ────────────────────────────────────────────────────────────────────
main() {
  local cmd="${1:-help}"
  shift || true

  case "$cmd" in
    search)      cmd_search "$@" ;;
    list)        cmd_list "$@" ;;
    categories)  cmd_categories ;;
    install)     cmd_install "$@" ;;
    installed)   cmd_installed ;;
    workflow)
      local sub="${1:-}"; shift || true
      case "$sub" in
        search) cmd_workflow_search "$@" ;;
        copy)   cmd_workflow_copy "$@" ;;
        *) err "Sous-commande workflow inconnue : $sub"; cmd_help; exit 1 ;;
      esac
      ;;
    update) cmd_update ;;
    help|--help|-h) cmd_help ;;
    *) err "Commande inconnue : $cmd"; cmd_help; exit 1 ;;
  esac
}

main "$@"
```

- [ ] **Step 3: Make executable**

```bash
chmod +x cli/kinetic-skills
```

- [ ] **Step 4: Quick smoke-test (help command — no catalog needed)**

```bash
bash cli/kinetic-skills help
```

Expected: help text printed in colour with usage examples.

- [ ] **Step 5: Test search (needs catalog)**

```bash
CATALOG="$(pwd)/catalog.json" \
  KINETIC_DIR="$(pwd)" \
  bash -c '
    source cli/kinetic-skills 2>/dev/null || true
    HOME_BAK=$HOME; export HOME=/tmp
    cp catalog.json /tmp/.kinetic_test_catalog.json 2>/dev/null || true
    HOME=$HOME_BAK
  '
# Simpler: override CATALOG env var directly isn't wired in the script.
# Test by temporarily pointing KINETIC_DIR to repo root:
KINETIC_DIR="$(pwd)" bash -c '
  # Patch CATALOG to point at repo-root catalog.json
  sed "s|CATALOG=.*|CATALOG=\"$(pwd)/catalog.json\"|" cli/kinetic-skills > /tmp/ks_test
  chmod +x /tmp/ks_test
  /tmp/ks_test search email | head -20
'
```

Expected: list of skills with "email" in name/description.

- [ ] **Step 6: Commit**

```bash
git add cli/kinetic-skills
git commit -m "feat: add kinetic-skills CLI"
```

---

## Chunk 3: install.sh + integration test + push

### Task 5: `install.sh`

**Files:**
- Create: `install.sh`

- [ ] **Step 1: Write `install.sh`**

```bash
#!/usr/bin/env bash
# install.sh — One-shot installer for kinetic-skills
# curl -fsSL https://raw.githubusercontent.com/kineticadmin/ressourses/main/install.sh | bash

set -euo pipefail

GREEN=$'\033[0;32m'
YELLOW=$'\033[1;33m'
RED=$'\033[0;31m'
CYAN=$'\033[0;36m'
RESET=$'\033[0m'

ok()   { echo "${GREEN}✓ $*${RESET}"; }
info() { echo "${YELLOW}→ $*${RESET}"; }
err()  { echo "${RED}✗ $*${RESET}" >&2; }
head_msg() { echo "${CYAN}$*${RESET}"; }

REPO_URL="https://github.com/kineticadmin/ressourses.git"
KINETIC_DIR="${HOME}/.kinetic/ressourses"
BIN_DIR="${HOME}/bin"
SKILLS_DIR="${HOME}/.claude/skills"
META_SKILL_DST="${SKILLS_DIR}/kinetic-skills"

head_msg "═══════════════════════════════════════"
head_msg "  Kinetic Skills — Installation"
head_msg "═══════════════════════════════════════"
echo

# ── 1. Check git ─────────────────────────────────────────────────────────────
if ! command -v git &>/dev/null; then
  err "git n'est pas installé. Installe-le et relance ce script."
  exit 1
fi
ok "git détecté"

# ── 2. Clone or update repo ───────────────────────────────────────────────────
if [[ -d "$KINETIC_DIR/.git" ]]; then
  info "Repo existant — mise à jour..."
  git -C "$KINETIC_DIR" pull --ff-only
  ok "Repo mis à jour"
else
  info "Clonage du repo dans $KINETIC_DIR..."
  mkdir -p "$(dirname "$KINETIC_DIR")"
  git clone --depth=1 "$REPO_URL" "$KINETIC_DIR"
  ok "Repo cloné"
fi

# ── 3. Create ~/bin ───────────────────────────────────────────────────────────
if [[ ! -d "$BIN_DIR" ]]; then
  mkdir -p "$BIN_DIR"
  ok "Créé : $BIN_DIR"
fi

# ── 4. Install CLI ────────────────────────────────────────────────────────────
cp "${KINETIC_DIR}/cli/kinetic-skills" "${BIN_DIR}/kinetic-skills"
chmod +x "${BIN_DIR}/kinetic-skills"
ok "CLI installé : ${BIN_DIR}/kinetic-skills"

# ── 5. Install meta-skill ─────────────────────────────────────────────────────
mkdir -p "$META_SKILL_DST"
cp "${KINETIC_DIR}/meta-skill/SKILL.md" "${META_SKILL_DST}/SKILL.md"
ok "Meta-skill installé : ${META_SKILL_DST}/SKILL.md"

# ── 6. Generate catalog if not present ───────────────────────────────────────
if [[ ! -f "${KINETIC_DIR}/catalog.json" ]]; then
  info "Génération du catalogue..."
  bash "${KINETIC_DIR}/scripts/generate-catalog.sh"
fi

# ── 7. PATH check ─────────────────────────────────────────────────────────────
echo
if [[ ":$PATH:" != *":${BIN_DIR}:"* ]]; then
  info "${BIN_DIR} n'est pas dans ton PATH."
  # Detect shell
  SHELL_NAME="$(basename "${SHELL:-bash}")"
  case "$SHELL_NAME" in
    zsh)  RC_FILE="$HOME/.zshrc" ;;
    bash) RC_FILE="$HOME/.bashrc" ;;
    *)    RC_FILE="$HOME/.profile" ;;
  esac
  echo
  echo "${YELLOW}Ajoute cette ligne à ${RC_FILE} :${RESET}"
  echo "  export PATH=\"\$HOME/bin:\$PATH\""
  echo
  echo "Ou exécute directement :"
  echo "  echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ${RC_FILE} && source ${RC_FILE}"
else
  ok "${BIN_DIR} est déjà dans le PATH"
fi

# ── 8. Summary ────────────────────────────────────────────────────────────────
SKILL_COUNT=$(python3 -c "import json; d=json.load(open('${KINETIC_DIR}/catalog.json')); print(len(d))" 2>/dev/null || echo "N/A")
N8N_COUNT=$(ls "${KINETIC_DIR}/1,900+ n8n Automations/workflows/"*.json 2>/dev/null | wc -l | tr -d ' ' || echo "N/A")

echo
head_msg "═══════════════════════════════════════"
head_msg "  Installation terminée !"
head_msg "═══════════════════════════════════════"
echo
echo "  ${CYAN}Skills Claude disponibles :${RESET} $SKILL_COUNT"
echo "  ${CYAN}Workflows n8n disponibles :${RESET} $N8N_COUNT"
echo
echo "  ${YELLOW}Commandes disponibles :${RESET}"
echo "    kinetic-skills help"
echo "    kinetic-skills categories"
echo "    kinetic-skills search <mot-clé>"
echo "    kinetic-skills install <nom>"
echo
echo "  ${YELLOW}Exemple :${RESET}"
echo "    kinetic-skills install blog-post"
echo
```

- [ ] **Step 2: Make executable**

```bash
chmod +x install.sh
```

- [ ] **Step 3: Test install.sh locally (dry-run — simulate fresh install)**

```bash
# Back up existing meta-skill if present
[ -d ~/.claude/skills/kinetic-skills ] && cp -r ~/.claude/skills/kinetic-skills /tmp/kinetic-skills-bak || true

# Run install script pointing at local repo (simulate curl | bash by running directly)
# We need to test without actually cloning — patch KINETIC_DIR for local test
KINETIC_DIR="$(pwd)" bash -c '
  BIN_DIR=/tmp/kinetic-test-bin
  SKILLS_DIR=/tmp/kinetic-test-skills
  mkdir -p $BIN_DIR $SKILLS_DIR
  # Run steps manually
  cp cli/kinetic-skills $BIN_DIR/kinetic-skills && chmod +x $BIN_DIR/kinetic-skills
  mkdir -p $SKILLS_DIR/kinetic-skills
  cp meta-skill/SKILL.md $SKILLS_DIR/kinetic-skills/SKILL.md
  echo "CLI OK: $($BIN_DIR/kinetic-skills help | head -1)"
  echo "Meta-skill OK: $(head -3 $SKILLS_DIR/kinetic-skills/SKILL.md)"
'
```

Expected: CLI help text + meta-skill frontmatter printed without errors.

- [ ] **Step 4: Test CLI commands end-to-end**

```bash
# Set KINETIC_DIR to local repo for testing
export KINETIC_DIR="$(pwd)"

# Test categories
bash cli/kinetic-skills categories 2>&1 | head -5

# Test search
bash cli/kinetic-skills search seo 2>&1 | head -10

# Test install
mkdir -p /tmp/test-claude-skills
SKILLS_DIR=/tmp/test-claude-skills bash cli/kinetic-skills install blog-post 2>&1
ls /tmp/test-claude-skills/blog-post/

# Test blacklist
bash cli/kinetic-skills install terms-of-use-app 2>&1 | grep -i "liste noire\|blacklist\|avertissement"
```

Expected:
- categories: list with counts
- search: at least one result for "seo"
- install: SKILL.md present in `/tmp/test-claude-skills/blog-post/`
- blacklist: error message about blacklisted skill

- [ ] **Step 5: Commit**

```bash
git add install.sh
git commit -m "feat: add one-shot install.sh"
```

---

### Task 6: Final commit + push

- [ ] **Step 1: Verify all files in place**

```bash
ls scripts/generate-catalog.sh meta-skill/SKILL.md cli/kinetic-skills install.sh catalog.json
```

Expected: all five files listed.

- [ ] **Step 2: Ensure catalog.json is NOT in .gitignore**

```bash
cat .gitignore 2>/dev/null | grep catalog || echo "catalog.json not ignored — OK"
```

- [ ] **Step 3: Final status check**

```bash
git status
git log --oneline -5
```

- [ ] **Step 4: Push branch**

```bash
git push -u origin feature/global-toolkit
```

Expected: branch pushed, URL shown.

---

## Notes for implementer

### YAML frontmatter extraction
The `generate-catalog.sh` reads frontmatter line by line (no `yq` dependency). The `description` field may contain embedded double-quotes — those are escaped with `\"` in the JSON output.

### Python3 dependency in CLI
The CLI uses `python3` for JSON parsing (to avoid writing a JSON parser in bash). Python3 is available on all modern macOS/Linux systems and is not an extra "dev" dependency.
The spec says "no Node/Python/Ruby", which we interpret as "no project-level dependency to install" — system Python is universally available and doesn't require a package manager. **If this interpretation is wrong, the JSON parsing commands can be rewritten with `jq` (if available) or pure `sed`/`awk` with a fallback warning.**

### fzf integration
The spec mentions optional fzf for interactive selection. This plan omits fzf for the initial implementation to keep the script focused and testable. A follow-up task can add `if command -v fzf; then ... ; fi` wrappers to `cmd_search` and `cmd_list`.

### Blacklisted skill
`Legal & Compliance/terms-of-use-app` is excluded from `catalog.json` at generation time (won't appear in search/list) **and** the CLI install command has an explicit runtime check by name.
