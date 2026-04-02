# -*- coding: utf-8 -*-
"""
VaultX GUI 界面模块
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional

from .vault import VaultManager, VaultData, DATA_DIR
from .password import PasswordGenerator

# 应用配置
APP_NAME = "VaultX"
APP_VERSION = "1.0.0"
DEFAULT_AUTO_LOCK = 300  # 5分钟自动锁定


class VaultXApp:
    """VaultX 主应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("950x680")
        self.root.minsize(850, 550)
        
        # 设置窗口图标
        self._set_icon()
        
        # 管理器
        self.manager = VaultManager()
        self.is_unlocked = False
        
        # 自动锁定
        self.auto_lock_seconds = DEFAULT_AUTO_LOCK
        self.last_activity = time.time()
        self.auto_lock_timer = None
        
        # 剪贴板自动清除
        self.clipboard_clear_timer = None
        self.clipboard_clear_seconds = 30
        
        # 样式
        self._setup_styles()
        
        # 初始界面
        self._show_lock_screen()
        
        # 启动自动锁定检测
        self._start_auto_lock_check()
        
        # 绑定活动检测
        self.root.bind_all("<Any-KeyPress>", self._on_activity)
        self.root.bind_all("<Any-Button>", self._on_activity)
        
        # 窗口关闭处理
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _set_icon(self):
        """设置窗口图标"""
        # 尝试加载图标
        icon_paths = [
            Path(__file__).parent / "icon.ico",
            Path(__file__).parent.parent / "icon.ico",
        ]
        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    self.root.iconbitmap(str(icon_path))
                    break
                except:
                    pass
    
    def _setup_styles(self):
        """设置样式 - 高对比度配色方案"""
        style = ttk.Style()
        
        # 使用clam主题作为基础
        style.theme_use('clam')
        
        # 配色方案 - 高对比度，清晰可读
        self.colors = {
            # 背景色 - 使用较亮的深色背景
            "bg": "#2d2d44",           # 主背景（深蓝灰）
            "bg_light": "#3d3d5c",     # 浅一点背景
            "card": "#363654",          # 卡片背景
            
            # 前景色 - 高对比度
            "fg": "#f0f0f5",           # 主文字（亮白）
            "fg_dim": "#b0b0c0",       # 次要文字
            "fg_dark": "#808090",      # 暗淡文字
            
            # 强调色
            "accent": "#5c9eff",       # 主强调色（亮蓝）
            "accent_hover": "#4a8ae0", # 悬停色
            "accent_dark": "#3d6cb0",  # 深强调色
            
            # 状态色
            "success": "#50c878",      # 成功（绿）
            "warning": "#ffb340",      # 警告（橙）
            "error": "#ff5c5c",        # 错误（红）
            
            # 输入框
            "input_bg": "#28283a",     # 输入框背景
            "input_fg": "#ffffff",     # 输入框文字
            
            # 选中状态
            "select_bg": "#5c9eff",    # 选中背景
            "select_fg": "#ffffff",    # 选中文字
        }
        
        # 窗口背景
        self.root.configure(bg=self.colors["bg"])
        
        # ===== Frame 样式 =====
        style.configure("TFrame", background=self.colors["bg"])
        style.configure("Card.TFrame", background=self.colors["card"])
        
        # ===== Label 样式 =====
        style.configure("TLabel", 
                       background=self.colors["bg"], 
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10))
        style.configure("Title.TLabel",
                       background=self.colors["bg"],
                       font=("Segoe UI", 22, "bold"),
                       foreground=self.colors["accent"])
        style.configure("Subtitle.TLabel",
                       background=self.colors["bg"],
                       font=("Segoe UI", 13),
                       foreground=self.colors["fg"])
        style.configure("Small.TLabel",
                       background=self.colors["bg"],
                       font=("Segoe UI", 9),
                       foreground=self.colors["fg_dim"])
        
        # ===== Button 样式 =====
        style.configure("TButton", 
                       font=("Segoe UI", 10),
                       padding=(12, 6),
                       background=self.colors["accent"],
                       foreground="white")
        style.map("TButton",
                 background=[("active", self.colors["accent_hover"]),
                            ("pressed", self.colors["accent_dark"])],
                 foreground=[("active", "white"), ("pressed", "white")])
        
        # ===== Entry 样式 =====
        style.configure("TEntry",
                       fieldbackground=self.colors["input_bg"],
                       foreground=self.colors["input_fg"],
                       insertcolor=self.colors["fg"],
                       padding=5)
        
        # ===== Combobox 样式 =====
        style.configure("TCombobox",
                       fieldbackground=self.colors["input_bg"],
                       background=self.colors["card"],
                       foreground=self.colors["input_fg"],
                       arrowcolor=self.colors["fg"])
        style.map("TCombobox",
                 fieldbackground=[("readonly", self.colors["input_bg"])],
                 foreground=[("readonly", self.colors["input_fg"])],
                 background=[("readonly", self.colors["card"])])
        
        # ===== Treeview 样式 =====
        style.configure("Treeview",
                       background=self.colors["card"],
                       foreground=self.colors["fg"],
                       fieldbackground=self.colors["card"],
                       font=("Segoe UI", 10),
                       rowheight=32,
                       borderwidth=0)
        style.configure("Treeview.Heading",
                       background=self.colors["bg_light"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=1,
                       relief="flat")
        style.map("Treeview",
                 background=[("selected", self.colors["select_bg"])],
                 foreground=[("selected", self.colors["select_fg"])])
        style.map("Treeview.Heading",
                 background=[("active", self.colors["accent"])])
        
        # ===== Radiobutton 样式 - 关键修复 =====
        style.configure("TRadiobutton",
                       background=self.colors["bg"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10),
                       indicatorsize=16)
        style.map("TRadiobutton",
                 background=[("active", self.colors["bg_light"]),
                            ("pressed", self.colors["bg"])],
                 foreground=[("active", self.colors["fg"]),
                            ("pressed", self.colors["fg"]),
                            ("selected", self.colors["fg"])])
        
        # ===== Checkbutton 样式 =====
        style.configure("TCheckbutton",
                       background=self.colors["bg"],
                       foreground=self.colors["fg"],
                       font=("Segoe UI", 10),
                       indicatorsize=16)
        style.map("TCheckbutton",
                 background=[("active", self.colors["bg_light"]),
                            ("pressed", self.colors["bg"])],
                 foreground=[("active", self.colors["fg"]),
                            ("pressed", self.colors["fg"])])
        
        # ===== Scrollbar 样式 =====
        style.configure("TScrollbar",
                       background=self.colors["card"],
                       troughcolor=self.colors["bg"],
                       arrowcolor=self.colors["fg"])
        style.map("TScrollbar",
                 background=[("active", self.colors["accent"])])
        
        # ===== Separator 样式 =====
        style.configure("TSeparator",
                       background=self.colors["bg_light"])
    
    def run(self):
        """运行应用"""
        self.root.mainloop()
    
    # ===== 活动检测与自动锁定 =====
    
    def _on_activity(self, event=None):
        """用户活动检测"""
        self.last_activity = time.time()
    
    def _start_auto_lock_check(self):
        """启动自动锁定检测"""
        def check():
            if self.is_unlocked and self.auto_lock_seconds > 0:
                elapsed = time.time() - self.last_activity
                if elapsed > self.auto_lock_seconds:
                    self._auto_lock()
            
            self.auto_lock_timer = threading.Timer(30, check)
            self.auto_lock_timer.daemon = True
            self.auto_lock_timer.start()
        
        check()
    
    def _auto_lock(self):
        """自动锁定（在主线程执行）"""
        self.root.after(0, self._do_auto_lock)
    
    def _do_auto_lock(self):
        """执行自动锁定"""
        if self.is_unlocked:
            self.is_unlocked = False
            self.manager.lock()
            messagebox.showinfo("已锁定", "由于长时间未活动，保险库已自动锁定")
            self._show_lock_screen()
    
    def _manual_lock(self):
        """手动锁定"""
        self.is_unlocked = False
        self.manager.lock()
        self._show_lock_screen()
    
    def _on_close(self):
        """窗口关闭处理"""
        if self.auto_lock_timer:
            self.auto_lock_timer.cancel()
        if self.clipboard_clear_timer:
            self.clipboard_clear_timer.cancel()
        self.root.destroy()
    
    # ===== 剪贴板操作 =====
    
    def _copy_to_clipboard(self, text: str, auto_clear: bool = True):
        """复制到剪贴板
        
        Args:
            text: 要复制的文本
            auto_clear: 是否自动清除
        """
        if not text:
            return
        
        # 复制到剪贴板
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # 确保剪贴板更新
        
        # 设置自动清除
        if auto_clear and self.clipboard_clear_seconds > 0:
            if self.clipboard_clear_timer:
                self.clipboard_clear_timer.cancel()
            
            def clear():
                try:
                    self.root.clipboard_clear()
                    self.root.update()
                except:
                    pass
            
            self.clipboard_clear_timer = threading.Timer(
                self.clipboard_clear_seconds, 
                clear
            )
            self.clipboard_clear_timer.daemon = True
            self.clipboard_clear_timer.start()
    
    # ===== 界面切换 =====
    
    def _clear_window(self):
        """清空窗口"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    # ===== 锁定界面 =====
    
    def _show_lock_screen(self):
        """显示锁定/创建界面"""
        self._clear_window()
        
        # 主框架
        frame = ttk.Frame(self.root, style="TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo和标题
        ttk.Label(frame, text="🔐", font=("Segoe UI", 48)).pack()
        ttk.Label(frame, text=APP_NAME, style="Title.TLabel").pack(pady=(10, 5))
        ttk.Label(frame, text="安全密码管理器", style="Subtitle.TLabel").pack(pady=(0, 30))
        
        if not self.manager.is_initialized():
            # === 创建新保险库 ===
            ttk.Label(frame, text="创建主密码", font=("Segoe UI", 11)).pack(pady=(0, 10))
            
            # 密码输入
            pwd_frame = ttk.Frame(frame, style="TFrame")
            pwd_frame.pack(pady=5)
            
            ttk.Label(pwd_frame, text="主密码:").pack(side="left", padx=(0, 10))
            self.new_pwd_entry = ttk.Entry(pwd_frame, show="●", width=30)
            self.new_pwd_entry.pack(side="left")
            self.new_pwd_entry.focus()
            
            # 确认密码
            confirm_frame = ttk.Frame(frame, style="TFrame")
            confirm_frame.pack(pady=10)
            
            ttk.Label(confirm_frame, text="确认密码:").pack(side="left", padx=(0, 10))
            self.confirm_pwd_entry = ttk.Entry(confirm_frame, show="●", width=30)
            self.confirm_pwd_entry.pack(side="left")
            
            # 密码强度指示
            self.strength_label = ttk.Label(frame, text="", style="Small.TLabel")
            self.strength_label.pack(pady=5)
            self.new_pwd_entry.bind("<KeyRelease>", self._update_strength)
            
            # 创建按钮
            ttk.Button(frame, text="创建保险库", 
                      command=self._create_vault).pack(pady=20)
            
        else:
            # === 解锁 ===
            ttk.Label(frame, text="输入主密码解锁", 
                     font=("Segoe UI", 11)).pack(pady=(0, 15))
            
            pwd_frame = ttk.Frame(frame, style="TFrame")
            pwd_frame.pack(pady=5)
            
            self.unlock_pwd_entry = ttk.Entry(pwd_frame, show="●", width=35)
            self.unlock_pwd_entry.pack(side="left", padx=(0, 10))
            self.unlock_pwd_entry.focus()
            self.unlock_pwd_entry.bind("<Return>", lambda e: self._unlock())
            
            ttk.Button(pwd_frame, text="解锁", 
                      command=self._unlock).pack(side="left")
        
        # 底部信息
        info_frame = ttk.Frame(frame, style="TFrame")
        info_frame.pack(pady=(40, 0))
        
        ttk.Label(info_frame, 
                 text="🔒 AES-256 加密  |  💾 本地存储  |  🚫 无网络连接",
                 style="Small.TLabel").pack()
        ttk.Label(info_frame, 
                 text=f"数据位置: {self.manager.get_data_path()}",
                 style="Small.TLabel").pack(pady=(5, 0))
    
    def _update_strength(self, event=None):
        """更新密码强度显示"""
        password = self.new_pwd_entry.get()
        if password:
            score, level, _ = PasswordGenerator.calculate_strength(password)
            color = {
                "非常弱": self.colors["error"],
                "弱": self.colors["warning"],
                "中等": "#e0c040",  # 金黄色
                "强": self.colors["success"],
                "非常强": self.colors["success"],
            }.get(level, self.colors["fg"])
            
            self.strength_label.configure(
                text=f"密码强度: {level} ({score}分)",
                foreground=color
            )
        else:
            self.strength_label.configure(text="")
    
    def _create_vault(self):
        """创建新保险库"""
        pwd = self.new_pwd_entry.get()
        confirm = self.confirm_pwd_entry.get()
        
        if not pwd:
            messagebox.showerror("错误", "请输入主密码")
            return
        
        if len(pwd) < 8:
            messagebox.showerror("错误", "主密码至少需要8位")
            return
        
        if pwd != confirm:
            messagebox.showerror("错误", "两次输入的密码不一致")
            return
        
        # 检查密码强度
        score, level, feedback = PasswordGenerator.calculate_strength(pwd)
        if score < 50:
            msg = f"密码强度: {level}\n\n建议:\n" + "\n".join(f"• {f}" for f in feedback)
            if not messagebox.askyesno("密码强度警告", msg + "\n\n是否仍要使用此密码?"):
                return
        
        # 创建保险库
        if self.manager.create_vault(pwd):
            self.is_unlocked = True
            messagebox.showinfo("成功", 
                "保险库创建成功!\n\n请牢记主密码，丢失将无法恢复数据。")
            self._show_main_screen()
        else:
            messagebox.showerror("错误", "创建保险库失败")
    
    def _unlock(self):
        """解锁保险库"""
        pwd = self.unlock_pwd_entry.get()
        
        if not pwd:
            messagebox.showerror("错误", "请输入主密码")
            return
        
        if self.manager.unlock(pwd):
            self.is_unlocked = True
            self._show_main_screen()
        else:
            messagebox.showerror("错误", "主密码错误或数据已损坏")
            self.unlock_pwd_entry.delete(0, tk.END)
            self.unlock_pwd_entry.focus()
    
    # ===== 主界面 =====
    
    def _show_main_screen(self):
        """显示主界面"""
        self._clear_window()
        self.last_activity = time.time()
        
        # 主框架
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        # 顶部工具栏
        self._create_toolbar(main_frame)
        
        # 中间区域
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # 左侧导航
        self._create_sidebar(content_frame)
        
        # 右侧内容
        self._create_content_area(content_frame)
        
        # 底部状态栏
        self._create_statusbar(main_frame)
    
    def _create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent, style="TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        
        # 左侧搜索
        search_frame = ttk.Frame(toolbar, style="TFrame")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(search_frame, text="🔍").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=45)
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Escape>", lambda e: self.search_var.set(""))
        
        # 右侧按钮
        btn_frame = ttk.Frame(toolbar, style="TFrame")
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="➕ 添加", 
                  command=self._show_add_dialog).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🔑 生成密码", 
                  command=self._show_generator_dialog).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="📤 导出", 
                  command=self._export_vault).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="📥 导入", 
                  command=self._import_vault).pack(side="left", padx=3)
        ttk.Button(btn_frame, text="🔒 锁定", 
                  command=self._manual_lock).pack(side="left", padx=3)
    
    def _create_sidebar(self, parent):
        """创建侧边栏"""
        sidebar = ttk.Frame(parent, style="TFrame", width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 15))
        sidebar.pack_propagate(False)
        
        # 标题
        ttk.Label(sidebar, text="分类", 
                 font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        # 分类选择
        self.category_var = tk.StringVar(value="all")
        
        # 全部
        ttk.Radiobutton(sidebar, text="📋 全部", 
                       variable=self.category_var, value="all",
                       command=self._refresh_items).pack(anchor="w", pady=3)
        
        # 收藏
        ttk.Radiobutton(sidebar, text="⭐ 收藏", 
                       variable=self.category_var, value="favorites",
                       command=self._refresh_items).pack(anchor="w", pady=3)
        
        # 分隔线
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)
        
        # 各类型
        for type_id, type_info in VaultData.ITEM_TYPES.items():
            icon = type_info["icon"]
            name = type_info["name"]
            ttk.Radiobutton(
                sidebar, 
                text=f"{icon} {name}",
                variable=self.category_var, 
                value=type_id,
                command=self._refresh_items
            ).pack(anchor="w", pady=3)
    
    def _create_content_area(self, parent):
        """创建内容区域"""
        content = ttk.Frame(parent, style="TFrame")
        content.pack(side="left", fill="both", expand=True)
        
        # 列表
        columns = ("title", "type", "updated")
        self.items_tree = ttk.Treeview(content, columns=columns, 
                                       show="headings", height=22)
        
        self.items_tree.heading("title", text="标题")
        self.items_tree.heading("type", text="类型")
        self.items_tree.heading("updated", text="更新时间")
        
        self.items_tree.column("title", width=350, minwidth=200)
        self.items_tree.column("type", width=120, minwidth=100)
        self.items_tree.column("updated", width=150, minwidth=120)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(content, orient="vertical", 
                                 command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 事件绑定
        self.items_tree.bind("<Double-1>", self._view_item)
        self.items_tree.bind("<Button-3>", self._show_context_menu)
        self.items_tree.bind("<Delete>", self._delete_selected)
        
        # 刷新列表
        self._refresh_items()
    
    def _create_statusbar(self, parent):
        """创建状态栏"""
        statusbar = ttk.Frame(parent, style="TFrame")
        statusbar.pack(fill="x", pady=(10, 0))
        
        # 统计
        stats = self.manager.get_stats()
        total = stats.get("total", 0)
        favorites = stats.get("favorites", 0)
        
        ttk.Label(statusbar, 
                 text=f"共 {total} 条记录  |  收藏 {favorites} 条").pack(side="left")
        ttk.Label(statusbar, 
                 text=f"自动锁定: {self.auto_lock_seconds // 60} 分钟").pack(side="right")
    
    def _refresh_items(self):
        """刷新条目列表"""
        # 清空
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # 获取筛选条件
        category = self.category_var.get()
        search = self.search_var.get().strip()
        
        # 获取条目
        if category == "all":
            items = self.manager.get_items(search=search)
        elif category == "favorites":
            items = self.manager.get_items(search=search, favorites_only=True)
        else:
            items = self.manager.get_items(item_type=category, search=search)
        
        # 填充列表
        for item in items:
            type_info = VaultData.ITEM_TYPES.get(item["type"], {})
            icon = type_info.get("icon", "📄")
            type_name = type_info.get("name", item["type"])
            
            title = item["title"]
            if item.get("favorite"):
                title = f"⭐ {title}"
            
            updated = item.get("updated_at", "")
            if updated:
                try:
                    dt = datetime.fromisoformat(updated)
                    updated = dt.strftime("%Y-%m-%d %H:%M")
                except:
                    pass
            
            self.items_tree.insert(
                "", "end", 
                iid=item["id"],
                values=(title, f"{icon} {type_name}", updated)
            )
    
    def _on_search(self, *args):
        """搜索事件"""
        self._refresh_items()
    
    # ===== 条目操作 =====
    
    def _show_add_dialog(self, preset_type: str = "login"):
        """显示添加对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加条目")
        dialog.geometry("520x550")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg=self.colors["bg"])
        
        # 类型选择
        type_frame = ttk.Frame(dialog, style="TFrame")
        type_frame.pack(fill="x", padx=20, pady=15)
        
        ttk.Label(type_frame, text="类型:").pack(side="left")
        type_var = tk.StringVar(value="login")
        
        type_names = [
            f"{v['icon']} {v['name']}" 
            for v in VaultData.ITEM_TYPES.values()
        ]
        type_combo = ttk.Combobox(type_frame, textvariable=type_var,
                                  values=type_names, state="readonly", width=30)
        # 设置默认值
        default_type_info = VaultData.ITEM_TYPES.get("login", {})
        type_combo.set(f"{default_type_info['icon']} {default_type_info['name']}")
        type_combo.pack(side="left", padx=10)
        
        # 标题
        title_frame = ttk.Frame(dialog, style="TFrame")
        title_frame.pack(fill="x", padx=20, pady=5)
        ttk.Label(title_frame, text="标题:").pack(anchor="w")
        title_entry = ttk.Entry(title_frame, width=60)
        title_entry.pack(fill="x", pady=3)
        title_entry.focus()
        
        # 动态字段区
        fields_canvas = tk.Canvas(dialog, bg=self.colors["bg"], 
                                 highlightthickness=0)
        fields_frame = ttk.Frame(fields_canvas, style="TFrame")
        
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", 
                                 command=fields_canvas.yview)
        fields_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side="right", fill="y")
        fields_canvas.pack(side="left", fill="both", expand=True, padx=20)
        
        canvas_window = fields_canvas.create_window((0, 0), window=fields_frame, anchor="nw")
        
        def configure_scroll(event):
            fields_canvas.configure(scrollregion=fields_canvas.bbox("all"))
            fields_canvas.itemconfig(canvas_window, width=event.width)
        
        fields_frame.bind("<Configure>", configure_scroll)
        
        fields_widgets = {}
        
        def update_fields(*args):
            # 清空
            for widget in fields_frame.winfo_children():
                widget.destroy()
            fields_widgets.clear()
            
            # 获取类型
            selected = type_var.get()
            type_id = None
            for tid, tinfo in VaultData.ITEM_TYPES.items():
                if f"{tinfo['icon']} {tinfo['name']}" == selected:
                    type_id = tid
                    break
            
            if not type_id:
                return
            
            type_info = VaultData.ITEM_TYPES[type_id]
            
            # 创建字段
            for field in type_info["fields"]:
                f_frame = ttk.Frame(fields_frame, style="TFrame")
                f_frame.pack(fill="x", pady=5)
                
                ttk.Label(f_frame, text=f"{field['label']}:").pack(anchor="w")
                
                if field["type"] == "textarea":
                    entry = tk.Text(f_frame, height=3, width=60,
                                   bg=self.colors["card"], fg=self.colors["fg"],
                                   font=("Segoe UI", 10))
                    entry.pack(fill="x", pady=2)
                elif field["type"] == "select":
                    entry = ttk.Combobox(f_frame, values=field.get("options", []),
                                        width=57)
                    entry.pack(fill="x", pady=2)
                else:
                    entry_frame = ttk.Frame(f_frame, style="TFrame")
                    entry_frame.pack(fill="x", pady=2)
                    
                    entry = ttk.Entry(entry_frame, width=45)
                    if field["type"] == "password":
                        entry.configure(show="●")
                    entry.pack(side="left", fill="x", expand=True)
                    
                    # 密码生成按钮
                    if field["type"] == "password":
                        def gen_pwd(e=entry):
                            pwd = PasswordGenerator.generate(16, use_symbols=True)
                            e.delete(0, tk.END)
                            e.insert(0, pwd)
                        ttk.Button(entry_frame, text="🎲", width=3,
                                  command=gen_pwd).pack(side="left", padx=2)
                
                fields_widgets[field["key"]] = (entry, field["type"])
        
        type_var.trace_add("write", update_fields)
        update_fields()
        
        # 备注
        notes_frame = ttk.Frame(dialog, style="TFrame")
        notes_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(notes_frame, text="备注:").pack(anchor="w")
        notes_entry = tk.Text(notes_frame, height=2, width=60,
                             bg=self.colors["card"], fg=self.colors["fg"],
                             font=("Segoe UI", 10))
        notes_entry.pack(fill="x", pady=2)
        
        # 按钮
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("错误", "请输入标题")
                return
            
            # 获取类型ID
            selected = type_var.get()
            type_id = None
            for tid, tinfo in VaultData.ITEM_TYPES.items():
                if f"{tinfo['icon']} {tinfo['name']}" == selected:
                    type_id = tid
                    break
            
            # 收集数据
            data = {}
            for key, (widget, wtype) in fields_widgets.items():
                if wtype == "textarea":
                    data[key] = widget.get("1.0", "end-1c")
                elif isinstance(widget, ttk.Combobox):
                    data[key] = widget.get()
                else:
                    data[key] = widget.get()
            
            notes = notes_entry.get("1.0", "end-1c")
            
            # 保存
            self.manager.add_item(type_id, title, data, notes=notes)
            self._refresh_items()
            dialog.destroy()
            messagebox.showinfo("成功", "条目已添加")
        
        ttk.Button(btn_frame, text="✓ 保存", command=save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✕ 取消", 
                  command=dialog.destroy).pack(side="left", padx=5)
    
    def _view_item(self, event=None):
        """查看/编辑条目"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.manager.get_item(item_id)
        if not item:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"查看: {item['title']}")
        dialog.geometry("550x600")
        dialog.transient(self.root)
        dialog.configure(bg=self.colors["bg"])
        
        type_info = VaultData.ITEM_TYPES.get(item["type"], {})
        
        # 标题
        title_frame = ttk.Frame(dialog, style="TFrame")
        title_frame.pack(fill="x", padx=20, pady=15)
        ttk.Label(title_frame, text="标题:").pack(anchor="w")
        title_entry = ttk.Entry(title_frame, width=65)
        title_entry.insert(0, item["title"])
        title_entry.pack(fill="x", pady=3)
        
        # 字段
        fields_frame = ttk.Frame(dialog, style="TFrame")
        fields_frame.pack(fill="both", expand=True, padx=20, pady=5)
        
        fields_widgets = {}
        
        for field in type_info.get("fields", []):
            f_frame = ttk.Frame(fields_frame, style="TFrame")
            f_frame.pack(fill="x", pady=5)
            
            label_frame = ttk.Frame(f_frame, style="TFrame")
            label_frame.pack(fill="x")
            ttk.Label(label_frame, text=f"{field['label']}:").pack(side="left")
            
            value = item.get("data", {}).get(field["key"], "")
            
            if field["type"] == "textarea":
                entry = tk.Text(f_frame, height=3, width=65,
                               bg=self.colors["card"], fg=self.colors["fg"])
                entry.insert("1.0", value)
                entry.pack(fill="x", pady=2)
            elif field["type"] == "select":
                entry = ttk.Combobox(f_frame, values=field.get("options", []),
                                    width=62)
                entry.set(value)
                entry.pack(fill="x", pady=2)
            else:
                entry_frame = ttk.Frame(f_frame, style="TFrame")
                entry_frame.pack(fill="x", pady=2)
                
                entry = ttk.Entry(entry_frame, width=50)
                entry.insert(0, value)
                if field["type"] == "password":
                    entry.configure(show="●")
                entry.pack(side="left", fill="x", expand=True)
                
                # 复制按钮
                def copy_val(e=entry):
                    self._copy_to_clipboard(e.get())
                    messagebox.showinfo("已复制", "已复制到剪贴板")
                
                ttk.Button(entry_frame, text="📋", width=3,
                          command=copy_val).pack(side="left", padx=2)
                
                # 显示/隐藏密码
                if field["type"] == "password":
                    def toggle(e=entry):
                        if e.cget("show"):
                            e.configure(show="")
                        else:
                            e.configure(show="●")
                    ttk.Button(entry_frame, text="👁", width=3,
                              command=toggle).pack(side="left", padx=2)
            
            fields_widgets[field["key"]] = (entry, field["type"])
        
        # 备注
        notes_frame = ttk.Frame(dialog, style="TFrame")
        notes_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(notes_frame, text="备注:").pack(anchor="w")
        notes_entry = tk.Text(notes_frame, height=2, width=65,
                             bg=self.colors["card"], fg=self.colors["fg"])
        notes_entry.insert("1.0", item.get("notes", ""))
        notes_entry.pack(fill="x", pady=2)
        
        # 收藏
        fav_var = tk.BooleanVar(value=item.get("favorite", False))
        ttk.Checkbutton(dialog, text="⭐ 收藏", variable=fav_var).pack(anchor="w", padx=20)
        
        # 时间信息
        time_frame = ttk.Frame(dialog, style="TFrame")
        time_frame.pack(fill="x", padx=20, pady=10)
        
        created = item.get("created_at", "")
        updated = item.get("updated_at", "")
        ttk.Label(time_frame, text=f"创建: {created}", 
                 style="Small.TLabel").pack(side="left")
        ttk.Label(time_frame, text=f"更新: {updated}",
                 style="Small.TLabel").pack(side="left", padx=20)
        
        # 按钮
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("错误", "请输入标题")
                return
            
            data = {}
            for key, (widget, wtype) in fields_widgets.items():
                if wtype == "textarea":
                    data[key] = widget.get("1.0", "end-1c")
                elif isinstance(widget, ttk.Combobox):
                    data[key] = widget.get()
                else:
                    data[key] = widget.get()
            
            notes = notes_entry.get("1.0", "end-1c")
            
            self.manager.update_item(
                item_id, title=title, data=data,
                notes=notes, favorite=fav_var.get()
            )
            self._refresh_items()
            dialog.destroy()
            messagebox.showinfo("成功", "条目已更新")
        
        def delete():
            if messagebox.askyesno("确认删除", "确定要删除此条目吗？\n此操作不可撤销。"):
                self.manager.delete_item(item_id)
                self._refresh_items()
                dialog.destroy()
                messagebox.showinfo("成功", "条目已删除")
        
        ttk.Button(btn_frame, text="✓ 保存", command=save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🗑 删除", command=delete).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✕ 取消",
                  command=dialog.destroy).pack(side="left", padx=5)
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        # 选中项目
        item = self.items_tree.identify_row(event.y)
        if item:
            self.items_tree.selection_set(item)
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="👁 查看/编辑", command=self._view_item)
        menu.add_command(label="📋 复制标题", 
                        command=lambda: self._copy_item_field("title"))
        menu.add_separator()
        menu.add_command(label="🗑 删除", command=self._delete_selected)
        
        menu.post(event.x_root, event.y_root)
    
    def _copy_item_field(self, field: str):
        """复制条目字段"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        item = self.manager.get_item(selection[0])
        if not item:
            return
        
        if field == "title":
            self._copy_to_clipboard(item["title"])
        elif field == "data":
            # 复制所有数据
            data_str = "\n".join(
                f"{k}: {v}" for k, v in item.get("data", {}).items()
            )
            self._copy_to_clipboard(data_str)
    
    def _delete_selected(self, event=None):
        """删除选中条目"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        if len(selection) == 1:
            msg = "确定要删除此条目吗？\n此操作不可撤销。"
        else:
            msg = f"确定要删除 {len(selection)} 个条目吗？\n此操作不可撤销。"
        
        if messagebox.askyesno("确认删除", msg):
            for item_id in selection:
                self.manager.delete_item(item_id)
            self._refresh_items()
    
    # ===== 密码生成器 =====
    
    def _show_generator_dialog(self):
        """显示密码生成器"""
        dialog = tk.Toplevel(self.root)
        dialog.title("密码生成器")
        dialog.geometry("450x400")
        dialog.transient(self.root)
        dialog.resizable(False, False)
        dialog.configure(bg=self.colors["bg"])
        
        # 长度
        len_frame = ttk.Frame(dialog, style="TFrame")
        len_frame.pack(fill="x", padx=20, pady=15)
        
        ttk.Label(len_frame, text="密码长度:").pack(side="left")
        length_var = tk.IntVar(value=16)
        length_scale = ttk.Scale(len_frame, from_=8, to=64, 
                                variable=length_var, length=200)
        length_scale.pack(side="left", padx=10)
        length_label = ttk.Label(len_frame, text="16")
        length_label.pack(side="left")
        
        def update_length(*args):
            length_label.configure(text=str(int(length_var.get())))
        length_var.trace_add("write", update_length)
        
        # 选项
        opts_frame = ttk.Frame(dialog, style="TFrame")
        opts_frame.pack(fill="x", padx=20, pady=10)
        
        upper_var = tk.BooleanVar(value=True)
        lower_var = tk.BooleanVar(value=True)
        digits_var = tk.BooleanVar(value=True)
        symbols_var = tk.BooleanVar(value=False)
        no_ambiguous_var = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(opts_frame, text="大写字母 (A-Z)",
                       variable=upper_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(opts_frame, text="小写字母 (a-z)",
                       variable=lower_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(opts_frame, text="数字 (0-9)",
                       variable=digits_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(opts_frame, text="特殊字符 (!@#$...)",
                       variable=symbols_var).pack(anchor="w", pady=2)
        ttk.Checkbutton(opts_frame, text="排除易混淆字符 (il1Lo0O)",
                       variable=no_ambiguous_var).pack(anchor="w", pady=2)
        
        # 生成的密码
        pwd_frame = ttk.Frame(dialog, style="TFrame")
        pwd_frame.pack(fill="x", padx=20, pady=15)
        
        ttk.Label(pwd_frame, text="生成的密码:").pack(anchor="w")
        
        pwd_entry_frame = ttk.Frame(pwd_frame, style="TFrame")
        pwd_entry_frame.pack(fill="x", pady=5)
        
        pwd_entry = ttk.Entry(pwd_entry_frame, width=50, font=("Consolas", 11))
        pwd_entry.pack(side="left", fill="x", expand=True)
        
        # 强度指示
        strength_label = ttk.Label(pwd_frame, text="", style="Small.TLabel")
        strength_label.pack(anchor="w")
        
        def generate():
            pwd = PasswordGenerator.generate(
                length=int(length_var.get()),
                use_upper=upper_var.get(),
                use_lower=lower_var.get(),
                use_digits=digits_var.get(),
                use_symbols=symbols_var.get(),
                exclude_ambiguous=no_ambiguous_var.get()
            )
            pwd_entry.delete(0, tk.END)
            pwd_entry.insert(0, pwd)
            
            score, level, _ = PasswordGenerator.calculate_strength(pwd)
            color = {
                "非常弱": self.colors["error"],
                "弱": self.colors["warning"],
                "中等": "#e0c040",  # 金黄色
                "强": self.colors["success"],
                "非常强": self.colors["success"],
            }.get(level, self.colors["fg"])
            strength_label.configure(
                text=f"强度: {level} ({score}分)",
                foreground=color
            )
        
        def copy():
            pwd = pwd_entry.get()
            if pwd:
                self._copy_to_clipboard(pwd)
                messagebox.showinfo("已复制", "密码已复制到剪贴板")
        
        # 按钮
        btn_frame = ttk.Frame(dialog, style="TFrame")
        btn_frame.pack(fill="x", padx=20, pady=15)
        
        ttk.Button(btn_frame, text="🎲 生成", command=generate).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📋 复制", command=copy).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="✕ 关闭",
                  command=dialog.destroy).pack(side="left", padx=5)
        
        # 初始生成
        generate()
    
    # ===== 导入导出 =====
    
    def _export_vault(self):
        """导出保险库"""
        filepath = filedialog.asksaveasfilename(
            title="导出保险库备份",
            defaultextension=".vaultx",
            filetypes=[("VaultX备份", "*.vaultx"), ("所有文件", "*.*")],
            initialfile=f"vaultx_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.vaultx"
        )
        
        if filepath:
            if self.manager.export_vault(filepath):
                messagebox.showinfo("成功", f"备份已保存到:\n{filepath}")
            else:
                messagebox.showerror("错误", "导出失败")
    
    def _import_vault(self):
        """导入保险库"""
        filepath = filedialog.askopenfilename(
            title="导入保险库备份",
            filetypes=[("VaultX备份", "*.vaultx"), ("所有文件", "*.*")]
        )
        
        if not filepath:
            return
        
        # 询问合并方式
        result = messagebox.askyesnocancel(
            "导入方式",
            "是否合并现有数据？\n\n"
            "是 = 合并（保留现有数据）\n"
            "否 = 替换（清空现有数据）\n"
            "取消 = 放弃导入"
        )
        
        if result is None:
            return
        
        merge = result
        
        if self.manager.import_vault(filepath, merge=merge):
            self._refresh_items()
            messagebox.showinfo("成功", "导入成功")
        else:
            messagebox.showerror("错误", 
                "导入失败\n可能原因：密码错误或文件损坏")
