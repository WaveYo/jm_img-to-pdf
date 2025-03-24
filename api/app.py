# /api/app.py

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import logging
from image2pdf.image_to_pdf import all2PDF as image_to_pdf

import yaml

with open("config.yml", "r", encoding="utf8") as f:
    config = yaml.safe_load(f)

app = FastAPI()

# 配置日志记录
logging.basicConfig(filename='api.log', level=logging.INFO)

class ComicRequest(BaseModel):
    album_id: str
    retry_count: Optional[int] = 3  # 默认重试3次[2](@ref)

class ErrorResponse(BaseModel):
    error_code: int
    message: str
    detail: Optional[str] = None

@app.post("/generate-pdf", responses={
    202: {"description": "任务已接受"},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def generate_pdf(request: ComicRequest):
    try:
        # 调用原有下载逻辑（通过子进程隔离）
        result = subprocess.run(
            ['python', 'image2pdf/image_to_pdf.py', request.album_id],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 查找生成的PDF路径
        pdf_path = os.path.join(config['dir_rule']['base_dir'], f"{request.album_id}.pdf")
        if not os.path.exists(pdf_path):
            raise HTTPException(status_code=404, detail="PDF生成失败")
            
        return FileResponse(pdf_path)

    except subprocess.CalledProcessError as e:
        logging.error(f"子进程错误详情：\n返回码：{e.returncode}\n输出：{e.stdout}\n错误：{e.stderr}")
        # 解析错误类型
        if "403" in e.stderr:
            logging.warning(f"禁止访问资源: {request.album_id}")
            raise HTTPException(
                status_code=403,
                detail={
                    "error_code": 1001,
                    "message": "访问被服务器拒绝",
                    "solution": "检查IP限制或身份验证"
                }
            )
        elif "404" in e.stderr:
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": 1002,
                    "message": "资源不存在",
                    "solution": "验证漫画ID有效性"
                }
            )
        else:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": 9999,
                    "message": "内部服务器错误"
                }
            )

    except Exception as e:
        logging.error(f"未知错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 9999,
                "message": "系统内部错误"
            }
        )