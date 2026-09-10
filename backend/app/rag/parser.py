import re
from dataclasses import dataclass
from .loader import PDFPage


@dataclass
class Section:
    page: int
    heading: str
    text: str


_HEADING_PATTERNS = [
    re.compile(r"^(#{1,6})\s+(.+)$"),
    re.compile(r"^\d+(\.\d+)*[\.)]?\s+.{3,100}$"),
    re.compile(r"^[A-Z][A-Za-z0-9 /&()_-]{2,80}$"),
]


def _looks_like_heading(line: str) -> bool:
    line = line.strip()
    if not line or len(line) > 120:
        return False
    if line.endswith((".", "?", "!", ":")):
        return False
    return any(pattern.match(line) for pattern in _HEADING_PATTERNS)


def parse_sections(pages: list[PDFPage]) -> list[Section]:
    sections: list[Section] = []
    current_heading = "Document"
    buffer: list[str] = []

    def flush(page_number: int) -> None:
        nonlocal buffer
        text = "\n".join(buffer).strip()
        if text:
            sections.append(Section(page_number, current_heading, text))
        buffer = []

    for page in pages:
        lines = [line.strip() for line in page.text.splitlines()]
        for line in lines:
            if not line:
                continue
            if _looks_like_heading(line):
                flush(page.page_number)
                current_heading = line
            else:
                buffer.append(line)
        if buffer:
            flush(page.page_number)

    return sections
