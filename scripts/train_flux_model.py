# train_flux_model.py
# Entrainement du modele de prediction des flux touristiques - Teranga-SN Eq.12
# Random Forest + MLflow tracking + export du modele

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime

from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import mean_squared_error, r2_score

import joblib
import mlflow
import mlflow.sklearn

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger('teranga.ml')

SEED       = 42
MODEL_PATH = os.environ.get('MODEL_PATH', '/opt/models/rf_flux_touristique.pkl')
MLFLOW_URI = os.environ.get('MLFLOW_TRACKING_URI', 'file:///opt/models/mlruns')

np.random.seed(SEED)


def generer_dataset_historique(n: int = 5000) -> pd.DataFrame:
    """
    Genere un historique simule de frequentation touristique.
    Les donnees sont calees sur la saisonnalite reelle du Senegal (haute saison nov-mars).
    """
    destinations  = ['DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING', 'CASAMANCE', 'TOUBA', 'ZIGUINCHOR']
    nationalites  = ['SN', 'FR', 'MA', 'CI', 'GN', 'US', 'DE', 'IT']
    types_activite = ['PLAGE', 'CULTURE', 'GASTRONOMIE', 'ARTISANAT', 'ECOTOURISME', 'PELERINAGE']

    records = []
    for _ in range(n):
        dest       = np.random.choice(destinations)
        nat        = np.random.choice(nationalites)
        activite   = np.random.choice(types_activite)
        mois       = np.random.randint(1, 13)
        note_moy   = round(np.random.uniform(2.5, 5.0), 2)
        sent_moy   = round(np.random.uniform(-0.8, 0.9), 3)

        # Calcul du flux : base + bonus saison + bonus destination + bruit
        base_flux  = 200
        bonus_saison  = 150 if mois in [11, 12, 1, 2, 3] else 0
        bonus_dest    = 100 if dest in ['DAKAR', 'SALY', 'SAINT_LOUIS'] else 0
        bonus_sent    = int(sent_moy * 80)
        bruit         = int(np.random.normal(0, 30))
        flux_reel     = max(10, base_flux + bonus_saison + bonus_dest + bonus_sent + bruit)

        records.append({
            'destination':   dest,
            'nationalite':   nat,
            'type_activite': activite,
            'mois':          mois,
            'note_moy':      note_moy,
            'sentiment_moy': sent_moy,
            'flux_touristes': flux_reel,
        })

    return pd.DataFrame(records)


def preparer_features(df: pd.DataFrame):
    """Encode les variables categorielles et retourne X, y."""
    df = df.copy()
    encodeurs = {}
    for col in ['destination', 'nationalite', 'type_activite']:
        le = LabelEncoder()
        df[col + '_enc'] = le.fit_transform(df[col])
        encodeurs[col] = le

    features = ['destination_enc', 'nationalite_enc', 'type_activite_enc',
                'mois', 'note_moy', 'sentiment_moy']
    X = df[features].values
    y = df['flux_touristes'].values
    return X, y, encodeurs, features


def entrainer_modele():
    """Entraine le Random Forest et logue les metriques dans MLflow."""
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment('teranga_flux_prediction')

    logger.info('Generation du dataset historique...')
    df = generer_dataset_historique(n=5000)
    X, y, encodeurs, features = preparer_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=SEED
    )

    params = {
        'n_estimators': 150,
        'max_depth':    10,
        'min_samples_split': 5,
        'random_state': SEED,
    }

    with mlflow.start_run(run_name=f'rf_flux_{datetime.utcnow().strftime("%Y%m%d_%H%M")}'):
        mlflow.log_params(params)

        logger.info('Entrainement Random Forest...')
        rf = RandomForestRegressor(**params)
        rf.fit(X_train, y_train)

        y_pred = rf.predict(X_test)
        rmse   = np.sqrt(mean_squared_error(y_test, y_pred))
        r2     = r2_score(y_test, y_pred)
        cv_r2  = cross_val_score(rf, X, y, cv=5, scoring='r2').mean()

        logger.info(f'RMSE  : {rmse:.2f} touristes')
        logger.info(f'R2    : {r2:.4f}')
        logger.info(f'CV R2 : {cv_r2:.4f}')

        mlflow.log_metric('rmse',   rmse)
        mlflow.log_metric('r2',     r2)
        mlflow.log_metric('cv_r2',  cv_r2)

        importances = dict(zip(features, rf.feature_importances_.tolist()))
        mlflow.log_dict(importances, 'feature_importances.json')
        logger.info(f'Importances : {importances}')

        mlflow.sklearn.log_model(rf, 'rf_flux_model')
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

        joblib.dump({'model': rf, 'encodeurs': encodeurs, 'features': features},
                    MODEL_PATH)
        logger.info(f'Modele sauvegarde : {MODEL_PATH}')

        metriques = {
            'rmse': round(rmse, 2),
            'r2':   round(r2, 4),
            'cv_r2': round(cv_r2, 4),
            'n_train': len(X_train),
            'n_test':  len(X_test),
            'date_entrainement': datetime.utcnow().isoformat(),
        }
        with open('/opt/models/metriques_rf.json', 'w') as f:
            json.dump(metriques, f, indent=2)

        return rf, rmse, r2


if __name__ == '__main__':
    entrainer_modele()
