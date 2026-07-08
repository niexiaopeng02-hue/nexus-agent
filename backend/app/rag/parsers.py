from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedSection:
    text: str
    page_number: int | None = None


class DocumentParser(ABC):
    @abstractmethod
    def parse(self, name: str, content: bytes) -> list[ParsedSection]:
        raise NotImplementedError


class TextParser(DocumentParser):
    def parse(self, name: str, content: bytes) -> list[ParsedSection]:
        return [ParsedSection(content.decode("utf-8", errors="ignore"))]


class PDFParser(DocumentParser):
    def parse(self, name: str, content: bytes) -> list[ParsedSection]:
        import fitz

        sections: list[ParsedSection] = []
        document = fitz.open(stream=content, filetype="pdf")
        for index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            if text:
                sections.append(ParsedSection(text=text, page_number=index))
        return sections


class DOCXParser(DocumentParser):
    def parse(self, name: str, content: bytes) -> list[ParsedSection]:
        from io import BytesIO

        from docx import Document

        document = Document(BytesIO(content))
        text = "\n\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip())
        return [ParsedSection(text=text)]


def get_parser(filename: str) -> DocumentParser:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return PDFParser()
    if suffix == ".docx":
        return DOCXParser()
    return TextParser()
