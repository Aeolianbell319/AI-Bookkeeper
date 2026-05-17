"""
小满 — 对话消息持久化
"""

from database import get_db

MAX_MESSAGES = 200  # 保留最近 200 条


def save_message(user_id: int, role: str, content: str) -> dict:
    """保存单条消息"""
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
        (user_id, role, content),
    )
    conn.commit()
    msg = conn.execute("SELECT * FROM messages WHERE id = %s", (cur.lastrowid,)).fetchone()
    conn.close()
    return msg


def save_messages(user_id: int, messages: list[dict]) -> bool:
    """批量保存消息，保存后自动清理旧消息"""
    if not messages:
        return True
    conn = get_db()
    for m in messages:
        conn.execute(
            "INSERT INTO messages (user_id, role, content) VALUES (%s, %s, %s)",
            (user_id, m["role"], m["content"]),
        )
    _trim_old_messages(conn, user_id)
    conn.commit()
    conn.close()
    return True


def get_messages(user_id: int, limit: int = 100) -> list[dict]:
    """获取最近 N 条消息，按时间正序返回"""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, role, content, created_at FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s",
        (user_id, limit),
    ).fetchall()
    conn.close()
    rows.reverse()
    return rows


def _trim_old_messages(conn, user_id: int):
    """保留最近 MAX_MESSAGES 条，删除更早的"""
    conn.execute("""
        DELETE FROM messages WHERE user_id = %s AND id NOT IN (
            SELECT id FROM (
                SELECT id FROM messages WHERE user_id = %s ORDER BY id DESC LIMIT %s
            ) AS t
        )
    """, (user_id, user_id, MAX_MESSAGES))


def clear_messages(user_id: int) -> bool:
    """清空所有消息"""
    conn = get_db()
    conn.execute("DELETE FROM messages WHERE user_id = %s", (user_id,))
    conn.commit()
    conn.close()
    return True
