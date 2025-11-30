import tkinter as tk
from tkinter import ttk, filedialog, colorchooser
import os
from PIL import Image, ImageTk

class UIBuilder:
    def __init__(self, app_instance):
        self.app = app_instance
        
    def setup_ui(self):
        """构建UI界面"""
        self.app.notebook = ttk.Notebook(self.app.root)
        self.app.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 经典模式
        self.app.classic_frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.app.classic_frame, text="经典模式")
        
        # 监听模式
        self.app.listener_frame = ttk.Frame(self.app.notebook)
        self.app.notebook.add(self.app.listener_frame, text="监听模式")

        self.setup_classic_mode()
        self.setup_listener_mode()

    def setup_classic_mode(self):
        """构建经典模式界面"""
        main_paned = tk.PanedWindow(self.app.classic_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧面板
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, width=400)

        # 文本输入区
        group_text = ttk.LabelFrame(left_frame, text="1. 输入文字")
        group_text.pack(fill=tk.X, pady=5)
        
        self.app.text_input = tk.Text(group_text, height=5, width=30)
        self.app.text_input.pack(fill=tk.X, padx=5, pady=5)
        self.app.text_input.bind('<KeyRelease>', self.app._on_input_change)

        # 外观设置区
        group_style = ttk.LabelFrame(left_frame, text="2. 样式设置")
        group_style.pack(fill=tk.X, pady=5)

        self.app.btn_color = tk.Button(group_style, text="点击修改文字颜色", bg="white", command=self.app._choose_color)
        self.app.btn_color.pack(fill=tk.X, padx=5, pady=5)

        frame_sliders = ttk.Frame(group_style)
        frame_sliders.pack(fill=tk.X, padx=5)
        
        ttk.Label(frame_sliders, text="最大字号:").grid(row=0, column=0, sticky='w')
        s1 = ttk.Scale(frame_sliders, from_=20, to=200, variable=self.app.var_font_size, command=self.app._on_input_change)
        s1.grid(row=0, column=1, sticky='ew')
        
        ttk.Checkbutton(frame_sliders, text="启用描边", variable=self.app.var_use_outline, command=self.app._on_input_change).grid(row=1, column=0, sticky='w')
        s2 = ttk.Scale(frame_sliders, from_=0, to=10, variable=self.app.var_outline_width, command=self.app._on_input_change)
        s2.grid(row=1, column=1, sticky='ew')

        # 资源选择区
        group_res = ttk.LabelFrame(left_frame, text="3. 资源选择")
        group_res.pack(fill=tk.X, pady=5)

        ttk.Label(group_res, text="背景图片:").pack(anchor='w', padx=5)
        self.app.combo_bg = ttk.Combobox(group_res, textvariable=self.app.var_bg_file, state="readonly")
        self.app.combo_bg.pack(fill=tk.X, padx=5, pady=2)
        self.app.combo_bg.bind("<<ComboboxSelected>>", self.app._on_input_change)
        
        btn_add_bg = ttk.Button(group_res, text="+ 添加新背景", command=self.app._add_background)
        btn_add_bg.pack(anchor='e', padx=5, pady=2)

        ttk.Label(group_res, text="字体文件:").pack(anchor='w', padx=5, pady=(10, 0))
        self.app.combo_font = ttk.Combobox(group_res, textvariable=self.app.var_font_file, state="readonly")
        self.app.combo_font.pack(fill=tk.X, padx=5, pady=2)
        self.app.combo_font.bind("<<ComboboxSelected>>", self.app._on_input_change)

        # 保存按钮
        self.app.btn_save = ttk.Button(left_frame, text="保存图片 (Save)", command=self.app._save_image)
        self.app.btn_save.pack(fill=tk.X, pady=20, ipady=10)

        # 右侧预览面板
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame)

        self.app.lbl_preview = ttk.Label(right_frame, text="预览区域", anchor="center", background="#e0e0e0")
        self.app.lbl_preview.pack(fill=tk.BOTH, expand=True)
        self.app.lbl_preview.bind('<Configure>', self.app._on_resize_preview)

    def setup_listener_mode(self):
        """构建监听模式界面"""
        main_paned = tk.PanedWindow(self.app.listener_frame, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True)

        # 左侧面板
        left_frame = ttk.Frame(main_paned)
        main_paned.add(left_frame, width=400)

        # 权限管理区域
        group_admin = ttk.LabelFrame(left_frame, text="0. 权限管理")
        group_admin.pack(fill=tk.X, pady=5)
        
        admin_frame = ttk.Frame(group_admin)
        admin_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.app.lbl_admin_status = ttk.Label(admin_frame, text="管理员权限: 检测中...")
        self.app.lbl_admin_status.pack(side=tk.LEFT, padx=5)
        
        self.app.btn_request_admin = ttk.Button(admin_frame, text="请求管理员权限", command=self.app._request_admin_privileges)
        self.app.btn_request_admin.pack(side=tk.RIGHT, padx=5)
        
        # 监听控制区
        group_control = ttk.LabelFrame(left_frame, text="1. 监听控制")
        group_control.pack(fill=tk.X, pady=5)
        
        control_frame = ttk.Frame(group_control)
        control_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.app.btn_listen = ttk.Button(control_frame, text="开始监听", command=self.app._toggle_listener)
        self.app.btn_listen.pack(side=tk.LEFT, padx=5)
        
        self.app.lbl_listen_status = ttk.Label(control_frame, text="监听未启动")
        self.app.lbl_listen_status.pack(side=tk.LEFT, padx=10)
        
        # 热键选择
        hotkey_frame = ttk.Frame(group_control)
        hotkey_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(hotkey_frame, text="热键选择:").pack(side=tk.LEFT)
        
        ttk.Radiobutton(hotkey_frame, text="Enter", variable=self.app.var_hotkey, 
                       value="enter", command=self.app._on_hotkey_change).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(hotkey_frame, text="Ctrl+Enter", variable=self.app.var_hotkey, 
                       value="ctrl+enter", command=self.app._on_hotkey_change).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(group_control, text="支持: 微信(wechat.exe/weixin.exe) 和 QQ(qq.exe/tim.exe)\n在聊天框输入文字后按热键自动生成并发送图片", 
                 justify=tk.LEFT).pack(fill=tk.X, padx=5, pady=5)

        # 样式设置区
        group_style = ttk.LabelFrame(left_frame, text="2. 样式设置")
        group_style.pack(fill=tk.X, pady=5)

        self.app.btn_color_listener = tk.Button(group_style, text="点击修改文字颜色", bg="white", command=self.app._choose_color)
        self.app.btn_color_listener.pack(fill=tk.X, padx=5, pady=5)

        frame_sliders = ttk.Frame(group_style)
        frame_sliders.pack(fill=tk.X, padx=5)
        
        ttk.Label(frame_sliders, text="最大字号:").grid(row=0, column=0, sticky='w')
        self.app.scale_font_listener = ttk.Scale(frame_sliders, from_=20, to=200, variable=self.app.var_font_size)
        self.app.scale_font_listener.grid(row=0, column=1, sticky='ew')
        self.app.scale_font_listener.configure(command=self._on_listener_resource_change)
        
        self.app.check_outline_listener = ttk.Checkbutton(frame_sliders, text="启用描边", variable=self.app.var_use_outline)
        self.app.check_outline_listener.grid(row=1, column=0, sticky='w')
        self.app.check_outline_listener.configure(command=self._on_listener_resource_change)
        
        self.app.scale_outline_listener = ttk.Scale(frame_sliders, from_=0, to=10, variable=self.app.var_outline_width)
        self.app.scale_outline_listener.grid(row=1, column=1, sticky='ew')
        self.app.scale_outline_listener.configure(command=self._on_listener_resource_change)

        # 资源选择区
        group_res = ttk.LabelFrame(left_frame, text="3. 资源选择")
        group_res.pack(fill=tk.X, pady=5)

        ttk.Label(group_res, text="背景图片:").pack(anchor='w', padx=5)
        self.app.combo_bg_listener = ttk.Combobox(group_res, textvariable=self.app.var_bg_file, state="readonly")
        self.app.combo_bg_listener.pack(fill=tk.X, padx=5, pady=2)
        self.app.combo_bg_listener.bind("<<ComboboxSelected>>", self._on_listener_resource_change)
        
        btn_add_bg = ttk.Button(group_res, text="+ 添加新背景", command=self.app._add_background)
        btn_add_bg.pack(anchor='e', padx=5, pady=2)

        ttk.Label(group_res, text="字体文件:").pack(anchor='w', padx=5, pady=(10, 0))
        self.app.combo_font_listener = ttk.Combobox(group_res, textvariable=self.app.var_font_file, state="readonly")
        self.app.combo_font_listener.pack(fill=tk.X, padx=5, pady=2)
        self.app.combo_font_listener.bind("<<ComboboxSelected>>", self._on_listener_resource_change)

        # 测试和调试按钮
        btn_frame = ttk.Frame(left_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        self.app.btn_test = ttk.Button(btn_frame, text="测试生成图片", command=self.app._test_generate)
        self.app.btn_test.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.app.btn_update_preview = ttk.Button(btn_frame, text="更新预览", command=self.app._update_listener_preview)
        self.app.btn_update_preview.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # 调试按钮
        debug_frame = ttk.Frame(left_frame)
        debug_frame.pack(fill=tk.X, pady=10)
        
        self.app.btn_debug_fonts = ttk.Button(debug_frame, text="调试字体", command=self.app._debug_fonts)
        self.app.btn_debug_fonts.pack(fill=tk.X, padx=5)

        # 右侧面板
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame)

        self.app.listener_right_notebook = ttk.Notebook(right_frame)
        self.app.listener_right_notebook.pack(fill=tk.BOTH, expand=True)

        # 日志选项卡
        log_frame = ttk.Frame(self.app.listener_right_notebook)
        self.app.listener_right_notebook.add(log_frame, text="运行日志")
        
        ttk.Label(log_frame, text="运行日志:").pack(anchor='w', padx=5, pady=5)
        
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.app.log_text = tk.Text(log_text_frame, height=20, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.app.log_text.yview)
        self.app.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.app.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # 预览选项卡
        preview_frame = ttk.Frame(self.app.listener_right_notebook)
        self.app.listener_right_notebook.add(preview_frame, text="渲染预览")
        
        self.app.lbl_preview_listener = ttk.Label(preview_frame, text="预览区域\n点击'更新预览'按钮生成预览", 
                                            anchor="center", background="#e0e0e0")
        self.app.lbl_preview_listener.pack(fill=tk.BOTH, expand=True)
        self.app.lbl_preview_listener.bind('<Configure>', self.app._on_resize_preview_listener)

    def _on_listener_resource_change(self, event=None):
        """监听模式资源变化时的处理"""
        self.app._on_listener_resource_change(event)