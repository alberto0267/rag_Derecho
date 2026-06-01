from fastapi import APIRouter, UploadFile, File, HTTPException
from services.ingest import ingest_file

router = APIRouter()

ALLOWED_EXTENSIONS = {"pdf", "docx"}


@router.post("/upload")
async def upload(file: UploadFile = File(...)):
    ext = file.filename.split(".")[-1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF y DOCX")
    try:
        content = await file.read()
        chunks_saved = ingest_file(content, file.filename)
        return {"filename": file.filename, "chunks_saved": chunks_saved}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
