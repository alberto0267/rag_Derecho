import os
import psycopg
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def rewrite_query(question):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Convierte esto en una afirmación clara como si fuera un fragmento de documentación técnica. Solo devuelve la afirmación, sin explicaciones:\n\n{question}"}]
    )
    return response.choices[0].message.content


def get_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def search(conn, question):
    rewritten = rewrite_query(question)
    embedding = get_embedding(rewritten)
    embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

    rows = conn.execute("""
        SELECT content, source, 1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT 5
    """, (embedding_str, embedding_str)).fetchall()

    return rows


def ask(question):
    conn = psycopg.connect(os.getenv("DATABASE_URL"))
    chunks = search(conn, question)
    conn.close()

    context = "\n\n---\n\n".join([row[0] for row in chunks])

    prompt = f"""Responde usando SOLO el siguiente contexto.
Si la respuesta no está en el contexto, di exactamente: "No tengo esa información en los documentos."

Contexto:
{context}

Pregunta: {question}"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response.choices[0].message.content

    print("\nRespuesta:")
    print(answer)
    print("\nFuentes usadas:")
    for row in chunks:
        print(f"  - {row[1]} (similitud: {row[2]:.2f})")


if __name__ == "__main__":
    question = input("Pregunta: ")
    ask(question)
