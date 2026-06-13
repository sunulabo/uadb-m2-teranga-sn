# tests/test_schemas.py
# Tests unitaires Pandera - Teranga-SN Eq.12

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import pandas as pd
from schema_pandera import schema_avis, schema_ecommerce, valider_avis, valider_ecommerce
import pandera.pandas as pa

# SHA-256 valide : 64 caracteres hexadecimaux minuscules
HASH_VALIDE_A = 'a' * 63 + 'b'
HASH_VALIDE_B = 'c' * 63 + 'd'


# Tests schema avis

@pytest.fixture
def df_avis_valide():
    return pd.DataFrame([{
        'avis_id':         'test_avis_001',
        'user_secure':     HASH_VALIDE_A,
        'destination':     'DAKAR',
        'note':            4.5,
        'sentiment_score': 0.8,
        'sentiment_label': 'POSITIF',
        'langue':          'FR',
    }])


def test_avis_valide(df_avis_valide):
    """Un avis correct doit passer la validation sans erreur."""
    df = valider_avis(df_avis_valide)
    assert len(df) == 1


def test_avis_note_superieure_a_5(df_avis_valide):
    """Une note superieure a 5 doit lever une erreur de validation."""
    df = df_avis_valide.copy()
    df['note'] = 6.0
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_note_inferieure_a_1(df_avis_valide):
    """Une note inferieure a 1 doit lever une erreur de validation."""
    df = df_avis_valide.copy()
    df['note'] = 0.5
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_destination_inconnue(df_avis_valide):
    """Une destination inconnue doit etre rejetee."""
    df = df_avis_valide.copy()
    df['destination'] = 'PARIS'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_pii_user_id_detecte(df_avis_valide):
    """Si user_id est present (PII non supprime), la validation echoue."""
    df = df_avis_valide.copy()
    df['user_id'] = 'USR_abc123'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_pii_email_detecte(df_avis_valide):
    """Si email_client est present, la validation echoue."""
    df = df_avis_valide.copy()
    df['email_client'] = 'user@test.sn'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_sentiment_label_invalide(df_avis_valide):
    """Un label sentiment non reconnu doit etre rejete."""
    df = df_avis_valide.copy()
    df['sentiment_label'] = 'TRES_POSITIF'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_user_secure_non_hexadecimal(df_avis_valide):
    """Un user_secure de 64 chars non hexadecimaux doit etre rejete."""
    df = df_avis_valide.copy()
    df['user_secure'] = 'Z' * 64
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


# Tests schema e-commerce

@pytest.fixture
def df_ecomm_valide():
    return pd.DataFrame([{
        'user_secure':      HASH_VALIDE_B,
        'categorie':        'MODE',
        'montant_fcfa':     25000.0,
        'region_livraison': 'DAKAR',
    }])


def test_ecomm_valide(df_ecomm_valide):
    df = valider_ecommerce(df_ecomm_valide)
    assert len(df) == 1


def test_ecomm_montant_negatif(df_ecomm_valide):
    """Un montant negatif n'a pas de sens - doit etre rejete."""
    df = df_ecomm_valide.copy()
    df['montant_fcfa'] = -500.0
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)


def test_ecomm_categorie_inconnue(df_ecomm_valide):
    df = df_ecomm_valide.copy()
    df['categorie'] = 'VOITURE'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)


def test_ecomm_pii_user_id_detecte(df_ecomm_valide):
    df = df_ecomm_valide.copy()
    df['user_id'] = 'USR_xyz'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)
