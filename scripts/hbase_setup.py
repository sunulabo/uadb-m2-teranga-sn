# hbase_setup.py
# Creation des tables HBase pour Teranga-SN - Eq.12
# A executer une seule fois avant le demarrage du pipeline

import happybase
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('teranga.hbase_setup')

HBASE_HOST = 'localhost'
HBASE_PORT = 9090

# Definition des trois tables et de leurs familles de colonnes
TABLES = {
    'teranga:avis_analyses': {
        'meta':      {'max_versions': 1},
        'sentiment': {'max_versions': 1},
        'geo':       {'max_versions': 1},
    },
    'teranga:alertes_reputation': {
        'alerte': {'max_versions': 1},
    },
    'teranga:stats_ecommerce': {
        'stats': {'max_versions': 1},
        'meta':  {'max_versions': 1},
    },
}


def create_teranga_tables():
    """Cree les tables HBase si elles n'existent pas encore."""
    try:
        conn = happybase.Connection(HBASE_HOST, port=HBASE_PORT, timeout=10000)
        conn.open()
        logger.info(f'Connecte a HBase - {HBASE_HOST}:{HBASE_PORT}')

        # Prerequis : le namespace 'teranga' doit exister avant cette etape
        # Si besoin : docker exec teranga-hbase sh -c "echo \"create_namespace 'teranga'\" | hbase shell"
        existantes = {t.decode() for t in conn.tables()}
        logger.info(f'Tables existantes : {existantes or "aucune"}')

        for nom, familles in TABLES.items():
            if nom in existantes:
                logger.info(f'Table {nom} - deja presente, ignoree')
            else:
                conn.create_table(nom, familles)
                logger.info(f'Table {nom} - creee avec succes')

        conn.close()
        logger.info('Configuration HBase terminee.')

    except Exception as exc:
        logger.error(f'Erreur HBase : {exc}')
        raise


if __name__ == '__main__':
    create_teranga_tables()
