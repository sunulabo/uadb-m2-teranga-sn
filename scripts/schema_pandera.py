# schema_pandera.py
# Validation des schemas de donnees avec Pandera - Teranga-SN Eq.12
# Verifie les contraintes metier avant ingestion dans HBase/Hive

import pandera.pandas as pa
from pandera.pandas import Column, DataFrameSchema, Check
import pandas as pd
import logging

logger = logging.getLogger('teranga.schema')

# Valeurs acceptees pour chaque champ categoriel
DESTINATIONS_VALIDES = {
    'DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING',
    'CASAMANCE', 'TOUBA', 'ZIGUINCHOR'
}
LANGUES_VALIDES      = {'FR', 'EN', 'WO'}
SENTIMENTS_VALIDES   = {'POSITIF', 'NEGATIF', 'NEUTRE'}
CATEGORIES_VALIDES   = {'ALIMENTATION', 'MODE', 'ELECTRONIQUE', 'ARTISANAT', 'TELECOM', 'BEAUTE'}


# Schema pour les avis touristiques apres anonymisation
schema_avis = DataFrameSchema(
    columns={
        'avis_id': Column(
            str,
            checks=Check(lambda s: s.str.len() > 10, error='avis_id trop court'),
            nullable=False,
        ),
        'user_secure': Column(
            str,
            checks=[
                Check(lambda s: s.str.len() == 64, error='user_secure doit avoir 64 caracteres'),
                Check(lambda s: s.str.match(r'^[0-9a-f]{64}$'),
                      error='user_secure doit etre un hash SHA-256 hexadecimal minuscule'),
            ],
            nullable=False,
        ),
        'destination': Column(
            str,
            checks=Check(lambda s: s.isin(DESTINATIONS_VALIDES),
                         error=f'destination inconnue - valeurs: {DESTINATIONS_VALIDES}'),
            nullable=False,
        ),
        'note': Column(
            float,
            checks=[
                Check(lambda s: s.between(1.0, 5.0), error='note hors intervalle [1.0, 5.0]'),
            ],
            nullable=True,
        ),
        'sentiment_score': Column(
            float,
            checks=Check(lambda s: s.between(-1.0, 1.0), error='score sentiment hors [-1, 1]'),
            nullable=True,
        ),
        'sentiment_label': Column(
            str,
            checks=Check(lambda s: s.isin(SENTIMENTS_VALIDES),
                         error=f'label sentiment invalide - valeurs: {SENTIMENTS_VALIDES}'),
            nullable=True,
        ),
        'langue': Column(
            str,
            checks=Check(lambda s: s.isin(LANGUES_VALIDES),
                         error=f'langue inconnue - valeurs: {LANGUES_VALIDES}'),
            nullable=True,
        ),
    },
    # Verification globale : aucun PII ne doit etre present dans le dataframe
    checks=[
        Check(
            lambda df: 'user_id' not in df.columns,
            error='PII DETECTE : colonne user_id presente - anonymisation incomplete',
        ),
        Check(
            lambda df: 'email_client' not in df.columns,
            error='PII DETECTE : colonne email_client presente - drop obligatoire',
        ),
    ],
    strict=False,
    coerce=True,
    name='avis_analyses_schema',
)


# Schema pour les transactions e-commerce apres anonymisation
schema_ecommerce = DataFrameSchema(
    columns={
        'user_secure': Column(
            str,
            checks=[
                Check(lambda s: s.str.len() == 64, error='user_secure doit avoir 64 caracteres'),
                Check(lambda s: s.str.match(r'^[0-9a-f]{64}$'),
                      error='user_secure doit etre un hash SHA-256 hexadecimal minuscule'),
            ],
            nullable=False,
        ),
        'categorie': Column(
            str,
            checks=Check(lambda s: s.isin(CATEGORIES_VALIDES),
                         error=f'categorie inconnue - valeurs: {CATEGORIES_VALIDES}'),
            nullable=False,
        ),
        'montant_fcfa': Column(
            float,
            checks=[
                Check(lambda s: s > 0, error='montant doit etre positif'),
                Check(lambda s: s <= 10_000_000, error='montant anormalement eleve'),
            ],
            nullable=False,
        ),
        'region_livraison': Column(
            str,
            checks=Check(lambda s: s.isin(DESTINATIONS_VALIDES),
                         error='region_livraison inconnue'),
            nullable=True,
        ),
    },
    checks=[
        Check(lambda df: 'user_id' not in df.columns,
              error='PII DETECTE : user_id present dans e-commerce'),
    ],
    strict=False,
    coerce=True,
    name='ecommerce_schema',
)


def valider_avis(df: pd.DataFrame) -> pd.DataFrame:
    """Valide un DataFrame d'avis et leve une erreur si la qualite est insuffisante."""
    try:
        df_valide = schema_avis.validate(df, lazy=True)
        logger.info(f'Validation avis OK - {len(df_valide)} lignes valides')
        return df_valide
    except pa.errors.SchemaErrors as e:
        logger.error(f'Erreurs de validation avis :\n{e.failure_cases}')
        raise


def valider_ecommerce(df: pd.DataFrame) -> pd.DataFrame:
    """Valide un DataFrame e-commerce."""
    try:
        df_valide = schema_ecommerce.validate(df, lazy=True)
        logger.info(f'Validation e-commerce OK - {len(df_valide)} lignes valides')
        return df_valide
    except pa.errors.SchemaErrors as e:
        logger.error(f'Erreurs de validation e-commerce :\n{e.failure_cases}')
        raise


# Test rapide si le fichier est lance directement
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    df_test = pd.DataFrame([{
        'avis_id':        'abc12345678',
        'user_secure':    'a' * 64,
        'destination':    'DAKAR',
        'note':           4.2,
        'sentiment_score': 0.75,
        'sentiment_label': 'POSITIF',
        'langue':         'FR',
    }])
    valider_avis(df_test)
    print('Schema avis : OK')

    df_ecomm = pd.DataFrame([{
        'user_secure':      'b' * 64,
        'categorie':        'MODE',
        'montant_fcfa':     15000.0,
        'region_livraison': 'DAKAR',
    }])
    valider_ecommerce(df_ecomm)
    print('Schema e-commerce : OK')
