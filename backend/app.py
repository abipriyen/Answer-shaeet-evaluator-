from flask import Flask, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import PyPDF2
import os
import difflib
import random

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Path to Tesseract (change if installed elsewhere)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Old UI style review list
reviews = {
    10: ["Excellent! Very close to the correct answer."],
    8: ["Good. Some points are missing or slightly off."],
    5: ["Fair attempt. Needs improvement"],
    2: ["Poor. Please review the topic again."],
    0: ["No relevant answer, Completely incorrect."]
}

def extract_text_from_image(image_path):
    image = Image.open(image_path)
    return pytesseract.image_to_string(image)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text() + "\n"
    return text

def compare_text(student_text, answer_key_text):
    similarity = difflib.SequenceMatcher(None, student_text.strip().lower(), answer_key_text.strip().lower()).ratio()
    raw_marks = round(similarity * 10)  # 0–10 range

    # Map marks to nearest defined category
    if raw_marks >= 9:
        marks = 10
    elif raw_marks >= 7:
        marks = 8
    elif raw_marks >= 4:
        marks = 5
    elif raw_marks >= 1:
        marks = 2
    else:
        marks = 0

    return marks, reviews.get(marks, ["No review available."])

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.get_json()
    correct_answer = data.get("correct", "")
    student_answer = data.get("student", "")

    if not correct_answer or not student_answer:
        return jsonify({"error": "Both correct and student answers are required"}), 400

    marks, review_list = compare_text(student_answer, correct_answer)
    return jsonify({
        "score": marks,
        "total": 10,
        "feedback": random.choice(review_list) if review_list else "No review available."
    })

@app.route("/custom-check", methods=["POST"])
def custom_check():
    answer_file = request.files.get("answerKey")
    student_file = request.files.get("studentPaper")

    if not answer_file or not student_file:
        return jsonify({"error": "Both answer key and student paper are required"}), 400

    # Save uploaded files
    answer_path = os.path.join(UPLOAD_FOLDER, answer_file.filename)
    student_path = os.path.join(UPLOAD_FOLDER, student_file.filename)
    answer_file.save(answer_path)
    student_file.save(student_path)

    # Extract text from uploaded files
    answer_text = extract_text_from_pdf(answer_path) if answer_path.lower().endswith(".pdf") else extract_text_from_image(answer_path)
    student_text = extract_text_from_pdf(student_path) if student_path.lower().endswith(".pdf") else extract_text_from_image(student_path)

    # Compare and get review
    marks, review_list = compare_text(student_text, answer_text)

    return jsonify({
        "score": marks,
        "total": 10,
        "reviews": review_list
    })

if __name__ == "__main__":
    app.run(debug=True)
