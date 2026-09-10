from dataclasses import dataclass
import re
import tiktoken

from backend.app.core.config import Settings
from backend.app.rag.parser import Section


@dataclass
class Chunk:
    page: int
    section: str
    text: str


class SemanticChunker:
    def __init__(self, settings: Settings):
        self.settings = settings
        try:
            self.encoder = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.encoder = None

    def _count(self, text: str) -> int:
        if self.encoder:
            return len(self.encoder.encode(text))
        return len(text.split())

    def _split_sentences(self, text: str) -> list[str]:
        return [
            part.strip()
            for part in re.split(r"(?<=[.!?])\s+", text)
            if part.strip()
        ]

    def chunk(self, sections: list[Section]) -> list[Chunk]:
        output: list[Chunk] = []

        for section in sections:
            sentences = self._split_sentences(section.text)
            current: list[str] = []
            current_tokens = 0

            for sentence in sentences:
                sentence_tokens = self._count(sentence)

                if (
                    current
                    and current_tokens + sentence_tokens > self.settings.chunk_max_tokens
                ):
                    output.append(
                        Chunk(
                            page=section.page,
                            section=section.heading,
                            text=" ".join(current).strip(),
                        )
                    )

                    overlap: list[str] = []
                    overlap_tokens = 0
                    for previous in reversed(current):
                        tokens = self._count(previous)
                        if overlap_tokens + tokens > self.settings.chunk_overlap_tokens:
                            break
                        overlap.insert(0, previous)
                        overlap_tokens += tokens

                    current = overlap
                    current_tokens = overlap_tokens

                current.append(sentence)
                current_tokens += sentence_tokens

                if current_tokens >= self.settings.chunk_target_tokens:
                    output.append(
                        Chunk(
                            page=section.page,
                            section=section.heading,
                            text=" ".join(current).strip(),
                        )
                    )
                    current = []
                    current_tokens = 0

            if current:
                text = " ".join(current).strip()
                if (
                    output
                    and self._count(text) < self.settings.chunk_min_tokens
                    and output[-1].section == section.heading
                ):
                    output[-1].text += " " + text
                else:
                    output.append(
                        Chunk(
                            page=section.page,
                            section=section.heading,
                            text=text,
                        )
                    )

        return output
