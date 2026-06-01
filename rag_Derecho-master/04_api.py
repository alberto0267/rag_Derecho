from fastapi import FastAPI
from middleware.cors import add_cors
from routers import query, upload, documents

app = FastAPI()

add_cors(app)

app.include_router(query.router)
app.include_router(upload.router)
app.include_router(documents.router)
