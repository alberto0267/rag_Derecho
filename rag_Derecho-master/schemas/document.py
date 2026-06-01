from pydantic import BaseModel


class DocumentInfo(BaseModel):
    filename: str
    chunks: int
