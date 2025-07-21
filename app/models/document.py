from pydantic import BaseModel
from typing import Optional
from typing import List, Optional
from pydantic import BaseModel

class Document(BaseModel):
    filename: str
    categories: List[str]           # plural y lista
    content: str
    filepath: str                   # el nombre exacto que usas en la BD
    cluster: Optional[int] = None
