@echo off
REM 启动后端开发服务器脚本
setlocal enabledelayedexpansion

REM 设置项目根目录
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM 检查Python环境
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到Python解释器，请先安装Python 3.8+并添加到系统PATH
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv\" (
    echo 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 虚拟环境创建失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [错误] 虚拟环境激活失败
    pause
    exit /b 1
)

REM 安装依赖
echo 正在安装依赖...
pip install -r requirements.txt --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [警告] 依赖安装出现错误，尝试继续启动...
)

REM 启动FastAPI服务
echo 正在启动开发服务器...
uvicorn api.app:app --reload --port 5302 --host 0.0.0.0

REM 保持窗口打开（开发模式）
echo 按任意键关闭窗口...
pause >nul