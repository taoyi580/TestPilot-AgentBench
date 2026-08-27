# TestPilot

仓库：[taoyi580/TestPilot-AgentBench](https://github.com/taoyi580/TestPilot-AgentBench)

研发文档与故障诊断助手：先检索资料，再按资料生成回答。资料不足时会明确说不知道。

主评测语料来自公开集 [RGB](https://github.com/chen700564/RGB)（AAAI 2024，CC BY-NC-SA 4.0，**仅非商业使用**）。

## 功能

- 网页提问，展示回答、工具轨迹和引用来源
- LangGraph 编排五个工具：文档检索、相似故障、历史运行、版本对比、回归保存
- 可切换 RGB 公开新闻问答，或本地研发笔记
- 无证据场景只提供无关文档，模型应拒绝作答
- 检索链路：切块 → BGE Embedding → Qdrant → 与 BM25 做 RRF 混合召回
- 检索、拒答、工具选择均由脚本实跑，结果在 `data/eval/`

## 本地运行

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000

把 `DEEPSEEK_API_KEY` 写入 `.env`。未配置时仍可使用「只看检索」。线上部署请把该变量配在平台环境变量中，不要写入代码。

首次启动会下载中文 Embedding 模型 `BAAI/bge-small-zh-v1.5`，并为 7000 余篇文档建向量库，需要几分钟。向量和 Qdrant 数据写在 `data/cache/`、`data/qdrant/`，不要提交到 Git。

## 评测（本仓库实跑）

公开集共 500 题（`zh_refine` 300 + `zh_int` 100 + `zh_fact` 100）。检索与拒答主评测用 `zh_refine`。

```bash
python eval_retrieval.py --mode all
python eval_reject.py
python eval_tools.py
```

| 项目 | 口径 | 结果 |
| --- | --- | --- |
| BM25 Hit@1 / Hit@5 / P95 | RGB `zh_refine` 300 题，7337 篇去重文档 | 67.0% / 94.7% / 40 ms |
| 向量检索 Hit@1 / Hit@5 / P95 | BGE-small-zh + Qdrant | 72.0% / 93.7% / 49 ms |
| 混合检索 Hit@1 / Hit@5 / P95 | BM25 与向量 RRF | 75.0% / 96.3% / 83 ms |
| 无证据拒答 | 前 100 题只给无关文档 | 84 / 100 |
| 五工具首轮选对 | 自建工具选择题 200 道 | 190 / 200（95%） |

以上数字以 `data/eval/` 里的 JSON 为准，换机器复跑可能有小幅波动。混合检索相对 BM25，Hit@1 由 67.0% 到 75.0%。

可选：设置 `TESTPILOT_RERANK=1` 后，混合检索会对前 20 条做 `bge-reranker-base` 重排。主评测数字未计入这一步。

## 目录

| 路径 | 作用 |
| --- | --- |
| `main.py` | FastAPI：页面、问答、检索 |
| `agent.py` | LangGraph 编排五个工具 |
| `agent_tools.py` | 文档检索、相似故障、历史运行、版本对比、回归保存 |
| `retriever.py` | BM25 与 Qdrant 向量混合检索 |
| `chunker.py` | 按段落和长度切块 |
| `embedder.py` | BGE-small-zh Embedding |
| `vector_store.py` | Qdrant 本地向量库 |
| `reranker.py` | 可选交叉编码器重排 |
| `rgb_data.py` | 读取 RGB 数据 |
| `eval_retrieval.py` | 检索评测 |
| `eval_reject.py` | 无证据拒答评测 |
| `eval_tools.py` | 五工具首轮选择评测 |
| `data/rgb/` | 公开集原文 |
| `data/kb/` | 本地研发笔记 |
| `data/eval/` | 实跑指标 |
| `static/index.html` | 应用页面 |
