import os
import tkinter as tk
from tkinter import ttk, messagebox
from services.keyboard_mgr import KeyboardListener
from services.clipboard_mgr import ClipboardManager
from services.process_mgr import ProcessManager

from core.generator import ImageGenerator

class ListenerTab(ttk.Frame):
    def __init__(self, parent, generator):
        super().__init__(parent)
        self.generator : ImageGenerator = generator
        
        # 初始化服务
        self.kb_service = KeyboardListener(self._on_hotkey)
        self.allowed_apps = ["wechat.exe", "weixin.exe", "qq.exe", "tim.exe"]
        
        self._init_vars()
        self._init_ui()
        self._load_resources()
        self._log("系统初始化完成，等待启动监听...")

    def _init_vars(self):
        """初始化绑定变量"""
        self.var_text_color = (255, 255, 255)
        self.var_font_size = tk.IntVar(value=100)
        self.var_use_outline = tk.BooleanVar(value=True)
        self.var_outline_width = tk.IntVar(value=3)
        self.var_bg_file = tk.StringVar()
        self.var_font_file = tk.StringVar()
        self.current_img = None
        self._debounce_job = None
        # 批量处理变量
        self.batch_bg_files = []
        self.var_batch_mode = tk.BooleanVar()

    def _init_ui(self):
        # 左右分栏：左边控制，右边日志
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        left = ttk.Frame(paned)
        paned.add(left, width=300)
        
        # 控制区
        grp_ctrl = ttk.LabelFrame(left, text="监听控制")
        grp_ctrl.pack(fill=tk.X, pady=5)
        
        self.btn_toggle = ttk.Button(grp_ctrl, text="启动监听 (Ctrl + Enter)", command=self._toggle_listener)
        self.btn_toggle.pack(fill=tk.X, padx=5, pady=5)
        self.lbl_status = ttk.Label(grp_ctrl, text="状态: 停止", foreground="red")
        self.lbl_status.pack(pady=5)
        
        # 批量处理选项
        grp_batch = ttk.LabelFrame(left, text="批量处理")
        grp_batch.pack(fill=tk.X, pady=5)
        
        ttk.Checkbutton(grp_batch, text="启用批量处理", variable=self.var_batch_mode).pack(anchor='w', padx=5, pady=2)
        
        self.btn_select_bgs = ttk.Button(grp_batch, text="选择批量背景", command=self._select_batch_backgrounds)
        self.btn_select_bgs.pack(fill=tk.X, padx=5, pady=2)
        
        self.lbl_selected_bgs = ttk.Label(grp_batch, text="已选择 0 个背景")
        self.lbl_selected_bgs.pack(fill=tk.X, padx=5, pady=2)
        
        # 样式区
        grp_style = ttk.LabelFrame(left, text="样式设置")
        grp_style.pack(fill=tk.X, pady=5)
        
        self.btn_color = tk.Button(grp_style, text="修改颜色", command=self._pick_color)
        self.btn_color.pack(fill=tk.X, padx=5, pady=5)
        
        f_slide = ttk.Frame(grp_style)
        f_slide.pack(fill=tk.X, padx=5)
        ttk.Scale(f_slide, from_=20, to=200, variable=self.var_font_size, command=lambda x: None).pack(fill=tk.X)
        ttk.Checkbutton(f_slide, text="描边", variable=self.var_use_outline).pack(anchor='w')
        
        # 资源区
        grp_res = ttk.LabelFrame(left, text="资源选择")
        grp_res.pack(fill=tk.X, pady=5)
        
        self.cb_bg = ttk.Combobox(grp_res, textvariable=self.var_bg_file, state="readonly")
        self.cb_bg.pack(fill=tk.X, padx=5)

        
        self.cb_font = ttk.Combobox(grp_res, textvariable=self.var_font_file, state="readonly")
        self.cb_font.pack(fill=tk.X, padx=5, pady=5)


        # 日志区
        right = ttk.Frame(paned)
        paned.add(right)
        self.txt_log = tk.Text(right, state="disabled")
        self.txt_log.pack(fill=tk.BOTH, expand=True)
    
    def _load_resources(self):
        """加载资源列表"""
        bgs = self.generator.get_files(self.generator.bg_folder, ('.png', '.jpg'))
        self.cb_bg['values'] = bgs
        if bgs: self.cb_bg.current(0)
        
        fonts = self.generator.get_files(self.generator.font_folder, ('.ttf', '.otf'))
        self.cb_font['values'] = fonts
        if fonts: self.cb_font.current(0)

    def _toggle_listener(self):
        """切换监听状态"""
        if self.kb_service.is_running:
            ok, msg = self.kb_service.stop()
            self.btn_toggle.config(text="启动监听 (Ctrl + Enter)")
            self.lbl_status.config(text="状态: 停止", foreground="red")
        else:
            ok, msg = self.kb_service.start()
            self.btn_toggle.config(text="停止监听")
            self.lbl_status.config(text="状态: 运行中", foreground="green")
        self._log(msg)

    def _pick_color(self):
        c = tk.colorchooser.askcolor(initialcolor=self.var_text_color)
        if c[0]: 
            self.var_text_color = tuple(map(int, c[0]))
            self.btn_color.config(bg=c[1])

    def _select_batch_backgrounds(self):
        """选择批量背景图片"""
        bgs = self.generator.get_files(self.generator.bg_folder, ('.png', '.jpg'))
        if not bgs:
            messagebox.showwarning("警告", "没有找到背景图片")
            return
            
        # 创建选择窗口
        selection_window = tk.Toplevel(self)
        selection_window.title("选择批量背景图片")
        selection_window.geometry("300x400")
        
        # 创建列表框和滚动条
        frame = ttk.Frame(selection_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE)
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        listbox.config(yscrollcommand=scrollbar.set)
        
        # 添加背景图片到列表框
        for bg in bgs:
            listbox.insert(tk.END, bg)
            
        # 如果之前已选择，则标记为选中
        for i, bg in enumerate(bgs):
            if bg in self.batch_bg_files:
                listbox.selection_set(i)
        
        def confirm_selection():
            selected_indices = listbox.curselection()
            self.batch_bg_files = [bgs[i] for i in selected_indices]
            self.lbl_selected_bgs.config(text=f"已选择 {len(self.batch_bg_files)} 个背景")
            selection_window.destroy()
        
        # 确认按钮
        btn_confirm = ttk.Button(selection_window, text="确认选择", command=confirm_selection)
        btn_confirm.pack(pady=10)

    def _on_hotkey(self):
        """核心业务流程：热键触发"""
        # 1. 检查当前窗口进程
        proc_name = ProcessManager.get_foreground_process_name()
        if proc_name not in self.allowed_apps:
            # self._log(f"忽略进程: {proc_name}") # 可选：太吵可以注释掉
            return

        self._log(f"检测到聊天窗口 ({proc_name})，开始处理...")
        
        # 2. 剪切文本
        text, old_clip = ClipboardManager.cut_text_via_hotkey()
        if not text.strip():
            self._log("未选中文本或文本为空")
            ClipboardManager.set_text(old_clip) # 恢复
            return

        self._log(f"捕获文本: {text[:10]}...")

        # 检查是否启用批量处理
        if self.var_batch_mode.get():
            # 批量处理模式
            self._process_batch(text)
        else:
            # 单张处理模式
            self._process_single(text)
        
        # 恢复旧剪贴板(如果是文本的话)
        ClipboardManager.set_text(old_clip)

    def _process_single(self, text):
        """处理单张图片"""
        settings = {
            'text': text,
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }
        img = self.generator.get_image(settings)

        if img:
            ok = ClipboardManager.set_image(img)
            if ok:
                ClipboardManager.paste_and_send()
                self._log("图片已发送")
            else:
                self._log("写入剪贴板失败")

    def _process_batch(self, text):
        """批量处理多张图片"""
        if not self.batch_bg_files:
            self._log("未选择背景图片，请先选择背景图片")
            return
            
        success_count = 0
        for i, bg_file in enumerate(self.batch_bg_files):
            settings = {
                'text': text,
                'text_color': self.var_text_color,
                'font_size': self.var_font_size.get(),
                'use_outline': self.var_use_outline.get(),
                'outline_width': self.var_outline_width.get(),
                'bg_path': os.path.join(self.generator.bg_folder, bg_file),
                'font_file': self.var_font_file.get()
            }
            img = self.generator.get_image(settings)

            if img:
                ok = ClipboardManager.set_image(img)
                if ok:
                    ClipboardManager.paste_and_send()
                    success_count += 1
                    self._log(f"第{i+1}张图片已发送")
                    # 添加短暂延迟避免发送过快
                    self.update()
                    self.after(500)
                else:
                    self._log(f"第{i+1}张图片写入剪贴板失败")
        
        self._log(f"批量处理完成，共发送 {success_count}/{len(self.batch_bg_files)} 张图片")

    def _log(self, msg):
        self.txt_log.config(state="normal")
        self.txt_log.insert(tk.END, msg + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.config(state="disabled")