from fastapi import FastAPI,Request
from pydantic import BaseModel
from datetime import date
from scalar_fastapi import add_scalar_reference,Theme,get_scalar_api_reference
from fastapi.responses import HTMLResponse
from routers.authority import AuthorityRouter
from routers.user import userRouter
from routers.product import productRouter
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError
from core.exceptions import AppException
from fastapi.responses import JSONResponse
from core.errorCode import ErrorCode
from middleware.routerLogger import RouteLoggerMiddleware
from schemas.response import ValidationErrorResponse,COMMON_RESPONSES

# 导入数据模型
import models
import logging
# 配置logger打印日志
logging.basicConfig(level=logging.INFO)
app = FastAPI(
    title="用户管理系统 API",
    version="1.0.0",
    responses=COMMON_RESPONSES
)
# @app.get("/scalar", response_class=HTMLResponse)
# async def scalar_html():
#     return get_scalar_api_reference(
#         openapi_url=app.openapi_url,
#         authentication={
#             "preferredSecurityScheme": "OAuth2PasswordBearer",
#             "securitySchemes": {
#                 "OAuth2PasswordBearer": {
#                     "type": "oauth2",
#                     "flows": {
#                         "password": {
#                             "tokenUrl": "http://localhost:8000/authority/token",
#                             "scopes": {}
#                         }
#                     },
#                     "x-scalar-client-id": "your-client-id"
#                 }
#             }
#         }
#     )
add_scalar_reference(app, route="/scalar", theme=Theme.BLUE_PLANET)
#添加路由打印日志
app.add_middleware(RouteLoggerMiddleware)
#重写异常处理
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request:Request,exc: StarletteHTTPException):
    code = getattr(exc,'code',ErrorCode.UNKNOWN)
    message = getattr(exc,'message',str(exc.detail))
    return JSONResponse(
        status_code=exc.status_code,
        content={
            'code':int(code),
            'message':message,
            'data':None
        })
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,exc: RequestValidationError):
    # pydantic校验失败就统一返回错误
    status_code = ErrorCode.PARAM_ERROR.http_status
    errors = [
        {
            'field': '.'.join(str(part) for part in err['loc']),
            'message': err['msg'],
         } for err in exc.errors()
    ]
    print(f'-------{errors}')
    content = ValidationErrorResponse(data = errors)
    print(f'+++++++++{content.model_dump()}')
    return JSONResponse(
        status_code=status_code,
        content=content.model_dump()
    )
@app.exception_handler(AppException)
async def exception_handler(request: Request,exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": exc.err_code.code,
            "message":exc.err_code.message,
            "data": None,
        },
    )

# 添加路由到主程序
app.include_router(userRouter)
app.include_router(productRouter)
app.include_router(AuthorityRouter)
@app.get("/")
async def root():
    return {"message": "Hello World12"}
class User(BaseModel):
    id: int
    name: str='jking'
    # Option(date) 可选
    created_at: date|None
    departments:list[str]
external_user = {
    'id': 123,
    'name':'liming',
    'created_at':'2026-03-01',
    'departments':['研发部','大数据']
}


user = User(**external_user)
# print(type(external_user))
# print(external_user.get('id'))
# print(external_user['name'])
# print(external_user.items())
print(f'user:{user}')
print(user.model_dump())
print(type(user))
a = [1,2,3]
b = '.'.join (str(c*2) for c in a)
print(b)
