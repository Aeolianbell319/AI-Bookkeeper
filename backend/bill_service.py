"""
小满 — 记账业务逻辑（CRUD + 查询）
"""
from datetime import date, timedelta

from database import get_db


def _row_to_dict(row) -> dict:
    return dict(row) if row else None


def _today() -> str:
    return date.today().isoformat()


def _week_start() -> str:
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def _month_start() -> str:
    return date.today().replace(day=1).isoformat()


# ==================== CRUD ====================

def add_bill(amount: float, category: str, item: str = "", bill_date: str = None, bill_type: str = "expense") -> dict:
    """新增账单，返回账单 dict + 今日总额"""
    conn = get_db()
    d = bill_date or _today()
    cur = conn.execute(
        "INSERT INTO bills (type, amount, category, item, date) VALUES (?, ?, ?, ?, ?)",
        (bill_type, amount, category, item, d),
    )
    conn.commit()
    bill = dict(conn.execute("SELECT * FROM bills WHERE id = ?", (cur.lastrowid,)).fetchone())
    today_total = _calc_total(conn, _today())
    conn.close()
    return {"bill": bill, "today_total": today_total}


def update_bill(bill_id: int, amount: float, category: str, item: str = "", bill_date: str = None) -> dict:
    """编辑账单"""
    conn = get_db()
    d = bill_date or _today()
    conn.execute(
        "UPDATE bills SET amount=?, category=?, item=?, date=? WHERE id=?",
        (amount, category, item, d, bill_id),
    )
    conn.commit()
    bill = dict(conn.execute("SELECT * FROM bills WHERE id = ?", (bill_id,)).fetchone())
    conn.close()
    return {"bill": bill}


def delete_bill(bill_id: int) -> bool:
    """删除账单"""
    conn = get_db()
    conn.execute("DELETE FROM bills WHERE id = ?", (bill_id,))
    conn.commit()
    conn.close()
    return True


# ==================== 查询 ====================

def _calc_total(conn, target_date: str) -> float:
    rows = conn.execute(
        "SELECT type, amount FROM bills WHERE date = ?", (target_date,)
    ).fetchall()
    return sum(r["amount"] if r["type"] == "expense" else -r["amount"] for r in rows)


def get_today() -> dict:
    """今日汇总：总额 + 明细列表"""
    conn = get_db()
    t = _today()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM bills WHERE date = ? ORDER BY created_at DESC", (t,)
    ).fetchall()]
    total = sum(r["amount"] if r["type"] == "expense" else -r["amount"] for r in rows)
    conn.close()
    return {"total": total, "breakdown": rows}


def get_week() -> dict:
    """本周汇总：支出总额 + 一级分类汇总 + 每日趋势"""
    conn = get_db()
    ws = _week_start()
    t = _today()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM bills WHERE date >= ? AND date <= ? ORDER BY date", (ws, t)
    ).fetchall()]

    expense_total = 0
    income_total = 0
    by_category = {}
    daily_totals = {}
    for r in rows:
        amt = r["amount"]
        if r["type"] == "expense":
            expense_total += amt
            cat = r["category"]
            by_category[cat] = by_category.get(cat, 0) + amt
            daily_totals[r["date"]] = daily_totals.get(r["date"], 0) + amt
        else:
            income_total += amt

    conn.close()
    return {
        "total": expense_total,
        "income_total": income_total,
        "by_category": by_category,
        "daily_totals": daily_totals,
        "count": len(rows),
    }


def get_month(budget: float = 0) -> dict:
    """本月总览：总额 + 预算进度 + 剩余"""
    conn = get_db()
    ms = _month_start()
    t = _today()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM bills WHERE date >= ? AND date <= ?", (ms, t)
    ).fetchall()]
    total = sum(r["amount"] if r["type"] == "expense" else -r["amount"] for r in rows)

    pct = round(total / budget * 100, 1) if budget > 0 else 0
    remaining = budget - total if budget > 0 else 0
    today = date.today()
    days_passed = today.day
    days_total = 30
    avg_daily = round(total / max(1, days_passed), 1)

    conn.close()
    return {
        "total": total,
        "budget": budget,
        "pct": pct,
        "remaining": remaining,
        "avg_daily": avg_daily,
        "count": len(rows),
    }


def get_date(target_date: str) -> dict:
    """某日明细"""
    conn = get_db()
    rows = [dict(r) for r in conn.execute(
        "SELECT * FROM bills WHERE date = ? ORDER BY created_at DESC", (target_date,)
    ).fetchall()]
    total = sum(r["amount"] if r["type"] == "expense" else -r["amount"] for r in rows)
    conn.close()
    return {"bills": rows, "total": total}


def get_month_daily_spent(year: int, month: int) -> dict:
    """获取某月每天的收支明细，用于日历展示"""
    conn = get_db()
    prefix = f"{year}-{month:02d}"
    rows = conn.execute(
        "SELECT date, type, amount FROM bills WHERE date LIKE ?", (prefix + "%",)
    ).fetchall()
    daily = {}
    for r in rows:
        d = r["date"]
        if d not in daily:
            daily[d] = {"income": 0.0, "expense": 0.0}
        if r["type"] == "income":
            daily[d]["income"] += r["amount"]
        else:
            daily[d]["expense"] += r["amount"]
    conn.close()
    return daily
