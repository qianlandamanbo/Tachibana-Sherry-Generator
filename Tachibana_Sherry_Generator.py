import os
import time
import threading
from PIL import Image, ImageDraw, ImageFont
import win32clipboard
from io import BytesIO
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser


class ImageGenerator:
    def __init__(self):
        self.selected_bg_image = None
        self.bg_images_folder = "background_images"
        self.available_bg_images = []
        # --- 修改点2: 字体文件夹改为同目录下的 Font 文件夹 ---
        self.fonts_folder = "Font"
        self.selected_font_file = None # 存储选中的字体文件名
        self.available_fonts = [] # 存储 Font 文件夹中的字体文件列表
        self.text_color = (255, 255, 255) # RGB 格式

        # 创建必要的文件夹
        if not os.path.exists(self.bg_images_folder):
            os.makedirs(self.bg_images_folder)
        self.output_folder = "output_images"
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)
        # --- 修改点2: 确保 Font 文件夹存在 ---
        if not os.path.exists(self.fonts_folder):
            os.makedirs(self.fonts_folder)
            print(f"已创建 {self.fonts_folder} 文件夹，请放入字体文件。")

        # 加载背景图片和字体
        self.load_background_images()
        self.load_available_fonts() # 加载可用字体列表

        # 创建GUI
        self.create_gui()

    # --- 修改点2: 加载 Font 文件夹中的字体 ---
    def load_available_fonts(self):
        """加载 Font 文件夹中的字体文件"""
        self.available_fonts = []
        if os.path.exists(self.fonts_folder):
            for file in os.listdir(self.fonts_folder):
                 # 支持常见的字体格式
                if file.lower().endswith(('.ttf', '.otf', '.ttc')):
                    self.available_fonts.append(file)
        if self.available_fonts:
             # 默认选择第一个字体文件
            self.selected_font_file = self.available_fonts[0]
            print(f"加载默认字体文件: {self.selected_font_file}")
        else:
             self.selected_font_file = None
             print(f"{self.fonts_folder} 文件夹中未找到字体文件。")


    def load_background_images(self):
        """加载背景图片"""
        self.available_bg_images = []
        if os.path.exists(self.bg_images_folder):
            for file in os.listdir(self.bg_images_folder):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                    self.available_bg_images.append(file)
        if self.available_bg_images:
            self.selected_bg_image = os.path.join(self.bg_images_folder, self.available_bg_images[0])
            print(f"加载默认背景图片: {self.selected_bg_image}")

    # --- 辅助方法 ---
    def calculate_text_size(self, text, font, max_width):
        """计算文本尺寸"""
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            try:
                # getbbox 返回 (left, top, right, bottom)
                bbox = font.getbbox(test_line)
                width = bbox[2] - bbox[0]
            except Exception as e:
                print(f"计算文本宽度时出错: {e}, 使用备用方法")
                # 简单估算，可能不准确
                width = len(test_line) * (font.size if hasattr(font, 'size') else 20)
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)

        try:
            # 计算单行高度
            bbox = font.getbbox("测试Ay") # 使用包含上下延伸部的字符
            line_height = bbox[3] - bbox[1] + 10 # 添加一些间距
        except Exception as e:
            print(f"计算行高时出错: {e}, 使用默认值")
            line_height = 30 # 默认行高

        text_height = len(lines) * line_height
        return lines, text_height, line_height

    # --- 新增: 颜色选择方法 ---
    def choose_text_color(self):
        """打开颜色选择器并更新文字颜色"""
        color_code = colorchooser.askcolor(title="选择文字颜色", initialcolor='#%02x%02x%02x' % self.text_color)
        if color_code[0]: # 如果用户选择了颜色而不是取消
            # color_code[0] 是 RGB 元组 (R, G, B)
            self.text_color = tuple(map(int, color_code[0]))
            print(f"文字颜色已设置为: {self.text_color}")
            # 更新GUI上的颜色显示 (例如，改变按钮背景色)
            try:
                # 将RGB元组转换为十六进制字符串
                hex_color = '#%02x%02x%02x' % self.text_color
                self.color_button.config(bg=hex_color)
                # 确保按钮文字可见（如果背景太浅）
                # 简单判断亮度
                brightness = (self.text_color[0]*299 + self.text_color[1]*587 + self.text_color[2]*114) / 1000
                text_color_for_button = "black" if brightness > 127 else "white"
                self.color_button.config(fg=text_color_for_button)
            except tk.TclError:
                # 如果颜色设置失败（例如非法值），则不更新按钮外观
                pass
            self.status_label.config(text=f"文字颜色已设为: {hex_color}")

    # --- 新增: 字体选择方法 ---
    def select_font_file(self):
        """选择字体文件"""
        if self.available_fonts:
            # 创建一个新的顶级窗口用于选择字体
            self.font_select_window = tk.Toplevel(self.root)
            self.font_select_window.title("选择字体文件")
            self.font_select_window.geometry("400x300")
            self.font_select_window.transient(self.root) # 设置为父窗口的临时窗口
            self.font_select_window.grab_set() # 模态对话框，阻止与主窗口交互

            tk.Label(self.font_select_window, text="选择字体文件:").pack(pady=10)

            # 创建列表框
            self.font_listbox = tk.Listbox(self.font_select_window)
            for font_file in self.available_fonts:
                self.font_listbox.insert(tk.END, font_file)
            self.font_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 尝试预选当前选中的字体
            if self.selected_font_file:
                try:
                    index = self.available_fonts.index(self.selected_font_file)
                    self.font_listbox.selection_set(index)
                    self.font_listbox.see(index) # 滚动到选中项
                except ValueError:
                    pass # 当前字体不在列表中

            button_frame = tk.Frame(self.font_select_window)
            button_frame.pack(pady=10)

            # 确认按钮
            self.font_confirm_button = tk.Button(button_frame, text="确定", command=self.confirm_font_selection)
            self.font_confirm_button.pack(side=tk.LEFT, padx=5)

            # 取消按钮
            self.font_cancel_button = tk.Button(button_frame, text="取消", command=self.font_select_window.destroy)
            self.font_cancel_button.pack(side=tk.LEFT, padx=5)

        else:
            messagebox.showinfo("提示", f"请在 {self.fonts_folder} 文件夹中放入字体文件 (支持 .ttf, .otf, .ttc)")


    def confirm_font_selection(self):
        """确认选择字体文件"""
        selection = self.font_listbox.curselection()
        if selection:
            selected_index = selection[0]
            selected_filename = self.available_fonts[selected_index]

            # 更新内部状态和主界面标签
            self.selected_font_file = selected_filename
            self.font_label.config(text=f"当前: {selected_filename}")
            print(f"已选择字体文件: {self.selected_font_file}")

            # 关闭选择窗口
            self.font_select_window.destroy()

            # 更新状态栏
            self.status_label.config(text=f"已选择字体: {selected_filename}")
        else:
            messagebox.showwarning("警告", "请选择一个字体文件")


    # --- 主要功能方法 ---
    def get_input_text_from_gui(self):
        """从GUI获取输入文本"""
        text = self.text_entry.get("1.0", tk.END).strip() # 获取多行文本框的内容
        print(f"从GUI获取到文本: '{text}'")
        return text

    def generate_and_save_image(self):
        """处理请求：获取文本 -> 生成图片 -> 保存图片"""
        text = self.get_input_text_from_gui()
        if not text:
            messagebox.showwarning("警告", "请输入要生成图片的文字。")
            self.status_label.config(text="请输入文字")
            return
        print(f"\n### 开始处理图片生成 for text: '{text}' ###")
        self.status_label.config(text="正在生成图片...")
        if not self.selected_bg_image:
            msg = "错误: 请先选择背景图片"
            print(msg)
            messagebox.showerror("错误", msg)
            self.status_label.config(text=msg)
            return
        if not self.selected_font_file:
             msg = "错误: 请先选择字体文件"
             print(msg)
             messagebox.showerror("错误", msg)
             self.status_label.config(text=msg)
             return
        # 在新线程中执行耗时操作，避免阻塞GUI
        threading.Thread(target=self._generate_and_save_in_thread, args=(text,), daemon=True).start()

    def _generate_and_save_in_thread(self, text):
        """在线程中执行图片生成和保存的核心逻辑"""
        try:
            print(f"正在打开背景图片: {self.selected_bg_image}")
            bg_image = Image.open(self.selected_bg_image)
            if bg_image.mode != 'RGB':
                print(f"转换图片模式从 {bg_image.mode} 到 RGB")
                bg_image = bg_image.convert('RGB')

            # 强制调整为 900x900
            if bg_image.size != (900, 900):
                print(f"调整图片尺寸从 {bg_image.size} 到 (900, 900)")
                bg_image = bg_image.resize((900, 900), Image.Resampling.LANCZOS)

            draw = ImageDraw.Draw(bg_image)

            # --- 文本布局参数 ---
            max_width = 800 # 文本区域最大宽度
            text_area_top_y = 600 # 900 * 2/3
            text_area_bottom_y = 900
            max_height = text_area_bottom_y - text_area_top_y # 最大高度为 300

            # --- 修改点: 使用 GUI 设置的最大字体大小 ---
            initial_font_size = self.max_font_size.get()
            print(f"使用设置的最大字体大小: {initial_font_size}")
            min_font_size = 20

            # --- 寻找合适的字体大小 ---
            font_size = initial_font_size
            best_font = None
            best_lines = []
            best_line_height = 0
            found_font_size = False

            # --- 修改点1: 根据加粗选项选择字体样式 ---
            font_style = "Bold" if self.use_bold.get() else "Regular"

            while font_size >= min_font_size:
                try:
                    # --- 修改点2: 构造字体文件的完整路径 ---
                    full_font_path = os.path.join(self.fonts_folder, self.selected_font_file)
                    # --- 修改点1: 尝试加载带指定样式的字体 (Pillow 的 truetype 对样式支持有限，主要看字体文件本身) ---
                    # 如果字体文件本身就是粗体，则直接加载即可。这里我们尝试传递 style 参数（但效果取决于字体文件）
                    # 更可靠的方法是让用户准备专门的粗体字体文件。
                    # 为了兼容性，我们暂时只传路径和大小。
                    font = ImageFont.truetype(full_font_path, font_size)
                    # 注意：Pillow 的 ImageFont.truetype 并不总是能通过 style 参数动态加粗，
                    # 最佳实践是提供单独的 Bold 字体文件。这里的 use_bold 主要作为一个标识供未来扩展或用户参考。

                    lines, text_height, line_height = self.calculate_text_size(text, font, max_width)
                    print(f"尝试字体大小 {font_size}: 文本高度 {text_height}")
                    if text_height <= max_height:
                        best_font = font
                        best_lines = lines
                        best_line_height = line_height
                        found_font_size = True
                        print(f"找到合适字体大小: {font_size}")
                        break
                    font_size -= 5
                except Exception as e_font:
                    print(f"尝试字体大小 {font_size} 时出错: {e_font}")
                    font_size -= 5
                    continue # 继续尝试更小的字体

            # 如果没找到合适的，使用最小字号
            if not found_font_size:
                font_size = min_font_size
                print(f"文本过大，强制使用最小字体大小: {font_size}")
                try:
                    full_font_path = os.path.join(self.fonts_folder, self.selected_font_file)
                    best_font = ImageFont.truetype(full_font_path, font_size)
                except Exception as e_min_font:
                     print(f"加载最小字体失败: {e_min_font}, 使用默认字体")
                     best_font = ImageFont.load_default()
                # 即使字体小了，也重新计算行数和高度
                best_lines, _, best_line_height = self.calculate_text_size(text, best_font, max_width)

            # --- 绘制文本 ---
            total_lines = len(best_lines)
            if total_lines > 0:
                # 计算垂直底部对齐位置 (在限定的下三分之一区域内)
                total_text_height = total_lines * best_line_height

                # --- 修改: 计算 Y 起始位置，使其靠近下三分之一区域的底部 ---
                # 保留一些底部边距，例如 10 像素
                bottom_margin = 30
                # 计算起始Y坐标，使得文本块的底部贴近 text_area_bottom_y
                y_position = text_area_bottom_y - total_text_height - bottom_margin
                # 确保 y_position 不低于 text_area_top_y，防止文本过高时移出区域顶部
                y_position = max(y_position, text_area_top_y)

                # --- 修改点2: 使用选定的颜色 ---
                text_color = self.text_color # 使用实例变量
                shadow_color = (0, 0, 0) # 黑色阴影

                for i, line in enumerate(best_lines):
                    # 确保即使文本超出预定区域也不会画到图片最底部之外（虽然可能性不大因为有高度限制）
                    if y_position + best_line_height > text_area_bottom_y:
                        print("警告：文本即将超出下三分之一区域，停止绘制。")
                        break

                    # 避免文本画出边界
                    try:
                        bbox = best_font.getbbox(line)
                        line_width = bbox[2] - bbox[0]
                    except Exception as e_bbox:
                        print(f"获取单行宽度时出错: {e_bbox}, 使用备用方法")
                        line_width = len(line) * (font_size // 2) # 粗略估计

                    # 水平居中
                    x_position = (900 - line_width) // 2

                    # --- 修改点: 根据设置决定是否绘制描边 ---
                    if self.use_outline.get() and self.outline_width.get() > 0:
                        outline_w = self.outline_width.get()
                        # 绘制描边（简单地在四周绘制多次）
                        for dx in range(-outline_w, outline_w + 1):
                            for dy in range(-outline_w, outline_w + 1):
                                if dx != 0 or dy != 0: # 避免在中心重复绘制
                                    draw.text((x_position + dx, y_position + dy), line, font=best_font, fill=shadow_color)
                    # 绘制主文本
                    draw.text((x_position, y_position), line, font=best_font, fill=text_color)

                    y_position += best_line_height
            else:
                print("警告：没有可绘制的文本行。")

            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="正在保存图片..."))

            # --- 修改点3: 使用本地时间戳命名图片 ---
            timestamp_str = time.strftime("%Y%m%d%H%M%S")
            output_path = os.path.join(self.output_folder, f"{timestamp_str}.png")
            bg_image.save(output_path, "PNG")
            print(f"图片已保存至: {output_path}")
            success_msg = f"图片生成成功！已保存至 {output_path}"
            self.root.after(0, lambda: self.status_label.config(text=success_msg))
            self.root.after(0, lambda: messagebox.showinfo("成功", success_msg))

            # 显示预览 (在主线程中更新UI)
            self.root.after(0, lambda: self.show_image_preview(bg_image))
            print("### 图片生成和保存流程结束 ###\n")

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"生成图片时出错: {str(e)}\n详情:\n{error_details}"
            print(error_msg)
            # 在主线程中弹出错误信息和更新状态
            self.root.after(0, lambda: messagebox.showerror("错误", f"生成图片时出错: {str(e)}")) # 简化错误消息给用户
            self.root.after(0, lambda: self.status_label.config(text="生成图片失败"))

    # --- GUI相关方法 ---
    def show_image_preview(self, image):
        """显示图片预览"""
        try:
            preview_size = (300, 300)
            preview_image = image.copy()
            preview_image.thumbnail(preview_size, Image.Resampling.LANCZOS)
            from PIL import ImageTk
            self.preview_image = ImageTk.PhotoImage(preview_image)
            if hasattr(self, 'preview_label'):
                self.preview_label.config(image=self.preview_image)
            else:
                self.preview_label = ttk.Label(self.root, image=self.preview_image)
                self.preview_label.grid(row=6, column=0, columnspan=2, pady=10) # Row 增加了
        except Exception as e:
            print(f"显示预览图时出错: {e}")

    def select_background_image(self):
        """选择背景图片"""
        if self.available_bg_images:
            # 创建一个新的顶级窗口用于选择图片
            self.select_window = tk.Toplevel(self.root)
            self.select_window.title("选择背景图片")
            self.select_window.geometry("400x300")
            self.select_window.transient(self.root) # 设置为父窗口的临时窗口
            self.select_window.grab_set() # 模态对话框，阻止与主窗口交互

            tk.Label(self.select_window, text="选择背景图片:").pack(pady=10)

            # 创建列表框
            self.listbox = tk.Listbox(self.select_window)
            for img in self.available_bg_images:
                self.listbox.insert(tk.END, img)
            self.listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # 尝试预选当前选中的图片
            if self.selected_bg_image:
                current_filename = os.path.basename(self.selected_bg_image)
                try:
                    index = self.available_bg_images.index(current_filename)
                    self.listbox.selection_set(index)
                    self.listbox.see(index) # 滚动到选中项
                except ValueError:
                    pass # 当前图片不在列表中

            button_frame = tk.Frame(self.select_window)
            button_frame.pack(pady=10)

            # 确认按钮
            self.confirm_button = tk.Button(button_frame, text="确定", command=self.confirm_selection)
            self.confirm_button.pack(side=tk.LEFT, padx=5)

            # 取消按钮
            self.cancel_button = tk.Button(button_frame, text="取消", command=self.select_window.destroy)
            self.cancel_button.pack(side=tk.LEFT, padx=5)

        else:
            messagebox.showinfo("提示", f"请在 {self.bg_images_folder} 文件夹中放入背景图片 (支持 .png, .jpg, .jpeg, .bmp)")

    def confirm_selection(self):
        """确认选择背景图片"""
        selection = self.listbox.curselection()
        if selection:
            selected_index = selection[0]
            selected_filename = self.available_bg_images[selected_index]
            new_selected_path = os.path.join(self.bg_images_folder, selected_filename)

            # 更新内部状态和主界面标签
            self.selected_bg_image = new_selected_path
            self.bg_label.config(text=f"当前: {selected_filename}")
            print(f"已选择背景图片: {self.selected_bg_image}")

            # 关闭选择窗口
            self.select_window.destroy()

            # 更新状态栏
            self.status_label.config(text=f"已选择背景: {selected_filename}")
        else:
            messagebox.showwarning("警告", "请选择一张图片")

    def add_background_image(self):
        """添加背景图片"""
        file_path = filedialog.askopenfilename(
            title="选择背景图片",
            filetypes=[("图片文件", "*.png *.jpg *.jpeg *.bmp")]
        )
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(self.bg_images_folder, filename)
            if os.path.exists(dest_path):
                overwrite = messagebox.askyesno("确认", f"文件 {filename} 已存在，是否覆盖？")
                if not overwrite:
                    return
            try:
                with Image.open(file_path) as img:
                    # 保存或转换时强制为RGB和900x900
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    if img.size != (900, 900):
                        img = img.resize((900, 900), Image.Resampling.LANCZOS)
                    img.save(dest_path, "PNG") # 统一保存为PNG
                self.load_background_images() # 重新加载列表

                # 如果之前没有选中图片，或者刚添加的就是选中的图片
                if not self.selected_bg_image or os.path.basename(self.selected_bg_image) == filename:
                    self.selected_bg_image = dest_path
                    self.bg_label.config(text=f"当前: {filename}")
                messagebox.showinfo("成功", "背景图片已添加/更新")
                print(f"背景图片已添加/更新: {dest_path}")
            except Exception as e:
                error_msg = f"添加失败: {str(e)}"
                print(error_msg)
                messagebox.showerror("错误", error_msg)

    def create_gui(self):
        """创建GUI界面"""
        self.root = tk.Tk()

        # --- 在这里添加 IntVar, BooleanVar 和 StringVar 的初始化 ---
        # 因为现在 self.root 已经存在了
        self.max_font_size = tk.IntVar(value=120) # 默认最大字体大小
        self.use_outline = tk.BooleanVar(value=True) # 默认启用描边
        self.outline_width = tk.IntVar(value=2) # 默认描边宽度
        # --- 修改点1: 添加加粗选项 ---
        self.use_bold = tk.BooleanVar(value=False) # 默认不加粗
        # ------------------------------------------

        self.root.title("橘雪莉表情包生成器")
        self.root.geometry("500x900") # 窗口稍微高一点以容纳新增控件和预览图

        title_label = ttk.Label(self.root, text="橘雪莉表情包生成器", font=("Microsoft YaHei", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)

        ttk.Label(self.root, text="请输入文字:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.text_entry = tk.Text(self.root, wrap=tk.WORD, height=8)
        self.text_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # --- 新增: 文字颜色选择按钮 ---
        color_frame = ttk.Frame(self.root)
        color_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky="w")
        ttk.Label(color_frame, text="文字颜色:").pack(side=tk.LEFT)
        # 初始化颜色按钮，显示默认颜色
        default_hex_color = '#%02x%02x%02x' % self.text_color
        brightness = (self.text_color[0]*299 + self.text_color[1]*587 + self.text_color[2]*114) / 1000
        text_color_for_button = "black" if brightness > 127 else "white"
        self.color_button = tk.Button(color_frame, text="选择颜色", bg=default_hex_color, fg=text_color_for_button, command=self.choose_text_color)
        self.color_button.pack(side=tk.LEFT, padx=5)
        # -----------------------------

        # --- 修改点1 & 2: 字体设置 UI (包含加粗和字体选择) ---
        # 字体设置框架
        font_settings_frame = ttk.LabelFrame(self.root, text="字体设置")
        font_settings_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # 字体文件选择部分
        font_file_frame = ttk.Frame(font_settings_frame)
        font_file_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        ttk.Label(font_file_frame, text="字体文件:").pack(side=tk.LEFT)
        self.font_label = ttk.Label(font_file_frame, text="未选择" if not self.selected_font_file else f"当前: {self.selected_font_file}")
        self.font_label.pack(side=tk.LEFT, padx=(5, 10))
        ttk.Button(font_file_frame, text="选择", command=self.select_font_file).pack(side=tk.LEFT)

         # 字体样式和大小部分
        font_options_frame = ttk.Frame(font_settings_frame)
        font_options_frame.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # 加粗选项
        self.bold_checkbutton = ttk.Checkbutton(font_options_frame, text="加粗", variable=self.use_bold)
        self.bold_checkbutton.pack(side=tk.LEFT, padx=5)

        # 最大字体大小
        ttk.Label(font_options_frame, text="最大字体大小:").pack(side=tk.LEFT, padx=(10, 5))
        self.font_size_spinbox = tk.Spinbox(font_options_frame, from_=50, to=200, increment=5, textvariable=self.max_font_size, width=5)
        self.font_size_spinbox.pack(side=tk.LEFT, padx=5)
        # 设置初始值
        self.font_size_spinbox.delete(0, "end")
        self.font_size_spinbox.insert(0, "120")

        # --- 描边设置 UI ---
        # 描边框架
        outline_frame = ttk.LabelFrame(self.root, text="文字描边")
        outline_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        self.outline_checkbutton = ttk.Checkbutton(outline_frame, text="启用描边", variable=self.use_outline)
        self.outline_checkbutton.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(outline_frame, text="描边大小:").grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.outline_width_spinbox = tk.Spinbox(outline_frame, from_=0, to=10, increment=1, textvariable=self.outline_width, width=3)
        self.outline_width_spinbox.grid(row=0, column=2, padx=5, pady=5, sticky="w")
        # 设置初始值
        self.outline_width_spinbox.delete(0, "end")
        self.outline_width_spinbox.insert(0, "2")
        # -----------------------------

        # --- 背景图片选择 UI ---
        ttk.Label(self.root, text="背景图片:").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        bg_frame = ttk.Frame(self.root)
        bg_frame.grid(row=5, column=1, padx=10, pady=5, sticky="ew")
        self.bg_label = ttk.Label(bg_frame, text="未选择" if not self.selected_bg_image else f"当前: {os.path.basename(self.selected_bg_image)}")
        self.bg_label.pack(side=tk.LEFT)
        ttk.Button(bg_frame, text="选择", command=self.select_background_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(bg_frame, text="添加", command=self.add_background_image).pack(side=tk.LEFT, padx=5)

        # --- 生成按钮 ---
        button_frame = ttk.Frame(self.root)
        button_frame.grid(row=7, column=0, columnspan=2, pady=20) # Row 更新
        generate_button = ttk.Button(button_frame, text="生成图片", command=self.generate_and_save_image)
        generate_button.pack(side=tk.LEFT, padx=10)

        # --- 状态栏 ---
        self.status_label = ttk.Label(self.root, text="请选择背景图片、字体文件并输入文字")
        self.status_label.grid(row=8, column=0, columnspan=2, pady=5) # Row 更新

        # --- 使用说明 ---
        instruction_text = """
        シェリーちゃん可愛い大好き！
        如果发现有些操作按钮没有出来，可以试试看把应用程序框拖大点！

        你是谁？请支持《魔法少女的魔女裁判》喵！"""
        instruction_label = ttk.Label(self.root, text=instruction_text, justify=tk.LEFT, wraplength=450)
        instruction_label.grid(row=9, column=0, columnspan=2, padx=20, pady=10, sticky="nw") # Row 更新

        # 更新网格权重配置
        self.root.grid_rowconfigure(9, weight=1) # 更新到最后一个 row
        self.root.grid_columnconfigure(1, weight=1)

    def run(self):
        """运行程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = ImageGenerator()
    app.run()