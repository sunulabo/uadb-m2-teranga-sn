# -*- coding: utf-8 -*-
# demo_streaming_output.py
# Simule la sortie console du pipeline Spark Streaming Teranga-SN
# Usage : python scripts/demo_streaming_output.py

import hashlib, time, random, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from lexique import LEXIQUE

SALT = "teranga2025dev"

AVIS = [
    ("USR_1234", "user12@test.sn", "DAKAR",       "FR", "Teranga incroyable, sejour magnifique !",     4.5),
    ("USR_5678", "user56@test.sn", "SAINT-LOUIS",  "EN", "Amazing city, beautiful colonial architecture", 4.8),
    ("USR_9012", "user90@test.sn", "SALY",         "WO", "Dafa baax lool, teranga bi dafa rafet !",     5.0),
    ("USR_3456", "user34@test.sn", "CASAMANCE",    "FR", "Cuisine locale terrible, service mauvais.",   1.5),
    ("USR_7890", "user78@test.sn", "CAP SKIRRING", "WO", "Dafa neka, amul solo, deception totale.",     2.0),
    ("USR_2345", "user23@test.sn", "TOUBA",        "FR", "Experience spirituelle inoubliable, parfait.", 5.0),
    ("USR_6789", "user67@test.sn", "DAKAR",        "EN", "Good food, friendly locals, loved it.",       4.2),
    ("USR_0123", "user01@test.sn", "ZIGUINCHOR",   "FR", "Marche artisanal excellent, tres bon accueil.", 4.6),
]


def score_sentiment(texte, langue):
    tokens = texte.lower().split()
    score = 0.0
    for token in tokens:
        score += LEXIQUE.get(token, 0.0)
    return round(max(-1.0, min(1.0, score)), 4)


def anonymize(user_id):
    return hashlib.sha256((user_id + SALT).encode()).hexdigest()


def label(score):
    if score >= 0.1:
        return "POSITIF"
    elif score <= -0.1:
        return "NEGATIF"
    return "NEUTRE"


print("=" * 72)
print("  Teranga-SN | Spark Structured Streaming | Pipeline NLP FR/EN/WO")
print("=" * 72)
print()

batch = 0
while batch < 3:
    batch += 1
    ts = time.strftime("%H:%M:%S")
    print(f"-------------------------------------------")
    print(f"Batch {batch}  |  {ts}  |  topic: teranga_avis_raw")
    print(f"-------------------------------------------")
    sample = random.sample(AVIS, k=random.randint(3, 5))
    for user_id, email, dest, langue, texte, note in sample:
        score = score_sentiment(texte, langue)
        user_secure = anonymize(user_id)
        print(f"  destination  : {dest:<15}  langue : {langue}")
        print(f"  note         : {note}   sentiment_score : {score:+.4f}  [{label(score)}]")
        print(f"  user_secure  : {user_secure[:32]}...")
        print(f"  PII drop     : email_client=DROPPED  user_id=DROPPED")
        print()
    time.sleep(1.5)

print("-------------------------------------------")
print("Fenetre glissante 7j - Reputation destinations")
print("-------------------------------------------")
reps = [
    ("DAKAR",        0.68,  "VERT"),
    ("SAINT-LOUIS",  0.54,  "VERT"),
    ("SALY",         0.72,  "VERT"),
    ("CASAMANCE",   -0.12,  "ORANGE"),
    ("CAP SKIRRING", -0.41, "ROUGE"),
    ("TOUBA",        0.88,  "VERT"),
    ("ZIGUINCHOR",   0.51,  "VERT"),
]
for dest, score, statut in reps:
    bar = "ALERTE -> teranga_alerts" if statut == "ROUGE" else ""
    print(f"  {dest:<15}  score={score:+.2f}  statut={statut:<6}  {bar}")

print()
print("Pipeline actif. CTRL+C pour arreter.")
