#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试图片自适应缩放模式
Test image adaptive resize modes
"""

import os
from utils.generator import ImageGenerator

def test_resize_modes():
    """测试两种缩放模式的效果"""
    gen = ImageGenerator()
    
    # 获取背景图片和字体文件
    bg_files = [os.path.join(gen.bg_folder, f) for f in os.listdir(gen.bg_folder) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    font_files = [os.path.join(gen.font_folder, f) for f in os.listdir(gen.font_folder) 
                  if f.lower().endswith(('.ttf', '.otf'))]
    
    if not bg_files or not font_files:
        print("缺少背景图片或字体文件，无法测试")
        return
    
    # 选择一个非正方形的背景图片来测试自适应效果
    # 查找一个宽高比不是1:1的图片
    test_bg = None
    for bg_file in bg_files:
        try:
            from PIL import Image
            img = Image.open(bg_file)
            width, height = img.size
            if width != height:  # 非正方形图片
                test_bg = bg_file
                print(f"选择非正方形背景图片: {os.path.basename(bg_file)}, 尺寸: {width}x{height}")
                break
        except:
            continue
    
    if not test_bg:
        test_bg = bg_files[0]
        print(f"使用默认背景图片: {os.path.basename(test_bg)}")
    
    # 测试设置
    settings = {
        'text': '测试图片自适应效果\n包含模式 vs 覆盖模式',
        'text_color': '#000000',
        'font_size': 35,
        'use_outline': True,
        'outline_width': 2,
        'bg_path': test_bg,
        'font_file': font_files[0]
    }
    
    # 测试包含模式
    settings['resize_mode'] = 'contain'
    img_contain = gen.render_image(settings)
    img_contain.save('test_contain_mode.png')
    print(f"包含模式图片已保存: test_contain_mode.png")
    
    # 测试覆盖模式
    settings['resize_mode'] = 'cover'
    img_cover = gen.render_image(settings)
    img_cover.save('test_cover_mode.png')
    print(f"覆盖模式图片已保存: test_cover_mode.png")
    
    print("\n两种缩放模式说明:")
    print("1. 包含模式(contain): 保持图片比例，不拉伸，可能会有留白")
    print("2. 覆盖模式(cover): 填充整个区域，可能会裁剪部分图片")
    print("\n测试完成！请查看生成的图片文件对比效果。")

if __name__ == "__main__":
    test_resize_modes()