import asyncio

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from recipe_agent.agent import run_agent

from ..models import RecommendRequest, RecommendResponse
from ..security import decode_token

router = APIRouter(tags=["recipes"])
_bearer = HTTPBearer()


def _get_current_user(creds: HTTPAuthorizationCredentials = Depends(_bearer)) -> str:
    email = decode_token(creds.credentials)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return email


@router.post("/recommend", response_model=RecommendResponse)
async def recommend(
    body: RecommendRequest,
    current_user: str = Depends(_get_current_user),
):
    try:
        result = await asyncio.to_thread(
            run_agent,
            "no additional preferences",
            body.ingredients or "pantry staples",
            body.dietary_restrictions,
        )
        return RecommendResponse(result=result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
