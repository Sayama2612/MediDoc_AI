import pickle
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from typing import List

MODEL_PATH = "models/classifier.pkl"
VEC_PATH = "models/tfidf_vectorizer.pkl"


class SimpleClassifier:
	def __init__(self):
		self.vectorizer: TfidfVectorizer = None
		self.model: LogisticRegression = None

	def train(self, texts: List[str], labels: List[str]):
		self.vectorizer = TfidfVectorizer(max_features=5000)
		X = self.vectorizer.fit_transform(texts)
		self.model = LogisticRegression(max_iter=1000)
		self.model.fit(X, labels)
		with open(MODEL_PATH, 'wb') as f:
			pickle.dump(self.model, f)
		with open(VEC_PATH, 'wb') as f:
			pickle.dump(self.vectorizer, f)

	def predict(self, texts: List[str]) -> List[str]:
		if self.model is None or self.vectorizer is None:
			with open(MODEL_PATH, 'rb') as f:
				self.model = pickle.load(f)
			with open(VEC_PATH, 'rb') as f:
				self.vectorizer = pickle.load(f)
		X = self.vectorizer.transform(texts)
		return self.model.predict(X).tolist()