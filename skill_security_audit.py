#!/usr/bin/env python3
"""
🔒 Audit Sécuritaire Automatisé des Claude Skills
===================================================
Script d'inspection de sécurité pour les fichiers SKILL.md.
Analyse en 3 couches :
  1. Détection de patterns suspects (prompt injection, exfiltration, etc.)
  2. Analyse du frontmatter YAML (permissions, cohérence)
  3. Vérification VirusTotal (optionnelle, par hash SHA-256)

Usage:
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle"
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle" --vt-key "YOUR_KEY"
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle" --scan-urls
"""

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
import urllib.error
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
from collections import defaultdict

# ─────────────────────────────────────────────
# CONFIGURATION : Patterns suspects par catégorie
# ─────────────────────────────────────────────

SUSPICIOUS_PATTERNS = {
    "🔴 Prompt Injection": {
        "severity": "CRITICAL",
        "patterns": [
            (r"ignore\s+(all\s+)?previous\s+instructions?", "Tentative d'ignorer les instructions précédentes"),
            (r"disregard\s+(all\s+)?(previous|above|prior)", "Tentative de contournement des instructions"),
            (r"forget\s+(your|all|previous)\s+instructions?", "Tentative de reset des instructions"),
            (r"you\s+are\s+now\s+(a|an)\s+", "Tentative de re-personnification de l'IA"),
            (r"act\s+as\s+if\s+you\s+(are|were)", "Tentative de changement de rôle"),
            (r"pretend\s+you\s+(are|have|can)", "Tentative de manipulation du comportement"),
            (r"do\s+not\s+follow\s+(any|your)", "Tentative de désactivation des règles"),
            (r"override\s+(your|all|system)", "Tentative d'override système"),
            (r"jailbreak", "Référence directe au jailbreak"),
            (r"DAN\s*mode", "Référence au mode DAN (Do Anything Now)"),
            (r"system\s*prompt", "Référence au prompt système"),
        ]
    },
    "🔴 Exfiltration de données": {
        "severity": "CRITICAL",
        "patterns": [
            (r"(?<!\w)curl\s+(-[a-zA-Z]+\s+)*https?://", "Commande curl vers URL externe"),
            (r"(?<!\w)wget\s+", "Commande wget détectée"),
            (r"fetch\s*\(", "Appel fetch() potentiel"),
            (r"XMLHttpRequest", "Requête HTTP via XMLHttpRequest"),
            (r"(?<!\w)eval\s*\(", "Appel eval() — exécution de code dynamique"),
            (r"(?<!\w)exec\s*\(", "Appel exec() — exécution de commande"),
            (r"subprocess\s*\.\s*(run|call|Popen)", "Exécution de processus système"),
            (r"os\s*\.\s*system\s*\(", "Appel os.system() — commande shell"),
            (r"import\s+requests", "Import de la lib requests"),
            (r"import\s+urllib", "Import de urllib"),
            (r"import\s+socket", "Import de socket"),
            (r"base64\s*\.\s*(encode|decode|b64encode|b64decode)", "Encodage/décodage Base64"),
        ]
    },
    "🟡 Accès fichiers suspects": {
        "severity": "WARNING",
        "patterns": [
            (r"~/\.ssh", "Accès au répertoire SSH"),
            (r"~/\.env", "Accès au fichier .env"),
            (r"/etc/passwd", "Accès à /etc/passwd"),
            (r"/etc/shadow", "Accès à /etc/shadow"),
            (r"~/\.aws", "Accès aux credentials AWS"),
            (r"~/\.kube", "Accès à la config Kubernetes"),
            (r"~/\.docker", "Accès à la config Docker"),
            (r"(?<!\w)(API_KEY|SECRET_KEY|PRIVATE_KEY|ACCESS_TOKEN)\s*[=:]", "Variable de secret définie"),
            (r"(?<!\w)credentials?\s*[=:\[]", "Accès à des credentials"),
            (r"(?<!\w)password\s*[=:]", "Mot de passe défini en clair"),
        ]
    },
    "🟡 Élévation de privilèges": {
        "severity": "WARNING",
        "patterns": [
            (r"(?<!\w)sudo\s+", "Commande sudo"),
            (r"chmod\s+777", "Permissions ouvertes à tous (777)"),
            (r"chmod\s+\+s", "SetUID/SetGID bit"),
            (r"rm\s+-rf\s+/", "Suppression récursive depuis la racine"),
            (r"rm\s+-rf\s+~/", "Suppression récursive du home"),
            (r"allowed-tools:\s*\*", "Wildcard dans allowed-tools (accès total)"),
            (r"allowed-tools:.*(?:Bash|Terminal|Shell|Execute)", "Accès terminal dans allowed-tools"),
        ]
    },
    "🟡 Obfuscation": {
        "severity": "WARNING",
        "patterns": [
            (r"(?:\\x[0-9a-fA-F]{2}){10,}", "Longue chaîne hexadécimale (possible obfuscation)"),
            (r"\\u200[b-f]", "Caractères Unicode zero-width (invisibles)"),
            (r"\\u00ad", "Soft hyphen Unicode (caractère invisible)"),
            (r"\\ufeff", "BOM Unicode (possible obfuscation)"),
            (r"[A-Za-z0-9+/]{100,}={0,2}", "Très longue chaîne Base64 potentielle"),
            (r"data:\s*text/html\s*;\s*base64", "Data URI Base64 en HTML"),
        ]
    },
    "🔵 URLs externes": {
        "severity": "INFO",
        "patterns": [
            (r"https?://(?!(?:claude\.ai|anthropic\.com|docs\.|github\.com|www\.virustotal\.com|en\.wikipedia\.org|jsonapi\.org))[^\s\)\"'>\]]+", "URL externe (non-standard)"),
        ]
    },
}

# Champs YAML attendus dans le frontmatter
EXPECTED_YAML_FIELDS = {"name", "description", "allowed-tools", "metadata"}
SAFE_ALLOWED_TOOLS = {"Read", "Write", "Glob", "Grep", "LS", "View"}

# ─────────────────────────────────────────────
# FONCTIONS UTILITAIRES
# ─────────────────────────────────────────────

def compute_sha256(filepath: str) -> str:
    """Calcule le hash SHA-256 d'un fichier."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def parse_yaml_frontmatter(content: str) -> Optional[dict]:
    """Parse le frontmatter YAML entre les --- délimiteurs."""
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None

    frontmatter = {}
    raw = match.group(1)
    current_key = None
    current_indent = 0

    for line in raw.split("\n"):
        # Simple key: value parsing
        kv_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if kv_match:
            key = kv_match.group(1)
            value = kv_match.group(2).strip().strip('"').strip("'")
            frontmatter[key] = value
            current_key = key
        elif current_key and line.strip().startswith("-"):
            # List item
            if not isinstance(frontmatter.get(current_key), list):
                frontmatter[current_key] = []
            frontmatter[current_key].append(line.strip().lstrip("- "))
        elif current_key and line.startswith("  "):
            # Nested value
            nested_match = re.match(r"\s+(\w[\w-]*):\s*(.*)", line)
            if nested_match:
                if not isinstance(frontmatter.get(current_key), dict):
                    frontmatter[current_key] = {}
                frontmatter[current_key][nested_match.group(1)] = nested_match.group(2).strip().strip('"').strip("'")

    return frontmatter


def analyze_frontmatter(frontmatter: Optional[dict], filepath: str) -> list:
    """Analyse le frontmatter YAML pour des anomalies."""
    findings = []

    if frontmatter is None:
        findings.append({
            "category": "🟡 Frontmatter YAML",
            "severity": "WARNING",
            "detail": "Pas de frontmatter YAML détecté",
            "line": 0,
        })
        return findings

    # Vérifier les champs inconnus
    known_fields = EXPECTED_YAML_FIELDS | {"metadata"}
    for key in frontmatter:
        if key not in known_fields and key not in {"author", "version", "tags", "category"}:
            findings.append({
                "category": "🟡 Frontmatter YAML",
                "severity": "WARNING",
                "detail": f"Champ YAML inhabituel : '{key}'",
                "line": 0,
            })

    # Vérifier allowed-tools
    if "allowed-tools" in frontmatter:
        tools_str = frontmatter["allowed-tools"]
        if isinstance(tools_str, str):
            tools = [t.strip() for t in tools_str.split()]
        elif isinstance(tools_str, list):
            tools = tools_str
        else:
            tools = []

        if "*" in tools or "all" in tools_str.lower() if isinstance(tools_str, str) else False:
            findings.append({
                "category": "🔴 Frontmatter YAML",
                "severity": "CRITICAL",
                "detail": "allowed-tools contient un wildcard (*) — accès illimité aux outils",
                "line": 0,
            })

        for tool in tools:
            if tool not in SAFE_ALLOWED_TOOLS:
                findings.append({
                    "category": "🟡 Frontmatter YAML",
                    "severity": "INFO",
                    "detail": f"Outil non-standard dans allowed-tools : '{tool}'",
                    "line": 0,
                })

    # Vérifier name manquant
    if "name" not in frontmatter:
        findings.append({
            "category": "🟡 Frontmatter YAML",
            "severity": "WARNING",
            "detail": "Champ 'name' manquant dans le frontmatter",
            "line": 0,
        })

    # Vérifier description manquante
    if "description" not in frontmatter:
        findings.append({
            "category": "🟡 Frontmatter YAML",
            "severity": "WARNING",
            "detail": "Champ 'description' manquant dans le frontmatter",
            "line": 0,
        })

    return findings


def scan_content_patterns(content: str, filepath: str) -> list:
    """Scanne le contenu pour des patterns suspects."""
    findings = []
    lines = content.split("\n")

    for category_name, category_data in SUSPICIOUS_PATTERNS.items():
        severity = category_data["severity"]
        for pattern, description in category_data["patterns"]:
            for line_num, line in enumerate(lines, 1):
                # Skip YAML frontmatter lines for some patterns
                if line.strip().startswith("#") and "Prompt Injection" not in category_name:
                    continue

                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Filtrer les faux positifs dans les blocs de code de documentation
                    context = line.strip()
                    findings.append({
                        "category": category_name,
                        "severity": severity,
                        "detail": f"{description} → `{match.group()[:80]}`",
                        "line": line_num,
                        "context": context[:120],
                    })

    return findings


def check_invisible_chars(content: str) -> list:
    """Détecte les caractères Unicode invisibles."""
    findings = []
    invisible_chars = {
        '\u200b': 'Zero-width space',
        '\u200c': 'Zero-width non-joiner',
        '\u200d': 'Zero-width joiner',
        '\u200e': 'Left-to-right mark',
        '\u200f': 'Right-to-left mark',
        '\u00ad': 'Soft hyphen',
        '\ufeff': 'BOM / Zero-width no-break space',
        '\u2060': 'Word joiner',
        '\u2061': 'Function application',
        '\u2062': 'Invisible times',
        '\u2063': 'Invisible separator',
        '\u2064': 'Invisible plus',
    }

    for line_num, line in enumerate(content.split("\n"), 1):
        for char, name in invisible_chars.items():
            if char in line:
                count = line.count(char)
                findings.append({
                    "category": "🔴 Obfuscation",
                    "severity": "CRITICAL",
                    "detail": f"Caractère invisible détecté : {name} (U+{ord(char):04X}) × {count}",
                    "line": line_num,
                    "context": repr(line[:80]),
                })

    return findings


# ─────────────────────────────────────────────
# VIRUSTOTAL API
# ─────────────────────────────────────────────

class VirusTotalClient:
    """Client simple pour l'API VirusTotal v3."""

    BASE_URL = "https://www.virustotal.com/api/v3"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.request_count = 0
        self.last_request_time = 0

    def _rate_limit(self):
        """Respecte la limite de 4 req/min pour l'API gratuite."""
        now = time.time()
        if self.request_count >= 4:
            elapsed = now - self.last_request_time
            if elapsed < 60:
                wait = 60 - elapsed + 1
                print(f"    ⏳ Rate limit — attente de {wait:.0f}s...")
                time.sleep(wait)
            self.request_count = 0
        self.last_request_time = time.time()
        self.request_count += 1

    def check_hash(self, file_hash: str) -> Optional[dict]:
        """Vérifie un hash SHA-256 sur VirusTotal."""
        self._rate_limit()
        url = f"{self.BASE_URL}/files/{file_hash}"
        req = urllib.request.Request(url, headers={"x-apikey": self.api_key})

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None  # File not found in VT
            raise
        except Exception as e:
            print(f"    ⚠ Erreur VT : {e}")
            return None

    def scan_url(self, target_url: str) -> Optional[dict]:
        """Soumet une URL pour analyse."""
        self._rate_limit()
        url = f"{self.BASE_URL}/urls"
        data = urllib.parse.urlencode({"url": target_url}).encode()
        req = urllib.request.Request(url, data=data, headers={"x-apikey": self.api_key})

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            print(f"    ⚠ Erreur VT URL scan : {e}")
            return None


# ─────────────────────────────────────────────
# MOTEUR D'AUDIT PRINCIPAL
# ─────────────────────────────────────────────

class SkillSecurityAuditor:
    """Moteur principal d'audit sécuritaire des skills."""

    def __init__(self, skills_dir: str, vt_key: Optional[str] = None, scan_urls: bool = False):
        self.skills_dir = Path(skills_dir)
        self.vt_client = VirusTotalClient(vt_key) if vt_key else None
        self.scan_urls = scan_urls
        self.results = {}
        self.stats = defaultdict(int)

    def find_skill_files(self) -> List[Path]:
        """Trouve tous les fichiers SKILL.md récursivement."""
        return sorted(self.skills_dir.rglob("SKILL.md"))

    def audit_skill(self, filepath: Path) -> dict:
        """Audite un seul fichier SKILL.md."""
        rel_path = filepath.relative_to(self.skills_dir)
        result = {
            "path": str(rel_path),
            "findings": [],
            "sha256": "",
            "vt_status": "non vérifié",
            "risk_level": "🟢 Clean",
        }

        try:
            content = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            result["findings"].append({
                "category": "🔴 Erreur",
                "severity": "CRITICAL",
                "detail": f"Impossible de lire le fichier : {e}",
                "line": 0,
            })
            result["risk_level"] = "🔴 Erreur"
            return result

        # Hash SHA-256
        result["sha256"] = compute_sha256(str(filepath))

        # Couche 1 : Patterns suspects
        result["findings"].extend(scan_content_patterns(content, str(filepath)))

        # Couche 1b : Caractères invisibles
        result["findings"].extend(check_invisible_chars(content))

        # Couche 2 : Frontmatter YAML
        frontmatter = parse_yaml_frontmatter(content)
        result["findings"].extend(analyze_frontmatter(frontmatter, str(filepath)))

        # Couche 3 : VirusTotal (optionnel)
        if self.vt_client:
            vt_result = self.vt_client.check_hash(result["sha256"])
            if vt_result:
                stats = vt_result.get("data", {}).get("attributes", {}).get("last_analysis_stats", {})
                malicious = stats.get("malicious", 0)
                suspicious = stats.get("suspicious", 0)
                result["vt_status"] = f"malicious={malicious}, suspicious={suspicious}"
                if malicious > 0 or suspicious > 0:
                    result["findings"].append({
                        "category": "🔴 VirusTotal",
                        "severity": "CRITICAL",
                        "detail": f"Détecté par VirusTotal : {malicious} malicious, {suspicious} suspicious",
                        "line": 0,
                    })
            else:
                result["vt_status"] = "inconnu de VT"

        # Déterminer le niveau de risque global
        severities = [f["severity"] for f in result["findings"]]
        if "CRITICAL" in severities:
            result["risk_level"] = "🔴 Critique"
        elif "WARNING" in severities:
            result["risk_level"] = "🟡 Suspect"
        elif "INFO" in severities:
            result["risk_level"] = "🔵 Info"
        else:
            result["risk_level"] = "🟢 Clean"

        return result

    def run_audit(self) -> dict:
        """Exécute l'audit complet."""
        skill_files = self.find_skill_files()
        total = len(skill_files)

        print(f"\n🔒 Audit Sécuritaire des Claude Skills")
        print(f"{'=' * 50}")
        print(f"📁 Répertoire : {self.skills_dir}")
        print(f"📄 Skills trouvées : {total}")
        print(f"🔑 VirusTotal : {'activé' if self.vt_client else 'désactivé'}")
        print(f"🔗 Scan URLs : {'oui' if self.scan_urls else 'non'}")
        print(f"{'=' * 50}\n")

        for i, filepath in enumerate(skill_files, 1):
            rel = filepath.relative_to(self.skills_dir)
            category = str(rel).split(os.sep)[0] if os.sep in str(rel) else "root"
            skill_name = str(rel)

            # Indicateur de progression
            bar_len = 30
            filled = int(bar_len * i / total)
            bar = "█" * filled + "░" * (bar_len - filled)
            print(f"\r  [{bar}] {i}/{total} — {skill_name[:50]}", end="", flush=True)

            result = self.audit_skill(filepath)
            self.results[skill_name] = result

            # Stats
            self.stats[result["risk_level"]] += 1
            if result["findings"]:
                self.stats["with_findings"] += 1

        print(f"\n\n{'=' * 50}")
        print(f"✅ Audit terminé !")
        print(f"{'=' * 50}")

        return self.results

    def generate_report(self, output_path: str) -> str:
        """Génère le rapport Markdown."""
        lines = []
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # En-tête
        lines.append("# 🔒 Rapport d'Audit Sécuritaire — Claude Skills")
        lines.append(f"\n**Date** : {now}")
        lines.append(f"**Répertoire** : `{self.skills_dir}`")
        lines.append(f"**VirusTotal** : {'✅ Activé' if self.vt_client else '❌ Désactivé (analyse locale uniquement)'}")
        lines.append("")

        # Résumé global
        total = len(self.results)
        critical = self.stats.get("🔴 Critique", 0)
        suspect = self.stats.get("🟡 Suspect", 0)
        info = self.stats.get("🔵 Info", 0)
        clean = self.stats.get("🟢 Clean", 0)

        lines.append("---")
        lines.append("")
        lines.append("## 📊 Résumé Global")
        lines.append("")
        lines.append(f"| Métrique | Valeur |")
        lines.append(f"|----------|--------|")
        lines.append(f"| **Skills scannées** | {total} |")
        lines.append(f"| 🔴 Critique | {critical} |")
        lines.append(f"| 🟡 Suspect | {suspect} |")
        lines.append(f"| 🔵 Info | {info} |")
        lines.append(f"| 🟢 Clean | {clean} |")
        lines.append("")

        if critical > 0:
            lines.append("> [!CAUTION]")
            lines.append(f"> **{critical} skill(s) avec des findings critiques détectés !** Examiner en priorité.")
            lines.append("")
        elif suspect > 0:
            lines.append("> [!WARNING]")
            lines.append(f"> **{suspect} skill(s) avec des findings suspects.** Revue recommandée.")
            lines.append("")
        else:
            lines.append("> [!TIP]")
            lines.append("> **Aucun finding critique ou suspect.** Le bundle semble sûr. ✅")
            lines.append("")

        # Détails par catégorie de risque
        lines.append("---")
        lines.append("")
        lines.append("## 🔍 Détails par Skill")
        lines.append("")

        # D'abord les critiques, puis suspects, puis info, puis clean
        sorted_results = sorted(
            self.results.items(),
            key=lambda x: (
                0 if x[1]["risk_level"].startswith("🔴") else
                1 if x[1]["risk_level"].startswith("🟡") else
                2 if x[1]["risk_level"].startswith("🔵") else 3
            )
        )

        current_level = None
        for skill_path, result in sorted_results:
            if result["risk_level"] != current_level:
                current_level = result["risk_level"]
                lines.append(f"### {current_level}")
                lines.append("")

            if result["findings"]:
                lines.append(f"#### `{skill_path}`")
                lines.append(f"- **SHA-256** : `{result['sha256'][:16]}...`")
                lines.append(f"- **VT** : {result['vt_status']}")
                lines.append("")
                lines.append("| Ligne | Catégorie | Sévérité | Détail |")
                lines.append("|-------|-----------|----------|--------|")
                for f in result["findings"]:
                    detail = f["detail"].replace("|", "\\|")[:100]
                    lines.append(f"| {f['line']} | {f['category']} | {f['severity']} | {detail} |")
                lines.append("")
            else:
                lines.append(f"- `{skill_path}` — ✅ Aucun finding")

        # Recommandations
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 💡 Recommandations")
        lines.append("")
        if critical > 0:
            lines.append("1. **Examiner les skills critiques** — Vérifier manuellement chaque finding 🔴 pour déterminer s'il s'agit d'un vrai risque ou d'un faux positif")
            lines.append("2. **Ne pas installer aveuglément** — Toute skill avec des findings critiques doit être revue avant utilisation")
        if suspect > 0:
            lines.append("3. **Revue des suspects** — Les findings 🟡 méritent une attention mais sont souvent des faux positifs (ex: `curl` mentionné dans de la documentation)")
        lines.append("4. **Auditer régulièrement** — Relancer ce script après chaque mise à jour du bundle")
        lines.append("5. **Principe de moindre privilège** — Préférer les skills avec des `allowed-tools` restreints")
        lines.append("")

        report_content = "\n".join(lines)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"\n📝 Rapport généré : {output_path}")
        return output_path


# ─────────────────────────────────────────────
# POINT D'ENTRÉE
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="🔒 Audit sécuritaire automatisé des Claude Skills",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples:
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle"
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle" --vt-key "YOUR_KEY"
  python3 skill_security_audit.py --dir "Claude Skills Ultimate Bundle" --scan-urls --vt-key "YOUR_KEY"
        """
    )
    parser.add_argument("--dir", required=True, help="Chemin vers le répertoire des skills")
    parser.add_argument("--vt-key", default=None, help="Clé API VirusTotal (optionnel)")
    parser.add_argument("--scan-urls", action="store_true", help="Scanner aussi les URLs trouvées dans les skills")
    parser.add_argument("--output", default=None, help="Chemin du rapport de sortie (défaut: skill_security_report.md)")
    parser.add_argument("--no-vt", action="store_true", help="Désactiver VirusTotal même si une clé est fournie")

    args = parser.parse_args()

    # Valider le répertoire
    skills_dir = Path(args.dir)
    if not skills_dir.exists():
        print(f"❌ Répertoire introuvable : {skills_dir}")
        sys.exit(1)

    # Chemin de sortie
    output_path = args.output or str(skills_dir.parent / "skill_security_report.md")

    # Clé VT
    vt_key = None if args.no_vt else args.vt_key

    # Lancer l'audit
    auditor = SkillSecurityAuditor(
        skills_dir=str(skills_dir),
        vt_key=vt_key,
        scan_urls=args.scan_urls,
    )

    auditor.run_audit()
    auditor.generate_report(output_path)

    # Résumé final
    print(f"\n📊 Résumé :")
    print(f"   🔴 Critique : {auditor.stats.get('🔴 Critique', 0)}")
    print(f"   🟡 Suspect  : {auditor.stats.get('🟡 Suspect', 0)}")
    print(f"   🔵 Info     : {auditor.stats.get('🔵 Info', 0)}")
    print(f"   🟢 Clean    : {auditor.stats.get('🟢 Clean', 0)}")


if __name__ == "__main__":
    main()
