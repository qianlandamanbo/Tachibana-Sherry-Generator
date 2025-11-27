#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tachibana Sherry Generator Setup Script
橘雪莉表情包生成器 - 打包配置
"""

import sys
import os
from cx_Freeze import setup, Executable

# 项目基本信息
project_name = "tachibana-sherry-generator"
version = "1.2"
description = "Tachibana Sherry Meme Generator - 橘雪莉表情包生成器"
author = "Tachibana Sherry Generator"

# 包含的文件和文件夹
include_files = [
    "background_images/",
    "Font/", 
    "output_images/",
    "images/",
    "comments/",
    "utils/",
]

# 排除的模块（减少打包体积）
excludes = [
    "test", "unittest", "email", "xml", "pydoc", "distutils",
    "setuptools", "pip", "wheel", "tkinter.test", "numpy",
    "scipy", "matplotlib", "pandas", "sqlite3", "ssl",
    "http", "urllib", "xmlrpc", "multiprocessing",
]

# 包含的包
packages = [
    "tkinter", "PIL", "os", "sys", "time", "threading",
    "utils", "comments"
]

# 构建选项
build_exe_options = {
    "packages": packages,
    "excludes": excludes,
    "include_files": include_files,
    "optimize": 2,
    "include_msvcr": True,  # 包含VC运行库
    "silent": True,
}

# 可执行文件配置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 不显示控制台窗口

# 主程序入口
main_executable = Executable(
    script="main.py",
    base=base,
    target_name="TachibanaSherryGenerator.exe",
    icon="images/show.png" if os.path.exists("images/show.png") else None,
    copyright="Copyright (C) 2024 Tachibana Sherry Generator",
    trademarks="Tachibana Sherry Generator",
)

setup(
    name=project_name,
    version=version,
    description=description,
    author=author,
    options={"build_exe": build_exe_options},
    executables=[main_executable],
)