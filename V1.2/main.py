import sys
import traceback
from memeapp import MemeApp

def handle_exception(exc_type, exc_value, exc_traceback):
    """全局异常处理"""
    if issubclass(exc_type, KeyboardInterrupt):
        print("\n程序被用户中断")
        sys.exit(0)
    else:
        print("未处理的异常:")
        traceback.print_exception(exc_type, exc_value, exc_traceback)

# 设置全局异常处理
sys.excepthook = handle_exception

# 主程序入口判断
if __name__ == "__main__":
    try:
        # 实例化应用
        app = MemeApp()
        # 运行应用
        app.run()
    except KeyboardInterrupt:
        print("\n程序已退出")
    except Exception as e:
        print(f"程序启动失败: {e}")
        input("按回车键退出...")