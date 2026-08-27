"""交叉编码器重排。模型加载失败时返回原顺序，不中断检索。"""

from __future__ import annotations

import os

from pathlib import Path

RERANK_MODEL = "BAAI/bge-reranker-base"
RERANK_TOP = 20
CACHE_DIR = Path(__file__).resolve().parent / "data" / "cache" / "fastembed"

_model = None
_failed = False
_used_once = False


def rerank_enabled() -> bool:
    flag = os.getenv("TESTPILOT_RERANK", "0").strip().lower()
    return flag in {"1", "true", "yes", "on"}


def last_rerank_used() -> bool:
    return _used_once


def _get_model():
    global _model, _failed
    if _failed:
        return None
    if _model is None:
        try:
            from fastembed.rerank.cross_encoder import TextCrossEncoder

            print(f"加载重排模型 {RERANK_MODEL}（首次会下载，约 1GB）…", flush=True)
            CACHE_DIR.mkdir(parents=True, exist_ok=True)
            _model = TextCrossEncoder(model_name=RERANK_MODEL, cache_dir=str(CACHE_DIR))
        except Exception as exc:
            print(f"重排模型不可用，混合检索只做 BM25+向量融合：{exc}")
            _failed = True
            return None
    return _model


def rerank_doc_ids(query: str, doc_ids: list[str], doc_by_id: dict[str, dict], top_n: int = RERANK_TOP) -> list[str]:
    global _used_once
    if not rerank_enabled() or not doc_ids:
        return doc_ids
    model = _get_model()
    if model is None:
        return doc_ids
    head = doc_ids[: max(1, min(top_n, len(doc_ids)))]
    rest = doc_ids[len(head) :]
    texts = [(doc_by_id[did]["text"] if did in doc_by_id else "")[:1200] for did in head]
    try:
        scores = list(model.rerank(query, texts, batch_size=16))
    except Exception as exc:
        print(f"重排失败，沿用融合顺序：{exc}")
        return doc_ids
    _used_once = True
    order = sorted(range(len(head)), key=lambda i: float(scores[i]), reverse=True)
    return [head[i] for i in order] + rest
