from typing import Optional
from pydantic import BaseModel,Field
class PairTokenResponse(BaseModel):
    token_type: str=Field(...,description='token类型')
    access_token: str=Field(...,description='OAuthorization授权')
    refresh_token:Optional[str]=Field(None,description='刷新token')
    expires_in:Optional[int]=Field(None,description='授权有效期')