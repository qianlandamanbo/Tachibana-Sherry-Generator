@echo off
chcp 65001 >nul

echo 正在安装打包所需的依赖...
pip install pillow pynput pywin32 psutil pyperclip cx_Freeze

echo.
echo 正在检查必要文件夹...
if not exist "background_images" (
    echo 创建background_images文件夹...
    mkdir background_images
    echo 请将900x900的背景图片放入background_images文件夹
)

echo.
echo 正在准备setup.py文件...
echo 请确保当前目录下有setup.py文件，并且配置正确。
pause

echo.
echo 正在打包成EXE文件，这可能需要几分钟...
python setup.py build

echo.
echo 打包完成！生成的EXE文件在build文件夹中
echo 请将SourceHanSerifSC.otf或simhei.ttf字体文件与EXE文件放在同一目录下

pause