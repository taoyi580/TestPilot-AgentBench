# 评测数据（公开集，不是自己出题）

原则：题目、文档、标准答案用别人已经公开的；Hit@5、发现数等成绩只写自己脚本跑出来的。
不抄论文里 ChatGPT / Qwen 的分数。

## TestPilot 用 RGB

来源：[chen700564/RGB](https://github.com/chen700564/RGB)（AAAI 2024 论文配套，中英新闻问答 + 正例/噪声文档）

许可证：CC BY-NC-SA 4.0，仅非商业使用。求职作品集可以，仓库必须写上来源；不能拿去卖产品。

本仓库已下载中文部分：

| 文件 | 题量 | 用途 |
| --- | --- | --- |
| `data/rgb/zh_refine.json` | 300 | 主评测：每题有 query、answer、positive、negative |
| `data/rgb/zh_int.json` | 100 | 多文档整合 |
| `data/rgb/zh_fact.json` | 100 | 文档含错误时的稳健性 |
| 合计 | 500 | 冻结评测集 |

检索评测已实跑，结果在 `data/eval/retrieval_zh_refine.json`（`python eval_retrieval.py` 可复算）：

- Hit@1 / Hit@5：前 1 / 5 条里是否出现该题的 positive 文档
- P95：检索耗时
- 拒答：页面「无证据演示」按 RGB 做法只给 negative，生成侧应回答不知道。自动拒答率脚本尚未覆盖 100 题。

`data/kb/` 里那 5 篇短文只给事件 2 练手，不算正式评测集。

## SpecPilot 用 VAmPI

来源：[erev0s/VAmPI](https://github.com/erev0s/VAmPI)（MIT）

这是专门给第三方工具评效果的公开脆弱 API，带官方 OpenAPI 3。

| 项目 | 公开事实 |
| --- | --- |
| 接口 | README 表格 14 个 path，不是自己写的 8 个 |
| 标准答案 | README「List of Vulnerabilities」9 类，不是自己埋的 20 个故障 |
| 误报 | 官方提供 `vulnerable=0/1`，同一套题在安全模式再跑一遍 |
| 对照 | 同一份 OpenAPI 上跑 [Schemathesis](https://github.com/schemathesis/schemathesis) |

检测率 = 命中上述 9 类公开问题的条数 / 9。
误报率 = `vulnerable=0` 时仍报警的比例。
不要把别人扫 VAmPI 的结果抄到简历上。

更大、但应届很难完整跑起来的公开集（先不作为主集）：[Defects4REST](https://github.com/ANSWER-OSU/Defects4REST) 110 个真实 REST 缺陷，MIT。
