
from pdf2image import convert_from_path
import pytesseract


def extract_text_from_pdf(pdf_path: str, lang: str = "ind") -> str:
    """
    Extract text from a PDF file, including OCR for images.
    """
    text_output = []

    images = convert_from_path(pdf_path)

    for img in images:
        extracted_text = pytesseract.image_to_string(img, lang=lang)
        text_output.append(extracted_text)
    
    return "\n".join(text_output)