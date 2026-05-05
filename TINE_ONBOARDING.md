# Pour TINE Abdoussalam - Teranga-SN Eq.12

Tout ce dont tu as besoin pour rejoindre le projet et contribuer.

---

## 1. Liens importants

### Depot GitHub
- Repo principal : https://github.com/pa-malick/uadb-m2-teranga-sn
- Ta branche : https://github.com/pa-malick/uadb-m2-teranga-sn/tree/dev-abdoussalam
- Historique des commits : https://github.com/pa-malick/uadb-m2-teranga-sn/commits/main

### Interfaces web (quand Docker est demarre)
- NiFi : http://localhost:8081 -- identifiants : admin / teranga2025!
- Spark UI : http://localhost:8080 -- pas d'identifiants
- HBase Master : http://localhost:16010 -- pas d'identifiants
- Airflow : http://localhost:8082 -- identifiants : admin / admin

---

## 2. Cloner et configurer ta branche

La branche `dev-abdoussalam` existe deja sur GitHub, tu n'as pas a la creer.

```bash
git clone https://github.com/pa-malick/uadb-m2-teranga-sn.git
cd uadb-m2-teranga-sn
git checkout dev-abdoussalam
git config user.name "TINE Abdoussalam"
git config user.email "abdoussalamtine4@gmail.com"
```

---

## 3. Installer les dependances Python

Minimum pour lancer les tests :

```bash
pip install pandera pandas pytest
```

Installation complete (pipeline Spark, Kafka, etc.) :

```bash
pip install -r requirements.txt
```

---

## 4. Demarrer l'infrastructure Docker

```bash
cd docker
docker compose up -d zookeeper
```

Attendre 10 secondes puis :

```bash
docker compose up -d kafka nifi hbase hive-metastore
```

Attendre 30 secondes puis :

```bash
docker compose up -d spark-master spark-worker airflow
```

Verifier que tout tourne :

```bash
docker compose ps
```

---

## 5. Tes taches

### Tache A - Importer et tester le template NiFi

Le template est deja dans `nifi_templates/template_nifi_eq12.xml`.

Etapes :
1. Ouvrir NiFi sur http://localhost:8081 (admin / teranga2025!)
2. Menu hamburger en haut a droite > Templates > Upload Template
3. Choisir le fichier `nifi_templates/template_nifi_eq12.xml`
4. Faire glisser le template depuis le menu Templates sur le canvas
5. Verifier que les 4 processors apparaissent :
   - GenerateFlowFile (avis touristiques)
   - GenerateFlowFile (transactions e-commerce)
   - PublishKafka vers teranga_avis_raw
   - PublishKafka vers teranga_arrivees_raw
6. Demarrer les processors et verifier que les messages arrivent dans Kafka :

```bash
docker exec teranga-kafka kafka-console-consumer \
  --bootstrap-server localhost:9092 \
  --topic teranga_avis_raw \
  --max-messages 3
```

### Tache B - Lancer les 21 tests existants

```bash
python -m pytest tests/ -v
```

Les 21 tests doivent passer. Si un test echoue, dis-le moi avant de commiter.

### Tache C - Enrichir le corpus d'avis Wolof

Dans `scripts/kafka_producer_teranga_sn.py`, le dictionnaire `AVIS_POSITIFS['WO']`
et `AVIS_NEGATIFS['WO']` contient des phrases en Wolof. Ajoute des phrases
que tu connais pour rendre la simulation plus realiste.

```bash
git add scripts/kafka_producer_teranga_sn.py
git commit -m "[S2] feat: enrichissement corpus avis Wolof"
git push origin dev-abdoussalam
```

---

## 6. Convention de commits obligatoire

```
[S1] feat: nouvelle fonctionnalite
[S1] fix: correction d un bug
[S2] docs: mise a jour documentation
[S2] test: ajout de tests
```

Toujours commiter sur `dev-abdoussalam`, jamais directement sur `main`.

---

## 7. Ne jamais commiter

- `.env` (contient le sel cryptographique)
- `data/` (graphiques generes, deja dans .gitignore)
- `models/*.pkl` (modele trop lourd, deja dans .gitignore)
- `.vscode/` ou `.idea/`

---

## 8. Structure du projet pour t'y retrouver

```
scripts/
  kafka_producer_teranga_sn.py   -> Simulateur de donnees (enrichir corpus Wolof ici)
  streaming_teranga_sn.py        -> Pipeline Spark NLP (lexique Wolof ici)
  schema_pandera.py              -> Validation des donnees
  hbase_setup.py                 -> Creation des tables HBase
  train_flux_model.py            -> Modele Random Forest + MLflow
nifi_templates/
  template_nifi_eq12.xml         -> Template a importer dans NiFi
dags/
  teranga_sn_dag.py              -> DAG Airflow (monitoring hebdomadaire)
tests/
  test_schemas.py                -> 10 tests Pandera (schemas + PII)
  test_streaming.py              -> 11 tests NLP (scoring FR/EN/WO)
docker/
  docker-compose.yml             -> Tous les 8 services
rapport_teranga_sn.docx          -> Rapport final Word
```

---

## 9. Ressources utiles

- Documentation NiFi 1.23 : https://nifi.apache.org/docs/nifi-docs/html/user-guide.html
- Documentation Spark Streaming : https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html
- Documentation happybase (HBase) : https://happybase.readthedocs.io/en/latest/
- Documentation Airflow 2.7 : https://airflow.apache.org/docs/apache-airflow/2.7.3/
- Kafka topics du projet : teranga_avis_raw / teranga_arrivees_raw / teranga_alerts

---

Des questions ? Contacte-moi sur WhatsApp.
