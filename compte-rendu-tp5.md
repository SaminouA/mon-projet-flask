# Compte-rendu TP5 — Livraison Continue (CD)
**Usine Logicielle — Master 1 DevOps**
**Sup de Vinci 2025/2026**

---

## Question 1 — Expliquez chaque instruction du Dockerfile. Pourquoi copie-t-on `requirements.txt` avant le code source ?

### Explication de chaque instruction

```dockerfile
FROM python:3.12-slim
```
Définit l'image de base utilisée pour construire le conteneur. On utilise `python:3.12-slim`, une version allégée de Python 3.12 qui ne contient que le strict minimum (pas d'outils de développement inutiles). Cela permet de partir d'un environnement Python propre tout en gardant une image légère.

```dockerfile
WORKDIR /app
```
Définit le répertoire de travail à l'intérieur du conteneur. Toutes les commandes suivantes (`COPY`, `RUN`, `CMD`) s'exécuteront depuis ce dossier `/app`. Si le dossier n'existe pas, Docker le crée automatiquement.

```dockerfile
COPY requirements.txt .
```
Copie uniquement le fichier `requirements.txt` depuis la machine hôte vers le répertoire de travail du conteneur (`.` = `/app`). On copie ce fichier **en premier**, avant le code source, pour une raison précise liée au cache Docker (expliquée ci-dessous).

```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
Installe toutes les dépendances listées dans `requirements.txt`. L'option `--no-cache-dir` évite de stocker le cache de pip dans l'image, ce qui réduit la taille finale de l'image Docker.

```dockerfile
COPY src/ ./src/
```
Copie le code source de l'application (le dossier `src/`) dans le conteneur. On le copie **après** les dépendances pour optimiser le cache Docker.

```dockerfile
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
```
Installe `curl` dans le conteneur via le gestionnaire de paquets Linux. `curl` est nécessaire pour que le HEALTHCHECK puisse effectuer des requêtes HTTP. Le `rm -rf /var/lib/apt/lists/*` supprime les listes de paquets après installation pour réduire la taille de l'image.

```dockerfile
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1
```
Configure une vérification automatique de l'état de l'application. Docker vérifie toutes les 30 secondes que l'application répond bien sur la route `/health`. Si elle ne répond pas après 3 tentatives (avec un timeout de 5 secondes chacune), le conteneur passe en état `unhealthy`. C'est essentiel en production pour détecter automatiquement les pannes.

```dockerfile
EXPOSE 5000
```
Documente que le conteneur écoute sur le port 5000. C'est une déclaration informative — elle n'ouvre pas réellement le port. L'ouverture du port se fait lors du `docker run` avec l'option `-p`.

```dockerfile
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
```
Définit la commande exécutée au démarrage du conteneur. On utilise **Gunicorn**, un serveur WSGI de production, pour lancer l'application Flask. `0.0.0.0:5000` signifie que le serveur écoute sur toutes les interfaces réseau du conteneur sur le port 5000.

### Pourquoi copier `requirements.txt` avant le code source ?

Docker construit les images par **couches** (layers). Chaque instruction du Dockerfile crée une nouvelle couche. Docker met en **cache** ces couches : si une couche n'a pas changé depuis le dernier build, Docker la réutilise directement sans la reconstruire.

En copiant `requirements.txt` avant le code source :
- Si seul le code source change (modification d'un fichier `.py`), les couches `COPY requirements.txt` et `RUN pip install` sont récupérées depuis le cache → **pip install n'est pas relancé**.
- Si on copiait tout le code d'abord, le moindre changement dans un fichier `.py` invaliderait le cache et forcerait une réinstallation complète de toutes les dépendances → **beaucoup plus lent**.

Cette optimisation peut faire passer le temps de build de plusieurs minutes à quelques secondes lors des modifications courantes du code.

---

## Question 2 — Quelle est la différence entre une VM et un container Docker ? Quel est l'avantage principal des containers ?

### Machine Virtuelle (VM)

Une machine virtuelle émule un **ordinateur complet**. Elle contient :
- Un système d'exploitation invité complet (noyau, pilotes, services...)
- Un hyperviseur (VirtualBox, VMware, Hyper-V) qui fait l'interface entre la VM et le matériel physique

Chaque VM est totalement isolée et occupe plusieurs gigaoctets sur le disque. Le démarrage prend plusieurs minutes car il faut booter un OS entier.

### Container Docker

Un container Docker ne virtualise **pas un OS complet**. Il partage le noyau (kernel) du système hôte et isole uniquement l'application et ses dépendances dans un espace de noms (namespace) séparé. Il est donc beaucoup plus léger et démarre en quelques secondes.

### Comparaison

| Critère | Machine Virtuelle | Container Docker |
|---|---|---|
| Taille | Plusieurs Go | Quelques Mo à quelques centaines de Mo |
| Démarrage | Plusieurs minutes | Quelques secondes |
| Isolation | OS complet | Processus isolé (namespace) |
| Performance | Plus lente (overhead hyperviseur) | Proche du natif |
| Portabilité | Moins portable (image lourde) | Très portable |
| Ressources | Consomme beaucoup de RAM/CPU | Léger en ressources |

### Avantage principal des containers

L'avantage principal est la **portabilité**. Un container fonctionne de façon **identique** sur n'importe quelle machine disposant de Docker : PC de développement, serveur Linux, cloud AWS, GCP, Azure... Le célèbre problème "ça marche sur ma machine" disparaît, car l'environnement d'exécution est entièrement encapsulé dans le container.

---

## Question 3 — Quel est l'intérêt de Docker Compose par rapport à un simple `docker run` ? Dans quel cas Docker Compose devient-il indispensable ?

### Limites de `docker run`

La commande `docker run` permet de lancer un seul conteneur, mais nécessite de spécifier manuellement toute la configuration à chaque fois :

```bash
docker run -d -p 5000:5000 \
  -e FLASK_ENV=development \
  -e SECRET_KEY=dev-key \
  -v ./src:/app/src \
  --name mon-app \
  mon-flask-app
```

Cette commande est longue, difficile à mémoriser, non partageable facilement avec l'équipe, et ne gère pas les dépendances entre services.

### Avantages de Docker Compose

Docker Compose permet de décrire toute la configuration dans un fichier `docker-compose.yml` versionné avec le code. Une seule commande suffit ensuite :

```bash
docker compose up --build
```

Avantages :
- **Configuration centralisée** dans un fichier lisible et versionné
- **Réseau automatique** entre les services (ils peuvent se parler par leur nom)
- **Reproductible** : tout le monde lance exactement le même environnement
- **Gestion des dépendances** entre services (un service attend qu'un autre soit prêt)
- **Commandes simples** : `up`, `down`, `logs`, `ps`

### Cas où Docker Compose devient indispensable

Docker Compose devient indispensable dès que l'application nécessite **plusieurs services** qui doivent communiquer entre eux, par exemple :

- Application Flask + base de données PostgreSQL
- Application Flask + cache Redis
- Application Flask + file de messages RabbitMQ + worker Celery
- Microservices avec plusieurs APIs interdépendantes

Dans ces cas, gérer chaque conteneur manuellement avec `docker run` serait extrêmement complexe et source d'erreurs.

---

## Question 4 — Pourquoi tagger une image avec plusieurs tags ? Pourquoi ne doit-on pas utiliser `:latest` en production ?

### Intérêt de plusieurs tags

Chaque tag a un rôle différent et complémentaire :

| Tag | Exemple | Rôle |
|---|---|---|
| SHA du commit | `sha-f0f2bd8` | Traçabilité parfaite vers un commit Git précis |
| Version sémantique | `v1.0.0` | Lisible par un humain, utile pour les releases |
| `latest` | `latest` | Pointe vers la dernière image, pratique en développement |

En combinant ces tags, on obtient :
- La **traçabilité** (quel commit a produit cette image ?)
- La **lisibilité** (quelle version fonctionnelle est déployée ?)
- La **commodité** (toujours accéder à la dernière version facilement)

### Pourquoi éviter `:latest` en production ?

Le tag `:latest` est **dangereux en production** pour plusieurs raisons :

1. **Il change à chaque build** : deux serveurs qui pullent `:latest` à des moments différents peuvent récupérer des versions différentes de l'image, créant des incohérences dans l'infrastructure.

2. **Pas de traçabilité** : impossible de savoir quelle version exacte tourne en production si on utilise `:latest`.

3. **Rollback impossible** : si un bug est introduit, on ne peut pas facilement identifier quelle version précédente relancer.

4. **Reproductibilité nulle** : un déploiement avec `:latest` aujourd'hui peut donner un résultat différent que le même déploiement dans 3 mois.

En production, on utilise toujours un tag précis comme `sha-f0f2bd8` ou `v1.2.3` pour garantir la **reproductibilité** et la **traçabilité**.

---

## Question 5 — Qu'est-ce qu'un registre de conteneurs ? Comparez ghcr.io, Docker Hub et Google Artifact Registry.

### Définition

Un **registre de conteneurs** (container registry) est un service de stockage et de distribution d'images Docker. C'est l'équivalent de GitHub mais pour les images Docker. On y **pousse** (`docker push`) des images depuis une CI/CD et on les **tire** (`docker pull`) pour les déployer sur des serveurs.

### Comparaison

| Critère | **ghcr.io** | **Docker Hub** | **Google Artifact Registry** |
|---|---|---|---|
| Propriétaire | GitHub (Microsoft) | Docker Inc. | Google Cloud |
| Gratuit | Oui (images publiques et privées) | Oui (limité : 1 image privée) | Payant (à l'usage) |
| Intégration native | GitHub Actions | Universel | GCP (Cloud Run, GKE, Cloud Build) |
| Authentification | GITHUB_TOKEN automatique | Docker login manuel | Service Account GCP |
| Usage typique | Projets hébergés sur GitHub | Images publiques open source | Entreprises sur Google Cloud |
| Limite de bande passante | Généreuse | Limitée sans compte payant | Illimitée (payant) |

### Pourquoi utilise-t-on ghcr.io dans ce TP ?

On utilise **ghcr.io** car notre code est hébergé sur GitHub. L'authentification est automatique grâce au `GITHUB_TOKEN` fourni par GitHub Actions — pas besoin de créer de secret manuellement. C'est la solution la plus simple et gratuite pour un projet sur GitHub.

---

## Question 6 — Pourquoi teste-t-on le conteneur dans la CI avant de le pousser sur le registre ?

Tester le conteneur dans la CI avant de le pousser sur le registre est une étape de **validation essentielle** pour plusieurs raisons :

1. **Le build ne garantit pas le fonctionnement** : une image peut se builder sans erreur mais échouer au démarrage (mauvaise configuration gunicorn, variable d'environnement manquante, erreur d'import Python...).

2. **Garantir la qualité du registre** : le registre doit ne contenir que des images **fonctionnelles**. Si on pousse des images cassées, les équipes qui les pullent pour déployer auront des problèmes en production.

3. **Détection précoce** : mieux vaut détecter qu'une image ne démarre pas dans la CI (en quelques secondes) plutôt qu'en production (avec impact utilisateur).

4. **Le test est simple et efficace** : on lance le conteneur, on attend 5 secondes, et on vérifie que `/health` répond avec un code HTTP 200. C'est un **smoke test** minimal mais suffisant pour valider que l'application démarre correctement.

```yaml
- name: Tester le conteneur
  run: |
    docker run -d -p 5000:5000 --name test-container $IMAGE:${{ github.sha }}
    sleep 5
    curl -f http://localhost:5000/health
    docker stop test-container
```

---

## Question 7 — Expliquez la condition `if: github.ref == 'refs/heads/main'`. Pourquoi le build Docker ne se déclenche-t-il pas sur les Pull Requests ?

### Explication de la condition

```yaml
if: github.ref == 'refs/heads/main' && github.event_name == 'push'
```

Cette condition vérifie **deux critères simultanément** :

- `github.ref == 'refs/heads/main'` : le déclencheur concerne bien la branche `main` (et non une branche de feature ou de fix).
- `github.event_name == 'push'` : l'événement est un push direct, et non une Pull Request.

### Pourquoi ne pas déclencher sur les Pull Requests ?

Sur une **Pull Request**, le code est en cours de révision et n'a pas encore été approuvé par l'équipe. Déclencher un build Docker sur chaque PR causerait plusieurs problèmes :

1. **Pollution du registre** : des dizaines d'images non finalisées s'accumuleraient sur ghcr.io pour chaque branche de travail.

2. **Gaspillage de ressources** : builder et pusher une image prend du temps et de la bande passante pour du code qui n'est peut-être pas prêt.

3. **Confusion** : il serait difficile de savoir quelles images sont "officielles" (issues de main) et lesquelles sont des images de travail temporaires.

4. **Sécurité** : publier des images issues de branches non relues pourrait exposer du code non audité.

En résumé : on ne publie sur le registre que le code **validé, relu et mergé** sur la branche principale.

---

## Question 8 — Pourquoi utilise-t-on `github.sha` comme tag d'image ? Quel avantage par rapport à un numéro de version manuel ?

### Qu'est-ce que `github.sha` ?

`github.sha` est le **hash SHA-1 complet du commit Git** qui a déclenché le pipeline (ex: `f0f2bd80d675ea3ace665b31c59e83af7aa41c23`). On l'utilise comme tag d'image Docker pour créer un lien direct entre l'image et le commit dont elle est issue.

### Avantages par rapport à un numéro de version manuel

| Critère | `github.sha` | Version manuelle (v1.0.0) |
|---|---|---|
| Automatique | ✅ Généré par Git | ❌ Doit être incrémenté manuellement |
| Unicité | ✅ Impossible d'avoir deux commits identiques | ⚠️ Risque d'oublier d'incrémenter |
| Traçabilité | ✅ Lien direct vers le commit exact | ❌ Nécessite un changelog séparé |
| Erreur humaine | ✅ Impossible | ❌ On peut oublier ou se tromper |
| Lisibilité | ❌ Peu lisible (`f0f2bd8`) | ✅ Lisible (`v1.2.3`) |

C'est pourquoi on combine les deux dans ce TP :
- `sha-f0f2bd8` pour la traçabilité automatique
- `v1.0.0` pour la lisibilité humaine lors des releases importantes

---

## Question 9 — Qu'est-ce qu'un rollback ? Pourquoi est-il essentiel de versionner les images Docker avec des tags précis ?

### Définition du rollback

Un **rollback** consiste à revenir à une version précédente et fonctionnelle d'une application, après qu'une nouvelle version a introduit un bug, une régression ou une panne en production.

Avec Docker et des tags précis, le rollback est **immédiat et fiable** :

```bash
# La nouvelle version v1.2 a un bug, on revient à v1.1
docker pull ghcr.io/saminoua/mon-projet-flask:sha-abc1234
docker run -d -p 5000:5000 ghcr.io/saminoua/mon-projet-flask:sha-abc1234
```

### Pourquoi versionner avec des tags précis ?

Sans tags précis, le rollback devient **impossible ou très risqué** :

1. **Avec uniquement `:latest`** : on ne sait pas quelle version correspond à quel état du code. Impossible de revenir en arrière de façon fiable.

2. **Avec des tags SHA** : chaque image est liée à un commit Git précis. On peut voir dans GitHub Actions exactement quelle image correspond à quel code, et relancer n'importe quelle version passée en quelques secondes.

3. **Audit et conformité** : en production, il est souvent obligatoire de pouvoir justifier exactement quelle version du code tourne sur les serveurs. Les tags SHA le permettent.

Le rollback est une **bouée de sauvetage** en production. Il doit être possible en quelques secondes, sans stress. C'est pour cela que la gestion rigoureuse des tags est une pratique DevOps fondamentale.

---

## Question 10 — Expliquez la différence entre Continuous Delivery et Continuous Deployment. Lequel avez-vous mis en place ?

### Continuous Delivery (Livraison Continue)

Le **Continuous Delivery** garantit que le code est **toujours dans un état déployable**. Chaque changement passe automatiquement par le pipeline (tests, build, publication), mais le **déploiement en production nécessite une validation humaine** (un clic ou une approbation).

```
Code → Tests → Build → Publication sur registre → [Validation humaine] → Déploiement
```

### Continuous Deployment (Déploiement Continu)

Le **Continuous Deployment** va un cran plus loin : chaque changement validé par les tests est **automatiquement déployé en production**, sans aucune intervention humaine.

```
Code → Tests → Build → Publication sur registre → Déploiement automatique en production
```

### Comparaison

| Critère | Continuous Delivery | Continuous Deployment |
|---|---|---|
| Déploiement en prod | Manuel (validation humaine) | Automatique |
| Risque | Plus faible | Plus élevé |
| Vitesse | Plus lente | Plus rapide |
| Contrôle | Total | Limité |
| Usage | Contextes critiques (banque, santé) | Startups, applications web |

### Ce qu'on a mis en place dans ce TP

On a mis en place du **Continuous Delivery**. Notre pipeline :
1. Exécute les tests et l'analyse de qualité automatiquement
2. Builde et publie l'image Docker sur ghcr.io automatiquement
3. Mais le **déploiement sur un vrai serveur de production reste manuel**

Pour passer au Continuous Deployment, il faudrait ajouter une étape dans le pipeline qui déploie automatiquement l'image sur un serveur (ex: via `gcloud run deploy` sur GCP Cloud Run).

---

## Question 11 — Quels risques pose le déploiement automatique ? Comment les atténuer ?

### Risques du déploiement automatique

1. **Bug en production** : un bug non détecté par les tests peut être déployé automatiquement et impacter les utilisateurs sans qu'un humain ait eu l'occasion de le repérer.

2. **Faille de sécurité** : une vulnérabilité introduite dans le code peut être déployée avant qu'un audit de sécurité soit effectué.

3. **Régression de performance** : une modification qui ralentit l'application peut passer les tests fonctionnels mais dégrader l'expérience utilisateur.

4. **Dépendances cassées** : une mise à jour automatique d'une dépendance peut introduire des incompatibilités non couvertes par les tests.

5. **Rollback en urgence** : si un problème est détecté en production, l'équipe doit réagir rapidement, parfois en dehors des heures de travail.

### Comment atténuer ces risques ?

| Stratégie | Description |
|---|---|
| **Couverture de tests élevée** | Viser 80-90% de couverture, avec des tests unitaires, d'intégration et end-to-end |
| **Feature flags** | Activer/désactiver des fonctionnalités sans redéployer, permettant de tester en production sur un sous-ensemble d'utilisateurs |
| **Canary release** | Déployer la nouvelle version sur 5-10% du trafic d'abord, surveiller, puis étendre progressivement |
| **Blue/Green deployment** | Maintenir deux environnements identiques, basculer le trafic de l'un à l'autre instantanément |
| **Monitoring et alertes** | Surveiller les métriques (taux d'erreur, latence) et alerter automatiquement en cas d'anomalie |
| **Rollback automatique** | Configurer un rollback automatique si les métriques de santé se dégradent après un déploiement |
| **Tests de smoke en production** | Exécuter des tests basiques automatiquement après chaque déploiement pour valider que l'app répond |

---

## Question 12 — Expliquez le principe du multi-stage build. Avantages en taille et sécurité. Dockerfile modifié et différence de taille.

### Principe du multi-stage build

Le **multi-stage build** permet d'utiliser **plusieurs instructions `FROM`** dans un seul Dockerfile. Chaque `FROM` démarre un nouveau stage avec sa propre image de base. On peut ensuite copier sélectivement des fichiers d'un stage à l'autre avec `COPY --from=`.

L'idée fondamentale est de **séparer l'environnement de build de l'environnement d'exécution** :
- **Stage builder** : image complète avec tous les outils nécessaires pour compiler/installer les dépendances
- **Stage final** : image minimale qui ne contient que ce qui est nécessaire pour faire tourner l'application

### Dockerfile modifié avec multi-stage build

```dockerfile
# Stage 1 : builder - installe les dependances
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2 : image finale ultra-legere
FROM python:3.12-alpine

WORKDIR /app

# Copier uniquement les dependances installees depuis le builder
COPY --from=builder /install /usr/local

# Copier le code source
COPY src/ ./src/

# Installer curl pour le health check
RUN apk add --no-cache curl

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
```

### Différence de taille

| Image | Taille non compressée | Taille compressée (registre) |
|---|---|---|
| Image originale (`python:3.12-slim`) | 813 MB | ~143 MB |
| Image multi-stage (`python:3.12-alpine`) | ~100-150 MB | ~50 MB |

### Avantages en taille

L'image finale ne contient pas :
- Les outils de build (gcc, make, compilateurs)
- Le cache pip
- Les headers de développement
- Les fichiers temporaires d'installation

### Avantages en sécurité

- **Moins de surface d'attaque** : moins de packages installés = moins de vulnérabilités potentielles
- **Pas d'outils de build en production** : un attaquant qui compromet le conteneur n'a pas accès aux compilateurs ou outils système
- **Image auditée** : il est plus facile de vérifier le contenu d'une image minimale
- **CVE réduites** : moins de dépendances = moins de vulnérabilités connues (CVE) à gérer

### Documentation consultée

[https://docs.docker.com/build/building/multi-stage/](https://docs.docker.com/build/building/multi-stage/)

---

*Compte-rendu rédigé dans le cadre du TP5 — Livraison Continue, Usine Logicielle M1 DevOps, Sup de Vinci 2025/2026*
