-- hive_setup.sql — Tables et vues analytiques Teranga-SN Eq.12
-- À exécuter dans HiveServer2 après démarrage de l'infrastructure

CREATE DATABASE IF NOT EXISTS teranga_sn
  COMMENT 'Tourisme & E-commerce Sénégal — UADB Master 2 2025-2026';

USE teranga_sn;

-- ── Table principale : avis touristiques analysés ────────────────────────────
CREATE TABLE IF NOT EXISTS avis_analyses (
    avis_id         STRING      COMMENT 'Identifiant unique de l avis',
    user_secure     STRING      COMMENT 'user_id anonymisé SHA-256',
    destination     STRING      COMMENT 'Destination sénégalaise',
    type_activite   STRING      COMMENT 'Type d activité touristique',
    nationalite     STRING      COMMENT 'Code pays du touriste',
    note            DOUBLE      COMMENT 'Note /5 donnée par le touriste',
    sentiment_score DOUBLE      COMMENT 'Score NLP [-1, 1]',
    sentiment_label STRING      COMMENT 'POSITIF | NEGATIF | NEUTRE',
    langue          STRING      COMMENT 'FR | EN | WO',
    plateforme      STRING      COMMENT 'Source de l avis',
    ingestion_ts    TIMESTAMP   COMMENT 'Timestamp d ingestion Spark'
)
PARTITIONED BY (date_obs STRING COMMENT 'Partition journalière YYYY-MM-DD')
STORED AS ORC
TBLPROPERTIES ('orc.compress' = 'SNAPPY');

-- ── Table : transactions e-commerce ──────────────────────────────────────────
CREATE TABLE IF NOT EXISTS ecommerce_transactions (
    user_secure       STRING    COMMENT 'user_id anonymisé SHA-256',
    categorie         STRING    COMMENT 'Catégorie produit',
    montant_fcfa      DOUBLE    COMMENT 'Montant transaction en FCFA',
    region_livraison  STRING    COMMENT 'Région de livraison',
    plateforme        STRING    COMMENT 'Jumia | Expat-Dakar | Senmarket',
    ingestion_ts      TIMESTAMP COMMENT 'Timestamp ingestion'
)
STORED AS ORC;

-- ── Vue : Satisfaction touristique par destination (30 derniers jours) ───────
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

-- ── Vue : Top catégories e-commerce par région ───────────────────────────────
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
