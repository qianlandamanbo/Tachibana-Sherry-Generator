import os  # 导入操作系统模块，用于文件路径和目录操作
from PIL import Image, ImageDraw, ImageFont, ImageTk  # 导入 Pillow 库，用于强大的图像处理

class ImageGenerator:
    def __init__(self, bg_folder="background_images", font_folder="Font"):
        """
        初始化图片渲染器
        """
        self.bg_folder = bg_folder
        self.font_folder = font_folder
        
        # 自动创建文件夹
        self._ensure_dir(bg_folder)
        self._ensure_dir(font_folder)
        self._ensure_dir("output_images")

    def _ensure_dir(self, path):
        """[辅助] 确保文件夹存在"""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"已创建目录: {path}")

    def get_files(self, folder, extensions):
        """[辅助] 获取指定后缀的文件列表"""
        if not os.path.exists(folder):
            return []
        return [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

    def _calculate_wrapped_text(self, draw, text, font, max_width):
        """
        [辅助] 计算自动换行
        返回: (处理后的行列表, 总高度, 单行高度)
        """
        lines = []
        try:
            # 获取单行高度 (bbox返回 left, top, right, bottom)
            # 使用 'Ay' 这种比较高的字符来定高
            bbox = font.getbbox("Ay") 
            line_height = bbox[3] - bbox[1] + 10 # 额外加点行间距
        except:
            line_height = 30 # 兜底默认值

        # 暴力换行算法
        for paragraph in text.split('\n'):
            current_line = ""
            for char in paragraph:
                test_line = current_line + char
                # 计算这一行现在的宽度
                w = font.getlength(test_line)
                if w <= max_width:
                    current_line = test_line
                else:
                    lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
        
        total_height = len(lines) * line_height
        return lines, total_height, line_height

<<<<<<< HEAD
    def _resize_image_with_ratio(self, img, target_size=(900, 900), mode='contain'):
        """
        [辅助] 按比例缩放图片，保持宽高比
        Args:
            img: PIL图片对象
            target_size: 目标尺寸 (width, height)
            mode: 缩放模式 'contain'(包含) 或 'cover'(覆盖)
        Returns:
            缩放后的PIL图片对象
        """
        original_width, original_height = img.size
        target_width, target_height = target_size
        
        if mode == 'contain':
            # 包含模式：图片完全显示在目标区域内，保持比例
            width_ratio = target_width / original_width
            height_ratio = target_height / original_height
            ratio = min(width_ratio, height_ratio)
        else:  # cover模式
            # 覆盖模式：图片覆盖整个目标区域，保持比例
            width_ratio = target_width / original_width
            height_ratio = target_height / original_height
            ratio = max(width_ratio, height_ratio)
        
        # 计算新尺寸
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        
        # 缩放图片
        resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # 创建新的画布
        new_img = Image.new('RGB', target_size, color='white')
        
        # 计算居中位置
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        # 将缩放后的图片粘贴到新画布上
        new_img.paste(resized_img, (x_offset, y_offset))
        
        return new_img

=======
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
    def render_image(self, settings):
        """
        核心渲染函数
        Args:
            settings: 包含所有绘图参数的字典 (text, bg_path, font_name, size, color 等)
        Returns:
            PIL.Image 对象
        """
        # 1. 加载背景
        bg_path = settings.get('bg_path')
<<<<<<< HEAD
        resize_mode = settings.get('resize_mode', 'contain')  # 默认使用包含模式
        
=======
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
        if not bg_path or not os.path.exists(bg_path):
            # 如果没背景，创建一个灰色的空背景防止报错
            img = Image.new('RGB', (900, 900), color='gray')
        else:
            try:
                img = Image.open(bg_path).convert('RGB')
                if img.size != (900, 900):
<<<<<<< HEAD
                    # 使用自适应缩放，保持比例不拉伸
                    img = self._resize_image_with_ratio(img, (900, 900), resize_mode)
=======
                    img = img.resize((900, 900), Image.Resampling.LANCZOS)
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
            except Exception as e:
                print(f"背景加载失败: {e}")
                img = Image.new('RGB', (900, 900), color='gray')

        draw = ImageDraw.Draw(img)
        text = settings.get('text', '')
        if not text:
            return img

        # 2. 加载字体
<<<<<<< HEAD
        font_file = settings.get('font_file', '')
        font_path = os.path.join(self.font_folder, font_file) if font_file else None
=======
        font_path = os.path.join(self.font_folder, settings.get('font_file', ''))
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
        max_font_size = settings.get('font_size', 100)
        
        # 简单的自适应字体大小逻辑
        # 从最大字号开始尝试，如果高度超了就减小
        current_size = max_font_size
        min_size = 20
        final_font = None
        final_lines = []
        final_line_h = 0
        
        # 文本绘制区域设定
        draw_area_w = 800
        draw_area_bottom_y = 880 # 留底边距
        draw_area_limit_h = 300  # 限制文字只在下半部分区域

        while current_size >= min_size:
            try:
                # 尝试加载字体
<<<<<<< HEAD
                if font_path and os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, current_size)
                else:
                    # 如果没有字体文件，使用默认字体
                    font = ImageFont.load_default()
=======
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, current_size)
                else:
                    font = ImageFont.load_default() # 兜底
>>>>>>> e6abe0196acb87bd3f559e0e491ccbf31c8ab8bc
                
                # 计算换行
                lines, h, line_h = self._calculate_wrapped_text(draw, text, font, draw_area_w)
                
                if h <= draw_area_limit_h:
                    # 找到了合适的大小
                    final_font = font
                    final_lines = lines
                    final_line_h = line_h
                    break
            except Exception as e:
                print(f"字体计算错误: {e}")
            
            current_size -= 5 # 缩小字号重试
        
        if final_font is None:
            # 如果循环完了还没找到，就用最小的
            final_font = ImageFont.load_default()
            final_lines = [text]
            final_line_h = 20

        # 3. 绘制文字
        # 计算起始Y坐标（底部对齐）
        total_h = len(final_lines) * final_line_h
        start_y = draw_area_bottom_y - total_h
        
        text_color = settings.get('text_color', (255, 255, 255))
        use_outline = settings.get('use_outline', False)
        outline_w = settings.get('outline_width', 2)

        for i, line in enumerate(final_lines):
            # 水平居中
            line_w = final_font.getlength(line)
            x = (900 - line_w) // 2
            y = start_y + i * final_line_h

            # 描边 (在上下左右偏移绘制黑色)
            if use_outline:
                # PIL 新版可以用 stroke_width, 但为了兼容旧逻辑我们手动画或者用参数
                # 这里使用 PIL 原生 stroke 参数更高效
                draw.text((x, y), line, font=final_font, fill=text_color, 
                          stroke_width=outline_w, stroke_fill=(0,0,0))
            else:
                draw.text((x, y), line, font=final_font, fill=text_color)

        return img
