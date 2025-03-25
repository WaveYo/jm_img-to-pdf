import jmcomic
import yaml
from pathlib import Path

class JMDownloader:
    def __init__(self, config_path):
        self.config = self._load_config(config_path)
        self.base_dir = Path(self.config["dir_rule"]["base_dir"])

    def _load_config(self, config_path):
        """加载配置文件"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f'Failed to load config: {str(e)}')
            exit(1)

    def _create_option(self, config):
        """创建配置对象"""
        try:
            # 将配置写入临时文件
            temp_config_path = Path(__file__).parent.parent / 'temp_config.yml'
            with open(temp_config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(config, f)
            
            # 从临时文件创建配置对象
            option = jmcomic.create_option(str(temp_config_path))
            
            # 删除临时配置文件
            temp_config_path.unlink()
            
            return option
        except Exception as e:
            print(f'Failed to create option: {str(e)}')
            exit(1)

    def _check_local_exists(self, album_id):
        """检查本地是否已经存在本子"""
        album_dir = self.base_dir / str(album_id)
        if not album_dir.exists():
            return False
        
        # 检查是否存在 JPG 文件
        for item in album_dir.rglob("*.jpg"):
            if item.is_file():
                return True
        return False

    def download_album(self, album_id):
        """下载指定本子"""
        try:
            # 检查本地是否已经存在本子
            if self._check_local_exists(album_id):
                print(f"Album {album_id} already exists locally. Skipping download.")
                return True

            # 创建配置对象
            option = self._create_option(self.config)
            
            print(f'Starting download for album {album_id}...')
            jmcomic.download_album(album_id, option)
            print(f'Successfully downloaded to: {self.base_dir / str(album_id)}')
            
            return True
        except Exception as e:
            print(f'Download failed: {str(e)}')
            return False