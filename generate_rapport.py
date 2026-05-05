# generate_rapport.py
# Generation du rapport final Teranga-SN en Word
# NDIAYE Papa Malick - Eq.12 - Master 2 DSGL UADB 2025-2026

from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
OUT_PATH = os.path.join(BASE_DIR, 'rapport_teranga_sn.docx')

BLEU     = RGBColor(0x1B, 0x3A, 0x6B)
BLEU_CLR = RGBColor(0x2E, 0x74, 0xB5)
GRIS     = RGBColor(0x60, 0x60, 0x60)
BLANC    = RGBColor(0xFF, 0xFF, 0xFF)


def set_col_width(table, col_idx, width_cm):
    for row in table.rows:
        row.cells[col_idx].width = Cm(width_cm)


def titre_para(doc, texte, niveau=1, couleur=None):
    h = doc.add_heading(texte, level=niveau)
    for run in h.runs:
        run.font.color.rgb = couleur or BLEU
        if niveau == 1:
            run.font.size = Pt(16)
            run.bold = True
        elif niveau == 2:
            run.font.size = Pt(13)
            run.bold = True
        else:
            run.font.size = Pt(11)
    return h


def para(doc, texte, taille=11, gras=False, couleur=None, italique=False, alignement=None):
    p = doc.add_paragraph()
    if alignement:
        p.alignment = alignement
    run = p.add_run(texte)
    run.font.size = Pt(taille)
    run.bold = gras
    run.italic = italique
    if couleur:
        run.font.color.rgb = couleur
    return p


def ligne_vide(doc):
    doc.add_paragraph('')


def ajouter_tableau(doc, headers, rows, col_widths=None):
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = 'Table Grid'
    # En-tete
    hdr = table.rows[0]
    for i, h in enumerate(headers):
        cell = hdr.cells[i]
        cell.text = h
        run = cell.paragraphs[0].runs[0]
        run.bold = True
        run.font.color.rgb = BLANC
        run.font.size = Pt(10)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        shading = OxmlElement('w:shd')
        shading.set(qn('w:fill'), '1B3A6B')
        shading.set(qn('w:color'), 'auto')
        shading.set(qn('w:val'), 'clear')
        cell._tc.get_or_add_tcPr().append(shading)
    # Donnees
    for r_idx, row_data in enumerate(rows):
        row = table.rows[r_idx + 1]
        bg = 'EBF0F8' if r_idx % 2 == 0 else 'FFFFFF'
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = str(val)
            cell.paragraphs[0].runs[0].font.size = Pt(10)
            shading = OxmlElement('w:shd')
            shading.set(qn('w:fill'), bg)
            shading.set(qn('w:color'), 'auto')
            shading.set(qn('w:val'), 'clear')
            cell._tc.get_or_add_tcPr().append(shading)
    if col_widths:
        for i, w in enumerate(col_widths):
            set_col_width(table, i, w)
    return table


def ajouter_code(doc, code, titre=None):
    if titre:
        p = doc.add_paragraph()
        run = p.add_run(titre)
        run.font.size = Pt(9)
        run.font.color.rgb = BLEU_CLR
        run.bold = True
        run.italic = True
    p = doc.add_paragraph()
    p.style = 'Normal'
    run = p.add_run(code)
    run.font.name = 'Courier New'
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x20, 0x20, 0x20)
    # Fond gris clair via shading
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), 'F2F2F2')
    pPr.append(shd)
    return p


def page_titre(doc):
    doc.add_picture(os.path.join(DATA_DIR, 'dashboard_teranga_sn.png'), width=Inches(6.0))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    ligne_vide(doc)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run('UNIVERSITE ALIOUNE DIOP DE BAMBEY')
    run.font.size = Pt(13)
    run.bold = True
    run.font.color.rgb = BLEU

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run2 = p2.add_run('Master 2 - Sciences et Gestion du Logiciel et des Donnees')
    run2.font.size = Pt(11)
    run2.font.color.rgb = GRIS

    ligne_vide(doc)

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run3 = p3.add_run('TERANGA-SN')
    run3.font.size = Pt(26)
    run3.bold = True
    run3.font.color.rgb = BLEU

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run4 = p4.add_run('Intelligence Touristique & Economie Numerique au Senegal')
    run4.font.size = Pt(14)
    run4.font.color.rgb = BLEU_CLR

    ligne_vide(doc)

    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run5 = p5.add_run('Projet Final - Big Data Pipeline')
    run5.font.size = Pt(12)
    run5.bold = True

    ligne_vide(doc)

    ajouter_tableau(doc,
        ['Equipe', 'Membres', 'Annee'],
        [['Eq.12', 'NDIAYE Papa Malick  |  TINE Abdoussalam', '2025-2026']],
        col_widths=[3, 9, 3]
    )

    ligne_vide(doc)
    p6 = doc.add_paragraph()
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run6 = p6.add_run('Dakar, mai 2026')
    run6.font.size = Pt(11)
    run6.font.color.rgb = GRIS
    run6.italic = True

    doc.add_page_break()


def section_introduction(doc):
    titre_para(doc, '1. Introduction et Contexte')

    para(doc,
        'Le secteur touristique senegalais represente environ 7% du PIB national et constitue '
        'l\'une des principales sources de devises du pays. Pourtant, la Direction Generale du '
        'Tourisme et des Transports Touristiques (DGTT) dispose de peu d\'outils modernes pour '
        'analyser en temps reel les flux de visiteurs et la reputation des destinations.')

    ligne_vide(doc)

    para(doc,
        'Le projet Teranga-SN repond a ce besoin en construisant une plateforme Big Data complete '
        'qui traite simultanement deux sources de donnees :')

    for item in [
        'Les avis touristiques en trois langues : francais (FR), anglais (EN) et wolof (WO)',
        'Les transactions e-commerce des principales plateformes locales (Jumia, Expat-Dakar, Senmarket)',
    ]:
        p = doc.add_paragraph(item, style='List Bullet')
        p.runs[0].font.size = Pt(11)

    ligne_vide(doc)

    para(doc,
        'Le nom du projet, "Teranga", signifie "hospitalite" en wolof - valeur fondamentale '
        'de la culture senegalaise et atout majeur du tourisme local. C\'est aussi le fil '
        'conducteur de notre approche : construire un systeme qui mesure et protege cette '
        'reputation d\'accueil.')

    ligne_vide(doc)
    titre_para(doc, '1.1 Objectifs du projet', niveau=2)

    ajouter_tableau(doc,
        ['Objectif', 'Description', 'Technologie'],
        [
            ['Ingestion temps reel', 'Collecter les avis et transactions en continu', 'Apache Kafka + NiFi'],
            ['Analyse NLP multilingue', 'Scorer le sentiment en FR/EN/WO', 'Spark Streaming + Lexique'],
            ['Privacy by Design', 'Anonymiser les donnees personnelles', 'SHA-256 + Pandera'],
            ['Stockage analytique', 'Persister pour requetes SQL et NoSQL', 'HBase + Hive ORC'],
            ['Prediction flux', 'Prevoir les arrivees touristiques', 'Random Forest + MLflow'],
            ['Orchestration', 'Monitorer et reagir automatiquement', 'Airflow DAG'],
            ['Visualisation', 'Tableau de bord pour la DGTT', 'Matplotlib + Seaborn'],
        ],
        col_widths=[4, 7, 5]
    )
    doc.add_page_break()


def section_architecture(doc):
    titre_para(doc, '2. Architecture Technique')

    para(doc,
        'L\'architecture Teranga-SN suit un pattern Lambda simplifie, avec une couche de '
        'traitement en flux (speed layer) et une couche de stockage analytique (serving layer). '
        'L\'ensemble est orchestre par Apache Airflow et deploye dans des conteneurs Docker.')

    ligne_vide(doc)
    titre_para(doc, '2.1 Vue d\'ensemble', niveau=2)

    ajouter_tableau(doc,
        ['Couche', 'Role', 'Services', 'Port'],
        [
            ['Ingestion', 'Collecte des donnees brutes', 'Kafka + NiFi', '9093 / 8081'],
            ['Traitement', 'NLP, anonymisation, agregation', 'Spark Structured Streaming', 'interne'],
            ['Validation', 'Controle qualite et PII', 'Pandera schemas', 'local'],
            ['Stockage NoSQL', 'Donnees analytiques temps reel', 'HBase Thrift', '9090'],
            ['Stockage SQL', 'Entrepot de donnees partitionne', 'Hive HiveServer2', '10000'],
            ['ML', 'Prediction flux touristiques', 'Scikit-learn + MLflow', 'local'],
            ['Orchestration', 'Scheduling et monitoring', 'Airflow', '8082'],
            ['Visualisation', 'Dashboard decision DGTT', 'Matplotlib + Seaborn', 'fichier PNG'],
        ],
        col_widths=[3.5, 5, 4.5, 3]
    )

    ligne_vide(doc)
    titre_para(doc, '2.2 Infrastructure Docker', niveau=2)

    para(doc,
        'Tous les services sont definis dans un seul fichier docker-compose.yml et communiquent '
        'sur un reseau prive teranga-net. Le tableau suivant recapitule l\'etat de chaque '
        'service apres demarrage :')

    ligne_vide(doc)

    ajouter_tableau(doc,
        ['Conteneur', 'Image', 'Etat', 'Ports exposes'],
        [
            ['teranga-zookeeper', 'confluentinc/cp-zookeeper:7.4.0', 'healthy', '2181'],
            ['teranga-kafka', 'confluentinc/cp-kafka:7.4.0', 'healthy', '9092, 9093'],
            ['teranga-nifi', 'apache/nifi:1.23.2', 'running', '8081'],
            ['teranga-hbase', 'harisekhon/hbase:2.1', 'healthy', '9090, 16010'],
            ['teranga-hive', 'apache/hive:3.1.3', 'running', '10000'],
            ['teranga-spark-master', 'apache/spark:latest (4.1.1)', 'running', '8080, 7077'],
            ['teranga-spark-worker', 'apache/spark:latest (4.1.1)', 'running', 'interne'],
            ['teranga-airflow', 'apache/airflow:2.7.3', 'running', '8082'],
        ],
        col_widths=[4.5, 5.5, 2.5, 3.5]
    )
    doc.add_page_break()


def section_kafka(doc):
    titre_para(doc, '3. Ingestion des Donnees : Kafka et NiFi')

    titre_para(doc, '3.1 Architecture Kafka', niveau=2)
    para(doc,
        'Apache Kafka sert de bus de messages central. Deux topics sont utilises :')

    ajouter_tableau(doc,
        ['Topic', 'Producteur', 'Contenu', 'Volume estime'],
        [
            ['teranga_avis_raw', 'kafka_producer_teranga_sn.py / NiFi', 'Avis touristiques JSON (FR/EN/WO)', '~1 msg / 3s'],
            ['teranga_arrivees_raw', 'kafka_producer_teranga_sn.py', 'Transactions e-commerce + arrivees DGTT', '~2 msg / 3s'],
        ],
        col_widths=[4.5, 4.5, 5, 3]
    )

    ligne_vide(doc)
    para(doc, 'Exemple de message brut dans teranga_avis_raw (avant anonymisation) :')
    ajouter_code(doc,
        '{\n'
        '  "avis_id": "b29b6f5d-5762-44b4-a449-3f5267bcbd11",\n'
        '  "user_id": "USR_27f989caa4",         <- PII a supprimer\n'
        '  "email_client": "user1680@test.sn",   <- PII a supprimer\n'
        '  "destination": "TOUBA",\n'
        '  "type_activite": "PELERINAGE",\n'
        '  "note": 1.4,\n'
        '  "texte_avis": "Arnaque taxi, prix non affiche a l\'avance",\n'
        '  "langue": "FR",\n'
        '  "timestamp": "2026-05-05T18:41:22Z"\n'
        '}'
    )

    ligne_vide(doc)
    titre_para(doc, '3.2 Flux NiFi', niveau=2)
    para(doc,
        'Apache NiFi (accessible sur localhost:8081, identifiants admin/teranga2025!) '
        'orchestre l\'ingestion depuis des sources externes (API TripAdvisor, flux RSS). '
        'Le template NiFi exporte (nifi_templates/template_nifi_eq12.xml) contient '
        'trois processors : GenerateFlowFile, PublishKafka (avis), PublishKafka (arrivees).')

    doc.add_page_break()


def section_spark(doc):
    titre_para(doc, '4. Traitement Spark Structured Streaming')

    para(doc,
        'Le coeur du traitement est realise par Apache Spark Structured Streaming. '
        'Trois queries tournent en parallele sur le cluster Spark (Master: localhost:8080).')

    ligne_vide(doc)
    titre_para(doc, '4.1 Privacy by Design : anonymisation SHA-256', niveau=2)

    para(doc,
        'Conformement au RGPD, les donnees personnelles (user_id, email_client) sont '
        'traitees des leur arrivee dans le pipeline. L\'identifiant est remplace par '
        'un hash SHA-256 irreversible avec sel cryptographique :')

    ajouter_code(doc,
        '# user_id -> SHA-256(user_id + sel) -> user_secure\n'
        '.withColumn("user_secure",\n'
        '    sha2(concat(col("user_id"), lit(SALT)), 256))\n'
        '.drop("user_id", "email_client")   # suppression immediate du PII',
        titre='Anonymisation dans streaming_teranga_sn.py'
    )

    para(doc,
        'Apres cette transformation, user_secure est un hash de 64 caracteres hexadecimaux '
        'qui permet de detecter les doublons sans jamais exposer l\'identite reelle.')

    ligne_vide(doc)
    titre_para(doc, '4.2 Analyse de sentiment NLP', niveau=2)

    para(doc,
        'L\'analyse de sentiment utilise une approche lexicale adaptee au domaine touristique '
        'senegalais. Le lexique couvre trois langues :')

    ajouter_tableau(doc,
        ['Langue', 'Termes positifs (exemples)', 'Termes negatifs (exemples)'],
        [
            ['Francais (FR)', 'magnifique (+0.90), teranga (+0.80), excellent (+0.90)', 'arnaque (-0.90), sale (-0.80), decevant (-0.70)'],
            ['Anglais (EN)', 'amazing (+0.90), paradise (+0.90), beautiful (+0.80)', 'disappointed (-0.70), dirty (-0.80), rude (-0.75)'],
            ['Wolof (WO)', 'dafa baax (+0.90), rafet (+0.80), baax (+0.85)', 'dafa neka (-0.80), amul solo (-0.70)'],
        ],
        col_widths=[3, 7, 6]
    )

    ligne_vide(doc)
    para(doc, 'Resultats du test lexical sur 5 avis :')

    ajouter_tableau(doc,
        ['Langue', 'Extrait de l\'avis', 'Score', 'Label'],
        [
            ['FR', 'Magnifique sejour, teranga incroyable !', '+1.70', 'POSITIF'],
            ['EN', 'Too many touts, disappointed', '-1.20', 'NEGATIF'],
            ['WO', 'Dafa baax torop, rafet na', '+2.55', 'POSITIF'],
            ['FR', 'Plage sale, arnaque taxi', '-1.70', 'NEGATIF'],
            ['EN', 'Amazing beaches, would recommend!', '+1.65', 'POSITIF'],
        ],
        col_widths=[2, 8, 2.5, 3.5]
    )

    ligne_vide(doc)
    titre_para(doc, '4.3 Agregation reputation (fenetre glissante)', niveau=2)

    para(doc,
        'La reputation de chaque destination est calculee sur une fenetre glissante de '
        '7 jours avec un pas d\'1 jour. Le watermark de 1 jour evite les fuites memoire '
        'en ignorant les evenements arrives avec plus d\'un jour de retard.')

    ajouter_code(doc,
        'reputation_df = (\n'
        '    avis_df\n'
        '    .withWatermark("event_ts", "1 day")\n'
        '    .groupBy(window("event_ts", "7 days", "1 day"), "destination")\n'
        '    .agg(\n'
        '        avg("note").alias("note_moy"),\n'
        '        avg("sentiment_score").alias("sentiment_moy"),\n'
        '        count("avis_id").alias("nb_avis"),\n'
        '    )\n'
        '    .withColumn("statut_reputation",\n'
        '        when(col("sentiment_moy") < -0.3, "ROUGE")\n'
        '        .when(col("sentiment_moy") < 0.0,  "ORANGE")\n'
        '        .otherwise("VERT")\n'
        '    )\n'
        ')'
    )

    doc.add_page_break()


def section_hbase_hive(doc):
    titre_para(doc, '5. Stockage : HBase et Hive')

    titre_para(doc, '5.1 HBase - Stockage NoSQL temps reel', niveau=2)

    para(doc,
        'HBase stocke les donnees a haute velocite pour les requetes operationnelles. '
        'Trois tables ont ete creees dans le namespace "teranga" :')

    ajouter_tableau(doc,
        ['Table HBase', 'Familles de colonnes', 'Usage'],
        [
            ['teranga:avis_analyses', 'meta, sentiment, geo', 'Avis enrichis apres Spark'],
            ['teranga:alertes_reputation', 'alerte', 'Destinations ROUGE/ORANGE pour le DAG Airflow'],
            ['teranga:stats_ecommerce', 'stats, meta', 'Agregats e-commerce par destination'],
        ],
        col_widths=[5, 5, 6]
    )

    ligne_vide(doc)
    para(doc, 'Validation d\'ecriture et lecture dans HBase (test realise) :')
    ajouter_code(doc,
        '# Ecriture\n'
        'table.put(b"TOUBA_20260505_001", {\n'
        '    b"meta:destination":  b"TOUBA",\n'
        '    b"sentiment:label":   b"NEGATIF",\n'
        '    b"sentiment:score":   b"-0.9",\n'
        '    b"geo:nationalite":   b"ES",\n'
        '})\n'
        '# Lecture => 9 colonnes restituees correctement'
    )

    ligne_vide(doc)
    titre_para(doc, '5.2 Hive - Entrepot analytique', niveau=2)

    para(doc,
        'Hive stocke les donnees historiques dans un format colonnaire optimise '
        '(ORC + compression SNAPPY) pour les requetes analytiques lentes.')

    ajouter_tableau(doc,
        ['Objet Hive', 'Type', 'Caracteristiques'],
        [
            ['avis_analyses', 'TABLE', 'ORC + SNAPPY, partitionnee par date_obs'],
            ['ecommerce_transactions', 'TABLE', 'ORC, non partitionnee'],
            ['vue_destinations', 'VIEW', 'Reputation 30 derniers jours, statut ROUGE/ORANGE/VERT'],
            ['vue_ecommerce', 'VIEW', 'Top categories par region, CA total en FCFA'],
        ],
        col_widths=[5, 2.5, 8.5]
    )

    doc.add_page_break()


def section_validation(doc):
    titre_para(doc, '6. Validation et Tests')

    titre_para(doc, '6.1 Tests unitaires Pandera (10/10)', niveau=2)

    para(doc,
        'Le module Pandera valide la qualite des donnees et s\'assure qu\'aucune information '
        'personnelle (PII) ne passe dans les couches de stockage. Dix tests sont definis :')

    ajouter_tableau(doc,
        ['Test', 'Scenario', 'Resultat'],
        [
            ['test_avis_valide', 'DataFrame conforme aux contraintes', 'PASSED'],
            ['test_avis_note_hors_intervalle', 'note = 6.0 (> 5.0)', 'PASSED'],
            ['test_avis_destination_inconnue', 'destination = "PARIS"', 'PASSED'],
            ['test_avis_pii_user_id_detecte', 'user_id present dans le DataFrame', 'PASSED'],
            ['test_avis_pii_email_detecte', 'email_client present dans le DataFrame', 'PASSED'],
            ['test_avis_sentiment_label_invalide', 'label = "TRES_POSITIF"', 'PASSED'],
            ['test_ecomm_valide', 'Transaction e-commerce conforme', 'PASSED'],
            ['test_ecomm_montant_negatif', 'montant_fcfa = -500.0', 'PASSED'],
            ['test_ecomm_categorie_inconnue', 'categorie = "VOITURE"', 'PASSED'],
            ['test_ecomm_pii_user_id_detecte', 'user_id present (e-commerce)', 'PASSED'],
        ],
        col_widths=[5.5, 6, 2.5]
    )

    ligne_vide(doc)
    ajouter_code(doc,
        '$ python -m pytest tests/ -v\n'
        '======================== 10 passed, 1 warning in 1.56s ========================'
    )

    ligne_vide(doc)
    titre_para(doc, '6.2 Validation du pipeline Kafka', niveau=2)

    para(doc,
        'Le producteur Kafka a ete teste et les messages arrivent correctement dans les deux topics :')

    ajouter_tableau(doc,
        ['Topic', 'Messages', 'Contenu verifie'],
        [
            ['teranga_avis_raw', '8 messages', 'JSON valide, user_id et email presents (a anonymiser)'],
            ['teranga_arrivees_raw', '10 messages', 'Transactions e-commerce + arrivees DGTT'],
        ],
        col_widths=[5, 3, 8]
    )

    ligne_vide(doc)
    titre_para(doc, '6.3 Validation HBase end-to-end', niveau=2)

    para(doc,
        'Un test complet d\'ecriture et lecture dans HBase a ete realise pour simuler '
        'ce que Spark produirait apres traitement. La lecture restitue correctement les '
        '9 colonnes ecrites avec leurs valeurs exactes.')

    doc.add_page_break()


def section_ml(doc):
    titre_para(doc, '7. Machine Learning : Prediction des Flux Touristiques')

    para(doc,
        'Un modele Random Forest predit le nombre quotidien de touristes par destination '
        'en fonction des caracteristiques saisonnieres et de la qualite perçue.')

    ligne_vide(doc)
    titre_para(doc, '7.1 Features et donnees d\'entrainement', niveau=2)

    ajouter_tableau(doc,
        ['Feature', 'Type', 'Description'],
        [
            ['destination_enc', 'categorielle encodee', '7 destinations senegalaises'],
            ['nationalite_enc', 'categorielle encodee', '8 nationalites principales'],
            ['type_activite_enc', 'categorielle encodee', '6 types d\'activite'],
            ['mois', 'numerique (1-12)', 'Capture la saisonnalite'],
            ['note_moy', 'numerique [2.5, 5.0]', 'Note moyenne de la destination'],
            ['sentiment_moy', 'numerique [-0.8, 0.9]', 'Score sentiment agregee'],
        ],
        col_widths=[5, 4, 7]
    )

    ligne_vide(doc)
    para(doc,
        'Le dataset d\'entrainement est genere a partir de regles metier calees sur '
        'la realite senegalaise : haute saison novembre-mars (+150 touristes/jour), '
        'bonus pour Dakar/Saly/Saint-Louis (+100), plus un bruit gaussien (sigma=30).')

    ligne_vide(doc)
    titre_para(doc, '7.2 Resultats du modele', niveau=2)

    ajouter_tableau(doc,
        ['Metrique', 'Valeur', 'Interpretation'],
        [
            ['RMSE', '31.23 touristes/jour', 'Erreur moyenne de prediction'],
            ['R2 (test set)', '0.9005', 'Le modele explique 90% de la variance'],
            ['R2 (cross-val 5-fold)', '0.8989', 'Bonne generalisation, pas de sur-apprentissage'],
            ['Dataset', '5000 observations', '80% train / 20% test'],
            ['Hyperparametres', 'n_estimators=150, max_depth=10', 'Optimises manuellement'],
        ],
        col_widths=[5, 5, 6]
    )

    ligne_vide(doc)
    para(doc,
        'Le suivi des experiences est assure par MLflow. Chaque entrainement logue '
        'automatiquement les parametres, les metriques et le modele serialise. '
        'En production, le DAG Airflow declenche un reentainement si plus d\'une '
        'destination passe en statut ROUGE.')

    doc.add_page_break()


def section_airflow(doc):
    titre_para(doc, '8. Orchestration : DAG Airflow')

    para(doc,
        'Le DAG teranga_sn_monitoring s\'execute chaque lundi a 07h00 et suit '
        'une logique de branchement conditionnelle (MLOps) :')

    ligne_vide(doc)

    ajouter_tableau(doc,
        ['Tache', 'Type', 'Action'],
        [
            ['start', 'DummyOperator', 'Point d\'entree du workflow'],
            ['check_reputation', 'BranchPythonOperator', 'Compte destinations ROUGE dans Hive'],
            ['retrain_model', 'PythonOperator', 'spark-submit train_flux_model.py si n_rouge > 1'],
            ['update_dashboard', 'PythonOperator', 'Ecrit alertes ROUGE/ORANGE dans HBase'],
            ['generer_rapport_semaine', 'PythonOperator', 'Export JSON des KPIs hebdomadaires'],
            ['end', 'DummyOperator', 'Point de sortie (trigger_rule: none_failed)'],
        ],
        col_widths=[4.5, 4.5, 7]
    )

    ligne_vide(doc)
    para(doc,
        'L\'interface Airflow est accessible sur http://localhost:8082 '
        '(identifiants : admin / admin). Le DAG apparait dans la liste avec le tag '
        '"teranga-sn".')

    doc.add_page_break()


def section_dashboard(doc):
    titre_para(doc, '9. Dashboard de Visualisation')

    para(doc,
        'Le tableau de bord genere par dashboard_teranga_sn.py presente quatre panneaux '
        'destines aux decideurs de la DGTT. Il fonctionne en mode demonstration si Hive '
        'n\'est pas disponible.')

    ligne_vide(doc)

    ajouter_tableau(doc,
        ['Panneau', 'Type de graphe', 'Indicateur'],
        [
            ['1 (haut gauche)', 'Barres horizontales colorees', 'Note moyenne par destination - couleur selon statut reputation'],
            ['2 (haut droite)', 'Barres groupees', '% avis positifs vs negatifs par destination'],
            ['3 (bas gauche)', 'Barres horizontales', 'CA e-commerce par categorie (millions FCFA)'],
            ['4 (bas droite)', 'Heatmap', 'CA par region x categorie de produit'],
        ],
        col_widths=[3.5, 4, 8.5]
    )

    ligne_vide(doc)

    img_path = os.path.join(DATA_DIR, 'dashboard_teranga_sn.png')
    if os.path.exists(img_path):
        doc.add_picture(img_path, width=Inches(6.2))
        p = doc.paragraphs[-1]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap = doc.add_paragraph('Figure 1 - Dashboard Teranga-SN (mode demonstration)')
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.runs[0].font.size = Pt(9)
        cap.runs[0].italic = True
        cap.runs[0].font.color.rgb = GRIS

    doc.add_page_break()


def section_conclusion(doc):
    titre_para(doc, '10. Conclusion et Perspectives')

    para(doc,
        'Le projet Teranga-SN constitue une demonstration complete d\'une architecture '
        'Big Data moderne appliquee au secteur touristique senegalais. En trois semaines '
        'de developpement, l\'equipe Eq.12 a mis en place :')

    for item in [
        '8 services Docker integres et valides (Kafka, NiFi, HBase, Hive, Spark, Airflow)',
        'Un pipeline de traitement NLP multilingue (FR/EN/WO) avec Privacy by Design',
        'Un modele de prediction Random Forest avec R2=0.90 et suivi MLflow',
        'Une suite de 10 tests Pandera garantissant la qualite des donnees',
        'Un tableau de bord interactif pour la DGTT',
    ]:
        p = doc.add_paragraph(item, style='List Bullet')
        p.runs[0].font.size = Pt(11)

    ligne_vide(doc)
    titre_para(doc, '10.1 Points d\'amelioration identifies', niveau=2)

    ajouter_tableau(doc,
        ['Axe', 'Amelioration possible'],
        [
            ['Lexique Wolof', 'Enrichissement avec des locuteurs natifs (tache binome Abdoussalam)'],
            ['NLP', 'Integration d\'un modele transformeur (CamemBERT, XLM-RoBERTa) pour le FR/EN'],
            ['HBase TTL', 'Configurer l\'expiration automatique des alertes apres 7 jours'],
            ['NiFi', 'Connexion directe a l\'API REST TripAdvisor pour les donnees reelles'],
            ['Deploiement', 'Migration vers Kubernetes pour la scalabilite en production'],
        ],
        col_widths=[4, 12]
    )

    ligne_vide(doc)
    para(doc,
        'Ce projet nous a permis de comprendre les enjeux concrets du Big Data applique '
        'a un secteur strategique senegalais. La combinaison Kafka + Spark Streaming + '
        'HBase + Hive forme un socle solide sur lequel des analyses plus profondes '
        'pourront etre construites.',
        italique=True, couleur=GRIS
    )


def main():
    doc = Document()

    # Marges
    for section in doc.sections:
        section.top_margin    = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin   = Cm(2.5)
        section.right_margin  = Cm(2.5)

    # Police par defaut
    doc.styles['Normal'].font.name = 'Calibri'
    doc.styles['Normal'].font.size = Pt(11)

    page_titre(doc)
    section_introduction(doc)
    section_architecture(doc)
    section_kafka(doc)
    section_spark(doc)
    section_hbase_hive(doc)
    section_validation(doc)
    section_ml(doc)
    section_airflow(doc)
    section_dashboard(doc)
    section_conclusion(doc)

    doc.save(OUT_PATH)
    print(f'Rapport genere : {OUT_PATH}')


if __name__ == '__main__':
    main()
