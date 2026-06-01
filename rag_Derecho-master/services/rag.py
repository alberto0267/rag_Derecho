from openai import OpenAI
from db import get_connection
from services.tools import TOOLS, execute_tool

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

    system_prompt = f"""Responde ÚNICAMENTE usando el contexto de documentos internos proporcionado o las herramientas disponibles.
NUNCA uses tu conocimiento de entrenamiento para responder.
Si la información no está en el contexto, DEBES usar la herramienta search_web.

Contexto:
{context}"""

    messages = [{"role": "system", "content": system_prompt}] + history + [{"role": "user", "content": question}]

    # Primera llamada — GPT decide si responde o usa una tool
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        tools=TOOLS,
        tool_choice="auto"
    )

    message = response.choices[0].message

    # Si GPT quiere usar una tool
    tool_used = None

    if message.tool_calls:
        tool_call = message.tool_calls[0]
        tool_used = tool_call.function.name
        tool_result = execute_tool(tool_used, tool_call.function.arguments)

        messages.append(message)
        messages.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": tool_result
        })

        final_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        answer = final_response.choices[0].message.content
    else:
        answer = message.content

    sources = [] if tool_used else [{"file": row[1], "similarity": round(row[2], 2)} for row in chunks]

    return {
        "answer": answer,
        "sources": sources,
        "tool_used": tool_used
    }
