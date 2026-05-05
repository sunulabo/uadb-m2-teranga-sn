# streaming_teranga_sn.py
# Pipeline Spark Structured Streaming - Teranga-SN Eq.12
# NLP sentiment FR/EN/WO + Privacy by Design + agregation reputation destination

import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sha2, concat, lit, from_json, to_json, struct,
    window, avg, count, when, coalesce, udf, current_timestamp,
    sum as spark_sum,
)
from pyspark.sql.types import (
    StructType, StructField, StringType, FloatType
)

# Configuration generale
KAFKA_SERVERS = os.environ.get('KAFKA_SERVERS', 'kafka:9092')
SALT          = os.environ.get('TERANGA_SECRET_SALT', 'teranga_salt_uadb_2025')

spark = (
    SparkSession.builder
    .appName('Teranga_SN_Streaming')
    .config('spark.sql.shuffle.partitions', '4')
    .config('spark.streaming.stopGracefullyOnShutdown', 'true')
    .getOrCreate()
)
spark.sparkContext.setLogLevel('WARN')

# Lexique sentiment FR/EN/Wolof pour le domaine touristique senegalais
LEXIQUE = {
    # Positif FR
    'magnifique': 0.90, 'excellent': 0.90, 'superbe': 0.85,
    'teranga': 0.80, 'chaleureux': 0.75, 'delicieux': 0.80,
    'incontournable': 0.70, 'parfait': 0.85, 'sympa': 0.60,
    # Positif EN
    'amazing': 0.90, 'wonderful': 0.85, 'recommend': 0.75,
    'beautiful': 0.80, 'paradise': 0.90, 'stunning': 0.85,
    # Positif Wolof
    'dafa baax': 0.90, 'rafet': 0.80, 'baax': 0.85, 'yomb': 0.70,
    'neex': 0.80, 'dafa neex': 0.85, 'dafa rafet': 0.85,
    'yomb na': 0.75, 'fi neex': 0.80, 'bari nit': 0.60,
    'jaam': 0.70, 'dafa baax lool': 0.95, 'ak yaakaar': 0.65,
    'benn probleme': 0.50, 'am na solo': 0.75, 'professionnel': 0.60,
    # Negatif FR
    'decevant': -0.70, 'arnaque': -0.90, 'sale': -0.80,
    'dechets': -0.70, 'cher': -0.50, 'insatisfait': -0.75,
    # Negatif EN
    'disappointed': -0.70, 'overpriced': -0.60, 'touts': -0.50,
    'dirty': -0.80, 'rude': -0.75,
    # Negatif Wolof
    'dafa neka': -0.80, 'amul solo': -0.70,
    'dafa bon': -0.80, 'metti': -0.65, 'dafa metti': -0.75,
    'xamul': -0.55, 'toorop cher': -0.60, 'dafa daw': -0.50,
    'amul barke': -0.65, 'loolu amul yaram': -0.80,
}


@udf(returnType=FloatType())
def score_sentiment(texte: str) -> float:
    """Calcule un score de sentiment [-1, 1] par correspondance lexicale."""
    if not texte:
        return 0.0
    t = texte.lower()
    score, n = 0.0, 0
    for terme, val in LEXIQUE.items():
        if terme in t:
            score += val
            n += 1
    return float(score / max(n, 1))


# Schemas JSON pour les deux topics Kafka
schema_avis = StructType([
    StructField('avis_id',       StringType(), True),
    StructField('user_id',       StringType(), True),
    StructField('email_client',  StringType(), True),
    StructField('destination',   StringType(), True),
    StructField('type_activite', StringType(), True),
    StructField('nationalite',   StringType(), True),
    StructField('note',          FloatType(),  True),
    StructField('texte_avis',    StringType(), True),
    StructField('langue',        StringType(), True),
    StructField('plateforme',    StringType(), True),
    StructField('timestamp',     StringType(), True),
])

schema_ecommerce = StructType([
    StructField('transaction_id',   StringType(), True),
    StructField('user_id',          StringType(), True),
    StructField('categorie',        StringType(), True),
    StructField('montant_fcfa',     FloatType(),  True),
    StructField('region_livraison', StringType(), True),
    StructField('plateforme',       StringType(), True),
    StructField('timestamp',        StringType(), True),
])


# Stream 1 : avis touristiques avec NLP et anonymisation
avis_df = (
    spark.readStream
    .format('kafka')
    .option('kafka.bootstrap.servers', KAFKA_SERVERS)
    .option('subscribe', 'teranga_avis_raw')
    .option('startingOffsets', 'latest')
    .load()
    .select(from_json(col('value').cast('string'), schema_avis).alias('d'))
    .select('d.*')
    .withColumn('event_ts', current_timestamp())
    # Privacy by Design : SHA-256 + suppression du PII
    .withColumn('user_secure', sha2(concat(col('user_id'), lit(SALT)), 256))
    .drop('user_id', 'email_client')
    # NLP sentiment
    .withColumn('sentiment_score', score_sentiment(col('texte_avis')))
    .withColumn('sentiment_label',
        when(col('sentiment_score') >  0.3, lit('POSITIF'))
        .when(col('sentiment_score') < -0.3, lit('NEGATIF'))
        .otherwise(lit('NEUTRE'))
    )
)

# Agregation reputation par destination sur une fenetre glissante de 7 jours
reputation_df = (
    avis_df
    .withWatermark('event_ts', '1 day')
    .groupBy(
        window('event_ts', '7 days', '1 day'),
        'destination',
    )
    .agg(
        avg(coalesce(col('note'), lit(3.0))).alias('note_moy'),
        avg('sentiment_score').alias('sentiment_moy'),
        count('avis_id').alias('nb_avis'),
        spark_sum(when(col('sentiment_label') == 'POSITIF', 1).otherwise(0)).alias('nb_positif'),
        spark_sum(when(col('sentiment_label') == 'NEGATIF', 1).otherwise(0)).alias('nb_negatif'),
    )
    .withColumn('statut_reputation',
        when(col('sentiment_moy') < -0.3, lit('ROUGE'))
        .when(col('sentiment_moy') <  0.0, lit('ORANGE'))
        .otherwise(lit('VERT'))
    )
)

# Stream 2 : transactions e-commerce avec anonymisation
ecomm_df = (
    spark.readStream
    .format('kafka')
    .option('kafka.bootstrap.servers', KAFKA_SERVERS)
    .option('subscribe', 'teranga_arrivees_raw')
    .option('startingOffsets', 'latest')
    .load()
    .select(from_json(col('value').cast('string'), schema_ecommerce).alias('d'))
    .select('d.*')
    .withColumn('event_ts', current_timestamp())
    # Privacy : anonymisation + suppression user_id
    .withColumn('user_secure', sha2(concat(col('user_id'), lit(SALT)), 256))
    .drop('user_id')
)

# Query 1 : alertes reputation envoyees vers un topic Kafka dedie
q_reputation = (
    reputation_df
    .select(to_json(struct('*')).alias('value'))
    .writeStream
    .format('kafka')
    .option('kafka.bootstrap.servers', KAFKA_SERVERS)
    .option('topic', 'teranga_alerts')
    .option('checkpointLocation', '/tmp/teranga_rep_ckpt')
    .outputMode('update')
    .start()
)

# Query 2 : avis enrichis vers console pour debug
q_avis = (
    avis_df
    .select('avis_id', 'user_secure', 'destination', 'note',
            'sentiment_score', 'sentiment_label', 'langue', 'event_ts')
    .writeStream
    .format('console')
    .option('truncate', False)
    .option('numRows', 5)
    .outputMode('append')
    .trigger(processingTime='10 seconds')
    .start()
)

# Query 3 : e-commerce vers console pour debug
q_ecomm = (
    ecomm_df
    .select('transaction_id', 'user_secure', 'categorie', 'montant_fcfa', 'region_livraison')
    .writeStream
    .format('console')
    .option('truncate', False)
    .option('numRows', 5)
    .outputMode('append')
    .trigger(processingTime='10 seconds')
    .start()
)

print('Pipeline Teranga-SN demarre - 3 queries actives')
q_reputation.awaitTermination()
