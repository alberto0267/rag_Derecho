# RAG Derecho

Chatbot conversacional con arquitectura RAG (Retrieval-Augmented Generation) para consultar documentación interna en lenguaje natural. Permite subir documentos PDF y DOCX y hacer preguntas sobre su contenido sin búsqueda manual.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Base de datos | PostgreSQL + pgvector |
| Embeddings | OpenAI `text-embedding-3-small` |
| LLM | OpenAI `gpt-4o-mini` |
| Frontend | React 19, TypeScript, Vite, TanStack Query |
| Contenedor DB | Docker |

## Cómo funciona

```
PDF/DOCX → Chunks (500 chars) → Embeddings → PostgreSQL (pgvector)
                                                      ↑
Pregunta → Reescritura (GPT) → Embedding → Búsqueda semántica → Contexto → GPT → Respuesta
```

## Requisitos

- Python 3.11+
- Node.js 18+
- pnpm
- Docker

## Arrancar el proyecto

### 1. Base de datos

```bash
docker run -d --name pgvector-rag -p 5432:5432 -e POSTGRES_PASSWORD=password pgvector/pgvector:pg16
docker exec pgvector-rag psql -U postgres -c "CREATE DATABASE ragdb;"
docker exec pgvector-rag psql -U postgres -d ragdb -c "CREATE EXTENSION vector;"
```

### 2. Backend

```bash
cd rag_Derecho-master
cp .env.example .env       # añade tu OPENAI_API_KEY
pip install -r requirements.txt
python 01_setup_db.py      # crea la tabla en PostgreSQL
python -m uvicorn 04_api:app --reload
```

API disponible en `http://localhost:8000/docs`

### 3. Frontend

```bash
cd rag-front
pnpm install
pnpm dev
```

App disponible en `http://localhost:5173`

## Variables de entorno

```env
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://postgres:password@localhost:5432/ragdb
```

## Estructura

```
rag_Derecho-master/          ← Backend
├── 04_api.py                ← Entrada FastAPI
├── db.py                    ← Conexión PostgreSQL
├── middleware/cors.py        ← CORS
├── routers/
│   ├── query.py             ← POST /query
│   ├── upload.py            ← POST /upload
│   └── documents.py         ← GET/DELETE /documents
├── services/
│   ├── rag.py               ← Lógica RAG (búsqueda + GPT)
│   └── ingest.py            ← Extracción, chunking, embeddings
├── schemas/                 ← Modelos Pydantic
└── docs/                    ← Documentos de prueba

rag-front/                   ← Frontend
└── src/
    ├── components/
    │   ├── Chat.tsx          ← Interfaz de chat con historial
    │   └── Documents.tsx     ← Upload y gestión de documentos
    └── api.ts                ← Llamadas al backend
```

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/query` | Pregunta con historial de conversación |
| POST | `/upload` | Subir PDF o DOCX |
| GET | `/documents` | Listar documentos subidos |
| DELETE | `/documents/{filename}` | Eliminar documento y sus embeddings |

## Documentos soportados

- PDF — incluyendo tablas (convertidas a Markdown)
- DOCX — texto y tablas
