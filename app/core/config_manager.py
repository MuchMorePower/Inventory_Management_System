# app/core/config_manager.py
import os

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.conf")

def save_company_name(name: str):
    """保存公司名称到配置文件"""
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            f.write(name)
    except IOError as e:
        print(f"Error saving config file: {e}")

def load_company_name() -> str:
    """从配置文件读取公司名称"""
    if not os.path.exists(CONFIG_FILE):
        return "" # 如果文件不存在，返回空字符串
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except IOError as e:
        print(f"Error loading config file: {e}")
        return ""
