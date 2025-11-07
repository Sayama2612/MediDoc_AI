import sys
import os

# ensure project root is on path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from src.ner.rule_ner import extract_structured, extract_medical_entities


def test_happy_path_extraction():
    text = (
        "Patient John Doe, male, 45 years. Admission: 2025-01-10. "
        "Diagnosis: acute bronchitis. Medication: amoxicillin 500 mg twice daily."
    )
    structured = extract_structured(text)
    assert structured['patient_name'] == 'John Doe'
    assert structured['age'] == '45'
    assert structured['gender'] == 'male'
    assert 'acute bronchitis' in structured['diagnosis'].lower()
    meds = structured['medications']
    assert any(m['medication'].lower().startswith('amoxicillin') for m in meds)
    assert any('500' in (m.get('dosage') or '') for m in meds)
    # frequency should be parsed
    assert any(('twice' in (m.get('frequency') or '') or 'daily' in (m.get('frequency') or '')) for m in meds)


def test_admission_and_discharge_mapping():
    text = "Admitted on 2025-02-01. Discharged on 2025-02-10."
    structured = extract_structured(text)
    # dates should be ISO-normalized
    assert structured['admission_date'] == '2025-02-01'
    assert structured['discharge_date'] == '2025-02-10'


def test_multiple_medication_parsing():
    text = "Medications: ibuprofen 200 mg; aspirin 81 mg once daily"
    structured = extract_structured(text)
    meds = structured['medications']
    names = [m['medication'].lower() for m in meds]
    assert 'ibuprofen' in ' '.join(names)
    assert any('200' in (m.get('dosage') or '') for m in meds)
    assert any('81' in (m.get('dosage') or '') for m in meds)
    assert any('daily' in (m.get('frequency') or '') or 'once' in (m.get('frequency') or '') for m in meds)


def test_no_medication():
    text = "Patient: Alice Smith. Age: 30."
    structured = extract_structured(text)
    assert structured['medications'] == []
