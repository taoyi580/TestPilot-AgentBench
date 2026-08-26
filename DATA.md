# 评测数据

题目、文档和参考答案使用公开集；检索成绩只采用本仓库脚本的实跑结果，不引用论文中其他模型的分数。

## RGB

来源：[chen700564/RGB](https://github.com/chen700564/RGB)（AAAI 2024）

许可证：CC BY-NC-SA 4.0，仅非商业使用。本仓库用于非商业演示，须保留来源说明。

已收录中文部分：

| 文件 | 题量 | 用途 |
| --- | --- | --- |
| `data/rgb/zh_refine.json` | 300 | 主评测：query、answer、positive、negative |
| `data/rgb/zh_int.json` | 100 | 多文档整合 |
| `data/rgb/zh_fact.json` | 100 | 含错误文档时的稳健性 |
| 合计 | 500 | 评测集 |

检索评测结果见 `data/eval/retrieval_zh_refine.json`（`python eval_retrieval.py` 可复算）：

- Hit@1 / Hit@5：前 1 / 5 条是否命中该题的 positive 文档
- P95：检索耗时
- 无证据场景：只提供 negative 文档，生成侧应回答不知道

`data/kb/` 为补充的本地研发笔记，不计入上述检索评测。
