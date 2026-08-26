# TestPilot

仓库：[taoyi580/TestPilot-AgentBench](https://github.com/taoyi580/TestPilot-AgentBench)

检索问答应用：先检索文档，再按资料生成回答。资料不足时会明确说不知道。

主评测语料来自公开集 [RGB](https://github.com/chen700564/RGB)（AAAI 2024，CC BY-NC-SA 4.0，**仅非商业使用**）。

## 功能

- 网页提问，展示回答和引用来源
- 可切换 RGB 公开新闻问答，或本地研发笔记
- 无证据场景只提供无关文档，模型应拒绝作答
- 检索指标由 `python eval_retrieval.py` 实跑

## 本地运行

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
copy .env.example .env
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

打开 http://127.0.0.1:8000

把 `DEEPSEEK_API_KEY` 写入 `.env`。未配置时仍可使用「只看检索」。线上部署请把该变量配在平台环境变量中，不要写入代码。

## 评测

```bash
python eval_retrieval.py
```

结果写入 `data/eval/retrieval_zh_refine.json`。指标为 Hit@K、MRR、P95，在 RGB `zh_refine` 的 300 道题、该分片全部正例与噪声去重后的文档上计算。这是派生检索集，不是 RGB 论文中的生成准确率。

## 目录

| 路径 | 作用 |
| --- | --- |
| `main.py` | FastAPI：页面、问答、检索 |
| `retriever.py` | jieba + BM25 |
| `rgb_data.py` | 读取 RGB 数据 |
| `eval_retrieval.py` | 检索评测 |
| `data/rgb/` | 公开集原文 |
| `data/kb/` | 本地研发笔记 |
| `static/index.html` | 应用页面 |
