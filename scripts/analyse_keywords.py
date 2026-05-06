# scripts/analyse_keywords.py
# Extraction TF-IDF des mots-cles par destination
# Genere data/keywords_tfidf.json pour le dashboard web

import os
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'data', 'keywords_tfidf.json')
os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)

DESTINATIONS = ['DAKAR', 'SAINT_LOUIS', 'SALY', 'CAP_SKIRRING', 'CASAMANCE', 'TOUBA', 'ZIGUINCHOR']

# Corpus d'avis par destination (simule - remplacer par requete Hive en production)
CORPUS = {
    'DAKAR': [
        'Dakar vivante et chaleureuse marche Sandaga incroyable ambiance unique',
        'Excellent accueil teranga hospitalite remarquable ville dynamique',
        'Cuisine delicieuse thieboudienne yassa poulet restaurant recommend',
        'Trafic intense mais ville fascinante musee IFAN incontournable',
        'Hotel confortable vue mer plage propre personnel sympa service parfait',
        'Arnaque taxi prix abusif touristes beware overpriced disappointed',
        'Amazing city vibrant culture music teranga wonderful people beautiful',
        'Dafa baax torop Dakar neex na lool rafet',
    ],
    'SAINT_LOUIS': [
        'Saint-Louis patrimoine UNESCO architecture coloniale magnifique pont Faidherbe',
        'Jazz festival exceptionnel musique atmosphere unique incontournable culture',
        'Ville historique guide excellent promenade ile calme reposant',
        'Fleuve Senegal coucher soleil superbe pirogue balade paisible',
        'Hotel charme maison coloniale accueil chaleureux personnel professionnel',
        'Dafa rafet lool Saint-Louis neex na yomb',
        'Stunning colonial architecture beautiful river sunset highly recommend',
    ],
    'SALY': [
        'Plage magnifique sable blanc eau turquoise paradis balneare',
        'Resort qualite piscine restaurant buffet excellent service parfait',
        'Animation soiree ambiance festive touristes europeens sympa',
        'Vendeurs plage insistants touts disappointing beach dirty garbage',
        'Beautiful beach wonderful resort recommend famille enfants',
        'Trop cher pour qualite proposee insatisfait overpriced',
        'Saly bees na lool ndox bi set na rafet',
    ],
    'CAP_SKIRRING': [
        'Plage sauvage exceptionnelle nature preservee calme reposant paradis',
        'Ecotourisme authentique population accueillante teranga magnifique',
        'Poissons frais restaurant bord mer cuisine locale delicieuse',
        'Acces difficile route piste mais vaut detour paradise hidden gem',
        'Amazing untouched beach beautiful nature stunning paradise recommend',
        'Dafa baax lool nature bi rafet na ci kanam',
    ],
    'CASAMANCE': [
        'Casamance verte nature luxuriante biodiversite exceptionnelle ecotourisme',
        'Paix retrouvee region magnifique population accueillante teranga',
        'Mangroves pirogue balade faune unique oiseaux migrateurs',
        'Guide excellent connaissance nature authentique sejour inoubliable',
        'Paradise on earth stunning nature beautiful peaceful recommend',
        'Dafa baax torop Casamance rafet na nature bi yomb',
    ],
    'TOUBA': [
        'Pelerinage mouridisme Grande Mosquee impressionnante spiritualite profonde',
        'Ville sainte accueil fraternel partage teranga exceptionnel',
        'Magal Touba evenement spirituel unique rassemblement impressionnant',
        'Organisation remarquable millions pelerins infrastructure serviable',
        'Jaam ak baraka Touba dafa baax lool am na solo',
        'Spiritual journey unique experience respectful welcoming community',
    ],
    'ZIGUINCHOR': [
        'Ville carrefour Casamance marche artisanat batik tissu local',
        'Gastronomie locale poisson frais fruits mer restaurant excellent',
        'Musique casamancaise ambiance festive culture riche diversite',
        'Ambiance tranquille ville a taille humaine accueil chaleureux',
        'Beautiful calm city great food local market authentic culture',
        'Ziguinchor dafa yomb rafet na bees na ci kanam',
    ],
}

STOP_WORDS = {
    'le', 'la', 'les', 'de', 'du', 'des', 'un', 'une', 'et', 'en', 'au', 'aux',
    'par', 'sur', 'dans', 'avec', 'pour', 'est', 'sont', 'mais', 'ou', 'si',
    'the', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'to', 'of', 'is', 'are',
    'na', 'bi', 'ci', 'ba', 'lool', 'torop', 'dafa', 'ni',
}


def extraire_keywords(n_keywords: int = 5) -> dict:
    resultats = {}

    for destination, avis_list in CORPUS.items():
        corpus_dest = ' '.join(avis_list)
        documents   = avis_list

        try:
            vectorizer = TfidfVectorizer(
                stop_words=list(STOP_WORDS),
                max_features=50,
                ngram_range=(1, 2),
                min_df=1,
            )
            tfidf_matrix = vectorizer.fit_transform(documents)
            feature_names = vectorizer.get_feature_names_out()

            scores_moy = np.asarray(tfidf_matrix.mean(axis=0)).flatten()
            top_indices = scores_moy.argsort()[-n_keywords:][::-1]
            keywords = [feature_names[i] for i in top_indices]

        except Exception:
            words = corpus_dest.lower().split()
            words = [w for w in words if w not in STOP_WORDS and len(w) > 3]
            keywords = list(dict.fromkeys(words))[:n_keywords]

        resultats[destination] = keywords
        print(f'{destination}: {keywords}')

    with open(OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)

    print(f'\nKeywords sauvegardes : {OUTPUT}')
    return resultats


if __name__ == '__main__':
    extraire_keywords()
