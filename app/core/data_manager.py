# app/core/data_manager.py
import sqlite3
import os
from datetime import datetime

DATABASE_DIR = "database"
DATABASE_NAME = os.path.join(DATABASE_DIR, "inventory.db")

def get_db_connection():
    """获取数据库连接"""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # 允许通过列名访问数据
    return conn

def initialize_database():
    """初始化数据库，创建表（如果不存在）"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        insertion_date DATE NOT NULL,
        product_name TEXT NOT NULL,
        model_number TEXT NOT NULL,
        unit TEXT,
        quantity INTEGER NOT NULL, -- 正数入库，负数出库
        unit_price REAL NOT NULL,
        total_amount REAL NOT NULL, -- quantity * unit_price (绝对值)
        is_undone BOOLEAN DEFAULT 0, -- 0: 有效, 1: 已撤销
        notes TEXT DEFAULT ''
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(product_name, model_number, unit, quantity, unit_price, insertion_date_str, notes=""):
    """
    添加一条交易记录 (入库或出库)
    :param quantity: 正数表示入库，负数表示出库
    :param insertion_date_str: 'YYYY-MM-DD' 格式的字符串
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # 将字符串日期转换为 date 对象存储，如果数据库支持 DATE 类型并正确处理
        # 为简化，这里直接存字符串，查询时也用字符串比较或转换
        # datetime.strptime(insertion_date_str, '%Y-%m-%d').date()
        total_amount = abs(quantity) * unit_price
        cursor.execute("""
        INSERT INTO transactions (insertion_date, product_name, model_number, unit, quantity, unit_price, total_amount, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (insertion_date_str, product_name, model_number, unit, quantity, unit_price, total_amount, notes))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return None
    finally:
        conn.close()

# def get_all_transactions(include_undone=False, sort_by_date_desc=True):
#     """获取所有交易记录"""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     query = "SELECT * FROM transactions"
#     if not include_undone:
#         query += " WHERE is_undone = 0"
    
#     if sort_by_date_desc:
#         query += " ORDER BY insertion_date DESC, transaction_time DESC"
#     else:
#         query += " ORDER BY insertion_date ASC, transaction_time ASC"
        
#     cursor.execute(query)
#     transactions = cursor.fetchall()
#     conn.close()
#     return transactions

def get_all_transactions(include_undone=False, sort_desc=True):
    """
    获取所有交易记录, 按ID排序。
    
    Args:
        include_undone (bool): 是否包含已撤销的记录。默认为 False。
        sort_desc (bool): 是否按ID降序排序。默认为 False (即升序)。
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM transactions"
    
    # 根据 ainclude_undone 参数添加 WHERE 子句
    if not include_undone:
        query += " WHERE is_undone = 0"
    
    # 【核心修改】将排序逻辑改为基于 id
    if sort_desc:
        # 按 id 降序排序 (例如: 10, 9, 8, ...)
        query += " ORDER BY id DESC"
    else:
        # 按 id 升序排序 (例如: 1, 2, 3, ...)
        query += " ORDER BY id ASC"
        
    cursor.execute(query)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transaction_by_id(transaction_id):
    """通过ID获取单个交易记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    return transaction

def update_transaction_undone_status(transaction_id, is_undone):
    """更新交易的撤销状态"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE transactions SET is_undone = ? WHERE id = ?", (1 if is_undone else 0, transaction_id))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    finally:
        conn.close()

def delete_transaction_permanently(transaction_id):
    """永久删除一条交易记录 (请谨慎使用)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return False
    finally:
        conn.close()
        
def get_transactions_by_date(year=None, month=None, day=None):
    """按年、月、日查询交易记录 (未撤销的)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = ["is_undone = 0"]
    params = []

    if year:
        conditions.append("strftime('%Y', insertion_date) = ?")
        params.append(str(year))
    if month:
        conditions.append("strftime('%m', insertion_date) = ?")
        params.append(str(month).zfill(2)) # 保证两位月份
    if day:
        conditions.append("strftime('%d', insertion_date) = ?")
        params.append(str(day).zfill(2)) # 保证两位日期

    query = "SELECT * FROM transactions WHERE " + " AND ".join(conditions) + " ORDER BY insertion_date DESC, transaction_time DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transactions_by_filter(name_filter=None, model_filter=None):
    """按项目名称或规格型号筛选交易记录 (未撤销的)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    conditions = ["is_undone = 0"]
    params = []

    if name_filter:
        conditions.append("product_name LIKE ?")
        params.append(f"%{name_filter}%")
    if model_filter:
        conditions.append("model_number LIKE ?")
        params.append(f"%{model_filter}%")

    if len(conditions) == 1: # 只有 is_undone = 0
        query = "SELECT * FROM transactions WHERE is_undone = 0 ORDER BY insertion_date DESC, transaction_time DESC"
    else:
        query = "SELECT * FROM transactions WHERE " + " AND ".join(conditions) + " ORDER BY insertion_date DESC, transaction_time DESC"
    
    cursor.execute(query, params)
    transactions = cursor.fetchall()
    conn.close()
    return transactions

def get_transactions_by_ids(transaction_ids: list):
    """根据ID列表获取指定的交易记录"""
    if not transaction_ids:
        return []
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建SQL查询中的占位符，例如 (?, ?, ?)
    placeholders = ', '.join(['?'] * len(transaction_ids))
    query = f"SELECT * FROM transactions WHERE id IN ({placeholders})"
    
    cursor.execute(query, transaction_ids)
    transactions = cursor.fetchall()

    # 同样，转换为字典列表以保证兼容性
    transactions_as_dicts = [dict(row) for row in transactions]
    
    conn.close()
    
    return transactions_as_dicts

def get_product_summary():
    """获取单个种类商品的总体情况 (当前库存)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    # 只统计未撤销的交易
    cursor.execute("""
    SELECT product_name, model_number, unit, SUM(quantity) as current_stock
    FROM transactions
    WHERE is_undone = 0
    GROUP BY product_name, model_number, unit
    HAVING current_stock != 0 -- 可以只显示有库存的
    ORDER BY product_name, model_number
    """)
    summary = cursor.fetchall()
    conn.close()
    return summary

# 在模块加载时确保数据库和表已创建
initialize_database()