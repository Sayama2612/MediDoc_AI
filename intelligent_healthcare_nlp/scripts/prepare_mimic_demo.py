"""Prepare a simple labeled CSV for document classification from the MIMIC-IV demo files.
This creates three classes: 'prescription', 'report', 'summary' from available tables.
"""
import os
import gzip
import pandas as pd

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(PROJECT_ROOT, 'data', 'mimic-iv-clinical-database-demo-2.2')
OUTPUT_CSV = os.path.join(PROJECT_ROOT, 'data', 'mimic_demo_dataset.csv')


def read_gz_csv(path):
    return pd.read_csv(path, compression='gzip')


def prepare():
    texts = []
    labels = []

    hosp_dir = os.path.join(DATA_DIR, 'hosp')
    icu_dir = os.path.join(DATA_DIR, 'icu')

    # PRESCRIPTIONS -> prescription
    pres_path = os.path.join(hosp_dir, 'prescriptions.csv.gz')
    if os.path.exists(pres_path):
        try:
            pres = read_gz_csv(pres_path)
            for _, row in pres.head(1000).iterrows():
                # combine fields into a short textual representation
                drug = str(row.get('drug', '') or row.get('drug_name', '') or '')
                dose = str(row.get('dose_val_rx', ''))
                form = str(row.get('form', ''))
                text = f"Prescription: {drug} dose={dose} form={form}"
                texts.append(text)
                labels.append('prescription')
        except Exception as e:
            print('Failed to read prescriptions:', e)

    # LAB/EVENTS -> report
    labs_path = os.path.join(hosp_dir, 'labevents.csv.gz')
    if os.path.exists(labs_path):
        try:
            labs = read_gz_csv(labs_path)
            for _, row in labs.head(1000).iterrows():
                item = row.get('itemid', '')
                val = row.get('valuenum', row.get('value', ''))
                text = f"Lab Report: item={item} value={val}"
                texts.append(text)
                labels.append('report')
        except Exception as e:
            print('Failed to read labevents:', e)

    # ADMISSIONS -> summary
    adm_path = os.path.join(hosp_dir, 'admissions.csv.gz')
    if os.path.exists(adm_path):
        try:
            adm = read_gz_csv(adm_path)
            for _, row in adm.head(1000).iterrows():
                admit = row.get('admittime', '')
                disch = row.get('dischtime', '')
                diag = row.get('diagnosis', '')
                text = f"Admission Summary: admit={admit} discharge={disch} diagnosis={diag}"
                texts.append(text)
                labels.append('summary')
        except Exception as e:
            print('Failed to read admissions:', e)

    if not texts:
        raise SystemExit('No data found in MIMIC demo for preparation')

    df = pd.DataFrame({'text': texts, 'label': labels})
    df.to_csv(OUTPUT_CSV, index=False)
    print('Wrote', OUTPUT_CSV)


if __name__ == '__main__':
    prepare()
