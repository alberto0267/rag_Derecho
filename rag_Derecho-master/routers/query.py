from fastapi import APIRouter, HTTPException, Depends
from schemas.question import Question, Answer
from services.rag import ask
from middleware.auth import get_user_id

router = APIRouter()


@router.post("/query", response_model=Answer)
def query(body: Question, user_id: str = Depends(get_user_id)):
    try:
        history = [{"role": m.role, "content": m.content} for m in body.history]
        return ask(body.question, history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
