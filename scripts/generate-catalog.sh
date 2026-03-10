#!/usr/bin/env bash
# generate-catalog.sh — scans Claude Skills Ultimate Bundle/ and emits catalog.json

set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BUNDLE_DIR="$REPO_DIR/Claude Skills Ultimate Bundle"
OUTPUT="$REPO_DIR/catalog.json"

if [[ ! -d "$BUNDLE_DIR" ]]; then
  echo "Error: Bundle directory not found: $BUNDLE_DIR" >&2
  exit 1
fi

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

# Extract a YAML scalar value from the frontmatter block
extract_yaml() {
  local fm="$1"
  local key="$2"
  echo "$fm" | grep -m1 "^${key}:" | sed 's/^[^:]*:[[:space:]]*//' | sed 's/^"//' | sed 's/"$//' | tr -d '\r' || true
}

echo "Scanning skills in: $BUNDLE_DIR"

first=1
printf '[\n' > "$OUTPUT"

while IFS= read -r -d '' skill_file; do
  skill_dir="$(dirname "$skill_file")"
  rel_dir="${skill_dir#$BUNDLE_DIR/}"
  category="${rel_dir%%/*}"
  skill_name="${rel_dir##*/}"

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

  # Escape name and category for JSON
  name_escaped="${name//\\/\\\\}"
  name_escaped="${name_escaped//\"/\\\"}"
  category_escaped="${category//\\/\\\\}"
  category_escaped="${category_escaped//\"/\\\"}"

  # Skip skills with no name
  if [[ -z "$name_escaped" ]]; then
    echo "  [WARN] missing name in $rel_dir — skipping"
    continue
  fi

  # Build JSON array for allowedTools
  tools_json="["
  first_tool=1
  for tool in $allowed_tools_raw; do
    tool_escaped="${tool//\\/\\\\}"
    tool_escaped="${tool_escaped//\"/\\\"}"
    if [[ $first_tool -eq 0 ]]; then tools_json+=", "; fi
    tools_json+="\"$tool_escaped\""
    first_tool=0
  done
  tools_json+="]"

  # Escape description for JSON
  description_escaped="${description//\\/\\\\}"
  description_escaped="${description_escaped//\"/\\\"}"
  description_escaped="${description_escaped//$'\n'/ }"

  rel_path="Claude Skills Ultimate Bundle/$rel_dir/SKILL.md"

  if [[ $first -eq 0 ]]; then printf ',\n' >> "$OUTPUT"; fi
  printf '  {\n    "name": "%s",\n    "category": "%s",\n    "description": "%s",\n    "path": "%s",\n    "allowedTools": %s\n  }' \
    "$name_escaped" "$category_escaped" "$description_escaped" "$rel_path" "$tools_json" >> "$OUTPUT"
  first=0

done < <(find "$BUNDLE_DIR" -name "SKILL.md" -print0 | sort -z)

printf '\n]\n' >> "$OUTPUT"

count=$(grep -c '"name":' "$OUTPUT" || true)
echo "Done. $count skills written to $OUTPUT"
