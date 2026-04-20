# AUTOHACK LAB COMMANDER

README orienté mainteneur.  
Ce document décrit l’architecture, les conventions de données, le cycle d’exécution et les points d’extension du projet.

Version actuelle : `2.0.0`

## Objectif

AUTOHACK est une application terminale Python qui centralise un catalogue de commandes shell et fournit deux surfaces :

- une TUI `Rich` pour naviguer, filtrer, documenter et lancer les commandes
- une CLI non interactive pour la recherche, l’export, les statistiques et l’exécution ciblée par ID

Le catalogue contient actuellement **212 commandes** réparties dans **12 catégories**.

## Stack et prérequis

- Python `3.10+`
- Linux recommandé
- dépendances Python installées via `requirements.txt`
- `xclip` optionnel pour la copie presse-papiers

Installation :

```bash
python3 -m pip install -r requirements.txt
```

## Points d’entrée

### TUI

```bash
python3 main.py
```

Le menu principal instancie `menus.main_menu.MainMenu`, qui crée les services cœur puis délègue aux sous-menus spécialisés.

### CLI

```bash
python3 main.py --help
```

Options actuellement exposées :

- `--run CMD_ID`
- `--dry-run CMD_ID`
- `--search KEYWORD`
- `--category CAT`
- `--list-categories`
- `--list-ids`
- `--export {md,txt,json,html}`
- `--check`
- `--stats`
- `--favorites`
- `--generate-completion {bash,zsh}`
- `--version`

## Architecture

### Vue d’ensemble

Le code est organisé en trois couches :

1. `main.py`
   Point d’entrée unique. Construit l’argument parser, route le mode CLI et démarre la TUI.

2. `core/`
   Services métier transverses : chargement du catalogue, exécution, configuration, thèmes, historique, favoris, logs, exports.

3. `menus/`
   Couche présentation TUI. Chaque menu correspond soit à une catégorie, soit à une fonction transverse.

### Arbre logique

```text
main.py
├── CLI helpers
└── MainMenu
    ├── CommandCatalog
    ├── CommandExecutor
    ├── ToolChecker
    ├── ConfigManager
    ├── SessionHistory
    └── Favorites
```

Les objets cœur sont partagés entre les menus, ce qui évite de dupliquer l’état utilisateur.

## Modules principaux

### `core/catalog.py`

Responsabilités :

- charger `commands_catalog.json`
- aplatir les commandes avec injection du champ `category`
- valider un sous-ensemble minimal du schéma
- offrir les primitives de recherche et de résolution de catégorie

Détails utiles :

- `REQUIRED_FIELDS = ("id", "name", "command", "risks", "safe_to_run")`
- la recherche normalise les accents et la casse via `unicodedata.normalize("NFKD", ...)`
- la recherche applique une logique `AND`
- score actuel :
  - `+10` si match sur `id`
  - `+8` si match sur `name` ou `short_name`
  - `+5` si match sur `tags`
  - `+2` si match sur `description` ou `purpose`
- `validate()` remonte aussi les IDs dupliqués et la contradiction `dangerous=true` + `safe_to_run=true`

### `core/executor.py`

Responsabilités :

- résoudre les placeholders shell comme `$TARGET`, `$PORT`, `$USER`
- afficher les avertissements pédagogiques
- appliquer la politique d’exécution
- lancer la commande, faire un dry-run, copier, capturer la sortie
- afficher un résumé d’exécution

Politique actuelle :

- `normal` : autorisé
- `safe` : autorisé
- `dry_run_only` : autorisé dans l’état actuel du projet
- `lab_only` : bloqué

Règle de fallback :

- si `execution_policy` est absente et `dangerous=true`, la commande est traitée comme `lab_only`
- sinon la commande est traitée comme `normal`

Points de vigilance :

- `_run_args()` choisit `shell=True` uniquement si la chaîne contient des opérateurs shell connus
- les placeholders sont persistés en cache mémoire de session dans `self._var_cache`
- les actions d’exécution sont journalisées via `core.logger.ActionLogger`

### `core/checker.py`

Responsabilités :

- vérifier si l’outil requis par une commande est installé
- fournir des badges de disponibilité et des hints d’installation

Cette couche est utilisée dans la TUI, la CLI catégorie et les vues de diagnostics.

### `core/config_manager.py`

Responsabilités :

- charger et persister `~/.autohack.json`
- fusionner avec les valeurs par défaut
- valider les valeurs mutables

Clés supportées :

| Clé | Défaut |
|---|---|
| `export_format` | `markdown` |
| `page_size` | `10` |
| `log_level` | `INFO` |
| `export_dir` | `null` |
| `confirm_safe_commands` | `true` |
| `show_history_in_menu` | `true` |
| `history_size` | `10` |

### `core/session_history.py`

Responsabilités :

- conserver l’historique local des exécutions
- persister les dernières entrées dans `~/.autohack_history.json`

Champs persistés :

- `id`
- `name`
- `command`
- `category`
- `exit_code`
- `dry_run`
- `timestamp`

### `core/favorites.py`

Responsabilités :

- gérer une liste ordonnée d’IDs favoris
- persister dans `~/.autohack_favorites.json`

### `core/exporter.py`

Responsabilités :

- exporter tout le catalogue en `txt`, `markdown`, `json`, `html`

Répertoire par défaut :

- `exports/`

### `core/theme.py`

Responsabilités :

- centraliser les composants visuels `Rich`
- exposer les helpers de layout réutilisés par les menus

Le projet a progressivement déplacé le style ici pour éviter les variations de rendu entre écrans.

## Couche TUI

### `menus/base.py`

`BaseMenu` est la pièce centrale de la navigation TUI.

Responsabilités :

- afficher les en-têtes de page
- gérer la palette globale
- construire les tableaux de commandes
- afficher les panneaux d’aperçu et les fiches commande
- piloter la boucle de navigation des listes
- piloter la boucle d’actions d’une fiche commande

Méthodes importantes :

- `run_loop(category, title)`
- `run_commands_loop(all_commands, title, ...)`
- `_build_commands_table(...)`
- `_build_command_preview_panel(...)`
- `_show_command_card(cmd)`
- `_action_loop(cmd)`

`run_commands_loop()` est le bon point d’entrée pour introduire de nouvelles vues transverses sur un sous-ensemble de commandes sans créer un menu dédié.

### `menus/main_menu.py`

Responsabilités :

- construire les services cœur
- câbler les sous-menus
- rendre le dashboard principal
- gérer certains raccourcis de niveau racine

Le rendu du menu principal a été volontairement simplifié récemment.  
Si vous rajoutez des panneaux, gardez en tête que l’utilisateur a explicitement demandé de retirer plusieurs blocs visuels du dashboard.

### Menus de catégorie

Menus existants :

- `environment.py`
- `dependencies.py`
- `network.py`
- `tor.py`
- `privoxy.py`
- `scrapy_menu.py`
- `json_export.py`
- `elastic.py`
- `diagnostic.py`
- `recon.py`
- `web_attack.py`
- `passwords.py`
- `post_exploit.py`

La plupart délèguent à `BaseMenu.run_loop()` avec un `CATEGORY` et un `TITLE`.

### Menus transverses

- `search.py`
- `favorites_menu.py`
- `config_menu.py`
- `run_all_checks.py`
- `export_all.py`
- `help_menu.py`

## Catalogue JSON

Le fichier source est `commands_catalog.json`.

Structure générale :

```json
{
  "categories": {
    "system": {
      "label": "...",
      "commands": [
        {
          "id": "sys_001",
          "name": "...",
          "command": "...",
          "safe_to_run": true,
          "risks": "..."
        }
      ]
    }
  }
}
```

### Champs requis

Le chargeur exige actuellement :

- `id`
- `name`
- `command`
- `risks`
- `safe_to_run`

### Champs courants

- `short_name`
- `description`
- `purpose`
- `expected_output`
- `prerequisites`
- `tool_required`
- `dangerous`
- `requires_sudo`
- `tags`
- `execution_policy`

### Conventions implicites

- l’ID embarque souvent la catégorie, par exemple `sys_001`, `tor_003`, `rec_018`
- le champ `category` est injecté à l’exécution par `CommandCatalog.load()`
- `tags` est utilisé à la fois pour la recherche et certaines vues transverses
- `tool_required=""` ou absent signifie qu’aucune vérification binaire n’est nécessaire

### Exemple de commande

```json
{
  "id": "sys_999",
  "name": "Exemple",
  "short_name": "echo test",
  "description": "Description courte",
  "command": "echo test",
  "purpose": "Explique l'objectif",
  "expected_output": "test",
  "risks": "Faible",
  "prerequisites": [],
  "tool_required": "",
  "safe_to_run": true,
  "dangerous": false,
  "requires_sudo": false,
  "tags": ["demo"]
}
```

## Flux d’exécution

### CLI `--run`

1. `main.py` résout l’ID via `CommandCatalog`
2. `CommandExecutor.confirm_and_run()` résout les placeholders
3. la politique d’exécution est appliquée
4. l’avertissement pédagogique est affiché
5. la confirmation utilisateur est demandée
6. la commande est exécutée

### TUI

1. `MainMenu` construit les services cœur
2. un sous-menu affiche une liste via `BaseMenu.run_loop()`
3. l’utilisateur ouvre une fiche commande
4. `_action_loop()` déclenche l’action choisie
5. l’historique et les favoris sont mis à jour si nécessaire

## Catégories actuelles

| Catégorie | ID | Commandes |
|---|---|---:|
| Système / Environnement | `system` | 32 |
| Réseau Local de Lab | `network` | 18 |
| Tor | `tor` | 15 |
| Privoxy | `privoxy` | 10 |
| Scrapy | `scrapy` | 15 |
| JSON / Export | `json_export` | 10 |
| Elastic / Logs | `elastic` | 13 |
| Diagnostic / Debug | `diagnostic` | 18 |
| Reconnaissance & Scan | `recon` | 22 |
| Attaque Web | `web_attack` | 20 |
| Cracking / Brute-force | `passwords` | 16 |
| Post-Exploitation | `post_exploit` | 23 |

## Configuration et chemins

### Répertoires projet

- `config/settings.py` définit les chemins racine
- `logs/` est créé au démarrage du module de settings
- `exports/` est créé au démarrage du module de settings

### Fichiers utilisateur

- `~/.autohack.json`
- `~/.autohack_history.json`
- `~/.autohack_favorites.json`

## Complétion shell

La génération est gérée depuis `main.py`.

Exemples :

```bash
python3 main.py --generate-completion bash
python3 main.py --generate-completion zsh
```

La complétion est générée dynamiquement depuis :

- les IDs du catalogue
- la liste des catégories
- les flags CLI

## Tests

Suite actuelle : **139 tests**.

Répartition implicite :

- tests unitaires pour les helpers UI et cœur
- tests du catalogue et de la CLI
- tests de l’exécuteur

Commandes utiles :

```bash
pytest -q
pytest tests/test_cli.py -q
pytest tests/test_executor.py -q
pytest tests/test_main_menu.py -q
```

## Contribuer proprement

### Ajouter une commande

1. modifier `commands_catalog.json`
2. vérifier la cohérence des champs
3. ajouter ou ajuster les tests CLI si la commande doit être trouvable par recherche
4. exécuter `pytest -q`

### Ajouter une catégorie

Changements minimum :

1. ajouter la catégorie dans `commands_catalog.json`
2. ajouter son label et son icône dans `config/settings.py`
3. créer le menu dédié dans `menus/` ou réutiliser `BaseMenu`
4. brancher le menu dans `menus/main_menu.py`
5. compléter les tests CLI et éventuellement la doc

### Ajouter une vue transverse

Le meilleur point d’entrée est généralement :

- `BaseMenu.run_commands_loop()` pour le rendu
- un filtre de commandes dans `menus/main_menu.py` ou un menu dédié

Éviter de recopier la logique de navigation de `BaseMenu`.

### Modifier la politique d’exécution

Centraliser les changements dans `core/executor.py`.

À ne pas disperser :

- les règles de blocage
- les confirmations
- la résolution des placeholders
- le résumé d’exécution

## Points de dette technique connus

- le schéma JSON n’est pas formalisé par `jsonschema` ou `pydantic`
- la politique `dry_run_only` est autorisée à l’exécution dans l’état actuel, ce qui mérite une clarification produit si le comportement doit évoluer
- `main.py` contient encore beaucoup de logique CLI en ligne au lieu d’un module dédié
- certains éléments du dashboard principal ont été ajoutés puis retirés selon feedback utilisateur ; garder cette zone sobre

## Fichiers à lire en premier

Pour prendre en main le projet rapidement :

1. [main.py](main.py:1)
2. [core/catalog.py](core/catalog.py:1)
3. [core/executor.py](core/executor.py:1)
4. [menus/base.py](menus/base.py:1)
5. [menus/main_menu.py](menus/main_menu.py:1)
6. [commands_catalog.json](commands_catalog.json:1)
