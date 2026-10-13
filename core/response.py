from schemas.response import ApiResponse
from typing import TypeVar,Generic,Optional
from.errorCode import ErrorCode
T = TypeVar("T")

def success_response(data:T,message:str = '') -> ApiResponse[T]:
    return ApiResponse[T](
        code=ErrorCode.SUCCESS.code,
        data = data,
        message= message or ErrorCode.SUCCESS.message
    )

