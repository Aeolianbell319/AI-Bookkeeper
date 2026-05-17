"""
小满 — Pydantic 请求/响应模型
"""
from pydantic import BaseModel, Field


# ==================== Chat ====================

class ChatRequest(BaseModel):
    messages: list[dict] = Field(default_factory=list)
    context: dict | None = None


class ChatResponse(BaseModel):
    reply: str
    bill_detected: dict | None = None
    goal_detected: dict | None = None
    goal_progress: dict | None = None


# ==================== Bill ====================

class BillBase(BaseModel):
    amount: float = Field(..., gt=0)
    category: str = "其他"
    item: str = ""
    date: str = ""  # YYYY-MM-DD，后端自动用今天兜底


class BillConfirmRequest(BillBase):
    pass


class BillManualRequest(BillBase):
    type: str = "expense"


class BillUpdateRequest(BillBase):
    pass


class BillResponse(BaseModel):
    bill: dict
    today_total: float | None = None


class DeleteResponse(BaseModel):
    ok: bool = True


# ==================== Report ====================

class TodayReport(BaseModel):
    total: float
    breakdown: list[dict]


class WeekReport(BaseModel):
    total: float
    by_category: dict
    daily_totals: dict
    count: int


class MonthReport(BaseModel):
    total: float
    budget: float
    pct: float
    remaining: float
    avg_daily: float
    count: int


class DateReport(BaseModel):
    bills: list[dict]
    total: float


# ==================== Goal ====================

class GoalCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)
    target_amount: float = Field(..., gt=0)


class GoalResponse(BaseModel):
    goal: dict | None = None
    goals: list[dict] | None = None
    message: str | None = None
    progress_text: str | None = None
    completed_count: int | None = None


# ==================== Mascot ====================

class MascotRequest(BaseModel):
    user_profile: dict = Field(default_factory=dict)
    current_data: dict = Field(default_factory=dict)
    mascot_history: list[dict] = Field(default_factory=list)
    current_page: str = "home"
    trigger: str = "tab_switch"


class MascotResponse(BaseModel):
    text: str = ""
