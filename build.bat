@echo off
chcp 65001 >nul
title Tachibana Sherry Generator - 构建脚本

echo ===============================================
echo   橘雪莉表情包生成器 - 优化构建脚本
echo   Tachibana Sherry Generator - Build Script
echo ===============================================

echo.
echo [1/5] 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo 错误: 未找到Python环境，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/5] 检查必要文件夹...
if not exist "background_images" (
    echo 创建background_images文件夹...
    mkdir background_images
    echo 请将900x900的背景图片放入background_images文件夹
)

if not exist "Font" (
    echo 创建Font文件夹...
    mkdir Font
    echo 请将字体文件(.ttf/.otf)放入Font文件夹
)

if not exist "output_images" (
    echo 创建output_images文件夹...
    mkdir output_images
)

echo.
echo [3/5] 安装依赖包...
echo 正在安装项目依赖...
pip install --upgrade pip
pip install pillow pynput pywin32 psutil pyperclip cx_Freeze

if %errorlevel% neq 0 (
    echo 错误: 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [4/5] 检查setup.py文件...
if not exist "setup.py" (
    echo 错误: setup.py文件不存在
    pause
    exit /b 1
)

echo.
echo [5/5] 开始编译为EXE文件...
echo 这可能需要几分钟，请耐心等待...
python setup.py build

if %errorlevel% neq 0 (
    echo 错误: 编译失败
    pause
    exit /b 1
)

echo.
echo ===============================================
echo           编译成功！
echo ===============================================
echo.
echo 生成的EXE文件位置:
echo   build\exe.win-*\TachibanaSherryGenerator.exe
echo.
echo 使用说明:
echo 1. 将EXE文件复制到任意位置
echo 2. 确保同目录下有Font文件夹（包含字体文件）
echo 3. 双击运行即可使用
echo.
echo 注意: 首次运行时可能需要安装VC++运行库
echo.
pause