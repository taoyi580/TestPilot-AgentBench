# TestPilot

仓库：[taoyi580/TestPilot-AgentBench](https://github.com/taoyi580/TestPilot-AgentBench)

研发文档与故障诊断助手：先检索资料，再按资料生成回答。资料不足时会明确说不知道。

主评测语料来自公开集 [RGB](https://github.com/chen700564/RGB)（AAAI 2024，CC BY-NC-SA 4.0，**仅非商业使用**）。

## 功能

- 网页提问，展示回答、工具轨迹和引用来源
- LangGraph 编排五个工具：文档检索、相似故障、历史运行、版本对比、回归保存
- 可切换 RGB 公开新闻问答，或本地研发笔记
- 无证据场景只提供无关文档，模型应拒绝作答
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

## 评测（本仓库实跑）

公开集共 500 题（`zh_refine` 300 + `zh_int` 100 + `zh_fact` 100）。检索与拒答主评测用 `zh_refine`。

```bash
python eval_retrieval.py --mode both
python eval_reject.py
python eval_tools.py
```

| 项目 | 口径 | 结果 |
| --- | --- | --- |
| BM25 Hit@1 / Hit@5 / P95 | RGB `zh_refine` 300 题，7337 篇去重文档 | 67.0% / 94.7% / 40 ms |
| 混合检索 Hit@1 / Hit@5 / P95 | BM25 + TF-IDF 融合后重排 | 68.0% / 93.7% / 63 ms |
| 无证据拒答 | 前 100 题只给无关文档 | 84 / 100 |
| 五工具首轮选对 | 自建 200 题，不是官方 BFCL | 190 / 200（95%） |

以上数字以 `data/eval/` 里的 JSON 为准，换机器复跑可能有小幅波动。混合检索对 Hit@1 只有约 1 个百分点提升，不要写成大幅跃升。

## 目录

| 路径 | 作用 |
| --- | --- |
| `main.py` | FastAPI：页面、问答、检索 |
| `agent.py` | LangGraph 编排五个工具 |
| `agent_tools.py` | 文档检索、相似故障、历史运行、版本对比、回归保存 |
| `retriever.py` | jieba + BM25，可选与 TF-IDF 融合重排 |
| `rgb_data.py` | 读取 RGB 数据 |
| `eval_retrieval.py` | 检索评测 |
| `eval_reject.py` | 无证据拒答评测 |
| `eval_tools.py` | 五工具首轮选择评测 |
| `data/rgb/` | 公开集原文 |
| `data/kb/` | 本地研发笔记 |
| `data/eval/` | 实跑指标 |
| `static/index.html` | 应用页面 |
