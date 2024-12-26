@echo off
echo === 智能学习机器人启动脚本 ===
echo.

:: 检查Python是否安装
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    echo 您可以从 https://www.python.org/downloads/ 下载安装
    pause
    exit /b
)

:: 检查并创建虚拟环境
if not exist "venv" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate

:: 安装依赖
echo [信息] 正在检查并安装依赖...
pip install -r requirements.txt

:: 检查配置文件
if not exist "api_keys.json" (
    echo [信息] 未检测到API配置文件，正在创建...
    echo {"openai": "", "serper": ""} > api_keys.json
    echo [提示] 请在api_keys.json中配置您的API密钥
)

:: 启动机器人
echo [信息] 正在启动机器人...
echo.
python simple_bot.py

pause 