from fastapi import APIRouter, UploadFile, Request
from entity.user_scheme import (
    RegisterRequest,
    LoginRequest,
    LoginResponse
)
import datetime

from entity.models import (
    User,
    database
)

user_router = APIRouter()

# 检查字符串是邮箱还是手机号
def check_account_type(s):
    import re
    # 匹配手机号
    phone_pattern = re.compile(r'^1[3-9]\d{9}$')
    # 匹配邮箱
    email_pattern = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    if phone_pattern.match(s):
        return 'phone'
    elif email_pattern.match(s):
        return 'email'
    else:
        return 'invalid'

# 注册


@user_router.post("/register", summary="注册", tags=["user"],)
async def register(request: Request, body: RegisterRequest) -> dict:
    account = body.account
    password = body.password
    # 1.检查account是手机还是邮箱
    account_type = check_account_type(account)
    if account_type == 'invalid':
        return {"status": 400, "msg": "账号格式错误"}

    # 2.验证账号是否已存在
    user_query = User.select().where(
        User.phone == account if account_type == 'phone' else User.email == account)
    if user_query.exists():
        return {"status": 400, "msg": "账号已存在"}

    if account_type == 'phone':
        user = User(phone=account, password=password,
                    create_time=datetime.datetime.now(), update_time=datetime.datetime.now())
    elif account_type == 'email':
        user = User(email=account, password=password,
                    create_time=datetime.datetime.now(), update_time=datetime.datetime.now())
    user.save()
    
    return {
        "status": 200,
        "msg": "注册成功",
    }


# 用户登录
@user_router.post("/login", summary="用户登录", tags=["user"],)
def login(request: Request, body: LoginRequest) -> dict:
    account = body.account
    account_type = check_account_type(account)
    if account_type == 'invalid':
        return {"status": 400, "msg": "账号格式错误"}
    if account_type == 'phone':
        user = User.find_one(User.phone == account)
    elif account_type == 'email':
        user = User.find_one(User.email == account)
    
    if not user:
        return {"status": 400, "msg": "账号不存在"}
    if user.password != body.password:
        return {"status": 400, "msg": "密码错误"}
    
    return {
        "status": 200,
        "msg": "登录成功",
        "data": {
            "token": user.id,
            "user": user.dict()
        }
    }