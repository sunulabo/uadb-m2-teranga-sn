# tests/test_schemas.py
# Tests unitaires Pandera — Teranga-SN Eq.12
# J'ai ajouté ces tests après avoir eu un bug de PII qui passait sans se faire détecter

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
import pandas as pd
from schema_pandera import schema_avis, schema_ecommerce, valider_avis, valider_ecommerce
import pandera as pa


# ── Tests schéma avis ─────────────────────────────────────────────────────────

def df_avis_valide():
    return pd.DataFrame([{
        'avis_id':        'test_avis_001',
        'user_secure':    'a' * 64,
        'destination':    'DAKAR',
        'note':           4.5,
        'sentiment_score': 0.8,
        'sentiment_label': 'POSITIF',
        'langue':         'FR',
    }])


def test_avis_valide():
    """Un avis correct doit passer la validation sans erreur."""
    df = valider_avis(df_avis_valide())
    assert len(df) == 1


def test_avis_note_hors_intervalle():
    """Une note > 5 doit lever une erreur de validation."""
    df = df_avis_valide().copy()
    df['note'] = 6.0
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_destination_inconnue():
    """Une destination inconnue doit être rejetée."""
    df = df_avis_valide().copy()
    df['destination'] = 'PARIS'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_pii_user_id_detecte():
    """Si user_id est présent (PII non supprimé), la validation échoue."""
    df = df_avis_valide().copy()
    df['user_id'] = 'USR_abc123'   # simule un oubli d'anonymisation
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_pii_email_detecte():
    """Si email_client est présent, la validation échoue."""
    df = df_avis_valide().copy()
    df['email_client'] = 'user@test.sn'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


def test_avis_sentiment_label_invalide():
    """Un label sentiment non reconnu doit être rejeté."""
    df = df_avis_valide().copy()
    df['sentiment_label'] = 'TRES_POSITIF'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_avis(df)


# ── Tests schéma e-commerce ───────────────────────────────────────────────────

def df_ecomm_valide():
    return pd.DataFrame([{
        'user_secure':      'b' * 64,
        'categorie':        'MODE',
        'montant_fcfa':     25000.0,
        'region_livraison': 'DAKAR',
    }])


def test_ecomm_valide():
    df = valider_ecommerce(df_ecomm_valide())
    assert len(df) == 1


def test_ecomm_montant_negatif():
    """Un montant négatif n'a pas de sens — doit être rejeté."""
    df = df_ecomm_valide().copy()
    df['montant_fcfa'] = -500.0
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)


def test_ecomm_categorie_inconnue():
    df = df_ecomm_valide().copy()
    df['categorie'] = 'VOITURE'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)


def test_ecomm_pii_user_id_detecte():
    df = df_ecomm_valide().copy()
    df['user_id'] = 'USR_xyz'
    with pytest.raises(pa.errors.SchemaErrors):
        valider_ecommerce(df)
