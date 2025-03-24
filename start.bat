@echo off
REM ������˿����������ű�
setlocal enabledelayedexpansion

REM ������Ŀ��Ŀ¼
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

REM ���Python����
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [����] δ�ҵ�Python�����������Ȱ�װPython 3.8+����ӵ�ϵͳPATH
    pause
    exit /b 1
)

REM ������⻷��
if not exist "venv\" (
    echo ���ڴ������⻷��...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [����] ���⻷������ʧ��
        pause
        exit /b 1
    )
)

REM �������⻷��
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [����] ���⻷������ʧ��
    pause
    exit /b 1
)

REM ��װ����
echo ���ڰ�װ����...
pip install -r requirements.txt --disable-pip-version-check
if %errorlevel% neq 0 (
    echo [����] ������װ���ִ��󣬳��Լ�������...
)

REM ����FastAPI����
echo ������������������...
uvicorn api.app:app --reload --port 5302 --host 0.0.0.0

REM ���ִ��ڴ򿪣�����ģʽ��
echo ��������رմ���...
pause >nul