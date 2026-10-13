
from core.exceptions import AppException
from core.errorCode import ErrorCode
from fastapi import APIRouter, Path,Depends,Query
from pydantic import BaseModel, Field
from typing import Annotated
from core.response import success_response

from core.auth import decode_token
from schemas.user import AddUserRequest, DeleteUserRequest
from models import AsyncSession
from models.user import User
from dependencies import get_session
from sqlalchemy import delete,select
from schemas.response import ApiResponse
from schemas.user import UserListResponse,UserInfoResponse
from utils.paginationQuery import per_page_common
from .authority import oauth2_scheme,get_user_by_id
userRouter = APIRouter(
    prefix="/user",
    tags=["用户"],
)

###
### 获取普通用户列表
###
@userRouter.get('/list',response_model=ApiResponse[UserListResponse])
async def get_user_list(query=Depends(per_page_common)):
    return ApiResponse(data={
        'page': query['page'],
        'size': query['size'],

    })
class LoginInfo(BaseModel):
    #... 代表字段为必填
    email: str = Field(...,min_length=8,max_length=20,description='用户邮箱')
    username: str = Field(...,description='用户名')
    password: str = Field(...,description='用户密码')
###
### 用户登录
###
@userRouter.post(
    '/login',
    operation_id='loginIn',
    summary="用户登录",
    description="用户登录"  # 详细说明=
)
async def login_in(data: LoginInfo):
    return{
        'email': data.email,
        'username': data.username,
    }
@userRouter.post(
    '/add',
    operation_id='addUser',
    summary='新增用户',
    description='注册新用户',
    response_model=ApiResponse[None],
)
async def add_user(payload:AddUserRequest,session:AsyncSession=Depends(get_session)):
    async with session.begin():
            user = User(**payload.model_dump())
            session.add(user)
    return {
        'data':None
    }
@userRouter.post('/delete',operation_id='deleteUser',summary='删除用户',description='删除用户')
async def delete_user(payload:DeleteUserRequest,session:AsyncSession=Depends(get_session)):
    async with session.begin():
        #先查找
        user = await session.get(User, payload.userId)
        if not user:
            print('user不存在')
        await session.execute(delete(User).where(payload.userId==User.id))
    return {
        'msg':'操作成功'
    }
###
### 获取用户详情
###
@userRouter.get(
    '/info',
    description='获取用户详情',
    operation_id='getUserInfo',
    response_model=ApiResponse[UserInfoResponse]
)
async def get_user(
        userId:int = Query(...,description='用户ID'),
        token: str = Depends(oauth2_scheme),
        session: AsyncSession = Depends(get_session)
):
    payload = decode_token(token,'access')
    if payload['user_id'] != userId:
        raise AppException(err_code=ErrorCode.FORBIDDEN)
    stmt = select(User).where(User.id == userId)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        raise AppException(err_code=ErrorCode.USER_NOT_FOUND)
    return success_response(data=user)
