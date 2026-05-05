# Onboarding — TINE Abdoussalam | Teranga-SN Eq.12

Salut Abdoussalam, voici comment rejoindre le projet et ce que tu dois faire.

---

## 1. Cloner le repo et créer ta branche

```bash
git clone https://github.com/pa-malick/uadb-m2-teranga-sn.git
cd uadb-m2-teranga-sn
git checkout -b dev-abdoussalam
git config user.name "TINE Abdoussalam"
git config user.email "abdoussalamtine4@gmail.com"
git push -u origin dev-abdoussalam
```

---

## 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

## 3. Ce que tu dois faire (tes tâches)

### Tâche A — Template NiFi (3 pts au barème)
Démarrer NiFi via Docker et créer le flux d'ingestion :
```bash
cd docker
docker compose up -d zookeeper kafka nifi
```
Accéder à http://localhost:8081 (admin / teranga2025!)

Créer un flux avec 3 processors :
- `GenerateFlowFile` → simule les avis (JSON)
- `PublishKafka` → envoie vers `teranga_avis_raw`
- `PublishKafka` → envoie vers `teranga_arrivees_raw`

Exporter le template : Menu → Templates → Create Template → nommer
`template_nifi_eq12` → sauvegarder dans `nifi_templates/`

### Tâche B — Tests pytest
Lancer les tests existants et corriger si nécessaire :
```bash
cd uadb-m2-teranga-sn
python -m pytest tests/ -v
```

### Tâche C — Enrichir le lexique Wolof
Dans `scripts/streaming_teranga_sn.py`, cherche le dictionnaire `LEXIQUE`
et ajoute des termes Wolof que tu connais (positifs et négatifs).
Commit avec le message : `[S1] feat: enrichissement lexique Wolof`

---

## 4. Convention de commits obligatoire

```
[S1] feat: description courte en français
[S1] fix: correction bug watermark
[S2] docs: mise à jour README
```

---

## 5. Ne jamais commiter

- Le fichier `.env` (contient le sel cryptographique)
- Les dossiers `data/`, `models/`
- Tes fichiers personnels IDE (`.vscode/`, `.idea/`)

---

## Structure du projet
```
scripts/   → codes Python (Kafka, Spark, ML)
dags/      → DAG Airflow
dashboard/ → graphiques Matplotlib
docker/    → docker-compose.yml
tests/     → tests pytest
```

Des questions ? Contacte-moi sur WhatsApp.
