from pathlib import Path


def load_sample_texts() -> list[tuple[str, str]]:
    root = Path(__file__).resolve().parents[3] / "sample_data"
    return [(path.name, path.read_text(encoding="utf-8")) for path in sorted(root.glob("*.md"))]

