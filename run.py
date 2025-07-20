import uvicorn
import webbrowser
import time
import os
from dotenv import load_dotenv

# Carga las variables de entorno
load_dotenv()

def run():
    host = "127.0.0.1"
    port = 8000
    url = f"http://{host}:{port}/docs"

    print("[🚀] Iniciando backend de clasificación documental...")
    
    # Espera para abrir el navegador después del arranque
    def open_browser():
        time.sleep(1.5)
        webbrowser.open(url)

    import threading
    threading.Thread(target=open_browser).start()

    # Ejecuta el servidor
    uvicorn.run("app.main:app", host=host, port=port, reload=True)

if __name__ == "__main__":
    run()
