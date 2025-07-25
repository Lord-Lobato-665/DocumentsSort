from pydantic import BaseModel, Field
from typing import List, Optional

class Document(BaseModel):
    id: Optional[str] = Field(None, alias="_id")  # Nuevo campo para el ObjectId
    filename: str
    categories: List[str]
    content: str
    filepath: str
    cluster: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

