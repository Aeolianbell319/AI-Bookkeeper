# 小满 — AI 理财搭子

一个面向大学生的智能记账助手，搭载 Live2D 看板娘，用自然语言对话帮你轻松记账、分析消费、攒钱实现目标。

## 功能特性

- **自然语言记账** — 输入"午饭15"即可自动识别金额、分类，一键确认
- **AI 对话** — 基于 DeepSeek 的智能聊天，像朋友一样聊消费和理财
- **Live2D 看板娘** — 趴在屏幕边缘的小满，会主动碎碎念、引导记账
- **消费分析** — 今日/本周/本月报表，分类汇总，日均分析
- **攒钱目标** — 设定想买的东西，跟踪进度，达成庆祝
- **多用户支持** — JWT 认证，每人独立数据
- **Docker 部署** — 一键启动 MySQL + 后端 + Nginx

## 技术栈

| 层 | 技术 |
|---|------|
| 前端 | Vanilla JS + OML2D (Live2D Cubism 4) |
| 后端 | FastAPI + Pydantic |
| AI | DeepSeek API (deepseek-chat / deepseek-v4-pro) |
| 数据库 | MySQL 8.0 |
| 部署 | Docker Compose + Nginx |

## 快速开始

### 方式一：Docker（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 DeepSeek API Key 和数据库密码

# 2. 启动
docker-compose up -d

# 3. 访问
# 打开浏览器 http://localhost
```

### 方式二：本地开发

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填入配置（Windows 也可直接改 start.bat）

# 2. 安装依赖
cd backend
pip install -r requirements.txt

# 3. 确保 MySQL 已运行，然后启动
python main.py
# Windows 用户可直接双击 start.bat
```

## 项目结构

```
xiaoman/
├── frontend/
│   └── index.html          # 单页应用（420px 手机端）
├── backend/
│   ├── main.py             # FastAPI 入口
│   ├── ai_service.py       # DeepSeek API 封装
│   ├── auth_service.py     # JWT 认证
│   ├── bill_service.py     # 账单 CRUD + 统计
│   ├── goal_service.py     # 攒钱目标逻辑
│   ├── message_service.py  # 聊天记录持久化
│   ├── database.py         # 数据库初始化
│   ├── models.py           # Pydantic 模型
│   └── persona.py          # AI 人设 Prompt
├── live2d/                 # Live2D 模型文件（Hiyori）
├── nginx.conf              # Nginx 反向代理配置
├── Dockerfile
├── docker-compose.yml
└── .env.example            # 环境变量模板
```

## API 接口

### 认证
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/auth/register` | 注册 |
| POST | `/api/auth/login` | 登录 |

### 对话 & 记账
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/chat` | AI 对话（支持流式中止） |
| POST | `/api/bill/confirm` | 确认记账 |
| POST | `/api/bill/manual` | 手动记账 |
| PUT | `/api/bill/{id}` | 修改账单 |
| DELETE | `/api/bill/{id}` | 删除账单 |

### 报表
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/report/today` | 今日支出 |
| GET | `/api/report/week` | 本周汇总 |
| GET | `/api/report/month` | 本月总览 |
| GET | `/api/report/date/{date}` | 指定日明细 |
| GET | `/api/report/month-daily/{y}/{m}` | 月每日收支 |

### 攒钱目标
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/goal` | 创建目标 |
| GET | `/api/goal` | 查询目标 |
| DELETE | `/api/goal` | 放弃目标 |
| POST | `/api/goal/add-savings` | 手动攒一笔 |

### 其他
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/mascot/warmup` | 预热看板娘碎碎念 |
| GET | `/api/messages` | 获取聊天记录 |
| POST | `/api/messages` | 保存聊天记录 |

## 配置项

| 环境变量 | 说明 | 必填 |
|----------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | 是 |
| `MYSQL_HOST` | MySQL 地址 | 是 |
| `MYSQL_USER` | MySQL 用户名 | 是 |
| `MYSQL_PASSWORD` | MySQL 密码 | 是 |
| `MYSQL_DATABASE` | 数据库名 | 是 |
| `JWT_SECRET` | JWT 签名密钥 | 是 |

## License

MIT
