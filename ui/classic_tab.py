import os
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk

class ClassicTab(ttk.Frame):
    def __init__(self, parent, generator):
        super().__init__(parent)
        self.generator = generator # 注入 Core 层的生成器
        self._init_vars()
        self._setup_ui()
        self._load_resources()
        self._trigger_preview() # 初始预览

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

    def _setup_ui(self):
        """构建经典模式的界面布局"""
        # 使用 PanedWindow 左右分栏
        paned = tk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        left = ttk.Frame(paned)
        paned.add(left, width=400)
        
        # --- 1. 输入区 ---
        grp_input = ttk.LabelFrame(left, text="1. 输入文字")
        grp_input.pack(fill=tk.X, pady=5)
        self.txt_input = tk.Text(grp_input, height=5, width=30)
        self.txt_input.pack(fill=tk.X, padx=5, pady=5)
        self.txt_input.bind('<KeyRelease>', self._on_change)

        # --- 2. 样式区 ---
        grp_style = ttk.LabelFrame(left, text="2. 样式设置")
        grp_style.pack(fill=tk.X, pady=5)
        
        self.btn_color = tk.Button(grp_style, text="修改颜色", command=self._pick_color)
        self.btn_color.pack(fill=tk.X, padx=5, pady=5)
        
        f_slide = ttk.Frame(grp_style)
        f_slide.pack(fill=tk.X, padx=5)
        ttk.Scale(f_slide, from_=20, to=200, variable=self.var_font_size, command=self._on_change).pack(fill=tk.X)
        ttk.Checkbutton(f_slide, text="描边", variable=self.var_use_outline, command=self._on_change).pack(anchor='w')
        
        # --- 3. 资源区 ---
        grp_res = ttk.LabelFrame(left, text="3. 资源选择")
        grp_res.pack(fill=tk.X, pady=5)
        
        self.cb_bg = ttk.Combobox(grp_res, textvariable=self.var_bg_file, state="readonly")
        self.cb_bg.pack(fill=tk.X, padx=5)
        self.cb_bg.bind("<<ComboboxSelected>>", self._on_change)
        
        self.cb_font = ttk.Combobox(grp_res, textvariable=self.var_font_file, state="readonly")
        self.cb_font.pack(fill=tk.X, padx=5, pady=5)
        self.cb_font.bind("<<ComboboxSelected>>", self._on_change)

        # --- 4. 批量处理区 ---
        grp_batch = ttk.LabelFrame(left, text="4. 批量处理")
        grp_batch.pack(fill=tk.X, pady=5)
        
        self.btn_select_bgs = ttk.Button(grp_batch, text="选择批量背景", command=self._select_batch_backgrounds)
        self.btn_select_bgs.pack(fill=tk.X, padx=5, pady=2)
        
        self.lbl_selected_bgs = ttk.Label(grp_batch, text="已选择 0 个背景")
        self.lbl_selected_bgs.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_generate_batch = ttk.Button(grp_batch, text="批量生成图片", command=self._generate_batch_images)
        self.btn_generate_batch.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(left, text="保存图片", command=self._save_image).pack(fill=tk.X, pady=20)

        # --- 右侧预览 ---
        right = ttk.Frame(paned)
        paned.add(right)
        self.lbl_preview = ttk.Label(right, text="预览区域", anchor="center", background="#ccc")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True)
        self.lbl_preview.bind('<Configure>', self._on_resize)

    def _load_resources(self):
        """加载资源列表"""
        bgs = self.generator.get_files(self.generator.bg_folder, ('.png', '.jpg'))
        self.cb_bg['values'] = bgs
        if bgs: self.cb_bg.current(0)
        
        fonts = self.generator.get_files(self.generator.font_folder, ('.ttf', '.otf'))
        self.cb_font['values'] = fonts
        if fonts: self.cb_font.current(0)

    def _on_change(self, event=None):
        """防抖更新"""
        if self._debounce_job: self.after_cancel(self._debounce_job)
        self._debounce_job = self.after(300, self._trigger_preview)

    def _trigger_preview(self):
        """收集参数并生成图片"""
        settings = {
            'text': self.txt_input.get("1.0", tk.END).strip(),
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }
        # 直接在主线程简单调用(量不大)，或者如果你想也可以用 Thread
        img = self.generator.get_image(settings)
        self._update_preview_ui(img)

    def _update_preview_ui(self, img):
        self.current_img = img
        # 简单缩放逻辑
        w, h = self.lbl_preview.winfo_width(), self.lbl_preview.winfo_height()
        if w < 10: return
        ratio = min(w/900, h/900)
        new_size = (int(900*ratio), int(900*ratio))
        try:
            preview = img.resize(new_size, Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(preview)
            self.lbl_preview.config(image=tk_img, text="")
            self.lbl_preview.image = tk_img
        except: pass

    def _on_resize(self, event):
        if self.current_img: self._update_preview_ui(self.current_img)

    def _pick_color(self):
        c = colorchooser.askcolor(initialcolor=self.var_text_color)
        if c[0]: 
            self.var_text_color = tuple(map(int, c[0]))
            self.btn_color.config(bg=c[1])
            self._trigger_preview()

    def _save_image(self):
        if not self.current_img: return
        path = os.path.join("output_images", f"{time.strftime('%Y%m%d%H%M%S')}.png")
        self.current_img.save(path)
        messagebox.showinfo("保存成功", path)

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

    def _generate_batch_images(self):
        """批量生成图片"""
        if not self.batch_bg_files:
            messagebox.showwarning("警告", "请先选择背景图片")
            return
            
        text = self.txt_input.get("1.0", tk.END).strip()
        if not text:
            messagebox.showwarning("警告", "请输入文字")
            return
            
        # 创建输出目录
        output_dir = "output_images"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # 批量生成图片
        generated_count = 0
        for bg_file in self.batch_bg_files:
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
                timestamp = time.strftime('%Y%m%d%H%M%S')
                filename = f"{timestamp}_{bg_file.split('.')[0]}.png"
                path = os.path.join(output_dir, filename)
                img.save(path)
                generated_count += 1
        
        messagebox.showinfo("批量生成完成", f"已生成 {generated_count} 张图片到 {output_dir} 目录")