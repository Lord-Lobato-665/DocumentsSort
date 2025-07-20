from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime
from bson import ObjectId
from app.db.mongodb import get_collection
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime
from collections import Counter, defaultdict

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
spanish_stopwords = stopwords.words('spanish')

vectorizer = None
model = None

# Etiquetas descriptivas para los clusters
CLUSTER_NAMES = {
    0: "Actas y Resoluciones",
    1: "Normativas y Políticas",
    2: "Comunicaciones Internas",
    3: "Informes Técnicos"
}

# ========== TEXT MODEL TRAINING ==========

async def train_text_model():
    global vectorizer, model, CLUSTER_NAMES
    collection = await get_collection("documents")
    docs = await collection.find({}).to_list(length=None)

    # Separar textos con categoría forzada
    forced = [(doc["content"], doc["forced_category"]) for doc in docs if "content" in doc and "forced_category" in doc]
    unforced = [doc["content"] for doc in docs if "content" in doc and "forced_category" not in doc]

    if not forced and not unforced:
        raise ValueError("No hay documentos para entrenar.")

    all_texts = [text for text, _ in forced] + unforced
    vectorizer = TfidfVectorizer(stop_words=spanish_stopwords)
    X = vectorizer.fit_transform(all_texts)

    n_clusters = 4
    model = KMeans(n_clusters=n_clusters, random_state=42)
    model.fit(X)

    labels = model.labels_
    forced_labels = labels[:len(forced)]
    unforced_labels = labels[len(forced):]

    # Asociar cluster -> nombre dominante de categoría forzada
    cluster_to_categories = defaultdict(list)
    for i, (_, category) in enumerate(forced):
        cluster_to_categories[forced_labels[i]].append(category)

    CLUSTER_NAMES = {}
    for cluster_id, cats in cluster_to_categories.items():
        most_common = Counter(cats).most_common(1)[0][0]
        CLUSTER_NAMES[cluster_id] = most_common

    # Asignar clusters y actualizar MongoDB
    for i, doc in enumerate(docs):
        doc_id = doc["_id"]
        cluster_id = int(labels[i])
        await collection.update_one({"_id": doc_id}, {"$set": {"cluster": cluster_id}})

    # Guardar visualización
    save_text_cluster_graph(X, labels)
    
async def predict_cluster(text: str):
    global vectorizer, model
    if vectorizer is None or model is None:
        await train_text_model()
    X = vectorizer.transform([text])
    cluster = model.predict(X)[0]
    return int(cluster)

async def train_model():
    collection = await get_collection("documents")
    docs = await collection.find({}).to_list(length=None)
    texts = [doc["content"] for doc in docs if "content" in doc]
    if not texts:
        raise ValueError("No hay documentos con contenido para entrenar.")

    vec = TfidfVectorizer(stop_words=spanish_stopwords)
    X = vec.fit_transform(texts)
    km = KMeans(n_clusters=4, random_state=42)
    km.fit(X)

    labels = km.labels_
    for i, doc in enumerate(docs):
        await collection.update_one({"_id": doc["_id"]}, {"$set": {"cluster": int(labels[i])}})

    # Guarda la gráfica del cluster
    save_text_cluster_graph(X, labels)

    return True

async def cluster_documents():
    collection = await get_collection("documents")
    return await collection.aggregate([
        {"$group": {"_id": "$cluster", "docs": {"$push": "$filename"}}}
    ]).to_list(length=None)

# ========== GENERIC CLUSTER GRAPH ==========

def save_kmeans_graph(df, column_name, folder_name):
    """
    Genera y guarda una gráfica de clustering KMeans sobre una sola columna numérica.
    
    Args:
        df (pd.DataFrame): DataFrame que contiene los datos.
        column_name (str): Nombre de la columna numérica a agrupar (e.g. "file_size").
        folder_name (str): Carpeta donde se guardará la imagen generada.

    Returns:
        dict: Información del clustering con etiquetas, centroides y ruta del gráfico.
    """
    
    # 1. Crear la carpeta de gráficos si no existe
    os.makedirs(f"graphics/{folder_name}", exist_ok=True)
    image_path = f"graphics/{folder_name}/result.png"

    # 2. Eliminar imagen anterior si ya existe
    if os.path.exists(image_path):
        os.remove(image_path)

    # 3. Extraer la columna de interés y escalarla (normalizar)
    X = df[[column_name]]
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. Aplicar KMeans para agrupar los datos (3 clusters por defecto)
    kmeans = KMeans(n_clusters=3, random_state=42)
    cluster_labels = kmeans.fit_predict(X_scaled)

    # 5. Guardar los resultados en el DataFrame original
    df["cluster"] = cluster_labels
    cluster_centers = kmeans.cluster_centers_

    # 6. Invertir el escalado para obtener los valores reales de los centroides
    real_centers = scaler.inverse_transform(cluster_centers)

    # 7. Crear la gráfica
    plt.figure(figsize=(10, 4))
    
    # Dibujar los puntos, todos en una sola línea horizontal (eje Y = 0)
    plt.scatter(df[column_name], [0]*len(df), c=cluster_labels, cmap="viridis", s=60, label="Documentos")
    
    # Dibujar los centroides en rojo con una 'X'
    plt.scatter(real_centers, [0]*len(real_centers), c="red", marker="x", s=120, label="Centroides")

    # 8. Etiquetas y título
    plt.xlabel(column_name)
    plt.title(f"Agrupación KMeans de documentos según '{column_name}'")
    plt.yticks([])  # Eliminar eje Y para claridad
    plt.legend()

    # 9. Guardar y cerrar la imagen
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    # 10. Retornar información útil
    return {
        "labels": cluster_labels.tolist(),
        "centroids": real_centers.tolist(),
        "graph": image_path
    }

def predict_category(model, vectorizer, text: str) -> str:
    """Predice la categoría del documento dado el texto"""
    cleaned_text = clean_text(text)
    X = vectorizer.transform([cleaned_text])
    prediction = model.predict(X)[0]
    return str(prediction)  # O si tienes un mapping de etiquetas, úsalo aquí

def save_text_cluster_graph(X, labels, folder="text"):
    """
    Guarda una imagen visual del clustering de documentos (TF-IDF) reducidos a 2D con nombres personalizados.
    
    Args:
        X (scipy.sparse): Matriz TF-IDF.
        labels (list): Lista de clusters asignados por KMeans.
        folder (str): Carpeta donde guardar la imagen.
        
    Returns:
        str: Ruta de la imagen generada.
    """
    os.makedirs(f"graphics/{folder}", exist_ok=True)
    image_path = f"graphics/{folder}/clusters.png"
    
    if os.path.exists(image_path):
        os.remove(image_path)

    # Reducción de dimensiones para visualización
    pca = PCA(n_components=2)
    reduced = pca.fit_transform(X.toarray())

    # Gráfico principal
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(reduced[:, 0], reduced[:, 1], c=labels, cmap='viridis', alpha=0.7)

    # Anotar centros de cada cluster con nombres
    for cluster_id in sorted(set(labels)):
        points = reduced[np.array(labels) == cluster_id]
        center = np.mean(points, axis=0)
        label = CLUSTER_NAMES.get(cluster_id, f"Cluster {cluster_id}")
        count = len(points)
        plt.text(center[0], center[1], f"{label}\n({count})", fontsize=9, ha='center', va='center',
                 bbox=dict(facecolor='white', edgecolor='black', alpha=0.8))

    # Títulos y leyenda
    plt.title("Clustering de Documentos (TF-IDF + KMeans)")
    plt.xlabel("Componente Principal 1 (Mayor varianza)")
    plt.ylabel("Componente Principal 2 (Segunda mayor varianza)")

    # Timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    plt.figtext(0.99, 0.01, f"Generado: {timestamp}", ha='right', fontsize=8, color='gray')

    # Guardar
    plt.tight_layout()
    plt.savefig(image_path)
    plt.close()

    return image_path