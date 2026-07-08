import math

from app.schemas.chat import Citation


def cosine(a: list[float], b: list[float]) -> float:
    limit = min(len(a), len(b))
    dot = sum(a[i] * b[i] for i in range(limit))
    norm_a = math.sqrt(sum(value * value for value in a)) or 1.0
    norm_b = math.sqrt(sum(value * value for value in b)) or 1.0
    return dot / (norm_a * norm_b)


def citations_from_chunks(chunks) -> list[Citation]:
    return [
        Citation(
            document_id=chunk.document_id,
            document_name=chunk.document_name,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            snippet=chunk.content[:240],
        )
        for chunk in chunks
    ]
