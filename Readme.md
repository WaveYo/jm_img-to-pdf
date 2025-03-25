本项目包含两个核心部分：
1. **jm_img-to-pdf**：一个后端服务，用于从 JMComic 下载图片并生成 PDF 文件。
2. **koishi-plugin-jmcomic-pdf**：一个基于 Koishi 框架的插件，用于通过与 `jm_img-to-pdf` 服务交互，获取并发送 JMComic 的 PDF 文件给用户。

### 您当前正在浏览：jm_img-to-pdf
点此前往 [koishi-plugin-jmcomic-pdf](https://github.com/WaveYo/koishi-plugin-jmcomic-pdf)


### 项目概述
`jm_img-to-pdf` 是一个后端服务，负责从 JMComic 下载图片并将其转换为 PDF 文件。它通过 Flask 提供 API 接口，支持下载指定 ID 的 JMComic 并生成 PDF。

### 项目结构
```
jm-v1                                 
├─ downloader                             
│  ├─ jm_downloader.py                
│  └─ __init__.py                     
├─ pdf_maker                             
│  ├─ pdf_maker.py                    
│  └─ __init__.py                     
├─ config.yml                         
├─ hect0x7-License                    
├─ jsconfig.json                      
├─ LICENSE                            
├─ main.py                            
├─ requirements.txt                   
└─ web_config.yml 
```

### 关键文件
- **`main.py`**：Flask 应用入口，提供 `/download` API 接口。
- **`web_config.yml`**：Flask 服务器配置，包括监听 IP、端口和域名。
- **`config.yml`**：JMComic 下载器配置，包括图片下载、缓存、线程等选项。

### 配置文件说明
#### `web_config.yml`
```yaml
server:
  host: 0.0.0.0       # 监听所有 IP
  port: 3502          # API 端口
  domain: localhost   # 域名或 IP，用于生成下载链接
```
- 修改 `host` 和 `port` 可以调整服务器的监听地址和端口。
- 修改 `domain` 可以调整生成下载链接时使用的域名或 IP。

#### `config.yml`
```yaml
download:
  image:
    suffix: .jpg  # 图片保存为jpg格式
    decode: true  # 是否解码图片
  dir_rule:
    base_dir: temp/img/  # 图片保存根目录
  client:
    retry_times: 5  # 请求重试次数
    timeout: 30     # 请求超时时间
  thread:
    count: 10      # 下载线程数
    enable: true   # 是否启用多线程
  cache:
    enable: false  # 是否启用缓存
log: true          # 是否启用日志
client:
  impl: html       # 客户端实现类（html 或 api）
  domain:
    - 18comic.vip  # 支持的域名
    - 18comic.org
    - jm-comic.org
    - jm-comic2.cc
```
- `download.dir_rule.base_dir`：设置图片下载的根目录。
- `client.domain`：设置 JMComic 支持的域名，可以添加或修改域名列表。
- `thread.count`：调整下载线程数以优化性能。

### 运行方式
1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
2. 启动 Flask 服务器：
   ```bash
   python main.py
   ```
3. 服务默认运行在 `http://localhost:3502`。

---

通过以上配置和说明，您可以轻松使用 `koishi-plugin-jmcomic-pdf` 和 `jm_img-to-pdf` 下载并发送 JMComic 的 PDF 文件。