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
        notes TEXT DEFAULT '',
        buyer TEXT DEFAULT '',      -- <<< 新增字段：购买方
        seller TEXT DEFAULT ''     -- <<< 新增字段：销售方
    )
    """)
    conn.commit()
    conn.close()

def add_transaction(product_name, model_number, unit, quantity, unit_price, insertion_date_str, notes="", buyer="", seller=""):
    """
    添加一条交易记录 (已更新，包含购买方和销售方)
    :param quantity: 正数表示入库，负数表示出库
    :param insertion_date_str: 'YYYY-MM-DD' 格式的字符串
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        total_amount = abs(quantity) * unit_price
        cursor.execute("""
        INSERT INTO transactions (insertion_date, product_name, model_number, unit, quantity, unit_price, total_amount, notes, buyer, seller)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (insertion_date_str, product_name, model_number, unit, quantity, unit_price, total_amount, notes, buyer, seller))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
        return None
    finally:
        conn.close()

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
    
    # 排序逻辑基于 id
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

def get_transactions_with_advanced_filter(filter_criteria: dict):
    """
    【新增】根据一个复杂的条件字典来动态构建查询
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query_parts = ["1=1"]  # 使用 1=1 作为基础，方便后面 AND 连接
    params = []

    if filter_criteria.get("product_name"):
        query_parts.append("product_name LIKE ?")
        params.append(f"%{filter_criteria['product_name']}%")
    
    if filter_criteria.get("model_number"):
        query_parts.append("model_number LIKE ?")
        params.append(f"%{filter_criteria['model_number']}%")

    if filter_criteria.get("buyer"):
        query_parts.append("buyer LIKE ?")
        params.append(f"%{filter_criteria['buyer']}%")

    if filter_criteria.get("seller"):
        query_parts.append("seller LIKE ?")
        params.append(f"%{filter_criteria['seller']}%")
        
    # 交易类型筛选
    trans_type = filter_criteria.get("transaction_type")
    if trans_type == "入库":
        query_parts.append("quantity > 0")
    elif trans_type == "出库":
        query_parts.append("quantity < 0")
    # 如果是 "全部"，则不添加此条件

    # 时间段筛选
    start_date = filter_criteria.get("start_date")
    end_date = filter_criteria.get("end_date")
    if start_date:
        query_parts.append("insertion_date >= ?")
        params.append(start_date)
    if end_date:
        query_parts.append("insertion_date <= ?")
        params.append(end_date)
        
    query = "SELECT * FROM transactions WHERE " + " AND ".join(query_parts) + " ORDER BY insertion_date DESC, transaction_time DESC"
    
    cursor.execute(query, params)
    transactions = [dict(row) for row in cursor.fetchall()]
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
    
    # 这里不使用 HAVING，因为我们希望显示所有商品，即使当前库存为0
    # group by 语句可能要进行修改，因为product_name 和 unit 可能会有多个名称
    cursor.execute("""
    SELECT product_name, model_number, unit, SUM(quantity) as current_stock
    FROM transactions
    WHERE is_undone = 0
    GROUP BY product_name, model_number, unit
    ORDER BY product_name, model_number
    """)
    summary = cursor.fetchall()
    conn.close()
    return summary

# 在模块加载时确保数据库和表已创建
initialize_database()