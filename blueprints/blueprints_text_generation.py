from fastapi import APIRouter, UploadFile, Request
from entity.openai_scheme import (
    CompletionRequest,
    CompletionResponse,
)

text_router = APIRouter()


@text_router.post("/openai/completion",summary="openai文本生成")
async def completion(request: Request, completion_request: CompletionRequest):
    return {
        "status": 200,
        "msg": "ok",
    }
