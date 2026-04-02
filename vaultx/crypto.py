# -*- coding: utf-8 -*-
"""
加密引擎模块
使用 AES-256 (Fernet) 加密
"""
import base64
import secrets
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class CryptoEngine:
    """加密引擎 - 使用 AES-256 (Fernet)"""
    
    # PBKDF2 迭代次数 (推荐 60万+)
    ITERATIONS = 600000
    
    @staticmethod
    def derive_key(password: str, salt: bytes) -> bytes:
        """从主密码派生加密密钥
        
        Args:
            password: 主密码
            salt: 盐值 (16字节)
            
        Returns:
            Base64编码的Fernet密钥
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=CryptoEngine.ITERATIONS,
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(password.encode('utf-8'))
        )
        return key
    
    @staticmethod
    def encrypt(data: Any, password: str) -> bytes:
        """加密数据
        
        Args:
            data: 要加密的数据 (会被JSON序列化)
            password: 主密码
            
        Returns:
            Base64编码的加密数据 (salt + encrypted)
        """
        import json
        
        # 生成随机盐值
        salt = secrets.token_bytes(16)
        
        # 派生密钥
        key = CryptoEngine.derive_key(password, salt)
        
        # 创建Fernet实例
        f = Fernet(key)
        
        # 序列化数据
        json_data = json.dumps(data, ensure_ascii=False, indent=2)
        
        # 加密
        encrypted = f.encrypt(json_data.encode('utf-8'))
        
        # 组合: salt(16) + encrypted
        return base64.b64encode(salt + encrypted)
    
    @staticmethod
    def decrypt(encrypted_data: bytes, password: str) -> Optional[Any]:
        """解密数据
        
        Args:
            encrypted_data: 加密的数据
            password: 主密码
            
        Returns:
            解密后的数据，失败返回None
        """
        import json
        
        try:
            # 解码
            raw = base64.b64decode(encrypted_data)
            
            # 提取盐值和加密数据
            salt = raw[:16]
            encrypted = raw[16:]
            
            # 派生密钥
            key = CryptoEngine.derive_key(password, salt)
            
            # 创建Fernet实例
            f = Fernet(key)
            
            # 解密
            decrypted = f.decrypt(encrypted)
            
            # 反序列化
            return json.loads(decrypted.decode('utf-8'))
            
        except Exception:
            return None
    
    @staticmethod
    def hash_password(password: str) -> str:
        """哈希密码 (用于验证)
        
        Args:
            password: 密码
            
        Returns:
            哈希值
        """
        import hashlib
        return hashlib.sha256(password.encode()).hexdigest()
