# exploration_rapide.py
# Script d'exploration perso - j'ai voulu comprendre les donnees avant de coder
# NDIAYE Papa Malick - Teranga-SN Eq.12

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

# Quelques donnees pour visualiser avant de brancher Kafka
np.random.seed(42)

destinations = ['DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING', 'CASAMANCE', 'TOUBA', 'ZIGUINCHOR']
mois_labels  = ['Jan', 'Fev', 'Mar', 'Avr', 'Mai', 'Jun',
                 'Jul', 'Aou', 'Sep', 'Oct', 'Nov', 'Dec']

# Ce que j'ai remarque : la saisonnalite est tres marquee au Senegal
# Novembre a Mars = haute saison (touristes europeens fuient l'hiver)
flux_mensuel = [320, 290, 280, 180, 140, 110, 100, 95, 130, 160, 240, 310]

print("=== Exploration des donnees Teranga-SN ===\n")

# Distribution des avis par langue
langues = pd.Series({'FR': 60, 'EN': 30, 'WO': 10})
print("Repartition des avis par langue :")
print(langues.to_string())
print()

# Simulation rapide d'un score de sentiment
avis_test = [
    ("Magnifique sejour, teranga incroyable !", "FR"),
    ("Too many touts, disappointed", "EN"),
    ("Dafa baax torop, rafet na", "WO"),
    ("Plage sale, arnaque taxi", "FR"),
    ("Amazing beaches, would recommend!", "EN"),
]

lexique_simple = {
    'magnifique': 0.9, 'teranga': 0.8, 'amazing': 0.9, 'recommend': 0.75,
    'dafa baax': 0.9, 'rafet': 0.8, 'baax': 0.85,
    'disappointed': -0.7, 'touts': -0.5, 'sale': -0.8, 'arnaque': -0.9,
}

print("Test du lexique sentiment :")
for texte, langue in avis_test:
    t = texte.lower()
    score = sum(v for k, v in lexique_simple.items() if k in t)
    label = 'POSITIF' if score > 0.3 else ('NEGATIF' if score < -0.3 else 'NEUTRE')
    print(f"  [{langue}] {texte[:40]:<40} => {score:+.2f} {label}")

print()

# Graphique saisonnalite - j'ai voulu voir visuellement avant tout
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
fig.suptitle("Exploration initiale - Donnees Teranga-SN", fontweight='bold')

# Flux mensuel
axes[0].plot(mois_labels, flux_mensuel, 'o-', color='#1B3A6B', linewidth=2, markersize=6)
axes[0].fill_between(range(12), flux_mensuel, alpha=0.15, color='#1B3A6B')
axes[0].axvspan(0, 2, alpha=0.1, color='orange', label='Haute saison')
axes[0].axvspan(10, 11, alpha=0.1, color='orange')
axes[0].set_xticks(range(12))
axes[0].set_xticklabels(mois_labels, rotation=45, fontsize=8)
axes[0].set_ylabel('Flux estime (touristes/jour)')
axes[0].set_title('Saisonnalite Touristique Senegal')
axes[0].legend()
axes[0].grid(alpha=0.3)

# Distribution langues
couleurs = ['#1B3A6B', '#4CAFDE', '#F0A500']
axes[1].pie(langues.values, labels=langues.index, colors=couleurs,
            autopct='%1.0f%%', startangle=90, textprops={'fontsize': 10})
axes[1].set_title('Repartition des Avis par Langue\n(FR/EN/WO)')

plt.tight_layout()
os.makedirs('data', exist_ok=True)
plt.savefig('data/exploration_initiale.png', dpi=120, bbox_inches='tight')
plt.close()
print("Graphique d'exploration sauvegarde : data/exploration_initiale.png")
print("\nConclusion : la saisonnalite et le Wolof sont deux defis cles du projet.")
