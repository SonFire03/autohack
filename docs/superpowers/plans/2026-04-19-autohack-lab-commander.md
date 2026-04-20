# AUTOHACK LAB COMMANDER Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CLI Python tool centralisant les commandes de lab (system, Tor, Privoxy, Scrapy, Elastic, réseau) avec interface rich hybride numéro+lettre.

**Architecture:** Catalogue JSON = source unique de vérité. Modules core (executor, catalog, checker, logger, exporter). Chaque catégorie = un fichier menu héritant de BaseMenu.

**Tech Stack:** Python 3.10+, rich, pyperclip, subprocess, shutil.which, pytest

---

### Task 1: Scaffold + config

**Files:**
- Create: `requirements.txt`
- Create: `config/__init__.py`
- Create: `config/settings.py`
- Create: `core/__init__.py`
- Create: `menus/__init__.py`
- Create: `tests/__init__.py`
- Create: `logs/.gitkeep`
- Create: `exports/.gitkeep`

- [ ] Create directories and empty init files
- [ ] Write requirements.txt
- [ ] Write config/settings.py
- [ ] Commit: `chore: project scaffold`

---

### Task 2: commands_catalog.json (system + network)

**Files:**
- Create: `commands_catalog.json`

- [ ] Write catalog JSON with system (28 commands) + network (10 commands)
- [ ] Commit: `feat: catalog system+network commands`

---

### Task 3: commands_catalog.json (tor + privoxy + scrapy)

**Files:**
- Modify: `commands_catalog.json`

- [ ] Add tor (12), privoxy (10), scrapy (12) commands to catalog
- [ ] Commit: `feat: catalog tor+privoxy+scrapy commands`

---

### Task 4: commands_catalog.json (json_export + elastic + diagnostic)

**Files:**
- Modify: `commands_catalog.json`

- [ ] Add json_export (10), elastic (10), diagnostic (10) commands
- [ ] Commit: `feat: catalog complete — all 102 commands`

---

### Task 5: core/catalog.py + tests

**Files:**
- Create: `core/catalog.py`
- Create: `tests/test_catalog.py`

- [ ] Write CommandCatalog class
- [ ] Write tests
- [ ] Run pytest, verify pass
- [ ] Commit

---

### Task 6: core/checker.py + core/logger.py

**Files:**
- Create: `core/checker.py`
- Create: `core/logger.py`
- Create: `tests/test_checker.py`

- [ ] Write ToolChecker class
- [ ] Write ActionLogger class
- [ ] Write tests for checker
- [ ] Commit

---

### Task 7: core/executor.py

**Files:**
- Create: `core/executor.py`

- [ ] Write CommandExecutor with confirm_and_run, dry_run, copy_to_clipboard
- [ ] Commit

---

### Task 8: core/exporter.py

**Files:**
- Create: `core/exporter.py`

- [ ] Write Exporter with export_txt, export_markdown, export_json, generate_full_report
- [ ] Commit

---

### Task 9: menus/base.py

**Files:**
- Create: `menus/base.py`

- [ ] Write BaseMenu with render_header, render_table, show_command_card, action_loop, run_loop
- [ ] Commit

---

### Task 10: All category menus

**Files:**
- Create: `menus/environment.py`, `menus/dependencies.py`, `menus/network.py`
- Create: `menus/tor.py`, `menus/privoxy.py`, `menus/scrapy_menu.py`
- Create: `menus/json_export.py`, `menus/elastic.py`, `menus/diagnostic.py`

- [ ] Write each menu as BaseMenu subclass
- [ ] Commit

---

### Task 11: Utility menus + main_menu

**Files:**
- Create: `menus/help_menu.py`, `menus/export_all.py`, `menus/search.py`
- Create: `menus/main_menu.py`

- [ ] Write help, export_all, search menus
- [ ] Write MainMenu routing to all submenus
- [ ] Commit

---

### Task 12: main.py + README.md + example_report.md

**Files:**
- Create: `main.py`
- Create: `README.md`
- Create: `example_report.md`

- [ ] Write main.py entry point
- [ ] Write README with install + usage instructions
- [ ] Generate example_report.md
- [ ] Commit: `feat: complete autohack lab commander v1.0.0`
