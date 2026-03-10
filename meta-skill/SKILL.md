---
name: kinetic-skills
description: >
  Scan automatique du catalogue Kinetic (500+ skills Claude) et installation des skills
  pertinents. Utilise ce skill quand l'utilisateur demande de trouver, chercher ou
  installer un skill, ou invoque-le toi-même avant une mission si le contexte le justifie.
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

## Scan proactif (usage autonome)

Quand tu reçois une mission substantielle, sans que l'utilisateur t'ait demandé :

1. Lis `~/.kinetic/ressourses/catalog.json`
2. Cherche des correspondances avec la nature de la mission (mots-clés du nom + description)
3. Si tu trouves des correspondances pertinentes (score de pertinence élevé) :
   - Annonce : "Avant de commencer, j'ai trouvé X skill(s) utile(s) : [noms + descriptions courtes]"
   - Installe-les avec `kinetic-skills install <nom>`
   - Informe que tu vas les utiliser
4. Si aucune correspondance évidente, ne rien mentionner et passer à la mission

Ne pas faire ce scan pour : corrections rapides, questions, explications, modifications mineures.

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
