from db import get_connection


def list_documents() -> list:
    conn = get_connection()
    rows = conn.execute("""
        SELECT source, COUNT(*) as chunks
        FROM documents
        GROUP BY source
        ORDER BY source
    """).fetchall()
    conn.close()
    return [{"filename": row[0], "chunks": row[1]} for row in rows]


def delete_document(filename: str) -> int:
    conn = get_connection()
    with conn:
        result = conn.execute(
            "DELETE FROM documents WHERE source = %s",
            (filename,)
        )
        deleted = result.rowcount
    conn.close()
    return deleted
