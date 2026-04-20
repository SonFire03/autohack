# AUTOHACK LAB COMMANDER — Catalogue de commandes

> Généré le 2026-04-19 à 04:22 | Version 1.0.0


## 🖥  Système / Environnement

### `sys_001` — Version Python

**Description :** Affiche la version Python 3 installée

```bash
python3 --version
```

**But :** Vérifier que Python 3 est installé et connaître sa version exacte. Utile pour s'assurer de la compatibilité des scripts.

**Sortie attendue :** `Python 3.10.x ou supérieur`

**Risques :** Aucun risque — commande de lecture seule

**Prérequis :** Python 3 doit être installé

---

### `sys_002` — Version pip

**Description :** Affiche la version de pip installée

```bash
pip --version
```

**But :** Vérifier que pip est disponible et connaître sa version pour la gestion des paquets Python.

**Sortie attendue :** `pip 22.x.x from /usr/lib/python3/dist-packages/pip (python 3.x)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** pip doit être installé

---

### `sys_003` — Chemin Python

**Description :** Affiche le chemin absolu de l'exécutable python3

```bash
which python3
```

**But :** Identifier quel Python sera utilisé quand on tape 'python3', utile en cas de multiple installations ou virtualenvs.

**Sortie attendue :** `/usr/bin/python3 ou /usr/local/bin/python3`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_004` — Chemin pip

**Description :** Affiche le chemin absolu de pip

```bash
which pip
```

**But :** Identifier quel pip sera utilisé, pour s'assurer d'installer les paquets dans le bon environnement.

**Sortie attendue :** `/usr/bin/pip ou /home/user/.local/bin/pip`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_005` — Info noyau Linux

**Description :** Affiche les informations complètes sur le noyau Linux

```bash
uname -a
```

**But :** Identifier la version du noyau, l'architecture (x86_64, arm64) et le système d'exploitation. Utile pour le diagnostic et la compatibilité.

**Sortie attendue :** `Linux hostname 5.15.x-generic #x-Ubuntu SMP x86_64 GNU/Linux`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_006` — Info hôte système

**Description :** Affiche le nom d'hôte, l'OS, le noyau et l'architecture

```bash
hostnamectl
```

**But :** Vue d'ensemble complète du système : OS, hostname, version noyau, architecture machine et virtualisation.

**Sortie attendue :** `Static hostname, Operating System, Kernel, Architecture`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd doit être installé

---

### `sys_007` — Interfaces réseau

**Description :** Affiche toutes les interfaces réseau et leurs adresses IP

```bash
ip a
```

**But :** Lister toutes les interfaces réseau (eth0, lo, wlan0, etc.) avec leurs adresses IPv4/IPv6. Essentiel pour identifier l'IP locale et vérifier la connectivité.

**Sortie attendue :** `lo: 127.0.0.1/8, eth0: 192.168.x.x/24, etc.`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 doit être installé

---

### `sys_008` — Ports en écoute

**Description :** Affiche tous les ports TCP/UDP en écoute avec les processus

```bash
ss -tulpn
```

**But :** Voir quels services écoutent sur quels ports. Indispensable pour vérifier que Tor (9050), Privoxy (8118), Elastic (9200) sont bien démarrés.

**Sortie attendue :** `LISTEN 0 128 0.0.0.0:22 ... sshd`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 doit être installé

---

### `sys_009` — Statut systemd

**Description :** Affiche l'état général de systemd et des unités en échec

```bash
systemctl status
```

**But :** Vue d'ensemble de l'état du système systemd : services actifs, en échec, utilisation mémoire du manager.

**Sortie attendue :** `State: running, N jobs, N loaded units`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd doit être le gestionnaire de services

---

### `sys_010` — Journaux système récents

**Description :** Affiche les derniers journaux système avec contexte

```bash
journalctl -xe --no-pager | tail -50
```

**But :** Consulter les événements système récents, particulièrement utile pour diagnostiquer pourquoi un service a échoué.

**Sortie attendue :** `Lignes de logs avec timestamps, priorités et messages`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd-journald doit être actif

---

### `sys_011` — Créer répertoire

**Description :** Crée un répertoire et ses parents si nécessaire

```bash
mkdir -p ~/lab/test_dir
```

**But :** Créer une arborescence de répertoires sans erreur si les parents n'existent pas. L'option -p évite l'erreur si le dossier existe déjà.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Faible — crée des répertoires dans votre home

**Prérequis :** Aucun

---

### `sys_012` — Lister fichiers

**Description :** Liste tous les fichiers avec détails et fichiers cachés

```bash
ls -la
```

**But :** Voir tous les fichiers (y compris cachés avec .) avec permissions, propriétaire, taille et date de modification.

**Sortie attendue :** `drwxr-xr-x 2 user group 4096 Apr 19 ... nom_fichier`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_013` — Répertoire courant

**Description :** Affiche le chemin absolu du répertoire courant

```bash
pwd
```

**But :** Connaître sa position dans l'arborescence. Utile pour s'assurer qu'on exécute les commandes au bon endroit.

**Sortie attendue :** `/home/user/projects/autohack`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_014` — Lire un fichier

**Description :** Affiche le contenu d'un fichier texte

```bash
cat /etc/os-release
```

**But :** Lire le contenu d'un fichier directement dans le terminal. Ici appliqué à /etc/os-release pour identifier la distribution Linux.

**Sortie attendue :** `NAME=Ubuntu, VERSION=22.04, etc.`

**Risques :** Aucun risque si fichier est lisible — lecture seule

**Prérequis :** Aucun

---

### `sys_015` — Rechercher dans fichiers

**Description :** Recherche un motif dans les fichiers ou l'entrée standard

```bash
grep -r 'localhost' /etc/ 2>/dev/null | head -20
```

**But :** Trouver des occurrences d'un texte dans des fichiers. Ici pour trouver les configs référençant localhost.

**Sortie attendue :** `Lignes contenant 'localhost' avec chemin de fichier`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_016` — Chercher fichiers

**Description :** Cherche des fichiers selon des critères

```bash
find /etc -name '*.conf' -type f 2>/dev/null | head -20
```

**But :** Localiser des fichiers par nom, type, taille, date. Utile pour trouver des fichiers de configuration.

**Sortie attendue :** `Liste de chemins de fichiers .conf`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_017` — Modifier permissions

**Description :** Modifie les permissions d'accès d'un fichier

```bash
chmod 755 ~/lab/test_script.sh
```

**But :** Définir qui peut lire (r), écrire (w) ou exécuter (x) un fichier. 755 = propriétaire tout, groupe+autres lecture+exécution.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Modéré — mauvaises permissions peuvent bloquer l'accès ou créer des failles de sécurité

**Prérequis :** Être propriétaire du fichier

---

### `sys_018` — Modifier propriétaire

**Description :** Change le propriétaire et/ou groupe d'un fichier

```bash
chown $USER:$USER ~/lab/test_file.txt
```

**But :** Attribuer la propriété d'un fichier à un utilisateur/groupe. Utile après des copies avec sudo ou des opérations qui changent le propriétaire.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Modéré — utiliser avec précaution, surtout avec sudo

**Prérequis :** Être propriétaire du fichier ou root

---

### `sys_019` — Copier fichier

**Description :** Copie un fichier ou répertoire

```bash
cp /etc/tor/torrc ~/lab/torrc.backup
```

**But :** Créer une copie d'un fichier. Essentiel avant toute modification de fichier de configuration (backup).

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Faible — peut écraser un fichier existant sans avertissement

**Prérequis :** Droits de lecture sur la source, Droits d'écriture sur la destination

---

### `sys_020` — Déplacer / renommer

**Description :** Déplace ou renomme un fichier ou répertoire

```bash
mv ~/lab/ancien_nom.txt ~/lab/nouveau_nom.txt
```

**But :** Renommer ou déplacer des fichiers. Contrairement à cp, mv supprime la source après la copie.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Modéré — déplace définitivement, peut écraser si destination existe

**Prérequis :** Droits sur source et destination

---

### `sys_021` — Supprimer fichier ⚠️**DANGEREUX**

**Description :** Supprime un fichier (IRRÉVERSIBLE sans backup)

```bash
rm ~/lab/test_file.txt
```

**But :** Supprimer un fichier. Attention : Linux n'a pas de corbeille pour rm — la suppression est définitive.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** DANGEREUX — suppression irréversible. Toujours vérifier le chemin avant exécution.

**Prérequis :** Droits d'écriture sur le fichier

---

### `sys_022` — Tee — écrire et afficher

**Description :** Lit stdin et écrit simultanément dans stdout ET un fichier

```bash
echo 'test log' | tee ~/lab/output.log
```

**But :** Capturer la sortie d'une commande dans un fichier tout en l'affichant dans le terminal. Très utile pour logger les résultats de commandes.

**Sortie attendue :** `test log (affiché ET écrit dans output.log)`

**Risques :** Faible — écrase le fichier si existant (utiliser tee -a pour append)

**Prérequis :** Aucun

---

### `sys_023` — Variables d'environnement

**Description :** Affiche toutes les variables d'environnement

```bash
env | sort
```

**But :** Voir toutes les variables d'environnement actives : PATH, HOME, USER, proxy settings, etc. Utile pour diagnostiquer des problèmes de configuration.

**Sortie attendue :** `HOME=/home/user, PATH=/usr/bin:..., USER=user, etc.`

**Risques :** Aucun risque — lecture seule. Note : peut afficher des informations sensibles

**Prérequis :** Aucun

---

### `sys_024` — Espace disque

**Description :** Affiche l'utilisation des disques en format lisible

```bash
df -h
```

**But :** Vérifier l'espace disponible sur chaque partition. Utile avant de lancer des opérations qui génèrent des données (scrapy, elastic).

**Sortie attendue :** `Filesystem, Size, Used, Avail, Use%, Mounted on`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_025` — Mémoire RAM

**Description :** Affiche l'utilisation de la mémoire RAM et swap

```bash
free -h
```

**But :** Vérifier la mémoire disponible. Elasticsearch nécessite au minimum 1-2 GB de RAM pour fonctionner correctement.

**Sortie attendue :** `total, used, free, shared, buff/cache, available`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_026` — Temps d'activité

**Description :** Affiche depuis combien de temps le système tourne

```bash
uptime
```

**But :** Connaître la durée de fonctionnement du système et la charge moyenne CPU. Utile pour évaluer la stabilité.

**Sortie attendue :** `hh:mm up X days, X:XX, N users, load average: 0.x, 0.x, 0.x`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_027` — Utilisateur courant

**Description :** Affiche le nom de l'utilisateur courant

```bash
whoami
```

**But :** Confirmer sous quel utilisateur on est connecté. Important avant d'exécuter des commandes qui nécessitent ou refusent root.

**Sortie attendue :** `user (ou root si élevé)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `sys_028` — Processus actifs

**Description :** Affiche tous les processus en cours d'exécution

```bash
ps aux | head -30
```

**But :** Lister les processus actifs avec leur PID, utilisation CPU/mémoire. Utile pour vérifier si tor, privoxy, elasticsearch sont en cours d'exécution.

**Sortie attendue :** `USER PID %CPU %MEM VSZ RSS TTY STAT START TIME COMMAND`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---


## 🌐 Réseau Local de Lab

### `net_001` — Ping localhost

**Description :** Vérifie la connectivité avec la boucle locale

```bash
ping -c 4 localhost
```

**But :** Tester que la pile réseau locale fonctionne. Si ce ping échoue, il y a un problème réseau fondamental sur la machine.

**Sortie attendue :** `4 paquets transmis, 4 reçus, 0% perte, temps ~0ms`

**Risques :** Aucun risque — trafic uniquement local

**Prérequis :** Aucun

---

### `net_002` — Test HTTP local

**Description :** Envoie une requête HTTP GET à localhost

```bash
curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1
```

**But :** Tester si un serveur HTTP tourne sur localhost port 80. Affiche le code HTTP (200=OK, 000=pas de serveur).

**Sortie attendue :** `200 (si serveur actif) ou 000/Connection refused (si absent)`

**Risques :** Aucun risque — requête locale uniquement

**Prérequis :** curl doit être installé

---

### `net_003` — Ports ouverts détaillés

**Description :** Liste tous les ports TCP/UDP ouverts avec les processus associés

```bash
ss -tulpn
```

**But :** Vue complète des ports en écoute. Permet de vérifier en un coup d'œil quels services sont actifs (SSH:22, Tor:9050, Privoxy:8118, Elastic:9200).

**Sortie attendue :** `LISTEN 0 128 127.0.0.1:9050 ... tor`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 doit être installé

---

### `net_004` — Processus sur port

**Description :** Identifie quel processus utilise un port spécifique

```bash
lsof -i :9050
```

**But :** Savoir quel processus occupe un port précis. Ici port 9050 (Tor SOCKS). Utile pour diagnostiquer les conflits de ports.

**Sortie attendue :** `COMMAND PID USER ... TCP localhost:9050 (LISTEN)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** lsof doit être installé

---

### `net_005` — Test port local (nc)

**Description :** Teste si un port local est accessible

```bash
nc -zv localhost 9050
```

**But :** Vérifier rapidement si un port est ouvert et accessible. Utile pour tester le port SOCKS de Tor ou le port HTTP de Privoxy.

**Sortie attendue :** `Connection to localhost 9050 port [tcp/*] succeeded!`

**Risques :** Aucun risque — test en lecture seule sur localhost

**Prérequis :** netcat (nc) doit être installé

---

### `net_006` — Test proxy Privoxy

**Description :** Teste le proxy Privoxy local avec curl

```bash
curl -x http://127.0.0.1:8118 -s -o /dev/null -w '%{http_code}' http://127.0.0.1
```

**But :** Vérifier que Privoxy est actif et accepte les connexions proxy sur le port 8118. La requête cible localhost pour rester local.

**Sortie attendue :** `200 ou 503 (si Privoxy actif mais cible inaccessible)`

**Risques :** Aucun risque — requête locale via proxy local uniquement

**Prérequis :** curl installé, Privoxy démarré sur port 8118

---

### `net_007` — Test SOCKS Tor

**Description :** Teste le proxy SOCKS5 de Tor

```bash
curl --socks5 127.0.0.1:9050 -s -o /dev/null -w '%{http_code}' http://127.0.0.1
```

**But :** Vérifier que Tor est actif et son proxy SOCKS5 répond sur le port 9050. La requête cible localhost pour rester en local.

**Sortie attendue :** `Code HTTP ou erreur de connexion`

**Risques :** Aucun risque — requête locale via SOCKS5 local uniquement

**Prérequis :** curl avec support SOCKS5, Tor démarré

---

### `net_008` — Table de routage

**Description :** Affiche la table de routage réseau

```bash
ip route
```

**But :** Voir comment le trafic réseau est routé : quelle interface par défaut, quels sous-réseaux sont accessibles directement.

**Sortie attendue :** `default via 192.168.1.1 dev eth0, 192.168.1.0/24 dev eth0 ...`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 installé

---

### `net_009` — DNS local

**Description :** Affiche la configuration DNS du système

```bash
cat /etc/resolv.conf
```

**But :** Voir quels serveurs DNS sont configurés. Important pour comprendre si les requêtes DNS passent par Tor ou non.

**Sortie attendue :** `nameserver 127.0.0.53 (systemd-resolved) ou 8.8.8.8`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `net_010` — Connexions actives

**Description :** Affiche les connexions TCP établies avec processus

```bash
ss -tnp
```

**But :** Voir les connexions réseau actuellement établies. Utile pour vérifier qu'une connexion Tor est active ou diagnostiquer des connexions inattendues.

**Sortie attendue :** `ESTAB 0 0 IP:PORT PEER_IP:PORT ... pid=X,fd=X`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 installé

---


## 🧅 Tor

### `tor_001` — Version Tor

**Description :** Affiche la version de Tor installée

```bash
tor --version
```

**But :** Vérifier que Tor est installé et connaître sa version. Tor 0.4.x et supérieur est recommandé.

**Sortie attendue :** `Tor version 0.4.x.x.`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Tor doit être installé : sudo apt install tor

---

### `tor_002` — Statut service Tor

**Description :** Affiche l'état du service systemd Tor

```bash
systemctl status tor
```

**But :** Voir si Tor est actif (active/running), inactif, ou en erreur. Affiche les dernières lignes de logs.

**Sortie attendue :** `● tor.service - Anonymizing overlay network for TCP... Active: active (running)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Tor installé, systemd disponible

---

### `tor_003` — Démarrer Tor `[sudo]`

**Description :** Démarre le service Tor

```bash
sudo systemctl start tor
```

**But :** Lancer le daemon Tor. Une fois démarré, un proxy SOCKS5 sera disponible sur 127.0.0.1:9050.

**Sortie attendue :** `Aucune sortie (succès silencieux) — vérifier avec systemctl status tor`

**Risques :** Faible — démarre un service local. Ne crée pas de connexion sortante immédiate.

**Prérequis :** Tor installé, Droits sudo

---

### `tor_004` — Arrêter Tor `[sudo]`

**Description :** Arrête le service Tor

```bash
sudo systemctl stop tor
```

**But :** Stopper le daemon Tor et fermer le proxy SOCKS5. Utile pour libérer des ressources ou tester l'absence de Tor.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Faible — coupe les connexions Tor en cours

**Prérequis :** Tor installé, Droits sudo

---

### `tor_005` — Redémarrer Tor `[sudo]`

**Description :** Redémarre le service Tor (nouveau circuit)

```bash
sudo systemctl restart tor
```

**But :** Redémarrer Tor pour obtenir un nouveau circuit et une nouvelle identité réseau. Utile après modification de torrc.

**Sortie attendue :** `Aucune sortie — vérifier avec systemctl status tor`

**Risques :** Faible — coupe brièvement les connexions Tor

**Prérequis :** Tor installé, Droits sudo

---

### `tor_006` — Logs Tor

**Description :** Affiche les journaux du service Tor

```bash
journalctl -u tor -n 50 --no-pager
```

**But :** Consulter les logs de Tor pour diagnostiquer des problèmes de démarrage, de circuit ou de connexion.

**Sortie attendue :** `Bootstrapped 100% (done): Done — indique que Tor est connecté`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd-journald actif, Tor installé

---

### `tor_007` — Test port SOCKS Tor

**Description :** Vérifie que le port SOCKS5 de Tor est ouvert

```bash
nc -zv localhost 9050
```

**But :** Confirmer que Tor écoute bien sur le port 9050 (SOCKS5 par défaut). Si fermé, Tor n'est pas démarré ou a changé de port.

**Sortie attendue :** `Connection to localhost 9050 port [tcp/*] succeeded!`

**Risques :** Aucun risque — test local uniquement

**Prérequis :** netcat installé, Tor démarré

---

### `tor_008` — Fichier torrc

**Description :** Affiche le fichier de configuration de Tor

```bash
cat /etc/tor/torrc
```

**But :** Lire la configuration actuelle de Tor : port SOCKS, ExitNodes, HiddenServices, etc. Nécessite parfois sudo.

**Sortie attendue :** `# This file was generated by Tor... SocksPort 9050`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Tor installé, Droits de lecture sur /etc/tor/torrc

---

### `tor_009` — Vérifier torrc (syntaxe)

**Description :** Vérifie la syntaxe du fichier torrc sans lancer Tor

```bash
tor --verify-config
```

**But :** Valider la configuration torrc avant de (re)démarrer Tor. Évite de casser le service par une erreur de syntaxe.

**Sortie attendue :** `Configuration was valid`

**Risques :** Aucun risque — ne démarre pas Tor, validation uniquement

**Prérequis :** Tor installé, Droits de lecture sur torrc

---

### `tor_010` — Activer Tor au démarrage `[sudo]`

**Description :** Active le démarrage automatique de Tor au boot

```bash
sudo systemctl enable tor
```

**But :** Configurer Tor pour démarrer automatiquement à chaque redémarrage du système.

**Sortie attendue :** `Created symlink /etc/systemd/system/... → /lib/systemd/system/tor.service`

**Risques :** Faible — Tor démarrera automatiquement à chaque boot

**Prérequis :** Tor installé, Droits sudo

---

### `tor_011` — Désactiver Tor au démarrage `[sudo]`

**Description :** Désactive le démarrage automatique de Tor

```bash
sudo systemctl disable tor
```

**But :** Empêcher Tor de démarrer automatiquement au boot, tout en gardant la possibilité de le lancer manuellement.

**Sortie attendue :** `Removed /etc/systemd/system/multi-user.target.wants/tor.service`

**Risques :** Faible — Tor ne démarrera plus automatiquement

**Prérequis :** Tor installé, Droits sudo

---

### `tor_012` — Installer Tor `[sudo]`

**Description :** Installe Tor depuis les dépôts apt

```bash
sudo apt-get update && sudo apt-get install -y tor
```

**But :** Installer Tor sur Ubuntu/Debian. L'option -y confirme automatiquement l'installation.

**Sortie attendue :** `Setting up tor (0.4.x.x) ...`

**Risques :** Modéré — installe des paquets système, nécessite connexion internet

**Prérequis :** Droits sudo, Connexion internet, apt disponible

---


## 🔀 Privoxy

### `prx_001` — Version Privoxy

**Description :** Affiche la version de Privoxy installée

```bash
privoxy --version
```

**But :** Vérifier que Privoxy est installé. Privoxy est un proxy HTTP qui peut être chaîné avec Tor (HTTP→SOCKS5).

**Sortie attendue :** `Privoxy version 3.0.x`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Privoxy doit être installé : sudo apt install privoxy

---

### `prx_002` — Statut Privoxy

**Description :** Affiche l'état du service Privoxy

```bash
systemctl status privoxy
```

**But :** Vérifier si Privoxy est actif et écoute sur le port 8118. Affiche les derniers logs.

**Sortie attendue :** `● privoxy.service - Privacy enhancing HTTP Proxy... Active: active (running)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Privoxy installé, systemd disponible

---

### `prx_003` — Démarrer Privoxy `[sudo]`

**Description :** Démarre le service Privoxy

```bash
sudo systemctl start privoxy
```

**But :** Lancer Privoxy. Une fois démarré, un proxy HTTP est disponible sur 127.0.0.1:8118.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Faible — démarre un proxy local

**Prérequis :** Privoxy installé, Droits sudo

---

### `prx_004` — Arrêter Privoxy `[sudo]`

**Description :** Arrête le service Privoxy

```bash
sudo systemctl stop privoxy
```

**But :** Stopper Privoxy et fermer le proxy HTTP sur port 8118.

**Sortie attendue :** `Aucune sortie (succès silencieux)`

**Risques :** Faible — coupe les connexions proxy en cours

**Prérequis :** Privoxy installé, Droits sudo

---

### `prx_005` — Redémarrer Privoxy `[sudo]`

**Description :** Redémarre le service Privoxy

```bash
sudo systemctl restart privoxy
```

**But :** Redémarrer Privoxy après modification de sa configuration.

**Sortie attendue :** `Aucune sortie — vérifier avec systemctl status privoxy`

**Risques :** Faible — coupe brièvement le proxy

**Prérequis :** Privoxy installé, Droits sudo

---

### `prx_006` — Logs Privoxy

**Description :** Affiche les journaux du service Privoxy

```bash
journalctl -u privoxy -n 50 --no-pager
```

**But :** Consulter les logs de Privoxy pour diagnostiquer des problèmes de proxy ou de filtrage.

**Sortie attendue :** `privoxy[PID]: Accepting connections on 127.0.0.1:8118`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd-journald actif

---

### `prx_007` — Test port Privoxy

**Description :** Vérifie que Privoxy écoute sur le port 8118

```bash
nc -zv localhost 8118
```

**But :** Confirmer que Privoxy est actif et accessible sur le port HTTP proxy 8118.

**Sortie attendue :** `Connection to localhost 8118 port [tcp/*] succeeded!`

**Risques :** Aucun risque — test local

**Prérequis :** netcat installé, Privoxy démarré

---

### `prx_008` — Config Privoxy

**Description :** Affiche la configuration de Privoxy

```bash
grep -v '^#' /etc/privoxy/config | grep -v '^$'
```

**But :** Voir la configuration active de Privoxy (sans les commentaires). Vérifier notamment forward-socks5 vers Tor.

**Sortie attendue :** `listen-address 127.0.0.1:8118, forward-socks5 / 127.0.0.1:9050 .`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Privoxy installé, Droits lecture sur /etc/privoxy/config

---

### `prx_009` — Installer Privoxy `[sudo]`

**Description :** Installe Privoxy depuis les dépôts apt

```bash
sudo apt-get update && sudo apt-get install -y privoxy
```

**But :** Installer Privoxy sur Ubuntu/Debian pour créer un proxy HTTP pouvant être chaîné avec Tor.

**Sortie attendue :** `Setting up privoxy (3.0.x) ...`

**Risques :** Modéré — installe des paquets système

**Prérequis :** Droits sudo, Connexion internet

---

### `prx_010` — Test proxy complet (Tor+Privoxy)

**Description :** Teste la chaîne proxy Privoxy→Tor sur localhost

```bash
curl -x http://127.0.0.1:8118 -s -o /dev/null -w 'HTTP: %{http_code}\n' http://127.0.0.1
```

**But :** Vérifier que la chaîne Privoxy (HTTP proxy) → Tor (SOCKS5) fonctionne. Si configuré correctement, Privoxy forward vers Tor.

**Sortie attendue :** `HTTP: 200 ou message Privoxy si cible inaccessible`

**Risques :** Aucun risque — requête locale uniquement

**Prérequis :** Privoxy actif sur 8118, Tor actif sur 9050, config forward-socks5 dans Privoxy

---


## 🕷  Scrapy

### `scr_001` — Version Scrapy

**Description :** Affiche la version de Scrapy installée

```bash
scrapy version
```

**But :** Vérifier que Scrapy est installé et connaître sa version. Scrapy 2.x est requis pour les fonctionnalités modernes.

**Sortie attendue :** `Scrapy 2.x.x`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Scrapy doit être installé : pip install scrapy

---

### `scr_002` — Créer projet Scrapy

**Description :** Crée un nouveau projet Scrapy dans ~/lab/

```bash
scrapy startproject demo_lab ~/lab/scrapy_demo
```

**But :** Initialiser la structure d'un projet Scrapy : spiders/, items.py, pipelines.py, middlewares.py, settings.py.

**Sortie attendue :** `New Scrapy project 'demo_lab' created in .../scrapy_demo`

**Risques :** Faible — crée des fichiers dans ~/lab/

**Prérequis :** Scrapy installé, ~/lab/ accessible en écriture

---

### `scr_003` — Générer spider

**Description :** Génère un spider de démonstration

```bash
cd ~/lab/scrapy_demo && scrapy genspider demo_spider example.com
```

**But :** Créer un spider de base dans spiders/. Un spider définit comment naviguer un site et extraire des données.

**Sortie attendue :** `Created spider 'demo_spider' using template 'basic'`

**Risques :** Faible — crée un fichier Python dans le projet

**Prérequis :** Scrapy installé, Projet Scrapy créé

---

### `scr_004` — Lister les spiders

**Description :** Liste tous les spiders disponibles dans le projet

```bash
cd ~/lab/scrapy_demo && scrapy list
```

**But :** Voir tous les spiders définis dans le projet courant. Utile pour confirmer qu'un spider a été correctement créé.

**Sortie attendue :** `demo_spider`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Projet Scrapy initialisé

---

### `scr_005` — Vérifier spider

**Description :** Vérifie les contrats du spider sans le lancer

```bash
cd ~/lab/scrapy_demo && scrapy check
```

**But :** Valider les contrats de tests du spider (annotations @url, @returns). Utile pour s'assurer de la qualité du spider sans exécuter de requêtes.

**Sortie attendue :** `... ran N items in N.Xs — OK`

**Risques :** Aucun risque — validation statique uniquement

**Prérequis :** Scrapy installé, Projet avec spiders

---

### `scr_006` — Shell Scrapy

**Description :** Lance le shell interactif Scrapy sur un fichier local

```bash
scrapy shell file:///etc/os-release
```

**But :** Explorer interactivement la structure d'une page et tester des sélecteurs CSS/XPath. Ici sur un fichier local pour rester dans le lab.

**Sortie attendue :** `Shell interactif avec accès à response, response.css(), response.xpath()`

**Risques :** Faible — lecture d'un fichier local uniquement

**Prérequis :** Scrapy installé

---

### `scr_007` — Export JSON local

**Description :** Lance un spider et exporte les résultats en JSON

```bash
cd ~/lab/scrapy_demo && scrapy crawl demo_spider -o ~/lab/output.json
```

**But :** Exécuter un spider et sauvegarder les items extraits dans un fichier JSON. L'option -o spécifie le fichier de sortie.

**Sortie attendue :** `Fichier ~/lab/output.json créé avec les items extraits`

**Risques :** Modéré — exécute le spider, faire des requêtes réseau si non limité à local

**Prérequis :** Scrapy installé, Spider configuré, Cible accessible

---

### `scr_008` — Version Scrapy détaillée

**Description :** Affiche Scrapy et ses dépendances (Twisted, Python, etc.)

```bash
scrapy version -v
```

**But :** Voir toutes les dépendances de Scrapy : Twisted (moteur async), lxml (parsing HTML), cssselect, etc.

**Sortie attendue :** `Scrapy X.X.X, Twisted X.X.X, Python X.X.X, ...`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Scrapy installé

---

### `scr_009` — Installer Scrapy

**Description :** Installe Scrapy via pip

```bash
pip install scrapy
```

**But :** Installer Scrapy dans l'environnement Python courant. Recommandé dans un virtualenv pour isoler les dépendances.

**Sortie attendue :** `Successfully installed scrapy-2.x.x ...`

**Risques :** Faible — installe des paquets Python dans l'environnement courant

**Prérequis :** pip installé, Python 3.8+

---

### `scr_010` — Benchmarks Scrapy

**Description :** Lance un benchmark de performance Scrapy

```bash
scrapy bench
```

**But :** Mesurer les performances du moteur Scrapy sur la machine locale. Donne une idée du nombre de pages/seconde atteignable.

**Sortie attendue :** `2016-xx-xx ... INFO: Crawled X pages (at X pages/min)`

**Risques :** Faible — benchmark local, consomme du CPU momentanément

**Prérequis :** Scrapy installé

---

### `scr_011` — Settings Scrapy

**Description :** Affiche la valeur d'un paramètre de configuration Scrapy

```bash
cd ~/lab/scrapy_demo && scrapy settings --get DOWNLOAD_DELAY
```

**But :** Consulter les paramètres de configuration du projet Scrapy. DOWNLOAD_DELAY est crucial pour ne pas surcharger les serveurs cibles.

**Sortie attendue :** `0 (délai par défaut, modifier dans settings.py)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Scrapy installé, Projet Scrapy initialisé

---

### `scr_012` — Contrats spider

**Description :** Analyse la réponse d'une URL avec un spider spécifique

```bash
cd ~/lab/scrapy_demo && scrapy parse file:///etc/os-release --spider demo_spider
```

**But :** Tester le parsing d'une URL par un spider sans lancer un crawl complet. Utile pour déboguer les extracteurs.

**Sortie attendue :** `Affiche les items et requests générés par le spider`

**Risques :** Faible — un seul fichier local parsé

**Prérequis :** Scrapy installé, Spider créé

---


## 📦 JSON / Export

### `jex_001` — Rediriger stdout vers fichier

**Description :** Redirige la sortie d'une commande vers un fichier

```bash
python3 --version > ~/lab/python_version.txt && cat ~/lab/python_version.txt
```

**But :** Capturer la sortie d'une commande dans un fichier. L'opérateur > crée ou écrase le fichier. >> pour ajouter.

**Sortie attendue :** `Python 3.x.x (écrit dans le fichier ET affiché via cat)`

**Risques :** Faible — crée un fichier dans ~/lab/

**Prérequis :** Aucun

---

### `jex_002` — Tee — double sortie

**Description :** Affiche ET sauvegarde la sortie simultanément

```bash
ls -la /etc/ | tee ~/lab/ls_etc.log | head -5
```

**But :** tee permet de voir la sortie en temps réel ET de la sauvegarder. Idéal pour les longues commandes dont on veut garder trace.

**Sortie attendue :** `5 premières lignes affichées, toutes les lignes dans ls_etc.log`

**Risques :** Faible — crée un fichier log

**Prérequis :** Aucun

---

### `jex_003` — Formater JSON (Python)

**Description :** Formate et valide du JSON depuis stdin

```bash
echo '{"nom":"test","valeur":42}' | python3 -m json.tool
```

**But :** Valider et formater du JSON avec indentation. Détecte les erreurs de syntaxe JSON.

**Sortie attendue :** `JSON indenté et coloré (si terminal le supporte)`

**Risques :** Aucun risque — lecture/validation uniquement

**Prérequis :** Python 3 installé

---

### `jex_004` — Formater JSON (jq)

**Description :** Formate, filtre et transforme du JSON avec jq

```bash
echo '[{"id":1,"nom":"test"}]' | jq '.[0].nom'
```

**But :** jq est l'outil de référence pour manipuler du JSON en ligne de commande. Filtrage, transformation, extraction.

**Sortie attendue :** `"test"`

**Risques :** Aucun risque — lecture seule

**Prérequis :** jq doit être installé : sudo apt install jq

---

### `jex_005` — Valider JSON Python

**Description :** Valide un fichier JSON avec Python

```bash
python3 -c "import json,sys; json.load(open(sys.argv[1])); print('JSON valide')" ~/lab/output.json
```

**But :** Vérifier qu'un fichier JSON est syntaxiquement correct. Affiche une erreur précise en cas de problème.

**Sortie attendue :** `JSON valide (ou SyntaxError avec la position de l'erreur)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Python 3 installé, Fichier JSON à valider

---

### `jex_006` — Afficher JSON formaté

**Description :** Affiche un fichier JSON avec indentation lisible

```bash
cat ~/lab/output.json | python3 -m json.tool 2>/dev/null || echo 'Fichier non trouvé ou JSON invalide'
```

**But :** Lire un fichier JSON avec une indentation claire. Utile pour inspecter les sorties de Scrapy ou Elasticsearch.

**Sortie attendue :** `JSON indenté sur plusieurs lignes`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Python 3 installé, Fichier JSON existant

---

### `jex_007` — Compter lignes fichier

**Description :** Compte le nombre de lignes dans un fichier

```bash
wc -l ~/lab/output.json
```

**But :** Connaître rapidement la taille d'un fichier en lignes. Utile pour savoir combien d'items Scrapy a exportés.

**Sortie attendue :** `42 /home/user/lab/output.json`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `jex_008` — Taille fichier

**Description :** Affiche la taille d'un fichier ou répertoire

```bash
du -sh ~/lab/ 2>/dev/null
```

**But :** Voir l'espace occupé par les fichiers de lab. Utile pour surveiller la croissance des exports JSON.

**Sortie attendue :** `4,5M    /home/user/lab/`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `jex_009` — Compresser archive

**Description :** Crée une archive compressée gzip d'un répertoire

```bash
tar -czf ~/lab/backup_$(date +%Y%m%d).tar.gz ~/lab/
```

**But :** Archiver et compresser les résultats de lab. Le nom inclut la date pour faciliter l'organisation.

**Sortie attendue :** `Fichier .tar.gz créé dans ~/lab/`

**Risques :** Faible — crée un fichier, peut écraser si même nom

**Prérequis :** tar installé

---

### `jex_010` — Lister fichiers exports

**Description :** Liste les fichiers dans le dossier exports avec tailles

```bash
ls -lh ~/lab/ 2>/dev/null | grep -E '\.(json|txt|md|log)$'
```

**But :** Voir rapidement tous les fichiers d'export disponibles avec leurs tailles en format lisible.

**Sortie attendue :** `-rw-r--r-- 1 user user 42K Apr 19 output.json`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---


## 🔍 Elastic / Logs

### `elk_001` — Vérifier installation Elastic

**Description :** Vérifie si Elasticsearch est installé

```bash
which elasticsearch || dpkg -l elasticsearch 2>/dev/null | tail -1
```

**But :** Savoir si Elasticsearch est installé sur la machine avant de tenter de l'utiliser.

**Sortie attendue :** `/usr/bin/elasticsearch ou ligne dpkg avec version`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `elk_002` — Statut Elasticsearch

**Description :** Affiche l'état du service Elasticsearch

```bash
systemctl status elasticsearch 2>/dev/null || echo 'Service elasticsearch non trouvé'
```

**But :** Vérifier si Elasticsearch est actif. Elasticsearch prend du temps à démarrer (30-60s normalement).

**Sortie attendue :** `● elasticsearch.service ... Active: active (running)`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Elasticsearch installé, systemd disponible

---

### `elk_003` — Test API Elasticsearch

**Description :** Vérifie que l'API REST Elasticsearch répond

```bash
curl -s http://localhost:9200 | python3 -m json.tool 2>/dev/null || echo 'Elasticsearch non accessible sur port 9200'
```

**But :** Confirmer qu'Elasticsearch est démarré et l'API REST répond. Affiche la version et l'état du cluster.

**Sortie attendue :** `{"name": "...", "version": {"number": "8.x.x"}, "tagline": "You Know, for Search"}`

**Risques :** Aucun risque — requête locale en lecture

**Prérequis :** Elasticsearch démarré, curl installé

---

### `elk_004` — Santé du cluster

**Description :** Affiche la santé du cluster Elasticsearch

```bash
curl -s http://localhost:9200/_cluster/health | python3 -m json.tool 2>/dev/null || echo 'Elasticsearch non accessible'
```

**But :** Vérifier l'état de santé : green (ok), yellow (réplicas manquants), red (données indisponibles).

**Sortie attendue :** `{"status": "green", "number_of_nodes": 1, ...}`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Elasticsearch démarré

---

### `elk_005` — Lister les index

**Description :** Liste tous les index Elasticsearch

```bash
curl -s http://localhost:9200/_cat/indices?v 2>/dev/null || echo 'Elasticsearch non accessible'
```

**But :** Voir tous les index existants avec leur statut, nombre de documents et taille. Vue d'ensemble rapide de la base.

**Sortie attendue :** `health status index uuid pri rep docs.count store.size`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Elasticsearch démarré

---

### `elk_006` — Créer index de démo

**Description :** Crée un index de démonstration local

```bash
curl -s -X PUT 'http://localhost:9200/lab-demo' -H 'Content-Type: application/json' | python3 -m json.tool 2>/dev/null
```

**But :** Créer un index local nommé 'lab-demo' pour les tests. Un index Elasticsearch est comparable à une table SQL.

**Sortie attendue :** `{"acknowledged": true, "shards_acknowledged": true, "index": "lab-demo"}`

**Risques :** Faible — crée un index local dans Elasticsearch

**Prérequis :** Elasticsearch démarré

---

### `elk_007` — Indexer document JSON

**Description :** Envoie un document JSON de démo dans Elasticsearch

```bash
curl -s -X POST 'http://localhost:9200/lab-demo/_doc' -H 'Content-Type: application/json' -d '{"titre":"Test lab","date":"2026-04-19","valeur":42}' | python3 -m json.tool
```

**But :** Insérer un document dans un index Elasticsearch. Chaque document a un _id unique auto-généré.

**Sortie attendue :** `{"_index": "lab-demo", "_id": "...", "result": "created"}`

**Risques :** Faible — écrit un document de test dans Elasticsearch local

**Prérequis :** Elasticsearch démarré, Index lab-demo créé

---

### `elk_008` — Recherche dans index

**Description :** Effectue une recherche dans l'index de démo

```bash
curl -s 'http://localhost:9200/lab-demo/_search?pretty' | python3 -m json.tool 2>/dev/null
```

**But :** Rechercher des documents dans un index. Sans query, retourne tous les documents (max 10 par défaut).

**Sortie attendue :** `{"hits": {"total": {"value": N}, "hits": [...]}}`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Elasticsearch démarré, Index avec documents

---

### `elk_009` — Logs Elasticsearch

**Description :** Affiche les logs du service Elasticsearch

```bash
journalctl -u elasticsearch -n 50 --no-pager 2>/dev/null || echo 'Service elasticsearch non trouvé dans journald'
```

**But :** Consulter les logs d'Elasticsearch pour diagnostiquer les problèmes de démarrage ou de performance.

**Sortie attendue :** `Lignes de logs incluant 'started' si démarré correctement`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Elasticsearch installé, systemd-journald actif

---

### `elk_010` — Installer Elasticsearch

**Description :** Installe Elasticsearch via apt (nécessite repo)

```bash
echo 'Ajout du repo Elastic requis. Voir: https://www.elastic.co/guide/en/elasticsearch/reference/current/deb.html'
```

**But :** Elasticsearch nécessite l'ajout du dépôt Elastic avant installation. Cette commande affiche les instructions.

**Sortie attendue :** `Instructions d'installation`

**Risques :** Modéré — installation de service système lourd (RAM)

**Prérequis :** Droits sudo, Connexion internet, Minimum 2GB RAM disponible

---


## 🔧 Diagnostic / Debug

### `diag_001` — Vérifier outil disponible

**Description :** Vérifie si un outil/commande est disponible dans le PATH

```bash
which tor privoxy scrapy curl jq nc 2>/dev/null; echo '---'; for t in tor privoxy scrapy curl jq nc; do command -v $t >/dev/null && echo "✅ $t" || echo "❌ $t"; done
```

**But :** Vérifier d'un coup quels outils essentiels du lab sont installés. Identifie ce qui manque avant de commencer.

**Sortie attendue :** `✅ ou ❌ pour chaque outil`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `diag_002` — Vérifier permissions fichier

**Description :** Affiche les permissions détaillées d'un fichier

```bash
stat /etc/tor/torrc 2>/dev/null || echo 'Fichier non trouvé'
```

**But :** Voir les permissions exactes (octal et symbolique), propriétaire, groupe et dates d'un fichier. Utile pour diagnostiquer les problèmes d'accès.

**Sortie attendue :** `File: /etc/tor/torrc, Size: ..., Access: (0640/-rw-r-----), Uid: (0/root), Gid: ...`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `diag_003` — Ports locaux ouverts

**Description :** Liste tous les ports TCP en écoute

```bash
ss -tlnp
```

**But :** Vue rapide de tous les services qui écoutent. Utile pour vérifier qu'aucun port inattendu n'est exposé.

**Sortie attendue :** `LISTEN 0 128 127.0.0.1:9050 *:* ... tor`

**Risques :** Aucun risque — lecture seule

**Prérequis :** iproute2 installé

---

### `diag_004` — Services systemd actifs

**Description :** Liste tous les services systemd en cours d'exécution

```bash
systemctl list-units --type=service --state=running --no-pager
```

**But :** Voir tous les services actifs. Permet de confirmer que tor, privoxy, elasticsearch sont dans la liste.

**Sortie attendue :** `tor.service, privoxy.service, etc. avec état 'running'`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd disponible

---

### `diag_005` — Dernières erreurs système

**Description :** Affiche les erreurs récentes dans les journaux système

```bash
journalctl -p err -n 20 --no-pager
```

**But :** Voir les erreurs et alertes récentes dans les logs système. Priorité err = erreurs seulement (sans info/debug).

**Sortie attendue :** `Lignes avec niveau ERROR des dernières heures`

**Risques :** Aucun risque — lecture seule

**Prérequis :** systemd-journald actif

---

### `diag_006` — Utilisation CPU

**Description :** Snapshot de l'utilisation CPU et mémoire

```bash
top -bn1 | head -20
```

**But :** Voir rapidement la charge CPU et les processus les plus gourmands. Utile pour diagnostiquer des ralentissements.

**Sortie attendue :** `Header avec CPU %, puis liste des processus par consommation`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---

### `diag_007` — Tester connectivité DNS

**Description :** Teste la résolution DNS locale

```bash
nslookup localhost 2>/dev/null || host localhost
```

**But :** Vérifier que la résolution DNS locale fonctionne. Un problème DNS peut empêcher Tor de se connecter aux guards.

**Sortie attendue :** `Server: ..., Address: ... Name: localhost, Address: 127.0.0.1`

**Risques :** Aucun risque — requête DNS locale

**Prérequis :** nslookup ou host installé

---

### `diag_008` — Vérifier Python path

**Description :** Affiche le PYTHONPATH et les chemins d'import

```bash
python3 -c "import sys; [print(p) for p in sys.path]"
```

**But :** Voir où Python cherche les modules. Utile pour diagnostiquer des 'ModuleNotFoundError' ou des conflits de versions.

**Sortie attendue :** `Liste de chemins : /usr/lib/python3, site-packages, etc.`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Python 3 installé

---

### `diag_009` — Paquets Python installés

**Description :** Liste tous les paquets Python installés

```bash
pip list 2>/dev/null | grep -iE 'scrapy|twisted|elastic|requests|rich'
```

**But :** Voir les paquets Python pertinents pour le lab (scrapy, elasticsearch-py, rich, etc.) et leurs versions.

**Sortie attendue :** `Scrapy 2.x.x, Twisted X.X.X, rich X.X.X`

**Risques :** Aucun risque — lecture seule

**Prérequis :** pip installé

---

### `diag_010` — Rapport système complet

**Description :** Lance tous les diagnostics essentiels en séquence

```bash
echo '=== SYSTÈME ===' && uname -a && echo '=== RÉSEAU ===' && ip a | grep 'inet ' && echo '=== PORTS ===' && ss -tlnp | head -10 && echo '=== OUTILS ===' && for t in python3 pip tor privoxy scrapy curl jq nc elasticsearch; do command -v $t >/dev/null && echo "✅ $t" || echo "❌ $t"; done
```

**But :** Snapshot complet de l'état du lab en une seule commande : système, réseau, ports ouverts, outils disponibles.

**Sortie attendue :** `Rapport multi-section avec infos système, réseau, ports et disponibilité des outils`

**Risques :** Aucun risque — lecture seule

**Prérequis :** Aucun

---
