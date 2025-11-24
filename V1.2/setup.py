# setup.py
import os
import sys
from cx_Freeze import setup, Executable

# 包含额外的文件
include_files = [
    "background_images",
    "Font",
    "output_images"
]

# 构建选项
build_exe_options = {
    "packages": [
        "os", "sys", "tkinter", "PIL", "threading", "time", 
        "keyboard", "psutil", "pyperclip", "win32clipboard", 
        "win32gui", "win32process", "io"
    ],
    "include_files": include_files,
    "excludes": ["test", "unittest", "email", "http", "urllib", "xml"],
    "optimize": 2,
}

# 基础设置
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # 隐藏控制台窗口

# 应用程序信息
setup(
    name="橘雪莉表情包生成器V1.2",
    version="1.2.0",
    description="一个功能强大的表情包生成工具，支持经典模式和监听模式",
    options={"build_exe": build_exe_options},
    executables=[
        Executable(
            "main.py",
            base=base,
            target_name="橘雪莉表情包生成器.exe",
            icon="icon.ico" if os.path.exists("icon.ico") else None
        )
    ]
)