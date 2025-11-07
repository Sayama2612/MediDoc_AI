# Intelligent Healthcare Document Processing — Quickstart

This repository is a starter scaffold for document classification, extraction (NER), OCR/text preprocessing, anomaly checks, and summarization with a small Flask backend for testing and integration.

This single README consolidates run and setup instructions. Other README files were removed to keep the project root canonical.

## What's included
- Flask web app: `src/web/app.py` (endpoints: `/test`, `/classify`, `/predict`, `/extract`, `/summarize`, `/ner`, `/anomaly`)
- Minimal NLP/processing stubs under `src/`
- Demo model scripts: `scripts/create_demo_artifacts.py` and `scripts/train_demo_models.py` (create models in `models/`)
- Small verification/test client: `run_local_test_client.py`

## Prerequisites
- Windows with PowerShell (these instructions use PowerShell)
- Python 3.8+ (workspace used Python 3.14)
- Optional: a virtual environment to isolate dependencies

## Quick setup (PowerShell)
1) Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies:

```powershell
pip install -r requirements.txt
```

3) (Optional) Install spaCy model if you intend to use spaCy-backed NER:

```powershell
python -m spacy download en_core_web_sm
```

## Create demo models (recommended for first run)
If you don't have trained model artifacts yet, create demo models that allow the app to return realistic predictions:

```powershell
# from project root
C:\Users\comp\AppData\Local\Programs\Python\Python314\python.exe scripts\create_demo_artifacts.py
# or (if your environment's python is active)
python scripts\create_demo_artifacts.py
```

This will create the following files:
- `models/simple_classifier.joblib` — pipeline (CountVectorizer + MultinomialNB) used by `/classify`
- `models/classifier.joblib` and `models/vectorizer.joblib` — separate vectorizer and classifier used by `/predict`

## Run the Flask app

```powershell
C:\Users\comp\AppData\Local\Programs\Python\Python314\python.exe src\web\app.py
# or when venv activated
python src\web\app.py
```

By default the patched app runs on port 8080. You can change the port in `src/web/app.py` or create a small launcher that reads an env var.

## Verify endpoints
- In a browser, open: `http://127.0.0.1:8080/test` — should return JSON {"status":"ok","message":"Server is running"}
- Basic check from PowerShell (use the Python stdlib if `Invoke-WebRequest` is unreliable):

```powershell
# Using Python stdlib
C:\Users\comp\AppData\Local\Programs\Python\Python314\python.exe -c "from urllib.request import urlopen; print(urlopen('http://127.0.0.1:8080/test').read().decode())"
```

## Using the endpoints
- `/classify` — accepts multipart file upload (text file) and uses `models/simple_classifier.joblib` to classify. If the artifact is missing, the endpoint returns a helpful error message.
- `/predict` — accepts JSON with {"text": "..."} and returns `prediction` and `probabilities` when `models/classifier.joblib` and `models/vectorizer.joblib` exist.
 - `/extract` — accepts JSON {"text": "..."} and returns:
   - `entities`: list of detected entities (labels like PATIENT_NAME, AGE, GENDER, DIAGNOSIS, MEDICATION, ADMISSION_DATE, DISCHARGE_DATE)
   - `structured`: a convenience mapping {patient_name, age, gender, diagnosis, medications, admission_date, discharge_date}
     - Each medication is an object {medication, dosage, frequency}
     - Dates are ISO-normalized (YYYY-MM-DD) when possible

UI / Side-by-side explanation
- The project currently exposes a minimal HTTP API (no single-page UI included). The `/extract` endpoint returns both:
  - rule-based extraction (fast, no extra dependencies)
  - spaCy-backed NER (if you install spaCy and train or provide `models/ner_model`).

  The API response includes a `structured` section which is intended for quick consumption (e.g., a simple UI can render the original text on the left and the `structured` fields on the right). Example conceptual layout for a lightweight UI:

  Left column: Original clinical text (editable)
  Right column: Extracted fields (patient_name, age, gender, diagnosis, medications with dosage/frequency, admission/discharge dates)

  Switching between rule-based and ML-backed NER:
  - By default the app uses rule-based NER (no additional install required).
  - If `models/ner_model` exists and `spaCy` is installed, the app will prefer the spaCy model and fall back to the rules when spaCy is unavailable.

  This README contains a small sample script you can use to render a side-by-side HTML preview using the `/extract` result (save as `tools/preview_side_by_side.py` and run):

  ```powershell
  # quick preview (Python required)
  python - <<'PY'
  import requests, json
  text = 'Patient John Doe, male, 45 years. Admission: 2025-01-10. Diagnosis: acute bronchitis. Medication: amoxicillin 500 mg twice daily.'
  r = requests.post('http://127.0.0.1:8080/extract', json={'text': text})
  data = r.json()
  html = f"<html><body><div style='display:flex'><pre style='width:50%'>"+text+"</pre><pre style='width:50%'>"+json.dumps(data['structured'], indent=2)+"</pre></div></body></html>"
  open('preview.html','w', encoding='utf-8').write(html)
  print('Wrote preview.html — open it in a browser')
  PY
  ```

## Troubleshooting
- If server does not start or you cannot connect:
  - Ensure no firewall is blocking Python listening on localhost. You can temporarily allow `python.exe` for private networks in Windows Firewall.
  - Check whether another process uses the port (example for port 8080):

```powershell
netstat -ano | Select-String ":8080"

# then find the process if present:
Get-Process -Id <PID>
```

  - If the Flask app prints that it's running but web requests fail, try starting the server in a new PowerShell window (or as Administrator) and re-test.

- If model endpoints return "Model not loaded", run the demo artifact script above or place your trained artifacts at:
  - `models/simple_classifier.joblib`
  - `models/classifier.joblib` and `models/vectorizer.joblib`

## Notes about the codebase
- The app includes safe fallback stubs for OCR, text cleaning, tokenization, and summarization so the server can start even when optional libraries or trained models are missing.
- Replace the fallback implementations in `src/web/app.py` with real implementations (Tesseract/EasyOCR, spaCy, transformers, etc.) to get full functionality.

## Next steps (suggestions)
- Replace stubbed helpers with production implementations.
- Add unit tests using `pytest` for the Flask endpoints.
- Add a `run_server.py` launcher that reads PORT and other env vars.
- Add a Dockerfile and docker-compose to containerize the app + MongoDB (if you plan to persist extracted data).

If anything in these instructions doesn't work on your machine, tell me the exact command and the output; I'll adjust the steps to fit your environment.

---
Last verified: demo artifact creation and app run were tested in this workspace on Windows with Python 3.14.

Project root files worth checking:
- `src/web/app.py` — main Flask app (start point)
- `scripts/create_demo_artifacts.py` — creates demo models
- `scripts/train_demo_models.py` — alternative demo training script
- `quick_start_app.py` — very small app used for initial environment checks

Enjoy — tell me if you want me to add Docker, tests, or CI wiring.
