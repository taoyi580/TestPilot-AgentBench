# 评测数据

题目、文档和参考答案使用公开集；检索成绩只采用本仓库脚本的实跑结果，不引用论文中其他模型的分数。

## RGB

来源：[chen700564/RGB](https://github.com/chen700564/RGB)（AAAI 2024）

许可证：CC BY-NC-SA 4.0，仅非商业使用。使用本仓库中的 RGB 语料须保留来源说明。

已收录中文部分：

| 文件 | 题量 | 用途 |
| --- | --- | --- |
| `data/rgb/zh_refine.json` | 300 | 主评测：query、answer、positive、negative |
| `data/rgb/zh_int.json` | 100 | 多文档整合 |
| `data/rgb/zh_fact.json` | 100 | 含错误文档时的稳健性 |
| 合计 | 500 | 评测集 |

检索评测结果见 `data/eval/`（可用脚本复算）：

- Hit@1 / Hit@5：前 1 / 5 条是否命中该题的 positive 文档
- P95：检索耗时（含问句 Embedding；不含大模型生成）
- 无证据场景：只提供 negative 文档，生成侧应回答不知道（`python eval_reject.py`）
- 五工具首轮选择：自建工具选择题 200 道（`python eval_tools.py`）

本仓库最近一次实跑（RGB `zh_refine`，7337 篇去重文档，切成 7401 块）：

- BM25：Hit@1 67.0%，Hit@5 94.7%，MRR@10 0.787，P95 40ms
- 向量检索（BGE-small-zh + Qdrant）：Hit@1 72.0%，Hit@5 93.7%，MRR@10 0.819，P95 49ms
- 混合检索（BM25 与向量 RRF）：Hit@1 75.0%，Hit@5 96.3%，MRR@10 0.844，P95 83ms
- 无证据拒答：84/100
- 五工具首轮选对：190/200（自建工具选择题）

混合检索相对 BM25，Hit@1 提高 8 个百分点。交叉编码器重排是可选步骤（`TESTPILOT_RERANK=1`），主数字未计入重排。

`data/kb/` 为补充的本地研发笔记，不计入上述检索评测。
