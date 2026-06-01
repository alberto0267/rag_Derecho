from fastapi import APIRouter, HTTPException
from schemas.question import Question, Answer
from services.rag import ask

router = APIRouter()


@router.post("/query", response_model=Answer)
def query(body: Question):
    try:
        history = [{"role": m.role, "content": m.content} for m in body.history]
        return ask(body.question, history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
