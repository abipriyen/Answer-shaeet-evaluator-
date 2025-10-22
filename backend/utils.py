import docx
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def extract_text_from_file(file_path):
    ext = file_path.split('.')[-1].lower()

    if ext == 'pdf':
        return extract_text_from_pdf(file_path)
    elif ext == 'docx':
        return extract_text_from_docx(file_path)
    elif ext in ['jpg', 'jpeg', 'png']:
        return extract_text_from_image(file_path)
    else:
        return ''

def extract_text_from_pdf(file_path):
    text = ''
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return ' '.join([para.text for para in doc.paragraphs])

def extract_text_from_image(file_path):
    image = Image.open(file_path)
    return pytesseract.image_to_string(image)

def calculate_similarity(correct_text, student_text):
    vectorizer = TfidfVectorizer().fit_transform([correct_text, student_text])
    vectors = vectorizer.toarray()
    similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    score = round(similarity * 100, 2)

    if score >= 90:
        feedback = 'Excellent! Very close to the correct answer.'
    elif score >= 70:
        feedback = 'Good. Some points are missing or slightly off.'
    elif score >= 50:
        feedback = 'Fair attempt. Needs improvement.'
    else:
        feedback = 'Poor. Please review the topic again.'

    return score, feedback
