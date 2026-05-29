import sqlite3


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect("planner.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                time  TEXT NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
        """)
