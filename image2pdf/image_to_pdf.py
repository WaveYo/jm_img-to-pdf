import os
import time
import yaml
from PIL import Image
import logging

# 配置日志记录
logging.basicConfig(
    filename='image_to_pdf.log',  # 日志文件路径
    level=logging.INFO,  # 日志级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S'  # 时间格式
)

logger = logging.getLogger(__name__)

def all2PDF(input_folder, pdfpath, pdfname):
    """将指定文件夹中的图片转换为 PDF"""
    logger.info(f"开始转换文件夹为PDF: {input_folder}")
    start_time = time.time()
    zimulu = []  # 子目录（里面为图片）
    image = []  # 子目录图集
    sources = []  # pdf格式的图

    try:
        # 扫描输入文件夹，获取子目录
        with os.scandir(input_folder) as entries:
            for entry in entries:
                if entry.is_dir():
                    zimulu.append(int(entry.name))
        # 对数字进行排序
        zimulu.sort()

        # 遍历子目录，获取所有图片文件
        for i in zimulu:
            subfolder = os.path.join(input_folder, str(i))
            with os.scandir(subfolder) as entries:
                for entry in entries:
                    if entry.is_dir():
                        logger.warning(f"发现意外子目录: {entry.name}")
                    if entry.is_file():
                        image.append(os.path.join(subfolder, entry.name))

        # 打开第一张图片作为 PDF 的基础
        if image and "jpg" in image[0]:
            output = Image.open(image[0])
            image.pop(0)

        # 将其他图片添加到 PDF
        for file in image:
            if "jpg" in file:
                img_file = Image.open(file)
                if img_file.mode == "RGB":
                    img_file = img_file.convert("RGB")
                sources.append(img_file)

        # 保存 PDF
        pdf_file_path = os.path.join(pdfpath, pdfname)
        if not pdf_file_path.endswith(".pdf"):
            pdf_file_path += ".pdf"
        output.save(pdf_file_path, "pdf", save_all=True, append_images=sources)
        end_time = time.time()
        run_time = end_time - start_time
        logger.info(f"PDF生成成功，路径: {pdf_file_path}, 耗时: {run_time:.2f}秒")

    except Exception as e:
        logger.error(f"PDF生成失败: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        # 获取项目根目录的路径
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(project_root, "config.yml")

        # 加载配置文件
        with open(config_path, "r", encoding="utf8") as f:
            data = yaml.safe_load(f)
            path = os.path.join(project_root, data["dir_rule"]["base_dir"])

        # 遍历目录并生成 PDF
        with os.scandir(path) as entries:
            for entry in entries:
                if entry.is_dir():
                    pdf_path = os.path.join(path, entry.name + ".pdf")
                    if os.path.exists(pdf_path):
                        logger.info(f"文件已存在，跳过: {entry.name}")
                        continue
                    else:
                        logger.info(f"开始转换: {entry.name}")
                        all2PDF(os.path.join(path, entry.name), path, entry.name)
    except Exception as e:
        logger.error(f"程序运行失败: {str(e)}")