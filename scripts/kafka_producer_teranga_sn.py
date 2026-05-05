# kafka_producer_teranga_sn.py
# Simulateur de données touristiques et e-commerce — Teranga-SN Eq.12
# Génère des avis (FR/EN/WO) et des transactions sur les topics Kafka

from kafka import KafkaProducer
import json, random, time, uuid
from datetime import datetime
import numpy as np

random.seed(42)
np.random.seed(42)

# ── Constantes domaine sénégalais ─────────────────────────────────────────────
DESTINATIONS = [
    'DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING',
    'CASAMANCE', 'TOUBA', 'ZIGUINCHOR'
]
TYPES_ACTIVITE   = ['PLAGE', 'CULTURE', 'GASTRONOMIE', 'ARTISANAT', 'ECOTOURISME', 'PELERINAGE']
NATIONALITES     = ['SN', 'FR', 'MA', 'CI', 'GN', 'US', 'DE', 'IT', 'ES', 'GB']
CATEGORIES_ECOMM = ['ALIMENTATION', 'MODE', 'ELECTRONIQUE', 'ARTISANAT', 'TELECOM', 'BEAUTE']
PLATEFORMES_AVIS = ['TRIPADVISOR', 'GOOGLE', 'BOOKING', 'EXPAT_DAKAR']
PLATEFORMES_ECOMM = ['JUMIA', 'EXPAT_DAKAR', 'SENMARKET']

# Corpus d'avis par langue (réaliste, ancré dans le contexte sénégalais)
AVIS_POSITIFS = {
    'FR': [
        'Excellent séjour, accueil chaleureux teranga !',
        'Magnifique destination, cuisine délicieuse thiéboudienne',
        'Plage de Saly superbe, personnel très sympa',
        'Saint-Louis patrimoine UNESCO, incontournable',
        'Casamance magnifique, nature préservée, guide excellent',
        'Dakar vivante et chaleureuse, marché Sandaga incroyable',
    ],
    'EN': [
        'Amazing hospitality, highly recommend Dakar',
        'Beautiful beaches, wonderful people',
        'Best trip ever to Casamance, paradise on earth',
        'Saly resort top quality, will come back',
        'Saint-Louis is stunning, colonial architecture and music',
    ],
    'WO': [
        'Dafa baax torop, teranga bi rafet na',
        'Dakar dafa yomb, rafet na ci kanam',
        'Saly bees na lool, ndox bi set na',
    ],
}

AVIS_NEGATIFS = {
    'FR': [
        'Trop de déchets sur la plage, décevant',
        'Arnaque taxi, prix non affiché à l\'avance',
        'Hôtel pas propre, ne recommande pas du tout',
        'Trop cher pour la qualité proposée',
        'Guides peu professionnels, pas satisfait',
    ],
    'EN': [
        'Too many touts, not a pleasant experience',
        'Overpriced for the quality, disappointed',
        'Beach was dirty, garbage everywhere',
        'Hotel staff rude, would not return',
    ],
    'WO': [
        'Dafa neka lool, dafa cher na torop',
        'Amul solo, dinañu dem yoon waw',
    ],
}


def gen_avis():
    """Génère un avis touristique avec probabilité de positivité selon la saison."""
    dest = random.choice(DESTINATIONS)
    mois = datetime.utcnow().month
    # Haute saison nov-mars : plus de touristes, avis plus positifs
    prob_pos = 0.65 if mois in [11, 12, 1, 2, 3] else 0.45
    langue = random.choices(['FR', 'EN', 'WO'], weights=[60, 30, 10])[0]

    if random.random() < prob_pos:
        texte = random.choice(AVIS_POSITIFS.get(langue, AVIS_POSITIFS['FR']))
        note  = round(random.uniform(3.5, 5.0), 1)
    else:
        texte = random.choice(AVIS_NEGATIFS.get(langue, AVIS_NEGATIFS['FR']))
        note  = round(random.uniform(1.0, 3.0), 1)

    return {
        'avis_id':       str(uuid.uuid4()),
        'user_id':       f'USR_{uuid.uuid4().hex[:10]}',   # anonymisé en streaming
        'email_client':  f'user{random.randint(1, 9999)}@test.sn',  # supprimé en streaming
        'destination':   dest,
        'type_activite': random.choice(TYPES_ACTIVITE),
        'nationalite':   random.choice(NATIONALITES),
        'note':          note,
        'texte_avis':    texte,
        'langue':        langue,
        'plateforme':    random.choice(PLATEFORMES_AVIS),
        'timestamp':     datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }


def gen_ecommerce():
    """Génère une transaction e-commerce locale sénégalaise."""
    return {
        'transaction_id':  str(uuid.uuid4()),
        'user_id':         f'USR_{uuid.uuid4().hex[:10]}',   # anonymisé en streaming
        'categorie':       random.choice(CATEGORIES_ECOMM),
        'montant_fcfa':    round(random.uniform(2000, 150000), 0),
        'region_livraison': random.choice(DESTINATIONS),
        'plateforme':      random.choice(PLATEFORMES_ECOMM),
        'timestamp':       datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }


def gen_arrivee_dgtt():
    """Génère une arrivée touristique DGTT (Direction Générale du Tourisme)."""
    return {
        'arrivee_id':    str(uuid.uuid4()),
        'nationalite':   random.choice(NATIONALITES),
        'destination':   random.choice(DESTINATIONS),
        'duree_sejour':  random.randint(1, 21),
        'type_hebergement': random.choice(['HOTEL', 'MAISON_HOTES', 'CAMPING', 'FAMILLE']),
        'motif':         random.choice(['TOURISME', 'AFFAIRES', 'PELERINAGE', 'FAMILLE']),
        'timestamp':     datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
    }


if __name__ == '__main__':
    producer = KafkaProducer(
        bootstrap_servers=['localhost:9093'],
        value_serializer=lambda v: json.dumps(v, ensure_ascii=False).encode('utf-8'),
    )

    print('Simulateur Teranga-SN démarré — Ctrl+C pour arrêter')
    print('Topics : teranga_avis_raw | teranga_arrivees_raw')

    compteur = 0
    while True:
        producer.send('teranga_avis_raw',     gen_avis())
        producer.send('teranga_arrivees_raw', gen_ecommerce())
        if compteur % 5 == 0:
            producer.send('teranga_arrivees_raw', gen_arrivee_dgtt())
        producer.flush()
        compteur += 1
        if compteur % 10 == 0:
            print(f'  {compteur} messages envoyés — {datetime.utcnow().strftime("%H:%M:%S")}')
        time.sleep(3)
