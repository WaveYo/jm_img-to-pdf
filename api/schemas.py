from pydantic import BaseModel
from typing import Optional

class ComicRequest(BaseModel):
    """漫画生成请求参数"""
    album_id: str
    retry_count: Optional[int] = 3

class SuccessResponse(BaseModel):
    """成功响应"""
    status: str = "success"
    message: str
    data: dict

class ErrorResponse(BaseModel):
    """错误响应"""
    status: str = "error"
    error_code: int
    message: str
    solution: Optional[str] = None