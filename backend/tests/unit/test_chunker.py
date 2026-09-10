from backend.app.core.config import Settings
from backend.app.rag.chunker import SemanticChunker
from backend.app.rag.parser import Section


def test_chunker_preserves_section_metadata():
    settings = Settings(
        chunk_target_tokens=20,
        chunk_min_tokens=5,
        chunk_max_tokens=30,
        chunk_overlap_tokens=5,
    )
    chunker = SemanticChunker(settings)
    sections = [
        Section(
            page=3,
            heading="Docker Volumes",
            text=(
                "A volume stores persistent data. "
                "Containers can be recreated without losing data. "
                "Volumes are managed by Docker."
            ),
        )
    ]

    chunks = chunker.chunk(sections)

    assert chunks
    assert all(chunk.page == 3 for chunk in chunks)
    assert all(chunk.section == "Docker Volumes" for chunk in chunks)
