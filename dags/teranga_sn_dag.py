# dags/teranga_sn_dag.py
# DAG Airflow MLOps Teranga-SN - Eq.12
# Monitoring hebdomadaire : detection derive -> reentainement ou mise a jour dashboard

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.dummy  import DummyOperator
from airflow.utils.dates      import days_ago
from datetime import timedelta
import subprocess
import logging

logger = logging.getLogger('teranga.dag')

default_args = {
    'owner':        'teranga_eq12',
    'retries':      2,
    'retry_delay':  timedelta(minutes=5),
    'email_on_failure': False,
}


def check_reputation(**ctx):
    """
    Verifie le nombre de destinations en statut ROUGE dans Hive.
    Si plus d'une destination critique est detectee, on relance l'entrainement.
    """
    try:
        from pyhive import hive
        conn = hive.Connection(host='hive-metastore', port=10000, database='teranga_sn')
        cur  = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM vue_destinations WHERE statut_reputation = 'ROUGE'"
        )
        n_rouge = cur.fetchone()[0]
        cur.close(); conn.close()

        logger.info(f'Destinations ROUGE : {n_rouge}')
        ctx['ti'].xcom_push(key='n_rouge', value=n_rouge)

        return 'retrain_model' if n_rouge > 1 else 'update_dashboard'

    except Exception as exc:
        logger.error(f'Erreur check_reputation : {exc}')
        return 'update_dashboard'


def retrain_model(**ctx):
    """Soumet le script d'entrainement via spark-submit."""
    n_rouge = ctx['ti'].xcom_pull(key='n_rouge', task_ids='check_reputation')
    logger.info(f'Reentainement declenche - {n_rouge} destinations ROUGE')
    subprocess.run(
        ['spark-submit', '--master', 'spark://spark-master:7077',
         '/opt/models/train_flux_model.py'],
        check=True,
        timeout=3600,
    )


def update_dashboard(**ctx):
    """
    Lit les KPIs depuis Hive et ecrit les alertes ROUGE/ORANGE dans HBase.
    Cette fonction est declenchee apres chaque run, avec ou sans reentainement.
    """
    try:
        import happybase
        from pyhive import hive
        from datetime import datetime

        conn_hive  = hive.Connection(host='hive-metastore', port=10000, database='teranga_sn')
        conn_hbase = happybase.Connection('hbase', port=9090)
        conn_hbase.open()

        cur = conn_hive.cursor()
        cur.execute(
            'SELECT destination, nb_avis_total, note_moy, sentiment_moy, statut_reputation '
            'FROM vue_destinations'
        )
        rows = cur.fetchall()
        cur.close(); conn_hive.close()

        table = conn_hbase.table(b'teranga:alertes_reputation')
        ts    = datetime.utcnow().isoformat().encode()

        for dest, nb, note, sent, statut in rows:
            if statut in ('ROUGE', 'ORANGE'):
                table.put(
                    dest.encode(),
                    {
                        b'alerte:destination': dest.encode(),
                        b'alerte:nb_avis':     str(nb).encode(),
                        b'alerte:note':        str(round(note, 2)).encode(),
                        b'alerte:sentiment':   str(round(sent, 3)).encode(),
                        b'alerte:statut':      statut.encode(),
                        b'alerte:ts':          ts,
                    }
                )
                logger.info(f'Alerte HBase ecrite - {dest} : {statut}')

        conn_hbase.close()
        logger.info('Dashboard mis a jour avec succes')

    except Exception as exc:
        logger.error(f'Erreur update_dashboard : {exc}')
        raise


def generer_rapport_semaine(**ctx):
    """Genere un rapport JSON hebdomadaire des KPIs."""
    import json, os
    from datetime import datetime
    semaine = datetime.utcnow().strftime('%Y-W%W')
    rapport = {
        'semaine':    semaine,
        'dag_run_id': ctx.get('run_id', 'N/A'),
        'statut':     'OK',
        'timestamp':  datetime.utcnow().isoformat(),
    }
    os.makedirs('/opt/models/rapports', exist_ok=True)
    path = f'/opt/models/rapports/rapport_{semaine}.json'
    with open(path, 'w') as f:
        json.dump(rapport, f, indent=2)
    logger.info(f'Rapport hebdo genere : {path}')


# Definition du DAG
with DAG(
    dag_id='teranga_sn_monitoring',
    default_args=default_args,
    schedule_interval='0 7 * * 1',
    start_date=days_ago(1),
    catchup=False,
    tags=['teranga-sn', 'tourisme', 'ecommerce', 'mlops'],
    description='Monitoring hebdomadaire Teranga-SN : reputation + reentainement ML',
) as dag:

    start  = DummyOperator(task_id='start')
    end    = DummyOperator(task_id='end', trigger_rule='none_failed_min_one_success')

    branch = BranchPythonOperator(
        task_id='check_reputation',
        python_callable=check_reputation,
        provide_context=True,
    )

    t_retrain  = PythonOperator(
        task_id='retrain_model',
        python_callable=retrain_model,
        provide_context=True,
    )

    t_dashboard = PythonOperator(
        task_id='update_dashboard',
        python_callable=update_dashboard,
        provide_context=True,
    )

    t_rapport = PythonOperator(
        task_id='generer_rapport_semaine',
        python_callable=generer_rapport_semaine,
        provide_context=True,
        trigger_rule='none_failed_min_one_success',
    )

    # Ordre d'execution
    start >> branch >> [t_retrain, t_dashboard]
    t_retrain  >> t_dashboard
    t_dashboard >> t_rapport >> end
