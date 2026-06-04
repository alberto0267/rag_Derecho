# Híbrido: extracción de texto propia (pdfplumber) para preservar tablas en Markdown,
# LangChain para chunking semántico (RecursiveCharacterTextSplitter),
# embeddings (OpenAIEmbeddings) y vectorstore (PGVector).
from dotenv import load_dotenv
load_dotenv()

import io
import os
import pdfplumber
import docx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_postgres import PGVector

CONNECTION_STRING = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/ragdb").replace(
    "postgresql://", "postgresql+psycopg://"
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)


def get_vectorstore() -> PGVector:
    return PGVector(
        embeddings=embeddings,
        collection_name="documents",
        connection=CONNECTION_STRING,
    )


def table_to_markdown(table):
    if not table or not table[0]:
        return ""
    rows = []
    header = ["" if cell is None else str(cell) for cell in table[0]]
    rows.append("| " + " | ".join(header) + " |")
    rows.append("| " + " | ".join("---" for _ in header) + " |")
    for row in table[1:]:
        cells = ["" if cell is None else str(cell) for cell in row]
        rows.append("| " + " | ".join(cells) + " |")
    return "\n".join(rows)


def extract_text_pdf(file_bytes: bytes) -> str:
    full_text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            tables = page.find_tables()
            table_bboxes = [t.bbox for t in tables]

            def not_in_table(obj):
                for bbox in table_bboxes:
                    if (obj.get("x0", 0) >= bbox[0] - 1 and
                            obj.get("x1", 0) <= bbox[2] + 1 and
                            obj.get("top", 0) >= bbox[1] - 1 and
                            obj.get("bottom", 0) <= bbox[3] + 1):
                        return False
                return True

            text = page.filter(not_in_table).extract_text() or ""
            if text.strip():
                full_text += text.strip() + "\n\n"

            for table in tables:
                data = table.extract()
                if data:
                    md = table_to_markdown(data)
                    if md:
                        full_text += md + "\n\n"

    return full_text


def extract_text_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    parts = []

    for element in doc.element.body:
        tag = element.tag.split("}")[-1]

        if tag == "p":
            paragraph = docx.text.paragraph.Paragraph(element, doc)
            text = paragraph.text.strip()
            if text:
                parts.append(text)

        elif tag == "tbl":
            table = docx.table.Table(element, doc)
            rows = []
            for i, row in enumerate(table.rows):
                cells = [cell.text.strip() for cell in row.cells]
                rows.append("| " + " | ".join(cells) + " |")
                if i == 0:
                    rows.append("| " + " | ".join("---" for _ in cells) + " |")
            parts.append("\n".join(rows))

    return "\n\n".join(parts)


def ingest_file(file_bytes: bytes, filename: str, user_id: str) -> int:
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        text = extract_text_pdf(file_bytes)
    elif ext == "docx":
        text = extract_text_docx(file_bytes)
    else:
        return 0

    chunks = splitter.create_documents(
        texts=[text],
        metadatas=[{"source": filename, "user_id": user_id}]
    )

    vectorstore = get_vectorstore()
    vectorstore.add_documents(chunks)

    return len(chunks)
