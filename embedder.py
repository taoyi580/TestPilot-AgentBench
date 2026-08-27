"""本地中文 Embedding：BGE-small-zh，ONNX，不依赖 PyTorch。"""

from __future__ import annotations

from pathlib import Path

import numpy as np

MODEL_NAME = "BAAI/bge-small-zh-v1.5"
VECTOR_DIM = 512
CACHE_DIR = Path(__file__).resolve().parent / "data" / "cache" / "fastembed"

_model = None


def get_model():
    global _model
    if _model is None:
        from fastembed import TextEmbedding

        print(f"加载 Embedding 模型 {MODEL_NAME}（首次会下载）…", flush=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _model = TextEmbedding(model_name=MODEL_NAME, cache_dir=str(CACHE_DIR))
    return _model


def embed_passages(texts: list[str], batch_size: int = 64) -> np.ndarray:
    if not texts:
        return np.zeros((0, VECTOR_DIM), dtype=np.float32)
    model = get_model()
    rows = []
    for i, vec in enumerate(model.embed(texts, batch_size=batch_size)):
        rows.append(np.asarray(vec, dtype=np.float32))
        if (i + 1) % 1000 == 0:
            print(f"  已向量化 {i + 1}/{len(texts)}", flush=True)
    matrix = np.vstack(rows)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms = np.clip(norms, 1e-8, None)
    return matrix / norms


def embed_query(text: str) -> np.ndarray:
    model = get_model()
    vec = np.asarray(next(model.query_embed(text)), dtype=np.float32)
    norm = float(np.linalg.norm(vec)) or 1e-8
    return vec / norm
