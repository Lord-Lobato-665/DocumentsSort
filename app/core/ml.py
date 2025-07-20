from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from app.db.mongodb import get_collection

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

spanish_stopwords = stopwords.words('spanish')

async def train_model():
    collection = await get_collection("documents")
    docs = await collection.find({}).to_list(length=None)
    texts = [doc["content"] for doc in docs if "content" in doc]

    if not texts:
        raise ValueError("No hay documentos con contenido para entrenar.")

    vectorizer = TfidfVectorizer(stop_words=spanish_stopwords)
    X = vectorizer.fit_transform(texts)

    model = KMeans(n_clusters=4, random_state=42)
    model.fit(X)

    labels = model.labels_
    for i, doc in enumerate(docs):
        await collection.update_one({"_id": doc["_id"]}, {"$set": {"cluster": int(labels[i])}})

    return True

async def cluster_documents():
    collection = await get_collection("documents")
    clusters = await collection.aggregate([
        {"$group": {"_id": "$cluster", "docs": {"$push": "$filename"}}}
    ]).to_list(length=None)
    return clusters