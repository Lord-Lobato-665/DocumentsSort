# app/schemas/training_example.py
from pydantic import BaseModel

class TrainingExample(BaseModel):
    category: str
    text: str
