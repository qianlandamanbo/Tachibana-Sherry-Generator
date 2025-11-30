import threading
import time
import win32con
import win32gui
import win32process
import psutil
from typing import Optional

# 导入C扩展
import keyboardhook

class KeyboardHookManager:
    def __init__(self, app_instance):
        self.app = app_instance
        self.is_listening = False
        self.is_simulating_key = False
        self.current_hotkey_mode = 0  # 0=enter, 1=ctrl+enter
        self._was_listening = False  # 用于暂停/恢复状态
        
        # 监听模式设置
        self.allowed_processes = ["wechat.exe", "weixin.exe", "qq.exe", "tim.exe"]
        self.select_all_hotkey = "ctrl+a"
        self.cut_hotkey = "ctrl+x"
        self.paste_hotkey = "ctrl+v"
        self.send_hotkey = "enter"
        self.delay = 0.2
        
        # C扩展回调设置
        self._c_callback_set = False

    def _c_keyboard_callback(self, vk_code):
        """C扩展的键盘回调函数"""
        if not self.is_listening or self.is_simulating_key:
            return
        
        # 检查是否在目标应用中
        current_process = self.get_foreground_window_process_name()
        if current_process and current_process in self.allowed_processes:
            # 立即处理热键
            self.app._append_log(f"检测到热键按下，vk_code: {vk_code}")
            threading.Thread(target=self._safe_process_hotkey, daemon=True).start()

    def start_listener(self):
        """开始监听"""
        try:
            self.stop_listener()
            
            # 更新热键模式
            hotkey = self.app.var_hotkey.get()
            if hotkey == "enter":
                self.current_hotkey_mode = 0
            elif hotkey == "ctrl+enter":
                self.current_hotkey_mode = 1
            
            # 创建回调函数
            import ctypes
            callback_type = ctypes.CFUNCTYPE(None, ctypes.c_int)
            self._c_callback = callback_type(self._c_keyboard_callback)
            
            # 设置钩子
            result = keyboardhook.set_keyboard_hook(self._c_callback, self.current_hotkey_mode)
            self._c_callback_set = True
            
            if result:
                self.is_listening = True
                mode_text = "Enter" if self.current_hotkey_mode == 0 else "Ctrl+Enter"
                self.app._append_log(f"监听模式已启动 - 热键: {mode_text}")
                self.app._append_log("使用C扩展键盘钩子")
                return True
            else:
                self.app._append_log("C扩展钩子设置失败", is_error=True)
                return False
                
        except Exception as e:
            self.app._append_log(f"启动监听失败: {e}", is_error=True)
            return False

    def stop_listener(self):
        """停止监听"""
        try:
            if self._c_callback_set:
                keyboardhook.remove_keyboard_hook()
                self._c_callback_set = False
            
            self.is_listening = False
            self.app._append_log("监听模式已停止")
        except Exception as e:
            self.app._append_log(f"停止监听失败: {e}", is_error=True)

    def pause_listener(self):
        """暂停监听"""
        if self.is_listening:
            self._was_listening = True
            self.stop_listener()
        else:
            self._was_listening = False

    def resume_listener(self):
        """恢复监听"""
        if hasattr(self, '_was_listening') and self._was_listening:
            self.start_listener()

    def get_foreground_window_process_name(self) -> Optional[str]:
        """获取前台窗口进程名"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            process = psutil.Process(pid)
            return process.name().lower()
        except:
            return None

    def _safe_process_hotkey(self):
        """安全处理热键"""
        try:
            self.app.root.after(0, self._process_hotkey_triggered)
        except:
            pass

    def _process_hotkey_triggered(self):
        """处理热键触发"""
        try:
            # 获取当前窗口信息
            hwnd = win32gui.GetForegroundWindow()
            active_window_title = win32gui.GetWindowText(hwnd)
            current_process = self.get_foreground_window_process_name()
            
            self.app._append_log(f"活动窗口: {active_window_title}")
            self.app._append_log(f"检测到进程: {current_process}")
            
            if not current_process or current_process not in self.allowed_processes:
                self.app._append_log("不在目标应用中，取消处理")
                return
            
            # 确保窗口处于前台
            self._bring_window_to_front(hwnd)
            time.sleep(0.1)  # 等待窗口激活
            
            # 使用剪切方式获取文本
            self.app._append_log("开始获取输入文本...")
            text, old_clipboard = self._cut_all_and_get_text()
            
            if not text or not text.strip():
                self.app._append_log("未检测到文本内容，取消处理")
                import pyperclip
                pyperclip.copy(old_clipboard)
                return
                
            self.app._append_log(f"获取到文本: {text}")
            
            # 生成并发送表情包
            self.app._generate_and_send_meme(text, active_window_title, old_clipboard)
            
        except Exception as e:
            self.app._append_log(f"处理热键时出错: {e}", is_error=True)

    def _bring_window_to_front(self, hwnd):
        """将窗口带到前台"""
        try:
            # 先尝试简单的激活
            win32gui.SetForegroundWindow(hwnd)
            
            # 如果上面的方法不行，尝试模拟Alt键
            import keyboard
            keyboard.press('alt')
            time.sleep(0.05)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.05)
            keyboard.release('alt')
        except:
            pass

    def _cut_all_and_get_text(self):
        """剪切文本获取方法"""
        try:
            import pyperclip
            
            # 备份原剪贴板
            old_clip = pyperclip.paste()
            self.app._append_log(f"原剪贴板内容: {repr(old_clip)}")

            # 清空剪贴板，防止读到旧数据
            pyperclip.copy("")
            time.sleep(0.1)

            # 发送 Ctrl+A 全选
            self.app._append_log("发送Ctrl+A全选")
            self._simulate_key_press(self.select_all_hotkey)
            time.sleep(self.delay)
            
            # 发送 Ctrl+X 剪切
            self.app._append_log("发送Ctrl+X剪切")
            self._simulate_key_press(self.cut_hotkey)
            time.sleep(self.delay)

            # 获取剪切后的内容
            new_clip = pyperclip.paste()
            self.app._append_log(f"剪切后剪贴板内容: {repr(new_clip)}")

            return new_clip, old_clip
        except Exception as e:
            self.app._append_log(f"剪切文本失败: {e}", is_error=True)
            return None, None

    def _simulate_key_press(self, key):
        """模拟按键"""
        self.is_simulating_key = True
        try:
            import keyboard
            keyboard.press_and_release(key)
        except Exception as e:
            self.app._append_log(f"模拟按键失败: {e}", is_error=True)
        finally:
            threading.Timer(0.5, self._reset_simulation_flag).start()
            
    def _reset_simulation_flag(self):
        """重置模拟按键标志"""
        self.is_simulating_key = False