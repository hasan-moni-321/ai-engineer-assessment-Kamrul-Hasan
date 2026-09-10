import time
from uuid import uuid4

import structlog

from backend.app.core.config import Settings
from backend.app.core.exceptions import NoGroundedContextError
from backend.app.schemas.ask import AskMetadata, AskResponse
from backend.app.schemas.common import RouteInfo, Source
from backend.app.services.answer_service import AnswerService
from backend.app.services.rag_service import RAGService
from backend.app.services.router_service import RouterService
from backend.app.services.superhero_service import SuperheroService
from backend.app.rag.context_builder import build_context

log = structlog.get_logger()


class AskOrchestrator:
    def __init__(
        self,
        settings: Settings,
        router: RouterService,
        rag: RAGService,
        superhero: SuperheroService,
        answer: AnswerService,
    ):
        self.settings = settings
        self.router = router
        self.rag = rag
        self.superhero = superhero
        self.answer = answer

    async def ask(self, question: str) -> AskResponse:
        request_id = str(uuid4())
        started = time.perf_counter()

        route_started = time.perf_counter()
        decision = await self.router.route(question)
        router_latency = int((time.perf_counter() - route_started) * 1000)

        rag_chunks = []
        superheroes = []

        retrieval_started = time.perf_counter()

        if decision.route in ("rag", "both"):
            rag_query = decision.rag_query or question
            rag_chunks = await self.rag.retrieve(rag_query)

        if decision.route in ("superhero", "both"):
            hero_query = decision.superhero_query or question
            superheroes = await self.superhero.search(hero_query)

        retrieval_latency = int((time.perf_counter() - retrieval_started) * 1000)

        if decision.route == "rag" and not rag_chunks:
            raise NoGroundedContextError(
                "No sufficiently relevant PDF evidence was found for this question."
            )

        if decision.route == "superhero" and not superheroes:
            raise NoGroundedContextError(
                "No matching superhero information was found from the Superhero API."
            )

        if decision.route == "both" and not rag_chunks and not superheroes:
            raise NoGroundedContextError(
                "Neither source returned sufficiently relevant information."
            )

        context, raw_sources = build_context(
            chunks=rag_chunks,
            superheroes=superheroes,
            final_k=self.settings.rag_final_context_k,
        )

        answer_started = time.perf_counter()
        answer = await self.answer.generate(question, context)
        answer_latency = int((time.perf_counter() - answer_started) * 1000)

        sources = [Source(**item) for item in raw_sources]
        total_latency = int((time.perf_counter() - started) * 1000)

        log.info(
            "ask_completed",
            request_id=request_id,
            route=decision.route,
            confidence=decision.confidence,
            retrieved_chunks=len(rag_chunks),
            superhero_results=len(superheroes),
            latency_ms=total_latency,
        )

        return AskResponse(
            request_id=request_id,
            answer=answer,
            route=RouteInfo(
                type=decision.route,
                confidence=decision.confidence,
            ),
            sources=sources,
            metadata=AskMetadata(
                retrieved_chunks=len(rag_chunks),
                latency_ms=total_latency,
                router_latency_ms=router_latency,
                retrieval_latency_ms=retrieval_latency,
                answer_latency_ms=answer_latency,
            ),
        )
