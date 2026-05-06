# Compte Rendu TP6 — Gestion des Artefacts
**Usine Logicielle — Master 1 DevOps**
**Sup de Vinci 2025/2026**
**Nom : Nadira**



## Questions

### Question 1 — Qu'est-ce qu'un artefact dans le contexte d'une usine logicielle ? Donnez 3 exemples.

**Définition :**

Dans le contexte d'une usine logicielle (pipeline CI/CD), un **artefact** est un
**livrable immutable produit par le pipeline**, résultat de la transformation du code
source. Un artefact est versionnée, traçable et peut être réutilisé dans des étapes
ultérieures du pipeline (tests, déploiement...) sans être reconstruit.

Le mot "immutable" est essentiel : une fois produit et publié, un artefact ne doit
jamais être modifié. Si une correction est nécessaire, on produit un nouvel artefact
avec un nouveau numéro de version.

**3 exemples d'artefacts :**

1. **Image Docker** : le résultat du `docker build` à partir du Dockerfile et du code
   source. L'image est publiée sur un registre (ghcr.io, Artifact Registry) et taggée
   avec un SHA ou un numéro de version. C'est l'artefact principal de ce TP — il peut
   être déployé sur n'importe quel environnement (staging, production) sans recompilation.

2. **Rapport de couverture de code** : le fichier HTML généré par `pytest-cov` après
   l'exécution des tests. C'est un artefact de CI sauvegardé dans GitHub Actions
   (via `upload-artifact`) pour être consulté par l'équipe après chaque run. Il n'est
   pas déployé mais sert à l'audit de qualité.

3. **Package Python (.whl ou .tar.gz)** : dans un projet de bibliothèque Python,
   le pipeline produit un package distributable publié sur PyPI. Ce package est
   versionné avec SemVer et peut être installé par d'autres projets via `pip install`.
   Exemples : Flask, pytest, requests sont tous des artefacts publiés sur PyPI.

---

### Question 2 — Pourquoi tagger une image avec plusieurs tags ? Dans quel cas utilise-t-on chacun ?

Tagger une image avec plusieurs tags permet de répondre à des besoins différents
selon le contexte d'utilisation. Chaque tag a un rôle précis :

**SHA complet (40 caractères)**
```
ghcr.io/saminoua/mon-projet-flask:f0f2bd80d675ea3ace665b31c59e83af7aa41c23
```
- **Usage** : traçabilité absolue et automatisation
- **Avantage** : lien direct et unique vers le commit exact. Utilisé dans les systèmes
  automatisés (orchestrateurs, scripts de déploiement) où la précision est critique.
- **Inconvénient** : illisible pour un humain

**SHA court (7 caractères)**
```
ghcr.io/saminoua/mon-projet-flask:sha-f0f2bd8
```
- **Usage** : traçabilité lisible par un humain
- **Avantage** : format identique à `git log --oneline`, facile à copier-coller et à
  référencer dans les discussions d'équipe ou les tickets
- **Inconvénient** : théoriquement, deux commits différents peuvent avoir le même
  SHA court (collision rare mais possible sur de très grands projets)

**Tag de version SemVer (v1.2.3)**
```
ghcr.io/saminoua/mon-projet-flask:v1.1.0
```
- **Usage** : déploiements en production et rollback
- **Avantage** : communique clairement le niveau de changement (MAJOR/MINOR/PATCH),
  facilite les décisions de déploiement et la communication avec les parties prenantes
- **Inconvénient** : nécessite un processus de versioning discipliné

**`latest`**
```
ghcr.io/saminoua/mon-projet-flask:latest
```
- **Usage** : développement local et environnements de test
- **Avantage** : toujours à jour, pratique pour `docker pull` rapide en développement
- **Inconvénient** : dangereux en production car il change à chaque build. Deux
  serveurs pullant `latest` à des moments différents peuvent obtenir des versions
  différentes, créant des incohérences.

**Résumé :**

| Tag | Environnement | Usage principal |
|---|---|---|
| SHA complet | CI/CD automatisé | Traçabilité absolue |
| SHA court | Équipe dev | Référence lisible |
| v1.2.3 | Production | Déploiement versionné |
| latest | Dev / Test | Accès rapide à la dernière version |

---

### Question 3 — Expliquez le versioning sémantique (SemVer). MAJOR, MINOR ou PATCH pour chaque cas ?

**Versioning Sémantique (SemVer) :**

Le versioning sémantique est une convention de nommage des versions au format
`MAJOR.MINOR.PATCH` (exemple : `v1.4.2`). Chaque composant a une signification précise
qui communique le type de changement introduit :

```
v  1  .  4  .  2
   │     │     └── PATCH : correction de bug, pas de nouvelle fonctionnalité
   │     └──────── MINOR : nouvelle fonctionnalité rétrocompatible
   └────────────── MAJOR : changement incompatible avec les versions précédentes
```

**Règles :**
- On incrémente **PATCH** pour une correction de bug rétrocompatible
- On incrémente **MINOR** et remet PATCH à 0 pour une nouvelle fonctionnalité rétrocompatible
- On incrémente **MAJOR** et remet MINOR et PATCH à 0 pour un changement incompatible
- `v0.x.x` = version en développement, l'API peut changer librement
- `v1.0.0` = première version stable publique

**Cas demandés :**

1. **Ajout d'une route `/version`** → **MINOR** (`v1.0.0` → `v1.1.0`)
   Ajouter une nouvelle route est une nouvelle fonctionnalité. Les clients existants
   continuent de fonctionner sans modification (rétrocompatible). On incrémente MINOR.

2. **Correction d'un bug** → **PATCH** (`v1.1.0` → `v1.1.1`)
   Corriger un bug existant sans ajouter de fonctionnalité ni casser l'API existante.
   Dans ce TP, l'amélioration du test de `/version` est un PATCH.

3. **Changement du format de réponse JSON** → **MAJOR** (`v1.1.1` → `v2.0.0`)
   Changer le format de réponse JSON (ex: renommer `"message"` en `"data"`) est un
   changement **incompatible** — les clients qui parsent l'ancienne réponse vont casser.
   On incrémente MAJOR pour signaler ce breaking change.

---

### Question 4 — Quelle est la différence entre un tag Git léger et un tag annoté ?

**Tag léger (`git tag v1.0`) :**

Un tag léger est simplement un **pointeur vers un commit**, comme une branche qui ne
bouge pas. Il ne contient aucune information supplémentaire — juste le nom du tag et
le hash du commit pointé.

```bash
git tag v1.0           # crée un tag léger sur le commit courant
git tag v1.0 abc1234   # crée un tag léger sur un commit spécifique
```

Caractéristiques :
- Pas de message, pas d'auteur, pas de date propre au tag
- Stocké comme un simple fichier dans `.git/refs/tags/`
- Ne peut pas être signé cryptographiquement
- Usage : marqueurs temporaires, tags personnels locaux

**Tag annoté (`git tag -a v1.0.0 -m "..."`) :**

Un tag annoté est un **objet Git complet** avec ses propres métadonnées : auteur,
date de création, message et optionnellement une signature GPG.

```bash
git tag -a v1.0.0 -m "Version 1.0.0 - première release stable"
```

Caractéristiques :
- Contient : nom de l'auteur, email, date, message
- Peut être signé avec GPG pour garantir l'authenticité
- Visible avec `git show v1.0.0` (affiche les métadonnées complètes)
- Recommandé pour les releases officielles

**Comparaison :**

| Critère | Tag léger | Tag annoté |
|---|---|---|
| Métadonnées | Non | Oui (auteur, date, message) |
| Signature GPG | Non | Oui |
| `git show` | Affiche le commit | Affiche tag + commit |
| Usage | Temporaire/local | Releases officielles |
| Commande | `git tag v1.0` | `git tag -a v1.0 -m "..."` |

**Bonne pratique :** toujours utiliser des tags annotés pour les releases officielles
(v1.0.0, v2.3.1...) car ils contiennent les métadonnées nécessaires pour l'audit
et sont mieux supportés par les outils comme GitHub Releases et release-please.

---

### Question 5 — Comment release-please détermine-t-il le numéro de version ? Quel est le lien avec les Conventional Commits ?

**Fonctionnement de release-please :**

release-please analyse l'historique des commits depuis la dernière release et
détermine automatiquement le prochain numéro de version en lisant les **préfixes
des Conventional Commits**.

**Mapping Conventional Commits → SemVer :**

| Préfixe de commit | Type de changement SemVer |
|---|---|
| `feat:` | MINOR (nouvelle fonctionnalité) |
| `fix:` | PATCH (correction de bug) |
| `docs:`, `chore:`, `ci:`, `test:`, `refactor:` | PATCH ou aucun changement |
| `feat!:` ou `BREAKING CHANGE:` | MAJOR (changement incompatible) |

**Exemple concret :**

Si depuis la dernière release `v1.0.0`, on a les commits suivants :
```
feat: ajout route /version      → MINOR
fix: correction test             → PATCH
docs: mise à jour README         → (ignoré)
feat: ajout route /stats         → MINOR
```
release-please déterminera que la prochaine version est **v1.1.0** (car il y a au
moins un `feat:`, on incrémente MINOR).

**Processus complet :**

1. À chaque push sur `main`, release-please analyse les nouveaux commits
2. Il calcule le prochain numéro de version selon les règles SemVer
3. Il crée (ou met à jour) une PR intitulée `chore(main): release v1.1.0`
4. Cette PR contient : la mise à jour de la version dans `pyproject.toml` et un
   `CHANGELOG.md` généré automatiquement
5. Quand on merge cette PR, release-please crée le tag Git et la GitHub Release

**Lien avec les Conventional Commits :**

Les Conventional Commits sont la **base du versioning automatique**. Sans ces
conventions de nommage (`feat:`, `fix:`...), release-please ne peut pas déterminer
le type de changement et donc le numéro de version. C'est pourquoi il est essentiel
que toute l'équipe respecte ces conventions dans ses messages de commit.

---

### Question 6 — Quel est l'avantage d'automatiser les releases plutôt que de les créer manuellement ?

**Problèmes des releases manuelles :**

1. **Oubli et inconsistance** : un développeur peut oublier de créer une release,
   de mettre à jour le numéro de version dans les fichiers, ou de rédiger le changelog.
2. **Changelog incomplet** : écrire manuellement la liste des changements est
   fastidieux et souvent incomplet ou inexact.
3. **Erreurs humaines** : erreur dans le numéro de version (MINOR au lieu de MAJOR),
   tag mal formé, mauvaise branche...
4. **Délai** : les releases manuelles sont souvent retardées car personne ne prend
   l'initiative ou n'a le temps.

**Avantages de l'automatisation avec release-please :**

1. **Cohérence garantie** : chaque release suit exactement le même processus, avec
   les mêmes fichiers mis à jour, le même format de changelog.

2. **Changelog automatique et exhaustif** : tous les commits `feat:` et `fix:` depuis
   la dernière release sont listés dans le `CHANGELOG.md`, rien n'est oublié.

3. **Versioning correct** : le numéro de version est calculé automatiquement selon
   les règles SemVer à partir des commits. Plus de risque d'erreur humaine.

4. **Traçabilité** : chaque release est liée à un ensemble précis de commits, un tag
   Git et une GitHub Release. La traçabilité est parfaite.

5. **Économie de temps** : les développeurs se concentrent sur le code, pas sur la
   gestion administrative des releases.

6. **Déclencheur de déploiement** : la release peut automatiquement déclencher le
   déploiement en production (comme dans ce TP avec `release_created`), créant un
   pipeline complet de commit au déploiement.

---

### Question 7 — Décrivez le pipeline de release complet, du commit au déploiement. Combien de workflows sont impliqués ?

**Deux workflows sont impliqués :**

**Workflow 1 : `ci.yml` — Intégration Continue**
- **Déclencheur** : push sur `main` ou Pull Request
- **Rôle** : vérifier la qualité et la sécurité du code
- **Étapes** : GitLeaks → Black → Ruff → pip-audit → Bandit → Semgrep → Tests

**Workflow 2 : `release.yml` — Release et Déploiement**
- **Déclencheur** : push sur `main`
- **Rôle** : créer les releases versionnées et déployer en production
- **Étapes** : release-please → (si release créée) Build Docker → Push → Deploy Cloud Run

**Pipeline complet du commit au déploiement :**

```
1. Le développeur fait un commit feat: ajout fonctionnalité X
   ↓
2. git push origin main
   ↓
3. [ci.yml] Déclenchement de la CI
   → GitLeaks, Black, Ruff, pip-audit, Bandit, Semgrep, Tests
   → Si tout passe : ✅
   ↓
4. [release.yml] release-please analyse les nouveaux commits
   → Détecte feat: → incrémente MINOR
   → Crée/met à jour la PR "chore(main): release v1.1.0"
   ↓
5. L'équipe relit et merge la PR de release
   ↓
6. release-please crée automatiquement :
   → Le tag Git v1.1.0
   → La GitHub Release avec changelog
   ↓
7. [release.yml - job deploy-release] Déclenché par release_created=true
   → Build de l'image Docker taggée v1.1.0 et latest
   → Push sur Artifact Registry
   → Déploiement sur Cloud Run avec l'image v1.1.0
   ↓
8. L'application v1.1.0 est en production ✅
```

---

### Question 8 — Différence entre déployer avec github.sha (TP5) et un tag SemVer (TP6) ?

**Déploiement avec `github.sha` (TP5) :**

```yaml
image: flask-app:f0f2bd80d675ea3ace665b31c59e83af7aa41c23
```

- **Fréquence** : chaque push sur `main` déclenche un déploiement
- **Traçabilité** : lien direct vers un commit, mais numéro illisible
- **Communication** : difficile de dire "on est en prod sur le SHA f0f2bd8"
- **Usage** : déploiement continu (Continuous Deployment), environnements de staging
- **Rollback** : possible mais nécessite de connaître le SHA de la version précédente

**Déploiement avec tag SemVer (TP6) :**

```yaml
image: flask-app:v1.1.0
```

- **Fréquence** : uniquement lors d'une release officielle (moins fréquent)
- **Traçabilité** : numéro de version lisible et significatif
- **Communication** : "on est en prod sur la v1.1.0" est clair pour tout le monde
- **Usage** : production, livraison à des clients, releases officielles
- **Rollback** : très simple — `docker pull flask-app:v1.0.0` et redéploiement

**Quand utiliser chacun :**

| Contexte | Approche recommandée |
|---|---|
| Staging / pre-production | SHA (déploiement continu) |
| Production avec clients | SemVer (releases contrôlées) |
| Débogage d'un bug précis | SHA (traçabilité exacte) |
| Communication externe | SemVer (lisible et compréhensible) |
| Rollback d'urgence | SemVer (version précédente claire) |

---

### Question 9 — Pourquoi le principe d'immutabilité des artefacts est-il important ? Que se passe-t-il si on écrase un tag Docker existant ?

**Principe d'immutabilité :**

Un artefact **immutable** est un artefact qui, une fois créé et publié, **ne peut jamais
être modifié**. Si une correction est nécessaire, on crée un nouvel artefact avec un
nouveau numéro de version. On ne modifie jamais l'artefact existant.

**Pourquoi c'est essentiel :**

1. **Reproductibilité** : si l'image `v1.0.0` est immuable, on est certain que
   redéployer `v1.0.0` dans 6 mois donnera exactement le même résultat qu'aujourd'hui.
   Si on pouvait modifier les artefacts, cette garantie disparaît.

2. **Rollback fiable** : en cas de problème en production, on peut revenir à `v1.0.0`
   en étant certain de retrouver l'état exact qu'on avait lors du déploiement initial.

3. **Audit et conformité** : dans des contextes réglementés (finance, santé...), il est
   obligatoire de pouvoir prouver exactement quel code était en production à une date
   donnée. L'immutabilité le garantit.

4. **Confiance dans le pipeline** : si les artefacts peuvent être modifiés après leur
   création, les équipes ne peuvent plus faire confiance au processus de déploiement.

**Que se passe-t-il si on écrase un tag Docker existant :**

Écraser un tag existant (ex: repusher une nouvelle image sur `v1.0.0`) est extrêmement
dangereux :

1. **Incohérence silencieuse** : les serveurs qui ont déjà pullé `v1.0.0` ont l'ancienne
   image en cache. Les nouveaux serveurs qui pullent `v1.0.0` obtiennent la nouvelle.
   L'infrastructure tourne des versions différentes sans que personne ne le sache.

2. **Rollback impossible** : si on a besoin de revenir à `v1.0.0`, on obtient la version
   écrasée, pas l'originale. Le rollback ne restaure pas l'état attendu.

3. **Audit cassé** : on ne peut plus prouver quel code correspond à `v1.0.0`.

4. **Bonne pratique** : si un bug est découvert en `v1.0.0`, on crée `v1.0.1` avec la
   correction. On ne modifie jamais `v1.0.0`.

---

### Question 10 — Analysez les 5 dernières releases du projet Flask sur GitHub.

**Projet analysé : Flask**

**Lien** : https://github.com/pallets/flask/releases

**Analyse des 5 dernières releases :**

| Version | Type SemVer | Type de changements |
|---|---|---|
| 3.1.1 | PATCH | Corrections de bugs, améliorations mineures |
| 3.1.0 | MINOR | Nouvelles fonctionnalités rétrocompatibles |
| 3.0.3 | PATCH | Corrections de sécurité et bugs |
| 3.0.2 | PATCH | Corrections de bugs |
| 3.0.1 | PATCH | Corrections de bugs post-release |

**Le changelog est-il automatisé ou manuel ?**

Le changelog de Flask est **semi-automatisé**. Le projet utilise un fichier `CHANGES.rst`
maintenu manuellement par les mainteneurs, mais le processus de release est automatisé
via des scripts et GitHub Actions. Les releases GitHub sont générées automatiquement
à partir des tags Git.

**Les tags suivent-ils SemVer ?**

Oui, Flask suit strictement SemVer avec le format `X.Y.Z`. Les tags sont annotés
et correspondent aux releases GitHub.

**Outils utilisés :**

Flask (projet Pallets) utilise :
- **`towncrier`** : outil de génération de changelog à partir de "news fragments"
- **GitHub Actions** pour l'automatisation de la publication sur PyPI
- **Tags Git annotés** pour marquer chaque release

La différence avec notre approche est que Flask utilise `towncrier` (fragments de
changelog écrits manuellement par les développeurs) plutôt que release-please
(génération automatique depuis les messages de commit). Cette approche donne un
changelog plus soigné mais nécessite plus d'effort humain.

---

## Lien du projet

https://github.com/SaminouA/mon-projet-flask
