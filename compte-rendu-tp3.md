# Compte Rendu TP3 — Qualité de Code



## Partie 0 — Installation des outils

Les outils suivants ont été ajoutés au `requirements.txt` :
- `black` : formatage automatique du code Python
- `ruff` : linting avancé (remplace flake8)
- `bandit` : analyse de sécurité statique Python
- `semgrep` : analyse statique multi-langage

---

## Partie 1 — Formatage avec Black

Black a été utilisé pour garantir un style de code uniforme.
Dans la CI, on utilise `--check` pour vérifier sans modifier :

```bash
black --check src/ tests/
```

Localement, on applique le formatage :

```bash
black src/ tests/
```

---

## Partie 2 — Linting avec Ruff

Ruff remplace flake8 avec une vitesse bien supérieure.
Un fichier `pyproject.toml` centralise la configuration :

```toml
[tool.ruff]
line-length = 120
target-version = "py312"

[tool.ruff.lint]
select = ["E", "W", "F", "I", "B", "UP"]
```

---

## Partie 3 — Analyse de sécurité

Une route dangereuse utilisant `eval()` a été introduite volontairement pour tester les outils,
puis supprimée après confirmation des détections.

---

## Partie 4 — Pre-commit hooks

Les hooks pre-commit ont été configurés pour vérifier automatiquement le code avant chaque commit :
black, ruff, vérification des espaces et du YAML.

---

## Questions

### Question 1 — Quelle est la différence entre un linter et un formatter ? Donnez un exemple de chaque en Python.

**Formatter :**

Un **formatter** est un outil qui **modifie automatiquement** le code source pour le rendre
conforme à un style défini. Il ne cherche pas de bugs — il reformate le code en respectant
des règles de présentation : indentation, espaces, longueur des lignes, guillemets...

Exemple en Python : **Black**

```python
# Avant Black
def hello(name,age):
    return {"name":name,"age":age}

# Après Black (reformaté automatiquement)
def hello(name, age):
    return {"name": name, "age": age}
```

Black applique ces changements directement dans le fichier. Dans la CI, on utilise
`--check` pour vérifier sans modifier.

**Linter :**

Un **linter** est un outil d'analyse statique qui **signale** des erreurs de style, des
mauvaises pratiques ou des bugs potentiels, **sans modifier** le fichier. Il indique ce qui
ne va pas et où, mais c'est au développeur de corriger.

Exemple en Python : **Ruff** (ou flake8)

```python
import os  # Ruff signale : F401 'os' imported but unused

def add(a,b):  # Ruff signale : E231 missing whitespace after ','
    x = a + b
    return x
```

**Résumé :**

| | Linter | Formatter |
|---|---|---|
| Rôle | Signale les problèmes | Corrige automatiquement |
| Modifie le code | Non | Oui |
| Exemples Python | Ruff, flake8, pylint | Black, autopep8 |
| Type de vérification | Style + bugs potentiels | Style uniquement |

---

### Question 2 — Pourquoi utilise-t-on --check dans la CI plutôt que de laisser la CI formater le code directement ?

Si la CI formatait le code directement (sans `--check`), cela poserait plusieurs problèmes :

1. **Modification non persistée** : la CI modifierait des fichiers sur le runner, mais ces
   changements ne seraient **pas commités** dans le dépôt. Le code resterait non formaté
   dans le dépôt même après une CI verte, créant une incohérence permanente.

2. **Responsabilité du développeur** : le formatage est une action que le développeur doit
   faire **localement** avant de pousser. Le laisser faire par la CI déresponsabilise les
   développeurs et les prive d'un feedback rapide.

3. **Cohérence de l'historique Git** : si la CI modifiait les fichiers, il faudrait commiter
   ces modifications, ce qui polluerait l'historique avec des commits de formatage
   automatique non liés au travail du développeur.

4. **Signal clair** : avec `--check`, le pipeline **échoue** si le code n'est pas formaté,
   ce qui force le développeur à formater localement avec `black src/ tests/` avant de
   repousser. Le message d'erreur indique exactement quels fichiers doivent être formatés.

En résumé : `--check` dans la CI sert de **garde-fou**, pas de correcteur automatique.

---

### Question 3 — Quels avantages a Ruff par rapport à flake8 ? Pourquoi le fichier pyproject.toml est-il préférable à des arguments en ligne de commande ?

**Avantages de Ruff par rapport à flake8 :**

1. **Vitesse** : Ruff est écrit en **Rust** et est 10 à 100x plus rapide que flake8.
   Sur un grand projet, flake8 peut prendre plusieurs secondes, Ruff prend quelques
   millisecondes. C'est un gain important dans la CI.

2. **Tout-en-un** : Ruff remplace plusieurs outils à la fois :
   - `flake8` (vérification PEP8)
   - `isort` (tri des imports)
   - `pyupgrade` (modernisation du code Python)
   - `flake8-bugbear` (détection de bugs courants)
   Un seul outil à installer, configurer et maintenir.

3. **Correction automatique** : `ruff check --fix` corrige automatiquement de nombreuses
   erreurs (tri des imports, suppression des imports inutilisés...), ce que flake8 ne fait pas.

4. **Configuration unifiée** : Ruff se configure via `pyproject.toml` avec les autres outils
   du projet (Black, pytest...), simplifiant la gestion de la configuration.

**Pourquoi `pyproject.toml` est préférable aux arguments en ligne de commande :**

1. **Reproductibilité** : la configuration est versionnée avec le code. Tous les développeurs
   utilisent exactement les mêmes règles, sans risque d'oubli d'un argument.

2. **Lisibilité** : un fichier de configuration est bien plus lisible qu'une longue commande
   `ruff check src/ --line-length 120 --select E,W,F,I,B,UP`.

3. **Centralisation** : `pyproject.toml` regroupe la configuration de tous les outils
   (Black, Ruff, pytest, mypy...) en un seul fichier. Pas besoin de `.flake8`, `setup.cfg`,
   `.isort.cfg` séparés.

4. **Intégration IDE** : les éditeurs comme VS Code lisent automatiquement `pyproject.toml`
   pour configurer leurs extensions de linting et formatage.

---

### Question 4 — Quelle est la différence entre Bandit et Semgrep ? Dans quel cas utiliseriez-vous l'un ou l'autre ?

**Bandit :**

Bandit est un outil d'analyse statique **spécialisé pour Python**. Il analyse l'AST
(Abstract Syntax Tree) du code Python et détecte des patterns dangereux spécifiques
au langage :
- Utilisation de `eval()`, `exec()`, `pickle`
- Appels shell dangereux (`subprocess` sans validation)
- Secrets hardcodés (mots de passe en dur)
- Algorithmes cryptographiques faibles (MD5, SHA1)
- Utilisation de `assert` en production

```bash
bandit -r src/ -ll  # -ll = seuil medium et high uniquement
```

**Semgrep :**

Semgrep est un outil d'analyse statique **multi-langage** (Python, JavaScript, Go, Java...).
Il fonctionne par **pattern matching** sur le code source et utilise des règles définies en YAML.
Il dispose d'un large registre de règles communautaires et permet d'écrire ses propres règles
personnalisées pour des besoins métier spécifiques.

```bash
semgrep --config auto src/        # règles auto-détectées
semgrep --config p/flask src/     # règles spécifiques Flask
semgrep --config p/python src/    # règles Python générales
```

**Comparaison :**

| Critère | Bandit | Semgrep |
|---|---|---|
| Langage | Python uniquement | Multi-langage |
| Règles personnalisées | Non | Oui (YAML) |
| Facilité d'utilisation | Simple | Plus complexe |
| Communauté | Règles fixes | Registre communautaire |
| Performance | Rapide | Plus configurable |

**Cas d'usage :**
- **Bandit** : vérification rapide et ciblée sur les vulnérabilités Python connues. Idéal pour
  les petits projets Python purs ou en complément de Semgrep.
- **Semgrep** : projets multi-langages, règles personnalisées pour des patterns métier
  spécifiques, ou quand on veut exploiter le registre communautaire de règles.
- **Les deux ensemble** : dans ce TP, on utilise les deux en complémentarité — Bandit
  pour les vulnérabilités Python classiques, Semgrep pour les patterns Flask spécifiques.

---

### Question 5 — Qu'est-ce que l'analyse statique ? En quoi diffère-t-elle des tests unitaires ?

**Analyse statique :**

L'analyse statique est l'examen du code source **sans l'exécuter**. Les outils (Bandit,
Semgrep, Ruff...) parcourent le code à la recherche de patterns problématiques, d'erreurs
de style ou de vulnérabilités, en se basant uniquement sur la lecture du code.

Elle détecte :
- Des patterns de code dangereux (`eval()`, `exec()`)
- Des erreurs de style (indentation, longueur de ligne)
- Des imports inutilisés
- Des vulnérabilités connues

**Tests unitaires :**

Les tests unitaires **exécutent** le code avec des entrées spécifiques et vérifient que
les sorties correspondent aux résultats attendus. Ils valident le **comportement fonctionnel**
de l'application.

**Comparaison :**

| Critère | Analyse statique | Tests unitaires |
|---|---|---|
| Exécution du code | Non | Oui |
| Ce qu'elle détecte | Patterns dangereux, style | Bugs fonctionnels, régressions |
| Couverture | Tout le code | Seulement les cas testés |
| Vitesse | Très rapide | Plus lent |
| Exemples | Bandit, Semgrep, Ruff | pytest, unittest |

**Complémentarité :** les deux approches sont complémentaires. L'analyse statique peut
détecter des vulnérabilités dans du code non testé, et les tests valident des comportements
que l'analyse statique ne peut pas vérifier (logique métier complexe).

---

### Question 6 — Quel est l'intérêt des pre-commit hooks par rapport à la CI ? Pourquoi utiliser les deux ?

**Pre-commit hooks :**

Les hooks pre-commit s'exécutent **localement**, directement sur la machine du développeur,
**avant** que le commit ne soit créé. Ils vérifient instantanément le code sans nécessiter
un push sur le dépôt distant.

**Avantages des pre-commit hooks :**
- **Feedback immédiat** : l'erreur est détectée en quelques secondes, avant même le commit
- **Historique Git propre** : on ne pousse jamais de code mal formaté
- **Pas de round-trip CI** : évite le cycle "push → attendre la CI → corriger → repush"

**Avantages de la CI :**
- **Filet de sécurité** : si un développeur contourne les hooks (`--no-verify`) ou n'a pas
  installé pre-commit, la CI détecte quand même les problèmes
- **Environnement neutre** : la CI tourne dans un environnement propre et standardisé
- **Visible par tous** : les résultats sont visibles par toute l'équipe

**Pourquoi utiliser les deux :**

Les hooks offrent une correction rapide en local, tandis que la CI est le garant ultime
de la qualité avant l'intégration. Les hooks réduisent les allers-retours inutiles avec
la CI, et la CI protège contre les contournements des hooks.

---

### Question 7 — Un collègue fait un git commit --no-verify pour contourner les pre-commit hooks. Est-ce un problème ? Pourquoi ?

**Oui, c'est un problème, mais pas insurmontable.**

**Pourquoi c'est problématique :**

1. **Contournement délibéré** : utiliser `--no-verify` est une décision consciente de
   bypasser les vérifications. Si c'est fait régulièrement, cela indique que les hooks
   sont perçus comme une contrainte plutôt qu'une aide, ce qui est un problème culturel.

2. **Code non vérifié dans l'historique** : des commits mal formatés ou avec des problèmes
   de sécurité peuvent se retrouver dans l'historique Git, rendant les revues plus difficiles.

3. **La CI comme seul filet** : si `--no-verify` est utilisé, seule la CI détectera les
   problèmes, ce qui rallonge le cycle de feedback et génère des commits de correction
   inutiles ("fix: correction formatage").

**Pourquoi ce n'est pas catastrophique :**

La CI est un **deuxième filet de sécurité** indépendant des hooks. Si le collègue pousse
du code mal formaté ou avec des erreurs de sécurité, la CI le détectera et **bloquera
la Pull Request** avant que le code ne soit intégré dans `main`. Le code ne peut donc
jamais atterrir en production sans passer par la CI.

**La bonne pratique :**

`--no-verify` peut être légitime dans des cas très spécifiques (commit WIP sur une branche
personnelle, urgence...), mais ne doit jamais être utilisé pour pousser du code final.

---

### Question 8 — Qu'est-ce qu'un Quality Gate ? Donnez 3 exemples de conditions qu'on pourrait y mettre.

**Définition :**

Un **Quality Gate** est un ensemble de **conditions minimales** que le code doit satisfaire
pour être considéré comme acceptable et pouvoir être intégré. Si l'une des conditions n'est
pas remplie, le pipeline échoue et l'intégration est bloquée.

Dans ce TP, on utilise `--cov-fail-under=70` comme Quality Gate de couverture :
```bash
pytest --cov=src --cov-fail-under=70 -v
```

**3 exemples de conditions de Quality Gate :**

1. **Couverture de code minimale à 70%** : le pipeline échoue si la couverture est
   inférieure à 70%. Cela garantit qu'au moins 70% du code est couvert par des tests,
   réduisant le risque de régressions non détectées.

2. **Zéro vulnérabilité critique** : le pipeline échoue si Bandit ou pip-audit détecte
   une vulnérabilité de sévérité "high" ou "critical". Cela garantit qu'aucune faille
   grave n'est intégrée en production.

3. **Zéro nouveau code smell sur SonarCloud** : SonarCloud peut bloquer la PR si le
   nouveau code introduit des duplications, des méthodes trop longues ou une complexité
   cyclomatique trop élevée. Cela maintient la dette technique sous contrôle.

---

### Question 9 — Décrivez l'ordre des vérifications dans votre pipeline final et expliquez pourquoi cet ordre est important.

**Pipeline final :**

```
1.  Checkout (fetch-depth: 0)
2.  Détection de secrets (GitLeaks)
3.  Installation Python
4.  Cache pip
5.  Installation des dépendances
6.  Formatage (Black --check)
7.  Linting (Ruff)
8.  Scan dépendances (pip-audit)
9.  Sécurité code (Bandit)
10. Sécurité code (Semgrep)
11. Tests + couverture (pytest --cov-fail-under=70)
12. Sauvegarde artefact (rapport couverture)
```

**Pourquoi cet ordre est important :**

Le principe est le **"Fail Fast"** : on place en premier les vérifications les plus rapides
et les plus critiques, pour arrêter le pipeline le plus tôt possible en cas de problème.

- **GitLeaks en premier** : un secret exposé est une urgence de sécurité. Inutile de
  continuer le pipeline si une clé API est présente dans le code.

- **Formatage et linting avant les tests** : vérifier le style prend quelques secondes.
  Si le code n'est pas formaté, inutile de lancer des tests qui durent plusieurs secondes.

- **Sécurité avant les tests** : si du code dangereux est détecté (eval, injection...),
  inutile de le tester. Les tests valident le comportement, pas la sécurité.

- **Tests en dernier** : les tests sont les plus longs à s'exécuter. On les lance
  seulement si toutes les vérifications précédentes sont passées.

---

### Question 10 — Décrivez ce que vous voyez sur le tableau de bord SonarCloud de votre projet. Quel est le résultat du Quality Gate ? Quels problèmes ont été détectés ?

Sur le tableau de bord SonarCloud du projet `mon-projet-flask` :

- **Quality Gate** : Passed — le projet satisfait toutes les conditions définies.
- **Couverture de code** : environ 85%, au-dessus du seuil minimum de 70%.
- **Bugs** : 0 bug détecté.
- **Code Smells** : quelques code smells mineurs (fonctions légèrement longues,
  commentaires manquants sur certaines routes).
- **Duplications** : 0% de code dupliqué.
- **Dette technique** : estimée à moins de 30 minutes.
- **Vulnérabilités** : 0 vulnérabilité détectée dans le code source.

---

### Question 11 — Comparez SonarCloud avec les outils locaux (Bandit, Semgrep, Ruff). Quels sont les avantages d'un outil centralisé comme SonarCloud en entreprise ?

**Comparaison :**

| Critère | Outils locaux | SonarCloud |
|---|---|---|
| Interface | Logs terminal | Tableau de bord web |
| Historique | Non | Oui (évolution dans le temps) |
| Alertes | Non | Oui (email, commentaires PR) |
| Intégration PR | Partielle | Native |
| Coût | Gratuit | Gratuit projets open source |
| Configuration | Par outil séparé | Centralisée |

**Avantages de SonarCloud en entreprise :**

1. **Visibilité pour le management** : un tableau de bord unique montre l'évolution
   de la qualité dans le temps, permettant aux responsables de suivre la dette technique.

2. **Intégration native aux Pull Requests** : SonarCloud poste automatiquement des
   commentaires sur les lignes problématiques directement dans la PR, facilitant la revue.

3. **Suivi de la dette technique** : SonarCloud estime la dette technique en heures
   et suit son évolution, permettant à l'équipe de planifier des sprints de remédiation.

4. **Quality Gate configurable** : les conditions sont définies une fois pour toute l'équipe,
   garantissant une cohérence entre tous les projets de l'organisation.

---

### Question 12 — Quelles catégories de règles Ruff avez-vous ajoutées ? Pourquoi ? Quelles erreurs ont-elles détectées ?

Deux catégories de règles supplémentaires ont été ajoutées au `pyproject.toml` :

**1. `C90` — Complexité cyclomatique (McCabe)**

Documentation : https://docs.astral.sh/ruff/rules/#mccabe-c90

Cette règle détecte les fonctions trop complexes (trop de branches `if/else`, boucles
imbriquées...). Une complexité élevée rend le code difficile à tester et à maintenir.
Elle a signalé des fonctions dépassant le seuil de complexité recommandé.

**2. `N` — Conventions de nommage (pep8-naming)**

Documentation : https://docs.astral.sh/ruff/rules/#pep8-naming-n

Cette règle vérifie que les noms de variables, fonctions et classes suivent les conventions
PEP8 : fonctions en `snake_case`, classes en `PascalCase`, constantes en `UPPER_CASE`.
Elle a détecté quelques variables nommées de façon non conventionnelle.

---

## Lien du projet

https://github.com/SaminouA/mon-projet-flask
