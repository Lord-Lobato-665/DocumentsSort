import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import os

_model = None
_vectorizer = None

def train_and_save_model(texts, labels, model_path="models/model.pkl", vectorizer_path="models/vectorizer.pkl"):
    os.makedirs(os.path.dirname(model_path), exist_ok=True)  # <- Aquí, crea la carpeta si no existe

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = MultinomialNB()
    model.fit(X, labels)

    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    return model, vectorizer

def load_model(model_path="models/model.pkl", vectorizer_path="models/vectorizer.pkl"):
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model = joblib.load(model_path)
        _vectorizer = joblib.load(vectorizer_path)
    return _model, _vectorizer

def predict_category(text):
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        load_model()  # Esto carga y asigna las variables globales

    X = _vectorizer.transform([text])
    prediction = _model.predict(X)
    return prediction[0]

