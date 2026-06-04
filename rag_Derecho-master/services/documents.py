from db import get_connection


def list_documents(user_id: str) -> list:
    conn = get_connection()
    try:
        rows = conn.execute("""
            SELECT cmetadata->>'source' AS source, COUNT(*) as chunks
            FROM langchain_pg_embedding
            WHERE cmetadata->>'user_id' = %s
            GROUP BY source
            ORDER BY source
        """, (user_id,)).fetchall()
        return [{"filename": row[0], "chunks": row[1]} for row in rows]
    except Exception:
        return []
    finally:
        conn.close()


def delete_document(filename: str, user_id: str) -> int:
    conn = get_connection()
    with conn:
        result = conn.execute(
            "DELETE FROM langchain_pg_embedding WHERE cmetadata->>'source' = %s AND cmetadata->>'user_id' = %s",
            (filename, user_id)
        )
        deleted = result.rowcount
    conn.close()
    return deleted
