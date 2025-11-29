import re
import os
from PIL import Image
import memeapp
import tkinter as tk
from tkinter import ttk

class Drag_fileManagement:

    def __init__(self, app_ref=None) -> None:
        self.app = app_ref
        self.app: memeapp.MemeApp

    def on_drop_file(self, event):
        """处理拖拽放下的文件"""
        files = self.parse_dropped_files(event.data)
        self.process_data(files)

    def process_data(self, files):
        """处理列表图片数据"""
        if files and self.app:
            current_files = (
                list(self.app.selected_files)
                if isinstance(self.app.selected_files, (list, tuple))
                else []
            )
            new_files = list(files)

            for f in new_files:
                if f not in current_files:
                    filename = os.path.basename(f)
                    current_files.append(filename)
                    # 如果用户主动拖入，说明他反悔了，从黑名单移除
                    if filename in self.app.ignored_files:
                        self.app.ignored_files.remove(filename)
                        self.app.log(f"文件 {filename} 已移出黑名单")
                    # 打开图片
                    try:
                        img = Image.open(f)
                        # 构造目标路径
                        target = os.path.join(self.app.generator.bg_folder, filename)
                        # 保存图片
                        img.save(target)
                        last_added_filename = filename
                    except Exception as e:
                        print(f"Error processing file {f}: {e}")
            self.app.selected_files = current_files
            self.app.log(f"已添加 {len(new_files)} 个文件")

            # 如果成功添加了图片，就选中最后一张
            if last_added_filename:
                self.app.log(f"已添加并选中: {last_added_filename}")

                # 先刷新下拉框的数据源
                if hasattr(self.app, "refresh_dropdowns"):
                    self.app.refresh_dropdowns()

                # 设置下拉框选中该文件
                self.app.combo_bg.set(last_added_filename)
                self.app.combo_bg_listener.set(last_added_filename)

                # 更新变量绑定
                self.app.var_bg_file.set(last_added_filename)

                # 立即触发预览更新
                self.app._trigger_preview_update()  # 刷新经典模式预览
                self.app._update_listener_preview()  # 刷新监听模式预览

    def parse_dropped_files(self, data):
        """解析拖拽进来的文件路径字符串"""
        filepaths = []
        # 匹配 {C:/path with space/file.jpg} 或 C:/path/file.jpg
        pattern = r"\{.*?\}|\S+"
        matches = re.findall(pattern, data)

        for match in matches:
            # 去除可能存在的大括号
            path = match.strip("{}")
            if os.path.isfile(path):
                # 检查是否是图片格式
                if path.lower().endswith((".png", ".jpeg", ".bmp", ".jpg", ".webp")):
                    filepaths.append(path)

        return tuple(filepaths)

    def open_file_manager(self):
        """打开文件管理弹窗"""
        if not self.app.selected_files:
            self.app.log("⚠️ 列表为空，无需管理")
            return

        # 创建弹窗
        top = tk.Toplevel(self.app.root)
        top.title("文件列表管理")
        top.geometry("500x400")
        top.transient(self.app.root)  # 设置为工具窗口
        top.grab_set()  # 模态窗口（禁止操作主窗口直到关闭此窗口）

        # --- 标题栏 ---
        header = ttk.Frame(top)
        header.pack(fill="x", padx=10, pady=10)

        # 保存 label 的引用以便后续更新文字
        self.lbl_count = ttk.Label(
            header,
            text=f"已选文件 ({len(self.app.selected_files)})",
            font=("Microsoft YaHei", 16, "bold"),
        )
        self.lbl_count.pack(side="left")

        ttk.Button(
            header, text="清空全部", width=10, command=lambda: self.clear_all_files(top)
        ).pack(side="right")

        # 创建外部容器
        container = ttk.Frame(top)
        container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 创建 Canvas和Scrollbar
        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        # 创建实际放内容的Frame,放在Canvas里
        scrollable_frame = ttk.Frame(canvas)

        # 逻辑绑定:当Frame大小改变时，更新Canvas的滚动区域
        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        # 获取 create_window 返回的 ID
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        # 监听Canvas大小变化，强制让内部Frame宽度等于Canvas宽度
        canvas.bind(
            "<Configure>", lambda e: canvas.itemconfig(window_id, width=e.width)
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 渲染列表
        self.render_file_list(scrollable_frame, top)

        # 绑定鼠标滚轮事件
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # 只有在鼠标进入区域时才绑定滚轮
        canvas.bind(
            "<Enter>", lambda _: canvas.bind_all("<MouseWheel>", _on_mousewheel)
        )
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))

    def render_file_list(self, parent_frame, top_window):
        """渲染文件列表项"""
        # 清空现有显示
        for widget in parent_frame.winfo_children():
            widget.destroy()

        for i, file_path in enumerate(self.app.selected_files):
            # 创建每一行的容器
            row = ttk.Frame(parent_frame)
            row.pack(fill="x", pady=2)

            # 删除按钮
            del_btn = ttk.Button(
                row,
                text="❌",
                width=3,
                command=lambda f=file_path: self.remove_file(
                    f, parent_frame, top_window
                ),
            )
            del_btn.pack(side="right", padx=(10, 0))

            # 处理长文件名
            filename = os.path.basename(file_path)
            display_name = self.truncate_filename(filename)

            # 文件名标签
            label = ttk.Label(row, text=f"{i+1}. {display_name}", anchor="w")
            label.pack(side="left", padx=10, pady=5, fill="x", expand=True)

    def remove_file(self, file_path, parent_frame, top_window):
        """从列表中移除指定文件"""
        if file_path in self.app.selected_files:
            self.app.selected_files.remove(file_path)

            self.app.log(f"已移除: {os.path.basename(file_path)}")
            self.app.refresh_dropdowns()
            filename = os.path.basename(file_path)
            self.app.ignored_files.add(filename)
            # 如果删完了，直接关闭窗口
            if not self.app.selected_files:
                top_window.destroy()
            else:
                # 重新渲染列表
                self.render_file_list(parent_frame, top_window)
                # 更新标题数量
                if hasattr(self, "lbl_count"):
                    self.lbl_count.configure(
                        text=f"已选文件 ({len(self.app.selected_files)})"
                    )

    def clear_all_files(self, top_window):
        """清空所有文件，并全部加入黑名单，防止自动恢复"""
        if not self.app.selected_files:
            return

        # 将现有所有文件加入黑名单
        for file_path in self.app.selected_files:
            filename = os.path.basename(file_path)
            self.app.ignored_files.add(filename)

        # 清空列表
        count = len(self.app.selected_files)
        self.app.selected_files.clear()

        # 刷新主界面下拉框
        if hasattr(self.app, "refresh_dropdowns"):
            self.app.refresh_dropdowns()

        self.app.log(f"已清空 {count} 个文件")

        # 4. 关闭管理窗口
        top_window.destroy()

    def truncate_filename(self, filename, max_length=35):
        """辅助函数：如果文件名太长，保留头尾，中间用 ... 代替"""
        if len(filename) <= max_length:
            return filename

        # 保留前15个字符，保留后15个字符（包含后缀）
        head = 15
        tail = 15
        if len(filename) < head + tail:
            return filename

        return filename[:head] + "..." + filename[-tail:]
