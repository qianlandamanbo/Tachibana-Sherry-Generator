import ctypes
import sys
import tkinter.messagebox as messagebox

def is_admin():
    """检查当前是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def request_admin_privileges():
    """请求管理员权限并重新启动程序"""
    try:
        if is_admin():
            return True
            
        # 获取当前执行文件路径
        executable = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
        
        # 以管理员权限重新启动
        result = ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            executable, 
            params, 
            None, 
            1
        )
        
        if result > 32:
            # 成功启动管理员权限的程序，退出当前实例
            sys.exit(0)
        else:
            return False
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False