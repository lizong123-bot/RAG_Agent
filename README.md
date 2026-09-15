# 私有知识库 RAG 智能问答 Agent

基于 **LangChain 1.x + Qdrant + FastAPI + Gradio** 的私有知识库问答系统。

上传 PDF / Markdown，Agent 自主判断是否需要检索，回答附带原文出处（文件名 + 页码）。

## 功能

- 上传 PDF / Markdown → 解析 → 切分 → 向量化 → 存入 Qdrant
- Agent 自主判断是否检索知识库（闲聊不查、文档问题才查）
- 回答附带原文引用（文件名 + 页码）
- token 统计
- FastAPI 提供 REST 接口，Gradio 提供演示前端

## 环境要求

- Python 3.10+
- LangChain 1.x（使用 `create_agent`）
- 一个 Qdrant 实例（Cloud 或本地）

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 LLM / Embedding / Qdrant 的密钥（见 .env.example 注释）

# 3. 初始化 Qdrant（建 collection 和 metadata.source 索引）
python -m scripts.init_qdrant

# 4. 启动后端
uvicorn app.main:app --reload --port 8000

# 5. 另开一个终端，启动前端
python ui/gradio_app.py
```

浏览器打开 `http://localhost:7860`，上传文档后提问。

> **注意**：必须先启动后端（8000），再启动前端（7860），否则前端会报连接错误。

## 配置

所有环境变量及说明见 [`.env.example`](.env.example)，复制后填入自己的密钥即可。

关键变量一览：

| 变量 | 说明 |
|------|------|
| `LLM_API_KEY` / `LLM_MODEL_ID` / `LLM_BASE_URL` | LLM（Chat）连接信息 |
| `EMBEDDING_API_KEY` / `EMBEDDING_MODEL_ID` / `EMBEDDING_BASE_URL` | Embedding 连接信息 |
| `QDRANT_URL` / `QDRANT_API_KEY` / `QDRANT_COLLECTION_NAME` | Qdrant 连接信息 |

## 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| `GET` | `/` | 健康检查 |
| `POST` | `/api/upload` | 上传文档（multipart/form-data） |
| `POST` | `/api/ask` | 提问，返回 `answer` / `sources` / `tokens_used` |

启动后端后，交互式 API 文档在 `http://localhost:8000/docs`。

## 项目结构

```
rag-agent/
├── app/
│   ├── main.py                  FastAPI 入口
│   ├── config.py                配置读取
│   ├── agent/                   Agent 与工具
│   ├── rag/                     加载、切分、向量库、检索、collection
│   ├── utils/                   token 统计等
│   └── api/                     FastAPI 路由
├── ui/
│   └── gradio_app.py            Gradio 前端
├── scripts/
│   └── init_qdrant.py           初始化 Qdrant
├── tests/                       测试
├── data/                        上传的文档（不进 Git）
├── .env.example                 环境变量模板
└── requirements.txt
```

## 注意事项

- **不支持扫描版 PDF**：本项目用 `PyPDFLoader`，只能提取内嵌文字层。图片型 PDF（扫描件）提取不到正文，需先 OCR 或换纯文本版。
- **Embedding 每批 ≤10 条**：DashScope 的 Embedding 接口单次最多 10 条，代码里已设 `batch_size=10`。
- **多文档混在同一 collection**：检索时可能跨文档召回，需要时按 `metadata.source` 过滤。
- **`tokens_used` 是估算值**：用 `tiktoken` 估算，对中文偏高，仅用于展示。

## 常见问题

| 现象 | 原因 / 解决 |
|------|------------|
| `Index required but not found for "metadata.source"` | 没建索引，跑 `python -m scripts.init_qdrant` |
| `batch size is invalid` | Embedding 每批 ≤10 条，已设 `batch_size=10` |
| `Ignoring wrong pointing object` | PDF 交叉引用表损坏，可忽略，不影响解析 |
| 上传成功但检索不到内容 | 文档是扫描版，或索引没建 |

## License
本项目采用 [MIT License](LICENSE)。
MIT