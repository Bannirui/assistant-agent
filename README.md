# 旅游客服 AI Copilot

AI 驱动的旅游企业客服助手，以工单号为唯一输入，自动聚合多系统信息，生成回复建议和操作建议。

## 架构概览

```
Ticket Input
     │
     ▼
┌──────────────────────────────┐
│     Copilot Agent (ReAct)    │
│                              │
│  ┌────────┐┌──────────┐┌────┐│
│  │  SOP   ││Calculate ││RAG ││
│  │ Engine ││ Engine   ││ KB ││
│  └────────┘└──────────┘└────┘│
└──────────────────────────────┘
     │
     ▼
┌────────────────────────────┐
│      Vue 3 Workstation     │
│  Left: Chat | Right: Panel │
└────────────────────────────┘
```

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端框架 | FastAPI |
| LLM | DeepSeek |
| Embedding | 通义千问 text-embedding-v3 |
| Agent | 原生 Function Calling + LangChain Tools + 状态机 |
| 向量数据库 | Qdrant (本地模式) |
| 前端 | Vue 3 + Element Plus + Pinia + Vite |
| 容器化 | Docker Compose |

## 快速开始

### 方式一: 本地开发

```bash
# 1. 配置环境
cp .env.example .env
# 编辑 .env 填入 API Key

# 2. 后端安装
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# 3. 前端安装
cd frontend
npm install
cd ..

# 4. 启动后端 (终端1)
source .venv/bin/activate
uvicorn src.main:app --reload --port 8000

# 5. 启动前端 (终端2)
cd frontend
npm run dev

# 6. 初始化知识库
curl -X POST http://localhost:8000/admin/knowledge/ingest

# 7. 访问 http://localhost:3000
```

### 方式二: Docker Compose

```bash
cp .env.example .env
# 编辑 .env 填入 API Key
docker compose up

# 初始化知识库
curl -X POST http://localhost:8000/admin/knowledge/ingest

# 访问 http://localhost:3000
```

### 运行测试

```bash
source .venv/bin/activate && python -m pytest tests/ -v
```

## 项目结构

```
assistant-agent/
├── src/
│   ├── agent/          # Agent ReAct 循环
│   ├── api/            # API 路由 (预留)
│   ├── calculator/     # 退改计算引擎 (状态机)
│   ├── config.py       # 配置加载
│   ├── llm/            # LLM/Embedding Provider 抽象
│   ├── main.py         # FastAPI 入口
│   ├── mocks/          # Mock 外部系统
│   ├── rag/            # RAG 知识库
│   ├── router/         # 订单路由器
│   └── sop/            # SOP 引擎
├── data/
│   ├── knowledge/      # 知识库文档
│   └── sop/            # SOP YAML 文件
├── frontend/           # Vue 3 前端
├── tests/              # 测试
└── openspec/           # 设计文档
```

## 工单类型

| 品类 | 示例工单 |
|------|---------|
| 机票 | TK-20240728-001 (退差价), TK-20240728-004 (退票) |
| 酒店 | TK-20240728-002 (取消预订), TK-20240728-007 (房间问题) |
| 打车 | TK-20240728-003 (司机迟到), TK-20240728-006 (司机未到) |
| 火车 | TK-20240728-005 (改签), TK-20240728-008 (退票) |
