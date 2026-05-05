# Onboarding - TINE Abdoussalam | Teranga-SN Eq.12

Salut Abdoussalam, voici comment rejoindre le projet et ce que tu dois faire.

## 1. Cloner le repo et creer ta branche

```bash
git clone https://github.com/pa-malick/uadb-m2-teranga-sn.git
cd uadb-m2-teranga-sn
git checkout -b dev-abdoussalam
git config user.name "TINE Abdoussalam"
git config user.email "abdoussalamtine4@gmail.com"
git push -u origin dev-abdoussalam
```

## 2. Installer les dependances

```bash
pip install -r requirements.txt
```

## 3. Ce que tu dois faire (tes taches)

### Tache A - Template NiFi (3 pts au bareme)
Demarrer NiFi via Docker et verifier le flux d'ingestion :
```bash
cd docker
docker compose up -d zookeeper kafka nifi
```
Acceder a http://localhost:8081 (admin / teranga2025!)

Le template est deja disponible dans `nifi_templates/template_nifi_eq12.xml`.
Tu peux l'importer dans NiFi : Templates > Upload Template > choisir le fichier XML.

Le flux contient 4 processors :
- `GenerateFlowFile` - simule les avis touristiques (JSON)
- `GenerateFlowFile` - simule les transactions e-commerce (JSON)
- `PublishKafka` - envoie vers `teranga_avis_raw`
- `PublishKafka` - envoie vers `teranga_arrivees_raw`

### Tache B - Tests pytest
Lancer les tests existants et corriger si necessaire :
```bash
cd uadb-m2-teranga-sn
python -m pytest tests/ -v
```

### Tache C - Enrichir le lexique Wolof
Le lexique dans `scripts/streaming_teranga_sn.py` a deja ete enrichi a 19 termes.
Tu peux en ajouter d'autres si tu connais des expressions courantes.
Commit avec le message : `[S2] feat: enrichissement lexique Wolof`

## 4. Convention de commits obligatoire

```
[S1] feat: description courte en francais
[S1] fix: correction bug watermark
[S2] docs: mise a jour README
```

## 5. Ne jamais commiter

- Le fichier `.env` (contient le sel cryptographique)
- Les dossiers `data/`, `models/`
- Tes fichiers personnels IDE (`.vscode/`, `.idea/`)

## Structure du projet

```
scripts/   -> codes Python (Kafka, Spark, ML)
dags/      -> DAG Airflow
dashboard/ -> graphiques Matplotlib
docker/    -> docker-compose.yml
tests/     -> tests pytest
```

Des questions ? Contacte-moi sur WhatsApp.
