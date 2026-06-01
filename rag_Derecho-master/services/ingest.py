import io
import pdfplumber
import docx
from openai import OpenAI
from db import get_connection

client = OpenAI()

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


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


def extract_text(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().split(".")[-1]
    if ext == "pdf":
        return extract_text_pdf(file_bytes)
    elif ext in ("docx",):
        return extract_text_docx(file_bytes)
    return ""


def chunk_text(text: str) -> list:
    chunks = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        chunks.append(text[start:end])
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def get_embedding(text: str) -> list:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def ingest_file(file_bytes: bytes, filename: str) -> int:
    text = extract_text(file_bytes, filename)
    chunks = chunk_text(text)

    conn = get_connection()
    total = 0

    with conn:
        for chunk in chunks:
            if not chunk.strip():
                continue
            embedding = get_embedding(chunk)
            embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
            conn.execute(
                "INSERT INTO documents (content, source, embedding) VALUES (%s, %s, %s::vector)",
                (chunk, filename, embedding_str)
            )
            total += 1

    conn.close()
    return total
