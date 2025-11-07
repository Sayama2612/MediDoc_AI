import os
import sys
from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
from flask_cors import CORS
from pathlib import Path
import joblib

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, PROJECT_ROOT)

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'data')
ALLOWED_EXT = set(['png', 'jpg', 'jpeg', 'pdf', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)

# Try to import the project's NER extractor if available (spaCy-based); otherwise use rule-based extractor
try:
    from src.ner.ner_spacy import extract_medical_entities as ner_extract
    print('Using spaCy NER extractor from src.ner.ner_spacy')
except Exception:
    try:
        from src.ner.rule_ner import extract_medical_entities as ner_extract, extract_structured as ner_structured
        print('Using rule-based NER extractor from src.ner.rule_ner')
    except Exception:
        ner_extract = None
        ner_structured = None

# Model artifact paths
SIMPLE_MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'simple_classifier.joblib')
# classifier/vectorizer for the predict endpoint
CLASSIFIER_MODEL_PATH = os.path.join(PROJECT_ROOT, 'models', 'classifier.joblib')
VECT_PATH = os.path.join(PROJECT_ROOT, 'models', 'vectorizer.joblib')

# In-memory model refs (loaded on demand)
model = None
_classifier = None
_vectorizer = None

@app.route('/', methods=['GET'])
def index():
    return """
    <html>
        <head>
            <title>Healthcare Document Classifier</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .container { max-width: 800px; margin: 0 auto; }
                .form-group { margin-bottom: 20px; }
                .result { margin-top: 20px; padding: 10px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Healthcare Document Classifier</h1>
                <form action="/classify" method="post" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Select a document to classify:</label><br>
                        <input type="file" id="file" name="file" required>
                    </div>
                    <button type="submit">Classify Document</button>
                </form>
                <div class="result" id="result"></div>
            </div>
            <script>
                document.querySelector('form').onsubmit = async (e) => {
                    e.preventDefault();
                    const formData = new FormData();
                    formData.append('file', document.getElementById('file').files[0]);
                    try {
                        const response = await fetch('/classify', {
                            method: 'POST',
                            body: formData
                        });
                        const result = await response.json();
                        document.getElementById('result').innerHTML = `
                            <h3>Classification Result:</h3>
                            <p>Document Type: ${result.document_type}</p>
                            <p>Confidence: ${Math.round(result.confidence * 100)}%</p>
                        `;
                    } catch (error) {
                        document.getElementById('result').innerHTML = `<p style="color: red">Error: ${error.message}</p>`;
                    }
                };
            </script>
        </body>
    </html>
    """


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


@app.route('/upload', methods=['POST'])
def upload():
    # Accept file upload and return extracted text (OCR for images)
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'no selected file'}), 400
    if f and allowed_file(f.filename):
        filename = secure_filename(f.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        f.save(save_path)
        # Simple handling: if txt file, read; otherwise OCR image
        if filename.lower().endswith('.txt'):
            with open(save_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
        else:
            # ocr_from_image may be provided elsewhere in the project. Provide a safe fallback.
            try:
                text = ocr_from_image(save_path, use_easyocr=True)
            except Exception:
                text = ''
        text = clean_text(text)
        return jsonify({'text': text})


@app.route('/extract', methods=['POST'])
def extract():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'no text provided'}), 400
    
    text = request.json['text']
    tokens = tokenize_and_lemmatize(text)
    entities = extract_medical_entities(text)

    # Structured mapping: prefer extractor-provided structured output if available
    structured = {}
    if 'ner_structured' in globals() and ner_structured:
        try:
            structured = ner_structured(text)
        except Exception:
            structured = {}
    else:
        # attempt to map entity labels to desired fields
        structured = {
            'patient_name': None,
            'age': None,
            'gender': None,
            'diagnosis': None,
            'medications': [],
            'admission_date': None,
            'discharge_date': None
        }
        for e in entities or []:
            label = e.get('label', '').upper()
            txt = e.get('text', '')
            if label in ('PATIENT_NAME', 'NAME') and not structured['patient_name']:
                structured['patient_name'] = txt
            if label == 'AGE' and not structured['age']:
                structured['age'] = txt
            if label == 'GENDER' and not structured['gender']:
                structured['gender'] = txt
            if label == 'DIAGNOSIS' and not structured['diagnosis']:
                structured['diagnosis'] = txt
            if label == 'MEDICATION':
                # try to split medication and dosage
                parts = txt.split()
                meds = {'medication': txt, 'dosage': ''}
                # find token with mg/mcg/etc
                for tok in parts:
                    if re.search(r'\d+\s*(?:mg|mcg|g|units)', tok, re.I):
                        meds['dosage'] = tok
                        meds['medication'] = txt.replace(tok, '').strip()
                        break
                structured['medications'].append(meds)
            if label in ('ADMISSION_DATE', 'ADMITTED', 'FOUND_DATE') and not structured['admission_date']:
                structured['admission_date'] = txt
            if label in ('DISCHARGE_DATE', 'DISCHARGE') and not structured['discharge_date']:
                structured['discharge_date'] = txt

    return jsonify({
        'entities': entities,
        'tokens': tokens,
        'structured': structured
    })


@app.route('/summarize', methods=['POST'])
def summarize_text():
    if not request.json or 'text' not in request.json:
        return jsonify({'error': 'no text provided'}), 400
    
    text = request.json['text']
    try:
        summary = summarize(text)
        return jsonify({'summary': summary})
    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return jsonify({'error': 'Failed to generate summary'}), 500


# Prediction endpoint for the document classifier
from pathlib import Path

def load_classifier_models():
    """Load classifier and vectorizer on demand. Raises RuntimeError if artifacts missing."""
    global _classifier, _vectorizer
    if _classifier is None or _vectorizer is None:
        if Path(CLASSIFIER_MODEL_PATH).exists() and Path(VECT_PATH).exists():
            try:
                print(f"Loading models from {CLASSIFIER_MODEL_PATH} and {VECT_PATH}")
                _classifier = joblib.load(CLASSIFIER_MODEL_PATH)
                _vectorizer = joblib.load(VECT_PATH)
                print("Models loaded successfully")
            except Exception as e:
                print(f"Error loading models: {str(e)}")
                raise
        else:
            raise RuntimeError('Model artifacts not found. Run training first.')


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'no text provided'}), 400
    try:
        load_classifier_models()
    except RuntimeError as e:
        return jsonify({'error': str(e)}), 500

    X = _vectorizer.transform([text])
    pred = _classifier.predict(X)[0]
    probs = None
    if hasattr(_classifier, 'predict_proba'):
        probs = _classifier.predict_proba(X).tolist()[0]
    return jsonify({'prediction': pred, 'probabilities': probs})


# --- Additional endpoints following the user's workflow ---


@app.route('/ner', methods=['POST'])
def ner():
    data = request.json or {}
    text = data.get('text', '')
    if not text:
        return jsonify({'error': 'no text provided'}), 400
    entities = extract_medical_entities(text)
    return jsonify({'entities': entities})


@app.route('/anomaly', methods=['POST'])
def anomaly_check():
    data = request.json or {}
    text = data.get('text', '')
    # If an anomaly module exists, use it; otherwise return placeholder
    try:
        from src.anomaly.anomaly import detect_anomalies
        findings = detect_anomalies(text)
    except Exception:
        findings = {'warning': 'anomaly module not available', 'checks': []}
    return jsonify({'anomalies': findings})


@app.route('/test', methods=['GET'])
def test():
    return jsonify({"status": "ok", "message": "Server is running"}), 200

@app.route('/classify', methods=['POST'])
def classify_document():
    # Load simple model on demand if available
    global model
    if model is None:
        try:
            if Path(SIMPLE_MODEL_PATH).exists():
                model = joblib.load(SIMPLE_MODEL_PATH)
        except Exception as e:
            print(f"Error loading simple model: {e}")

    if model is None:
        return jsonify({"error": "Model not loaded. Place a model at models/simple_classifier.joblib or run training."}), 500
        
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
        
    try:
        # Read the file content directly
        text = file.read().decode('utf-8')
            
        # Make prediction
        prediction = model.predict([text])[0]
        probability = float(max(model.predict_proba([text])[0]))
        
        return jsonify({
            "document_type": prediction,
            "confidence": probability
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.errorhandler(500)
def internal_error(e):
    # Return JSON for server errors during development
    return jsonify({'error': 'internal server error', 'detail': str(e)}), 500


# --- Helpers: provide safe fallbacks for optional project helpers ---
def ocr_from_image(path, use_easyocr=True):
    # Placeholder OCR: return empty string so endpoints won't crash.
    return ''

def clean_text(text):
    if not text:
        return ''
    return text.strip()

def tokenize_and_lemmatize(text):
    # Minimal tokenization fallback
    return [t for t in text.split() if t]

def extract_medical_entities(text):
    # If a spaCy-based extractor is available, delegate to it
    if 'ner_extract' in globals() and ner_extract:
        try:
            ents = ner_extract(text)
            return ents
        except Exception:
            # fall through to fallback
            pass
    # Return empty list to indicate no entities found by fallback
    return []

def summarize(text):
    # Simple summarizer fallback
    return text[:500]


if __name__ == '__main__':
    # Single app.run to avoid repeated bindings
    app.run(host='127.0.0.1', port=8080, debug=True)