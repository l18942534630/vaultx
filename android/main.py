# -*- coding: utf-8 -*-
"""
VaultX Android - 本地密码管理器 (Kivy)
"""
import os, json, base64, secrets, threading
from datetime import datetime
from pathlib import Path

from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, RoundedRectangle

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

APP_NAME, APP_VERSION = "VaultX", "1.0.0"
DATA_DIR = Path.home() / ".vaultx"
DATA_FILE = DATA_DIR / "vault.enc"

def dp(x): return x

# 加密
class Crypto:
    @staticmethod
    def key(pwd, salt):
        kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=600000)
        return base64.urlsafe_b64encode(kdf.derive(pwd.encode('utf-8')))
    
    @staticmethod
    def encrypt(data, pwd):
        salt, key = secrets.token_bytes(16), Crypto.key(pwd, salt)
        return base64.b64encode(salt + Fernet(key).encrypt(json.dumps(data, ensure_ascii=False).encode()))

    @staticmethod
    def decrypt(enc, pwd):
        try:
            raw = base64.b64decode(enc)
            return json.loads(Fernet(Crypto.key(pwd, raw[:16])).decrypt(raw[16:]).decode())
        except: return None

# 密码生成
class Gen:
    @staticmethod
    def pwd(len_=16, upper=True, lower=True, digits=True, symbols=False):
        c = (lower and "abcdefghijklmnopqrstuvwxyz" or "") + (upper and "ABCDEFGHIJKLMNOPQRSTUVWXYZ" or "") + (digits and "0123456789" or "") + (symbols and "!@#$%^&*()_+-=[]{}|;:,.<>?" or "") or "abcdefghijklmnopqrstuvwxyz"
        p = [(c and upper and "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and secrets.choice("abcdefghijklmnopqrstuvwxyz")) or (c and "abcdefghijklmnopqrstuvwxyz" and secrets.choice("abcdefghijklmnopqrstuvwxyz")), (c and upper and "ABCDEFGHIJKLMNOPQRSTUVWXYZ" and secrets.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")), (c and digits and secrets.choice("0123456789"))]
        while len(p) < len_: p.append(secrets.choice(c))
        secrets.SystemRandom().shuffle(p)
        return ''.join(p)
    
    @staticmethod
    def strength(pwd):
        s = sum([len(pwd) >= 8 and 15, len(pwd) >= 12 and 15, len(pwd) >= 16 and 10, any(c.islower() for c in pwd) and 10, any(c.isupper() for c in pwd) and 10, any(c.isdigit() for c in pwd) and 10, any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd) and 20])
        return min(s, 100), ["非常弱","弱","中等","强","非常强"][min(s // 20, 4)]

# 类型定义
TYPES = {
    "login": {"name": "登录密码", "icon": "🔐", "fields": [{"k":"username","l":"用户名","t":"text"},{"k":"password","l":"密码","t":"password"},{"k":"url","l":"网址","t":"text"}]},
    "bank": {"name": "银行卡", "icon": "💳", "fields": [{"k":"bank_name","l":"银行名称","t":"text"},{"k":"card_number","l":"卡号","t":"text"},{"k":"cvv","l":"CVV","t":"password"},{"k":"pin","l":"PIN码","t":"password"}]},
    "api": {"name": "API密钥", "icon": "🔑", "fields": [{"k":"api_key","l":"API Key","t":"text"},{"k":"secret","l":"Secret","t":"password"}]},
    "personal": {"name": "个人信息", "icon": "👤", "fields": [{"k":"full_name","l":"姓名","t":"text"},{"k":"id_number","l":"证件号码","t":"text"}]},
    "note": {"name": "安全笔记", "icon": "📝", "fields": [{"k":"content","l":"内容","t":"textarea"}]},
    "wifi": {"name": "WiFi密码", "icon": "📶", "fields": [{"k":"ssid","l":"网络名称","t":"text"},{"k":"password","l":"密码","t":"password"}]},
    "credit": {"name": "信用卡", "icon": "💳", "fields": [{"k":"card_name","l":"卡片名称","t":"text"},{"k":"card_number","l":"卡号","t":"text"},{"k":"cvv","l":"CVV","t":"password"}]},
    "email": {"name": "邮箱账号", "icon": "📧", "fields": [{"k":"email","l":"邮箱地址","t":"text"},{"k":"password","l":"密码","t":"password"}]},
}
TYPE_LIST = ["🔐 登录密码","💳 银行卡","🔑 API密钥","👤 个人信息","📝 安全笔记","📶 WiFi密码","💳 信用卡","📧 邮箱账号"]
TYPE_MAP = {v: k for k, v in TYPES.items()}

# 保险库管理
class Vault:
    def __init__(self):
        self.d, self.pwd = {"items":[]}, None
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    def ready(self): return DATA_FILE.exists()
    def create(self, pwd):
        try: self.pwd, self.d = pwd, {"items":[],"created_at":datetime.now().isoformat()}; self._save(); return True
        except: return False
    def unlock(self, pwd):
        try:
            d = Crypto.decrypt(DATA_FILE.read_bytes(), pwd)
            if not d: return False
            self.d, self.pwd = d, pwd; return True
        except: return False
    def lock(self): self.d, self.pwd = {"items":[]}, None
    def _save(self):
        if self.pwd: DATA_FILE.write_bytes(Crypto.encrypt(self.d, self.pwd))
    def add(self, type_, title, data, notes=""):
        item = {"id":secrets.token_hex(16),"type":type_,"title":title,"data":data,"notes":notes,"favorite":False,"created_at":datetime.now().isoformat(),"updated_at":datetime.now().isoformat()}
        self.d["items"].append(item); self._save(); return item
    def del_(self, id_):
        for i, item in enumerate(self.d["items"]):
            if item["id"] == id_: del self.d["items"][i]; self._save(); return True
        return False
    def items(self, type_=None, search=None):
        its = self.d.get("items", [])
        if type_: its = [i for i in its if i["type"] == type_]
        if search: s = search.lower(); its = [i for i in its if s in i["title"].lower()]
        its.sort(key=lambda x: (not x.get("favorite"), x.get("updated_at","")), reverse=True)
        return its

# Toast
class Toast:
    @staticmethod
    def show(msg):
        p = Popup(content=Label(text=msg, font_size="14sp", halign="center", valign="middle", text_size=(280, None)),
                  size_hint=(0.7, 0.12), pos_hint={"center_y":0.12}, background_color=(0.2,0.2,0.2,0.9))
        p.open()
        threading.Timer(2.5, p.dismiss).start()

# KV布局
KV = """
<SM>:
    LockScreen:
    MainScreen:
    AddScreen:
    ViewScreen:

# 锁定屏幕
<LockScreen>:
    name: "lock"
    BoxLayout:
        orientation: "vertical"
        padding: [0, dp(60), 0, dp(40)]
        spacing: dp(15)
        
        Label:
            text: "🔐"
            font_size: "50sp"
            size_hint_y: None
            height: dp(60)
        Label:
            text: "VaultX"
            font_size: "30sp"
            bold: True
            color: 0.1, 0.4, 0.8, 1
        Label:
            text: "安全密码管理器"
            font_size: "14sp"
            color: 0.5, 0.5, 0.5, 1
        
        TextInput:
            id: pwd_in
            hint_text: "输入主密码"
            password: True
            multiline: False
            size_hint_x: 0.85
            pos_hint: {"center_x": 0.5}
            padding: [dp(15), dp(12)]
            font_size: "17sp"
            on_text_validate: root.do_ok()
        
        Button:
            id: ok_btn
            text: "创建保险库"
            size_hint_x: 0.85
            pos_hint: {"center_x": 0.5}
            height: dp(50)
            font_size: "16sp"
            background_color: 0.1, 0.4, 0.8, 1
            on_release: root.do_ok()
        
        Label:
            text: "🔒 AES-256 加密  ·  💾 本地存储  ·  🚫 无网络"
            font_size: "11sp"
            color: 0.55, 0.55, 0.55, 1
            size_hint_y: None
            height: dp(30)

# 主屏幕
<MainScreen>:
    name: "main"
    BoxLayout:
        orientation: "vertical"
        
        # 顶栏
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(12)
            canvas.before:
                Color: rgba(0.1, 0.4, 0.8, 1)
                Rectangle: pos=self.pos, size=self.size
            Label:
                text: "🔐  VaultX"
                font_size: "22sp"
                bold: True
                color: 1, 1, 1, 1
            Widget:
            Button:
                text: "🔒"
                font_size: "22sp"
                background_color: 0, 0, 0, 0
                on_release: app.lock_vault()
        
        # 搜索
        TextInput:
            id: search_in
            hint_text: "🔍  搜索..."
            multiline: False
            size_hint_y: None
            height: dp(48)
            padding: [dp(12), dp(10)]
            font_size: "15sp"
            on_text: root.do_search(self.text)
        
        # 分类栏
        ScrollView:
            size_hint_y: None
            height: dp(48)
            do_scroll_x: True
            do_scroll_y: False
            bar_width: 0
            BoxLayout:
                id: cat_bar
                size_hint_x: None
                spacing: dp(6)
                padding: [dp(10), dp(6)]
                width: self.minimum_width
        
        # 条目列表
        ScrollView:
            BoxLayout:
                id: items_box
                orientation: "vertical"
                spacing: dp(8)
                padding: dp(10)
                size_hint_y: None
                height: self.minimum_height
        
        # 底栏
        BoxLayout:
            size_hint_y: None
            height: dp(58)
            padding: dp(12), dp(6)
            spacing: dp(10)
            Button:
                text: "🔑 密码生成"
                font_size: "13sp"
                background_color: 0.2, 0.6, 0.3, 1
                on_release: root.show_gen()
            Button:
                text: "➕ 添加"
                font_size: "13sp"
                background_color: 0.1, 0.4, 0.8, 1
                on_release: app.go_add()

# 添加屏幕
<AddScreen>:
    name: "add"
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(10)
            spacing: dp(10)
            canvas.before:
                Color: rgba(0.1, 0.4, 0.8, 1)
                Rectangle: pos=self.pos, size=self.size
            Button:
                text: "← 返回"
                size_hint_x: None
                width: dp(75)
                background_color: 0, 0, 0, 0
                color: 1, 1, 1, 1
                font_size: "14sp"
                on_release: app.root.current = "main"
            Label:
                text: "添加条目"
                font_size: "20sp"
                bold: True
                color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                id: add_form
                orientation: "vertical"
                padding: dp(15)
                spacing: dp(12)
                size_hint_y: None
                height: self.minimum_height
        Button:
            text: "✓ 保存"
            size_hint_y: None
            height: dp(50)
            font_size: "16sp"
            background_color: 0.1, 0.4, 0.8, 1
            on_release: root.do_save()

# 查看屏幕
<ViewScreen>:
    name: "view"
    BoxLayout:
        orientation: "vertical"
        BoxLayout:
            size_hint_y: None
            height: dp(56)
            padding: dp(10)
            spacing: dp(10)
            canvas.before:
                Color: rgba(0.1, 0.4, 0.8, 1)
                Rectangle: pos=self.pos, size=self.size
            Button:
                text: "← 返回"
                size_hint_x: None
                width: dp(75)
                background_color: 0, 0, 0, 0
                color: 1, 1, 1, 1
                font_size: "14sp"
                on_release: app.root.current = "main"
            Label:
                id: vtitle
                text: "查看"
                font_size: "20sp"
                bold: True
                color: 1, 1, 1, 1
        ScrollView:
            BoxLayout:
                id: vcontent
                orientation: "vertical"
                padding: dp(15)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height
        BoxLayout:
            size_hint_y: None
            height: dp(58)
            padding: dp(12), dp(6)
            spacing: dp(10)
            Button:
                text: "🗑 删除"
                background_color: 0.8, 0.2, 0.2, 1
                font_size: "14sp"
                on_release: root.do_del()
            Button:
                text: "✏ 重新添加"
                background_color: 0.1, 0.4, 0.8, 1
                font_size: "14sp"
                on_release: root.do_readd()
"""

class SM(ScreenManager): pass

class LockScreen(Screen):
    def on_enter(self):
        self.ids.ok_btn.text = "解锁" if app.manager.ready() else "创建保险库"
    def do_ok(self):
        pwd = self.ids.pwd_in.text.strip()
        if not pwd: Toast.show("请输入主密码"); return
        if app.manager.ready():
            if app.manager.unlock(pwd):
                app.root.current = "main"; self.ids.pwd_in.text = ""; app.main_screen.refresh()
            else: Toast.show("密码错误")
        else:
            if len(pwd) < 8: Toast.show("主密码至少8位"); return
            if app.manager.create(pwd):
                app.root.current = "main"; self.ids.pwd_in.text = ""; app.main_screen.refresh()

class MainScreen(Screen):
    cur_type = "all"
    def on_enter(self): self.refresh()
    def refresh(self):
        bar = self.ids.cat_bar; bar.clear_widgets()
        cats = [("all","📋 全部")] + [(k, "{} {}".format(v["icon"], v["name"])) for k,v in TYPES.items()]
        for tid, lbl in cats:
            b = Button(text=lbl, size_hint_x=None, width=dp(105), font_size="12sp",
                      background_color=(0.1,0.4,0.8,1) if tid==self.cur_type else (0.85,0.85,0.87,1),
                      color=(1,1,1,1) if tid==self.cur_type else (0.2,0.2,0.2,1))
            b.bind(on_release=lambda x, t=tid: self.sel_cat(t))
            bar.add_widget(b)
        self.do_search(self.ids.search_in.text or "")
    
    def sel_cat(self, t):
        self.cur_type = t; self.refresh()
    
    def do_search(self, txt):
        box = self.ids.items_box; box.clear_widgets()
        its = app.manager.items(type_=None if self.cur_type=="all" else self.cur_type, search=txt)
        if not its:
            box.add_widget(Label(text="暂无条目，点击下方「添加」创建", font_size="14sp", color=(0.5,0.5,0.5,1), size_hint_y=None, height=dp(80), halign="center"))
            return
        for item in its:
            ti = TYPES.get(item["type"], {})
            icon, tname = ti.get("icon","📄"), ti.get("name","")
            pwd = item.get("data",{}).get("password","") or ""
            mask = "●"*min(len(pwd),12) if pwd else "—"
            
            card = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(82), padding=[dp(14),dp(8)], spacing=dp(10))
            with card.canvas.before:
                Color(rgba=(0.95,0.95,0.97,1))
                RoundedRectangle(pos=card.pos, size=card.size, radius=[dp(10)])
            card.add_widget(Label(text=icon, font_size="26sp", size_hint_x=None, width=dp(42), halign="center", valign="middle"))
            
            c = BoxLayout(orientation="vertical", spacing=dp(1))
            for txt2, clr, sz, bld in [(item["title"],(0.15,0.15,0.15,1),"16sp",True),(tname,(0.5,0.5,0.5,1),"12sp",False),(mask,(0.35,0.35,0.35,1),"12sp",False)]:
                lbl = Label(text=txt2, font_size=sz, color=clr, bold=bld, text_size=(dp(190),None), halign="left", valign="middle", shorten=True)
                c.add_widget(lbl)
            card.add_widget(c)
            
            btns = BoxLayout(orientation="horizontal", size_hint_x=None, width=dp(88), spacing=dp(4))
            
            def mc(iid):
                def cpy():
                    it = next((x for x in app.manager.d.get("items",[]) if x["id"]==iid),None)
                    if it and it.get("data",{}).get("password"): Clipboard.copy(it["data"]["password"]); Toast.show("密码已复制")
                return cpy
            
            def mv(iid):
                def vw():
                    app.view_screen.show(iid); app.root.current = "view"
                return vw
            
            bc = Button(text="📋", font_size="18sp", background_color=(0.72,0.72,0.72,1))
            bc.bind(on_release=mc(item["id"]))
            bv = Button(text="👁", font_size="18sp", background_color=(0.1,0.4,0.8,1))
            bv.bind(on_release=mv(item["id"]))
            btns.add_widget(bc); btns.add_widget(bv)
            card.add_widget(btns)
            box.add_widget(card)
    
    def show_gen(self):
        pwd = [Gen.pwd(16, symbols=True)]
        
        def up(lbl, slbl):
            pwd[0] = Gen.pwd(16, symbols=True)
            lbl.text = pwd[0]; s,v = Gen.strength(pwd[0]); slbl.text = "强度: {} ({}分)".format(v,s)
        
        def cp():
            Clipboard.copy(pwd[0]); Toast.show("已复制")
        
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(10), size_hint_y=None, height=dp(320))
        content.add_widget(Label(text="🔑 密码生成器", font_size="20sp", bold=True, size_hint_y=None, height=dp(40)))
        
        plbl = Label(text=pwd[0], font_size="16sp", color=(0.1,0.4,0.8,1), text_size=(Window.width-dp(60),None), halign="left", valign="middle")
        content.add_widget(plbl)
        
        s,v = Gen.strength(pwd[0])
        slbl = Label(text="强度: {} ({}分)".format(v,s), font_size="13sp", size_hint_y=None, height=dp(28))
        content.add_widget(slbl)
        
        bc = Button(text="📋 复制", size_hint_y=None, height=dp(44), background_color=(0.1,0.4,0.8,1), font_size="15sp")
        bg = Button(text="🎲 重新生成", size_hint_y=None, height=dp(44), background_color=(0.2,0.6,0.3,1), font_size="15sp")
        bx = Button(text="关闭", size_hint_y=None, height=dp(40), background_color=(0.7,0.7,0.7,1), font_size="14sp")
        
        bc.bind(on_release=lambda x: cp())
        bg.bind(on_release=lambda x: up(plbl, slbl))
        bx.bind(on_release=lambda x: p.dismiss())
        
        content.add_widget(bc); content.add_widget(bg); content.add_widget(bx)
        p = Popup(title="密码生成器", content=content, size_hint=(0.92, 0.52), background_color=(1,1,1,1), auto_dismiss=False)
        p.open()

class AddScreen(Screen):
    fw = {}  # field widgets
    
    def on_enter(self):
        self.ids.add_form.clear_widgets(); self.fw = {}
        
        # 类型
        self.ids.add_form.add_widget(Label(text="类型", font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
        sp = Spinner(text="🔐 登录密码", values=TYPE_LIST, size_hint_y=None, height=dp(42), font_size="15sp")
        sp.bind(text=lambda s,v: self.build())
        self.ids.add_form.add_widget(sp)
        self.spinner = sp
        
        # 标题
        self.ids.add_form.add_widget(Label(text="标题", font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
        ti = TextInput(hint_text="输入标题", multiline=False, size_hint_y=None, height=dp(42), padding=[dp(10),dp(8)], font_size="15sp")
        self.ids.add_form.add_widget(ti)
        self.title_in = ti
        
        # 动态字段
        self.fields_box = BoxLayout(orientation="vertical", size_hint_y=None, height=self.minimum_height)
        self.ids.add_form.add_widget(self.fields_box)
        
        # 备注
        self.ids.add_form.add_widget(Label(text="备注", font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
        ni = TextInput(hint_text="备注信息（可选）", multiline=True, size_hint_y=None, height=dp(70), padding=[dp(10),dp(8)], font_size="14sp")
        self.ids.add_form.add_widget(ni)
        self.notes_in = ni
        
        self.build()
    
    def build(self):
        self.fields_box.clear_widgets(); self.fw = {}
        tid = TYPE_MAP.get(self.spinner.text, "login")
        for f in TYPES.get(tid, {}).get("fields", []):
            box = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(70))
            box.add_widget(Label(text=f["l"], font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
            row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(5))
            inp = TextInput(hint_text=f["l"], multiline=False, padding=[dp(10),dp(6)], font_size="15sp", size_hint_x=1)
            if f["t"] == "password": inp.password = True
            if f["t"] == "textarea":
                inp.multiline = True; box.height = dp(90); row.height = dp(60)
            
            row.add_widget(inp)
            
            if f["t"] == "password":
                def mg(e=inp):
                    def gen():
                        e.text = Gen.pwd(16, symbols=True); e.password = False
                    return gen
                bg = Button(text="🎲", size_hint_x=None, width=dp(44), background_color=(0.2,0.6,0.3,1), font_size="16sp")
                bg.bind(on_release=mg(inp))
                row.add_widget(bg)
                
                showing = [False]
                def mt(e=inp, sh=showing):
                    def tgl():
                        sh[0] = not sh[0]; e.password = not sh[0]
                    return tgl
                bt = Button(text="👁", size_hint_x=None, width=dp(44), background_color=(0.7,0.7,0.7,1), font_size="16sp")
                bt.bind(on_release=mt(inp, showing))
                row.add_widget(bt)
            
            box.add_widget(row)
            self.fields_box.add_widget(box)
            self.fw[f["k"]] = inp
    
    def do_save(self):
        title = self.title_in.text.strip()
        if not title: Toast.show("请输入标题"); return
        tid = TYPE_MAP.get(self.spinner.text, "login")
        data = {k: w.text for k, w in self.fw.items()}
        notes = self.notes_in.text
        app.manager.add(tid, title, data, notes)
        Toast.show("保存成功")
        app.root.current = "main"

class ViewScreen(Screen):
    iid = None
    
    def show(self, item_id):
        self.iid = item_id
        item = next((x for x in app.manager.d.get("items",[]) if x["id"]==item_id), None)
        if not item: return
        self.ids.vtitle.text = item["title"]
        box = self.ids.vcontent; box.clear_widgets()
        ti = TYPES.get(item["type"], {})
        
        for f in ti.get("fields", []):
            val = item.get("data",{}).get(f["k"],"") or ""
            vbox = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(75))
            vbox.add_widget(Label(text=f["l"], font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
            
            row = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
            
            if f["t"] == "password":
                masked = "●"*min(len(val),12) if val else "—"
                vlbl = Label(text=masked, font_size="16sp", color=(0.1,0.1,0.1,1), size_hint_x=1, text_size=(Window.width-dp(170),None), halign="left", valign="middle")
                showing = [False]
                def mt2(lbl, v, sh=showing):
                    def t():
                        sh[0] = not sh[0]; lbl.text = v if sh[0] else "●"*len(v)
                    return t
                bc = Button(text="📋", size_hint_x=None, width=dp(44), background_color=(0.1,0.4,0.8,1), font_size="16sp")
                bc.bind(on_release=lambda x,v=val: (Clipboard.copy(v), Toast.show("已复制")) if v else None)
                be = Button(text="👁", size_hint_x=None, width=dp(44), background_color=(0.7,0.7,0.7,1), font_size="16sp")
                be.bind(on_release=mt2(vlbl, val, showing))
                row.add_widget(vlbl); row.add_widget(bc); row.add_widget(be)
            else:
                vlbl = Label(text=val or "—", font_size="15sp", color=(0.15,0.15,0.15,1), size_hint_x=1, text_size=(Window.width-dp(70),None), halign="left", valign="middle")
                bc = Button(text="📋", size_hint_x=None, width=dp(44), background_color=(0.1,0.4,0.8,1), font_size="16sp")
                bc.bind(on_release=lambda x,v=val: (Clipboard.copy(v), Toast.show("已复制")) if v else None)
                row.add_widget(vlbl); row.add_widget(bc)
            
            vbox.add_widget(row)
            box.add_widget(vbox)
        
        if item.get("notes"):
            nvbox = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(80))
            nvbox.add_widget(Label(text="备注", font_size="13sp", color=(0.45,0.45,0.45,1), size_hint_y=None, height=dp(20), text_size=self.size, halign="left"))
            nlbl = Label(text=item["notes"], font_size="14sp", color=(0.2,0.2,0.2,1), text_size=(Window.width-dp(30),None), halign="left", valign="top")
            nvbox.add_widget(nlbl)
            box.add_widget(nvbox)
    
    def do_del(self):
        if self.iid:
            app.manager.del_(self.iid); Toast.show("已删除")
            app.root.current = "main"
    
    def do_readd(self):
        if self.iid:
            item = next((x for x in app.manager.d.get("items",[]) if x["id"]==self.iid), None)
            app.manager.del_(self.iid)
            if item:
                app.add_screen.ids.add_form.clear_widgets()
                app.root.current = "add"

class VaultXApp(App):
    def build(self):
        Builder.load_string(KV)
        Window.size = (400, 720)
        sm = SM()
        self.lock_screen = LockScreen(name="lock")
        self.main_screen = MainScreen(name="main")
        self.add_screen = AddScreen(name="add")
        self.view_screen = ViewScreen(name="view")
        sm.add_widget(self.lock_screen)
        sm.add_widget(self.main_screen)
        sm.add_widget(self.add_screen)
        sm.add_widget(self.view_screen)
        self.root = sm
        self.manager = Vault()
        return sm
    
    def lock_vault(self):
        self.manager.lock()
        self.root.current = "lock"
    
    def go_add(self):
        self.add_screen.on_enter()
        self.root.current = "add"

app = None
def main():
    global app
    app = VaultXApp()
    app.run()

if __name__ == '__main__':
    main()
