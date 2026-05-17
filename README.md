<p align="center">
  <h1 align="center">小满 · AI 理财搭子</h1>
  <p align="center">
    <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/FastAPI-0.100+-009688?style=flat&logo=fastapi&logoColor=white" alt="FastAPI">
    <img src="https://img.shields.io/badge/Vue-Vanilla_JS-f7df1e?style=flat&logo=javascript&logoColor=black" alt="Vanilla JS">
    <img src="https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white" alt="MySQL">
    <img src="https://img.shields.io/badge/AI-DeepSeek-4B6BFB?style=flat" alt="DeepSeek">
    <img src="https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/license-MIT-green?style=flat" alt="License">
  </p>
  <p align="center">
    <b>一个有人情味的 AI 记账助手</b><br>
    用自然对话帮你记账、分析消费、攒钱追梦<br>
    搭载 Live2D 看板娘，让理财不再枯燥
  </p>
</p>

---

## 为什么是小满？

> "小满"——物致于此小得盈满。不追求暴富，不贩卖焦虑，只希望你的每一笔消费都被温柔记录，每一个攒钱目标都能踏实达成。

记账 App 很多，但大多数冷冰冰的——填金额、选分类、看报表，像在做作业。**小满** 不一样：她是一个趴在屏幕边缘的少女，你只需要像跟朋友聊天一样说"午饭 15 块"，她就帮你记好。她会碎碎念，会调侃，会在你花超的时候递台阶，也会在你攒够钱的时候替你开心。

## 核心功能

### 自然语言记账
不是填表单，是聊天。输入"今天外卖 28""打车去公司 15""食堂晚饭 12"，AI 自动提取金额、分类、事项，生成一张确认卡片。你只需要点一下"确认"，记账就完成了。

### AI 对话理财
基于 DeepSeek 深度推理模型的智能聊天，像朋友一样陪你聊消费、聊省钱、聊生活。她不讲课、不说教、不列清单——只是在你需要的时候，给出刚刚好的建议。

### Live2D 看板娘 · 碎碎念系统
小满趴在屏幕右下角，会根据当前页面和你的消费数据主动搭话：

| 页面 | 她会跟你聊什么 |
|------|----------------|
| 首页 | 攒钱进度、预算提醒、周末问你去哪玩、工作日问你午饭吃了啥 |
| 统计 | 消费数据分析、省钱建议、消费习惯观察 |
| 账单 | 账单趣事、记账习惯提醒 |
| 我的 | 攒钱目标鼓励、个人设定建议 |

她的碎碎念不是随机生成的——每条都结合了当前时间、星期、你的消费数据，由 AI 实时生成。说完后留下一个呼吸光点，点击可以重温。

### 攒钱目标追踪
设定你想买的东西——耳机、旅行、游戏机——设定金额，然后每次手动记账自动攒 ¥2，也可以手动追加。进度条实时更新，达成后卡片变绿色庆祝，给你满满的仪式感。

### 四维度消费分析
- **今日**：当日支出明细，一目了然
- **本周**：分类汇总 + 每日趋势，发现花钱规律
- **本月**：预算进度、日均消费、剩余可花
- **日历**：每月每日收支明细，支持任意月份切换

### 多用户 · 数据独立
JWT 认证机制，同一份部署，不同账号数据完全隔离。每人独立记账、独立攒钱、独立聊天记录。

### Docker 一键部署
三容器编排——MySQL 8.0 + FastAPI 后端 + Nginx 反向代理——一个 `docker-compose up -d` 全部跑起来。

## 设计理念

- **手机优先**：420px 宽度的单页应用，模拟手机形态，专为移动端设计
- **AI 原生**：不是"先做功能再接入 AI"，整个产品围绕 AI 对话构建
- **零压力记账**：不强制记录，不用分类标签筛选，不说教
- **人情味交互**：确认卡片、按钮呼吸动画、碎碎念气泡、庆祝特效……细节让体验有温度

## 页面结构

```
┌──────────────┐
│   Top Bar    │ 小满头像 + 状态
├──────────────┤
│              │
│  4 个 Tab    │  首页 / 统计 / 账单 / 我的
│  (页面区)    │  + 对话页（从看板娘进入）
│              │
├──────────────┤
│   Tab Bar    │ 底部导航
├──────────────┤
│   Live2D     │ 看板娘悬浮在右下角
└──────────────┘
```

## 快速开始

### 准备工作

你需要一个 **DeepSeek API Key**（[申请地址](https://platform.deepseek.com)），以及 **Docker** 或本地 **MySQL**。

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/Aeolianbell319/AI-Bookkeeper.git
cd AI-Bookkeeper

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key 和数据库密码

# 3. 一键启动
docker-compose up -d

# 4. 浏览器访问
# http://localhost
```

### 方式二：本地开发

```bash
# 1. 配置
cp .env.example .env
# 编辑 .env 填入配置项

# 2. 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 3. 确保 MySQL 已运行，然后启动
python main.py
# 访问 http://127.0.0.1:8000

# Windows 用户可以直接双击 start.bat（会自动读取 .env）
```

## 技术栈

| 层级 | 技术选型 | 说明 |
|------|----------|------|
| **前端** | Vanilla JS + CSS3 | 零依赖框架，420px 移动端单页应用 |
| **看板娘** | OML2D + Live2D Cubism 4 | 搭载 Hiyori 模型，10 组动作 |
| **后端** | FastAPI 0.100+ | 异步 Python Web 框架 |
| **数据校验** | Pydantic v2 | 请求/响应模型定义与校验 |
| **AI 引擎** | DeepSeek API | deepseek-chat（轻量 NLU）+ deepseek-v4-pro（深度对话） |
| **数据库** | MySQL 8.0 | pymysql 驱动，utf8mb4 字符集 |
| **认证** | JWT + bcrypt | 24 小时 Token，密码哈希存储 |
| **部署** | Docker + Nginx | 三容器编排，反向代理 |

## AI 架构

```
用户输入 "午饭15块"
    │
    ▼
┌──────────────────────┐
│  deepseek-chat       │ ← NLU 提取：金额/分类/事项（轻量快速）
│  (extract_bill)      │
└──────┬───────────────┘
       │ {"type":"expense","amount":15,"category":"餐饮","item":"午饭"}
       ▼
  前端确认卡片（✅确认 / ✎编辑 / ×取消）
       │
       ▼ 确认
┌──────────────────────┐
│  写入 MySQL           │
│  自动攒钱 +¥2         │
│  重新预热碎碎念缓存    │
└──────────────────────┘
```

**碎碎念预热机制**：初始化或每次记账后，后端并行调用 4 次 `deepseek-chat`，为四个页面各预生成一条碎碎念，前端缓存后秒级弹出，无感知延迟。

## 项目结构

```
xiaoman/
├── frontend/
│   └── index.html              # 单页应用（~3000 行），包含全部 UI 逻辑
├── backend/
│   ├── main.py                 # FastAPI 入口，路由注册
│   ├── ai_service.py           # DeepSeek API 调用封装
│   ├── auth_service.py         # JWT 签发/验证 + bcrypt 密码哈希
│   ├── bill_service.py         # 账单 CRUD + 今日/本周/本月/日历统计
│   ├── goal_service.py         # 攒钱目标：创建/攒钱/达成/清理
│   ├── message_service.py      # 聊天记录持久化（按用户隔离）
│   ├── database.py             # MySQL 连接池 + 建库建表
│   ├── models.py               # Pydantic 请求/响应模型
│   ├── persona.py              # AI 人设 Prompt：性格、规则、语气
│   └── requirements.txt        # Python 依赖
├── live2d/                     # Live2D Cubism 模型文件（Hiyori）
│   ├── hiyori_pro_t11.model3.json
│   ├── hiyori_pro_t11.moc3
│   ├── hiyori_pro_t11.physics3.json
│   ├── hiyori_pro_t11.pose3.json
│   ├── hiyori_pro_t11.cdi3.json
│   ├── hiyori_pro_t11.2048/    # 纹理贴图
│   └── motion/                 # 10 组动作文件
├── nginx.conf                  # Nginx 反向代理配置
├── Dockerfile                  # Python 后端镜像
├── docker-compose.yml          # MySQL + Backend + Nginx 编排
├── .env.example                # 环境变量模板
├── start.bat / stop.bat        # Windows 本地启停脚本
└── README.md
```

## API 参考

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册（username + password） |
| POST | `/api/auth/login` | 登录，返回 JWT Token |
| GET | `/api/auth/me` | 获取当前用户信息 |

### 对话
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | AI 对话，支持 AbortController 中止 |

请求体示例：

```json
{
  "messages": [
    {"role": "user", "content": "午饭花了15块"}
  ],
  "context": {"time": "中午", "weekday": "周三"}
}
```

响应会同时返回 AI 回复、检测到的账单信息、攒钱目标信息。

### 记账
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/bill/confirm` | 确认 AI 提取的账单 |
| POST | `/api/bill/manual` | 手动记账（记账后自动攒 ¥2） |
| PUT | `/api/bill/{id}` | 修改账单 |
| DELETE | `/api/bill/{id}` | 删除账单 |

### 报表
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/report/today` | 今日支出总额 + 明细 |
| GET | `/api/report/week` | 本周支出总额 + 分类汇总 + 每日趋势 |
| GET | `/api/report/month?budget=2000` | 本月支出 + 预算进度 + 日均 |
| GET | `/api/report/date/{date}` | 指定日期账单明细（YYYY-MM-DD） |
| GET | `/api/report/month-daily/{year}/{month}` | 月每日收支（用于日历） |

### 攒钱目标
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/goal` | 创建目标（name + target_amount） |
| GET | `/api/goal` | 查询当前目标 + 已达成历史计数 |
| POST | `/api/goal/add-savings?amount=50` | 手动攒一笔 |
| DELETE | `/api/goal` | 放弃未完成目标 |
| DELETE | `/api/goal/{id}` | 消除已完成目标 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/mascot/warmup` | 并行预热四个页面的碎碎念 |
| GET | `/api/messages?limit=100` | 获取聊天历史 |
| POST | `/api/messages` | 保存聊天记录 |
| DELETE | `/api/messages` | 清空聊天记录 |
| GET | `/api/health` | 健康检查 |

## 配置项

所有配置通过环境变量注入：

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 无（必填） |
| `MYSQL_HOST` | MySQL 地址 | `127.0.0.1` |
| `MYSQL_PORT` | MySQL 端口 | `3306` |
| `MYSQL_USER` | MySQL 用户名 | `root` |
| `MYSQL_PASSWORD` | MySQL 密码 | 无 |
| `MYSQL_DATABASE` | 数据库名 | `xiaoman` |
| `JWT_SECRET` | JWT 签名密钥 | 内置占位值（生产环境务必修改） |

直接开发时复制 `.env.example` 为 `.env` 修改即可；Docker 部署时 `docker-compose.yml` 会自动读取 `.env` 并注入容器。

## 开发计划

- [ ] WebSocket 流式对话（替代当前 HTTP 轮询）
- [ ] 消费预算告警通知
- [ ] 语音输入记账
- [ ] 多人共享账本（室友 AA）
- [ ] PWA 离线支持
- [ ] 数据导出 CSV/Excel

## License

MIT © Aeolianbell319
