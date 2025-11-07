import re
from typing import List, Dict, Optional
from datetime import datetime


def _find_name(text: str) -> str:
    # Look for common patterns: 'Patient: Name', 'Name: First Last', 'Patient name: X'
    patterns = [r'Patient\s*[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Name\s*[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)',
                r'Patient name\s*[:\-]\s*([A-Z][a-z]+\s+[A-Z][a-z]+)']
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    # Fallback: look for two capitalized words near start
    m = re.search(r'^(?:Patient\s*)?([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
    if m:
        return m.group(1)
    return ''


def _find_age(text: str) -> str:
    m = re.search(r'(\d{1,3})\s*(?:years old|years|yrs|yr|y/o|yo|-year-old)', text, re.I)
    if m:
        return m.group(1)
    m = re.search(r'Age\s*[:\-]\s*(\d{1,3})', text, re.I)
    if m:
        return m.group(1)
    return ''


def _find_gender(text: str) -> str:
    m = re.search(r'\b(Male|Female|M|F|male|female)\b', text)
    if m:
        g = m.group(1)
        if g.lower().startswith('m'):
            return 'male'
        if g.lower().startswith('f'):
            return 'female'
    return ''


def _find_dates(text: str) -> Dict[str, str]:
    # Recognize dates in various formats and map them to admission/discharge
    dates = {}

    # Common date patterns
    iso = r'\d{4}-\d{2}-\d{2}'
    dmy = r'\d{1,2}/\d{1,2}/\d{4}'
    month_day = r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'
    any_date = rf'({iso}|{dmy}|{month_day})'

    # Look for explicit admission/admitted context
    m = re.search(r'(?:Admission|Admitted|Date of admission)\s*(?:[:\-])?\s*' + any_date, text, re.I)
    if not m:
        # try 'admitted on 2025-01-01' variants
        m = re.search(r'admitted(?: on)?\s*' + any_date, text, re.I)
    if m:
        dates['admission_date'] = m.group(1)

    # explicit discharge
    m = re.search(r'(?:Discharge|Discharged|Date of discharge)\s*(?:[:\-])?\s*' + any_date, text, re.I)
    if not m:
        m = re.search(r'discharged(?: on)?\s*' + any_date, text, re.I)
    if m:
        dates['discharge_date'] = m.group(1)

    # If admission/discharge not explicit, try to infer from nearby keywords
    # Capture all date-like tokens and then look at the sentence containing them
    if 'admission_date' not in dates or 'discharge_date' not in dates:
        all_dates = list(re.finditer(any_date, text, re.I))
        for dtm in all_dates:
            dt = dtm.group(1)
            # get surrounding context (30 chars each side)
            start = max(0, dtm.start() - 30)
            end = min(len(text), dtm.end() + 30)
            ctx = text[start:end].lower()
            if 'admiss' in ctx or 'arrival' in ctx or 'from' in ctx and 'to' not in ctx:
                if 'admission_date' not in dates:
                    dates['admission_date'] = dt
                    continue
            if 'discharg' in ctx or 'discharged' in ctx or 'to' in ctx or 'until' in ctx:
                if 'discharge_date' not in dates:
                    dates['discharge_date'] = dt
                    continue
        # If still no explicit mapping but we found dates, set a generic found_date
        if 'admission_date' not in dates and 'discharge_date' not in dates and all_dates:
            dates['found_date'] = all_dates[0].group(1)

    return dates


def _find_diagnosis(text: str) -> str:
    m = re.search(r'(?:Diagnosis|DX|Dx)[:\-]\s*(.+?)(?:\.|\n|$)', text, re.I)
    if m:
        return m.group(1).strip()
    # fallback: look for 'Dx:'
    m = re.search(r'Dx[:\-]\s*(.+?)(?:\.|\n|$)', text, re.I)
    if m:
        return m.group(1).strip()
    return ''


def _find_medications(text: str) -> List[Dict[str, str]]:
    meds = []
    # Look for lines starting with Medication(s): or Meds:
    lines = re.split(r'[\n\r]+', text)
    for ln in lines:
        m = re.search(r'(?:Medication|Meds|Meds:|Medications|Medication[s]?)[:\-]\s*(.+)', ln, re.I)
        if m:
            rest = m.group(1)
            # extract med and dosage if present
            # capture multiple meds separated by commas or ';'
            parts = re.split(r'[;,]\s*', rest)
            for part in parts:
                # try to split out medication, dosage and optional frequency
                md = re.search(r'([A-Za-z0-9\-\(\)\/\s]+?)\s+(\d+(?:[\.,]\d+)?\s*(?:mg|mcg|g|units|ml|mL|tablet|tablets|capsule|capsules|IU))\b\s*(.*)', part, re.I)
                if md:
                    medname = md.group(1).strip(' .,-')
                    dose = md.group(2).replace('\u00A0', ' ').strip()
                    rest_after = md.group(3).strip()
                    freq = _extract_frequency(rest_after)
                    meds.append({'medication': medname, 'dosage': dose, 'frequency': freq})
                else:
                    # no dosage present, still try to detect frequency within part
                    freq = _extract_frequency(part)
                    meds.append({'medication': part.strip(' .,-'), 'dosage': '', 'frequency': freq})
    # Also try to find inline medication patterns like 'aspirin 81 mg'
    inline = re.findall(r'([A-Za-z0-9\-\(\)\/\s]+?)\s+(\d+(?:[\.,]\d+)?\s*(?:mg|mcg|g|units|ml|mL|tablet|tablets|capsule|capsules|IU))\b(?:\s*(.*))?', text, re.I)
    for medname, dose, rest in inline:
        entry = {'medication': medname.strip(' .,-'), 'dosage': dose.replace('\u00A0', ' ').strip(), 'frequency': _extract_frequency(rest or '')}
        if entry not in meds:
            meds.append(entry)
    return meds


def _extract_frequency(text: str) -> str:
    if not text:
        return ''
    text = text.lower()
    # common frequency phrases
    patterns = [
        (r'once (?:daily|a day|per day)', 'once daily'),
        (r'twice (?:daily|a day|per day)', 'twice daily'),
        (r'three times|three[- ]times|tid|t.i.d', 'three times daily'),
        (r'bid|b.i.d', 'twice daily'),
        (r'qd|q\.d|once daily', 'once daily'),
        (r'q\d+h', 'every X hours'),
        (r'every \d+ (?:hours|hrs|hr)', 'every N hours'),
        (r'once daily', 'once daily'),
        (r'daily', 'daily'),
        (r'weekly', 'weekly'),
    ]
    for p, label in patterns:
        if re.search(p, text):
            # preserve numeric n in 'every N hours'
            m = re.search(r'every (\d+) (?:hours|hrs|hr)', text)
            if m:
                return f'every {m.group(1)} hours'
            m2 = re.search(r'q(\d+)h', text)
            if m2:
                return f'every {m2.group(1)} hours'
            return label
    return ''


def _normalize_date(d: str) -> Optional[str]:
    if not d:
        return None
    d = d.strip()
    # Try ISO first
    try:
        return datetime.strptime(d, '%Y-%m-%d').date().isoformat()
    except Exception:
        pass
    # Try D/M/YYYY or DD/MM/YYYY
    for fmt in ('%d/%m/%Y', '%m/%d/%Y'):
        try:
            return datetime.strptime(d, fmt).date().isoformat()
        except Exception:
            pass
    # Try 'Month D, YYYY'
    try:
        return datetime.strptime(d, '%B %d, %Y').date().isoformat()
    except Exception:
        pass
    try:
        return datetime.strptime(d, '%b %d, %Y').date().isoformat()
    except Exception:
        pass
    # fallback: return original
    return d


def extract_medical_entities(text: str) -> List[Dict]:
    """Return list of detected entities with label, text, start, end."""
    entities = []
    try:
        name = _find_name(text)
        if name:
            idx = text.find(name)
            entities.append({'label': 'PATIENT_NAME', 'text': name, 'start': idx, 'end': idx + len(name)})

        age = _find_age(text)
        if age:
            idx = text.find(age)
            entities.append({'label': 'AGE', 'text': age, 'start': idx, 'end': idx + len(age)})

        gender = _find_gender(text)
        if gender:
            idx = text.lower().find(gender.lower())
            entities.append({'label': 'GENDER', 'text': gender, 'start': idx, 'end': idx + len(gender)})

        diag = _find_diagnosis(text)
        if diag:
            idx = text.find(diag)
            entities.append({'label': 'DIAGNOSIS', 'text': diag, 'start': idx, 'end': idx + len(diag)})

        meds = _find_medications(text)
        for m in meds:
            med_text = m['medication']
            if m.get('dosage'):
                med_text = f"{med_text} {m['dosage']}".strip()
            idx = text.find(m['medication'])
            if idx == -1:
                # fallback: find med text occurrence
                idx = text.find(med_text)
            end = idx + len(med_text) if idx != -1 else -1
            entities.append({'label': 'MEDICATION', 'text': med_text, 'start': idx, 'end': end})

        dates = _find_dates(text)
        for k, v in dates.items():
            idx = text.find(v)
            label = k.upper()
            entities.append({'label': label, 'text': v, 'start': idx, 'end': idx + len(v)})
    except Exception:
        # fail-safe: return empty list on error
        return []

    return entities


def extract_structured(text: str) -> Dict[str, object]:
    """Return structured mapping of fields based on regex heuristics."""
    name = _find_name(text)
    age = _find_age(text)
    gender = _find_gender(text)
    diagnosis = _find_diagnosis(text)
    medications = _find_medications(text)
    dates = _find_dates(text)

    return {
        'patient_name': name,
        'age': age,
        'gender': gender,
        'diagnosis': diagnosis,
        'medications': medications,
        'admission_date': dates.get('admission_date', ''),
        'discharge_date': dates.get('discharge_date', ''),
    }
