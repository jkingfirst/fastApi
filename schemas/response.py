from typing import TypeVar,Generic,Optional
from pydantic import BaseModel,Field
from core.errorCode import ErrorCode
T = TypeVar('T')
class ApiResponse(BaseModel, Generic[T]):
    code: int = Field(ErrorCode.SUCCESS.code, description="业务状态码，200 表示成功")
    data: Optional[T] = Field(None, description="业务数据")
    message: str = Field("success", description="提示信息")

class ValidationErrorItem(BaseModel):
    field: str
    message: str
class ValidationErrorResponse(ApiResponse[list[ValidationErrorItem]]):
    code: int = ErrorCode.PARAM_ERROR.code
    data: list[ValidationErrorItem] = Field(default_factory=list)
    message: str = ErrorCode.PARAM_ERROR.message
COMMON_RESPONSES = {
    422: {
        "model": ValidationErrorResponse,
        "description": "请求参数校验失败",
    }
}

