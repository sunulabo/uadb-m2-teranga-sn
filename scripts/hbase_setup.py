# hbase_setup.py
# Création des tables HBase pour Teranga-SN — Eq.12
# À exécuter une seule fois avant le démarrage du pipeline

import happybase
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('teranga.hbase_setup')

HBASE_HOST = 'localhost'
HBASE_PORT = 9090

# Définition des tables et familles de colonnes
TABLES = {
    b'teranga:avis_analyses': {
        b'meta':      {'max_versions': 1},
        b'sentiment': {'max_versions': 1},
        b'geo':       {'max_versions': 1},
    },
    b'teranga:alertes_reputation': {
        b'alerte': {'max_versions': 1},
    },
    b'teranga:stats_ecommerce': {
        b'stats': {'max_versions': 1},
        b'meta':  {'max_versions': 1},
    },
}


def create_teranga_tables():
    """Crée les tables HBase si elles n'existent pas encore."""
    try:
        conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT, timeout=10000)
        conn.open()
        logger.info(f'Connecté à HBase — {HBASE_HOST}:{HBASE_PORT}')

        existantes = {t.decode() for t in conn.tables()}
        logger.info(f'Tables existantes : {existantes or "aucune"}')

        for nom_bytes, familles in TABLES.items():
            nom = nom_bytes.decode()
            if nom in existantes:
                logger.info(f'Table {nom} — déjà présente, ignorée')
            else:
                conn.create_table(nom_bytes, familles)
                logger.info(f'Table {nom} — créée avec succès ✓')

        conn.close()
        logger.info('Configuration HBase terminée.')

    except Exception as exc:
        logger.error(f'Erreur HBase : {exc}')
        raise


if __name__ == '__main__':
    create_teranga_tables()
