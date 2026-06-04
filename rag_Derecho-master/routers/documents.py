from fastapi import APIRouter, HTTPException, Depends
from schemas.document import DocumentInfo
from services.documents import list_documents, delete_document
from middleware.auth import get_user_id

router = APIRouter()


@router.get("/documents", response_model=list[DocumentInfo])
def get_documents(user_id: str = Depends(get_user_id)):
    try:
        return list_documents(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
def remove_document(filename: str, user_id: str = Depends(get_user_id)):
    try:
        deleted = delete_document(filename, user_id)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {"deleted_chunks": deleted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
