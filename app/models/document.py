from pydantic import BaseModel
from typing import Optional

class Document(BaseModel):
    filename: str
    category: str
    content: str
    path: str
    cluster: Optional[int] = None
