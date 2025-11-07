"""Train a tiny spaCy NER model on synthetic data for medical fields.

Creates a model directory at `models/ner_model`.

Notes:
- This script requires `spacy` to be installed. If spaCy is not available,
  the script will exit with an informative message.
- The synthetic dataset is small and intended for demo purposes only — use
  a larger human-annotated corpus for production-quality models.

Usage:
  python scripts/train_ner_demo.py
"""
from pathlib import Path
import json
import random
import sys


MODEL_DIR = Path(__file__).resolve().parents[1] / 'models' / 'ner_model'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

examples = [
    ("Patient John Doe, a 45-year-old male, was admitted on 2025-01-10 with chest pain.",
     [(8, 16, 'PATIENT_NAME'), (19, 21, 'AGE'), (31, 35, 'GENDER'), (51, 61, 'ADMISSION_DATE'), (66, 75, 'DIAGNOSIS')]),
    ("Jane Smith (F, 29) was discharged 2025-01-15. Diagnosis: acute bronchitis.",
     [(0, 10, 'PATIENT_NAME'), (12, 13, 'GENDER'), (15, 17, 'AGE'), (31, 41, 'DISCHARGE_DATE'), (52, 68, 'DIAGNOSIS')]),
    ("Admitted: 2025-02-01. Name: Alan Turing Age: 41 Diagnosis: postoperative infection. Medication: amoxicillin 500 mg twice daily.",
     [(10, 20, 'ADMISSION_DATE'), (28, 39, 'PATIENT_NAME'), (46, 48, 'AGE'), (60, 83, 'DIAGNOSIS'), (97, 126, 'MEDICATION')]),
    ("Patient: Mary Johnson, female, 72 years. Discharge: 2025-03-02. Meds: aspirin 81 mg.",
     [(9, 21, 'PATIENT_NAME'), (23, 29, 'GENDER'), (31, 33, 'AGE'), (45, 55, 'DISCHARGE_DATE'), (62, 73, 'MEDICATION')]),
    ("DX: Type II diabetes. Patient name: Carlos Ruiz. Start metformin 500 mg daily on 2025-04-12.",
     [(4, 22, 'DIAGNOSIS'), (24, 36, 'PATIENT_NAME'), (44, 75, 'MEDICATION'), (76, 86, 'ADMISSION_DATE')])
]

try:
    import spacy
    from spacy.training import Example
except Exception:
    print("spaCy is not installed in this environment. Install it with: pip install spacy", file=sys.stderr)
    sys.exit(2)


def build_training_data(examples):
    # Convert examples into spaCy training format
    train_data = []
    for text, ents in examples:
        entities = []
        for start, end, label in ents:
            entities.append((start, end, label))
        train_data.append((text, {'entities': entities}))
    return train_data


def train(output_dir: Path, n_iter: int = 40):
    nlp = spacy.blank('en')
    if 'ner' not in nlp.pipe_names:
        ner = nlp.add_pipe('ner')
    else:
        ner = nlp.get_pipe('ner')

    # collect labels
    train_data = build_training_data(examples)
    labels = set(l for _, ann in train_data for _, _, l in ann['entities'])
    for l in labels:
        ner.add_label(l)

    # Disable other pipes during training
    optimizer = nlp.begin_training()
    for itn in range(n_iter):
        random.shuffle(train_data)
        losses = {}
        for text, annotations in train_data:
            doc = nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            nlp.update([example], sgd=optimizer, drop=0.2, losses=losses)
        if itn % 10 == 0:
            print(f'Iteration {itn}, losses: {losses}')

    output_dir = Path(output_dir)
    nlp.to_disk(output_dir)
    print(f'Saved NER model to {output_dir}')


if __name__ == '__main__':
    print('Training demo NER model (requires spaCy).')
    train(MODEL_DIR, n_iter=60)
