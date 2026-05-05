# Teranga-SN — Intelligence Touristique & Économie Numérique

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
git clone https://github.com/sunulabo/uadb-m2-teranga-sn.git
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
| NiFi    | http://localhost:8081 | admin / teranga2025! |
| Spark   | http://localhost:8080 | — |
| HBase   | http://localhost:16010 | — |
| Airflow | http://localhost:8082 | admin / admin |

## Métriques ML (Random Forest)

| Métrique | Valeur |
|----------|--------|
| RMSE     | 31.23  |
| R²       | 0.90   |
| CV R²    | 0.8989 |

## Structure du dépôt

```
scripts/
  kafka_producer_teranga_sn.py   # Simulateur données (avis + e-commerce)
  schema_pandera.py              # Validation schémas + Privacy
  hbase_setup.py                 # Création tables HBase
  streaming_teranga_sn.py        # Pipeline Spark Streaming NLP
  train_flux_model.py            # Entraînement Random Forest + MLflow
dags/
  teranga_sn_dag.py              # DAG Airflow MLOps hebdomadaire
dashboard/
  dashboard_teranga_sn.py        # Dashboard Matplotlib 4 graphiques
docker/
  docker-compose.yml             # Infrastructure complète
nifi_templates/
  template_nifi_eq12.xml         # Template NiFi (4 processors, 2 topics)
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
