@echo off
chcp 65001 >nul
cls
echo ===========================================================
echo 🎬 启动提示词扩展工具...
echo ===========================================================
echo.
echo 🎉 欢迎加入赵图图的知识星球 🎉
echo 知识星球有很多独家的小软件，星球号：12116758
echo 📌 QQ群：
echo - 小粉屋 628266084
echo - 小绿屋 903753035
echo - 小黑屋 950351015
echo ===========================================================

:: 创建虚拟环境（如果不存在）
if not exist venv (
    echo [🔧] 正在创建虚拟环境...
    python -m venv venv >nul 2>&1
    if %ERRORLEVEL% neq 0 (
        echo [❌] 创建虚拟环境失败，请检查 Python 是否正确安装！
        pause
        exit /b
    )
)

:: 激活虚拟环境
call venv\Scripts\activate >nul 2>&1

:: 更新 pip
echo [🔄] 正在更新 pip...
python -m pip install --upgrade pip >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] pip 更新失败，请检查网络连接！
    type install.log
    pause
    exit /b
)

:: 安装依赖
echo [🔄] 正在安装依赖...
pip install -r requirements.txt > install.log 2>&1
if %ERRORLEVEL% neq 0 (
    echo [❌] 依赖安装失败，错误日志如下：
    type install.log
    pause
    exit /b
)

:: 启动 Web 界面
echo [🚀] 启动 Web 界面...
start cmd /c "timeout /t 6 >nul && start http://127.0.0.1:7860"
python app.py

:: 保持窗口打开，防止关闭
pause
