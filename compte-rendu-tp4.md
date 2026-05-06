# Compte Rendu TP4 — Sécurité dans l'Usine Logicielle


## Questions

### Question 1 — Qu'est-ce qu'une CVE ? Expliquez le score CVSS et donnez un exemple.

**CVE (Common Vulnerabilities and Exposures) :**

Une **CVE** est un identifiant unique et standardisé attribué à une vulnérabilité de
sécurité connue dans un logiciel. Elle est gérée par le MITRE Corporation et sert de
référence commune dans la communauté de la cybersécurité pour parler d'une même
vulnérabilité sans ambiguïté.

Format : `CVE-ANNÉE-NUMÉRO` (ex: `CVE-2023-30861`)

Chaque CVE contient :
- Une description de la vulnérabilité
- Le ou les packages affectés
- Les versions vulnérables et la version corrigée
- Le score CVSS

**Score CVSS (Common Vulnerability Scoring System) :**

Le score CVSS est une note de **0 à 10** qui évalue la gravité d'une vulnérabilité
en tenant compte de plusieurs critères :
- **Vecteur d'attaque** : réseau, local, physique...
- **Complexité** : l'attaque est-elle facile à réaliser ?
- **Privilèges requis** : l'attaquant doit-il être authentifié ?
- **Impact** : confidentialité, intégrité, disponibilité

| Score | Sévérité |
|---|---|
| 0.0 | Aucune |
| 0.1 – 3.9 | Faible |
| 4.0 – 6.9 | Moyen |
| 7.0 – 8.9 | Élevé |
| 9.0 – 10.0 | Critique |

**Exemple concret : CVE-2023-30861**

- **Package** : Flask
- **Score CVSS** : 7.5 (Élevé)
- **Impact** : fuite de cookies de session via un proxy cache mal configuré. Un attaquant
  peut récupérer les cookies de session d'autres utilisateurs et usurper leur identité.
- **Version corrigée** : Flask 2.2.5 ou 2.3.2
- **Correction** : pip-audit détecte automatiquement cette CVE et recommande la mise à jour.

---

### Question 2 — Pourquoi est-il important de scanner les dépendances et pas seulement votre propre code ?

Notre propre code représente souvent une faible partie de ce qui tourne réellement en
production. Une application Flask typique utilise des dizaines de dépendances directes
(Flask, requests, SQLAlchemy...) et des centaines de dépendances indirectes (dépendances
des dépendances). Chacune de ces bibliothèques peut contenir des vulnérabilités connues.

**Raisons principales :**

1. **Dépendances tierces = code non maîtrisé** : on ne contrôle pas le code des
   bibliothèques externes. Une vulnérabilité peut être introduite à n'importe quel moment
   dans une mise à jour, même mineure (ex: `1.2.3` → `1.2.4`).

2. **Attaques sur la chaîne d'approvisionnement** : les attaques "supply chain" ciblent
   directement les dépendances populaires (ex: incident SolarWinds, Log4Shell). Si une
   bibliothèque très utilisée est compromise, des milliers d'applications sont vulnérables.

3. **CVE connues et exploitables** : les bases de données comme NVD ou GitHub Advisory
   recensent des milliers de CVE pour des packages Python courants. Un attaquant qui sait
   qu'une application utilise Flask 2.0.0 peut immédiatement exploiter CVE-2023-30861.

4. **Code sûr + dépendance vulnérable = application vulnérable** : écrire du code parfaitement
   sécurisé ne sert à rien si une dépendance introduit une faille. La sécurité globale d'une
   application est celle de son maillon le plus faible.

---

### Question 3 — Quel est l'avantage de Dependabot par rapport à un scan manuel avec pip-audit ? Pourquoi configure-t-on aussi l'écosystème github-actions ?

**pip-audit seul :**

pip-audit **détecte** les vulnérabilités et les affiche dans le pipeline. C'est à l'équipe
de mettre à jour manuellement les packages concernés, de tester que rien ne casse, et de
créer un commit de mise à jour. Ce processus est manuel, chronophage et souvent oublié.

**Dependabot :**

Dependabot **automatise entièrement** le processus de mise à jour. Il scanne les dépendances
chaque semaine, crée automatiquement des **Pull Requests** de mise à jour, et ces PR
déclenchent la CI qui vérifie que la mise à jour ne casse rien. L'équipe n'a plus qu'à
relire et merger.

**Comparaison :**

| Critère | pip-audit | Dependabot |
|---|---|---|
| Détection | Oui | Oui |
| Mise à jour auto | Non (signal seulement) | Oui (PR automatique) |
| Fréquence | À chaque push | Hebdomadaire (configurable) |
| Effort humain | Mise à jour manuelle | Relire et merger la PR |
| Historique | Logs CI | PRs traçables dans GitHub |

**Pourquoi configurer aussi `github-actions` :**

```yaml
- package-ecosystem: "github-actions"
  directory: "/"
  schedule:
    interval: "weekly"
```

Les actions GitHub (comme `actions/checkout`, `actions/setup-python`) sont elles-mêmes
des dépendances de notre pipeline. Elles peuvent contenir des vulnérabilités de sécurité
(injection de code, exfiltration de secrets...). Dependabot surveille aussi ces actions et
propose de les mettre à jour (ex: `actions/checkout@v3` → `actions/checkout@v4`) quand
de nouvelles versions sécurisées sont disponibles.

---

### Question 4 — Pourquoi ne doit-on jamais mettre un secret directement dans le code source ? Citez 3 endroits où stocker des secrets de manière sécurisée.

**Pourquoi ne jamais mettre un secret dans le code :**

1. **Git conserve tout l'historique** : même si on supprime le secret dans un commit
   suivant, il reste accessible dans l'historique Git. N'importe qui ayant accès au dépôt
   peut retrouver le secret avec `git log` ou `git show`.

2. **Dépôts publics** : si le dépôt devient public (accidentellement ou intentionnellement),
   tous les secrets sont immédiatement exposés au monde entier et peuvent être récupérés
   par des bots qui scannent GitHub en permanence.

3. **Rotation difficile** : changer un secret hardcodé dans le code nécessite de modifier
   le code, de créer un commit, de le déployer. Avec un gestionnaire de secrets, la rotation
   se fait en quelques clics sans toucher au code.

4. **Partage involontaire** : partager le code avec un prestataire, un stagiaire ou lors
   d'une démo expose automatiquement tous les secrets hardcodés.

**3 endroits sécurisés pour stocker des secrets :**

1. **GitHub Secrets** : secrets chiffrés stockés dans GitHub, injectés dans le pipeline
   via `${{ secrets.NOM_DU_SECRET }}`. Jamais visibles dans les logs (masqués par `***`).
   Idéal pour les secrets utilisés dans la CI/CD.

2. **Variables d'environnement + fichier `.env`** (non versionné) : le fichier `.env`
   est listé dans `.gitignore` et ne sera jamais commité. Les valeurs sont chargées
   localement par la bibliothèque `python-dotenv`. Idéal pour le développement local.

3. **Gestionnaires de secrets dédiés** : en production, des outils comme
   **GCP Secret Manager**, **AWS Secrets Manager** ou **HashiCorp Vault** stockent les
   secrets chiffrés, gèrent les accès par rôles, permettent la rotation automatique
   et enregistrent tous les accès pour audit. C'est la solution de référence en entreprise.

---

### Question 5 — Un développeur a accidentellement commité une clé API GCP, puis l'a supprimée dans un commit suivant. Le secret est-il en sécurité ? Que faut-il faire ?

**Non, le secret n'est absolument pas en sécurité.**

**Pourquoi :**

Git est conçu pour conserver **tout l'historique** de façon immuable. Supprimer un fichier
ou une ligne dans un commit ne le supprime pas de l'historique. N'importe qui peut
retrouver le secret avec :

```bash
git log --all                    # voir tous les commits
git show <hash-du-commit>        # voir le contenu du commit avec le secret
git diff HEAD~2 HEAD~1           # voir les changements entre commits
```

De plus, si le dépôt est public ou si quelqu'un a cloné le dépôt entre les deux commits,
le secret est définitivement compromis. Des bots automatisés scannent GitHub en permanence
et peuvent avoir déjà récupéré la clé.

**Que faut-il faire immédiatement :**

1. **Révoquer la clé immédiatement** : aller dans la console GCP et désactiver/supprimer
   la clé API compromise. C'est l'action la plus urgente — peu importe l'état du dépôt.

2. **Générer une nouvelle clé** et la stocker correctement dans GitHub Secrets ou
   GCP Secret Manager.

3. **Nettoyer l'historique Git** avec `git filter-branch` ou `BFG Repo Cleaner` pour
   supprimer le secret de tout l'historique. Attention : cela réécrit l'historique et
   nécessite un `git push --force`, ce qui peut poser des problèmes si d'autres ont déjà
   cloné le dépôt.

4. **Auditer les accès** : vérifier dans les logs GCP si la clé a été utilisée par des
   tiers non autorisés depuis sa publication.

5. **Prévenir l'équipe** et mettre en place des pre-commit hooks avec GitLeaks pour
   éviter que cela ne se reproduise.

---

### Question 6 — Pourquoi GitLeaks est-il placé au tout début du pipeline, avant même le linting ?

GitLeaks est placé en **premier** dans le pipeline pour plusieurs raisons importantes :

1. **Urgence de sécurité maximale** : un secret exposé dans le code est la vulnérabilité
   la plus critique possible. Si une clé API, un mot de passe ou un token est détecté,
   il faut stopper immédiatement le pipeline et traiter l'incident. Il est inutile et
   dangereux de continuer à builder, tester ou déployer du code contenant un secret exposé.

2. **Principe du Fail Fast** : en plaçant GitLeaks en premier, on échoue le plus tôt
   possible. On économise le temps d'exécution des étapes suivantes (linting, tests...)
   qui peuvent durer plusieurs minutes.

3. **Scan de tout l'historique** : avec `fetch-depth: 0`, GitLeaks scanne **tous les commits**
   du dépôt, pas seulement le dernier. Si un secret a été commité il y a 10 commits,
   il est quand même détecté. Les étapes suivantes (linting, tests) n'ont pas accès à cet
   historique de la même façon.

4. **Indépendance des autres outils** : GitLeaks ne nécessite pas Python, pip ou les
   dépendances du projet. Il peut s'exécuter immédiatement après le checkout, sans
   installation préalable. Le placer avant l'installation des dépendances économise
   du temps si un secret est détecté.

---

### Question 7 — Citez 3 risques de l'OWASP Top 10 et expliquez comment votre pipeline CI les adresse.

L'**OWASP Top 10** est la liste des 10 risques de sécurité les plus critiques pour les
applications web, publiée par l'Open Web Application Security Project.

**1. A06:2021 — Vulnerable and Outdated Components (Composants vulnérables)**

Ce risque concerne l'utilisation de bibliothèques, frameworks ou autres composants
présentant des vulnérabilités connues.

Notre pipeline l'adresse avec :
- **pip-audit** : scanne les dépendances Python à chaque push et détecte les CVE connues
- **Dependabot** : crée automatiquement des PR de mise à jour quand des vulnérabilités
  sont détectées dans les dépendances

**2. A02:2021 — Cryptographic Failures (Failles cryptographiques / Exposition de données sensibles)**

Ce risque concerne l'exposition de données sensibles comme les mots de passe, tokens,
clés API, souvent dûe à des secrets hardcodés dans le code.

Notre pipeline l'adresse avec :
- **GitLeaks** : scanne tout l'historique Git pour détecter des secrets accidentellement
  commités (clés API, mots de passe, tokens...)
- **GitHub Secrets** : les secrets sont stockés de façon chiffrée et injectés via des
  variables d'environnement, jamais exposés dans le code

**3. A03:2021 — Injection**

Ce risque concerne les injections SQL, OS, LDAP... où des données non validées sont
envoyées à un interpréteur. En Python/Flask, l'utilisation de `eval()` avec des entrées
utilisateur est un exemple classique.

Notre pipeline l'adresse avec :
- **Bandit** : détecte les utilisations dangereuses de `eval()`, `exec()`, appels shell
  non sécurisés, et autres patterns d'injection
- **Semgrep** : détecte des patterns Flask spécifiques liés aux injections avec les
  règles `p/flask` et `p/python`

---

### Question 8 — Décrivez l'ordre complet de votre pipeline final. Pour chaque étape, indiquez quel type de problème elle détecte.

```
Étape 1 : Checkout (fetch-depth: 0)
→ Récupère tout l'historique Git pour le scan GitLeaks

Étape 2 : Détection de secrets (GitLeaks)
→ Détecte : clés API, tokens, mots de passe dans le code et l'historique Git

Étape 3 : Installation Python (setup-python)
→ Prépare l'environnement d'exécution

Étape 4 : Cache pip
→ Optimisation : réutilise les dépendances si requirements.txt n'a pas changé

Étape 5 : Installation des dépendances
→ Installe Flask, pytest, black, ruff, bandit, semgrep, pip-audit

Étape 6 : Formatage (Black --check)
→ Détecte : code non conforme au style Black (indentation, espaces, guillemets...)

Étape 7 : Linting (Ruff)
→ Détecte : erreurs PEP8, imports inutilisés, bugs courants, code non moderne

Étape 8 : Scan dépendances (pip-audit)
→ Détecte : CVE connues dans les dépendances Python listées dans requirements.txt

Étape 9 : Sécurité code (Bandit)
→ Détecte : patterns dangereux Python (eval, exec, algos crypto faibles, assert...)

Étape 10 : Sécurité code (Semgrep)
→ Détecte : patterns Flask dangereux, injections, mauvaises pratiques multi-langages

Étape 11 : Tests + couverture (pytest --cov-fail-under=70)
→ Détecte : régressions fonctionnelles, bugs, couverture insuffisante (<70%)

Étape 12 : Sauvegarde artefact (rapport couverture)
→ Conserve le rapport HTML de couverture pour analyse post-run
```

---

### Question 9 — Comparez les approches Shift Left et audit de sécurité traditionnel. Quels sont les avantages du Shift Left ?

**Audit de sécurité traditionnel (Shift Right) :**

Dans l'approche traditionnelle, la sécurité est vérifiée **à la fin** du cycle de
développement, juste avant la mise en production. Un auditeur externe ou une équipe
dédiée effectue des tests de pénétration (pentests) sur l'application finale.

Problèmes :
- Les vulnérabilités sont découvertes tard, quand elles sont coûteuses à corriger
- Les corrections en fin de projet peuvent déstabiliser l'architecture
- Les délais de mise en production sont allongés

**Shift Left :**

Le **Shift Left** consiste à intégrer les vérifications de sécurité **le plus tôt possible**
dans le cycle de développement ("déplacer à gauche" sur la timeline). La sécurité devient
une responsabilité des développeurs dès l'écriture du code, pas seulement des équipes
de sécurité en fin de projet.

Dans notre pipeline : GitLeaks, Bandit, Semgrep, pip-audit s'exécutent à chaque push,
pendant le développement actif.

**Avantages du Shift Left :**

| Critère | Audit traditionnel | Shift Left |
|---|---|---|
| Moment de détection | Fin de projet | Pendant le développement |
| Coût de correction | Très élevé | Faible (code frais) |
| Fréquence | Ponctuelle | Continue (chaque push) |
| Responsabilité | Équipe sécurité | Tous les développeurs |
| Délai mise en production | Allongé | Non impacté |

1. **Coût réduit** : corriger une vulnérabilité découverte pendant le développement coûte
   jusqu'à 100x moins cher que la corriger en production.

2. **Feedback immédiat** : le développeur est encore dans le contexte du code qu'il vient
   d'écrire, la correction est plus facile et rapide.

3. **Culture sécurité** : les développeurs apprennent à écrire du code sécurisé dès le
   départ grâce aux retours automatiques du pipeline.

4. **Sécurité continue** : chaque push est vérifié, pas seulement en phase de recette.

---

### Question 10 — Votre pipeline contient maintenant de nombreuses étapes. Si le temps d'exécution devenait trop long, comment pourriez-vous l'optimiser ?

Plusieurs stratégies permettent d'optimiser le temps d'exécution du pipeline :

1. **Cache pip** (déjà en place) : réutiliser les dépendances installées si `requirements.txt`
   n'a pas changé. Gain : de 30-60s à 2-3s pour l'installation des dépendances.

2. **Parallélisation des jobs** : séparer le pipeline en plusieurs jobs indépendants qui
   s'exécutent en parallèle. Par exemple, lancer `linting + sécurité` en parallèle avec
   `tests`, puis merger les résultats :
   ```yaml
   jobs:
     lint:
       runs-on: ubuntu-latest
       steps: [black, ruff, bandit, semgrep]
     test:
       runs-on: ubuntu-latest
       steps: [pytest]
     deploy:
       needs: [lint, test]  # attend les deux
   ```

3. **Conditions d'exécution** : ne lancer certaines étapes lourdes (Semgrep, SonarCloud)
   que sur les PR vers `main`, pas sur toutes les branches :
   ```yaml
   if: github.event_name == 'pull_request'
   ```

4. **Tests rapides d'abord** : exécuter les tests unitaires rapides avant les tests
   d'intégration plus lents. Si les tests unitaires échouent, inutile d'attendre les
   tests d'intégration.

5. **Réduction de la portée** : configurer bandit et semgrep pour ne scanner que les
   fichiers modifiés dans la PR (diff-aware scanning) plutôt que tout le projet.

6. **Self-hosted runners** : pour des pipelines très intensifs, utiliser des runners
   auto-hébergés avec du matériel plus puissant que les runners GitHub gratuits.

---

### Question 11 — Décrivez la CVE Flask que vous avez trouvée sur GitHub Advisory.

**CVE trouvée : CVE-2023-30861**

- **Identifiant** : CVE-2023-30861
- **Package affecté** : Flask (PyPI)
- **Score CVSS** : 7.5 (Élevé)
- **Versions vulnérables** : Flask < 2.2.5 et Flask >= 2.3.0 < 2.3.2
- **Version corrigée** : Flask 2.2.5 ou 2.3.2

**Impact :**

Lorsqu'une application Flask est placée derrière un proxy cache (comme Nginx ou Varnish),
une réponse contenant un cookie de session peut être mise en cache par le proxy et servie
à d'autres utilisateurs. Cela permet à un attaquant de récupérer le cookie de session
d'un autre utilisateur et d'usurper son identité sans authentification.

**Comment pip-audit et Dependabot auraient prévenu ce problème :**

- **pip-audit** : en scannant `requirements.txt`, pip-audit aurait détecté que Flask 2.0.0
  est affecté par CVE-2023-30861 et afficher un avertissement avec la version corrigée
  recommandée. Le pipeline aurait échoué, bloquant l'intégration.

- **Dependabot** : Dependabot aurait automatiquement créé une Pull Request pour mettre à
  jour Flask vers la version corrigée, avec un lien vers la CVE et une description de
  l'impact. L'équipe n'aurait eu qu'à relire et merger la PR.

**Lien** : https://github.com/advisories/GHSA-m2qf-hxjv-5gpq

---

## Lien du projet

https://github.com/SaminouA/mon-projet-flask
