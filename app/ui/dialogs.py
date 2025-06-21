# app/ui/dialogs.py
import customtkinter as ctk
from datetime import datetime
import tkinter.messagebox as tkmb # For simple pop-up messages

class SettingsDialog(ctk.CTkToplevel):
    """【全新】用于设置公司名称的对话框"""
    def __init__(self, parent, current_name=""):
        super().__init__(parent)
        self.transient(parent)
        self.title("设置")
        self.geometry("400x180")
        self.result = None

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="本公司名称:").pack(padx=10, pady=(5, 5), anchor="w")
        self.entry_company_name = ctk.CTkEntry(main_frame, placeholder_text="请输入本公司名称...")
        self.entry_company_name.insert(0, current_name)
        self.entry_company_name.pack(padx=10, pady=5, fill="x")

        btn_save = ctk.CTkButton(main_frame, text="保存", command=self.save_settings)
        btn_save.pack(padx=10, pady=20)

        self.grab_set()
        self.lift()
        self.entry_company_name.focus_set()

    def save_settings(self):
        self.result = self.entry_company_name.get().strip()
        self.destroy()

    def get_new_name(self):
        self.wait_window(self)
        return self.result

class TransactionDialog(ctk.CTkToplevel):
    """
    用于处理商品入库和出库的对话框。
    已更新，增加了'购买方'和'销售方'字段。
    """
    def __init__(self, parent, title="交易记录", transaction_type="", company_name="", existing_data=None):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
        self.transaction_type = transaction_type
        self.existing_data = existing_data if existing_data else {}
        # --- 修改：稍微加高窗口以容纳新控件 ---
        self.geometry("450x620") 

        # --- 修改：优化字体以获得更好的中文显示效果 ---
        label_font = ("Microsoft YaHei UI", 14)
        entry_font = ("Microsoft YaHei UI", 14)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- 控件定义 (原有控件保持不变) ---
        ctk.CTkLabel(main_frame, text="项目名称:", font=label_font).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.entry_product_name = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_product_name.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="规格型号:", font=label_font).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.entry_model_number = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_model_number.grid(row=1, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="单位:", font=label_font).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.entry_unit = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_unit.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="数量:", font=label_font).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.entry_quantity = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_quantity.grid(row=3, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="单价:", font=label_font).grid(row=4, column=0, padx=5, pady=8, sticky="w")
        self.entry_unit_price = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_unit_price.grid(row=4, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="操作日期 (YYYY-MM-DD):", font=label_font).grid(row=5, column=0, padx=5, pady=8, sticky="w")
        self.entry_insertion_date = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_insertion_date.grid(row=5, column=1, padx=5, pady=8, sticky="ew")
        self.entry_insertion_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # --- 关键修改：同时创建购买方和销售方输入框，并设置默认值 ---
        ctk.CTkLabel(main_frame, text="购买方:").grid(row=6, column=0, padx=5, pady=8, sticky="w")
        self.entry_buyer = ctk.CTkEntry(main_frame, width=250)
        self.entry_buyer.grid(row=6, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="销售方:").grid(row=7, column=0, padx=5, pady=8, sticky="w")
        self.entry_seller = ctk.CTkEntry(main_frame, width=250)
        self.entry_seller.grid(row=7, column=1, padx=5, pady=8, sticky="ew")

        if transaction_type == "入库":
            # 入库时，本公司是购买方，所以默认填入公司名
            self.entry_buyer.insert(0, company_name)
            self.entry_seller.configure(placeholder_text="请输入销售方名称...")
        elif transaction_type == "出库":
            # 出库时，本公司是销售方，所以默认填入公司名
            self.entry_seller.insert(0, company_name)
            self.entry_buyer.configure(placeholder_text="请输入购买方名称...")

        # 调整后续控件的行号
        ctk.CTkLabel(main_frame, text="备注:").grid(row=8, column=0, padx=5, pady=8, sticky="nw")
        self.entry_notes = ctk.CTkTextbox(main_frame, height=80)
        self.entry_notes.grid(row=8, column=1, padx=5, pady=8, sticky="ew")

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=20, sticky="ew")

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)

        self.button_confirm = ctk.CTkButton(button_frame, text="确认", command=self._confirm_input)
        self.button_confirm.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        self.button_cancel = ctk.CTkButton(button_frame, text="取消", command=self._cancel_event, fg_color="gray")
        self.button_cancel.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # (填充编辑数据的逻辑保持不变，但新字段不会被填充，因为旧数据没有)
        if self.existing_data:
            # --- 编辑模式：用旧数据填充所有字段 ---
            self.entry_product_name.insert(0, self.existing_data.get('product_name', ''))
            self.entry_model_number.insert(0, self.existing_data.get('model_number', ''))
            self.entry_unit.insert(0, self.existing_data.get('unit', ''))
            self.entry_quantity.insert(0, str(abs(self.existing_data.get('quantity', ''))))
            self.entry_unit_price.insert(0, str(self.existing_data.get('unit_price', '')))
            self.entry_insertion_date.insert(0, self.existing_data.get('insertion_date', ''))
            self.entry_buyer.insert(0, self.existing_data.get('buyer', ''))
            self.entry_seller.insert(0, self.existing_data.get('seller', ''))
            self.entry_notes.insert("1.0", self.existing_data.get('notes', ''))
        
        self.grab_set()
        self.lift()
        self.entry_product_name.focus_set()

    def _validate_input(self):
        # (验证逻辑不需要改变，因为新字段是可选的)
        product_name = self.entry_product_name.get().strip()
        model_number = self.entry_model_number.get().strip()
        quantity_str = self.entry_quantity.get().strip()
        unit_price_str = self.entry_unit_price.get().strip()
        insertion_date = self.entry_insertion_date.get().strip()
        if not all([product_name, model_number, quantity_str, unit_price_str, insertion_date]):
            tkmb.showerror("输入错误", "项目名称, 规格型号, 数量, 单价, 操作日期不能为空!", parent=self)
            return False
        try:
            quantity = int(quantity_str)
            if quantity <= 0:
                tkmb.showerror("输入错误", "数量必须是正整数!", parent=self)
                return False
        except ValueError:
            tkmb.showerror("输入错误", "数量必须是有效的整数!", parent=self)
            return False
        try:
            unit_price = float(unit_price_str)
            if unit_price < 0:
                tkmb.showerror("输入错误", "单价不能为负数!", parent=self)
                return False
        except ValueError:
            tkmb.showerror("输入错误", "单价必须是有效的数字!", parent=self)
            return False
        try:
            datetime.strptime(insertion_date, '%Y-%m-%d')
        except ValueError:
            tkmb.showerror("输入错误", "日期格式应为YYYY-MM-DD!", parent=self)
            return False
        return True

    def _confirm_input(self):
        if not self._validate_input():
            return

        # --- 修改：在返回结果中加入新字段的数据 ---
        self.result = {
            "product_name": self.entry_product_name.get().strip(),
            "model_number": self.entry_model_number.get().strip(),
            "unit": self.entry_unit.get().strip(),
            "quantity": int(self.entry_quantity.get().strip()),
            "unit_price": float(self.entry_unit_price.get().strip()),
            "insertion_date": self.entry_insertion_date.get().strip(),
            "notes": self.entry_notes.get("1.0", "end-1c").strip(),
            # 使用 hasattr 检查控件是否存在，以安全地获取值
            "buyer": self.entry_buyer.get().strip() if hasattr(self, 'entry_buyer') else "",
            "seller": self.entry_seller.get().strip() if hasattr(self, 'entry_seller') else ""
        }
        self.destroy()

    def _cancel_event(self, event=None):
        self.result = None
        self.destroy()

    def get_input_data(self):
        self.parent.wait_window(self)
        return self.result


class AdvancedFilterDialog(ctk.CTkToplevel):
    """
    【全新】用于设置多种组合筛选规则的对话框。
    返回的数据格式（通过 get_filters() 获取）：
    {
        "product_name": str,     # 项目名称（可为空）
        "model_number": str,     # 规格型号（可为空）
        "buyer": str,            # 购买方（可为空）
        "seller": str,           # 销售方（可为空）
        "transaction_type": str, # 交易类型（"入库", "出库", "全部"），默认为"全部"
        "start_date": str,       # 开始日期（格式：YYYY-MM-DD，可为空）
        "end_date": str          # 结束日期（格式：YYYY-MM-DD，可为空）
    }
    
    注意：如果用户点击“重置规则”，则返回空字典 {}。
    """
    def __init__(self, parent, current_filters=None):
        super().__init__(parent)
        self.transient(parent)
        self.title("高级筛选")
        self.geometry("500x480")
        self.result = None
        if current_filters is None:
            current_filters = {}

        label_font = ("Microsoft YaHei UI", 14)
        entry_font = ("Microsoft YaHei UI", 14)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # --- 筛选条件控件 ---
        ctk.CTkLabel(main_frame, text="项目名称:", font=label_font).grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.entry_product_name = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_product_name.insert(0, current_filters.get("product_name", ""))
        self.entry_product_name.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="规格型号:", font=label_font).grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.entry_model_number = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_model_number.insert(0, current_filters.get("model_number", ""))
        self.entry_model_number.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="购买方:", font=label_font).grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.entry_buyer = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_buyer.insert(0, current_filters.get("buyer", ""))
        self.entry_buyer.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="销售方:", font=label_font).grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.entry_seller = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_seller.insert(0, current_filters.get("seller", ""))
        self.entry_seller.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="交易类型:", font=label_font).grid(row=4, column=0, padx=5, pady=8, sticky="w")
        self.combo_type = ctk.CTkComboBox(main_frame, values=["全部", "入库", "出库"], font=entry_font)
        self.combo_type.set(current_filters.get("transaction_type", "全部"))
        self.combo_type.grid(row=4, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="开始日期:", font=label_font).grid(row=5, column=0, padx=5, pady=8, sticky="w")
        self.entry_start_date = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD", font=entry_font)
        self.entry_start_date.insert(0, current_filters.get("start_date", ""))
        self.entry_start_date.grid(row=5, column=1, padx=5, pady=8, sticky="ew")

        ctk.CTkLabel(main_frame, text="结束日期:", font=label_font).grid(row=6, column=0, padx=5, pady=8, sticky="w")
        self.entry_end_date = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD", font=entry_font)
        self.entry_end_date.insert(0, current_filters.get("end_date", ""))
        self.entry_end_date.grid(row=6, column=1, padx=5, pady=8, sticky="ew")

        # --- 按钮 ---
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=25, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)
        
        btn_apply = ctk.CTkButton(button_frame, text="应用筛选", command=self.apply_filters)
        btn_apply.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        btn_reset = ctk.CTkButton(button_frame, text="重置规则", command=self.reset_filters, fg_color="gray")
        btn_reset.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.grab_set()
        self.lift()

    def _validate_date(self, date_str):
        if not date_str:
            return True
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def apply_filters(self):
        start_date = self.entry_start_date.get().strip()
        end_date = self.entry_end_date.get().strip()
        
        if not self._validate_date(start_date) or not self._validate_date(end_date):
            tkmb.showerror("格式错误", "日期格式应为 YYYY-MM-DD，或留空。", parent=self)
            return

        self.result = {
            "product_name": self.entry_product_name.get().strip(),
            "model_number": self.entry_model_number.get().strip(),
            "buyer": self.entry_buyer.get().strip(),
            "seller": self.entry_seller.get().strip(),
            "transaction_type": self.combo_type.get(),
            "start_date": start_date,
            "end_date": end_date,
        }
        # 移除值为空的键，使筛选字典更干净
        self.result = {k: v for k, v in self.result.items() if v and v != "全部"}
        self.destroy()

    def reset_filters(self):
        self.result = {} # 返回一个空字典作为重置信号
        self.destroy()

    def get_filters(self):
        self.wait_window(self)
        return self.result


