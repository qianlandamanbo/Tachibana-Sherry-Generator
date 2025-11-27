<<<<<<< HEAD
@echo off
chcp 65001 nul
title 微信图片生成器 - 安装和运行

echo ========================================
echo        橘雪莉表情包生成器 - 安装依赖
echo ========================================
echo.

echo 正在检查并安装升级所需的Python库...
echo 使用清华大学镜像源以提高下载速度。
echo 如果pip提示需要升级，可以按 Ctrl+C 终止，然后手动运行
echo pip install --upgrade pip -i httpspypi.tuna.tsinghua.edu.cnsimple
echo --------------------------------------------------

pip install --upgrade pip setuptools wheel -i httpspypi.tuna.tsinghua.edu.cnsimple --disable-pip-version-check --no-warn-script-location nul 2&1

pip install pillow pynput pywin32 psutil pyautogui --timeout 1000 --retries 3 -i httpspypi.tuna.tsinghua.edu.cnsimple --disable-pip-version-check --no-warn-script-location

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 依赖安装完成，正在启动橘雪莉表情包生成器 - 安装依赖
echo ==================...
    echo ========================================
    echo.
    Tachibana_Sherry_Generator.py
) else (
    echo.
    echo 
    echo  错误：安装依赖时出现问题，请检查网络连接或错误信息 
    echo 
    echo 错误码 %errorlevel%
    echo.
    echo 可能的原因：
    echo   1. 网络连接不稳定。
    echo   2. 没有以管理员权限运行此脚本。
    echo   3. Python 或 pip 未正确安装。
    echo.
    echo 尝试解决：
    echo   - 检查网络连接。
    echo   - 右键单击此 .bat 文件，选择 以管理员身份运行。
    echo   - 手动在命令行运行以下命令检查Python和pip
    echo     python --version
    echo     pip --version
    echo   - 手动尝试安装依赖
    echo     pip install pillow pynput pywin32 psutil pyautogui -i httpspypi.tuna.tsinghua.edu.cnsimple
    echo.
)

echo.
echo 脚本执行完毕。
=======
@echo off
chcp 65001 nul
title 微信图片生成器 - 安装和运行

echo ========================================
echo        橘雪莉表情包生成器 - 安装依赖
echo ========================================
echo.

echo 正在检查并安装升级所需的Python库...
echo 使用清华大学镜像源以提高下载速度。
echo 如果pip提示需要升级，可以按 Ctrl+C 终止，然后手动运行
echo pip install --upgrade pip -i httpspypi.tuna.tsinghua.edu.cnsimple
echo --------------------------------------------------

pip install --upgrade pip setuptools wheel -i httpspypi.tuna.tsinghua.edu.cnsimple --disable-pip-version-check --no-warn-script-location nul 2&1

pip install pillow pynput pywin32 psutil pyautogui --timeout 1000 --retries 3 -i httpspypi.tuna.tsinghua.edu.cnsimple --disable-pip-version-check --no-warn-script-location

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo 依赖安装完成，正在启动橘雪莉表情包生成器 - 安装依赖
echo ==================...
    echo ========================================
    echo.
    Tachibana_Sherry_Generator.py
) else (
    echo.
    echo 
    echo  错误：安装依赖时出现问题，请检查网络连接或错误信息 
    echo 
    echo 错误码 %errorlevel%
    echo.
    echo 可能的原因：
    echo   1. 网络连接不稳定。
    echo   2. 没有以管理员权限运行此脚本。
    echo   3. Python 或 pip 未正确安装。
    echo.
    echo 尝试解决：
    echo   - 检查网络连接。
    echo   - 右键单击此 .bat 文件，选择 以管理员身份运行。
    echo   - 手动在命令行运行以下命令检查Python和pip
    echo     python --version
    echo     pip --version
    echo   - 手动尝试安装依赖
    echo     pip install pillow pynput pywin32 psutil pyautogui -i httpspypi.tuna.tsinghua.edu.cnsimple
    echo.
)

echo.
echo 脚本执行完毕。
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
pause