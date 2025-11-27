import time
import win32clipboard
import pyperclip
import keyboard  # 用于模拟 Ctrl+C/V 操作
from io import BytesIO

class ClipboardManager:
    """负责剪贴板的读写和模拟按键操作"""
    
    @staticmethod
    def get_text_safe():
        """
        Description: 安全获取剪贴板文本
        """
        try:
            return pyperclip.paste()
        except Exception:
            return ""

    @staticmethod
    def set_text(text):
        """
        Description: 设置剪贴板文本
        """
        pyperclip.copy(text)

    @staticmethod
    def set_image(pil_image):
        """
        Description: 
            将 PIL Image 对象写入 Windows 剪贴板。
            Writes PIL Image to Windows clipboard.
        
        Args:
            pil_image (PIL.Image): 图片对象
            
        Returns:
            bool: 是否成功
        """
        try:
            output = BytesIO()
            # 必须保存为 BMP 格式才能被 Windows 剪贴板识别为 DIB
            pil_image.save(output, "BMP")
            data = output.getvalue()[14:]  # 去掉 BMP 文件头(14字节)
            output.close()
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            print(f"Clipboard Error: {e}")
            return False

    @staticmethod
    def cut_text_via_hotkey(delay=0.1):
        """
        Description:
            模拟 Ctrl+A -> Ctrl+X 操作，并返回剪切到的文本。
            Simulates Ctrl+A, Ctrl+X and returns the clipped text.
        
        Returns:
            tuple: (new_text, old_clipboard_backup)
        """
        # 1. 备份旧剪贴板
        old_clip = pyperclip.paste()
        # 2. 清空
        pyperclip.copy("")
        # 3. 模拟按键
        keyboard.send("ctrl+a")
        time.sleep(0.05) # 稍微等待按键响应
        keyboard.send("ctrl+x")
        time.sleep(delay) # 等待系统剪切完成
        
        # 4. 获取新内容
        new_text = pyperclip.paste()
        return new_text, old_clip

    @staticmethod
    def paste_and_send(delay=0.1):
        """
        Description: 模拟 Ctrl+V -> Enter
        """
        keyboard.send("ctrl+v")
        time.sleep(delay)
        keyboard.send("enter")