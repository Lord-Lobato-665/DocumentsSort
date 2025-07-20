from app.ml.model import train_and_save_model


# Datos de ejemplo, reemplaza por tus datos reales
texts = [
    "Se presenta el informe correspondiente al periodo anteriormente señalado, en el cual se describen las actividades realizadas, los resultados obtenidos y las observaciones relevantes.",
    "ACTA DE REUNIÓN ORDINARIA DEL CONSEJO DIRECTIVO",
    "representada en este acto por, en su carácter de",
    "Durante el periodo evaluado se registra un avance financiero del [XX]% respecto al presupuesto aprobado. Los recursos se han ejercido conforme a la planeación origi-nal, con ajustes mínimos en algunos rubros estratégicos.",
    "1. Objetivo del Proyecto Describir claramente el propósito general del proyecto:",
    "Por este conducto, me permito dirigirme a usted de la manera más atenta para ",
]

labels = [
    "Informes y Reportes",
    "Actas y Acuerdos",
    "Contratos y Convenios",
    "Documentación Financiera y Presupuestaria",
    "Expedientes Técnicos y Proyectos",
    "Oficios y Comunicaciones Oficiales",
]

if __name__ == "__main__":
    model, vectorizer = train_and_save_model(texts, labels)
    print("Modelo entrenado y guardado correctamente.")
