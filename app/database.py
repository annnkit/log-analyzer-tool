import sqlite3

DB_PATH = "logs.db"


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            timestamp TEXT,
            level TEXT,
            message TEXT,
            source_file TEXT
        )
    """)
    conn.commit()
    conn.close()

def append_logs(entries, source_file):
    conn = get_connection()
    for e in entries:
        conn.execute(
            "INSERT INTO logs VALUES (?, ?, ?, ?)",
            (e["timestamp"], e["level"], e["message"], source_file),
        )
    conn.commit()
    conn.close()
    return len(entries)


def insert_logs(entries, source_file):
    conn = get_connection()
    conn.execute("DELETE FROM logs WHERE source_file = ?", (source_file,))
    conn.commit()
    conn.close()
    return append_logs(entries, source_file)

def delete_file(source_file):
    conn = get_connection()
    cur = conn.execute("DELETE FROM logs WHERE source_file = ?", (source_file,))
    conn.commit()
    deleted = cur.rowcount   # how many rows the DELETE removed
    conn.close()
    return deleted