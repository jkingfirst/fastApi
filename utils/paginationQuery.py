

from fastapi import Query
from typing import Annotated

# 依赖注入，公共的方法复用
def per_page_common(page: Annotated[int,Query(...,ge=1,description='页码')],size: Annotated[int,Query(...,ge=1,le=100,description='每页查询数目')]):
    return {
        'page':page,
        'size':size,
    }