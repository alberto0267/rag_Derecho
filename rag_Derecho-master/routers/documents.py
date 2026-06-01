from fastapi import APIRouter, HTTPException
from schemas.document import DocumentInfo
from services.documents import list_documents, delete_document

router = APIRouter()


@router.get("/documents", response_model=list[DocumentInfo])
def get_documents():
    try:
        return list_documents()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/documents/{filename}")
def remove_document(filename: str):
    try:
        deleted = delete_document(filename)
        if deleted == 0:
            raise HTTPException(status_code=404, detail="Documento no encontrado")
        return {"deleted_chunks": deleted}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
