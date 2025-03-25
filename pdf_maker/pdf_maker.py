from PIL import Image
from pathlib import Path

class PDFMaker:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)

    def _find_jpg_files(self, album_dir):
        """递归查找 JPG 文件"""
        return sorted(album_dir.rglob("*.jpg"))

    def make_pdf(self, album_id, output_dir):
        """将下载的图片合成为 PDF"""
        try:
            # 获取图片目录
            album_dir = self.base_dir / str(album_id)
            if not album_dir.exists():
                print(f"Image directory not found: {album_dir}")
                return False

            # 获取所有图片文件
            img_files = self._find_jpg_files(album_dir)
            if not img_files:
                print(f"No JPG files found in directory: {album_dir}")
                return False

            # 打开所有图片
            images = [Image.open(img) for img in img_files]

            # 创建输出目录
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # 保存为 PDF
            pdf_path = output_dir / f"{album_id}.pdf"
            images[0].save(pdf_path, save_all=True, append_images=images[1:], resolution=100.0)
            print(f"PDF successfully saved to: {pdf_path}")

            return True
        except Exception as e:
            print(f"Failed to create PDF: {str(e)}")
            return False