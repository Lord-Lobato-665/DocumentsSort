from pydantic import BaseModel

class PredictRequest(BaseModel):
    document_text: str
