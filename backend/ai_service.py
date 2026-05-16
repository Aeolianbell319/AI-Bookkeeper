"""
小满 — DeepSeek API 调用封装（兼容 OpenAI 格式）
"""
import json
import os
import httpx

from persona import CHAT_PROMPT, EXTRACT_PROMPT, MASCOT_PROMPT

DEEPSEEK_BASE = "https://api.deepseek.com"
DEEPSEEK_CHAT_URL = f"{DEEPSEEK_BASE}/v1/chat/completions"
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")

# V4 Flash：轻量快速 — 用于 NLU 提取、人偶碎碎念
# V4 Pro：深度推理 — 用于主对话
MODEL_FLASH = "deepseek-v4-flash"
MODEL_PRO = "deepseek-v4-pro"


async def _call_deepseek(messages: list[dict], model: str = MODEL_PRO, temperature: float = 0.8, max_tokens: int = 800) -> str:
    """底层调用 DeepSeek API，返回回复文本"""
    if not API_KEY:
        return "（未配置 DEEPSEEK_API_KEY 环境变量）"

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            DEEPSEEK_CHAT_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json=payload,
        )
        data = resp.json()

    if resp.status_code != 200:
        return f"（AI 调用失败: {data.get('error', {}).get('message', '未知错误')}）"

    return data["choices"][0]["message"]["content"]


async def chat(messages: list[dict], context: dict | None = None) -> str:
    """对话生成（Pro 模型）：拼接 system prompt + 上下文 + 历史消息"""
    system_content = CHAT_PROMPT

    if context:
        ctx_str = json.dumps(context, ensure_ascii=False, indent=2)
        system_content += f"\n\n## 当前用户上下文\n{ctx_str}"

    full_messages = [{"role": "system", "content": system_content}] + messages
    return await _call_deepseek(full_messages, model=MODEL_PRO)


async def extract_bill(user_text: str) -> dict | None:
    """从用户消息中提取消费信息（Flash 模型），返回 {amount, category, item} 或 None"""
    messages = [
        {"role": "system", "content": EXTRACT_PROMPT},
        {"role": "user", "content": user_text},
    ]
    raw = await _call_deepseek(messages, model=MODEL_FLASH, temperature=0.1, max_tokens=150)
    try:
        raw = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        result = json.loads(raw)
        if result.get("amount") and result["amount"] > 0:
            return {
                "amount": float(result["amount"]),
                "category": result.get("category", "其他"),
                "item": result.get("item", ""),
            }
    except (json.JSONDecodeError, ValueError):
        pass
    return None


async def mascot_chat(context_str: str) -> str:
    """人偶碎碎念（Flash 模型）：一句话，≤30字"""
    messages = [
        {"role": "system", "content": MASCOT_PROMPT},
        {"role": "user", "content": context_str},
    ]
    text = await _call_deepseek(messages, model=MODEL_FLASH, temperature=0.9, max_tokens=80)
    return text.strip()[:60]
