import pytesseract
from pdf2image import convert_from_path

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text from a PDF file, including OCR for images.
    Always uses both English (eng) and Indonesian (ind) languages.
    """
    text_output = []

    images = convert_from_path(pdf_path)

    for img in images:
        extracted_text = pytesseract.image_to_string(img, lang="eng+ind")
        text_output.append(extracted_text)
    
    return "\n".join(text_output)