# -*- coding: utf-8 -*-
# nifi_setup.py
# Cree le flow NiFi Teranga-SN via REST API
# Usage : python scripts/nifi_setup.py

import requests
import json
import sys

BASE = "http://localhost:8081/nifi-api"
HEADERS = {"Content-Type": "application/json"}


def get_root_id():
    r = requests.get(f"{BASE}/flow/process-groups/root")
    r.raise_for_status()
    return r.json()["processGroupFlow"]["id"]


def create_processor(group_id, name, proc_type, bundle, x, y, props, schedule="5 sec"):
    body = {
        "revision": {"version": 0},
        "component": {
            "type": proc_type,
            "bundle": bundle,
            "name": name,
            "position": {"x": x, "y": y},
            "config": {
                "schedulingPeriod": schedule,
                "schedulingStrategy": "TIMER_DRIVEN",
                "properties": props,
                "autoTerminatedRelationships": [],
            },
        },
    }
    r = requests.post(
        f"{BASE}/process-groups/{group_id}/processors",
        headers=HEADERS,
        data=json.dumps(body),
    )
    if r.status_code not in (200, 201):
        print(f"  ERREUR creation {name}: {r.status_code} - {r.text[:200]}")
        return None
    comp = r.json()
    print(f"  OK  {name}  [{comp['id']}]")
    return comp


def connect(group_id, src_id, dst_id, relationship, src_type="PROCESSOR", dst_type="PROCESSOR"):
    body = {
        "revision": {"version": 0},
        "component": {
            "source": {"id": src_id, "groupId": group_id, "type": src_type},
            "destination": {"id": dst_id, "groupId": group_id, "type": dst_type},
            "selectedRelationships": [relationship],
            "backPressureObjectThreshold": 10000,
            "backPressureDataSizeThreshold": "1 GB",
        },
    }
    r = requests.post(
        f"{BASE}/process-groups/{group_id}/connections",
        headers=HEADERS,
        data=json.dumps(body),
    )
    if r.status_code not in (200, 201):
        print(f"  ERREUR connexion {src_id}->{dst_id}: {r.status_code} - {r.text[:200]}")
        return None
    print(f"  OK  connexion {relationship}")
    return r.json()


def start_processor(proc_id, revision):
    body = {
        "revision": revision,
        "component": {"id": proc_id, "state": "RUNNING"},
    }
    r = requests.put(
        f"{BASE}/processors/{proc_id}/run-status",
        headers=HEADERS,
        data=json.dumps(body),
    )
    return r.status_code in (200, 201)


def auto_terminate(proc_id, revision, relationship):
    """Auto-termine une relation pour eviter les warnings."""
    r = requests.get(f"{BASE}/processors/{proc_id}")
    if r.status_code != 200:
        return
    proc = r.json()
    config = proc["component"]["config"]
    config["autoTerminatedRelationships"] = [relationship]
    body = {
        "revision": proc["revision"],
        "component": {"id": proc_id, "config": config},
    }
    requests.put(f"{BASE}/processors/{proc_id}", headers=HEADERS, data=json.dumps(body))


# ── Main ─────────────────────────────────────────────────────

print("\nConfiguration NiFi Teranga-SN")
print("=" * 40)

root_id = get_root_id()
print(f"Root group : {root_id}\n")

KAFKA_BUNDLE = {
    "group": "org.apache.nifi",
    "artifact": "nifi-kafka-2-6-nar",
    "version": "1.23.2",
}
STD_BUNDLE = {
    "group": "org.apache.nifi",
    "artifact": "nifi-standard-nar",
    "version": "1.23.2",
}

AVIS_JSON = """{
  "avis_id": "${UUID()}",
  "user_id": "USR_${random():mod(9999):plus(1000)}",
  "email_client": "user${random():mod(999)}@test.sn",
  "destination": "DAKAR",
  "type_activite": "CULTURE",
  "nationalite": "FR",
  "note": ${random():mod(3):plus(3)}.0,
  "texte_avis": "Sejour magnifique, teranga incroyable !",
  "langue": "FR",
  "plateforme": "TRIPADVISOR",
  "timestamp": "${now():format('yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\'')}\"
}"""

ECOMM_JSON = """{
  "transaction_id": "${UUID()}",
  "user_id": "USR_${random():mod(9999):plus(1000)}",
  "categorie": "ALIMENTATION",
  "montant_fcfa": ${random():mod(50000):plus(5000)}.0,
  "region_livraison": "DAKAR",
  "plateforme": "JUMIA",
  "timestamp": "${now():format('yyyy-MM-dd\\'T\\'HH:mm:ss\\'Z\\'')}\"
}"""

print("Creation des processors...")

p_gen_avis = create_processor(
    root_id, "GenerateFlowFile - Avis Touristiques",
    "org.apache.nifi.processors.standard.GenerateFlowFile",
    STD_BUNDLE, 200, 150,
    {"Custom Text": AVIS_JSON, "Unique FlowFiles": "true", "Batch Size": "1"},
    schedule="5 sec",
)

p_gen_ecomm = create_processor(
    root_id, "GenerateFlowFile - E-commerce",
    "org.apache.nifi.processors.standard.GenerateFlowFile",
    STD_BUNDLE, 200, 400,
    {"Custom Text": ECOMM_JSON, "Unique FlowFiles": "true", "Batch Size": "1"},
    schedule="3 sec",
)

p_kafka_avis = create_processor(
    root_id, "PublishKafka - teranga_avis_raw",
    "org.apache.nifi.processors.kafka.pubsub.PublishKafka_2_6",
    KAFKA_BUNDLE, 600, 150,
    {
        "bootstrap.servers": "kafka:9092",
        "topic": "teranga_avis_raw",
        "Delivery Guarantee": "Best Effort",
        "Client Name": "teranga-nifi-avis",
    },
    schedule="0 sec",
)

p_kafka_ecomm = create_processor(
    root_id, "PublishKafka - teranga_arrivees_raw",
    "org.apache.nifi.processors.kafka.pubsub.PublishKafka_2_6",
    KAFKA_BUNDLE, 600, 400,
    {
        "bootstrap.servers": "kafka:9092",
        "topic": "teranga_arrivees_raw",
        "Delivery Guarantee": "Best Effort",
        "Client Name": "teranga-nifi-ecomm",
    },
    schedule="0 sec",
)

if not all([p_gen_avis, p_gen_ecomm, p_kafka_avis, p_kafka_ecomm]):
    print("\nErreur : certains processors n ont pas ete crees. Arret.")
    sys.exit(1)

avis_id   = p_gen_avis["id"]
ecomm_id  = p_gen_ecomm["id"]
kavis_id  = p_kafka_avis["id"]
kecomm_id = p_kafka_ecomm["id"]

print("\nCreation des connexions...")
connect(root_id, avis_id,   kavis_id,  "success")
connect(root_id, ecomm_id,  kecomm_id, "success")
connect(root_id, kavis_id,  avis_id,   "failure")
connect(root_id, kecomm_id, ecomm_id,  "failure")

print("\nConfiguration auto-terminate des relations 'success' des PublishKafka...")
auto_terminate(kavis_id,  None, "success")
auto_terminate(kecomm_id, None, "success")

print("\nDemarrage des processors...")
for proc in [p_gen_avis, p_gen_ecomm, p_kafka_avis, p_kafka_ecomm]:
    ok = start_processor(proc["id"], proc["revision"])
    state = "RUNNING" if ok else "ERREUR"
    print(f"  {state}  {proc['component']['name']}")

print("\nFlow Teranga-SN configure avec succes !")
print(f"Ouvre http://localhost:8081/nifi pour voir le canvas")
