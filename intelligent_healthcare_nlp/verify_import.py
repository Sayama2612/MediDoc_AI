import importlib
import joblib

try:
    importlib.import_module('src.web.app')
    print('import_ok')
except Exception as e:
    import traceback
    traceback.print_exc()
    raise

clf = joblib.load('models/classifier.joblib')
vect = joblib.load('models/vectorizer.joblib')

texts = ["Take aspirin 75 mg daily", "CT shows no acute intracranial hemorrhage"]
X = vect.transform(texts)
print(clf.predict(X))
