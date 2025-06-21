# app/core/config_manager.py
import os
import json

CONFIG_DIR = "config"
CONFIG_FILE = os.path.join(CONFIG_DIR, "settings.json")
DEFAULT_SCALE = 18 # 定义一个默认的缩放基准
DEFAULT_TTK_ADJUSTMENT = 1.0

def _load_config() -> dict:
    """【私有】加载完整的配置文件（JSON格式）"""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}

def _save_config(config_data: dict):
    """【私有】保存完整的配置文件（JSON格式）"""
    try:
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
    except IOError as e:
        print(f"Error saving config file: {e}")

# --- 公司名称相关 ---
def save_company_name(name: str):
    config = _load_config()
    config['company_name'] = name
    _save_config(config)

def load_company_name() -> str:
    config = _load_config()
    return config.get('company_name', "")

# --- UI缩放相关 (新增) ---
def save_ui_scale(scale: int):
    """保存UI缩放基准值"""
    config = _load_config()
    config['ui_scale'] = scale
    _save_config(config)

def load_ui_scale() -> int:
    """读取UI缩放基准值"""
    config = _load_config()
    # 使用 .get 提供一个默认值
    return config.get('ui_scale', DEFAULT_SCALE)

# --- 【新增】ttk 表格微调系数相关 ---
def save_ttk_scale_adjustment(adjustment: float):
    """保存 ttk 微调系数"""
    config = _load_config()
    config['ttk_scale_adjustment'] = adjustment
    _save_config(config)

def load_ttk_scale_adjustment() -> float:
    """读取 ttk 微调系数，如果不存在则默认为 1.0"""
    config = _load_config()
    return config.get('ttk_scale_adjustment', DEFAULT_TTK_ADJUSTMENT)
