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
