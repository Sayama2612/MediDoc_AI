import os
import sys
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Add project root to Python path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, PROJECT_ROOT)

from src.ocr.ocr import ocr_from_image
from src.preprocessing.text_preprocess import clean_text, tokenize_and_lemmatize
from src.ner.ner_spacy import extract_medical_entities
from src.summarization.summarizer import summarize

UPLOAD_FOLDER = os.path.join(PROJECT_ROOT, 'data')
ALLOWED_EXT = set(['png', 'jpg', 'jpeg', 'pdf', 'txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return 'Intelligent Healthcare Document Processing System - API'


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
            text = ocr_from_image(save_path, use_easyocr=True)
        text = clean_text(text)
        return jsonify({'text': text})
    return jsonify({'error': 'file type not allowed'}), 400


@app.route('/extract', methods=['POST'])
def extract():
    data = request.json or {}
    text = data.get('text', '')
    ents = extract_medical_entities(text)
    return jsonify({'entities': ents})


@app.route('/summarize', methods=['POST'])
def summarize_route():
    data = request.json or {}
    text = data.get('text', '')
    summ = summarize(text)
    return jsonify({'summary': summ})


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
