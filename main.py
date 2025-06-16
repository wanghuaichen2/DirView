import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import subprocess
import platform
from PIL import Image, ImageTk

# 加载本地图标（你需要将对应图标保存为 file.png 和 folder.png）
icon_folder = None
icon_file = None
icon_images = {}  # 缓存图标

def load_icons():
    global icon_folder, icon_file
    icon_folder = ImageTk.PhotoImage(Image.open("./logo/folder.png").resize((16, 16), Image.Resampling.LANCZOS))
    icon_file = ImageTk.PhotoImage(Image.open("./logo/file.png").resize((16, 16), Image.Resampling.LANCZOS))
    icon_images['folder'] = icon_folder
    icon_images['file'] = icon_file

def build_tree(parent, path):
    try:
        items = sorted(os.listdir(path))
        for item in items:
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                node = tree.insert(parent, "end", text=item, image=icon_folder, open=False, values=[item_path])
                build_tree(node, item_path)
            else:
                tree.insert(parent, "end", text=item, image=icon_file, values=[item_path])
    except PermissionError:
        pass

def choose_directory():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        tree.delete(*tree.get_children())
        base = os.path.basename(folder_selected.rstrip("/\\"))
        root_node = tree.insert("", "end", text=base, image=icon_folder, open=True, values=[folder_selected])
        build_tree(root_node, folder_selected)

def open_item(event):
    selected_item = tree.focus()
    if not selected_item:
        return
    path = tree.item(selected_item, 'values')[0]
    abspath = os.path.abspath(path)
    if platform.system() == "Windows":
        subprocess.run(["explorer", "/select,", abspath])
    elif platform.system() == "Darwin":
        subprocess.run(["open", "-R", abspath])
    else:
        folder = abspath if os.path.isdir(abspath) else os.path.dirname(abspath)
        subprocess.run(["xdg-open", folder])

def expand_all():
    def recurse_expand(item):
        tree.item(item, open=True)
        for child in tree.get_children(item):
            recurse_expand(child)
    for root_item in tree.get_children():
        recurse_expand(root_item)

def collapse_all():
    def recurse_collapse(item):
        tree.item(item, open=False)
        for child in tree.get_children(item):
            recurse_collapse(child)
    for root_item in tree.get_children():
        recurse_collapse(root_item)

# 创建主窗口
root = tk.Tk()
root.title("📂 文件目录树查看器")
root.geometry("800x600")
root.configure(bg="#f2f2f2")

# 加载图标
load_icons()

style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview",
                background="#ffffff",
                foreground="#333333",
                rowheight=28,
                fieldbackground="#f2f2f2",
                font=("Times New Roman", 10))
style.configure("Treeview.Heading", font=("Microsoft YaHei", 11, "bold"))
style.map("Treeview",
          background=[("selected", "#cce5ff")],
          foreground=[("selected", "#000000")])

# 替换 Treeview 文本绘制逻辑以支持中英混排字体（需补丁方式或使用自定义组件）
def mixed_font_text(text):
    # 暂时简单判断，只是演示性地换字体，不支持精细控制
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return ("Microsoft YaHei", 10)
    return ("Times New Roman", 10)

frame = tk.Frame(root, bg="#f2f2f2")
frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

btn_frame = tk.Frame(frame, bg="#f2f2f2")
btn_frame.pack(fill=tk.X, pady=10)

btn = tk.Button(btn_frame, text="选择文件夹", command=choose_directory,
                font=("Microsoft YaHei", 10), bg="#4CAF50", fg="white",
                activebackground="#45a049", relief=tk.FLAT, padx=10, pady=5)
btn.pack(side=tk.LEFT, padx=5)

# 右侧展开/合并按钮组
right_btn_frame = tk.Frame(btn_frame, bg="#f2f2f2")
right_btn_frame.pack(side=tk.RIGHT)

expand_btn = tk.Button(right_btn_frame, text="展开", command=expand_all,
                       font=("Microsoft YaHei", 9), bg="#2196F3", fg="white",
                       activebackground="#1976D2", relief=tk.FLAT, padx=8, pady=4)
expand_btn.pack(side=tk.LEFT, padx=2)

collapse_btn = tk.Button(right_btn_frame, text="合并", command=collapse_all,
                         font=("Microsoft YaHei", 9), bg="#FF9800", fg="white",
                         activebackground="#F57C00", relief=tk.FLAT, padx=8, pady=4)
collapse_btn.pack(side=tk.LEFT, padx=2)

# 文件目录树控件 + 滚动条容器
tree_container = tk.Frame(frame)
tree_container.pack(fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(tree_container, orient="vertical")
scrollbar.pack(side="right", fill="y")

tree = ttk.Treeview(tree_container, yscrollcommand=scrollbar.set)
tree.pack(side="left", fill=tk.BOTH, expand=True)
tree.bind("<Double-1>", open_item)

scrollbar.config(command=tree.yview)

# 启动主事件循环
root.mainloop()
