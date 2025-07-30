import joblib
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score


from app.db.mongodb import get_collection

# Rutas centralizadas
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "model.pkl")
VECTORIZER_PATH = os.path.join(MODEL_DIR, "vectorizer.pkl")

# Variables globales (caché en memoria)
_model = None
_vectorizer = None

def _clear_cache():
    global _model, _vectorizer
    _model = None
    _vectorizer = None

async def train_model_from_db():
    collection = await get_collection("training_examples")
    examples = await collection.find().to_list(None)

    texts = [e["text"] for e in examples]
    labels = [e["category"] for e in examples]

    if not texts or not labels:
        raise ValueError("No hay datos para entrenar el modelo")

    # 🔥 Limpia modelos anteriores en disco
    if os.path.exists(MODEL_PATH):
        os.remove(MODEL_PATH)
    if os.path.exists(VECTORIZER_PATH):
        os.remove(VECTORIZER_PATH)

    # 🧠 Entrenamiento
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)
    model = MultinomialNB()
    model.fit(X, labels)

    # 💾 Guardado
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    # 🧹 Limpieza de cache vieja para que se cargue la nueva en predicción
    _clear_cache()

    return {"message": "Modelo entrenado y guardado correctamente"}

def load_model():
    global _model, _vectorizer
    if _model is None or _vectorizer is None:
        _model = joblib.load(MODEL_PATH)
        _vectorizer = joblib.load(VECTORIZER_PATH)
    return _model, _vectorizer

def predict_category(text: str) -> str:
    model, vectorizer = load_model()
    X = vectorizer.transform([text])
    return model.predict(X)[0]

async def evaluate_model_accuracy():
    collection = await get_collection("training_examples")
    examples = await collection.find().to_list(None)

    if not examples:
        raise ValueError("No hay ejemplos en la base de datos para evaluar")

    texts = [e["text"] for e in examples]
    labels = [e["category"] for e in examples]

    model, vectorizer = load_model()
    X = vectorizer.transform(texts)
    predictions = model.predict(X)

    accuracy = accuracy_score(labels, predictions)
    return {"accuracy": round(accuracy, 4)}
