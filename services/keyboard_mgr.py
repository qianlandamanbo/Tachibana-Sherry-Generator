import keyboard

class KeyboardListener:
    """负责管理键盘热键的注册和注销"""
    
    def __init__(self, callback, hotkey="ctrl+enter"):
        self.callback = callback
        self.hotkey = hotkey
        self.is_running = False
        self.hook = None

    def start(self):
        """启动监听"""
        if not self.is_running:
            try:
                # 注册热键，触发时调用回调函数
                # suppress=True 表示拦截按键，防止其他程序处理
                self.hook = keyboard.add_hotkey(self.hotkey, self.callback, suppress=True)
                self.is_running = True
                return True, f"监听已启动 (热键: {self.hotkey})"
            except Exception as e:
                return False, f"启动失败: {e}"
        return False, "监听已在运行"

    def stop(self):
        """停止监听"""
        if self.is_running:
            try:
                if self.hook:
                    keyboard.remove_hotkey(self.hook)
                self.is_running = False
                return True, "监听已停止"
            except Exception as e:
                return False, f"停止失败: {e}"
        return False, "监听未运行"