from pathlib import Path
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline
import joblib

ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = ROOT / 'models'
MODELS_DIR.mkdir(parents=True, exist_ok=True)

print('Models dir:', MODELS_DIR)

texts = [
    "Prescribe ibuprofen 200mg three times daily.",
    "Start metformin 500 mg twice a day.",
    "CT scan shows stable postoperative changes.",
    "Pathology report: no malignancy identified.",
    "Summary: patient improved and was discharged home.",
    "Short summary for discharge and follow-up."    
]
labels = ['prescription', 'prescription', 'report', 'report', 'summary', 'summary']

# pipeline
pipe = make_pipeline(CountVectorizer(), MultinomialNB())
pipe.fit(texts, labels)
joblib.dump(pipe, MODELS_DIR / 'simple_classifier.joblib')
print('Wrote simple_classifier.joblib')

# separate
vect = CountVectorizer()
X = vect.fit_transform(texts)
clf = MultinomialNB()
clf.fit(X, labels)
joblib.dump(clf, MODELS_DIR / 'classifier.joblib')
joblib.dump(vect, MODELS_DIR / 'vectorizer.joblib')
print('Wrote classifier.joblib and vectorizer.joblib')
