from typing import Optional
from PIL import Image
import pytesseract
import os
try:
    import easyocr
except Exception:
    easyocr = None

# Set Tesseract path for Windows
if os.name == 'nt':  # Windows
    tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    if os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

def ocr_from_image(path: str, use_easyocr: bool = False) -> str:
    """Return extracted text from an image file.
    If use_easyocr is True and easyocr is installed, it will be used as fallback.
    """
    img = Image.open(path)
    text = pytesseract.image_to_string(img)
    if (not text or text.strip() == "") and use_easyocr and easyocr is not None:
        reader = easyocr.Reader(["en"])
        res = reader.readtext(path, detail=0)
        text = "\n".join(res)
    return text