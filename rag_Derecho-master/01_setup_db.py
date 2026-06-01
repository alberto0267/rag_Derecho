import os
import psycopg
from dotenv import load_dotenv

load_dotenv()


def setup():
    conn = psycopg.connect(os.getenv("DATABASE_URL"))

    with conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id        SERIAL PRIMARY KEY,
                content   TEXT NOT NULL,
                source    TEXT NOT NULL,
                embedding vector(1536)
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS documents_embedding_idx
            ON documents
            USING hnsw (embedding vector_cosine_ops)
        """)

    conn.close()
    print("Base de datos lista.")


if __name__ == "__main__":
    setup()
