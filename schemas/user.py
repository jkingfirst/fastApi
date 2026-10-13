from pydantic import BaseModel,Field,EmailStr
from typing import Annotated

Username = Annotated[str,Field(...,description='用户名')]
Password = Annotated[str,Field(...,description='用户密码',min_length=6,max_length=30)]
#新增用户
class AddUserRequest(BaseModel):
    username:Username
    email:EmailStr = Field(...,description='用户邮箱')
    mobile:str = Field(...,max_length=20, description='手机号')
    password: Password
class DeleteUserRequest(BaseModel):
    userId:int=Field(...,description='用户ID')
class UserInfoResponse(BaseModel):
    username:str
    mobile:str
    email:str
    disabled:bool
#公共页码类
class CommonPaginationResponse(BaseModel):
    page:int
    size:int
class UserListResponse(CommonPaginationResponse):
    pass
