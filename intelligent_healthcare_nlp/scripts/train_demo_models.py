"""Train and save small demo models for the project.
Creates:
 - models/simple_classifier.joblib  (pipeline: CountVectorizer + MultinomialNB)
 - models/classifier.joblib         (MultinomialNB fitted on vectorized text)
 - models/vectorizer.joblib        (CountVectorizer fitted)

Run from project root:
  python scripts/train_demo_models.py
"""
from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

MODEL_DIR = Path(__file__).resolve().parents[1] / 'models'
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# Synthetic dataset
texts = [
    "Patient prescribed 5mg amlodipine daily for hypertension.",
    "Start amoxicillin 500 mg twice daily for 7 days.",
    "The chest x-ray shows no acute cardiopulmonary disease.",
    "MRI reveals small infarct in the left temporal lobe.",
    "This is a brief summary of the patient's hospital stay and discharge plan.",
    "Discharged with follow-up in clinic and medication reconciliation performed."
]
labels = [
    'prescription',
    'prescription',
    'report',
    'report',
    'summary',
    'summary'
]

# 1) simple pipeline (used by /classify endpoint)
print('Training simple pipeline model...')
pipe = make_pipeline(CountVectorizer(), MultinomialNB())
pipe.fit(texts, labels)
simple_path = MODEL_DIR / 'simple_classifier.joblib'
joblib.dump(pipe, simple_path)
print(f'Saved simple pipeline to: {simple_path}')

# 2) separate vectorizer + classifier (used by /predict endpoint)
print('Training separate vectorizer + classifier...')
vect = CountVectorizer()
X = vect.fit_transform(texts)
clf = MultinomialNB()
clf.fit(X, labels)
classifier_path = MODEL_DIR / 'classifier.joblib'
vectorizer_path = MODEL_DIR / 'vectorizer.joblib'
joblib.dump(clf, classifier_path)
joblib.dump(vect, vectorizer_path)
print(f'Saved classifier to: {classifier_path}')
print(f'Saved vectorizer to: {vectorizer_path}')

print('Demo models training complete.')
