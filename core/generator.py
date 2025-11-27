import os  # 导入操作系统模块
from typing import Dict,  List
from PIL import Image, ImageDraw, ImageFont  # 导入 Pillow 核心库 (移除了 UI 相关的 ImageTk)

from core.config import GeneratorConfig

class ImageGenerator:
    def __init__(self, bg_folder : str = None, font_folder : str = None):
        """
        Description:
            初始化图片渲染器，准备资源文件夹。
            Initialize image renderer and prepare resource folders.

        Args:
            bg_folder (str): 背景文件夹路径.
            font_folder (str): 字体文件夹路径.

        Returns:
            None
        """
        self.bg_folder =  GeneratorConfig.bg_folder
        self.font_folder = GeneratorConfig.font_folder
        
        # 确保必要的文件夹存在
        self._ensure_dir(self.bg_folder)
        self._ensure_dir(self.font_folder)
        self._ensure_dir(GeneratorConfig.output_folder)

    def _ensure_dir(self, path : str) -> None:
        """[辅助] 确保文件夹存在，不存在则创建"""
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"已创建目录: {path}")

    def get_files(self, folder : str, extensions : tuple) -> List[str]:
        """
        Description:
            获取指定后缀的文件列表。
            Get list of files with specific extensions.
        """
        if not os.path.exists(folder):
            return []
        return [f for f in os.listdir(folder) if f.lower().endswith(extensions)]

    def _calculate_wrapped_text(self, text : str, font : ImageFont, max_width : int):
        """
        [辅助] 计算自动换行逻辑
        """
        lines = []
        try:
            # 使用 'Ay' 这种字符来确定比较通用的行高
            bbox = font.getbbox(GeneratorConfig.height_calculation_char) 
            line_height = bbox[3] - bbox[1] + GeneratorConfig.line_spacing # 额外加 10px 行间距
        except:
            line_height = GeneratorConfig.line_height # 兜底默认值

        # 遍历每一段文本
        for paragraph in text.split('\n'):
            current_line = ""
            for char in paragraph:
                test_line = current_line + char
                # 获取当前拼接文本的宽度
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

    def get_image(self, settings : Dict):
        """
        Description:
            核心渲染函数，根据设置生成 PIL Image 对象。
            Core rendering function, returns a PIL Image object.

        Args:
            settings (dict): 包含 text, bg_path, font_file, font_size 等配置.

        Returns:
            PIL.Image.Image: 生成的图片对象，如果失败或无内容可能返回默认图.
        """
        # 1. 加载背景
        bg_path = settings.get('bg_path')
        if not bg_path or not os.path.exists(bg_path):
            img = Image.new('RGB', (GeneratorConfig.image_width, GeneratorConfig.image_height), 
                            color=GeneratorConfig.default_bg_color)
        else:
            try:
                img = Image.open(bg_path).convert('RGB')
                if img.size != (GeneratorConfig.image_width, GeneratorConfig.image_height):
                    img = img.resize((GeneratorConfig.image_width, GeneratorConfig.image_height), 
                                     Image.Resampling.LANCZOS)
            except Exception as e:
                print(f"背景加载失败: {e}")
                img = Image.new('RGB', (GeneratorConfig.image_width, GeneratorConfig.image_height), 
                                color=GeneratorConfig.default_bg_color)

        draw = ImageDraw.Draw(img)
        text = settings.get('text', '')
        if not text:
            return img

        # 2. 加载字体
        font_path = os.path.join(self.font_folder, settings.get('font_file', ''))
        max_font_size = settings.get('font_size', GeneratorConfig.max_font_size)
        
        # 字体自适应算法
        current_size = max_font_size
        min_size = GeneratorConfig.min_font_size
        final_font = None
        final_lines = []
        final_line_h = 0
        
        # 绘图区域限制
        draw_area_w = GeneratorConfig.draw_area_w
        draw_area_bottom_y = GeneratorConfig.draw_area_bottom_y
        draw_area_limit_h = GeneratorConfig.draw_area_limit_h

        while current_size >= min_size:
            try:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, current_size)
                else:
                    font = ImageFont.load_default()
                
                lines, h, line_h = self._calculate_wrapped_text(text, font, draw_area_w)
                
                if h <= draw_area_limit_h:
                    final_font = font
                    final_lines = lines
                    final_line_h = line_h
                    break
            except Exception as e:
                print(f"字体计算错误: {e}")
            
            current_size -= GeneratorConfig.font_size_step
        
        if final_font is None:
            final_font = ImageFont.load_default()
            final_lines = [text]
            final_line_h = GeneratorConfig.line_height

        # 3. 绘制文字
        total_h = len(final_lines) * final_line_h
        start_y = draw_area_bottom_y - total_h
        
        text_color = settings.get('text_color', GeneratorConfig.default_text_color)
        use_outline = settings.get('use_outline', False)
        outline_w = settings.get('outline_width', GeneratorConfig.default_outline_width)

        for i, line in enumerate(final_lines):
            line_w = final_font.getlength(line)
            x = (GeneratorConfig.image_width - line_w) // 2
            y = start_y + i * final_line_h

            if use_outline:
                draw.text((x, y), line, font=final_font, fill=text_color, 
                          stroke_width=outline_w, stroke_fill=(0,0,0))
            else:
                draw.text((x, y), line, font=final_font, fill=text_color)

        return img