# TestPilot

研发文档与故障诊断 Agent：先检索证据，再按资料生成回答。资料不足时明确拒绝作答，不编造。

检索与拒答主评测使用公开集 [RGB](https://github.com/chen700564/RGB)（AAAI 2024，CC BY-NC-SA 4.0，仅非商业使用）。题目、文档和参考答案来自该数据集；成绩只采用本仓库脚本的实跑结果。

## 它做什么

中文文档量大、问句短时，单靠关键词或单靠向量都容易漏。TestPilot 把切块后的文档建成两路索引，按 Reciprocal Rank Fusion 混合召回，再交给五个工具做问答和排查。

```text
文档切块
    → BGE-small-zh Embedding 写入 Qdrant
    → 与 jieba + BM25 做 RRF 混合召回
    → LangGraph 选择工具（检索 / 相似故障 / 运行记录 / 版本对比 / 回归保存）
    → 只根据工具返回的资料生成；没有证据则拒答
```

五个工具：

| 工具 | 作用 |
| --- | --- |
| `search_docs` | 在语料中检索文档 |
| `similar_incidents` | 查相似故障记录 |
| `run_history` | 读最近一次运行轨迹 |
| `compare_versions` | 对比两份检索评测结果 |
| `save_regression` | 把失败样本写入回归文件 |

## 公开集结果

RGB 中文部分共 500 题：`zh_refine` 300 + `zh_int` 100 + `zh_fact` 100。检索与拒答主评测用 `zh_refine`：300 题，7337 篇去重文档，切成 7401 块。数字以 `data/eval/` 为准。

| 实验 | 口径 | Hit@1 | Hit@5 | MRR@10 | P95 |
| --- | --- | --- | --- | --- | --- |
| BM25 | jieba 分词 | 67.0% | 94.7% | 0.787 | 40 ms |
| 向量 | `BAAI/bge-small-zh-v1.5` + Qdrant | 72.0% | 93.7% | 0.819 | 49 ms |
| 混合 | BM25 与向量 RRF | **75.0%** | 96.3% | 0.844 | 83 ms |

相对 BM25，混合检索 Hit@1 由 67.0% 到 75.0%。P95 含问句 Embedding，不含大模型生成。

| 实验 | 口径 | 结果 |
| --- | --- | --- |
| 无证据拒答 | 前 100 题只提供 negative 文档 | 84 / 100 |
| 五工具首轮选对 | 自建工具选择题 200 道 | 190 / 200（95%） |

可选：设置 `TESTPILOT_RERANK=1` 后，混合检索会对前 20 条做 `bge-reranker-base` 重排。上表主数字未计入这一步。换机器复跑可能有小幅波动。明细见 [DATA.md](DATA.md)。

## 在另一台电脑运行

推荐使用 **Python 3.12（64 位）**。首次运行需要联网下载中文向量模型，并为仓库内的文档建立本地索引；完成前服务不会开始接收请求。

Windows PowerShell：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

macOS / Linux：

```bash
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
./.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000 。不配置 `DEEPSEEK_API_KEY` 仍可使用“只看检索”；需要生成完整回答时，再把密钥写入本机 `.env`，不要提交。

如果首次模型下载被网络或代理阻断，应用无法完成索引初始化。生成的模型缓存和 Qdrant 数据只保存在本机 `data/cache/`、`data/qdrant/`，已被 Git 忽略。

## 复现评测

```bash
./.venv/bin/python eval_retrieval.py --mode all
./.venv/bin/python eval_reject.py
./.venv/bin/python eval_tools.py
```

Windows 将命令中的 `./.venv/bin/python` 换成 `.\.venv\Scripts\python.exe`。

首次评测会下载 `BAAI/bge-small-zh-v1.5`，并为 7000 余篇文档建向量库。向量和 Qdrant 数据写在 `data/cache/`、`data/qdrant/`，不提交到 Git。

生成回答需要 `DEEPSEEK_API_KEY`。未配置时检索评测仍可完整跑完。

## 仓库结构

| 路径 | 作用 |
| --- | --- |
| `retriever.py` | BM25 与 Qdrant 向量的 RRF 混合召回 |
| `chunker.py` | 按段落和长度切块 |
| `embedder.py` | BGE-small-zh Embedding |
| `vector_store.py` | Qdrant 本地向量库 |
| `reranker.py` | 可选交叉编码器重排 |
| `agent.py` | LangGraph 编排五个工具 |
| `agent_tools.py` | 工具实现 |
| `eval_retrieval.py` | BM25 / 向量 / 混合检索评测 |
| `eval_reject.py` | 无证据拒答评测 |
| `eval_tools.py` | 五工具首轮选择评测 |
| `rgb_data.py` | 读取 RGB |
| `data/rgb/` | 公开集原文 |
| `data/eval/` | 实跑指标 |
| `DATA.md` | 评测口径 |

`data/kb/` 是补充的研发笔记，不计入上表 RGB 检索成绩。
