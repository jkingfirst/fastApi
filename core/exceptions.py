from .errorCode import ErrorCode
from fastapi import HTTPException,status
from typing import Optional

class AppException(HTTPException):
    def __init__(self,err_code:ErrorCode,message:Optional[str] = None):
        self.err_code = err_code
        self.message = message or err_code.message
        super().__init__(status_code=self.err_code.http_status, detail=self.message)
