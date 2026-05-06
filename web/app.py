# web/app.py
# Application web Teranga-SN - Dashboard interactif + API prediction
# Flask + Bootstrap 5

import os
import json
import numpy as np
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'rf_flux_touristique.pkl')
METRIQUES  = os.path.join(BASE_DIR, 'models', 'metriques_rf.json')
KEYWORDS   = os.path.join(BASE_DIR, 'data', 'keywords_tfidf.json')

DESTINATIONS   = ['DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING', 'CASAMANCE', 'TOUBA', 'ZIGUINCHOR']
TYPES_ACTIVITE = ['PLAGE', 'CULTURE', 'GASTRONOMIE', 'ARTISANAT', 'ECOTOURISME', 'PELERINAGE']
NATIONALITES   = ['SN', 'FR', 'MA', 'CI', 'GN', 'US', 'DE', 'IT']
MOIS_LABELS    = ['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin',
                  'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']


def charger_modele():
    try:
        import joblib
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def donnees_destinations():
    np.random.seed(42)
    sentiments = np.random.uniform(-0.6, 0.8, len(DESTINATIONS))
    notes      = np.clip(3.0 + sentiments * 1.2, 1, 5)
    nb_avis    = np.random.randint(80, 800, len(DESTINATIONS))
    pct_pos    = np.clip(50 + sentiments * 40, 5, 95)
    statuts    = ['ROUGE' if s < -0.3 else 'ORANGE' if s < 0 else 'VERT' for s in sentiments]
    return [
        {
            'destination': d,
            'note':        round(float(n), 2),
            'sentiment':   round(float(s), 3),
            'nb_avis':     int(nb),
            'pct_positif': round(float(p), 1),
            'statut':      st,
        }
        for d, n, s, nb, p, st in zip(DESTINATIONS, notes, sentiments, nb_avis, pct_pos, statuts)
    ]


@app.route('/')
def index():
    metriques    = {}
    keywords     = {}

    if os.path.exists(METRIQUES):
        with open(METRIQUES, encoding='utf-8') as f:
            metriques = json.load(f)

    if os.path.exists(KEYWORDS):
        with open(KEYWORDS, encoding='utf-8') as f:
            keywords = json.load(f)

    destinations = donnees_destinations()
    nb_vert   = sum(1 for d in destinations if d['statut'] == 'VERT')
    nb_orange = sum(1 for d in destinations if d['statut'] == 'ORANGE')
    nb_rouge  = sum(1 for d in destinations if d['statut'] == 'ROUGE')

    carte_disponible = os.path.exists(
        os.path.join(BASE_DIR, 'data', 'carte_senegal.html')
    )

    return render_template(
        'index.html',
        metriques=metriques,
        destinations=destinations,
        destinations_list=DESTINATIONS,
        types_activite=TYPES_ACTIVITE,
        mois_labels=enumerate(MOIS_LABELS, 1),
        nb_vert=nb_vert,
        nb_orange=nb_orange,
        nb_rouge=nb_rouge,
        keywords=keywords,
        carte_disponible=carte_disponible,
    )


@app.route('/predict', methods=['POST'])
def predict():
    data       = request.json
    destination = data.get('destination', 'DAKAR')
    mois        = int(data.get('mois', 1))
    type_act    = data.get('type_activite', 'PLAGE')
    note_moy    = float(data.get('note_moy', 4.0))
    sentiment   = float(data.get('sentiment_moy', 0.3))
    nationalite = data.get('nationalite', 'FR')

    modele_data = charger_modele()

    if modele_data:
        import joblib
        rf        = modele_data['model']
        encodeurs = modele_data['encodeurs']
        dest_enc  = encodeurs['destination'].transform([destination])[0]
        nat_enc   = encodeurs['nationalite'].transform([nationalite])[0]
        act_enc   = encodeurs['type_activite'].transform([type_act])[0]
        X    = np.array([[dest_enc, nat_enc, act_enc, mois, note_moy, sentiment]])
        flux = int(rf.predict(X)[0])
        mode = 'Random Forest'
    else:
        base         = 200
        bonus_saison = 150 if mois in [11, 12, 1, 2, 3] else 0
        bonus_dest   = 100 if destination in ['DAKAR', 'SALY', 'SAINT_LOUIS'] else 0
        bonus_sent   = int(sentiment * 80)
        flux = max(10, base + bonus_saison + bonus_dest + bonus_sent)
        mode = 'Demo'

    saison = 'Haute saison (Nov-Mar)' if mois in [11, 12, 1, 2, 3] else 'Basse saison'
    return jsonify({
        'flux_predit':  flux,
        'destination':  destination,
        'mois':         MOIS_LABELS[mois - 1],
        'saison':       saison,
        'mode':         mode,
    })


@app.route('/carte')
def carte():
    path = os.path.join(BASE_DIR, 'data', 'carte_senegal.html')
    if not os.path.exists(path):
        return 'Carte non generee. Lancez scripts/carte_senegal.py', 404
    with open(path, encoding='utf-8') as f:
        return f.read()


if __name__ == '__main__':
    print('Teranga-SN Web App - http://localhost:5000')
    app.run(debug=True, port=5000)
