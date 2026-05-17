"""
小满 — 攒钱目标业务逻辑
"""
from database import get_db


def create_goal(user_id: int, name: str, target_amount: float) -> dict:
    """创建新目标（允许同时多个未完成目标）"""
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO goals (user_id, name, target_amount) VALUES (%s, %s, %s)",
        (user_id, name, target_amount),
    )
    conn.commit()
    goal = conn.execute("SELECT * FROM goals WHERE id = %s AND user_id = %s", (cur.lastrowid, user_id)).fetchone()
    conn.close()

    weekly = round(target_amount / 4, 1)
    return {
        "goal": goal,
        "message": f"好的！「{name}」¥{target_amount:.0f}，每周攒¥{weekly}一个月拿下 💪",
    }


def get_goals(user_id: int) -> dict:
    """查询所有目标（未完成在前，已完成在后）"""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM goals WHERE user_id = %s ORDER BY completed ASC, created_at DESC", (user_id,)
    ).fetchall()
    conn.close()

    goals = list(rows)
    completed_count = sum(1 for g in goals if g["completed"])

    if not goals:
        return {"goals": [], "completed_count": 0, "progress_text": "还没有攒钱目标，去对话页跟小满说一声吧~"}

    return {"goals": goals, "completed_count": completed_count}


def delete_goal(user_id: int, goal_id: int) -> bool:
    """删除指定目标"""
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id = %s AND user_id = %s", (goal_id, user_id))
    conn.commit()
    conn.close()
    return True


def add_savings(user_id: int, amount: float = 2.0, goal_id: int | None = None) -> dict | None:
    """攒钱到指定目标（未指定则攒到最近创建的未完成目标）"""
    conn = get_db()
    if goal_id:
        goal = conn.execute("SELECT * FROM goals WHERE id = %s AND user_id = %s", (goal_id, user_id)).fetchone()
    else:
        goal = conn.execute(
            "SELECT * FROM goals WHERE user_id = %s AND completed = 0 ORDER BY created_at DESC LIMIT 1", (user_id,)
        ).fetchone()
    if not goal:
        conn.close()
        return None

    from datetime import datetime
    new_saved = min(goal["target_amount"], goal["saved_amount"] + amount)
    completed = 1 if new_saved >= goal["target_amount"] else 0
    now = datetime.now().isoformat() if completed else None
    conn.execute(
        "UPDATE goals SET saved_amount = %s, completed = %s, completed_at = %s WHERE id = %s AND user_id = %s",
        (new_saved, completed, now, goal["id"], user_id),
    )
    conn.commit()
    g = conn.execute("SELECT * FROM goals WHERE id = %s AND user_id = %s", (goal["id"], user_id)).fetchone()
    conn.close()
    return {"goal": g}


def dismiss_completed_goal(user_id: int) -> bool:
    """移除已完成超过24小时的目标"""
    conn = get_db()
    from datetime import datetime, timedelta
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    conn.execute(
        "DELETE FROM goals WHERE user_id = %s AND completed = 1 AND completed_at IS NOT NULL AND completed_at < %s",
        (user_id, cutoff),
    )
    conn.commit()
    conn.close()
    return True


def get_completed_count(user_id: int) -> int:
    """已完成目标总数"""
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) as cnt FROM goals WHERE user_id = %s AND completed = 1", (user_id,)).fetchone()
    conn.close()
    return row["cnt"] if row else 0


def dismiss_goal(user_id: int, goal_id: int) -> bool:
    """手动移除已完成目标"""
    conn = get_db()
    conn.execute("DELETE FROM goals WHERE id = %s AND user_id = %s AND completed = 1", (goal_id, user_id))
    conn.commit()
    conn.close()
    return True
