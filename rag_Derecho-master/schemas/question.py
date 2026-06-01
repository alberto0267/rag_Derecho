from pydantic import BaseModel


class HistoryMessage(BaseModel):
    role: str
    content: str


class Question(BaseModel):
    question: str
    history: list[HistoryMessage] = []


class Answer(BaseModel):
    answer: str
    sources: list[dict]
    tool_used: str | None = None
