import re
import spacy
from typing import List

nlp = None
try:
	nlp = spacy.load("en_core_web_sm")
except Exception:
	# User should run: python -m spacy download en_core_web_sm
	pass


def clean_text(text: str) -> str:
	text = text.replace('\r', ' ')
	text = re.sub(r"\s+", ' ', text).strip()
	return text


def tokenize_and_lemmatize(text: str) -> List[str]:
	if nlp is None:
		return text.split()
	doc = nlp(text)
	return [token.lemma_.lower() for token in doc if not token.is_stop and token.is_alpha]