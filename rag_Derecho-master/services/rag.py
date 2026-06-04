# LangChain LCEL: el pipeline RAG se define como una cadena de componentes encadenados con |
# Retriever (pgvector) | Prompt | LLM | Parser
# El tool-calling se gestiona manualmente porque LangChain no soporta tools + RAG en una sola chain simple.
from dotenv import load_dotenv
load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector
from services.tools import TOOLS, execute_tool
import os

CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ragdb").replace(
    "postgresql://", "postgresql+psycopg://"
)

llm = ChatOpenAI(model="gpt-4o-mini")
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

prompt = ChatPromptTemplate.from_messages([
    ("system", """Responde ÚNICAMENTE usando el contexto de documentos internos proporcionado o las herramientas disponibles.
NUNCA uses tu conocimiento de entrenamiento para responder.
Si la información no está en el contexto, DEBES usar la herramienta search_web.

Contexto:
{context}"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{question}"),
])


def get_retriever():
    vectorstore = PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=CONNECTION_STRING,
    )
    return vectorstore.as_retriever(search_kwargs={"k": 5})


def format_docs(docs) -> str:
    return "\n\n---\n\n".join([doc.page_content for doc in docs])


def build_history(history: list) -> list:
    messages = []
    for msg in history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
    return messages


def ask(question: str, history: list) -> dict:
    retriever = get_retriever()
    docs = retriever.invoke(question)
    context = format_docs(docs)
    sources = [{"file": doc.metadata.get("source", ""), "similarity": 0} for doc in docs]

    # LCEL chain: prompt | llm con tools | parser
    chain = prompt | llm.bind_tools(TOOLS) | StrOutputParser()

    tool_used = None
    lc_history = build_history(history)

    # Primera llamada — GPT decide si responde o usa una tool
    response = (prompt | llm.bind_tools(TOOLS)).invoke({
        "context": context,
        "history": lc_history,
        "question": question
    })

    if response.tool_calls:
        import json
        tool_call = response.tool_calls[0]
        tool_used = tool_call["name"]
        tool_result = execute_tool(tool_used, json.dumps(tool_call["args"]))

        # Segunda llamada — GPT formula la respuesta con el resultado de la tool
        final_chain = prompt | llm | StrOutputParser()
        answer = final_chain.invoke({
            "context": tool_result,
            "history": lc_history,
            "question": question
        })
        sources = []
    else:
        parser = StrOutputParser()
        answer = parser.invoke(response)

    return {
        "answer": answer,
        "sources": sources,
        "tool_used": tool_used
    }
