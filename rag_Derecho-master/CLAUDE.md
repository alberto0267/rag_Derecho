# RAG con Python + PostgreSQL — Guía de aprendizaje

## Regla de oro

No avanzamos al siguiente paso hasta que entiendas el anterior. Cada archivo se explica línea a línea antes de ejecutar. Si algo no está claro, paramos y lo debatimos.

---

## ¿Qué es RAG?

**RAG = Retrieval-Augmented Generation**

El problema: los LLMs (ChatGPT, Claude) no conocen *tu* información privada. RAG es la técnica para darles contexto relevante antes de responder, sin reentrenar el modelo.

```
Documentos → Chunks → Embeddings → PostgreSQL (pgvector)
                                          ↑
Pregunta del usuario → Embedding → Búsqueda semántica → Contexto → LLM → Respuesta
```

---

## Stack técnico — Por qué cada pieza

| Componente | Herramienta | Por qué |
|---|---|---|
| Lenguaje | Python 3.11+ | Estándar en IA/ML, más recursos y ejemplos |
| Base de datos | PostgreSQL + pgvector | Búsqueda vectorial en SQL puro, sin servicios externos |
| Embeddings | OpenAI `text-embedding-3-small` | Anthropic no tiene embeddings; OpenAI es el estándar |
| LLM | OpenAI `gpt-4o-mini` | Barato (~$0.15/1M tokens), suficiente para aprender |
| DB client | `psycopg` | Maduro, sin magia extra |
| Env vars | `python-dotenv` | Para guardar la API key sin exponerla en el código |
| API | FastAPI + Uvicorn | Framework moderno, genera Swagger automático, compatible con Angular |
| Frontend | Angular (pendiente) | Consume la API via HTTP, UI de chat y subida de PDFs |

**Costo total para aprender:** < $0.10 USD

---

## Estructura del proyecto

```
rag-postgres/
├── CLAUDE.md             ← estás aquí
├── .env                  ← OPENAI_API_KEY y DATABASE_URL (nunca al git)
├── requirements.txt      ← dependencias Python
├── db.py                 ← conexión a PostgreSQL (get_connection)
├── 01_setup_db.py        ← Paso 1: crear la tabla con columna vector
├── 02_ingest.py          ← Paso 2: CLI para ingestar PDFs desde /docs
├── 03_query.py           ← Paso 3: preguntar por terminal (debug/aprendizaje)
├── 04_api.py             ← Servidor FastAPI (entrada principal)
├── middleware/
│   └── cors.py           ← CORS para permitir llamadas desde Angular (puerto 4200)
├── routers/
│   ├── query.py          ← POST /query — recibe pregunta, devuelve respuesta JSON
│   └── upload.py         ← POST /upload — recibe PDF, lo ingesta en la DB
├── services/
│   ├── rag.py            ← lógica de búsqueda semántica y respuesta con GPT
│   └── ingest.py         ← lógica de extracción, chunking y embeddings (usada por 02 y upload)
├── schemas/
│   └── question.py       ← modelos Pydantic: Question (entrada) y Answer (salida)
└── docs/                 ← PDFs de prueba
    └── guia_tecnica.pdf
```

**Regla de capas:** cada capa tiene una sola responsabilidad. Los routers solo gestionan HTTP, los servicios solo contienen lógica, `db.py` solo gestiona la conexión.

**Sin duplicación:** `02_ingest.py` y `routers/upload.py` comparten el mismo código — ambos importan desde `services/ingest.py`.

Los archivos están numerados a propósito. El flujo de aprendizaje va en orden.

---

## Conceptos clave que aprenderás

1. **Embeddings** — representación matemática del significado de un texto (vector de 1536 números). Textos similares tienen vectores similares.
2. **Chunking** — dividir documentos grandes en piezas manejables (~500 tokens). Si no chunkeamos, el embedding pierde precisión.
3. **Similaridad coseno** (`<=>`) — medir qué tan "cerca" están dos vectores en el espacio matemático. Más cerca = más parecido en significado.
4. **Prompt engineering** — construir el prompt correctamente para que el LLM use el contexto recuperado y no "invente".
5. **pgvector** — extensión de PostgreSQL que permite guardar vectores y hacer búsquedas de similitud directamente en SQL.

---

## Prerequisitos antes de empezar

- [ ] Python 3.11+ instalado
- [ ] PostgreSQL con pgvector — opción más fácil: `docker run -p 5432:5432 pgvector/pgvector:pg16`
- [ ] API key de OpenAI (crea cuenta en platform.openai.com, cuesta centavos para aprender)

---

## Verificación — cómo saber que funciona

1. `python 01_setup_db.py` → debe crear la tabla sin errores
2. `python 02_ingest.py` → debe mostrar "X chunks guardados"
3. `python 03_query.py` → pregunta algo que esté en tus docs → debe responder con esa info
4. Prueba preguntar algo que NO esté en los docs → debe decir que no tiene esa información

---

## Notas de diseño

- No usamos LangChain ni LlamaIndex a propósito — esos frameworks esconden la magia. Aquí cada línea es explícita para que entiendas qué hace cada paso.
- Cuando entiendas todo, refactorizar a LangChain es trivial y sabrás exactamente qué hace por debajo.
