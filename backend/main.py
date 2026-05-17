"""
小满 AI理财搭子 — FastAPI 后端入口（多用户）
"""
from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import init_db
from models import (
    ChatRequest, ChatResponse,
    BillBase, BillConfirmRequest, BillManualRequest, BillUpdateRequest, BillResponse, DeleteResponse,
    TodayReport, WeekReport, MonthReport, DateReport,
    GoalCreateRequest, GoalResponse,
    MascotRequest, MascotResponse,
)
from ai_service import chat as ai_chat, extract_bill, extract_goal, warmup_mascot
from bill_service import (
    add_bill, update_bill, delete_bill,
    get_today, get_week, get_month, get_date as get_date_report,
    get_month_daily_spent,
)
from goal_service import create_goal, get_goals, delete_goal, add_savings, get_completed_count, dismiss_goal
from message_service import save_messages, get_messages, clear_messages
from auth_service import register, login, verify_token

# ========== 应用初始化 ==========
app = FastAPI(title="小满 AI理财搭子", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 静态文件 ==========
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
LIVE2D_DIR = BASE_DIR / "live2d"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
if LIVE2D_DIR.exists():
    app.mount("/live2d", StaticFiles(directory=str(LIVE2D_DIR)), name="live2d")


# ========== 启动 ==========
@app.on_event("startup")
async def startup():
    init_db()


# ========== 认证依赖 ==========

def get_current_user(authorization: str = Header(None)) -> int:
    """从 Authorization header 解析 JWT，返回 user_id"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录")
    token = authorization[len("Bearer "):]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return payload["user_id"]


# ========== 无需认证 ==========

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}


@app.get("/")
async def root():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "小满 API 服务已启动"}


# ========== 认证路由 ==========

@app.post("/api/auth/register")
async def auth_register(req: dict):
    return register(req["username"], req["password"])


@app.post("/api/auth/login")
async def auth_login(req: dict):
    return login(req["username"], req["password"])


@app.get("/api/auth/me")
async def auth_me(user_id: int = Depends(get_current_user)):
    return {"id": user_id}


# ========== 对话 ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, user_id: int = Depends(get_current_user)):
    last_user_msg = ""
    for m in reversed(req.messages):
        if m.get("role") == "user":
            last_user_msg = m["content"]
            break

    bill_detected = await extract_bill(last_user_msg) if last_user_msg else None
    goal_detected = await extract_goal(last_user_msg) if last_user_msg else None

    # 如果同时检测到消费和攒钱目标，优先攒钱目标
    if goal_detected:
        bill_detected = None

    reply = await ai_chat(req.messages, req.context)

    goal_data = get_goals(user_id)
    goal_progress = goal_data if goal_data.get("goals") else None

    return ChatResponse(
        reply=reply,
        bill_detected=bill_detected,
        goal_detected=goal_detected,
        goal_progress=goal_progress,
    )


# ========== 记账 ==========

@app.post("/api/bill/confirm", response_model=BillResponse)
async def bill_confirm(req: BillConfirmRequest, user_id: int = Depends(get_current_user)):
    return add_bill(user_id, req.amount, req.category, req.item, req.date or None)


@app.post("/api/bill/manual", response_model=BillResponse)
async def bill_manual(req: BillManualRequest, user_id: int = Depends(get_current_user)):
    result = add_bill(user_id, req.amount, req.category, req.item, req.date or None, req.type)
    add_savings(user_id)
    return result


@app.put("/api/bill/{bill_id}", response_model=BillResponse)
async def bill_update(bill_id: int, req: BillUpdateRequest, user_id: int = Depends(get_current_user)):
    return update_bill(user_id, bill_id, req.amount, req.category, req.item, req.date or None)


@app.delete("/api/bill/{bill_id}", response_model=DeleteResponse)
async def bill_delete(bill_id: int, user_id: int = Depends(get_current_user)):
    delete_bill(user_id, bill_id)
    return DeleteResponse(ok=True)


# ========== 报表 ==========

@app.get("/api/report/today", response_model=TodayReport)
async def report_today(user_id: int = Depends(get_current_user)):
    return get_today(user_id)


@app.get("/api/report/week", response_model=WeekReport)
async def report_week(user_id: int = Depends(get_current_user)):
    return get_week(user_id)


@app.get("/api/report/month", response_model=MonthReport)
async def report_month(budget: float = 0, user_id: int = Depends(get_current_user)):
    return get_month(user_id, budget)


@app.get("/api/report/date/{target_date}", response_model=DateReport)
async def report_date(target_date: str, user_id: int = Depends(get_current_user)):
    return get_date_report(user_id, target_date)


@app.get("/api/report/month-daily/{year}/{month}")
async def report_month_daily(year: int, month: int, user_id: int = Depends(get_current_user)):
    return get_month_daily_spent(user_id, year, month)


# ========== 攒钱目标 ==========

@app.post("/api/goal", response_model=GoalResponse)
async def goal_create(req: GoalCreateRequest, user_id: int = Depends(get_current_user)):
    return create_goal(user_id, req.name, req.target_amount)


@app.get("/api/goal", response_model=GoalResponse)
async def goal_query(user_id: int = Depends(get_current_user)):
    return get_goals(user_id)


@app.delete("/api/goal", response_model=DeleteResponse)
async def goal_delete(goal_id: int, user_id: int = Depends(get_current_user)):
    delete_goal(user_id, goal_id)
    return DeleteResponse(ok=True)


@app.delete("/api/goal/{goal_id}")
async def goal_dismiss(goal_id: int, user_id: int = Depends(get_current_user)):
    dismiss_goal(user_id, goal_id)
    return {"ok": True}


@app.get("/api/goal/history")
async def goal_history(user_id: int = Depends(get_current_user)):
    return {"completed_count": get_completed_count(user_id)}


@app.post("/api/goal/add-savings", response_model=GoalResponse)
async def goal_add_savings(amount: float = 0, goal_id: int | None = None, user_id: int = Depends(get_current_user)):
    if amount <= 0:
        return {"goal": None, "message": "金额必须大于0"}
    result = add_savings(user_id, amount, goal_id)
    if result is None:
        return {"goal": None, "message": "还没有攒钱目标，先去设一个吧~"}
    return result


# ========== 消息持久化 ==========

@app.get("/api/messages")
async def messages_get(limit: int = 100, user_id: int = Depends(get_current_user)):
    return {"messages": get_messages(user_id, limit)}


@app.post("/api/messages")
async def messages_save(messages: list[dict], user_id: int = Depends(get_current_user)):
    save_messages(user_id, messages)
    return {"ok": True}


@app.delete("/api/messages")
async def messages_clear(user_id: int = Depends(get_current_user)):
    clear_messages(user_id)
    return {"ok": True}


# ========== 碎碎念 ==========

@app.post("/api/mascot/warmup")
async def mascot_warmup(req: MascotRequest, user_id: int = Depends(get_current_user)):
    import json
    ctx_str = json.dumps({
        "user_profile": req.user_profile,
        "current_data": req.current_data,
        "mascot_history": [h.get("said", "") for h in req.mascot_history[-5:]],
    }, ensure_ascii=False, indent=2)
    results = await warmup_mascot(ctx_str)
    return results


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
