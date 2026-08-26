"""在 RGB zh_refine 上评测文档级 BM25：Hit@K、MRR、P95 延迟。"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from rgb_data import doc_id
from retriever import get_index, get_rgb_items

BASE_DIR = Path(__file__).resolve().parent
OUT_PATH = BASE_DIR / "data" / "eval" / "retrieval_zh_refine.json"


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def evaluate(k_list: tuple[int, ...] = (1, 3, 5, 10)) -> dict:
    items = get_rgb_items("zh_refine")
    index = get_index("rgb")
    max_k = max(k_list)
    hits = {k: 0 for k in k_list}
    reciprocal_ranks: list[float] = []
    latencies: list[float] = []

    for item in items:
        gold = {doc_id(text) for text in item["positive"]}
        ranked, elapsed_ms = index.search(item["query"], k=max_k)
        latencies.append(elapsed_ms)
        ids = [hit["id"] for hit in ranked]
        rank = next((i + 1 for i, hid in enumerate(ids) if hid in gold), None)
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
        for k in k_list:
            if any(hid in gold for hid in ids[:k]):
                hits[k] += 1

    n = len(items)
    result = {
        "dataset": "RGB zh_refine",
        "source": "https://github.com/chen700564/RGB",
        "license": "CC BY-NC-SA 4.0",
        "retriever": "jieba + BM25，文档级，语料为该分片全部 positive+negative 去重",
        "n_queries": n,
        "n_docs": len(index.docs),
        "hit": {
            str(k): {"count": hits[k], "rate": round(hits[k] / n, 4)}
            for k in k_list
        },
        "mrr_at_10": round(sum(reciprocal_ranks) / n, 4),
        "p50_latency_ms": round(percentile(latencies, 50), 2),
        "p95_latency_ms": round(percentile(latencies, 95), 2),
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    print("正在建索引并评测，第一次大约一两分钟…")
    result = evaluate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"已写入 {OUT_PATH}")


if __name__ == "__main__":
    main()
