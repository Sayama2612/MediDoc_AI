"""Simple spaCy-based NER loader and extractor for medical fields.

Exports:
- `load_ner_model(path)` - load model from disk (returns nlp)
- `extract_medical_entities(text)` - returns list of detected entities as dicts

The extractor expects a spaCy model saved to `models/ner_model` (see
`scripts/train_ner_demo.py`). If the model is not present, functions will
raise informative errors.
"""
from pathlib import Path
from typing import List, Dict


def load_ner_model(path: str = None):
	try:
		import spacy
	except Exception as e:
		raise RuntimeError('spaCy is not installed. Install with: pip install spacy') from e

	model_path = Path(path) if path else Path(__file__).resolve().parents[2] / 'models' / 'ner_model'
	if not model_path.exists():
		raise RuntimeError(f'NER model not found at {model_path}. Train it with scripts/train_ner_demo.py')

	nlp = spacy.load(str(model_path))
	return nlp


_nlp = None


def _ensure_model():
	global _nlp
	if _nlp is None:
		_nlp = load_ner_model()
    

def extract_medical_entities(text: str) -> List[Dict]:
	"""Return list of entities with fields: label, text, start, end"""
	_ensure_model()
	doc = _nlp(text)
	results = []
	for ent in doc.ents:
		results.append({'label': ent.label_, 'text': ent.text, 'start': ent.start_char, 'end': ent.end_char})
	return results
import spacy
from typing import Dict, List, Tuple

nlp = None
try:
	nlp = spacy.load('en_core_web_sm')
except Exception:
	pass


def extract_entities(text: str) -> List[Tuple[str, str]]:
	"""Return list of (entity_text, label) tuples."""
	if nlp is None:
		return []
	doc = nlp(text)
	return [(ent.text, ent.label_) for ent in doc.ents]


# Example mapping helper for medical fields (you can extend or train custom model)
MEDICAL_LABELS = ['PERSON', 'DATE', 'GPE', 'ORG', 'NORP', 'CARDINAL']


def extract_medical_entities(text: str) -> Dict[str, List[str]]:
	ents = extract_entities(text)
	out = {'PATIENT_NAME': [], 'DATES': [], 'OTHER': []}
	for e, lab in ents:
		if lab == 'PERSON':
			out['PATIENT_NAME'].append(e)
		elif lab == 'DATE':
			out['DATES'].append(e)
		else:
			out['OTHER'].append(f"{e}({lab})")
	return out