import argparse
import asyncio
from pathlib import Path
import uuid


from backend.app.clients.openai_client import OpenAIClient
from backend.app.clients.qdrant_client import QdrantRepository
from backend.app.core.config import get_settings
from backend.app.rag.chunker import SemanticChunker
from backend.app.rag.embeddings import EmbeddingService
from backend.app.rag.loader import load_pdf
from backend.app.rag.parser import parse_sections
from backend.app.schemas.rag import DocumentChunk


async def ingest(pdf_path: str) -> None:
    settings = get_settings()

    pages = load_pdf(pdf_path)
    sections = parse_sections(pages)
    chunker = SemanticChunker(settings)
    raw_chunks = chunker.chunk(sections)

    openai = OpenAIClient(settings)
    embeddings = EmbeddingService(openai)
    qdrant = QdrantRepository(settings)

    texts = [item.text for item in raw_chunks]
    vectors = await embeddings.embed_texts(texts)

    if not vectors:
        raise RuntimeError("No chunks were generated from the PDF.")

    await qdrant.ensure_collection(len(vectors[0]))

    document_id = Path(pdf_path).stem
    document_version = "v1"

    # chunks = [
    #     DocumentChunk(
    #         chunk_id=f"{document_id}-{index:06d}",
    #         document_id=document_id,
    #         document_version=document_version,
    #         source_name=Path(pdf_path).name,
    #         page=item.page,
    #         section=item.section,
    #         topic=_infer_topic(item.section, item.text),
    #         content_type="technical_knowledge",
    #         text=item.text,
    #     )
    #     for index, item in enumerate(raw_chunks, start=1)
    # ]
    chunks = [
        DocumentChunk(
            chunk_id=f"{document_id}-{index:06d}",
            point_id=str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    f"{document_id}:{document_version}:{index}",
                )
            ),
            document_id=document_id,
            document_version=document_version,
            source_name=Path(pdf_path).name,
            page=item.page,
            section=item.section,
            topic=_infer_topic(item.section, item.text),
            content_type="technical_knowledge",
            text=item.text,
        )
        for index, item in enumerate(raw_chunks, start=1)
    ]

    await qdrant.upsert(chunks, vectors)
    print(
        f"Ingested {len(chunks)} chunks into "
        f"Qdrant collection '{settings.qdrant_collection}'."
    )


def _infer_topic(section: str, text: str) -> str:
    value = f"{section} {text}".lower()
    if "kubernetes" in value or any(
        token in value for token in ["pod", "deployment", "replicaset", "ingress", "service"]
    ):
        return "kubernetes"
    return "docker"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True)
    args = parser.parse_args()
    asyncio.run(ingest(args.pdf))


if __name__ == "__main__":
    main()
