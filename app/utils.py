import pdfplumber
import requests
from io import BytesIO

def extract_pdf_text(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with pdfplumber.open(BytesIO(response.content)) as pdf:
            text = ''.join(page.extract_text() or "" for page in pdf.pages)
            return text.strip() or "No text extracted from PDF"
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def chunk_text(text, max_words=200):
    if not text:
        return []
    sentences = text.split('. ')
    chunks, chunk, count = [], [], 0
    for sentence in sentences:
        words = sentence.split()
        count += len(words)
        chunk.append(sentence)
        if count >= max_words:
            chunks.append('. '.join(chunk) + '.')
            chunk, count = [], 0
    if chunk:
        chunks.append('. '.join(chunk) + '.')
    return chunks