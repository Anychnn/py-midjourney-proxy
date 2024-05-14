from pydoc import describe
from typing import Optional

from typing import List, Tuple, Set
from pydantic import BaseModel, Field

class ImagineRequest(BaseModel):
    # RELAX和FAST两种，默认为RELAX
    mode: Optional[str] = "RELAX"
    # 任务状态发生变化自动回调的地址
    notify_hook: Optional[str]
    # 用于参考的图片列表，可以传入base64或者url
    imgs: Optional[List[str]]
    prompt: str
    
class ImagineResponseData(BaseModel):
    # 任务ID
    task_id: str
    # 任务状态
    task_status: str
    # 图片地址
    image_url: Optional[str]
    
class ImagineResponse(BaseModel):
    status: int = Field(..., title="状态码", description="状态码")
    msg: str = Field(..., title="消息", description="消息")
    data: ImagineResponseData = Field(..., title="数据", description="数据")

class QueryImagineStatusRequest(BaseModel):
    task_id: str = Field(..., title="任务ID", description="任务ID")
    # 返回图片的格式,base64或者url
    # img_type: str = "base64"

class QueryImagineStatusResponseData(BaseModel):
    task_id: str = Field(..., title="任务ID", description="任务ID")
    task_status: str = Field(..., title="状态码", description="状态码")
    image_url: Optional[str]
    
    
class QueryImagineStatusResponse(BaseModel):
    status: int = Field(..., title="状态码", description="状态码")
    msg: str = Field(..., title="消息", description="消息")
    data: QueryImagineStatusResponseData = Field(..., title="数据", description="数据")
    
    
class UpscaleRequest(BaseModel):
    # 任务ID
    task_id: str
    # 缩放的索引
    # index: int
    # action_type: str
    mode: Optional[str]
    custom_id: str
    # 任务状态发生变化自动回调的地址
    notify_hook: Optional[str]
    
    
class QueryUpscaleStatusRequest(BaseModel):
    task_id: str = Field(..., title="任务ID", description="任务ID")
    
    
class QueryVariationStatusRequest(BaseModel):
    task_id: str = Field(..., title="任务ID", description="任务ID")
    
    
class ImageUploadRequest(BaseModel):
    bs64: str
    
    
class DescribeRequest(BaseModel):
    img: str

class BlendRequest(BaseModel):
    imgs: List[str]
    dimensions: Optional[str]
    
class ShortenRequest(BaseModel):
    prompt: str