from pydoc import describe
from typing import Optional

from typing import List, Tuple, Set
from pydantic import BaseModel, Field

# 用户注册请求
class ShowQrcodeRequest(BaseModel):
    pass

# 二维码请求
class QrcodeResponseData(BaseModel):
    ticketUrl: str = Field(..., description="二维码地址")
    sceneStr: int = Field(..., description="二维码场景值")

# 二维码展示响应
class ShowQrcodeResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: QrcodeResponseData = Field(..., description="数据")


# 二维码状态请求
class QrcodeStatusRequest(BaseModel):
    sceneStr: str = Field(..., description="二维码场景值")


class QrcodeStatusData(BaseModel):
    status: int = Field(..., description="状态码")
    uid: int = Field(..., description="用户ID")

# 二维码状态响应
class QrcodeStatusResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: QrcodeStatusData = Field(..., description="数据")


# 用户秘钥生成
class SecretGenerateRequest(BaseModel):
    pass


# 用户秘钥生成响应
class SecretGenerateResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: str = Field(..., description="数据")
    
# 秘钥查询
class SecretQueryRequest(BaseModel):
    uid: int = Field(..., description="用户ID")

class SecretQueryData(BaseModel):
    secret: str = Field(..., description="秘钥")
    
# 秘钥查询响应
class SecretQueryResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: SecretQueryData = Field(..., description="数据")

# 支付二维码生成
class PayQrcodeGenerateRequest(BaseModel):
    uid: int = Field(..., description="用户ID")

class PayQrcodeGenerateData(BaseModel):
    qrcode_img_bs64: str = Field(..., description="二维码图片base64")
    price: int = Field(..., description="价格,单位分")
    order_id: str = Field(..., description="订单ID")
    

# 支付二维码生成响应
class PayQrcodeGenerateResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: str = Field(..., description="数据")

# 支付二维码状态查询
class PayQrcodeStatusRequest(BaseModel):
    order_id: str = Field(..., description="订单ID")

# 支付二维码状态查询响应
class PayQrcodeStatusData(BaseModel):
    status: int = Field(..., description="状态码")
    price: int = Field(..., description="价格,单位分")
    payed: bool = Field(..., description="是否支付")

# 支付二维码状态查询响应
class PayQrcodeStatusResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: PayQrcodeStatusData = Field(..., description="数据")
    



class RegisterRequest(BaseModel):
    account: str = Field(..., description="账号")
    password: str = Field(..., description="密码")
    

class LoginRequest(BaseModel):
    account: str = Field(..., description="账号")
    password: str = Field(..., description="密码")
    

class LoginResponseData(BaseModel):
    token: str = Field(..., description="token")
    

class LoginResponse(BaseModel):
    status: int = Field(..., description="状态码")
    msg: str = Field(..., description="消息")
    data: LoginResponseData = Field(..., description="数据")