import psutil
import win32gui
import win32process

class ProcessManager:
    """负责进程检测相关的操作"""

    @staticmethod
    def get_foreground_process_name():
        """
        Description:
            获取当前前台窗口所属的进程名称。
            Get the process name of the current foreground window.
        
        Returns:
            str: 进程名小写 (e.g., 'wechat.exe') 或 None
        """
        try:
            # 获取前台窗口句柄
            hwnd = win32gui.GetForegroundWindow()
            # 获取线程和进程ID
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            # 通过 PID 获取进程对象
            process = psutil.Process(pid)
            return process.name().lower()
        except Exception as e:
            print(f"Process Check Error: {e}")
            return None