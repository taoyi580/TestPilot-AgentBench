"""在 RGB zh_refine 上评测 BM25、向量或混合检索。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from reranker import RERANK_MODEL, last_rerank_used
from rgb_data import doc_id
from retriever import get_index, get_rgb_items

BASE_DIR = Path(__file__).resolve().parent

LABELS = {
    "bm25": "jieba + BM25",
    "vector": "BGE-small-zh 向量检索（Qdrant）",
    "hybrid": "BM25 与 BGE 向量（Qdrant）RRF 混合召回",
}
OUT_NAMES = {
    "bm25": "retrieval_zh_refine.json",
    "vector": "retrieval_vector_zh_refine.json",
    "hybrid": "retrieval_hybrid_zh_refine.json",
}


def percentile(values: list[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def evaluate(mode: str = "bm25", k_list: tuple[int, ...] = (1, 3, 5, 10)) -> dict:
    items = get_rgb_items("zh_refine")
    index = get_index("rgb")
    max_k = max(k_list)
    hits = {k: 0 for k in k_list}
    reciprocal_ranks: list[float] = []
    latencies: list[float] = []

    for i, item in enumerate(items, start=1):
        gold = {doc_id(text) for text in item["positive"]}
        ranked, elapsed_ms = index.search(item["query"], k=max_k, mode=mode)
        latencies.append(elapsed_ms)
        ids = [hit["id"] for hit in ranked]
        rank = next((pos + 1 for pos, hid in enumerate(ids) if hid in gold), None)
        reciprocal_ranks.append(0.0 if rank is None else 1.0 / rank)
        for k in k_list:
            if any(hid in gold for hid in ids[:k]):
                hits[k] += 1
        if i % 50 == 0:
            print(f"  {mode} {i}/{len(items)}", flush=True)

    n = len(items)
    rerank_model = RERANK_MODEL if mode == "hybrid" and last_rerank_used() else None
    retriever = LABELS[mode]
    if rerank_model:
        retriever = f"{LABELS['hybrid']}，再经 {rerank_model} 重排前 20"
    result = {
        "dataset": "RGB zh_refine",
        "source": "https://github.com/chen700564/RGB",
        "license": "CC BY-NC-SA 4.0",
        "retriever": f"{retriever}，文档级，语料为该分片全部 positive+negative 去重",
        "mode": mode,
        "embed_model": index.embed_model if mode != "bm25" else None,
        "vector_backend": index.vector_backend if mode != "bm25" else None,
        "rerank_model": rerank_model,
        "n_queries": n,
        "n_docs": len(index.docs),
        "n_chunks": index.n_chunks,
        "hit": {
            str(k): {"count": hits[k], "rate": round(hits[k] / n, 4)}
            for k in k_list
        },
        "mrr_at_10": round(sum(reciprocal_ranks) / n, 4),
        "p50_latency_ms": round(percentile(latencies, 50), 2),
        "p95_latency_ms": round(percentile(latencies, 95), 2),
    }
    out_path = BASE_DIR / "data" / "eval" / OUT_NAMES[mode]
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["out_path"] = str(out_path)
    return result


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["bm25", "vector", "hybrid", "both", "all"], default="both")
    args = parser.parse_args()
    if args.mode == "both":
        modes = ["bm25", "hybrid"]
    elif args.mode == "all":
        modes = ["bm25", "vector", "hybrid"]
    else:
        modes = [args.mode]
    print("正在评测…")
    for mode in modes:
        result = evaluate(mode)
        print(json.dumps({k: v for k, v in result.items() if k != "out_path"}, ensure_ascii=False, indent=2))
        print(f"已写入 {result['out_path']}")


if __name__ == "__main__":
    main()
