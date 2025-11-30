import os
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
from PIL import Image, ImageTk
from generator import ImageGenerator
import keyboard
import pyperclip

# 导入拆分后的模块
from admin_utils import is_admin, request_admin_privileges
from keyboard_hook import KeyboardHookManager
from clipboard_utils import copy_image_to_clipboard, restore_clipboard
from ui_builder import UIBuilder

class MemeApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("橘雪莉表情包生成器V1.2")
        self.root.geometry("1000x700") 
        
        # 检查管理员权限
        self.is_admin = is_admin()
        
        # 初始化各个管理器
        self.keyboard_hook = KeyboardHookManager(self)
        self.ui_builder = UIBuilder(self)
        
        # 配置
        self.settings = {
            'text_color': '#FFFFFF',
            'font_path': self._get_default_font(),
            'use_outline': True,
            'outline_width': 2,
            'current_bg_index': 0,
            'hotkey': 'ctrl+enter',
            'target_text': '请输入文字...'
        }
        
        self.log_messages = []
        self.max_logs = 100
        
        # 初始化图片渲染器
        self.generator = ImageGenerator()
        
        # UI 控件变量
        self.var_text_color = (255, 255, 255) 
        self.var_font_size = tk.IntVar(value=100)
        self.var_use_outline = tk.BooleanVar(value=True)
        self.var_outline_width = tk.IntVar(value=3)
        self.var_bg_file = tk.StringVar()
        self.var_font_file = tk.StringVar()
        self.var_hotkey = tk.StringVar(value='ctrl+enter')
        
        # 内部状态
        self.current_image_obj = None 
        self.current_image_obj_listener = None
        self._preview_job = None 
        
        # 构建界面
        self.ui_builder.setup_ui()
        self._load_resources()
        self._trigger_preview_update()
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _get_default_font(self):
        """获取默认字体"""
        font_path = os.path.join("Font", "NotoSansCJKsc-Regular.otf")
        if os.path.exists(font_path):
            return font_path
        elif os.name == 'nt' and os.path.exists('C:\\Windows\\Fonts\\simsun.ttc'):
            return 'C:\\Windows\\Fonts\\simsun.ttc'
        else:
            return None

    # ==========================================
    #  权限管理功能
    # ==========================================

    def _request_admin_privileges(self):
        """请求管理员权限"""
        try:
            self._append_log("正在请求管理员权限...")
            
            if self.is_admin:
                self._append_log("当前已具有管理员权限")
                messagebox.showinfo("权限信息", "当前已具有管理员权限")
                return True
                
            # 显示确认对话框
            result = messagebox.askyesno(
                "请求管理员权限", 
                "监听模式需要管理员权限才能正常工作。\n\n"
                "点击'是'将以管理员权限重新启动程序。\n"
                "注意：重启后需要重新设置参数。\n\n"
                "是否继续？"
            )
            
            if result:
                self._append_log("用户确认请求管理员权限")
                self.root.destroy()  # 先关闭当前窗口
                
                # 请求管理员权限并重启
                if request_admin_privileges():
                    self._append_log("已请求管理员权限重启")
                else:
                    self._append_log("请求管理员权限失败", is_error=True)
                    messagebox.showerror("错误", "请求管理员权限失败，请手动以管理员权限运行程序")
            else:
                self._append_log("用户取消请求管理员权限")
                
        except Exception as e:
            self._append_log(f"请求管理员权限时出错: {e}", is_error=True)
            messagebox.showerror("错误", f"请求管理员权限时出错: {e}")

    def _check_admin_privileges(self):
        """检查并显示当前权限状态"""
        if self.is_admin:
            self._append_log("当前已具有管理员权限")
            self.lbl_admin_status.config(text="管理员权限: 已获取", foreground="green")
            self.btn_request_admin.config(state=tk.DISABLED)
        else:
            self._append_log("警告: 当前没有管理员权限，监听模式可能无法正常工作")
            self.lbl_admin_status.config(text="管理员权限: 未获取", foreground="red")
            self.btn_request_admin.config(state=tk.NORMAL)

    # ==========================================
    #  监听模式控制
    # ==========================================

    def _toggle_listener(self):
        """切换监听状态"""
        if self.keyboard_hook.is_listening:
            self._stop_listener()
        else:
            self._start_listener()

    def _start_listener(self):
        """开始监听"""
        try:
            # 检查管理员权限
            if not self.is_admin:
                self._append_log("警告: 没有管理员权限，监听模式可能无法正常工作", is_error=True)
                result = messagebox.askyesno(
                    "权限警告", 
                    "当前没有管理员权限，监听模式可能无法正常工作。\n\n"
                    "是否继续？"
                )
                if not result:
                    return
            
            if self.keyboard_hook.start_listener():
                self.btn_listen.config(text="停止监听")
                self.lbl_listen_status.config(text="监听运行中")
            else:
                messagebox.showerror("错误", "启动监听失败\n请尝试以管理员权限运行程序")
                
        except Exception as e:
            self._append_log(f"启动监听失败: {e}", is_error=True)

    def _stop_listener(self):
        """停止监听"""
        self.keyboard_hook.stop_listener()
        self.btn_listen.config(text="开始监听")
        self.lbl_listen_status.config(text="监听未启动")

    def _on_hotkey_change(self):
        """热键改变时的处理"""
        self._append_log(f"热键已更改为: {self.var_hotkey.get()}")
        if self.keyboard_hook.is_listening:
            self._stop_listener()
            self._start_listener()

    # ==========================================
    #  表情包生成和发送
    # ==========================================

    def _generate_and_send_meme(self, text, active_window_title, old_clipboard):
        """生成并发送表情包"""
        try:
            self._append_log("开始生成表情包...")
            
            # 生成图片
            bg_path = os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None
            
            settings = {
                'text': text,
                'text_color': self.var_text_color,
                'font_size': self.var_font_size.get(),
                'use_outline': self.var_use_outline.get(),
                'outline_width': self.var_outline_width.get(),
                'bg_path': bg_path,
                'font_file': self.var_font_file.get()
            }
            
            meme_image = self.generator.render_image(settings)
            
            # 复制到剪贴板
            self._append_log("复制图片到剪贴板...")
            if copy_image_to_clipboard(meme_image):
                self._append_log("图片已复制到剪贴板")
                
                # 延迟确保剪贴板操作完成
                time.sleep(0.3)
                
                # 直接发送图片，不恢复剪贴板
                self._append_log("直接发送图片...")
                self._send_image_directly()
                
                # 恢复原始剪贴板内容
                restore_clipboard(old_clipboard)
                
                self._append_log("表情包发送成功！")
            else:
                self._append_log("复制图片到剪贴板失败", is_error=True)
                # 恢复原始剪贴板内容
                restore_clipboard(old_clipboard)
                
        except Exception as e:
            self._append_log(f"生成/发送失败: {e}", is_error=True)
            # 恢复原始剪贴板内容
            restore_clipboard(old_clipboard)

    def _send_image_directly(self):
        """直接发送图片，不经过剪贴板恢复"""
        try:
            # 暂停监听，防止干扰粘贴操作
            was_listening = self.keyboard_hook.is_listening
            if was_listening:
                self.keyboard_hook.pause_listener()
            
            # 粘贴图片
            self.keyboard_hook._simulate_key_press(self.keyboard_hook.paste_hotkey)
            time.sleep(0.3)
            
            # 发送图片
            self.keyboard_hook._simulate_key_press(self.keyboard_hook.send_hotkey)
            time.sleep(0.2)
            
            # 恢复监听
            if was_listening:
                self.keyboard_hook.resume_listener()
                
        except Exception as e:
            self._append_log(f"发送图片失败: {e}", is_error=True)
            # 确保恢复监听
            if was_listening:
                self.keyboard_hook.resume_listener()

    # ==========================================
    #  UI 交互方法
    # ==========================================

    def _append_log(self, message: str, is_error: bool = False):
        """添加日志"""
        timestamp = time.strftime("[%H:%M:%S]")
        log_entry = f"{timestamp} {'[错误]' if is_error else '[信息]'} {message}"
        self.log_messages.append(log_entry)
        if len(self.log_messages) > self.max_logs:
            self.log_messages.pop(0)
        self.root.after(0, self._update_log_ui)

    def _update_log_ui(self):
        """更新日志UI"""
        if hasattr(self, 'log_text'):
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete('1.0', tk.END)
            self.log_text.insert(tk.END, "\n".join(self.log_messages))
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

    def _load_resources(self):
        """加载资源文件"""
        try:
            # 加载背景图片
            bgs = self.generator.get_files(self.generator.bg_folder, ('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
            self.combo_bg['values'] = bgs
            self.combo_bg_listener['values'] = bgs
            if bgs:
                self.combo_bg.current(0)
                self.combo_bg_listener.current(0)
                self.var_bg_file.set(bgs[0])
            
            # 加载字体文件 - 支持更多字体格式
            font_extensions = ('.ttf', '.otf', '.ttc', '.fon', '.fnt')
            fonts = self.generator.get_files(self.generator.font_folder, font_extensions)
            
            # 如果没有找到字体文件，尝试在系统字体目录中查找
            if not fonts:
                self._append_log("字体文件夹中没有找到字体文件，尝试查找系统字体...")
                fonts = self._find_system_fonts()
            
            self.combo_font['values'] = fonts
            self.combo_font_listener['values'] = fonts
            if fonts:
                self.combo_font.current(0)
                self.combo_font_listener.current(0)
                self.var_font_file.set(fonts[0])
                self._append_log(f"成功加载 {len(fonts)} 个字体文件")
            else:
                self._append_log("警告: 没有找到任何字体文件", is_error=True)
                
        except Exception as e:
            self._append_log(f"加载资源时出错: {e}", is_error=True)

    def _find_system_fonts(self):
        """查找系统字体"""
        fonts = []
        try:
            # Windows 系统字体目录
            system_font_dirs = [
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'Windows', 'Fonts')
            ]
            
            for font_dir in system_font_dirs:
                if os.path.exists(font_dir):
                    font_files = self.generator.get_files(font_dir, ('.ttf', '.otf', '.ttc'))
                    fonts.extend(font_files)
                    if font_files:
                        self._append_log(f"在系统字体目录找到 {len(font_files)} 个字体")
        
        except Exception as e:
            self._append_log(f"查找系统字体时出错: {e}", is_error=True)
        
        return fonts

    def _debug_fonts(self):
        """调试字体文件"""
        try:
            self._append_log("=== 字体调试信息 ===")
            
            # 检查字体文件夹
            font_folder = self.generator.font_folder
            self._append_log(f"字体文件夹路径: {font_folder}")
            self._append_log(f"字体文件夹存在: {os.path.exists(font_folder)}")
            
            if os.path.exists(font_folder):
                all_files = os.listdir(font_folder)
                self._append_log(f"字体文件夹中的所有文件: {all_files}")
                
                # 检查各种字体格式
                font_extensions = ('.ttf', '.otf', '.ttc', '.fon', '.fnt')
                font_files = [f for f in all_files if any(f.lower().endswith(ext) for ext in font_extensions)]
                self._append_log(f"识别的字体文件: {font_files}")
                
                # 测试字体加载
                for font_file in font_files:
                    font_path = os.path.join(font_folder, font_file)
                    try:
                        from PIL import ImageFont
                        test_font = ImageFont.truetype(font_path, 20)
                        self._append_log(f"✓ 字体 {font_file} 加载成功")
                    except Exception as e:
                        self._append_log(f"✗ 字体 {font_file} 加载失败: {e}")
            
            self._append_log("=== 字体调试结束 ===")
            
        except Exception as e:
            self._append_log(f"字体调试时出错: {e}", is_error=True)

    def _choose_color(self):
        """选择文字颜色"""
        colors = colorchooser.askcolor(initialcolor='#%02x%02x%02x' % self.var_text_color)
        if colors[0]:
            self.var_text_color = tuple(map(int, colors[0])) 
            self.btn_color.config(bg=colors[1]) 
            self.btn_color_listener.config(bg=colors[1])
            self._trigger_preview_update()
            self._update_listener_preview()

    def _add_background(self):
        """添加新背景图片"""
        path = filedialog.askopenfilename(filetypes=[("Images", "*.png;*.jpg;*.jpeg")])
        if path:
            try:
                img = Image.open(path)
                filename = os.path.basename(path)
                target = os.path.join(self.generator.bg_folder, filename)
                img.save(target)
                self._load_resources() 
                self.combo_bg.set(filename)
                self.combo_bg_listener.set(filename)
                self._trigger_preview_update()
                self._update_listener_preview()
                messagebox.showinfo("成功", "背景已添加")
            except Exception as e:
                messagebox.showerror("错误", f"无法添加图片: {e}")

    def _on_input_change(self, event=None):
        """输入内容变化时的处理"""
        if self._preview_job:
            self.root.after_cancel(self._preview_job)
        self._preview_job = self.root.after(300, self._trigger_preview_update)

    def _trigger_preview_update(self):
        """触发预览更新"""
        settings = {
            'text': self.text_input.get("1.0", tk.END).strip(),
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }
        thread = threading.Thread(target=self._generate_task, args=(settings,), daemon=True)
        thread.start()

    def _generate_task(self, settings):
        """生成图片任务"""
        image = self.generator.render_image(settings)
        self.root.after(0, self._update_preview_ui, image)

    def _update_preview_ui(self, pil_image):
        """更新预览UI"""
        self.current_image_obj = pil_image 
        win_w = self.lbl_preview.winfo_width()
        win_h = self.lbl_preview.winfo_height()
        if win_w < 10 or win_h < 10: return 
        ratio = min(win_w / 900, win_h / 900)
        new_size = (int(900 * ratio), int(900 * ratio))
        try:
            preview_img = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(preview_img)
            self.lbl_preview.config(image=tk_img, text="") 
            self.lbl_preview.image = tk_img 
        except Exception as e:
            print(f"预览更新失败: {e}")

    def _on_resize_preview(self, event):
        """预览区域大小变化时的处理"""
        if self.current_image_obj:
            self._update_preview_ui(self.current_image_obj)

    def _save_image(self):
        """保存图片"""
        if not self.current_image_obj:
            return
        timestamp = time.strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.png"
        save_path = os.path.join("output_images", filename)
        try:
            self.current_image_obj.save(save_path)
            messagebox.showinfo("保存成功", f"图片已保存至:\n{save_path}")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def _test_generate(self):
        """测试生成图片"""
        test_text = "这是一条测试消息，用于验证监听模式功能是否正常工作！"
        self._append_log(f"测试生成图片，文本: {test_text}")
        settings = {
            'text': test_text,
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }
        try:
            image = self.generator.render_image(settings)
            if image:
                self._append_log("测试生成成功！")
                timestamp = time.strftime("%Y%m%d%H%M%S")
                test_path = os.path.join("output_images", f"test_{timestamp}.png")
                image.save(test_path)
                self._append_log(f"测试图片已保存至: {test_path}")
                self.root.after(0, lambda: self._update_preview_ui_listener(image))
            else:
                self._append_log("测试生成失败")
        except Exception as e:
            self._append_log(f"测试生成时出错: {e}")

    def _update_listener_preview(self):
        """更新监听模式预览"""
        settings = {
            'text': '预览文本 - 这是监听模式的预览效果',
            'text_color': self.var_text_color,
            'font_size': self.var_font_size.get(),
            'use_outline': self.var_use_outline.get(),
            'outline_width': self.var_outline_width.get(),
            'bg_path': os.path.join(self.generator.bg_folder, self.var_bg_file.get()) if self.var_bg_file.get() else None,
            'font_file': self.var_font_file.get()
        }
        thread = threading.Thread(target=self._generate_preview_task, args=(settings,), daemon=True)
        thread.start()

    def _generate_preview_task(self, settings):
        """生成预览任务"""
        image = self.generator.render_image(settings)
        self.root.after(0, self._update_preview_ui_listener, image)

    def _update_preview_ui_listener(self, pil_image):
        """更新监听模式预览UI"""
        self.current_image_obj_listener = pil_image
        win_w = self.lbl_preview_listener.winfo_width()
        win_h = self.lbl_preview_listener.winfo_height()
        if win_w < 10 or win_h < 10: 
            return
        ratio = min(win_w / 900, win_h / 900)
        new_size = (int(900 * ratio), int(900 * ratio))
        try:
            preview_img = pil_image.resize(new_size, Image.Resampling.LANCZOS)
            tk_img = ImageTk.PhotoImage(preview_img)
            self.lbl_preview_listener.config(image=tk_img, text="")
            self.lbl_preview_listener.image = tk_img
        except Exception as e:
            print(f"预览更新失败: {e}")

    def _on_resize_preview_listener(self, event):
        """监听模式预览区域大小变化时的处理"""
        if hasattr(self, 'current_image_obj_listener') and self.current_image_obj_listener:
            self._update_preview_ui_listener(self.current_image_obj_listener)

    def _on_listener_resource_change(self, event=None):
        """监听模式资源变化时的处理"""
        self._update_listener_preview()

    def _on_closing(self):
        """窗口关闭事件处理"""
        if self.keyboard_hook.is_listening:
            self._stop_listener()
        choice = self._show_exit_dialog()
        if choice == "exit":
            try:
                keyboard.unhook_all()
            except:
                pass
            self.root.destroy()
        elif choice == "background":
            self.root.withdraw()
            self._append_log("程序已最小化到后台运行")

    def _show_exit_dialog(self):
        """显示退出对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("退出选项")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        ttk.Label(dialog, text="请选择退出方式:", font=("Microsoft YaHei", 10)).pack(pady=20)
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        result = {"choice": "cancel"}
        def set_choice(choice):
            result["choice"] = choice
            dialog.destroy()
        ttk.Button(btn_frame, text="直接退出", command=lambda: set_choice("exit")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="后台运行", command=lambda: set_choice("background")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
        self.root.wait_window(dialog)
        return result["choice"]

    def run(self):
        """运行应用程序"""
        try:
            # 初始化权限状态
            self._check_admin_privileges()
            self.root.mainloop()
        except KeyboardInterrupt:
            self._safe_shutdown()
        except Exception as e:
            print(f"程序异常: {e}")
            self._safe_shutdown()

    def _safe_shutdown(self):
        """安全关闭程序"""
        try:
            if hasattr(self, 'keyboard_hook') and self.keyboard_hook.is_listening:
                self._stop_listener()
            if hasattr(self, 'root'):
                self.root.quit()
                self.root.destroy()
        except:
            pass