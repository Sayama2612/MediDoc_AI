"""Prepare dataset from MIMIC demo and train a TF-IDF + LogisticRegression classifier.
Saves model and vectorizer to models/.
"""
import os
import importlib.util
spec = importlib.util.spec_from_file_location('prepare_mimic_demo', os.path.join(os.path.dirname(__file__), 'prepare_mimic_demo.py'))
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)
prepare = prep.prepare
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_CSV = os.path.join(PROJECT_ROOT, 'data', 'mimic_demo_dataset.csv')
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models')
os.makedirs(MODELS_DIR, exist_ok=True)


def load_data(path):
    df = pd.read_csv(path)
    return df['text'].astype(str).tolist(), df['label'].astype(str).tolist()


def train_on_data(csv_path=DATA_CSV):
    X, y = load_data(csv_path)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    vect = TfidfVectorizer(ngram_range=(1,2), max_df=0.9)
    Xtr = vect.fit_transform(X_train)
    Xte = vect.transform(X_test)

    clf = LogisticRegression(max_iter=1000)
    clf.fit(Xtr, y_train)

    preds = clf.predict(Xte)
    acc = accuracy_score(y_test, preds)
    print('Accuracy:', acc)
    print('\nClassification report:\n')
    print(classification_report(y_test, preds))

    # Save artifacts
    model_path = os.path.join(MODELS_DIR, 'classifier.joblib')
    vec_path = os.path.join(MODELS_DIR, 'vectorizer.joblib')
    joblib.dump(clf, model_path)
    joblib.dump(vect, vec_path)
    print(f'Saved model to {model_path}')
    print(f'Saved vectorizer to {vec_path}')


if __name__ == '__main__':
    print('Preparing MIMIC demo dataset...')
    prepare()
    print('Training classifier on prepared dataset...')
    train_on_data()
