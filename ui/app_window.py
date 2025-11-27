import tkinter as tk
from tkinter import ttk
from core.generator import ImageGenerator
from ui.classic_tab import ClassicTab
from ui.listener_tab import ListenerTab

class AppWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("橘雪莉表情包生成器")
        self.root.geometry("1000x700")

        # 初始化核心
        self.generator = ImageGenerator()

        # 初始化 Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 加载界面
        self.tab_classic = ClassicTab(self.notebook, self.generator)
        self.tab_listener = ListenerTab(self.notebook, self.generator)

        self.notebook.add(self.tab_classic, text="经典模式")
        self.notebook.add(self.tab_listener, text="监听模式")

        # 关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _on_close(self):
        # 确保退出时停止监听，释放钩子
        if hasattr(self.tab_listener, 'kb_service'):
            self.tab_listener.kb_service.stop()
        self.root.destroy()

    def run(self):
        self.root.mainloop()