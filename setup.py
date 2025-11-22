from cx_Freeze import setup, Executable

# 基本信息
executables = [Executable("Tachibana_Sherry_Generator.py")]

# 设置
setup(
    name="橘雪莉表情包生成器",
    version="1.0",
    description="シェリーちゃん可愛い大好き！",
    executables=executables,
)