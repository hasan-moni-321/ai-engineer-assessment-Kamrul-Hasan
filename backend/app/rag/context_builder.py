from backend.app.schemas.rag import RetrievedChunk
from backend.app.schemas.superhero import SuperheroResult


def build_context(
    chunks: list[RetrievedChunk],
    superheroes: list[SuperheroResult],
    final_k: int,
) -> tuple[str, list[dict]]:
    selected = chunks[:final_k]
    source_records: list[dict] = []
    blocks: list[str] = []

    for index, chunk in enumerate(selected, start=1):
        blocks.append(
            f"[PDF SOURCE {index}]\n"
            f"File: {chunk.source_name}\n"
            f"Page: {chunk.page}\n"
            f"Section: {chunk.section}\n"
            f"Similarity: {chunk.score:.4f}\n"
            f"Content:\n{chunk.text}"
        )
        source_records.append(
            {
                "source_type": "pdf",
                "source_name": chunk.source_name,
                "page": chunk.page,
                "section": chunk.section,
                "chunk_id": chunk.chunk_id,
                "score": chunk.score,
            }
        )

    offset = len(selected)
    for index, hero in enumerate(superheroes, start=1):
        blocks.append(
            f"[SUPERHERO API SOURCE {offset + index}]\n"
            f"Title: {hero.title}\n"
            f"Source: {hero.source_name}\n"
            f"Content:\n{hero.content}"
        )
        source_records.append(
            {
                "source_type": "superhero",
                "source_name": hero.source_name,
                "title": hero.title,
                "metadata": hero.metadata,
            }
        )

    return "\n\n".join(blocks), source_records
