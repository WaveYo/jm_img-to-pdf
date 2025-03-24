# /api/schemas.py

from pydantic import BaseModel
from typing import Optional

class ComicRequest(BaseModel):
    """漫画生成请求参数"""
    album_id: str
    retry_count: Optional[int] = 3
    proxy: Optional[str] = None  # 代理服务器地址

class ErrorResponse(BaseModel):
    """标准化错误响应"""
    error_type: str
    error_code: int
    message: str
    suggestion: Optional[str] = None

class TaskStatusResponse(BaseModel):
    """任务状态查询响应"""
    task_id: str
    status: str  # pending/processing/completed/failed
    progress: Optional[float] = None
    download_url: Optional[str] = None