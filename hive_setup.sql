-- hive_setup.sql - Tables et vues analytiques Teranga-SN Eq.12
-- A executer dans HiveServer2 apres demarrage de l'infrastructure

CREATE DATABASE IF NOT EXISTS teranga_sn
  COMMENT 'Tourisme et E-commerce Senegal - UADB Master 2 2025-2026';

USE teranga_sn;

-- Table principale : avis touristiques analyses
CREATE TABLE IF NOT EXISTS avis_analyses (
    avis_id         STRING      COMMENT 'Identifiant unique de l avis',
    user_secure     STRING      COMMENT 'user_id anonymise SHA-256',
    destination     STRING      COMMENT 'Destination senegalaise',
    type_activite   STRING      COMMENT 'Type d activite touristique',
    nationalite     STRING      COMMENT 'Code pays du touriste',
    note            DOUBLE      COMMENT 'Note /5 donnee par le touriste',
    sentiment_score DOUBLE      COMMENT 'Score NLP entre -1 et 1',
    sentiment_label STRING      COMMENT 'POSITIF ou NEGATIF ou NEUTRE',
    langue          STRING      COMMENT 'FR ou EN ou WO',
    plateforme      STRING      COMMENT 'Source de l avis',
    ingestion_ts    TIMESTAMP   COMMENT 'Timestamp d ingestion Spark'
)
PARTITIONED BY (date_obs STRING COMMENT 'Partition journaliere YYYY-MM-DD')
STORED AS ORC
TBLPROPERTIES ('orc.compress' = 'SNAPPY');

-- Table : transactions e-commerce
CREATE TABLE IF NOT EXISTS ecommerce_transactions (
    user_secure       STRING    COMMENT 'user_id anonymise SHA-256',
    categorie         STRING    COMMENT 'Categorie produit',
    montant_fcfa      DOUBLE    COMMENT 'Montant transaction en FCFA',
    region_livraison  STRING    COMMENT 'Region de livraison',
    plateforme        STRING    COMMENT 'Jumia ou Expat-Dakar ou Senmarket',
    ingestion_ts      TIMESTAMP COMMENT 'Timestamp ingestion'
)
STORED AS ORC;

-- Vue : Satisfaction touristique par destination (30 derniers jours)
CREATE OR REPLACE VIEW vue_destinations AS
SELECT
    destination,
    COUNT(avis_id)                              AS nb_avis_total,
    AVG(COALESCE(note, 3.0))                    AS note_moy,
    AVG(COALESCE(sentiment_score, 0.0))         AS sentiment_moy,
    SUM(CASE WHEN sentiment_label = 'POSITIF' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*)                              AS pct_positif,
    SUM(CASE WHEN sentiment_label = 'NEGATIF' THEN 1 ELSE 0 END) * 100.0
        / COUNT(*)                              AS pct_negatif,
    CASE
        WHEN AVG(COALESCE(sentiment_score, 0)) < -0.3 THEN 'ROUGE'
        WHEN AVG(COALESCE(sentiment_score, 0)) <  0.0 THEN 'ORANGE'
        ELSE 'VERT'
    END                                         AS statut_reputation
FROM avis_analyses
WHERE date_obs >= DATE_SUB(CURRENT_DATE(), 30)
GROUP BY destination
ORDER BY note_moy DESC;

-- Vue : Top categories e-commerce par region
CREATE OR REPLACE VIEW vue_ecommerce AS
SELECT
    region_livraison,
    categorie,
    COUNT(*)                                    AS nb_transactions,
    SUM(montant_fcfa)                           AS ca_total_fcfa,
    AVG(montant_fcfa)                           AS panier_moyen_fcfa
FROM ecommerce_transactions
GROUP BY region_livraison, categorie
ORDER BY ca_total_fcfa DESC;
