from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health/live")
async def liveness():
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness(request: Request):
    qdrant = request.app.state.qdrant
    ready = await qdrant.health()
    if not ready:
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "dependencies": {"qdrant": "unavailable"}},
        )
    return {"status": "ready", "dependencies": {"qdrant": "ok"}}
