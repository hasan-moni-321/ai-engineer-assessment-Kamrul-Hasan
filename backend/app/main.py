from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1 import api_router
from backend.app.clients.openai_client import OpenAIClient
from backend.app.clients.qdrant_client import QdrantRepository
from backend.app.clients.superhero_client import SuperheroClient
from backend.app.core.config import get_settings
from backend.app.core.exceptions import AppError
from backend.app.core.logging import configure_logging
from backend.app.rag.retriever import Retriever
from backend.app.services.answer_service import AnswerService
from backend.app.services.orchestrator import AskOrchestrator
from backend.app.services.rag_service import RAGService
from backend.app.services.router_service import RouterService
from backend.app.services.superhero_service import SuperheroService

settings = get_settings()
configure_logging(settings.log_level)
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    openai = OpenAIClient(settings)
    qdrant = QdrantRepository(settings)
    superhero_client = SuperheroClient(settings)

    retriever = Retriever(
        openai=openai,
        qdrant=qdrant,
        top_k=settings.rag_top_k,
        threshold=settings.rag_score_threshold,
    )

    orchestrator = AskOrchestrator(
        settings=settings,
        router=RouterService(openai),
        rag=RAGService(retriever, settings.rag_final_context_k),
        superhero=SuperheroService(superhero_client),
        answer=AnswerService(openai),
    )

    app.state.qdrant = qdrant
    app.state.orchestrator = orchestrator
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="Production-oriented modular RAG chatbot",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization", "X-Request-ID"],
)

app.include_router(api_router)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    request_id = request.headers.get("X-Request-ID", "generated-by-server")
    log.error(
        "application_error",
        request_id=request_id,
        code=exc.code,
        message=exc.message,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "request_id": request_id,
            "code": exc.code,
            "message": exc.message,
        },
    )


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "generated-by-server")
    log.exception("unhandled_error", request_id=request_id)
    return JSONResponse(
        status_code=500,
        content={
            "request_id": request_id,
            "code": "internal_error",
            "message": "An unexpected internal error occurred.",
        },
    )
