"""
小满 — 用户认证（JWT + bcrypt）
"""

import os
from datetime import datetime, timedelta

import jwt
import bcrypt

from database import get_db

JWT_SECRET = os.environ.get("JWT_SECRET", "xiaoman-secret-change-me")
JWT_EXPIRE_HOURS = 24


def _hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def register(username: str, password: str) -> dict:
    """注册新用户"""
    if len(username) < 2 or len(username) > 50:
        return {"ok": False, "message": "用户名需 2-50 个字符"}
    if len(password) < 4:
        return {"ok": False, "message": "密码至少 4 位"}

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = %s", (username,)
    ).fetchone()
    if existing:
        conn.close()
        return {"ok": False, "message": "用户名已被注册"}

    pwd_hash = _hash_password(password)
    cur = conn.execute(
        "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, pwd_hash),
    )
    conn.commit()
    user = conn.execute("SELECT id, username FROM users WHERE id = %s", (cur.lastrowid,)).fetchone()
    conn.close()

    token = _make_token(user["id"], user["username"])
    return {"ok": True, "token": token, "user": user}


def login(username: str, password: str) -> dict:
    """登录"""
    conn = get_db()
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = %s", (username,)
    ).fetchone()
    conn.close()

    if not user or not _verify_password(password, user["password_hash"]):
        return {"ok": False, "message": "用户名或密码错误"}

    token = _make_token(user["id"], user["username"])
    return {"ok": True, "token": token, "user": {"id": user["id"], "username": user["username"]}}


def _make_token(user_id: int, username: str) -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRE_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    """验证 token，返回 payload 或 None"""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
