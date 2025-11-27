import os  # 导入操作系统模块，用于文件路径和目录操作
import time  # 导入时间模块，用于生成时间戳文件名
import threading  # 导入多线程模块，用于后台生成图片，防止界面卡死
import tkinter as tk  # 导入 tkinter，Python 标准 GUI 库
from tkinter import ttk, filedialog, messagebox, colorchooser  # 导入 tkinter 的高级组件和弹窗工具
from PIL import Image, ImageTk  # 导入 Pillow 库，用于强大的图像处理
from generator import ImageGenerator

# ==========================================
#  UI 交互层: 负责显示和用户输入
#  (View/Controller Layer: Handles UI)
# ==========================================
class MemeApp:
    def __init__(self):
        """
        Description:
            应用程序入口，初始化主窗口、变量和界面。
            App entry point, initializes main window, variables, and UI.

        Args:
            None

        Returns:
            None

        Examples:
            >>> app = MemeApp()
            >>> app.run()
        """
        # 创建 tkinter 主窗口
        self.root = tk.Tk()
        # 设置窗口标题
        self.root.title("橘雪莉表情包生成器 (Refactored)")
        # 设置窗口初始大小 (宽x高)
        self.root.geometry("1000x700") 
        
        # 初始化我们上面定义的图片渲染器
        self.generator = ImageGenerator()
        
        # --- 定义绑定到 UI 控件的变量 ---
        # 文字颜色，默认白色
        self.var_text_color = (255, 255, 255) 
        # 字体大小，绑定到滑块
        self.var_font_size = tk.IntVar(value=100)
        # 是否描边，绑定到复选框
        self.var_use_outline = tk.BooleanVar(value=True)
        # 描边宽度，绑定到滑块
        self.var_outline_width = tk.IntVar(value=3)
        # 背景文件名，绑定到下拉框
        self.var_bg_file = tk.StringVar()
        # 字体文件名，绑定到下拉框
        self.var_font_file = tk.StringVar()
        
        # --- 内部状态变量 ---
        # 用于缓存当前生成的高清大图 (用于保存)
        self.current_image_obj = None 
        # 用于防抖动的定时器任务 ID
        self._preview_job = None 

        # 构建界面布局
        self._setup_ui()
        # 加载下拉框的资源数据
        self._load_resources()
        
        # 程序启动时，手动触发一次预览更新
        self._trigger_preview_update()

    def _load_resources(self):
        """
        Description:
            读取文件夹内容并更新下拉框选项。
            Load file lists from folders and update combobox values.

        Args:
            None

        Returns:
            None

        Examples:
            >>> self._load_resources()
        """
        # 从渲染器获取背景图片列表
        bgs = self.generator.get_files(self.generator.bg_folder, ('.png', '.jpg', '.jpeg'))
        # 设置下拉框的值
        self.combo_bg['values'] = bgs
        # 如果列表不为空，默认选中第 1 个
        if bgs:
            self.combo_bg.current(0)
        
        # 从渲染器获取字体文件列表
        fonts = self.generator.get_files(self.generator.font_folder, ('.ttf', '.otf'))
        # 设置下拉框的值
        self.combo_font['values'] = fonts
        # 如果列表不为空，默认选中第 1 个
        if fonts:
            self.combo_font.current(0)

    def _setup_ui(self):
        """
        Description:
            构建左右分栏的 GUI 布局。
            Construct the split-pane GUI layout.

        Args:
            None

        Returns:
            None

        Examples:
            >>> self._setup_ui()
        """
        # === 主容器: PanedWindow (支持拖动调整左右比例) ===
        main_paned = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        # 充满整个窗口，留点边距
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # === 左侧控制面板 ===
        left_frame = ttk.Frame(main_paned)
        # 将左侧面板加入 PanedWindow，初始宽度 400
        main_paned.add(left_frame, width=400)

        # --- 区域 1. 文本输入区 ---
        # 创建带标题的容器框
        group_text = ttk.LabelFrame(left_frame, text="1. 输入文字")
        # 横向填充
        group_text.pack(fill=tk.X, pady=5)
        
        # 创建多行文本输入框
        self.text_input = tk.Text(group_text, height=5, width=30)
        self.text_input.pack(fill=tk.X, padx=5, pady=5)
        # [关键] 绑定键盘松开事件，实现打字即预览
        self.text_input.bind('<KeyRelease>', self._on_input_change)

        # --- 区域 2. 外观设置区 ---
        group_style = ttk.LabelFrame(left_frame, text="2. 样式设置")
        group_style.pack(fill=tk.X, pady=5)

        # 颜色选择按钮
        self.btn_color = tk.Button(group_style, text="点击修改文字颜色", bg="white", command=self._choose_color)
        self.btn_color.pack(fill=tk.X, padx=5, pady=5)

        # 滑块容器
        frame_sliders = ttk.Frame(group_style)
        frame_sliders.pack(fill=tk.X, padx=5)
        
        # 字体大小滑块
        ttk.Label(frame_sliders, text="最大字号:").grid(row=0, column=0, sticky='w')
        # 绑定 command 到 _on_input_change，拖动滑块时实时刷新
        s1 = ttk.Scale(frame_sliders, from_=20, to=200, variable=self.var_font_size, command=self._on_input_change)
        s1.grid(row=0, column=1, sticky='ew')
        
        # 描边复选框
        ttk.Checkbutton(frame_sliders, text="启用描边", variable=self.var_use_outline, command=self._on_input_change).grid(row=1, column=0, sticky='w')
        # 描边宽度滑块
        s2 = ttk.Scale(frame_sliders, from_=0, to=10, variable=self.var_outline_width, command=self._on_input_change)
        s2.grid(row=1, column=1, sticky='ew')

        # --- 区域 3. 资源选择区 ---
        group_res = ttk.LabelFrame(left_frame, text="3. 资源选择")
        group_res.pack(fill=tk.X, pady=5)

        # 背景选择下拉框
        ttk.Label(group_res, text="背景图片:").pack(anchor='w', padx=5)
        self.combo_bg = ttk.Combobox(group_res, textvariable=self.var_bg_file, state="readonly")
        self.combo_bg.pack(fill=tk.X, padx=5, pady=2)
        # 绑定选中事件，切换图片时刷新预览
        self.combo_bg.bind("<<ComboboxSelected>>", self._on_input_change)
        
        # 添加背景按钮
        btn_add_bg = ttk.Button(group_res, text="+ 添加新背景", command=self._add_background)
        btn_add_bg.pack(anchor='e', padx=5, pady=2)

        # 字体选择下拉框
        ttk.Label(group_res, text="字体文件:").pack(anchor='w', padx=5, pady=(10, 0))
        self.combo_font = ttk.Combobox(group_res, textvariable=self.var_font_file, state="readonly")
        self.combo_font.pack(fill=tk.X, padx=5, pady=2)
        self.combo_font.bind("<<ComboboxSelected>>", self._on_input_change)

        # --- 区域 4. 保存按钮 ---
        self.btn_save = ttk.Button(left_frame, text="保存图片 (Save)", command=self._save_image)
        # 设置 padding 把它撑大一点
        self.btn_save.pack(fill=tk.X, pady=20, ipady=10)

        # === 右侧预览面板 ===
        right_frame = ttk.Frame(main_paned)
        main_paned.add(right_frame)

        # 预览图标签 (Label)
        self.lbl_preview = ttk.Label(right_frame, text="预览区域", anchor="center", background="#e0e0e0")
        self.lbl_preview.pack(fill=tk.BOTH, expand=True)
        # [关键] 监听窗口大小变化事件，以便调整预览图大小
        self.lbl_preview.bind('<Configure>', self._on_resize_preview)

    def _choose_color(self):
        """
        Description:
            打开系统颜色选择器，更新文字颜色。
            Open system color picker and update text color.

        Args:
            None

        Returns:
            None

        Examples:
            >>> # Triggered by button click
        """
        # 弹出颜色选择框
        colors = colorchooser.askcolor(initialcolor='#%02x%02x%02x' % self.var_text_color)
        # colors 返回格式: ((r,g,b), '#hex')。如果点击取消，返回 None
        if colors[0]:
            # 更新颜色变量
            self.var_text_color = tuple(map(int, colors[0])) 
            # 更新按钮的背景色，给用户反馈
            self.btn_color.config(bg=colors[1]) 
            # 触发预览刷新
            self._trigger_preview_update()

    def _add_background(self):
        """
        Description:
            打开文件对话框添加新背景图，并自动复制到资源目录。
            Open file dialog to add new bg image, copy to resource folder.

        Args:
            None

        Returns:
            None

        Examples:
            >>> # Triggered by button click
        """
        # 打开文件选择框
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            try:
                # 打开图片
                img = Image.open(path)
                # 获取文件名
                filename = os.path.basename(path)
                # 构造目标路径
                target = os.path.join(self.generator.bg_folder, filename)
                # 保存到项目的 background_images 文件夹
                img.save(target)
                # 重新加载资源列表
                self._load_resources() 
                # 自动选中刚添加的图片
                self.combo_bg.set(filename)
                # 触发预览刷新
                self._trigger_preview_update()
                messagebox.showinfo("成功", "背景已添加")
            except Exception as e:
                messagebox.showerror("错误", f"无法添加图片: {e}")

    def _on_input_change(self, event=None):
        """
        Description:
            统一的事件处理入口。使用防抖动机制(Debounce)避免频繁渲染。
            Unified event handler. Uses debounce to avoid frequent rendering.

        Args:
            event (tk.Event): 事件对象 (键盘事件或组件事件). Defaults to None.

        Returns:
            None

        Examples:
            >>> # Triggered by KeyRelease or Scale command
        """
        # 如果之前已经有计划执行的任务，先取消它
        if self._preview_job:
            self.root.after_cancel(self._preview_job)
        # 设置新的定时任务：300毫秒后执行 _trigger_preview_update
        # 如果在这 300ms 内用户又打字了，这个任务会被上面的 cancel 取消掉
        self._preview_job = self.root.after(300, self._trigger_preview_update)

    def _trigger_preview_update(self):
        """
        Description:
            收集所有 UI 参数，并在后台线程启动生成任务。
            Gather UI params and start generation task in background thread.

        Args:
            None

        Returns:
            None

        Examples:
            >>> self._trigger_preview_update()
        """
        # 1. 收集参数字典
        settings = {
            # 获取文本框内容，从第一行第0列到结尾，并去除首尾空格
            'text': self.text_input.get("1.0", tk.END).strip(),
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            # 构造背景图完整路径
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }

        # 2. 启动新线程生成 (避免卡死 UI 主线程)
        thread = threading.Thread(target=self._generate_task, args=(settings,))
        # 设置为守护线程，这样主程序关闭时线程也会自动关闭
        thread.daemon = True
        thread.start()

    def _generate_task(self, settings):
        """
        Description:
            [线程内部] 调用渲染器生成图片，完成后通知主线程。
            [Thread Internal] Call renderer, then notify main thread.

        Args:
            settings (dict): 绘图参数.

        Returns:
            None

        Examples:
            >>> # Called by thread
        """
        # 调用核心渲染逻辑
        image = self.generator.render_image(settings)
        # 渲染耗时操作结束后，通过 root.after 把更新 UI 的工作排队给主线程
        # 注意：tkinter 的 UI 操作必须在主线程进行
        self.root.after(0, self._update_preview_ui, image)

    def _update_preview_ui(self, pil_image):
        """
        Description:
            [主线程] 将生成的图片显示在界面上。
            [Main Thread] Display the generated image on UI.

        Args:
            pil_image (Image): Pillow 的图像对象.

        Returns:
            None

        Examples:
            >>> self._update_preview_ui(img_obj)
        """
        # 保存一份原始高清图引用，用于稍后保存到硬盘
        self.current_image_obj = pil_image 
        
        # 获取预览标签当前的宽高
        win_w = self.lbl_preview.winfo_width()
        win_h = self.lbl_preview.winfo_height()
        
        # 如果窗口还没初始化好(太小)，暂不渲染
        if win_w < 10 or win_h < 10: return 

        # 计算缩放比例：保持图片比例适应窗口 (Contain模式)
        ratio = min(win_w / 900, win_h / 900)
        # 计算新的缩放尺寸
        new_size = (int(900 * ratio), int(900 * ratio))
        
        try:
            # 高质量缩放图片用于预览
            preview_img = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            # 转换为 tkinter 能显示的格式
            tk_img = ImageTk.PhotoImage(preview_img)
            # 更新标签图片
            self.lbl_preview.config(image=tk_img, text="") 
            # [重要] 必须手动持有图片引用，否则会被 Python 垃圾回收导致不显示
            self.lbl_preview.image = tk_img 
        except Exception as e:
            print(f"预览更新失败: {e}")

    def _on_resize_preview(self, event):
        """
        Description:
            当预览区域大小改变时触发，重新调整预览图大小。
            Triggered when preview area resizes, adjusts preview image size.

        Args:
            event (tk.Event): 窗口大小改变事件.

        Returns:
            None

        Examples:
            >>> # Triggered by window resize
        """
        # 如果当前已经有生成好的图片
        if self.current_image_obj:
            # 直接复用该图片进行缩放显示，不需要重新运行渲染文字的逻辑
            self._update_preview_ui(self.current_image_obj)

    def _save_image(self):
        """
        Description:
            将当前高清大图保存到本地磁盘。
            Save current high-res image to local disk.

        Args:
            None

        Returns:
            None

        Examples:
            >>> # Triggered by Save button
        """
        # 如果还没生成图片，直接返回
        if not self.current_image_obj:
            return
        
        # 生成时间戳文件名 (e.g., 20231001120000.png)
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.png"
        # 拼接保存路径
        save_path = os.path.join("output_images", filename)
        
        try:
            # 保存文件
            self.current_image_obj.save(save_path)
            # 弹窗提示成功
            messagebox.showinfo("保存成功", f"图片已保存至:\n{save_path}")
        except Exception as e:
            # 弹窗提示失败
            messagebox.showerror("保存失败", str(e))

    def run(self):
        """
        Description:
            启动 GUI 主事件循环。
            Start the GUI main event loop.

        Args:
            None

        Returns:
            None

        Examples:
            >>> app.run()
        """
        self.root.mainloop()
