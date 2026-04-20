# Design Spec — AUTOHACK LAB COMMANDER
**Date:** 2026-04-19  
**Statut:** Approuvé

---

## Objectif

Application CLI Python pour centraliser et automatiser des commandes de lab autour de : environnement système, Tor, Privoxy, Scrapy, Elastic/logs, réseau local, diagnostic. Interface terminal `rich` avec navigation hybride numéro+lettre.

---

## Stack

- Python 3.10+
- `rich` — UI terminal (panels, tables, prompts, syntax highlight)
- `subprocess` — exécution des commandes shell
- `shutil.which` — détection des outils installés
- `pyperclip` — copie dans le presse-papiers
- Pas de base de données externe — catalogue JSON pur

---

## Arborescence

```
autohack/
├── main.py
├── requirements.txt
├── README.md
├── commands_catalog.json
├── config/
│   ├── __init__.py
│   └── settings.py
├── core/
│   ├── __init__.py
│   ├── catalog.py
│   ├── executor.py
│   ├── logger.py
│   ├── exporter.py
│   └── checker.py
├── menus/
│   ├── __init__.py
│   ├── base.py
│   ├── main_menu.py
│   ├── environment.py
│   ├── dependencies.py
│   ├── network.py
│   ├── tor.py
│   ├── privoxy.py
│   ├── scrapy_menu.py
│   ├── json_export.py
│   ├── elastic.py
│   ├── diagnostic.py
│   ├── help_menu.py
│   ├── export_all.py
│   └── search.py
├── exports/
└── logs/
    └── autohack.log
```

---

## Modèle de données — entrée catalogue

```json
{
  "id": "sys_001",
  "name": "Version Python",
  "short_name": "python3 --version",
  "description": "Affiche la version Python 3 installée",
  "command": "python3 --version",
  "purpose": "Vérifier que Python 3 est installé et connaître sa version",
  "expected_output": "Python 3.x.x",
  "risks": "Aucun — lecture seule",
  "prerequisites": ["python3 installé"],
  "tool_required": "python3",
  "safe_to_run": true,
  "dangerous": false,
  "requires_sudo": false,
  "category": "system",
  "tags": ["python", "version", "check"],
  "dry_run_command": null
}
```

**Catégories du catalogue :** `system`, `network`, `tor`, `privoxy`, `scrapy`, `json_export`, `elastic`, `diagnostic`

---

## Flux de navigation

```
main_menu [1-12 + q]
  └─ sous-menu catégorie [1-N + b]
       └─ fiche commande
            ├─ [r] run (avec confirmation pédagogique)
            ├─ [d] dry-run (affiche la commande sans exécuter)
            ├─ [e] explain (purpose + expected_output)
            ├─ [c] copy (presse-papiers via pyperclip)
            ├─ [p] prérequis
            └─ [b] retour au sous-menu
```

---

## Composants core

### `catalog.py` — `CommandCatalog`
- `load()` : charge `commands_catalog.json`
- `get_by_category(cat)` : filtre par catégorie
- `search(keyword)` : recherche dans name/description/tags
- `get_all()` : toutes les commandes

### `executor.py` — `CommandExecutor`
- `show_warning(cmd)` : panel `rich` jaune/rouge avec command, risks, requires_sudo
- `confirm_and_run(cmd)` : demande `[o/N]`, si `dangerous=true` demande double confirmation
- `dry_run(cmd)` : affiche sans exécuter, panel bleu
- `copy_to_clipboard(cmd)` : via `pyperclip`
- `run_all_checks(category)` : exécute toutes les commandes `safe_to_run=true` d'une catégorie

### `logger.py` — `ActionLogger`
- Écrit dans `logs/autohack.log` : `[TIMESTAMP] [USER] [CMD] [EXIT_CODE] [STATUS]`
- Méthodes : `log_run()`, `log_copy()`, `log_export()`

### `exporter.py` — `Exporter`
- `export_txt()` → `exports/commands_YYYY-MM-DD.txt`
- `export_markdown()` → `exports/report_YYYY-MM-DD_HH-MM.md`
- `export_json()` → dump du catalogue entier
- `generate_full_report()` : rapport markdown avec toutes catégories, descriptions, commandes

### `checker.py` — `ToolChecker`
- `check(tool_name)` → `True/False` via `shutil.which()`
- `check_all()` → dict `{tool: bool}` pour tous les `tool_required` du catalogue
- Résultat mis en cache (session)
- Badge `✅` / `❌` affiché dans les tableaux de menus

### `base.py` — `BaseMenu`
- `render_header(title)` : panel `rich` avec titre + breadcrumb
- `render_table(commands, checker)` : `rich.Table` avec colonnes : #, Nom, Commande, Outil, Statut (✅/❌)
- `prompt_choice(max_n)` : `Prompt.ask()` retourne choix valide
- `show_command_card(cmd)` : fiche détaillée d'une commande
- `action_loop(cmd)` : boucle `[r/d/e/c/p/b]` sur une commande

---

## Menus principaux

| # | Menu | Catégorie catalogue |
|---|------|-------------------|
| 1 | Préparation environnement | `system` |
| 2 | Vérification dépendances | `system` (subset) |
| 3 | Services réseau locaux | `network` |
| 4 | Tor | `tor` |
| 5 | Privoxy | `privoxy` |
| 6 | Scrapy | `scrapy` |
| 7 | Export JSON / fichiers | `json_export` |
| 8 | Elastic / logs | `elastic` |
| 9 | Diagnostic / debug | `diagnostic` |
| 10 | Aide pédagogique | — (help généré depuis catalogue) |
| 11 | Export de toutes les commandes | — (appelle Exporter) |
| 12 | Quitter | — |

---

## Catalogue de commandes — couverture minimale

### A. Système (≥25 commandes)
python3 --version, pip --version, which python3, which pip, uname -a, hostnamectl, ip a, ss -tulpn, systemctl status, journalctl -xe, mkdir -p, ls -la, pwd, cat, grep, find, chmod, chown, cp, mv, rm (double confirmation), tee, env, printenv, df -h, free -h, uptime, whoami

### B. Réseau local (≥10 commandes)
ping localhost, curl http://127.0.0.1, ss -tulpn, lsof -i, nc -zv localhost PORT, vérification proxy local, test port local, netstat -an

### C. Tor (≥12 commandes)
tor --version, systemctl status/start/stop/restart tor, journalctl -u tor, test SOCKS port 9050, vérification torrc, affichage exemple torrc safe, curl via socks5

### D. Privoxy (≥10 commandes)
privoxy --version, systemctl status/start/stop/restart privoxy, journalctl -u privoxy, test port 8118, curl via privoxy local, exemple config

### E. Scrapy (≥12 commandes)
scrapy version, startproject, genspider, list, crawl, shell, check, parse, export JSON local, explication spider/items/pipelines/middlewares/settings

### F. JSON / Export (≥10 commandes)
stdout redirect, tee, jq, python3 -m json.tool, export markdown, export txt, export json catalogue

### G. Elastic (≥10 commandes)
vérif installation, systemctl status, curl localhost:9200, test index local, envoi doc JSON demo, lecture index, logs service

### H. Diagnostic (≥10 commandes)
which, vérif permissions, ports ouverts, services actifs, erreurs fréquentes, suggestions correction, mode verbose

---

## Comportement si outil absent

- Commandes toujours affichées dans les menus (jamais cachées)
- Badge `❌` rouge + message `"outil non trouvé — sudo apt install <tool>"`
- Option `[r] run` disponible mais affiche un warning supplémentaire
- Aucun crash — graceful degradation totale

---

## Sécurité & journalisation

- Toute exécution réelle loguée dans `logs/autohack.log`
- Commandes `dangerous=true` : double confirmation explicite
- Commandes `requires_sudo` : avertissement visible avant exécution
- `rm` toujours en `dangerous=true` avec affichage de la cible exacte

---

## Fonctionnalités supplémentaires

- Moteur de recherche (`/search`) : filtre le catalogue par mot-clé en temps réel
- "Exécuter toutes les vérifications" : run de tous les `safe_to_run=true`
- "Générer rapport markdown" : snapshot complet dans `exports/`
- "Sauvegarder résultats" : output des runs dans `exports/results_*.txt`
