from fastapi.routing import APIRouter
from fastapi import Query
from fastapi.responses import StreamingResponse
from bpcl.services.generate_chat_response import generate_chat_responses
from typing import Optional

router = APIRouter(prefix="/chat_stream")


@router.post("/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    """ """
    return StreamingResponse(
        generate_chat_responses(message=message, checkpoint_id=checkpoint_id)
    )
