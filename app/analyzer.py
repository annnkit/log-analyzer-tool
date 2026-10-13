from app.database import get_connection

def list_files():
    conn = get_connection()
    rows = conn.execute(
        "SELECT source_file, COUNT(*) FROM logs GROUP BY source_file ORDER BY source_file"
    ).fetchall()
    conn.close()
    return [{"source_file": f, "count": c} for f, c in rows]


def count_by_level(source_file=None):
    query = "SELECT level, COUNT(*) FROM logs"
    params = []
    if source_file:
        query += " WHERE source_file = ?"
        params.append(source_file)
    query += " GROUP BY level"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return dict(rows)


def top_errors(limit=3):
    conn = get_connection()
    rows = conn.execute(
        """SELECT message, COUNT(*) FROM logs
           WHERE level = 'ERROR'
           GROUP BY message
           ORDER BY COUNT(*) DESC
           LIMIT ?""",
        (limit,),
    ).fetchall()
    conn.close()
    return [{"message": m, "count": c} for m, c in rows]

def errors_per_hour():
    conn = get_connection()
    rows = conn.execute(
        """SELECT substr(timestamp, 1, 13) as hour, COUNT(*) as count FROM logs
           WHERE level = 'ERROR'
           GROUP BY hour
           ORDER BY hour"""
    ).fetchall()
    conn.close()
    return [{"hour": h, "count": c} for h, c in rows]

def search_logs(level=None, keyword=None, limit=50):
    query = "SELECT timestamp, level, message FROM logs WHERE 1=1"
    params = []

    if level:
        query += " AND level = ?"
        params.append(level.upper())
    if keyword:
        query += " AND message LIKE ?"
        params.append(f"%{keyword}%")

    query += " ORDER BY timestamp DESC LIMIT ?"
    params.append(limit)

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [{"timestamp": t, "level": l, "message": m} for t, l, m in rows]