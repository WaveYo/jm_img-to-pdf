from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional
import subprocess
import os
import logging
import yaml
import requests
from jmcomic import JmApiClient  # 导入 JM 客户端

# 配置日志记录
logging.basicConfig(
    filename='api.log',  # 日志文件路径
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式
)

# 定义 FastAPI 应用
app = FastAPI()

# 加载配置文件
with open("config.yml", "r", encoding="utf8") as f:
    config = yaml.safe_load(f)

logger = logging.getLogger(__name__)

class Postman:
    """自定义 Postman 类，兼容 JmApiClient 的要求"""
    def __init__(self):
        self.session = requests.Session()

    def get_meta_data(self, url, headers=None):
        """获取 URL 的元数据"""
        logger.info(f"调用 get_meta_data() 方法，参数: url={url}, headers={headers}")
        response = self.session.head(url, headers=headers)
        return {
            'content_length': response.headers.get('Content-Length'),
            'content_type': response.headers.get('Content-Type')
        }

    def send_request(self, url, method='GET', **kwargs):
        """发送 HTTP 请求"""
        return self.session.request(method, url, **kwargs)

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

@app.post("/generate-pdf", response_model=SuccessResponse, responses={
    200: {"model": SuccessResponse},
    400: {"model": ErrorResponse},
    403: {"model": ErrorResponse},
    404: {"model": ErrorResponse},
    500: {"model": ErrorResponse}
})
async def generate_pdf(request: ComicRequest):
    logger.info(f"收到请求，album_id: {request.album_id}")
    try:
        # 动态构建路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        temp_dir = os.path.join(project_root, config['dir_rule']['base_dir'], request.album_id)
        pdf_path = os.path.join(project_root, config['dir_rule']['base_dir'], f"{request.album_id}.pdf")

        # 创建临时目录
        os.makedirs(temp_dir, exist_ok=True)

        # 从 JM 服务器抓取数据
        domain_list = config['client']['domain_list']  # 从配置中读取域名列表
        postman = Postman()  # 使用自定义 Postman 类
        client = JmApiClient(domain_list=domain_list, postman=postman)  # 初始化 JmApiClient
        image_urls = client.fetch_album(request.album_id)  # 获取图片 URL 列表

        # 下载图片
        for index, url in enumerate(image_urls):
            image_path = os.path.join(temp_dir, f"{index + 1}.jpg")
            headers = {'User-Agent': 'Mozilla/5.0'}  # 自定义请求头
            meta_data = postman.get_meta_data(url, headers)
            logger.info(f"下载图片成功: {image_path}")

        # 合成 PDF
        subprocess.run(
            ['python', 'image2pdf/image_to_pdf.py', request.album_id],
            capture_output=True,
            text=True,
            check=True
        )

        # 检查生成的 PDF 文件
        if not os.path.exists(pdf_path):
            logger.error(f"PDF生成失败，路径不存在: {pdf_path}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": 1002,
                    "message": "资源不存在",
                    "solution": "验证漫画ID有效性"
                }
            )
        
        # 返回成功响应
        logger.info(f"PDF生成成功，路径: {pdf_path}")
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "PDF生成成功",
                "data": {
                    "pdf_path": pdf_path,
                    "下载URL": f"http://127.0.0.1:5302/download/{request.album_id}.pdf"
                }
            }
        )

    except subprocess.CalledProcessError as e:
        logger.error(f"子进程错误详情：\n返回码：{e.returncode}\n输出：{e.stdout}\n错误：{e.stderr}")
        if "403" in e.stderr:
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
        logger.error(f"未知错误: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 9999,
                "message": "系统内部错误"
            }
        )

@app.get("/download/{filename}")
async def download_pdf(filename: str):
    """下载生成的 PDF 文件"""
    try:
        # 动态构建 PDF 路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        pdf_path = os.path.join(project_root, config['dir_rule']['base_dir'], filename)

        # 检查文件是否存在
        if not os.path.exists(pdf_path):
            logger.error(f"文件不存在: {pdf_path}")
            raise HTTPException(
                status_code=404,
                detail={
                    "error_code": 1002,
                    "message": "文件不存在",
                    "solution": "验证文件名是否正确"
                }
            )
        
        # 返回文件响应
        logger.info(f"文件下载成功，路径: {pdf_path}")
        return FileResponse(pdf_path, filename=filename)

    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": 9999,
                "message": "系统内部错误"
            }
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5302)