import jwt
from datetime import datetime, timedelta,timezone
from core.exceptions import AppException
from core.errorCode import ErrorCode
SECRET_KEY = "jwt_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7
#创建token
def create_token(data:dict,expires_delta:timedelta,token_type:str)->str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({
        "exp":expire,
        "token_type":token_type
    })
    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
#创建refresh_token
def create_refresh_token(user_id:str)->str:
    return create_token({"user_id":user_id},timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),'refresh')
#创建认证token
def create_access_token(user_id:str)->str:
   return create_token({'user_id':user_id},timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),'access')
#解码校验
def decode_token(token:str,token_type:str)->dict:
    try:
        pyload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AppException(err_code=ErrorCode.TOKEN_EXPIRES)
    except jwt.InvalidTokenError:
        raise AppException(err_code=ErrorCode.UNAUTHORIZED)
    if pyload['token_type'] != token_type:
        raise ValueError(f"token 类型错误,期望类型{token_type}")
    return pyload



