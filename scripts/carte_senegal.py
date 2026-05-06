# scripts/carte_senegal.py
# Carte interactive du Senegal - destinations colorees selon reputation
# Genere data/carte_senegal.html (ouvrir dans un navigateur)

import os
import numpy as np
import folium
from folium import plugins

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'carte_senegal.html')
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

# Coordonnees GPS des destinations
DESTINATIONS = {
    'DAKAR':       {'lat': 14.6928, 'lon': -17.4467},
    'SAINT_LOUIS': {'lat': 16.0179, 'lon': -16.4896},
    'SALY':        {'lat': 14.4598, 'lon': -16.9915},
    'CAP_SKIRRING':{'lat': 12.3900, 'lon': -16.7400},
    'CASAMANCE':   {'lat': 12.5500, 'lon': -15.5000},
    'TOUBA':       {'lat': 14.8500, 'lon': -15.8833},
    'ZIGUINCHOR':  {'lat': 12.5610, 'lon': -16.2719},
}

# Donnees simulees (remplacees par Hive en production)
np.random.seed(42)
noms = list(DESTINATIONS.keys())
sentiments  = np.random.uniform(-0.6, 0.8, len(noms))
notes       = np.clip(3.0 + sentiments * 1.2, 1, 5)
nb_avis     = np.random.randint(80, 800, len(noms))
pct_positif = np.clip(50 + sentiments * 40, 5, 95)
statuts     = ['ROUGE' if s < -0.3 else 'ORANGE' if s < 0 else 'VERT' for s in sentiments]

COULEURS = {'VERT': 'green', 'ORANGE': 'orange', 'ROUGE': 'red'}
ICONES   = {'VERT': 'thumbs-up', 'ORANGE': 'exclamation-sign', 'ROUGE': 'thumbs-down'}


def generer_carte():
    carte = folium.Map(
        location=[14.0, -14.5],
        zoom_start=7,
        tiles='CartoDB positron',
    )

    for i, nom in enumerate(noms):
        coords  = DESTINATIONS[nom]
        statut  = statuts[i]
        couleur = COULEURS[statut]

        popup_html = f"""
        <div style="font-family:sans-serif; min-width:180px;">
          <h6 style="color:#1B3A6B; margin-bottom:8px;">{nom}</h6>
          <table style="width:100%; font-size:13px;">
            <tr><td>Statut</td><td><b style="color:{'#2E8B57' if statut=='VERT' else '#FF8C00' if statut=='ORANGE' else '#DC143C'}">{statut}</b></td></tr>
            <tr><td>Note</td><td><b>{round(float(notes[i]),2)} / 5</b></td></tr>
            <tr><td>Avis</td><td><b>{int(nb_avis[i])}</b></td></tr>
            <tr><td>% Positif</td><td><b>{round(float(pct_positif[i]),1)}%</b></td></tr>
            <tr><td>Sentiment</td><td><b>{round(float(sentiments[i]),3)}</b></td></tr>
          </table>
        </div>
        """

        folium.Marker(
            location=[coords['lat'], coords['lon']],
            popup=folium.Popup(popup_html, max_width=220),
            tooltip=f"{nom} - {statut}",
            icon=folium.Icon(color=couleur, icon=ICONES[statut], prefix='glyphicon'),
        ).add_to(carte)

    # Legende
    legende_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:12px 16px; border-radius:8px;
                box-shadow:0 2px 8px rgba(0,0,0,.2); font-family:sans-serif; font-size:13px;">
      <div style="font-weight:700; color:#1B3A6B; margin-bottom:8px;">Reputation</div>
      <div style="margin:4px 0;"><span style="color:green; font-size:16px;">&#9679;</span> VERT - Satisfaisant</div>
      <div style="margin:4px 0;"><span style="color:orange; font-size:16px;">&#9679;</span> ORANGE - Attention</div>
      <div style="margin:4px 0;"><span style="color:red; font-size:16px;">&#9679;</span> ROUGE - Critique</div>
      <hr style="margin:8px 0;">
      <div style="color:#888; font-size:11px;">Teranga-SN Eq.12 - UADB 2025</div>
    </div>
    """
    carte.get_root().html.add_child(folium.Element(legende_html))

    titre_html = """
    <div style="position:fixed; top:10px; left:50%; transform:translateX(-50%); z-index:1000;
                background:#1B3A6B; color:white; padding:8px 20px; border-radius:20px;
                font-family:sans-serif; font-size:14px; font-weight:600; box-shadow:0 2px 6px rgba(0,0,0,.3);">
      Teranga-SN &mdash; Carte de Reputation Touristique du Senegal
    </div>
    """
    carte.get_root().html.add_child(folium.Element(titre_html))

    carte.save(OUTPUT)
    print(f'Carte generee : {OUTPUT}')
    return OUTPUT


if __name__ == '__main__':
    generer_carte()
