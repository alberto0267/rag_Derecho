import os
from services.ingest import ingest_file


def ingest():
    docs_folder = os.path.join(os.path.dirname(__file__), "docs")

    for filename in os.listdir(docs_folder):
        if not filename.lower().endswith((".pdf", ".docx")):
            continue

        path = os.path.join(docs_folder, filename)
        print(f"Procesando: {filename}")

        with open(path, "rb") as f:
            pdf_bytes = f.read()

        total = ingest_file(pdf_bytes, filename)
        print(f"{total} chunks guardados.")


if __name__ == "__main__":
    ingest()
