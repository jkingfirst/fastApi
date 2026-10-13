from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter,Depends,HTTPException,status
from schemas.auth import PairTokenResponse
from core.auth import decode_token, create_access_token, create_refresh_token
from models import AsyncSession
from models.user import User, verify_password
from dependencies import get_session
from sqlalchemy import select

from schemas.response import ApiResponse

AuthorityRouter = APIRouter(
    prefix="/authority",
    tags=["权限认证"],
)
'''Oauth2密码模式和fastapi OAuth2PasswordBearer实现jwt登录认证'''

'''
OAuth2PasswordBearer是接收url作为参数的一个类：客户端会向该URL发送用户名和密码作为参数，然后会得到一个token
'''
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authority/token")
@AuthorityRouter.get('/getToken',description='获取token',operation_id='getToken')
def get_token(token: str = Depends(oauth2_scheme)):
    return {
        'token': token,
    }
@AuthorityRouter.post(
    '/token',
    description='OAuthorization认证',
    operation_id='OAuth2Password',
    response_model=PairTokenResponse,
)
async def authorization_password(form_data: OAuth2PasswordRequestForm = Depends(),session: AsyncSession = Depends(get_session)):
        username = form_data.username
        user = await get_user_by_username(username,session)
        print(f'用户:{user}')
        if not user :
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='用户不存在'
            )
        if not verify_password(form_data.password,user.hashed_password):
            print('密码错误')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='密码错误'
            )
        return {
            'access_token': create_access_token(user.id),
            'refresh_token': create_refresh_token(user.id),
             'expires_in': 86400,
             'token_type': 'bearer'
        }

#用户名获取用户
async def get_user_by_username(username:str, session: AsyncSession ):
    async with session.begin():
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
#id获取用户
async def get_user_by_id(user_id:str,session:AsyncSession):
    async with session.begin():
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()
    pass
#获取当前用户
async def get_current_user(token:str=Depends(oauth2_scheme)):
    try:
        payload = decode_token(token, 'access')
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_id = int(payload['user_id'])
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='用户不存在'
        )
    return user


#获取当前激活激活的用户
def get_current_active_user(current_user:User=Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='inactive user'
        )
    return current_user
    pass