# tests/test_streaming.py
# Tests unitaires du scoring NLP - Teranga-SN Eq.12
# Valide le comportement du lexique FR/EN/WO sans Spark

import pytest

# Lexique duplique ici pour tester sans PySpark
LEXIQUE = {
    'magnifique': 0.90, 'excellent': 0.90, 'superbe': 0.85,
    'teranga': 0.80, 'chaleureux': 0.75, 'delicieux': 0.80,
    'incontournable': 0.70, 'parfait': 0.85, 'sympa': 0.60,
    'amazing': 0.90, 'wonderful': 0.85, 'recommend': 0.75,
    'beautiful': 0.80, 'paradise': 0.90, 'stunning': 0.85,
    'dafa baax': 0.90, 'rafet': 0.80, 'baax': 0.85, 'yomb': 0.70,
    'neex': 0.80, 'dafa neex': 0.85, 'dafa rafet': 0.85,
    'yomb na': 0.75, 'fi neex': 0.80, 'jaam': 0.70,
    'dafa baax lool': 0.95, 'am na solo': 0.75,
    'decevant': -0.70, 'arnaque': -0.90, 'sale': -0.80,
    'dechets': -0.70, 'cher': -0.50, 'insatisfait': -0.75,
    'professionnel': 0.60,
    'disappointed': -0.70, 'overpriced': -0.60, 'touts': -0.50,
    'dirty': -0.80, 'rude': -0.75,
    'dafa neka': -0.80, 'amul solo': -0.70,
    'dafa bon': -0.80, 'metti': -0.65, 'dafa metti': -0.75,
    'xamul': -0.55, 'toorop cher': -0.60,
    'amul barke': -0.65, 'loolu amul yaram': -0.80,
}


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
