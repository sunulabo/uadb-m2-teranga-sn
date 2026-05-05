# Contexte complet - Teranga-SN Eq.12
# A coller dans une nouvelle session Claude pour continuer le projet

---

## Qui je suis

- NDIAYE Papa Malick, Master 2 Data Science et Genie du Logiciel (DSGL), UADB Bambey
- Equipe 12, binome : TINE Abdoussalam (abdoussalamtine4@gmail.com)
- Enseignant : M. Ahmed Ben Sidy Bouya SEYE
- Annee : 2025-2026

---

## Le projet

Nom : Teranga-SN - Plateforme d'Intelligence Touristique et d'Economie Numerique au Senegal

Pipeline Big Data complet :
- Kafka ingere les avis touristiques (FR/EN/Wolof) et les transactions e-commerce
- NiFi simule l'ingestion via template XML
- Spark Structured Streaming fait le NLP sentiment + anonymisation SHA-256
- HBase stocke les avis analyses et les alertes reputation
- Hive stocke en ORC+SNAPPY avec 2 vues analytiques
- Random Forest predit les flux touristiques (RMSE=31.23, R2=0.90, CV R2=0.8989)
- Airflow orchestre le monitoring hebdomadaire avec BranchPythonOperator
- Dashboard Matplotlib 4 graphiques (PNG)
- 21 tests pytest (10 Pandera + 11 NLP)
- CI GitHub Actions

---

## Repo GitHub

- URL : https://github.com/pa-malick/uadb-m2-teranga-sn
- Branches : main, dev-papamalick, dev-abdoussalam
- 15 commits propres sur main
- Format commits : [S1] ou [S2] + type + description en francais

---

## Regles absolues a respecter

1. Aucune trace de Claude ou d'IA dans le repo (pas dans les commits, le code, les commentaires)
2. Pas de tirets longs (ce caractere : --) dans les commentaires de code
3. Pas de caracteres speciaux dans les commentaires Python/SQL/YAML
4. Les commentaires du code sont sans accents
5. Le rapport Word garde les accents (c'est un document humain)
6. Ne jamais commiter .env, data/, models/*.pkl
7. Toujours commiter avec le format : [S1] ou [S2] type: description

---

## Fichiers du projet (21 fichiers trackes)

```
.env.example
.github/workflows/ci.yml
.gitignore
dags/teranga_sn_dag.py
dashboard/dashboard_teranga_sn.py
docker/docker-compose.yml
hive_setup.sql
models/metriques_rf.json
nifi_templates/template_nifi_eq12.xml
notes_apprentissage.md
rapport_teranga_sn.docx
README.md
requirements.txt
scripts/exploration_rapide.py
scripts/hbase_setup.py
scripts/kafka_producer_teranga_sn.py
scripts/schema_pandera.py
scripts/streaming_teranga_sn.py
scripts/train_flux_model.py
tests/test_schemas.py
tests/test_streaming.py
TINE_ONBOARDING.md
```

---

## Infrastructure Docker (docker-compose.yml)

8 services sur le reseau teranga-net :

- zookeeper : confluentinc/cp-zookeeper:7.4.0, port 2181
- kafka : confluentinc/cp-kafka:7.4.0, ports 9092/9093
- nifi : apache/nifi:1.23.2, port 8081, admin/teranga2025!
- hbase : harisekhon/hbase:2.1, ports 16000/16010/16020/9090
- hive-metastore : apache/hive:3.1.3, ports 10000/10002
- spark-master : apache/spark:latest, ports 8080/7077
- spark-worker : apache/spark:latest, depend de spark-master
- airflow : apache/airflow:2.7.3, port 8082 (->8080), admin/admin

Airflow utilise SequentialExecutor + SQLite (pas LocalExecutor, incompatible SQLite).
Le dossier scripts/ est monte dans Airflow : ../scripts:/opt/airflow/scripts

---

## Topics Kafka

- teranga_avis_raw : avis touristiques JSON
- teranga_arrivees_raw : transactions e-commerce JSON
- teranga_alerts : alertes reputation (output Spark)

---

## Tables HBase

Namespace : teranga (a creer avant hbase_setup.py)
Commande : docker exec teranga-hbase sh -c "echo \"create_namespace 'teranga'\" | hbase shell"

Tables :
- teranga:avis_analyses (familles : meta, sentiment, geo)
- teranga:alertes_reputation (famille : alerte)
- teranga:stats_ecommerce (familles : stats, meta)

Port Thrift HBase : 9090
Healthcheck : nc -z localhost 9090 (pas hbase status qui charge la JVM)

---

## Tables Hive

Base : teranga_sn
- avis_analyses : partitionnee par date_obs, ORC+SNAPPY
- ecommerce_transactions : ORC
- vue_destinations : satisfaction par destination (30 derniers jours)
- vue_ecommerce : CA par region et categorie

---

## Modele ML

- Algorithme : Random Forest (sklearn)
- Features : destination_enc, nationalite_enc, type_activite_enc, mois, note_moy, sentiment_moy
- Target : flux_touristes
- Params : n_estimators=150, max_depth=10, min_samples_split=5
- RMSE : 31.23, R2 : 0.90, CV R2 : 0.8989
- Tracking : MLflow (file:///opt/models/mlruns)
- Modele sauve : /opt/models/rf_flux_touristique.pkl (via joblib)
- Metriques : models/metriques_rf.json

Note : donnees entierement simulees (pas de vraies donnees DGTT/TripAdvisor)

---

## DAG Airflow

- dag_id : teranga_sn_monitoring
- Schedule : tous les lundis a 7h (0 7 * * 1)
- Flux : start -> check_reputation (BranchPythonOperator) -> retrain_model OU update_dashboard -> generer_rapport_semaine -> end
- check_reputation interroge Hive, si >1 destination ROUGE -> reentraine le modele
- update_dashboard ecrit les alertes ROUGE/ORANGE dans HBase
- Rapport JSON hebdo dans /opt/models/rapports/

---

## NLP Sentiment

LEXIQUE dans streaming_teranga_sn.py :
- FR positif : magnifique, excellent, teranga, chaleureux, delicieux, parfait, sympa, superbe, incontournable
- EN positif : amazing, wonderful, recommend, beautiful, paradise, stunning
- WO positif : dafa baax, rafet, baax, yomb, neex, dafa neex, dafa rafet, yomb na, fi neex, jaam, dafa baax lool, am na solo
- FR negatif : decevant, arnaque, sale, dechets, cher, insatisfait
- EN negatif : disappointed, overpriced, touts, dirty, rude
- WO negatif : dafa neka, amul solo, dafa bon, metti, dafa metti, xamul, toorop cher, amul barke, loolu amul yaram

Score : moyenne des valeurs des termes trouves dans le texte
Labels : POSITIF si score > 0.3, NEGATIF si score < -0.3, NEUTRE sinon
Watermark : 1 day
Fenetres glissantes : 7 jours / 1 jour

Privacy by Design :
- SHA-256 : sha2(concat(col('user_id'), lit(SALT)), 256)
- SALT : variable d'environnement TERANGA_SECRET_SALT
- Drop obligatoire de user_id et email_client avant HBase/Hive

---

## Tests (21 au total, tous passent)

tests/test_schemas.py (10 tests Pandera) :
- test_avis_valide, test_avis_note_hors_intervalle, test_avis_destination_inconnue
- test_avis_pii_user_id_detecte, test_avis_pii_email_detecte
- test_avis_sentiment_label_invalide, test_ecomm_valide
- test_ecomm_montant_negatif, test_ecomm_categorie_inconnue
- test_ecomm_pii_user_id_detecte

tests/test_streaming.py (11 tests NLP) :
- test_texte_vide_retourne_zero, test_avis_positif_fr, test_avis_negatif_fr
- test_avis_positif_en, test_avis_negatif_en
- test_avis_positif_wolof, test_avis_negatif_wolof
- test_avis_neutre, test_score_dans_intervalle
- test_casse_insensible, test_lexique_wolof_enrichi

Lancer : python -m pytest tests/ -v

---

## Rapport Word

Fichier : rapport_teranga_sn.docx (a la racine du repo)
- Premiere page : Universite Alioune Diop de Bambey / Master 2 - Data Science et Genie du Logiciel (DSGL) / TERANGA-SN
- Style : tableaux blanc (Table Grid), pas de couleurs, pas de zones grises
- Sections : resume executif, introduction, architecture, Kafka/NiFi, Spark, HBase/Hive, validation, ML, Airflow, dashboard, conclusion
- Le rapport a les accents (c'est voulu)
- NE PAS regenerer le rapport sans instruction explicite (le fichier est a jour)

---

## Ce qui reste a faire

1. Attendre les commits de TINE Abdoussalam sur dev-abdoussalam
   - Il doit importer le template NiFi et tester
   - Il doit enrichir le corpus Wolof dans kafka_producer_teranga_sn.py
   - Quand c'est fait : git merge dev-abdoussalam depuis main

2. Avant la soutenance :
   - Generer le dashboard : python dashboard/dashboard_teranga_sn.py
   - Demarrer Docker la veille
   - Ajouter des captures d'ecran dans le rapport (NiFi, Airflow, Spark UI)

3. Ce qui n'existe pas et n'est pas a faire :
   - Pas de site web
   - Pas de frontend
   - Les interfaces de demo sont NiFi/Airflow/Spark/HBase en local

---

## Commandes utiles

Demarrer l'infrastructure :
```
cd docker
docker compose up -d zookeeper && sleep 10
docker compose up -d kafka nifi hbase hive-metastore && sleep 30
docker compose up -d spark-master spark-worker airflow
```

Initialiser HBase :
```
docker exec teranga-hbase sh -c "echo \"create_namespace 'teranga'\" | hbase shell"
python scripts/hbase_setup.py
```

Lancer le simulateur Kafka :
```
python scripts/kafka_producer_teranga_sn.py
```

Lancer le pipeline Spark :
```
spark-submit --master spark://localhost:7077 scripts/streaming_teranga_sn.py
```

Generer le dashboard :
```
python dashboard/dashboard_teranga_sn.py
```

Lancer les tests :
```
python -m pytest tests/ -v
```

Merger la branche binome quand il a termine :
```
git checkout main
git merge dev-abdoussalam
git push origin main
```

---

## Bugs deja corriges (ne pas retoucher)

1. Airflow LocalExecutor -> SequentialExecutor (incompatible avec SQLite)
2. Airflow commande YAML multiline -> single line bash -c
3. HBase healthcheck hbase status -> nc -z localhost 9090
4. HBase volume stale -> docker volume rm docker_hbase-data
5. happybase TypeError bytes/string -> noms de familles en string
6. HBase NamespaceNotFoundException -> creer namespace avant les tables
7. Hive warehouse permissions -> mkdir + chmod 777
8. coalesce('note') -> coalesce(col('note'), lit(3.0))
9. TimestampType import inutile supprime
10. professionnel deplace dans la section positive du LEXIQUE
11. import joblib remonte en haut de train_flux_model.py
12. Chemin spark-submit corrige -> /opt/airflow/scripts/train_flux_model.py
13. Table HBase en bytes -> string dans le DAG
14. Volume scripts/ monte dans Airflow Docker
