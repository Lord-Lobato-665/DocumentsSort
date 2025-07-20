import os
from fastapi import UploadFile
from dotenv import dotenv_values
config = dotenv_values(".env")

async def save_document(file: UploadFile, category: str):
    dir_name = category.replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i")
    dir_path = os.path.join(config["DOCUMENT_ROOT"], dir_name)

    os.makedirs(dir_path, exist_ok=True)
    file_path = os.path.join(dir_path, file.filename)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return file_path, content.decode("utf-8", errors="ignore")
