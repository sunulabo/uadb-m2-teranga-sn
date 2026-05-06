# dashboard_teranga_sn.py
# Dashboard graphique Teranga-SN - Eq.12
# Satisfaction touristique + tendances e-commerce + alertes reputation

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Palette couleurs - vert/orange/rouge pour les statuts, bleu Senegal pour le reste
COULEURS_STATUT = {'VERT': '#2E8B57', 'ORANGE': '#FF8C00', 'ROUGE': '#DC143C'}
PALETTE_DASH    = ['#1B3A6B', '#2E74B5', '#4CAFDE', '#F0A500', '#E05C2E']


def charger_donnees_hive():
    """Charge les donnees depuis Hive. Retourne None si non disponible."""
    try:
        from pyhive import hive
        conn = hive.Connection(host='hive-metastore', port=10000, database='teranga_sn')
        df_dest  = pd.read_sql('SELECT * FROM vue_destinations',  conn)
        df_ecomm = pd.read_sql('SELECT * FROM vue_ecommerce LIMIT 50', conn)
        conn.close()
        return df_dest, df_ecomm
    except Exception:
        return None, None


def generer_donnees_demo():
    """Donnees de demonstration realistes si Hive est indisponible."""
    destinations = ['DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING', 'CASAMANCE', 'TOUBA', 'ZIGUINCHOR']
    categories   = ['ALIMENTATION', 'MODE', 'ELECTRONIQUE', 'ARTISANAT', 'TELECOM', 'BEAUTE']
    np.random.seed(42)

    sentiments  = np.random.uniform(-0.6, 0.8, len(destinations))
    notes       = np.clip(3.0 + sentiments * 1.2 + np.random.normal(0, 0.3, len(destinations)), 1, 5)
    nb_avis     = np.random.randint(80, 800, len(destinations))
    pct_positif = np.clip(50 + sentiments * 40 + np.random.normal(0, 5, len(destinations)), 5, 95)
    pct_negatif = 100 - pct_positif - np.random.uniform(5, 25, len(destinations))

    statuts = ['ROUGE' if s < -0.3 else 'ORANGE' if s < 0 else 'VERT' for s in sentiments]

    df_dest = pd.DataFrame({
        'destination':   destinations,
        'nb_avis_total': nb_avis,
        'note_moy':      np.round(notes, 2),
        'sentiment_moy': np.round(sentiments, 3),
        'pct_positif':   np.round(pct_positif, 1),
        'pct_negatif':   np.round(np.clip(pct_negatif, 2, 60), 1),
        'statut_reputation': statuts,
    })

    records = []
    for dest in destinations:
        for cat in categories:
            records.append({
                'region_livraison': dest,
                'categorie':        cat,
                'nb_transactions':  int(np.random.randint(20, 300)),
                'ca_total_fcfa':    float(np.random.uniform(500_000, 15_000_000)),
                'panier_moyen_fcfa': float(np.random.uniform(5_000, 80_000)),
            })
    df_ecomm = pd.DataFrame(records)

    return df_dest, df_ecomm


def tracer_carte_reputation(df_dest: pd.DataFrame, ax):
    """Graphique 1 : satisfaction par destination avec couleur selon le statut."""
    df_s = df_dest.sort_values('note_moy', ascending=True)
    couleurs = [COULEURS_STATUT[s] for s in df_s['statut_reputation']]

    bars = ax.barh(df_s['destination'], df_s['note_moy'], color=couleurs, edgecolor='white', height=0.6)

    for bar, note, nb in zip(bars, df_s['note_moy'], df_s['nb_avis_total']):
        ax.text(bar.get_width() + 0.05, bar.get_y() + bar.get_height() / 2,
                f'{note:.2f} ({nb} avis)', va='center', fontsize=8, color='#333333')

    ax.set_xlim(0, 6.5)
    ax.set_xlabel('Note moyenne /5', fontsize=10)
    ax.set_title('Satisfaction Touristique par Destination\n(DGTT - 30 derniers jours)',
                 fontsize=11, fontweight='bold', color='#1B3A6B')

    legendes = [mpatches.Patch(color=c, label=s) for s, c in COULEURS_STATUT.items()]
    ax.legend(handles=legendes, loc='lower right', fontsize=8, title='Reputation')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)


def tracer_sentiment_detail(df_dest: pd.DataFrame, ax):
    """Graphique 2 : distribution positif/negatif par destination."""
    df_s = df_dest.sort_values('pct_positif', ascending=False)
    x    = np.arange(len(df_s))
    w    = 0.35

    ax.bar(x - w/2, df_s['pct_positif'], w, label='% Positif',
           color='#2E8B57', alpha=0.85, edgecolor='white')
    ax.bar(x + w/2, df_s['pct_negatif'], w, label='% Negatif',
           color='#DC143C', alpha=0.85, edgecolor='white')

    ax.set_xticks(x)
    ax.set_xticklabels(df_s['destination'], rotation=35, ha='right', fontsize=8)
    ax.set_ylabel('Pourcentage des avis (%)', fontsize=10)
    ax.set_title('Distribution Sentiment par Destination\n(Avis FR / EN / WO)',
                 fontsize=11, fontweight='bold', color='#1B3A6B')
    ax.legend(fontsize=9)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)


def tracer_top_ecommerce(df_ecomm: pd.DataFrame, ax):
    """Graphique 3 : top categories e-commerce par chiffre d'affaires."""
    df_cat = (df_ecomm.groupby('categorie')
              .agg(ca_total=('ca_total_fcfa', 'sum'),
                   nb_trans=('nb_transactions', 'sum'))
              .sort_values('ca_total', ascending=True))

    df_cat['ca_millions'] = df_cat['ca_total'] / 1_000_000
    couleurs = PALETTE_DASH[:len(df_cat)]

    bars = ax.barh(df_cat.index, df_cat['ca_millions'],
                   color=couleurs, edgecolor='white', height=0.6)

    for bar, nb in zip(bars, df_cat['nb_trans']):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f'{nb} transactions', va='center', fontsize=8)

    ax.set_xlabel('Chiffre d\'affaires (millions FCFA)', fontsize=10)
    ax.set_title('Top Categories E-commerce Senegal\n(Jumia - Expat-Dakar - Senmarket)',
                 fontsize=11, fontweight='bold', color='#1B3A6B')
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    ax.set_axisbelow(True)


def tracer_heatmap_ecommerce(df_ecomm: pd.DataFrame, ax):
    """Graphique 4 : heatmap du CA par region et categorie."""
    pivot = df_ecomm.pivot_table(
        index='region_livraison', columns='categorie',
        values='ca_total_fcfa', aggfunc='sum', fill_value=0
    ) / 1_000_000

    sns.heatmap(pivot, ax=ax, cmap='YlOrRd', annot=True, fmt='.1f',
                linewidths=0.5, cbar_kws={'label': 'CA (M FCFA)'}, annot_kws={'size': 7})
    ax.set_title('Heatmap CA E-commerce\nRegion x Categorie (M FCFA)',
                 fontsize=11, fontweight='bold', color='#1B3A6B')
    ax.set_xlabel('Categorie', fontsize=9)
    ax.set_ylabel('Region', fontsize=9)
    ax.tick_params(axis='x', rotation=30, labelsize=8)
    ax.tick_params(axis='y', rotation=0,  labelsize=8)


def generer_dashboard():
    """Genere le dashboard complet en PNG haute resolution."""
    df_dest, df_ecomm = charger_donnees_hive()
    mode = 'Hive'
    if df_dest is None:
        df_dest, df_ecomm = generer_donnees_demo()
        mode = 'Demonstration'
    print(f'Mode donnees : {mode}')

    fig, axes = plt.subplots(2, 2, figsize=(18, 12))
    fig.suptitle(
        'Teranga-SN - Tableau de Bord Intelligence Touristique & E-commerce\n'
        f'DGTT Senegal | {datetime.now().strftime("%d/%m/%Y %H:%M")} | Mode : {mode}',
        fontsize=14, fontweight='bold', color='#1B3A6B', y=1.01
    )

    tracer_carte_reputation(df_dest, axes[0, 0])
    tracer_sentiment_detail(df_dest, axes[0, 1])
    tracer_top_ecommerce(df_ecomm, axes[1, 0])
    tracer_heatmap_ecommerce(df_ecomm, axes[1, 1])

    plt.tight_layout(pad=3.0)

    out_path = os.path.join(OUTPUT_DIR, 'dashboard_teranga_sn.png')
    fig.savefig(out_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f'Dashboard genere : {out_path}')
    return out_path


if __name__ == '__main__':
    generer_dashboard()
