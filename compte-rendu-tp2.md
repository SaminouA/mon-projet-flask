# Compte Rendu TP2 — Intégration Continue avec GitHub Actions
**Usine Logicielle — Master 1 DevOps**
**Sup de Vinci 2025/2026**
**Nom : Nadira**



## Questions

### Question 1 — Décrivez la structure du fichier ci.yml : que signifient on, jobs, runs-on, steps et uses ?

Le fichier `ci.yml` est un fichier YAML qui définit un **workflow GitHub Actions**. Voici la structure et le rôle de chaque élément :

```yaml
name: CI Pipeline
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - name: Lancer les tests
        run: pytest -v
```

- **`name`** : Le nom du workflow, affiché dans l'onglet Actions de GitHub.

- **`on`** : Définit les **événements déclencheurs** du workflow. Dans notre cas :
  - `push` sur `main` : le pipeline se lance à chaque push sur la branche main
  - `pull_request` sur `main` : le pipeline se lance à chaque Pull Request vers main
  Cela garantit que le code est toujours vérifié avant et après intégration.

- **`jobs`** : Un workflow contient un ou plusieurs **jobs**. Chaque job est un ensemble
  de steps qui s'exécute sur un runner. Par défaut, les jobs s'exécutent en parallèle.
  On peut les rendre séquentiels avec `needs:`.

- **`runs-on`** : Définit le **runner** (environnement d'exécution) sur lequel le job
  tourne. `ubuntu-latest` signifie une machine virtuelle Linux gérée par GitHub.
  On pourrait aussi utiliser `windows-latest` ou `macos-latest`.

- **`steps`** : La liste des **étapes** du job, exécutées séquentiellement dans l'ordre.
  Chaque step peut soit exécuter une commande shell (`run`), soit utiliser une action
  préexistante (`uses`).

- **`uses`** : Permet d'utiliser une **action réutilisable** de la marketplace GitHub
  ou d'un autre dépôt. Par exemple :
  - `actions/checkout@v4` : clone le dépôt dans le runner
  - `actions/setup-python@v5` : installe Python dans l'environnement

---

### Question 2 — Expliquez le rôle de la fixture client dans les tests Flask. Pourquoi utilise-t-on app.test_client() plutôt que de lancer le serveur ?

```python
@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
```

**Rôle de la fixture `client` :**

Une **fixture pytest** est une fonction qui prépare un environnement de test réutilisable.
La fixture `client` est injectée automatiquement dans chaque fonction de test qui la déclare
en paramètre, ce qui évite de dupliquer le code d'initialisation dans chaque test.

Elle configure l'application en mode `TESTING = True`, ce qui active des comportements
spécifiques aux tests dans Flask (meilleure gestion des erreurs, désactivation de certaines
protections...).

**Pourquoi `app.test_client()` plutôt que lancer le serveur ?**

`app.test_client()` simule un client HTTP **directement en mémoire**, sans démarrer de
vrai serveur réseau. Les avantages sont multiples :

1. **Rapidité** : pas besoin d'ouvrir un port réseau, les requêtes sont traitées
   directement en mémoire → les tests s'exécutent beaucoup plus vite.

2. **Isolation** : chaque test obtient un client propre sans état partagé avec les autres.

3. **Pas de dépendance réseau** : les tests fonctionnent même sans accès au réseau,
   ce qui est essentiel dans un environnement CI.

4. **Contrôle total** : on peut simuler n'importe quelle requête (GET, POST, headers
   personnalisés...) sans contraintes d'un vrai serveur HTTP.

---

### Question 3 — Pourquoi est-il important de tester localement avant de pousser ? Que se passe-t-il si un test échoue dans la CI ?

**Pourquoi tester localement :**

1. **Feedback immédiat** : corriger une erreur en local prend quelques secondes.
   Attendre le pipeline CI peut prendre 1 à 2 minutes, ce qui ralentit considérablement
   le cycle de développement.

2. **Économie de ressources** : chaque exécution de pipeline consomme des minutes
   GitHub Actions. Pousser du code cassé gaspille ces ressources inutilement.

3. **Historique propre** : des commits du type "fix: correction test raté" polluent
   l'historique Git et rendent la relecture plus difficile.

4. **Bonne pratique professionnelle** : en entreprise, pousser du code qui casse la CI
   bloque toute l'équipe qui ne peut plus merger ses propres branches.

**Que se passe-t-il si un test échoue dans la CI :**

- Le job échoue et affiche une croix rouge dans l'onglet Actions
- GitHub envoie une notification par email au développeur
- Si la branche main est protégée, la Pull Request **ne peut pas être mergée**
- Les autres développeurs voient que la CI est cassée et sont bloqués
- Le rapport d'erreur est visible dans les logs du pipeline pour faciliter le débogage

---

### Question 4 — Qu'est-ce qu'un artefact GitHub Actions ? Donnez 3 exemples d'artefacts utiles.

Un **artefact GitHub Actions** est un fichier ou ensemble de fichiers produit pendant
l'exécution d'un pipeline et **conservé après la fin du job**. Par défaut, les fichiers
créés pendant un job disparaissent à la fin de son exécution car le runner est détruit.
Les artefacts permettent de persister ces fichiers pour les télécharger ou les réutiliser.

Ils sont configurés avec l'action `actions/upload-artifact` et accessibles dans
l'interface GitHub sous l'onglet Actions → run → Artifacts.

**3 exemples d'artefacts utiles :**

1. **Rapport de couverture de code (`coverage-report/`)** : rapport HTML généré par
   `pytest-cov` montrant quelles lignes du code sont couvertes par les tests. Permet
   aux développeurs de visualiser les zones non testées et d'améliorer la qualité des tests.

2. **Binaire ou application compilée** : dans un projet Java ou Go, le `.jar` ou
   l'exécutable compilé est sauvegardé comme artefact pour être déployé ensuite sans
   avoir à recompiler.

3. **Rapport de sécurité** : les outils comme `bandit` ou `semgrep` génèrent des
   rapports JSON ou HTML listant les vulnérabilités détectées. Les conserver comme
   artefacts permet de les analyser et de les archiver pour audit.

---

### Question 5 — Qu'est-ce que la couverture de code ? Pourquoi 100% n'est pas toujours souhaitable ?

**Définition de la couverture de code :**

La **couverture de code** (code coverage) est une métrique qui mesure le **pourcentage
de lignes de code exécutées** lors de l'exécution des tests. Elle indique quelles parties
du code sont testées et lesquelles ne le sont pas.

Par exemple, avec `pytest --cov=src`, on obtient :
```
src/app.py    95%    → 95% des lignes sont couvertes par les tests
```

**Pourquoi 100% n'est pas toujours souhaitable :**

1. **Coût vs bénéfice** : atteindre 100% demande un effort considérable pour tester
   des cas extrêmement rares (gestion d'erreurs système, pannes réseau...) qui n'apportent
   pas de valeur proportionnelle au temps investi.

2. **Faux sentiment de sécurité** : une ligne couverte à 100% ne signifie pas qu'elle
   est correctement testée. Un test peut exécuter une ligne sans vérifier son résultat
   (`assert`). La qualité des tests compte plus que leur quantité.

3. **Code impossible à tester** : certaines branches (ex: `except Exception`) ne peuvent
   être déclenchées que dans des conditions très spécifiques difficiles à simuler en test.

4. **Overhead de maintenance** : des tests écrits uniquement pour augmenter la couverture
   sont fragiles, peu lisibles et coûteux à maintenir.

En pratique, un seuil de **70% à 80%** est généralement considéré comme un bon équilibre
entre qualité et coût. Dans ce TP, le seuil minimum est fixé à 70% avec `--cov-fail-under=70`.

---

### Question 6 — Quel est le rôle d'un linter ? Pourquoi l'exécuter avant les tests dans le pipeline ?

**Rôle d'un linter :**

Un **linter** est un outil d'analyse statique qui vérifie le code source **sans l'exécuter**,
à la recherche de :
- **Erreurs de style** : indentation incorrecte, lignes trop longues, espaces superflus
- **Mauvaises pratiques** : variables non utilisées, imports inutiles
- **Problèmes potentiels** : comparaisons incorrectes, code mort

Dans ce TP, on utilise **flake8** qui vérifie la conformité au standard **PEP8** (le guide
de style officiel Python) :
```bash
flake8 src/ tests/ --max-line-length=120
```

**Pourquoi l'exécuter avant les tests :**

1. **Fail fast** : si le code ne respecte pas le style, inutile de lancer les tests.
   On détecte l'erreur plus tôt et on économise du temps de pipeline.

2. **Lisibilité du code** : un code propre et homogène est plus facile à relire lors
   des code reviews et à maintenir sur le long terme.

3. **Prévention de bugs** : certaines erreurs de style cachent des bugs réels
   (ex: une variable non utilisée peut indiquer une logique incorrecte).

4. **Convention d'équipe** : dans une équipe, le linter garantit que tout le monde
   écrit du code dans le même style, réduisant les frictions lors des revues.

---

### Question 7 — Comment fonctionne le cache dans GitHub Actions ? Que se passe-t-il quand requirements.txt change ?

**Fonctionnement du cache :**

```yaml
- name: Cache pip
  uses: actions/cache@v4
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('requirements.txt') }}
    restore-keys: |
      ${{ runner.os }}-pip-
```

Le cache GitHub Actions fonctionne avec un système de **clé/valeur** :

1. **Première exécution** : GitHub télécharge les dépendances normalement avec `pip install`,
   puis **sauvegarde le dossier** `~/.cache/pip` associé à la clé générée.

2. **Exécutions suivantes** : GitHub calcule la clé à partir du hash de `requirements.txt`.
   Si la clé correspond à un cache existant, il **restaure directement** le dossier
   `~/.cache/pip` sans retélécharger les packages → gain de temps significatif
   (de ~30-60s à ~2-3s).

**La clé `${{ hashFiles('requirements.txt') }}`** est un hash MD5 du fichier
`requirements.txt`. Si le fichier ne change pas, le hash reste identique → le cache
est réutilisé.

**Que se passe-t-il quand `requirements.txt` change :**

Quand on ajoute ou modifie une dépendance dans `requirements.txt`, le hash du fichier
change → la clé du cache est différente → **aucun cache ne correspond** → GitHub
retélécharge toutes les dépendances et crée un **nouveau cache** avec la nouvelle clé.

Le `restore-keys` sert de fallback : si aucune clé exacte ne correspond, GitHub utilise
le cache le plus récent correspondant au préfixe `ubuntu-pip-`, ce qui permet de
réutiliser partiellement le cache même si une dépendance a changé.

---

### Question 8 — Comparez les runners GitHub-hosted et self-hosted : avantages, inconvénients, et dans quel cas utiliser chacun.

| Critère | GitHub-hosted | Self-hosted |
|---|---|---|
| Gestion | GitHub gère tout | L'équipe gère le serveur |
| Coût | Gratuit (limites) puis payant | Coût infrastructure propre |
| Configuration | Prête à l'emploi | À configurer soi-même |
| Maintenance | Aucune | Mises à jour, sécurité... |
| Accès réseau | Internet uniquement | Accès réseau interne possible |
| Performance | Standardisée | Personnalisable |
| Disponibilité | Garantie par GitHub | Dépend de l'infrastructure |

**GitHub-hosted runners :**

- **Avantages** : zéro configuration, toujours à jour, disponibles immédiatement,
  environnement propre à chaque run (pas de pollution entre runs).
- **Inconvénients** : limites de minutes gratuites (2000 min/mois pour les comptes gratuits),
  pas d'accès aux ressources internes (base de données privée, serveurs internes).
- **Cas d'usage** : projets open source, petites équipes, projets sans ressources internes.

**Self-hosted runners :**

- **Avantages** : accès aux ressources internes (base de données, serveurs privés, VPN),
  hardware personnalisé (plus de RAM, GPU pour le ML...), pas de limite de minutes,
  coût maîtrisé pour de gros volumes.
- **Inconvénients** : maintenance à la charge de l'équipe (mises à jour, sécurité,
  disponibilité), risque de pollution entre runs si mal configuré.
- **Cas d'usage** : grandes entreprises, projets nécessitant des ressources internes,
  pipelines très lourds (compilation, ML, tests d'intégration avec base de données).

---

### Question 9 — Décrivez le workflow complet qu'un développeur doit suivre pour intégrer du code quand la branche main est protégée.

Quand la branche `main` est protégée, il est impossible de pousser directement dessus.
Voici le workflow complet à suivre :

1. **Créer une branche de travail** depuis main :
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/ma-nouvelle-fonctionnalite
   ```

2. **Développer la fonctionnalité** en faisant des commits réguliers :
   ```bash
   git add .
   git commit -m "feat: ajout de la nouvelle fonctionnalité"
   ```

3. **Tester localement** avant de pousser :
   ```bash
   pytest -v
   flake8 src/ tests/
   ```

4. **Pousser la branche** sur le dépôt distant :
   ```bash
   git push origin feature/ma-nouvelle-fonctionnalite
   ```

5. **Créer une Pull Request** sur GitHub depuis la branche vers `main`.
   La CI se déclenche automatiquement et vérifie : linting, tests, couverture.

6. **Attendre que la CI soit verte** ✅. Si elle échoue, corriger les erreurs localement
   et repousser. La PR se met à jour automatiquement.

7. **Code review** : un ou plusieurs développeurs relisent le code, laissent des
   commentaires, demandent des modifications si nécessaire.

8. **Merger la PR** une fois la CI verte et la review approuvée. GitHub propose
   plusieurs stratégies : merge commit, squash, rebase.

9. **Supprimer la branche** après le merge pour garder le dépôt propre.

---

### Question 10 — Quelle action avez-vous trouvée et intégrée ? Expliquez son rôle, montrez la configuration YAML, et décrivez le résultat obtenu.

L'action choisie est **[actions/github-script](https://github.com/marketplace/actions/github-script)**,
qui permet d'exécuter du JavaScript directement dans le pipeline pour interagir avec
l'API GitHub. Elle a été utilisée pour **poster automatiquement un commentaire sur la
Pull Request** avec le résumé du résultat des tests.

**Configuration YAML ajoutée :**

```yaml
- name: Commentaire automatique sur la PR
  if: github.event_name == 'pull_request'
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({
        issue_number: context.issue.number,
        owner: context.repo.owner,
        repo: context.repo.repo,
        body: '✅ La CI est passée avec succès ! Tous les tests sont verts.'
      })
```

**Résultat obtenu :**

À chaque Pull Request, un commentaire automatique est posté par le bot GitHub Actions
pour informer l'équipe que la CI est verte, sans avoir à consulter l'onglet Actions.
Cela améliore la visibilité et accélère le processus de revue de code.

**Lien marketplace :** https://github.com/marketplace/actions/github-script

---

## Lien du projet

https://github.com/SaminouA/mon-projet-flask
