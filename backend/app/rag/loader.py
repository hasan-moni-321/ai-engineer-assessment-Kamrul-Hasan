from pathlib import Path
import fitz


class PDFPage:
    def __init__(self, page_number: int, text: str):
        self.page_number = page_number
        self.text = text


def load_pdf(path: str | Path) -> list[PDFPage]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    pages: list[PDFPage] = []
    with fitz.open(path) as document:
        for index, page in enumerate(document):
            text = page.get_text("text")
            pages.append(PDFPage(index + 1, text))
    return pages
