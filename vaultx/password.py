# -*- coding: utf-8 -*-
"""
密码生成器模块
"""
import secrets
from typing import List, Tuple


class PasswordGenerator:
    """密码生成器"""
    
    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGITS = "0123456789"
    SYMBOLS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    AMBIGUOUS = "il1Lo0O"  # 易混淆字符
    
    @staticmethod
    def generate(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = False,
        exclude_ambiguous: bool = True
    ) -> str:
        """生成随机密码
        
        Args:
            length: 密码长度
            use_upper: 包含大写字母
            use_lower: 包含小写字母
            use_digits: 包含数字
            use_symbols: 包含特殊字符
            exclude_ambiguous: 排除易混淆字符
            
        Returns:
            生成的密码
        """
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
    def calculate_strength(password: str) -> Tuple[int, str, List[str]]:
        """计算密码强度
        
        Args:
            password: 密码
            
        Returns:
            (分数, 等级, 建议)
        """
        score = 0
        feedback = []
        
        # 长度评分
        if len(password) >= 8:
            score += 15
        else:
            feedback.append("长度至少8位")
            
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
            feedback.append("添加小写字母")
            
        if any(c.isupper() for c in password):
            score += 10
        else:
            feedback.append("添加大写字母")
            
        if any(c.isdigit() for c in password):
            score += 10
        else:
            feedback.append("添加数字")
            
        if any(c in PasswordGenerator.SYMBOLS for c in password):
            score += 20
        else:
            feedback.append("添加特殊字符")
        
        # 检查重复和连续字符
        if len(set(password)) < len(password) * 0.5:
            score -= 10
            feedback.append("避免过多重复字符")
        
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
        
        return min(max(score, 0), 100), level, feedback
    
    @staticmethod
    def generate_passphrase(word_count: int = 4, separator: str = "-") -> str:
        """生成密码短语 (Diceware风格)
        
        Args:
            word_count: 单词数量
            separator: 分隔符
            
        Returns:
            密码短语
        """
        # 简化的词表 (实际应用应使用完整Diceware词表)
        words = [
            "apple", "brave", "cloud", "delta", "eagle", "focus", "guitar", "house",
            "igloo", "jungle", "kite", "lemon", "mango", "noble", "ocean", "piano",
            "queen", "river", "storm", "tiger", "unity", "vivid", "whale", "xenon",
            "yacht", "zebra", "amber", "blade", "coral", "drift", "ember", "flame",
            "globe", "haven", "index", "jewel", "knack", "lunar", "marble", "north",
            "orbit", "pearl", "quest", "raven", "solar", "terra", "ultra", "vapor",
            "wave", "xray", "yield", "zephyr", "aegis", "beam", "crisp", "dawn",
        ]
        
        selected = [secrets.choice(words) for _ in range(word_count)]
        return separator.join(selected)
