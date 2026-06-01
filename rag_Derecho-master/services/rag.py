from openai import OpenAI
from db import get_connection

client = OpenAI()


def rewrite_query(question: str, history: list) -> str:
    messages = history + [{"role": "user", "content": f"Convierte esto en una afirmación clara como si fuera un fragmento de documentación técnica. Solo devuelve la afirmación, sin explicaciones:\n\n{question}"}]
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )
    return response.choices[0].message.content


def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def search(question: str, history: list) -> list:
    rewritten = rewrite_query(question, history)
    embedding = get_embedding(rewritten)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    conn = get_connection()
    rows = conn.execute("""
        SELECT content, source, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT 5
    """, (embedding_str, embedding_str)).fetchall()
    conn.close()

    return rows


def ask(question: str, history: list) -> dict:
    chunks = search(question, history)
    context = "\n\n---\n\n".join([row[0] for row in chunks])

    system_prompt = f"""Responde usando SOLO el siguiente contexto.
Si la respuesta no está en el contexto, di exactamente: "No tengo esa información en los documentos."

Contexto:
{context}"""

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": question}]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    return {
        "answer": response.choices[0].message.content,
        "sources": [{"file": row[1], "similarity": round(row[2], 2)} for row in chunks]
    }
