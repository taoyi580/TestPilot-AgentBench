"""按段落和长度切块。RGB 新闻大多短于一块；本地笔记会切成多块。"""

from __future__ import annotations

MAX_CHARS = 400
OVERLAP = 80


def _windows(text: str, max_chars: int, overlap: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    step = max(1, max_chars - overlap)
    out: list[str] = []
    start = 0
    while start < len(text):
        out.append(text[start : start + max_chars])
        if start + max_chars >= len(text):
            break
        start += step
    return out


def split_text(text: str, max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[str]:
    text = (text or "").replace("\r\n", "\n").strip()
    if not text:
        return []
    if len(text) <= max_chars:
        return [text]

    parts = [p.strip() for p in text.split("\n") if p.strip()]
    if not parts:
        return _windows(text, max_chars, overlap)

    packed: list[str] = []
    buf = ""
    for part in parts:
        candidate = part if not buf else f"{buf}\n{part}"
        if len(candidate) <= max_chars:
            buf = candidate
            continue
        if buf:
            packed.append(buf)
        if len(part) <= max_chars:
            buf = part
        else:
            packed.extend(_windows(part, max_chars, overlap))
            buf = ""
    if buf:
        packed.append(buf)
    return packed or [text[:max_chars]]


def chunk_docs(docs: list[dict], max_chars: int = MAX_CHARS, overlap: int = OVERLAP) -> list[dict]:
    chunks: list[dict] = []
    for doc in docs:
        pieces = split_text(doc["text"], max_chars=max_chars, overlap=overlap)
        if not pieces:
            pieces = [doc["text"]]
        for index, piece in enumerate(pieces):
            chunks.append(
                {
                    "chunk_id": f"{doc['id']}:{index}",
                    "doc_id": doc["id"],
                    "title": doc["title"],
                    "text": piece,
                }
            )
    return chunks
