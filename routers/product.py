from fastapi import APIRouter,Depends,Header
from pydantic import BaseModel, Field
from typing import Annotated,Dict,Optional
from utils.paginationQuery import per_page_common
productRouter = APIRouter(
    prefix="/product",
    tags=["商品"],
)
@productRouter.get(
    '/list',
    operation_id='getProdCuts',
    summary='商品列表',
    description='获取系统所有商品'
)
def get_good_list(query:Dict=Depends(per_page_common),user_agent:Optional[str] = Header(None,convert_underscores=True),x_token:str = Header(None,convert_underscores=True)):
    return {
        'page':query['page'],
        'size':query['size'],
        user_agent:x_token,
        x_token:x_token,
    }