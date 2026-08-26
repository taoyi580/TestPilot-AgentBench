# TestPilot

可演示的检索问答：先检索本地文档，再按资料生成回答。资料不够会说不知道。

主评测语料来自公开集 [RGB](https://github.com/chen700564/RGB)（AAAI 2024，CC BY-NC-SA 4.0，**仅非商业使用**）。本仓库用于求职作品演示，不用于商业产品。

## 现在能看什么

- 打开网页提问，看到回答和用来源的原文
- 语料可切换：RGB 中文 300 题派生文档，或 `data/kb/` 里 5 篇研发笔记
- 「无证据演示」按 RGB 官方做法，只提供噪声文档，模型应拒答
- 检索效果由脚本实跑：`python eval_retrieval.py`

## 启动

```powershell
cd C:\Users\19073\Documents\TestPilot-AgentBench
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

浏览器打开 http://127.0.0.1:8000

把 DeepSeek 钥匙写进 `.env`（复制 `.env.example`）。没有钥匙时仍可点「只看检索」。

在线演示和仓库地址见本页顶部；部署时把 `DEEPSEEK_API_KEY` 配在平台环境变量里，不要写进代码。

## 评测

```powershell
.\.venv\Scripts\python.exe eval_retrieval.py
```

结果写入 `data/eval/retrieval_zh_refine.json`。指标是 **Hit@K / MRR / P95**，在 RGB `zh_refine` 的 300 道题、该分片全部正例+噪声去重后的文档上计算。这是派生检索集，不是 RGB 论文里的生成准确率。

## 目录

| 路径 | 作用 |
| --- | --- |
| `main.py` | FastAPI：页面、问答、检索 |
| `retriever.py` | jieba + BM25 |
| `rgb_data.py` | 读取 RGB jsonl |
| `eval_retrieval.py` | 检索评测 |
| `data/rgb/` | 公开集原文 |
| `data/kb/` | 本地研发笔记 |
| `static/index.html` | 演示页 |

面试学习台仍在 http://127.0.0.1:8000/learn
