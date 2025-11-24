@echo off
chcp 65001 >nul
title 构建 橘雪莉表情包生成器

echo ========================================
echo   橘雪莉表情包生成器 - 构建脚本
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

echo [信息] 检查依赖包...

:: 安装/升级必要的包
echo [信息] 安装/升级依赖包...
pip install --upgrade pip

pip install pillow
pip install keyboard
pip install psutil
pip install pyperclip
pip install pywin32
pip install cx-freeze

echo.
echo [信息] 开始构建应用程序...

:: 创建构建目录
if not exist "build" mkdir build
if not exist "dist" mkdir dist

:: 运行构建
python setup.py build

if errorlevel 1 (
    echo.
    echo [错误] 构建失败！
    pause
    exit /b 1
)

echo.
echo [成功] 构建完成！
echo.

:: 复制必要的文件到构建目录
echo [信息] 复制资源文件...
xcopy /Y /I "background_images" "build\exe.win-amd64-3.*\background_images\" >nul 2>&1
xcopy /Y /I "Font" "build\exe.win-amd64-3.*\Font\" >nul 2>&1

:: 创建输出目录
if not exist "build\exe.win-amd64-3.*\output_images" mkdir "build\exe.win-amd64-3.*\output_images"

echo.
echo ========================================
echo   构建完成！
echo ========================================
echo.
echo 可执行文件位置: build\exe.win-amd64-3.*\
echo.
echo 使用说明:
echo 1. 整个 build\exe.win-amd64-3.*\ 文件夹可以独立运行
echo 2. 可以将此文件夹打包分发给其他用户
echo 3. 确保文件夹内包含:
echo    - 橘雪莉表情包生成器.exe
echo    - background_images\ 文件夹
echo    - Font\ 文件夹
echo    - output_images\ 文件夹
echo.
pause