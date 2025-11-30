import win32clipboard
from PIL import Image
from io import BytesIO
import pyperclip

def copy_image_to_clipboard(image: Image.Image):
    """复制图片到剪贴板"""
    try:
        output = BytesIO()
        image.convert("RGB").save(output, "BMP")
        data = output.getvalue()[14:]
        output.close()

        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        return False

def restore_clipboard(content):
    """恢复剪贴板内容"""
    try:
        pyperclip.copy(content)
    except:
        pass