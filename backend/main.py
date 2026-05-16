"""
小满 AI理财搭子 — FastAPI 后端入口
"""
from pathlib import Path

from fastapi import FastAPI
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
from ai_service import chat as ai_chat, extract_bill, mascot_chat
from bill_service import (
    add_bill, update_bill, delete_bill,
    get_today, get_week, get_month, get_date as get_date_report,
    get_month_daily_spent,
)
from goal_service import create_goal, get_goal, delete_goal, add_savings

# ========== 应用初始化 ==========
app = FastAPI(title="小满 AI理财搭子", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== 静态文件挂载 ==========
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"
LIVE2D_DIR = BASE_DIR / "live2d"

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

if LIVE2D_DIR.exists():
    app.mount("/live2d", StaticFiles(directory=str(LIVE2D_DIR)), name="live2d")


# ========== 启动事件 ==========

@app.on_event("startup")
async def startup():
    init_db()


# ========== 通用路由 ==========

@app.get("/api/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}


@app.get("/")
async def root():
    """返回前端页面"""
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return {"message": "小满 API 服务已启动，前端文件未找到"}


# ========== 核心对话 (含 NLU 记账) ==========

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """核心对话：NLU 提取消费 → AI 对话 → 查目标进度"""
    last_user_msg = ""
    for m in reversed(req.messages):
        if m.get("role") == "user":
            last_user_msg = m["content"]
            break

    # Step 1: NLU 提取消费
    bill_detected = await extract_bill(last_user_msg) if last_user_msg else None

    # Step 2: AI 对话
    reply = await ai_chat(req.messages, req.context)

    # Step 3: 查询攒钱进度
    goal_data = get_goal()
    goal_progress = goal_data if goal_data["goal"] else None

    return ChatResponse(
        reply=reply,
        bill_detected=bill_detected,
        goal_progress=goal_progress,
    )


# ========== 记账 CRUD ==========

@app.post("/api/bill/confirm", response_model=BillResponse)
async def bill_confirm(req: BillConfirmRequest):
    """确认 AI 检测到的账单"""
    return add_bill(req.amount, req.category, req.item, req.date or None)


@app.post("/api/bill/manual", response_model=BillResponse)
async def bill_manual(req: BillManualRequest):
    """手动记账"""
    result = add_bill(req.amount, req.category, req.item, req.date or None, req.type)
    # 自动攒一点
    add_savings()
    return result


@app.put("/api/bill/{bill_id}", response_model=BillResponse)
async def bill_update(bill_id: int, req: BillUpdateRequest):
    """编辑账单"""
    return update_bill(bill_id, req.amount, req.category, req.item, req.date or None)


@app.delete("/api/bill/{bill_id}", response_model=DeleteResponse)
async def bill_delete(bill_id: int):
    """删除账单"""
    delete_bill(bill_id)
    return DeleteResponse(ok=True)


# ========== 报表查询 ==========

@app.get("/api/report/today", response_model=TodayReport)
async def report_today():
    return get_today()


@app.get("/api/report/week", response_model=WeekReport)
async def report_week():
    return get_week()


@app.get("/api/report/month", response_model=MonthReport)
async def report_month(budget: float = 0):
    """本月总览，可从「我的」页传入用户设定的月预算"""
    return get_month(budget)


@app.get("/api/report/date/{target_date}", response_model=DateReport)
async def report_date(target_date: str):
    return get_date_report(target_date)


@app.get("/api/report/month-daily/{year}/{month}")
async def report_month_daily(year: int, month: int):
    """某月每日消费合计，用于日历展示"""
    return get_month_daily_spent(year, month)


# ========== 攒钱目标 ==========

@app.post("/api/goal", response_model=GoalResponse)
async def goal_create(req: GoalCreateRequest):
    """创建攒钱目标"""
    return create_goal(req.name, req.target_amount)


@app.get("/api/goal", response_model=GoalResponse)
async def goal_query():
    """查询当前目标与进度"""
    return get_goal()


@app.delete("/api/goal", response_model=DeleteResponse)
async def goal_delete():
    """放弃目标"""
    delete_goal()
    return DeleteResponse(ok=True)


# ========== 人偶碎碎念 ==========

@app.post("/api/mascot", response_model=MascotResponse)
async def mascot(req: MascotRequest):
    """人偶 AI 碎碎念"""
    import json
    ctx_str = json.dumps({
        "user_profile": req.user_profile,
        "current_data": req.current_data,
        "mascot_history": [h.get("said", "") for h in req.mascot_history[-5:]],
        "current_page": req.current_page,
        "trigger": req.trigger,
    }, ensure_ascii=False, indent=2)
    text = await mascot_chat(ctx_str)
    return MascotResponse(text=text)
