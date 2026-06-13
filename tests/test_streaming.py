# tests/test_streaming.py
# Tests unitaires du scoring NLP - Teranga-SN Eq.12
# Valide le comportement du lexique FR/EN/WO sans Spark

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import pytest
from lexique import LEXIQUE


def score_sentiment(texte: str) -> float:
    if not texte:
        return 0.0
    t = texte.lower()
    score, n = 0.0, 0
    for terme, val in LEXIQUE.items():
        if terme in t:
            score += val
            n += 1
    return round(score / max(n, 1), 4)


def label_sentiment(score: float) -> str:
    if score > 0.3:
        return 'POSITIF'
    if score < -0.3:
        return 'NEGATIF'
    return 'NEUTRE'


# Tests scoring

def test_texte_vide_retourne_zero():
    assert score_sentiment('') == 0.0
    assert score_sentiment(None) == 0.0


def test_avis_positif_fr():
    score = score_sentiment('Sejour magnifique, teranga incroyable !')
    assert score > 0.3
    assert label_sentiment(score) == 'POSITIF'


def test_avis_negatif_fr():
    score = score_sentiment('Arnaque taxi, plage sale, decevant')
    assert score < -0.3
    assert label_sentiment(score) == 'NEGATIF'


def test_avis_positif_en():
    score = score_sentiment('Amazing hospitality, highly recommend Dakar')
    assert score > 0.3
    assert label_sentiment(score) == 'POSITIF'


def test_avis_negatif_en():
    score = score_sentiment('Too many touts, overpriced and dirty')
    assert score < -0.3
    assert label_sentiment(score) == 'NEGATIF'


def test_avis_positif_wolof():
    score = score_sentiment('Dafa baax torop, rafet na ci kanam')
    assert score > 0.3
    assert label_sentiment(score) == 'POSITIF'


def test_avis_negatif_wolof():
    score = score_sentiment('Dafa neka lool, amul solo')
    assert score < -0.3
    assert label_sentiment(score) == 'NEGATIF'


def test_avis_neutre():
    score = score_sentiment('Sejour correct, rien a signaler')
    assert label_sentiment(score) == 'NEUTRE'


def test_score_dans_intervalle():
    phrases = [
        'Magnifique excellent parfait superbe',
        'Arnaque sale decevant insatisfait',
        'Voyage sympa',
    ]
    for phrase in phrases:
        score = score_sentiment(phrase)
        assert -1.0 <= score <= 1.0, f'Score hors intervalle : {score} pour "{phrase}"'


def test_casse_insensible():
    score_min = score_sentiment('magnifique')
    score_maj = score_sentiment('MAGNIFIQUE')
    assert score_min == score_maj


def test_lexique_wolof_enrichi():
    termes_wolof = ['neex', 'dafa neex', 'jaam', 'dafa bon', 'metti', 'xamul']
    for terme in termes_wolof:
        assert terme in LEXIQUE, f'Terme Wolof manquant dans le lexique : {terme}'
