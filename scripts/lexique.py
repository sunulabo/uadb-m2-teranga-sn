# lexique.py
# Lexique de sentiment FR/EN/Wolof pour le domaine touristique senegalais.
# Source unique importee par streaming_teranga_sn.py et les tests.

LEXIQUE: dict[str, float] = {
    # Positif FR
    'magnifique':      0.90,
    'excellent':       0.90,
    'superbe':         0.85,
    'teranga':         0.80,
    'chaleureux':      0.75,
    'delicieux':       0.80,
    'incontournable':  0.70,
    'parfait':         0.85,
    'sympa':           0.60,
    'professionnel':   0.60,
    # Positif EN
    'amazing':         0.90,
    'wonderful':       0.85,
    'recommend':       0.75,
    'beautiful':       0.80,
    'paradise':        0.90,
    'stunning':        0.85,
    # Positif Wolof
    'dafa baax lool':  0.95,
    'dafa baax':       0.90,
    'dafa neex':       0.85,
    'dafa rafet':      0.85,
    'baax':            0.85,
    'neex':            0.80,
    'fi neex':         0.80,
    'rafet':           0.80,
    'am na solo':      0.75,
    'yomb na':         0.75,
    'yomb':            0.70,
    'jaam':            0.70,
    'ak yaakaar':      0.65,
    'benn probleme':   0.50,
    'bari nit':        0.60,
    # Negatif FR
    'arnaque':         -0.90,
    'sale':            -0.80,
    'insatisfait':     -0.75,
    'decevant':        -0.70,
    'dechets':         -0.70,
    'cher':            -0.50,
    # Negatif EN
    'dirty':           -0.80,
    'rude':            -0.75,
    'disappointed':    -0.70,
    'overpriced':      -0.60,
    'toorop cher':     -0.60,
    'touts':           -0.50,
    # Negatif Wolof
    'loolu amul yaram': -0.80,
    'dafa bon':        -0.80,
    'dafa neka':       -0.80,
    'amul solo':       -0.70,
    'amul barke':      -0.65,
    'dafa metti':      -0.75,
    'metti':           -0.65,
    'xamul':           -0.55,
    'dafa daw':        -0.50,
}
