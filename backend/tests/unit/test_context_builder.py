from backend.app.rag.context_builder import build_context
from backend.app.schemas.rag import RetrievedChunk


def test_context_builder_contains_sources():
    chunk = RetrievedChunk(
        # chunk_id="c1",
        # document_id="doc",
        chunk_id="c1",
        point_id="550e8400-e29b-41d4-a716-446655440000",
        document_id="doc",
        document_version="v1",
        source_name="docker_kubernetes_dataset.pdf",
        page=10,
        section="Pods",
        topic="kubernetes",
        content_type="technical_knowledge",
        text="A Pod is the smallest deployable unit in Kubernetes.",
        score=0.8,
    )

    context, sources = build_context([chunk], [], final_k=5)

    assert "Pods" in context
    assert sources[0]["source_type"] == "pdf"
    assert sources[0]["page"] == 10
