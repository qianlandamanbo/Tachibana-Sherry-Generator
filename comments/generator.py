import os
from PIL import Image, ImageDraw, ImageFont, ImageTk

# ==========================================
#  核心逻辑层: 只负责画图，不负责弹窗
#  (Model Layer: Handles logic and data)
# ==========================================
class ImageGenerator:
    def __init__(self, bg_folder="background_images", font_folder="Font"):
        """
        Description:
            初始化图片渲染器，设置资源文件夹路径并确保它们存在。
            Initialize the image renderer, set resource paths and ensure they exist.

        Args:
            bg_folder (str): 背景图片文件夹名称. Defaults to "background_images".
            font_folder (str): 字体文件文件夹名称. Defaults to "Font".

        Returns:
            None

        Examples:
            >>> renderer = ImageRenderer()
        """
        # 保存背景文件夹路径
        self.bg_folder = bg_folder
        # 保存字体文件夹路径
        self.font_folder = font_folder
        
        # 自动检查并创建背景文件夹
        self._ensure_dir(bg_folder)
        # 自动检查并创建字体文件夹
        self._ensure_dir(font_folder)
        # 自动检查并创建输出文件夹
        self._ensure_dir("output_images")

    def _ensure_dir(self, path):
        """
        Description:
            [内部辅助] 检查文件夹是否存在，不存在则创建。
            [Internal Helper] Check if directory exists, create if not.

        Args:
            path (str): 文件夹路径.

        Returns:
            None

        Examples:
            >>> self._ensure_dir("my_folder")
        """
        # 判断路径是否存在
        if not os.path.exists(path):
            # 创建文件夹
            os.makedirs(path)
            # 打印控制台日志
            print(f"已创建目录: {path}")

    def get_files(self, folder, extensions):
        """
        Description:
            获取指定文件夹下符合特定后缀名的文件列表。
            Get list of files in a folder matching specific extensions.

        Args:
            folder (str): 目标文件夹路径.
            extensions (tuple): 后缀名元组 (e.g., ('.jpg', '.png')).

        Returns:
            list: 包含文件名的字符串列表.

        Examples:
            >>> files = self.get_files("bg_images", ('.png', '.jpg'))
            >>> print(files)
            ['bg1.png', 'bg2.jpg']
        """
        # 如果文件夹不存在，直接返回空列表
        if not os.path.exists(folder):
            return []
        # 列表推导式：遍历目录，筛选出以指定后缀结尾的文件
        return [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

    def _calculate_wrapped_text(self, draw, text, font, max_width):
        """
        Description:
            [内部辅助] 计算文本自动换行逻辑。
            [Internal Helper] Calculate text wrapping logic.

        Args:
            draw (ImageDraw): Pillow 的画笔对象 (用于计算宽度).
            text (str): 原始文本.
            font (ImageFont): 使用的字体对象.
            max_width (int): 允许的最大宽度 (像素).

        Returns:
            tuple: (处理后的行列表 lines, 总高度 total_height, 单行高度 line_height)

        Examples:
            >>> lines, h, lh = self._calculate_wrapped_text(draw, "Hello World", font, 800)
        """
        lines = []  # 用于存储切分好的每一行文字
        try:
            # 获取单行高度。getbbox 返回 (left, top, right, bottom)
            # 使用 'Ay' 这种比较高的字符来定高，确保涵盖上伸部和下延部
            bbox = font.getbbox("Ay") 
            # 计算字符高度，并额外加 10 像素行间距
            line_height = bbox[3] - bbox[1] + 10 
        except:
            # 如果获取失败（极少数情况），使用兜底默认值
            line_height = 30 

        # 暴力换行算法：先按换行符分割段落
        for paragraph in text.split('\n'):
            current_line = ""  # 当前正在拼接的行
            # 遍历段落中的每个字符
            for char in paragraph:
                # 尝试把字符加到当前行后面
                test_line = current_line + char
                # 计算这一行现在的像素宽度
                w = font.getlength(test_line)
                # 如果宽度在允许范围内
                if w <= max_width:
                    # 确认加入这个字符
                    current_line = test_line
                else:
                    # 宽度超了，把之前的 current_line 存入结果列表
                    lines.append(current_line)
                    # 新的一行从当前这个字符开始
                    current_line = char
            # 处理段落末尾的剩余字符
            if current_line:
                lines.append(current_line)
        
        # 计算总高度 = 行数 * 单行高度
        total_height = len(lines) * line_height
        # 返回计算结果
        return lines, total_height, line_height

    def render_image(self, settings):
        """
        Description:
            核心渲染函数，根据设置生成最终图片。
            Core rendering function, generates final image based on settings.

        Args:
            settings (dict): 包含绘图参数的字典 (text, bg_path, font_name, size, color, etc.).

        Returns:
            Image: Pillow 的 Image 对象.

        Examples:
            >>> cfg = {'text': 'Hi', 'bg_path': 'a.png', 'font_size': 50}
            >>> img = renderer.render_image(cfg)
        """
        # 1. 加载背景图片
        bg_path = settings.get('bg_path')  # 从字典获取路径
        # 检查路径是否存在
        if not bg_path or not os.path.exists(bg_path):
            # 如果没背景或路径不对，创建一个 900x900 的灰色空背景防止报错
            img = Image.new('RGB', (900, 900), color='gray')
        else:
            try:
                # 打开图片并强制转换为 RGB 模式 (防止 PNG 透明通道导致的兼容问题)
                img = Image.open(bg_path).convert('RGB')
                # 强制调整尺寸为 900x900 (你可以根据需求修改这里)
                if img.size != (900, 900):
                    img = img.resize((900, 900), Image.Resampling.LANCZOS)
            except Exception as e:
                # 如果图片损坏，打印错误并使用灰色背景兜底
                print(f"背景加载失败: {e}")
                img = Image.new('RGB', (900, 900), color='gray')

        # 创建画笔对象
        draw = ImageDraw.Draw(img)
        # 获取要绘制的文字，默认为空字符串
        text = settings.get('text', '')
        # 如果没有文字，直接返回只有背景的图
        if not text:
            return img

        # 2. 加载字体逻辑
        # 拼接字体文件的完整路径
        font_path = os.path.join(self.font_folder, settings.get('font_file', ''))
        # 获取用户设置的最大字号，默认 100
        max_font_size = settings.get('font_size', 100)
        
        # --- 字体自适应算法 Start ---
        # 从用户设定的最大字号开始尝试
        current_size = max_font_size
        min_size = 20  # 最小字号限制
        final_font = None  # 最终选定的字体对象
        final_lines = []   # 最终切分好的行
        final_line_h = 0   # 最终行高
        
        # 定义文本绘制区域参数
        draw_area_w = 800  # 左右边距各留 50 (900-800=100)
        draw_area_bottom_y = 880 # 底部留 20 像素边距
        draw_area_limit_h = 300  # 限制文字只在下半部分 300px 高度内

        # 循环尝试字号，直到文字能塞进指定区域
        while current_size >= min_size:
            try:
                # 尝试加载字体文件
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, current_size)
                else:
                    # 如果字体文件找不到，使用 Pillow 默认字体 (不支持中文)
                    font = ImageFont.load_default()
                
                # 调用辅助函数计算换行和高度
                lines, h, line_h = self._calculate_wrapped_text(draw, text, font, draw_area_w)
                
                # 判断高度是否超出限制
                if h <= draw_area_limit_h:
                    # 找到了合适的大小！保存结果并退出循环
                    final_font = font
                    final_lines = lines
                    final_line_h = line_h
                    break
            except Exception as e:
                print(f"字体计算错误: {e}")
            
            # 如果当前字号太大，减小 5 号，继续尝试
            current_size -= 5 
        
        # 如果循环结束还没找到 (final_font 还是 None)
        if final_font is None:
            # 强制使用默认字体和最小行高兜底
            final_font = ImageFont.load_default()
            final_lines = [text]
            final_line_h = 20
        # --- 字体自适应算法 End ---

        # 3. 绘制文字逻辑
        # 计算文字块的总高度
        total_h = len(final_lines) * final_line_h
        # 计算起始 Y 坐标：确保文字块底部对齐 draw_area_bottom_y
        start_y = draw_area_bottom_y - total_h
        
        # 获取文字颜色
        text_color = settings.get('text_color', (255, 255, 255))
        # 获取是否描边
        use_outline = settings.get('use_outline', False)
        # 获取描边宽度
        outline_w = settings.get('outline_width', 2)

        # 逐行绘制
        for i, line in enumerate(final_lines):
            # 计算水平居中 X 坐标
            line_w = final_font.getlength(line)
            x = (900 - line_w) // 2
            # 计算当前行 Y 坐标
            y = start_y + i * final_line_h

            # 判断是否需要描边
            if use_outline:
                # PIL 的 stroke_width 参数用于描边，stroke_fill 是描边颜色(这里固定黑色)
                draw.text((x, y), line, font=final_font, fill=text_color, 
                          stroke_width=outline_w, stroke_fill=(0,0,0))
            else:
                # 不描边直接画
                draw.text((x, y), line, font=final_font, fill=text_color)

        # 返回绘制好的图片对象
        return img


