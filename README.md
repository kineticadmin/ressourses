# Kinetic Skills

Catalogue de 500+ skills Claude + 1 900 workflows n8n, avec un CLI bash et un meta-skill
qui s'intègrent globalement dans Claude Code.

## Installation (une seule commande)

```bash
curl -fsSL https://raw.githubusercontent.com/kineticadmin/ressourses/main/install.sh | bash
```

Ce que ça fait :
- Clone le repo dans `~/.kinetic/ressourses/`
- Installe le CLI `kinetic-skills` dans `~/bin/`
- Installe le meta-skill dans `~/.claude/skills/kinetic-skills/`
- Injecte les instructions de scan automatique dans `~/.claude/CLAUDE.md`

Si `~/bin` n'est pas dans ton PATH, ajoute cette ligne à `~/.zshrc` ou `~/.bashrc` :

```bash
export PATH="$HOME/bin:$PATH"
```

## Commandes CLI

```bash
kinetic-skills help                        # Aide
kinetic-skills categories                  # Liste les 20 catégories
kinetic-skills search "email marketing"    # Chercher un skill
kinetic-skills install email-sequence      # Installer un skill dans ~/.claude/skills/
kinetic-skills installed                   # Voir les skills installés
kinetic-skills update                      # Mettre à jour le repo et le meta-skill

kinetic-skills workflow search "chatbot"   # Chercher un workflow n8n
kinetic-skills workflow copy <nom>         # Copier le JSON dans le clipboard
```

## Usage avec Claude Code

Après installation, Claude vérifie automatiquement le catalogue avant chaque mission
et installe les skills pertinents sans que tu aies à le demander.

Tu peux aussi demander explicitement :

```
"trouve-moi un skill pour rédiger des propositions commerciales"
"installe le skill SEO audit"
"quels skills ont accès à Notion ?"
```

## Structure du repo

```
install.sh                          # Installer globalement
cli/kinetic-skills                  # CLI bash
meta-skill/SKILL.md                 # Meta-skill Claude (source)
catalog.json                        # Index de tous les skills (500+)
scripts/generate-catalog.sh         # Régénérer catalog.json
Claude Skills Ultimate Bundle/      # 500+ skills (20 catégories)
1,900+ n8n Automations/workflows/   # 1 900+ workflows n8n (JSON)
```

## Catégories disponibles

Content & Copywriting · Sales & Funnels · Operations & Systems ·
Email Marketing & Automation · HR & Team · Branding & Design · SEO & Search ·
E-commerce & Products · Social Media · Finance & Pricing · Courses & Education ·
Launch & Growth · Client & Consulting · Events & Speaking · Ads & Paid Media ·
Analytics & Data · Legal & Compliance · AI & Technology · Nonprofit & Community · Industry-Specific

## Mise à jour

```bash
kinetic-skills update
```

## Contraintes

- Bash pur, aucune dépendance (hors git + curl)
- `fzf` utilisé si disponible, sinon liste numérotée
- Le skill `Legal & Compliance/terms-of-use-app` est blacklisté (injection de prompt détectée)
