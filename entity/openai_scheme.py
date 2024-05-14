from pydoc import describe
from typing import Optional
from pydantic import BaseModel, Field


class CompletionRequest(BaseModel):
    model: str
    prompt: str
    temperature: float
    top_p: float
    stream: bool
    
class CompletionResponseData(BaseModel):
    text: str
    
    
class CompletionResponse(BaseModel):
    status: int=Field(..., description="状态")
    msg: str=Field(..., description="消息")
    data: CompletionResponseData=Field(..., description="数据")