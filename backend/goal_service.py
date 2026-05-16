"""
小满 — 攒钱目标业务逻辑
"""
from database import get_db


def create_goal(name: str, target_amount: float) -> dict:
    """创建新目标（先检查是否已有未完成目标）"""
    conn = get_db()
    existing = conn.execute(
        "SELECT * FROM goals WHERE completed = 0 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if existing:
        conn.close()
        return {"goal": None, "message": "你还有一个未完成的目标「" + existing["name"] + "」，先完成它再定新的吧~"}

    cur = conn.execute(
        "INSERT INTO goals (name, target_amount) VALUES (?, ?)",
        (name, target_amount),
    )
    conn.commit()
    goal = dict(conn.execute("SELECT * FROM goals WHERE id = ?", (cur.lastrowid,)).fetchone())
    conn.close()

    weekly = round(target_amount / 4, 1)
    return {
        "goal": goal,
        "message": f"好的！「{name}」¥{target_amount:.0f}，每周攒¥{weekly}一个月拿下 💪",
    }


def get_goal() -> dict:
    """查询当前目标（优先级：未完成 > 最近完成）"""
    conn = get_db()
    goal = conn.execute(
        "SELECT * FROM goals ORDER BY completed ASC, created_at DESC LIMIT 1"
    ).fetchone()
    conn.close()

    if not goal:
        return {"goal": None, "progress_text": "还没有攒钱目标，去对话页跟小满说一声吧~"}

    g = dict(goal)
    pct = round(g["saved_amount"] / g["target_amount"] * 100, 1) if g["target_amount"] > 0 else 0
    remaining = g["target_amount"] - g["saved_amount"]

    if g["completed"]:
        progress_text = f"「{g['name']}」已达成！攒了 ¥{g['saved_amount']:.0f} 🎉"
    else:
        progress_text = f"「{g['name']}」已攒 ¥{g['saved_amount']:.0f} / ¥{g['target_amount']:.0f}（{pct}%），还差 ¥{remaining:.0f}"

    return {"goal": g, "progress_text": progress_text}


def delete_goal() -> bool:
    """放弃当前目标（软删除：标记完成但清空金额）"""
    conn = get_db()
    goal = conn.execute(
        "SELECT * FROM goals WHERE completed = 0 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if goal:
        conn.execute("DELETE FROM goals WHERE id = ?", (goal["id"],))
        conn.commit()
    conn.close()
    return True


def add_savings(amount: float = 2.0) -> dict | None:
    """每次记账后自动攒一点，返回更新后的目标"""
    conn = get_db()
    goal = conn.execute(
        "SELECT * FROM goals WHERE completed = 0 ORDER BY created_at DESC LIMIT 1"
    ).fetchone()
    if not goal:
        conn.close()
        return None

    new_saved = min(goal["target_amount"], goal["saved_amount"] + amount)
    completed = 1 if new_saved >= goal["target_amount"] else 0
    conn.execute(
        "UPDATE goals SET saved_amount = ?, completed = ? WHERE id = ?",
        (new_saved, completed, goal["id"]),
    )
    conn.commit()
    g = dict(conn.execute("SELECT * FROM goals WHERE id = ?", (goal["id"],)).fetchone())
    conn.close()
    return {"goal": g}
