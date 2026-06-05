<<<<<<< HEAD
# Teranga-SN - Intelligence Touristique et Economie Numerique

**Eq.12 | Master 2 DSGL UADB Bambey | 2025-2026**

| | |
|---|---|
| **Étudiant 1** | TINE Abdoussalam |
| **Étudiant 2** | NDIAYE Papa Malick |
| **Domaine** | Tourisme & E-commerce Local Sénégal |
| **Enseignant** | M. Ahmed Ben Sidy Bouya SEYE |

---

## Architecture

```
[ SOURCES ]  -->  [ NiFi ]  -->  [ KAFKA ]  -->  [ SPARK NLP ]  -->  [ STORAGE ]
  Avis/Reviews   Ingestion    teranga_avis_raw   Sentiment FR/EN/WO   HBase/Hive
  DGTT arrivées  & Routage    teranga_arrivees    Prédiction flux       Gold Layer
  Jumia/Ecomm                                          │
                                                       ▼
                                              [ AIRFLOW DAG ]
                                              Monitoring hebdo
                                              Réentraînement ML
                                                       │
                                                       ▼
                                              [ DASHBOARD ]
                                              Matplotlib/Seaborn
```

## Démarrage rapide

```bash
# 1. Cloner le dépôt
git clone https://github.com/pa-malick/uadb-m2-teranga-sn.git
cd uadb-m2-teranga-sn

# 2. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env : TERANGA_SECRET_SALT=votre_sel_secret

# 3. Démarrer l'infrastructure
cd docker
docker compose up -d zookeeper && sleep 10
docker compose up -d kafka nifi hbase hive-metastore && sleep 30
docker compose up -d spark-master spark-worker airflow

# 4. Initialiser HBase
python scripts/hbase_setup.py

# 5. Démarrer le simulateur de données
python scripts/kafka_producer_teranga_sn.py &

# 6. Lancer le pipeline Spark Streaming
spark-submit --master spark://localhost:7077 scripts/streaming_teranga_sn.py

# 7. Générer le dashboard
python dashboard/dashboard_teranga_sn.py
```

## Interfaces Web

| Service | URL | Credentials |
|---------|-----|-------------|
| **Teranga-SN Web App** | http://localhost:5000 | - |
| NiFi    | http://localhost:8081 | admin / teranga2025! |
| Spark   | http://localhost:8080 | - |
| HBase   | http://localhost:16010 | - |
| Airflow | http://localhost:8082 | admin / admin |

## Lancer l'application web

```bash
# Generer les donnees necessaires
python scripts/analyse_keywords.py
python scripts/carte_senegal.py

# Demarrer le serveur Flask
python web/app.py
# Ouvrir http://localhost:5000
```

## Métriques ML (Random Forest)

| Métrique | Valeur |
|----------|--------|
| RMSE     | 31.23  |
| R²       | 0.90   |
| CV R²    | 0.8989 |

## Structure du dépôt

```
web/
  app.py                         # Application Flask (dashboard + API prediction)
  templates/index.html           # Interface Bootstrap 5
scripts/
  kafka_producer_teranga_sn.py   # Simulateur données (avis + e-commerce)
  schema_pandera.py              # Validation schémas + Privacy
  hbase_setup.py                 # Création tables HBase
  streaming_teranga_sn.py        # Pipeline Spark Streaming NLP
  train_flux_model.py            # Entraînement Random Forest + MLflow
  carte_senegal.py               # Carte Folium interactive des destinations
  analyse_keywords.py            # Extraction TF-IDF mots-clés par destination
  exploration_rapide.py          # Exploration initiale des données
dags/
  teranga_sn_dag.py              # DAG Airflow MLOps hebdomadaire
dashboard/
  dashboard_teranga_sn.py        # Dashboard Matplotlib 4 graphiques
docker/
  docker-compose.yml             # Infrastructure complète
nifi_templates/
  template_nifi_eq12.xml         # Template NiFi (4 processors, 2 topics)
tests/
  test_schemas.py                # 10 tests Pandera (schemas + PII)
  test_streaming.py              # Tests unitaires scoring NLP
models/
  metriques_rf.json              # Métriques Random Forest (RMSE, R², CV R²)
.github/workflows/
  ci.yml                         # CI GitHub Actions (pytest automatique)
rapport_teranga_sn.docx          # Rapport final Word
hive_setup.sql                   # Tables et vues Hive
requirements.txt
README.md
```

## Sécurité & Privacy by Design

- Anonymisation SHA-256 des `user_id` avec sel cryptographique
- Drop des colonnes PII (`email_client`) avant HBase/Hive
- Sel stocké en variable d'environnement (jamais en clair dans le code)
- Validation Pandera avec contrôle d'absence de PII

