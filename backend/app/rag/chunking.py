import re


def clean_text(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text.replace("\r\n", "\n")).strip()


def paragraph_aware_chunks(text: str, target_size: int = 900, overlap: int = 120) -> list[str]:
    paragraphs = [part.strip() for part in clean_text(text).split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        if len(current) + len(paragraph) + 2 <= target_size:
            current = f"{current}\n\n{paragraph}".strip()
            continue
        if current:
            chunks.append(current)
            tail = current[-overlap:] if overlap > 0 else ""
            current = f"{tail}\n\n{paragraph}".strip()
        else:
            chunks.append(paragraph[:target_size])
            current = paragraph[target_size - overlap :]
    if current:
        chunks.append(current)
    return chunks
