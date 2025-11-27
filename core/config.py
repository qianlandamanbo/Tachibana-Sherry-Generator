class GeneratorConfig:
    # 文件夹路径
    # 该路径的 Base 为 根目录
    bg_folder = "background_images/"
    font_folder = "Font/"
    output_folder = "output_images/"

    # 绘制图片的默认尺寸
    image_width = 900  # 宽度
    image_height = 900  # 高度

    # 绘图区域限制
    draw_area_w = 800  # 宽度最大不超过这个数
    draw_area_bottom_y = 880  # 最大高度不超过这个数
    draw_area_limit_h = 300  # 绘制字体区域最大高度

    # 计算换行参数
    max_width = 600
    line_height = 30  # 兜底默认值
    line_spacing = 10  # 行间距

    # Font字体大小范围
    max_font_size = 100
    min_font_size = 20
    font_size_step = 5

    # 默认颜色
    default_bg_color = 'gray'
    default_text_color = (255, 255, 255)

    # 默认字符用于计算行高
    height_calculation_char = "Ay"

    # 描边默认值
    default_outline_width = 2