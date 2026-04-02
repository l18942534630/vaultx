# -*- coding: utf-8 -*-
"""
保险库数据管理模块
"""
import json
import secrets
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

from .crypto import CryptoEngine


# 数据存储路径
DATA_DIR = Path.home() / ".vaultx"
DATA_FILE = DATA_DIR / "vault.enc"


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
                {"key": "id_type", "label": "证件类型", "type": "select", 
                 "options": ["身份证", "护照", "驾照", "社保卡", "其他"]},
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
                {"key": "security", "label": "加密类型", "type": "select",
                 "options": ["WPA2", "WPA3", "WEP", "无"]},
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
                {"key": "billing_date", "label": "账单日", "type": "text"},
                {"key": "due_date", "label": "还款日", "type": "text"},
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
        "email": {
            "name": "邮箱账号",
            "icon": "📧",
            "fields": [
                {"key": "email", "label": "邮箱地址", "type": "email"},
                {"key": "password", "label": "密码", "type": "password"},
                {"key": "smtp_server", "label": "SMTP服务器", "type": "text"},
                {"key": "imap_server", "label": "IMAP服务器", "type": "text"},
            ]
        },
        "database": {
            "name": "数据库",
            "icon": "🗄️",
            "fields": [
                {"key": "db_name", "label": "数据库名", "type": "text"},
                {"key": "host", "label": "主机地址", "type": "text"},
                {"key": "port", "label": "端口", "type": "text"},
                {"key": "username", "label": "用户名", "type": "text"},
                {"key": "password", "label": "密码", "type": "password"},
            ]
        },
        "ssh": {
            "name": "SSH密钥",
            "icon": "🖥️",
            "fields": [
                {"key": "host", "label": "主机地址", "type": "text"},
                {"key": "port", "label": "端口", "type": "text"},
                {"key": "username", "label": "用户名", "type": "text"},
                {"key": "password", "label": "密码", "type": "password"},
                {"key": "private_key", "label": "私钥", "type": "textarea"},
            ]
        },
    }
    
    def __init__(self):
        self.items: List[Dict] = []
        self.folders: List[Dict] = []
        self.created_at: Optional[str] = None
        self.updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "items": self.items,
            "folders": self.folders,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VaultData':
        """从字典创建"""
        vault = cls()
        vault.items = data.get("items", [])
        vault.folders = data.get("folders", [])
        vault.created_at = data.get("created_at")
        vault.updated_at = data.get("updated_at")
        return vault


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
    
    def get_data_path(self) -> Path:
        """获取数据文件路径"""
        return DATA_FILE
    
    def create_vault(self, password: str) -> bool:
        """创建新保险库
        
        Args:
            password: 主密码
            
        Returns:
            是否成功
        """
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
        """解锁保险库
        
        Args:
            password: 主密码
            
        Returns:
            是否成功
        """
        try:
            if not DATA_FILE.exists():
                return False
                
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
        if self.vault and self.master_password:
            self.vault.updated_at = datetime.now().isoformat()
            encrypted = CryptoEngine.encrypt(
                self.vault.to_dict(), 
                self.master_password
            )
            DATA_FILE.write_bytes(encrypted)
    
    # ===== 条目操作 =====
    
    def add_item(
        self, 
        item_type: str, 
        title: str, 
        data: Dict,
        folder: str = None, 
        tags: List[str] = None, 
        notes: str = "", 
        favorite: bool = False
    ) -> Dict:
        """添加条目
        
        Args:
            item_type: 条目类型
            title: 标题
            data: 数据字段
            folder: 所属文件夹
            tags: 标签列表
            notes: 备注
            favorite: 是否收藏
            
        Returns:
            创建的条目
        """
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
        """更新条目
        
        Args:
            item_id: 条目ID
            **kwargs: 要更新的字段
            
        Returns:
            是否成功
        """
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
        """删除条目
        
        Args:
            item_id: 条目ID
            
        Returns:
            是否成功
        """
        for i, item in enumerate(self.vault.items):
            if item["id"] == item_id:
                del self.vault.items[i]
                self._save()
                return True
        return False
    
    def get_items(
        self, 
        item_type: str = None, 
        search: str = None,
        favorites_only: bool = False
    ) -> List[Dict]:
        """获取条目列表
        
        Args:
            item_type: 类型过滤
            search: 搜索关键词
            favorites_only: 仅收藏
            
        Returns:
            条目列表
        """
        items = self.vault.items
        
        if item_type:
            items = [i for i in items if i["type"] == item_type]
        
        if favorites_only:
            items = [i for i in items if i.get("favorite", False)]
        
        if search:
            search_lower = search.lower()
            items = [
                i for i in items 
                if search_lower in i["title"].lower()
                or search_lower in i.get("notes", "").lower()
                or any(
                    search_lower in str(v).lower() 
                    for v in i.get("data", {}).values()
                )
            ]
        
        # 排序：收藏在前，然后按更新时间
        items.sort(
            key=lambda x: (
                not x.get("favorite", False), 
                x.get("updated_at", "")
            ), 
            reverse=True
        )
        
        return items
    
    def get_item(self, item_id: str) -> Optional[Dict]:
        """获取单个条目
        
        Args:
            item_id: 条目ID
            
        Returns:
            条目或None
        """
        for item in self.vault.items:
            if item["id"] == item_id:
                return item
        return None
    
    # ===== 导入导出 =====
    
    def export_vault(self, filepath: str) -> bool:
        """导出加密备份
        
        Args:
            filepath: 导出路径
            
        Returns:
            是否成功
        """
        try:
            encrypted = CryptoEngine.encrypt(
                self.vault.to_dict(), 
                self.master_password
            )
            Path(filepath).write_bytes(encrypted)
            return True
        except Exception as e:
            print(f"导出失败: {e}")
            return False
    
    def import_vault(self, filepath: str, merge: bool = False) -> bool:
        """导入备份
        
        Args:
            filepath: 导入文件路径
            merge: 是否合并（True）或替换（False）
            
        Returns:
            是否成功
        """
        try:
            encrypted = Path(filepath).read_bytes()
            data = CryptoEngine.decrypt(encrypted, self.master_password)
            
            if data is None:
                return False
            
            imported = VaultData.from_dict(data)
            
            if merge:
                # 合并条目（不覆盖已存在的）
                existing_ids = {i["id"] for i in self.vault.items}
                for item in imported.items:
                    if item["id"] not in existing_ids:
                        self.vault.items.append(item)
            else:
                # 完全替换
                self.vault = imported
            
            self._save()
            return True
            
        except Exception as e:
            print(f"导入失败: {e}")
            return False
    
    # ===== 统计 =====
    
    def get_stats(self) -> Dict:
        """获取统计信息
        
        Returns:
            统计数据
        """
        if not self.vault:
            return {}
        
        items = self.vault.items
        
        # 按类型统计
        type_counts = {}
        for item in items:
            t = item.get("type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1
        
        return {
            "total": len(items),
            "favorites": sum(1 for i in items if i.get("favorite")),
            "by_type": type_counts,
            "created_at": self.vault.created_at,
            "updated_at": self.vault.updated_at,
        }
