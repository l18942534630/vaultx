# -*- coding: utf-8 -*-
"""
VaultX - 本地密码管理器
安全、本地、无需联网的密码管理解决方案
"""
import os
import sys
import json
import base64
import hashlib
import secrets
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any

# 加密库
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# GUI
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
from tkinter import font as tkfont

# 剪贴板
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False

# ============================================================
# 配置
# ============================================================
APP_NAME = "VaultX"
APP_VERSION = "1.0.0"
APP_AUTHOR = "VaultX Team"

# 数据存储路径
DATA_DIR = Path.home() / ".vaultx"
DATA_FILE = DATA_DIR / "vault.enc"
CONFIG_FILE = DATA_DIR / "config.json"

# 自动锁定时间（秒）
DEFAULT_AUTO_LOCK = 300  # 5分钟

# ============================================================
# 加密引擎
# ============================================================
class CryptoEngine:
    """加密引擎 - 使用 AES-256 (Fernet)"""
    
    ITERATIONS = 600000  # PBKDF2 迭代次数
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """从主密码派生加密密钥"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=CryptoEngine.ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode('utf-8')))
        return key
    
    @staticmethod
    def encrypt(data: Any, password: str) -> bytes:
        """加密数据"""
        salt = secrets.token_bytes(16)
        key = CryptoEngine.derive_key(password, salt)
        f = Fernet(key)
        
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        encrypted = f.encrypt(json_data.encode('utf-8'))
        
        # 格式: salt(16) + encrypted_data
        return base64.b64encode(salt + encrypted)
    
    @staticmethod
    def decrypt(encrypted_data: bytes, password: str) -> Optional[Any]:
        """解密数据"""
        try:
            raw = base64.b64decode(encrypted_data)
            salt = raw[:16]
            encrypted = raw[16:]
            
            key = CryptoEngine.derive_key(password, salt)
            f = Fernet(key)
            
            decrypted = f.decrypt(encrypted)
            return json.loads(decrypted.decode('utf-8'))
        except Exception:
            return None

# ============================================================
# 密码生成器
# ============================================================
class PasswordGenerator:
    """密码生成器"""
    
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGITS = "0123456789"
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    AMBIGUOUS = "il1Lo0O"
    
    @staticmethod
    def generate(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = False,
        exclude_ambiguous: bool = True
    ) -> str:
        """生成随机密码"""
        chars = ""
        
        lower = PasswordGenerator.LOWERCASE
        upper = PasswordGenerator.UPPERCASE
        digits = PasswordGenerator.DIGITS
        symbols = PasswordGenerator.SYMBOLS
        
        if exclude_ambiguous:
            lower = ''.join(c for c in lower if c not in PasswordGenerator.AMBIGUOUS)
            upper = ''.join(c for c in upper if c not in PasswordGenerator.AMBIGUOUS)
            digits = ''.join(c for c in digits if c not in PasswordGenerator.AMBIGUOUS)
        
        if use_lower:
            chars += lower
        if use_upper:
            chars += upper
        if use_digits:
            chars += digits
        if use_symbols:
            chars += symbols
        
        if not chars:
            chars = lower or PasswordGenerator.LOWERCASE
        
        # 确保至少包含每种选中的字符类型
        password = []
        if use_lower and lower:
            password.append(secrets.choice(lower))
        if use_upper and upper:
            password.append(secrets.choice(upper))
        if use_digits and digits:
            password.append(secrets.choice(digits))
        if use_symbols:
            password.append(secrets.choice(symbols))
        
        # 填充剩余长度
        while len(password) < length:
            password.append(secrets.choice(chars))
        
        # 随机打乱
        secrets.SystemRandom().shuffle(password)
        return ''.join(password)
    
    @staticmethod
    def calculate_strength(password: str) -> tuple:
        """计算密码强度，返回 (分数, 等级)"""
        score = 0
        feedback = []
        
        # 长度评分
        if len(password) >= 8:
            score += 15
        if len(password) >= 12:
            score += 15
        if len(password) >= 16:
            score += 10
        if len(password) >= 20:
            score += 10
        
        # 字符类型评分
        if any(c.islower() for c in password):
            score += 10
        else:
            feedback.append("建议添加小写字母")
            
        if any(c.isupper() for c in password):
            score += 10
        else:
            feedback.append("建议添加大写字母")
            
        if any(c.isdigit() for c in password):
            score += 10
        else:
            feedback.append("建议添加数字")
            
        if any(c in PasswordGenerator.SYMBOLS for c in password):
            score += 20
        else:
            feedback.append("建议添加特殊字符")
        
        # 确定等级
        if score < 30:
            level = "非常弱"
        elif score < 50:
            level = "弱"
        elif score < 70:
            level = "中等"
        elif score < 90:
            level = "强"
        else:
            level = "非常强"
        
        return min(score, 100), level, feedback

# ============================================================
# 数据模型
# ============================================================
class VaultData:
    """保险库数据模型"""
    
    # 条目类型定义
    ITEM_TYPES = {
        "login": {
            "name": "登录密码",
            "icon": "🔐",
            "fields": [
                {"key": "username", "label": "用户名", "type": "text"},
                {"key": "password", "label": "密码", "type": "password"},
                {"key": "url", "label": "网址", "type": "url"},
                {"key": "email", "label": "邮箱", "type": "email"},
            ]
        },
        "bank": {
            "name": "银行卡",
            "icon": "💳",
            "fields": [
                {"key": "bank_name", "label": "银行名称", "type": "text"},
                {"key": "card_number", "label": "卡号", "type": "text"},
                {"key": "holder_name", "label": "持卡人", "type": "text"},
                {"key": "expiry", "label": "有效期", "type": "text"},
                {"key": "cvv", "label": "CVV", "type": "password"},
                {"key": "pin", "label": "PIN码", "type": "password"},
            ]
        },
        "api": {
            "name": "API密钥",
            "icon": "🔑",
            "fields": [
                {"key": "api_key", "label": "API Key", "type": "text"},
                {"key": "secret", "label": "Secret", "type": "password"},
                {"key": "endpoint", "label": "端点", "type": "url"},
                {"key": "description", "label": "说明", "type": "textarea"},
            ]
        },
        "personal": {
            "name": "个人信息",
            "icon": "👤",
            "fields": [
                {"key": "full_name", "label": "姓名", "type": "text"},
                {"key": "id_number", "label": "证件号码", "type": "text"},
                {"key": "id_type", "label": "证件类型", "type": "select", "options": ["身份证", "护照", "驾照", "其他"]},
                {"key": "issue_date", "label": "发证日期", "type": "text"},
                {"key": "expiry_date", "label": "有效期", "type": "text"},
            ]
        },
        "note": {
            "name": "安全笔记",
            "icon": "📝",
            "fields": [
                {"key": "content", "label": "内容", "type": "textarea"},
            ]
        },
        "wifi": {
            "name": "WiFi密码",
            "icon": "📶",
            "fields": [
                {"key": "ssid", "label": "网络名称", "type": "text"},
                {"key": "password", "label": "密码", "type": "password"},
                {"key": "security", "label": "加密类型", "type": "select", "options": ["WPA2", "WPA3", "WEP", "无"]},
            ]
        },
        "credit": {
            "name": "信用卡",
            "icon": "💳",
            "fields": [
                {"key": "card_name", "label": "卡片名称", "type": "text"},
                {"key": "card_number", "label": "卡号", "type": "text"},
                {"key": "holder_name", "label": "持卡人", "type": "text"},
                {"key": "expiry", "label": "有效期", "type": "text"},
                {"key": "cvv", "label": "CVV", "type": "password"},
                {"key": "credit_limit", "label": "额度", "type": "text"},
            ]
        },
        "software": {
            "name": "软件许可",
            "icon": "💿",
            "fields": [
                {"key": "software_name", "label": "软件名称", "type": "text"},
                {"key": "license_key", "label": "许可证", "type": "text"},
                {"key": "email", "label": "注册邮箱", "type": "email"},
                {"key": "expiry", "label": "到期日期", "type": "text"},
            ]
        },
    }
    
    def __init__(self):
        self.items: List[Dict] = []
        self.folders: List[Dict] = []
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "items": self.items,
            "folders": self.folders,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VaultData':
        vault = cls()
        vault.items = data.get("items", [])
        vault.folders = data.get("folders", [])
        vault.created_at = data.get("created_at")
        vault.updated_at = data.get("updated_at")
        return vault

# ============================================================
# 保险库管理器
# ============================================================
class VaultManager:
    """保险库管理器"""
    
    def __init__(self):
        self.vault: Optional[VaultData] = None
        self.master_password: Optional[str] = None
        self._ensure_data_dir()
    
    def _ensure_data_dir(self):
        """确保数据目录存在"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    def is_initialized(self) -> bool:
        """检查是否已初始化"""
        return DATA_FILE.exists()
    
    def create_vault(self, password: str) -> bool:
        """创建新保险库"""
        try:
            self.master_password = password
            self.vault = VaultData()
            self.vault.created_at = datetime.now().isoformat()
            self.vault.updated_at = datetime.now().isoformat()
            self._save()
            return True
        except Exception as e:
            print(f"创建保险库失败: {e}")
            return False
    
    def unlock(self, password: str) -> bool:
        """解锁保险库"""
        try:
            encrypted = DATA_FILE.read_bytes()
            data = CryptoEngine.decrypt(encrypted, password)
            if data is None:
                return False
            self.vault = VaultData.from_dict(data)
            self.master_password = password
            return True
        except Exception as e:
            print(f"解锁失败: {e}")
            return False
    
    def lock(self):
        """锁定保险库"""
        self.vault = None
        self.master_password = None
    
    def _save(self):
        """保存数据"""
        if self.vault:
            self.vault.updated_at = datetime.now().isoformat()
            encrypted = CryptoEngine.encrypt(self.vault.to_dict(), self.master_password)
            DATA_FILE.write_bytes(encrypted)
    
    # ===== 条目操作 =====
    
    def add_item(self, item_type: str, title: str, data: Dict, 
                 folder: str = None, tags: List[str] = None, 
                 notes: str = "", favorite: bool = False) -> Dict:
        """添加条目"""
        item = {
            "id": secrets.token_hex(16),
            "type": item_type,
            "title": title,
            "data": data,
            "folder": folder,
            "tags": tags or [],
            "notes": notes,
            "favorite": favorite,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        }
        self.vault.items.append(item)
        self._save()
        return item
    
    def update_item(self, item_id: str, **kwargs) -> bool:
        """更新条目"""
        for item in self.vault.items:
            if item["id"] == item_id:
                for key, value in kwargs.items():
                    if key in ["title", "data", "folder", "tags", "notes", "favorite"]:
                        item[key] = value
                item["updated_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def delete_item(self, item_id: str) -> bool:
        """删除条目"""
        for i, item in enumerate(self.vault.items):
            if item["id"] == item_id:
                del self.vault.items[i]
                self._save()
                return True
        return False
    
    def get_items(self, item_type: str = None, search: str = None, 
                  favorites_only: bool = False) -> List[Dict]:
        """获取条目列表"""
        items = self.vault.items
        
        if item_type:
            items = [i for i in items if i["type"] == item_type]
        
        if favorites_only:
            items = [i for i in items if i.get("favorite", False)]
        
        if search:
            search_lower = search.lower()
            items = [i for i in items if 
                     search_lower in i["title"].lower() or
                     search_lower in i.get("notes", "").lower() or
                     any(search_lower in str(v).lower() for v in i.get("data", {}).values())]
        
        # 排序：收藏在前，然后按更新时间
        items.sort(key=lambda x: (not x.get("favorite", False), x.get("updated_at", "")), reverse=True)
        
        return items
    
    def get_item(self, item_id: str) -> Optional[Dict]:
        """获取单个条目"""
        for item in self.vault.items:
            if item["id"] == item_id:
                return item
        return None
    
    # ===== 导入导出 =====
    
    def export_vault(self, filepath: str) -> bool:
        """导出加密备份"""
        try:
            encrypted = CryptoEngine.encrypt(self.vault.to_dict(), self.master_password)
            Path(filepath).write_bytes(encrypted)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_vault(self, filepath: str, merge: bool = False) -> bool:
        """导入备份"""
        try:
            encrypted = Path(filepath).read_bytes()
            data = CryptoEngine.decrypt(encrypted, self.master_password)
            if data is None:
                return False
            
            imported = VaultData.from_dict(data)
            
            if merge:
                # 合并条目
                existing_ids = {i["id"] for i in self.vault.items}
                for item in imported.items:
                    if item["id"] not in existing_ids:
                        self.vault.items.append(item)
            else:
                self.vault = imported
            
            self._save()
            return True
        except Exception as e:
            print(f"导入失败: {e}")
            return False

# ============================================================
# GUI 应用
# ============================================================
class VaultXApp:
    """VaultX 主应用"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)
        
        # 设置窗口图标（如果存在）
        icon_path = Path(__file__).parent / "icon.ico"
        if icon_path.exists():
            self.root.iconbitmap(str(icon_path))
        
        # 管理器
        self.manager = VaultManager()
        self.is_unlocked = False
        
        # 自动锁定
        self.auto_lock_seconds = DEFAULT_AUTO_LOCK
        self.last_activity = time.time()
        self.auto_lock_timer = None
        
        # 样式
        self._setup_styles()
        
        # 初始界面
        self._show_lock_screen()
        
        # 启动自动锁定检测
        self._start_auto_lock_check()
        
        # 绑定活动检测
        self.root.bind_all("<Any-KeyPress>", self._on_activity)
        self.root.bind_all("<Any-Button>", self._on_activity)
    
    def _setup_styles(self):
        """设置样式"""
        style = ttk.Style()
        
        # 主题色
        style.theme_use('clam')
        
        # 配置颜色
        bg_color = "#1a1a2e"
        fg_color = "#eaeaea"
        accent_color = "#4a90d9"
        card_bg = "#16213e"
        
        # 窗口背景
        self.root.configure(bg=bg_color)
        
        # 样式配置
        style.configure("TFrame", background=bg_color)
        style.configure("TLabel", background=bg_color, foreground=fg_color, font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10), padding=8)
        style.configure("Treeview", 
                       background=card_bg, 
                       foreground=fg_color,
                       fieldbackground=card_bg,
                       font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                       background=accent_color,
                       foreground="white",
                       font=("Segoe UI", 10, "bold"))
        
        # 特殊样式
        style.configure("Title.TLabel", font=("Segoe UI", 18, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 12))
        style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
        
        # Entry 样式
        style.configure("TEntry", fieldbackground=card_bg, foreground=fg_color)
    
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
        """自动锁定"""
        self.root.after(0, self._do_auto_lock)
    
    def _do_auto_lock(self):
        """执行自动锁定"""
        if self.is_unlocked:
            self.is_unlocked = False
            self.manager.lock()
            messagebox.showinfo("已锁定", "由于长时间未活动，保险库已自动锁定")
            self._show_lock_screen()
    
    # ===== 锁定界面 =====
    
    def _show_lock_screen(self):
        """显示锁定界面"""
        self._clear_window()
        
        frame = ttk.Frame(self.root, style="TFrame")
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # 标题
        ttk.Label(frame, text="🔐 VaultX", style="Title.TLabel").pack(pady=(0, 10))
        ttk.Label(frame, text="安全密码管理器", style="Subtitle.TLabel").pack(pady=(0, 30))
        
        if not self.manager.is_initialized():
            # 创建新保险库
            ttk.Label(frame, text="设置主密码").pack(pady=(0, 10))
            
            pwd_frame = ttk.Frame(frame)
            pwd_frame.pack(pady=5)
            
            ttk.Label(pwd_frame, text="主密码:").pack(side="left", padx=5)
            self.new_pwd_entry = ttk.Entry(pwd_frame, show="●", width=25)
            self.new_pwd_entry.pack(side="left", padx=5)
            
            ttk.Label(frame, text="确认密码:").pack(pady=(10, 0))
            confirm_frame = ttk.Frame(frame)
            confirm_frame.pack(pady=5)
            
            self.confirm_pwd_entry = ttk.Entry(confirm_frame, show="●", width=25)
            self.confirm_pwd_entry.pack()
            
            ttk.Button(frame, text="创建保险库", command=self._create_vault).pack(pady=20)
        else:
            # 解锁
            ttk.Label(frame, text="输入主密码解锁").pack(pady=(0, 10))
            
            pwd_frame = ttk.Frame(frame)
            pwd_frame.pack(pady=5)
            
            self.unlock_pwd_entry = ttk.Entry(pwd_frame, show="●", width=30)
            self.unlock_pwd_entry.pack(side="left", padx=5)
            self.unlock_pwd_entry.bind("<Return>", lambda e: self._unlock())
            
            ttk.Button(pwd_frame, text="解锁", command=self._unlock).pack(side="left", padx=5)
        
        # 版本信息
        ttk.Label(frame, text=f"v{APP_VERSION} | 本地存储 | AES-256加密").pack(pady=(50, 0))
    
    def _create_vault(self):
        """创建新保险库"""
        pwd = self.new_pwd_entry.get()
        confirm = self.confirm_pwd_entry.get()
        
        if not pwd:
            messagebox.showerror("错误", "请输入主密码")
            return
        
        if len(pwd) < 8:
            messagebox.showerror("错误", "主密码至少8位")
            return
        
        if pwd != confirm:
            messagebox.showerror("错误", "两次密码不一致")
            return
        
        # 检查密码强度
        score, level, _ = PasswordGenerator.calculate_strength(pwd)
        if score < 50:
            if not messagebox.askyesno("警告", f"密码强度: {level}\n建议使用更强的密码\n是否继续?"):
                return
        
        if self.manager.create_vault(pwd):
            self.is_unlocked = True
            self._show_main_screen()
        else:
            messagebox.showerror("错误", "创建失败")
    
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
            messagebox.showerror("错误", "密码错误或数据损坏")
            self.unlock_pwd_entry.delete(0, tk.END)
    
    # ===== 主界面 =====
    
    def _show_main_screen(self):
        """显示主界面"""
        self._clear_window()
        self.last_activity = time.time()
        
        # 主框架
        main_frame = ttk.Frame(self.root, style="TFrame")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 顶部工具栏
        self._create_toolbar(main_frame)
        
        # 中间区域（左导航 + 右内容）
        content_frame = ttk.Frame(main_frame, style="TFrame")
        content_frame.pack(fill="both", expand=True, pady=10)
        
        # 左侧导航
        self._create_sidebar(content_frame)
        
        # 右侧内容
        self._create_content_area(content_frame)
        
        # 状态栏
        self._create_statusbar(main_frame)
    
    def _create_toolbar(self, parent):
        """创建工具栏"""
        toolbar = ttk.Frame(parent, style="TFrame")
        toolbar.pack(fill="x", pady=(0, 10))
        
        # 左侧：搜索
        search_frame = ttk.Frame(toolbar, style="TFrame")
        search_frame.pack(side="left", fill="x", expand=True)
        
        ttk.Label(search_frame, text="🔍").pack(side="left", padx=(0, 5))
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self._on_search)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
        search_entry.pack(side="left", padx=5)
        
        # 右侧：操作按钮
        btn_frame = ttk.Frame(toolbar, style="TFrame")
        btn_frame.pack(side="right")
        
        ttk.Button(btn_frame, text="➕ 添加", command=self._show_add_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔄 生成密码", command=self._show_generator_dialog).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📤 导出", command=self._export_vault).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📥 导入", command=self._import_vault).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🔒 锁定", command=self._manual_lock).pack(side="left", padx=5)
    
    def _create_sidebar(self, parent):
        """创建侧边栏"""
        sidebar = ttk.Frame(parent, style="TFrame", width=180)
        sidebar.pack(side="left", fill="y", padx=(0, 10))
        sidebar.pack_propagate(False)
        
        # 分类列表
        ttk.Label(sidebar, text="分类", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 10))
        
        self.category_var = tk.StringVar(value="all")
        
        # 全部
        ttk.Radiobutton(sidebar, text="📋 全部", variable=self.category_var, 
                       value="all", command=self._refresh_items).pack(anchor="w", pady=2)
        
        # 收藏
        ttk.Radiobutton(sidebar, text="⭐ 收藏", variable=self.category_var,
                       value="favorites", command=self._refresh_items).pack(anchor="w", pady=2)
        
        ttk.Separator(sidebar, orient="horizontal").pack(fill="x", pady=10)
        
        # 各类型
        for type_id, type_info in VaultData.ITEM_TYPES.items():
            icon = type_info["icon"]
            name = type_info["name"]
            ttk.Radiobutton(sidebar, text=f"{icon} {name}", variable=self.category_var,
                           value=type_id, command=self._refresh_items).pack(anchor="w", pady=2)
    
    def _create_content_area(self, parent):
        """创建内容区域"""
        content = ttk.Frame(parent, style="TFrame")
        content.pack(side="left", fill="both", expand=True)
        
        # 条目列表
        columns = ("title", "type", "updated")
        self.items_tree = ttk.Treeview(content, columns=columns, show="headings", height=20)
        
        self.items_tree.heading("title", text="标题")
        self.items_tree.heading("type", text="类型")
        self.items_tree.heading("updated", text="更新时间")
        
        self.items_tree.column("title", width=300)
        self.items_tree.column("type", width=100)
        self.items_tree.column("updated", width=150)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(content, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 双击查看
        self.items_tree.bind("<Double-1>", self._view_item)
        
        # 右键菜单
        self.items_tree.bind("<Button-3>", self._show_context_menu)
        
        # 刷新列表
        self._refresh_items()
    
    def _create_statusbar(self, parent):
        """创建状态栏"""
        statusbar = ttk.Frame(parent, style="TFrame")
        statusbar.pack(fill="x", pady=(10, 0))
        
        count = len(self.manager.vault.items)
        ttk.Label(statusbar, text=f"共 {count} 条记录").pack(side="left")
        ttk.Label(statusbar, text=f"自动锁定: {self.auto_lock_seconds // 60} 分钟").pack(side="right")
    
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
            
            self.items_tree.insert("", "end", iid=item["id"], values=(title, f"{icon} {type_name}", updated))
    
    def _on_search(self, *args):
        """搜索"""
        self._refresh_items()
    
    def _show_add_dialog(self, preset_type: str = "login"):
        """显示添加对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加条目")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 类型选择
        type_frame = ttk.Frame(dialog)
        type_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(type_frame, text="类型:").pack(side="left")
        type_var = tk.StringVar(value=preset_type)
        type_combo = ttk.Combobox(type_frame, textvariable=type_var, 
                                  values=[f"{v['icon']} {v['name']}" for v in VaultData.ITEM_TYPES.values()],
                                  state="readonly", width=25)
        type_combo.pack(side="left", padx=10)
        
        # 标题
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(title_frame, text="标题:").pack(anchor="w")
        title_entry = ttk.Entry(title_frame, width=50)
        title_entry.pack(fill="x", pady=5)
        
        # 动态字段区域
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields_widgets = {}
        
        def update_fields(*args):
            # 清空现有字段
            for widget in fields_frame.winfo_children():
                widget.destroy()
            fields_widgets.clear()
            
            # 获取选中的类型
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
                f_frame = ttk.Frame(fields_frame)
                f_frame.pack(fill="x", pady=5)
                
                ttk.Label(f_frame, text=f"{field['label']}:").pack(anchor="w")
                
                if field["type"] == "textarea":
                    entry = tk.Text(f_frame, height=4, width=50)
                    entry.pack(fill="x", pady=2)
                elif field["type"] == "select":
                    entry = ttk.Combobox(f_frame, values=field.get("options", []), width=47)
                    entry.pack(fill="x", pady=2)
                else:
                    entry = ttk.Entry(f_frame, width=50)
                    if field["type"] == "password":
                        entry.configure(show="●")
                    entry.pack(fill="x", pady=2)
                
                fields_widgets[field["key"]] = (entry, field["type"])
        
        type_var.trace_add("write", update_fields)
        update_fields()
        
        # 备注
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(notes_frame, text="备注:").pack(anchor="w")
        notes_entry = tk.Text(notes_frame, height=3, width=50)
        notes_entry.pack(fill="x", pady=2)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
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
            
            # 收集字段数据
            data = {}
            for key, (widget, wtype) in fields_widgets.items():
                if wtype == "textarea":
                    data[key] = widget.get("1.0", "end-1c")
                else:
                    data[key] = widget.get()
            
            notes = notes_entry.get("1.0", "end-1c")
            
            # 保存
            self.manager.add_item(type_id, title, data, notes=notes)
            self._refresh_items()
            dialog.destroy()
            messagebox.showinfo("成功", "条目已添加")
        
        ttk.Button(btn_frame, text="保存", command=save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
    
    def _view_item(self, event=None):
        """查看条目详情"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        item_id = selection[0]
        item = self.manager.get_item(item_id)
        if not item:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"查看: {item['title']}")
        dialog.geometry("500x600")
        dialog.transient(self.root)
        
        # 类型信息
        type_info = VaultData.ITEM_TYPES.get(item["type"], {})
        
        # 标题
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(title_frame, text="标题:").pack(anchor="w")
        title_entry = ttk.Entry(title_frame, width=50)
        title_entry.insert(0, item["title"])
        title_entry.pack(fill="x", pady=2)
        
        # 字段
        fields_frame = ttk.Frame(dialog)
        fields_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        fields_widgets = {}
        
        for field in type_info.get("fields", []):
            f_frame = ttk.Frame(fields_frame)
            f_frame.pack(fill="x", pady=5)
            
            label_frame = ttk.Frame(f_frame)
            label_frame.pack(fill="x")
            ttk.Label(label_frame, text=f"{field['label']}:").pack(side="left")
            
            # 复制按钮
            def copy_value(w):
                value = w.get() if isinstance(w, ttk.Entry) else w.get("1.0", "end-1c")
                self._copy_to_clipboard(value)
            
            value = item.get("data", {}).get(field["key"], "")
            
            if field["type"] == "textarea":
                entry = tk.Text(f_frame, height=4, width=50)
                entry.insert("1.0", value)
                entry.pack(fill="x", pady=2)
            elif field["type"] == "select":
                entry = ttk.Combobox(f_frame, values=field.get("options", []), width=47)
                entry.set(value)
                entry.pack(fill="x", pady=2)
            else:
                entry_frame = ttk.Frame(f_frame)
                entry_frame.pack(fill="x", pady=2)
                
                entry = ttk.Entry(entry_frame, width=40)
                entry.insert(0, value)
                if field["type"] == "password":
                    entry.configure(show="●")
                entry.pack(side="left", fill="x", expand=True)
                
                # 复制按钮
                ttk.Button(entry_frame, text="📋", width=3,
                          command=lambda e=entry: copy_value(e)).pack(side="left", padx=2)
                
                # 显示/隐藏按钮
                if field["type"] == "password":
                    def toggle(e=entry):
                        if e.cget("show"):
                            e.configure(show="")
                        else:
                            e.configure(show="●")
                    ttk.Button(entry_frame, text="👁", width=3, command=toggle).pack(side="left", padx=2)
            
            fields_widgets[field["key"]] = (entry, field["type"])
        
        # 备注
        notes_frame = ttk.Frame(dialog)
        notes_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(notes_frame, text="备注:").pack(anchor="w")
        notes_entry = tk.Text(notes_frame, height=3, width=50)
        notes_entry.insert("1.0", item.get("notes", ""))
        notes_entry.pack(fill="x", pady=2)
        
        # 标签
        tags_frame = ttk.Frame(dialog)
        tags_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(tags_frame, text="标签 (逗号分隔):").pack(anchor="w")
        tags_entry = ttk.Entry(tags_frame, width=50)
        tags_entry.insert(0, ", ".join(item.get("tags", [])))
        tags_entry.pack(fill="x", pady=2)
        
        # 收藏
        fav_var = tk.BooleanVar(value=item.get("favorite", False))
        ttk.Checkbutton(dialog, text="收藏", variable=fav_var).pack(anchor="w", padx=20)
        
        # 按钮
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(fill="x", padx=20, pady=20)
        
        def save():
            title = title_entry.get().strip()
            if not title:
                messagebox.showerror("错误", "请输入标题")
                return
            
            # 收集字段数据
            data = {}
            for key, (widget, wtype) in fields_widgets.items():
                if wtype == "textarea":
                    data[key] = widget.get("1.0", "end-1c")
                else:
                    data[key] = widget.get()
            
            notes = notes_entry.get("1.0", "end-1c")
            tags = [t.strip() for t in tags_entry.get().split(",") if t.strip()]
            
            self.manager.update_item(item_id, title=title, data=data, 
                                    notes=notes, tags=tags, favorite=fav_var.get())
            self._refresh_items()
            dialog.destroy()
            messagebox.showinfo("成功", "条目已更新")
        
        def delete():
            if messagebox.askyesno("确认删除", "确定要删除此条目吗？"):
                self.manager.delete_item(item_id)
                self._refresh_items()
                dialog.destroy()
                messagebox.showinfo("成功", "条目已删除")
        
        ttk.Button(btn_frame, text="保存", command=save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="删除", command=delete).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="取消", command=dialog.destroy).pack(side="left", padx=5)
    
    def _show_context_menu(self, event):
        """显示右键菜单"""
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="查看/编辑", command=self._view_item)
        menu.add_command(label="复制标题", command=lambda: self._copy_field("title"))
        menu.add_separator()
        menu.add_command(label="删除", command=self._delete