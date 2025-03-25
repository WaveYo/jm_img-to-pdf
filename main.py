from flask import Flask, jsonify, send_file, request
import yaml
from pathlib import Path
from downloader.jm_downloader import JMDownloader
from pdf_maker.pdf_maker import PDFMaker

# 加载 Web 配置
def load_web_config():
    config_path = Path(__file__).parent / 'web_config.yml'
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f'Failed to load web config: {str(e)}')
        exit(1)

# 初始化 Flask 应用
app = Flask(__name__)
web_config = load_web_config()

# 初始化下载器和 PDF 合成器
jm_config_path = Path(__file__).parent / 'config.yml'
downloader = JMDownloader(jm_config_path)
pdf_maker = PDFMaker(base_dir=Path("temp/img"))

@app.route('/download', methods=['POST'])
def download_and_make_pdf():
    try:
        # 获取前端发送的 ID
        data = request.json
        album_id = data.get('id')
        if not album_id:
            return jsonify({"error": "Missing 'id' parameter"}), 400

        # 下载本子
        if not downloader.download_album(album_id):
            return jsonify({"error": "Failed to download album"}), 500

        # 合成 PDF
        pdf_path = Path("temp/pdf") / f"{album_id}.pdf"
        if not pdf_maker.make_pdf(album_id, output_dir=Path("temp/pdf")):
            return jsonify({"error": "Failed to create PDF"}), 500

        # 生成下载链接
        domain = web_config['server']['domain']
        port = web_config['server']['port']
        download_url = f"http://{domain}:{port}/download/{album_id}.pdf"

        # 返回结果
        return jsonify({
            "message": "PDF created successfully",
            "download_url": download_url,
            "pdf_path": str(pdf_path)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download_pdf(filename):
    try:
        # 返回 PDF 文件
        pdf_path = Path("temp/pdf") / filename
        if not pdf_path.exists():
            return jsonify({"error": "File not found"}), 404
        return send_file(pdf_path, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # 启动 Web 服务器
    host = web_config['server']['host']
    port = web_config['server']['port']
    app.run(host=host, port=port, debug=True)  # 启用调试模式