from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class Document(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    created_at: Optional[datetime]
    filename: str
    categories: List[str]
    original_category: Optional[str] = None
    moved: bool = False
    content: str
    filepath: str
    cluster: Optional[int] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True

