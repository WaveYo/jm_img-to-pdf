import requests
import os
import logging
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

class JmClient:
    """增强版禁漫下载客户端"""
    
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.session = self._create_session()
        self.logger = logging.getLogger('jmcomic')

    def load_config(self, path):
        """加载配置文件"""
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def _create_session(self):
        """创建带重试机制的会话"""
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=3,
            pool_maxsize=100
        )
        session.mount('https://', adapter)
        return session

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, max=10),
        retry=retry_if_exception_type((requests.ConnectionError, requests.Timeout))
    )
    def fetch_album(self, album_id):
        """获取漫画数据（带错误处理）"""
        url = f"https://{self.config['client']['domain'][0]}/album/{album_id}"
        try:
            self.logger.info(f"开始获取漫画数据，album_id: {album_id}")
            response = self.session.get(
                url,
                headers=self._build_headers(),
                timeout=30
            )
            response.raise_for_status()
            return self._parse_response(response)  # 返回图片 URL 列表
        except requests.HTTPError as e:
            self._handle_http_error(e, album_id)
        except Exception as e:
            self.logger.error(f"未知错误: {str(e)}")
            raise

    def download_image(self, url, save_path):
        """下载图片到本地"""
        try:
            self.logger.info(f"开始下载图片: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            with open(save_path, 'wb') as f:
                f.write(response.content)
            self.logger.info(f"图片下载成功: {save_path}")
        except Exception as e:
            self.logger.error(f"图片下载失败: {str(e)}")
            raise

    def _build_headers(self):
        """构造请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': f'https://{self.config["client"]["domain"][0]}/'
        }

    def _parse_response(self, response):
        """解析响应数据"""
        # 这里添加实际解析逻辑，返回图片 URL 列表
        return ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]

    def _handle_http_error(self, error, album_id):
        """处理HTTP错误"""
        status_code = error.response.status_code
        error_map = {
            403: {
                'type': 'access_denied',
                'message': f'访问被拒绝（专辑ID: {album_id}）',
                'suggestion': '尝试更换代理IP或等待解除限制'
            },
            404: {
                'type': 'not_found',
                'message': '专辑不存在或已被删除'
            },
            429: {
                'type': 'rate_limit',
                'message': '请求过于频繁',
                'suggestion': '降低请求频率或添加延迟'
            }
        }
        
        if status_code in error_map:
            err_info = error_map[status_code]
            self.logger.warning(f"{status_code} 错误: {err_info['message']}")
            raise JmApiError(status_code, err_info)
        else:
            self.logger.error(f"未知HTTP错误: {status_code}")
            raise

class JmApiError(Exception):
    """自定义API异常"""
    
    def __init__(self, status_code, error_info):
        self.status_code = status_code
        self.error_type = error_info.get('type', 'unknown_error')
        self.message = error_info.get('message', '未知错误')
        self.suggestion = error_info.get('suggestion')