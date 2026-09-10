from fastapi import APIRouter, Depends, Request

from backend.app.schemas.ask import AskRequest, AskResponse
from backend.app.services.orchestrator import AskOrchestrator

router = APIRouter(tags=["ask"])


def get_orchestrator(request: Request) -> AskOrchestrator:
    return request.app.state.orchestrator


@router.post("/api/v1/ask", response_model=AskResponse)
@router.post("/ask", response_model=AskResponse, include_in_schema=False)
async def ask(
    payload: AskRequest,
    orchestrator: AskOrchestrator = Depends(get_orchestrator),
):
    return await orchestrator.ask(payload.question)
