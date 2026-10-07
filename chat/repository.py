import sqlite3

from config.settings import DB_FILE


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            FOREIGN KEY (session_id)
                REFERENCES sessions(id)
                ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


def get_all_sessions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title
        FROM sessions
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return rows


def create_session(title="Nueva Sesión"):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO sessions (title) VALUES (?)",
        (title,)
    )

    session_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return session_id


def delete_session(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM messages WHERE session_id = ?",
        (session_id,)
    )

    cursor.execute(
        "DELETE FROM sessions WHERE id = ?",
        (session_id,)
    )

    conn.commit()
    conn.close()


def get_messages(session_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def save_message(session_id, role, content):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO messages (session_id, role, content)
        VALUES (?, ?, ?)
    """, (session_id, role, content))

    conn.commit()
    conn.close()


def update_session_title(session_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE sessions
        SET title = ?
        WHERE id = ?
    """, (title, session_id))

    conn.commit()
    conn.close()