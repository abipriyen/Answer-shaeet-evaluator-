from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def evaluate_answer(model_answer, student_answer):
    documents = [model_answer, student_answer]
    vectorizer = TfidfVectorizer().fit_transform(documents)
    similarity = cosine_similarity(vectorizer[0:1], vectorizer[1:2])[0][0]
    score = round(similarity * 10, 2)
    return score, similarity
