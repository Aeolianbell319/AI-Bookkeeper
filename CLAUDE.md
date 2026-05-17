# 小满 · AI理财搭子

## 技术栈
- 前端：Vanilla JS + OML2D (Live2D)
- 后端：FastAPI + MySQL (pymysql) + DeepSeek API
- 设计：420px 手机端单页应用

## 目录结构
```
xiaoman/
├── frontend/index.html    # 单页前端
├── backend/
│   ├── main.py            # FastAPI 入口
│   ├── ai_service.py      # DeepSeek API 封装
│   ├── bill_service.py    # 账单 CRUD + 统计
│   ├── goal_service.py    # 攒钱目标逻辑
│   ├── database.py        # SQLite 初始化
│   ├── models.py          # Pydantic 模型
│   └── persona.py         # Prompt 模板
├── live2d/                # Live2D 模型文件
└── data/                  # SQLite 数据库（gitignore）
```

## 启动方式
```bash
cd backend
pip install -r requirements.txt

# 数据库连接（MySQL，默认连本地）
set MYSQL_HOST=你的腾讯云IP       # Windows
set MYSQL_USER=你的数据库用户名
set MYSQL_PASSWORD=你的密码
set MYSQL_DATABASE=xiaoman
set DEEPSEEK_API_KEY=你的key

python main.py
```
前端直接打开 `frontend/index.html`，或通过后端静态文件服务访问。

## 碎碎念系统

### 架构：预热缓存 + 秒弹
```
初始化 / 记账后 → warmupMascotCache()
  ├─ 拉报表（今日/本周/目标）
  ├─ POST /api/mascot/warmup → 后端并行 4 次调用 DeepSeek（deepseek-chat）
  ├─ 返回 {"home":"...","stats":"...","bills":"...","me":"..."}
  └─ 写入 mascotCache

切 Tab → updateMascot(page)
  ├─ 对话页？→ 跳过
  ├─ 全局冷却 10s？→ 跳过
  ├─ 缓存命中 → 秒弹
  ├─ 缓存未命中 → 等预热最多 4s → 拿到就弹
  └─ 拿不到 → 不弹（无兜底，纯 AI 驱动）
```

### 预热时机
- 页面初始化（`init()`，延迟 2.5s 等数据就绪）
- 每次 CRUD 后（`refreshAll()` → `warmupMascotCache()`）
- 缓存剩余 ≤2 条时后台补充

### Prompt 策略
- 模型：`deepseek-chat`（轻量快速）
- 空返回自动重试（换 temperature 1.0→1.3）
- 每页指定话题方向：

| 页面 | 话题方向 |
|------|---------|
| 首页 | 攒钱进度、预算提醒、引导记账（周末问吃了什么/去哪玩，工作日问午饭，晚上问今天过得怎样） |
| 统计 | 消费数据分析、省钱建议、消费习惯 |
| 账单 | 账单趣事、记账习惯、提醒漏记 |
| 我的 | 攒钱目标鼓励、个人设定建议 |

- 上下文注入：时间（早/中/晚）+ 星期 + 工作日/周末
- 引导策略：根据时间场景自然引导用户去对话页记账，不硬广

### 气泡动画流程
```
showBubble(msg)
  ├─ 🟡 黄点隐藏
  ├─ 气泡弹出（opacity 0→1, 0.5s 淡入）
  ├─ 停留 4 秒
  ├─ 添加 .fade-out → 0.5s 淡出（上飘 4px）
  ├─ 动画结束后隐藏气泡
  └─ 🟡 黄点出现（呼吸脉冲动画，right:55px bottom:290px）
        │ 点击 → showLastBubble() 重新弹出
        │ 新消息 → 自动消失
        │ 点击 × → dismissBubble()
```

### 气泡定位
- 气泡：`right: 140px; bottom: 255px`，箭头指向右
- 黄点：`right: 55px; bottom: 290px`
- z-index：气泡 21 > tabbar 20 > Live2D 1

## 记账流程
1. 用户在对话页输入自然语言（如"午饭15"）
2. 后端调用 DeepSeek 提取 金额+分类+事项
3. 小满回复确认卡片（✅确认 / ✎编辑 / ×取消）
4. 确认后写入 SQLite，更新首页/统计/账单 + 重新预热碎碎念

## 攒钱目标生命周期

### 创建
- 手动弹窗：首页「🎯 设攒钱目标」按钮 → 填名称+金额 → `POST /api/goal`
- 聊天自然语言：「想攒500买耳机」→ `/api/chat` 自动提取并创建
- 限制：同时只能一个未完成目标

### 攒钱
- 手动：首页/我的页输入金额 → `POST /api/goal/add-savings`
- 自动：每次手动记账 +¥2

### 达成
- `saved_amount >= target_amount` → `completed = 1`, 记录 `completed_at`
- 首页卡片变绿色庆祝态 🎉，显示「✅ 完成，开始新目标」
- 我的页同样显示庆祝态

### 清理
- **手动**：点击「✅ 完成，开始新目标」→ `DELETE /api/goal/{id}` 立即删除
- **自动**：后端启动时清理 `completed_at` 超过 24 小时的目标
- 历史计数：`GET /api/goal` 返回 `completed_count`，在我的页展示「🏆 已达成 X 个」

## API 接口
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/chat | 对话（支持 AbortController 中止） |
| POST | /api/bill/confirm | 确认记账 |
| POST | /api/bill/manual | 手动记账 |
| PUT | /api/bill/{id} | 修改账单 |
| DELETE | /api/bill/{id} | 删除账单 |
| GET | /api/report/today | 今日支出汇总 |
| GET | /api/report/week | 本周支出汇总 |
| GET | /api/report/month | 本月支出总览 |
| GET | /api/report/date/{date} | 指定日账单明细 |
| GET | /api/report/month-daily/{y}/{m} | 月每日收支 |
| POST | /api/goal | 创建攒钱目标 |
| GET | /api/goal | 查询攒钱目标（含历史计数） |
| DELETE | /api/goal | 放弃未完成目标 |
| DELETE | /api/goal/{id} | 消除已完成目标 |
| POST | /api/goal/add-savings | 手动攒一笔 |
| GET | /api/goal/history | 已完成目标数 |
| POST | /api/mascot/warmup | 预热四个页面的碎碎念 |

## 数据过滤规则
所有统计/汇总接口只计算 **支出**（type='expense'），收入不参与统计。

## Live2D 显隐规则
- **对话页**：小满隐藏（`visibility: hidden`），避免遮挡聊天内容
- **其他页面**：小满显示
- 点击小满跳转对话页时自动隐藏

## 对话中止机制
- 发送消息后按钮变为 `■` 暂停键（红色），输入框禁用
- 使用 `AbortController` 控制请求，点击暂停中止 fetch
- 主动暂停显示"已停止生成"，网络错误不影响暂停体验
- 快捷按钮在思考期间不可点击

## 按钮风格统一
所有主按钮统一风格：`border-radius: 0.8rem`、`border-color: #E2CEB8`、渐变背景、`box-shadow` 阴影、`scale(0.97)` 按下反馈。Primary 按钮使用橙色渐变 `#F0A882→#E8886A`。

## 首页卡片导航
- 今日消费 → 跳转**账单页**
- 本周汇总 → 跳转**统计页**
- 攒钱目标 → 跳转**我的页**
