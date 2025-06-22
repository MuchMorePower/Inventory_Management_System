# app/ui/dialogs.py
import customtkinter as ctk
import tkcalendar as tkc
from datetime import datetime
from app.core import config_manager
import tkinter.messagebox as tkmb # For simple pop-up messages

class SettingsDialog(ctk.CTkToplevel):
    """【已更新】用于统一设置公司名称、UI缩放基准和表格微调系数的对话框"""
    def __init__(self, parent, current_name: str, current_scale: int, current_ttk_adjustment: float):
        super().__init__(parent)
        self.transient(parent)
        self.title("系统设置")
        self.scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.9
        ctk.set_widget_scaling(self.scale_factor)

        self.geometry(f"{int(350 * self.scale_factor)}x{int(500 * self.scale_factor)}")

        pad_s = 5 * self.scale_factor
        pad_m = 10 * self.scale_factor * 0.95
        pad_l = 15 * self.scale_factor * 0.95
        
        self.result = None

        label_font = ("Microsoft YaHei UI", int(current_scale * 1.5))

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=pad_l, pady=pad_l, fill="both", expand=True)

        # --- 公司名称设置 ---
        ctk.CTkLabel(main_frame, text="本公司名称:", font=label_font).pack(padx=pad_m, pady=(pad_m, pad_s), anchor="w")
        self.entry_company_name = ctk.CTkEntry(main_frame, placeholder_text="请输入本公司名称...", font=label_font)
        self.entry_company_name.insert(0, current_name)
        self.entry_company_name.pack(padx=pad_m, pady=pad_s, fill="x")

        # --- 界面缩放基准设置 ---
        ctk.CTkLabel(main_frame, text="界面缩放基准:", font=label_font).pack(padx=pad_m, pady=(pad_l, pad_s), anchor="w")
        self.scale_label_info = ctk.CTkLabel(main_frame, text=f"当前大小: {current_scale}", font=label_font)
        self.scale_label_info.pack()
        self.scale_slider = ctk.CTkSlider(main_frame, from_=1, to=30, number_of_steps=30, command=lambda v: self.scale_label_info.configure(text=f"当前大小: {int(v)}"))
        self.scale_slider.set(current_scale)
        self.scale_slider.pack(pady=pad_m, padx=pad_l, fill="x")

        # --- 【新增】表格微调系数设置 ---
        ctk.CTkLabel(main_frame, text="表格(ttk)微调系数:", font=label_font).pack(padx=pad_m, pady=(pad_l, pad_s), anchor="w")
        self.ttk_adj_label = ctk.CTkLabel(main_frame, text=f"当前: {current_ttk_adjustment:.2f}x (建议 0.8-1.2)", font=label_font)
        self.ttk_adj_label.pack()
        self.ttk_adj_slider = ctk.CTkSlider(main_frame, from_=0.7, to=1.5, number_of_steps=80, command=lambda v: self.ttk_adj_label.configure(text=f"当前: {v:.2f}x"))
        self.ttk_adj_slider.set(current_ttk_adjustment)
        self.ttk_adj_slider.pack(pady=pad_m, padx=pad_l, fill="x")

        # --- 按钮 ---
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(pady=25, side="bottom")
        ctk.CTkButton(button_frame, text="保存并应用", command=self.apply_settings, font=(label_font[0], label_font[1], "bold")).pack(side="left", padx=pad_m)
        ctk.CTkButton(button_frame, text="取消", command=self.cancel, fg_color="gray", font=(label_font[0], label_font[1], "bold")).pack(side="left", padx=pad_m)

        self.grab_set()
        self.lift()

    def apply_settings(self):
        """用户点击保存，打包返回所有设置"""
        self.result = {
            "company_name": self.entry_company_name.get().strip(),
            "ui_scale": int(self.scale_slider.get()),
            "ttk_scale_adjustment": self.ttk_adj_slider.get() # 新增返回值
        }
        self.destroy()

    def cancel(self):
        """用户点击取消，不返回任何数据"""
        self.result = None
        self.destroy()

    def get_settings(self):
        """主窗口调用此方法来获取设置结果"""
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

        scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.85
        ctk.set_widget_scaling(scale_factor)

        self.base_size = config_manager.load_ui_scale()
        dialog_font_size = int((self.base_size - 1) * scale_factor)

        # --- 修改：稍微加高窗口以容纳新控件 ---
        self.geometry(f"{int(500 * scale_factor)}x{int(500 * scale_factor)}")


        # --- 修改：优化字体以获得更好的中文显示效果 ---
        label_font = ("Microsoft YaHei UI", dialog_font_size)
        entry_font = ("Microsoft YaHei UI", dialog_font_size)

        pad_s = int(2 * scale_factor)
        pad_m = int(4 * scale_factor)
        pad_l = int(5 * scale_factor)
        pad_xl = int(10 * scale_factor)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=pad_xl, pady=pad_l, fill="both", expand=True)

        # --- 控件定义 (原有控件保持不变) ---
        ctk.CTkLabel(main_frame, text="项目名称:", font=label_font).grid(row=0, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_product_name = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_product_name.grid(row=0, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="规格型号:", font=label_font).grid(row=1, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_model_number = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_model_number.grid(row=1, column=1, padx=pad_m, pady=pad_l, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="单位:", font=label_font).grid(row=2, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_unit = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_unit.grid(row=2, column=1, padx=pad_m, pady=pad_l, sticky="ew")
        self.entry_unit.insert(0, "个")  # 默认单位为"个"

        ctk.CTkLabel(main_frame, text="数量:", font=label_font).grid(row=3, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_quantity = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_quantity.grid(row=3, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="单价:", font=label_font).grid(row=4, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_unit_price = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_unit_price.grid(row=4, column=1, padx=pad_m, pady=pad_l, sticky="ew")
        # self.entry_unit_price.insert(0, "0.00")  # 默认单价为0.00

        ctk.CTkLabel(main_frame, text="操作日期 (YYYY-MM-DD):", font=label_font).grid(row=5, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_insertion_date = ctk.CTkEntry(main_frame, font=entry_font)
        self.entry_insertion_date.grid(row=5, column=1, padx=pad_m, pady=pad_l, sticky="ew")
        self.entry_insertion_date.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # --- 关键修改：同时创建购买方和销售方输入框，并设置默认值 ---
        ctk.CTkLabel(main_frame, text="购买方:").grid(row=6, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_buyer = ctk.CTkEntry(main_frame, width=200 * scale_factor)
        self.entry_buyer.grid(row=6, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="销售方:").grid(row=7, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_seller = ctk.CTkEntry(main_frame, width=200 * scale_factor)
        self.entry_seller.grid(row=7, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        if transaction_type == "入库":
            # 入库时，本公司是购买方，所以默认填入公司名
            self.entry_buyer.insert(0, company_name)
            self.entry_seller.configure(placeholder_text="请输入销售方名称...")
        elif transaction_type == "出库":
            # 出库时，本公司是销售方，所以默认填入公司名
            self.entry_seller.insert(0, company_name)
            self.entry_buyer.configure(placeholder_text="请输入购买方名称...")

        # 调整后续控件的行号
        ctk.CTkLabel(main_frame, text="备注:").grid(row=8, column=0, padx=pad_m, pady=pad_l, sticky="nw")
        self.entry_notes = ctk.CTkTextbox(main_frame, height=50 * scale_factor)
        self.entry_notes.grid(row=8, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        

        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=9, column=0, columnspan=2, pady=pad_xl, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)

        self.button_confirm = ctk.CTkButton(button_frame, text="确认", command=self._confirm_input)
        self.button_confirm.grid(row=0, column=0, padx=pad_xl, pady=pad_m, sticky="ew")
        self.button_cancel = ctk.CTkButton(button_frame, text="取消", command=self._cancel_event, fg_color="gray")
        self.button_cancel.grid(row=0, column=1, padx=pad_xl, pady=pad_m, sticky="ew")

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
    


# class AdvancedFilterDialog(ctk.CTkToplevel):
#     """
#     【全新】用于设置多种组合筛选规则的对话框。
#     返回的数据格式（通过 get_filters() 获取）：
#     {
#         "product_name": str,     # 项目名称（可为空）
#         "model_number": str,     # 规格型号（可为空）
#         "buyer": str,            # 购买方（可为空）
#         "seller": str,           # 销售方（可为空）
#         "transaction_type": str, # 交易类型（"入库", "出库", "全部"），默认为"全部"
#         "start_date": str,       # 开始日期（格式：YYYY-MM-DD，可为空）
#         "end_date": str          # 结束日期（格式：YYYY-MM-DD，可为空）
#     }
    
#     注意：如果用户点击“重置规则”，则返回空字典 {}。
#     """
#     def __init__(self, parent, current_filters=None):
#         super().__init__(parent)
#         self.transient(parent)
#         self.title("高级筛选")
#         self.geometry("500x480")
#         self.result = None
#         if current_filters is None:
#             current_filters = {}

#         label_font = ("Microsoft YaHei UI", 14)
#         entry_font = ("Microsoft YaHei UI", 14)

#         main_frame = ctk.CTkFrame(self)
#         main_frame.pack(padx=20, pady=20, fill="both", expand=True)

#         # --- 筛选条件控件 ---
#         ctk.CTkLabel(main_frame, text="项目名称:", font=label_font).grid(row=0, column=0, padx=5, pady=8, sticky="w")
#         self.entry_product_name = ctk.CTkEntry(main_frame, font=entry_font)
#         self.entry_product_name.insert(0, current_filters.get("product_name", ""))
#         self.entry_product_name.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

#         ctk.CTkLabel(main_frame, text="规格型号:", font=label_font).grid(row=1, column=0, padx=5, pady=8, sticky="w")
#         self.entry_model_number = ctk.CTkEntry(main_frame, font=entry_font)
#         self.entry_model_number.insert(0, current_filters.get("model_number", ""))
#         self.entry_model_number.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

#         ctk.CTkLabel(main_frame, text="购买方:", font=label_font).grid(row=2, column=0, padx=5, pady=8, sticky="w")
#         self.entry_buyer = ctk.CTkEntry(main_frame, font=entry_font)
#         self.entry_buyer.insert(0, current_filters.get("buyer", ""))
#         self.entry_buyer.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

#         ctk.CTkLabel(main_frame, text="销售方:", font=label_font).grid(row=3, column=0, padx=5, pady=8, sticky="w")
#         self.entry_seller = ctk.CTkEntry(main_frame, font=entry_font)
#         self.entry_seller.insert(0, current_filters.get("seller", ""))
#         self.entry_seller.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
#         ctk.CTkLabel(main_frame, text="交易类型:", font=label_font).grid(row=4, column=0, padx=5, pady=8, sticky="w")
#         self.combo_type = ctk.CTkComboBox(main_frame, values=["全部", "入库", "出库"], font=entry_font)
#         self.combo_type.set(current_filters.get("transaction_type", "全部"))
#         self.combo_type.grid(row=4, column=1, padx=5, pady=8, sticky="ew")

#         ctk.CTkLabel(main_frame, text="开始日期:", font=label_font).grid(row=5, column=0, padx=5, pady=8, sticky="w")
#         self.entry_start_date = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD", font=entry_font)
#         self.entry_start_date.insert(0, current_filters.get("start_date", ""))
#         self.entry_start_date.grid(row=5, column=1, padx=5, pady=8, sticky="ew")

#         ctk.CTkLabel(main_frame, text="结束日期:", font=label_font).grid(row=6, column=0, padx=5, pady=8, sticky="w")
#         self.entry_end_date = ctk.CTkEntry(main_frame, placeholder_text="YYYY-MM-DD", font=entry_font)
#         self.entry_end_date.insert(0, current_filters.get("end_date", ""))
#         self.entry_end_date.grid(row=6, column=1, padx=5, pady=8, sticky="ew")

#         # --- 按钮 ---
#         button_frame = ctk.CTkFrame(main_frame)
#         button_frame.grid(row=7, column=0, columnspan=2, pady=25, sticky="ew")
#         button_frame.columnconfigure((0, 1), weight=1)
        
#         btn_apply = ctk.CTkButton(button_frame, text="应用筛选", command=self.apply_filters)
#         btn_apply.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

#         btn_reset = ctk.CTkButton(button_frame, text="重置规则", command=self.reset_filters, fg_color="gray")
#         btn_reset.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
#         self.grab_set()
#         self.lift()

#     def _validate_date(self, date_str):
#         if not date_str:
#             return True
#         try:
#             datetime.strptime(date_str, '%Y-%m-%d')
#             return True
#         except ValueError:
#             return False

#     def apply_filters(self):
#         start_date = self.entry_start_date.get().strip()
#         end_date = self.entry_end_date.get().strip()
        
#         if not self._validate_date(start_date) or not self._validate_date(end_date):
#             tkmb.showerror("格式错误", "日期格式应为 YYYY-MM-DD，或留空。", parent=self)
#             return

#         self.result = {
#             "product_name": self.entry_product_name.get().strip(),
#             "model_number": self.entry_model_number.get().strip(),
#             "buyer": self.entry_buyer.get().strip(),
#             "seller": self.entry_seller.get().strip(),
#             "transaction_type": self.combo_type.get(),
#             "start_date": start_date,
#             "end_date": end_date,
#         }
#         # 移除值为空的键，使筛选字典更干净
#         self.result = {k: v for k, v in self.result.items() if v and v != "全部"}
#         self.destroy()

#     def reset_filters(self):
#         self.result = {} # 返回一个空字典作为重置信号
#         self.destroy()

#     def get_filters(self):
#         self.wait_window(self)
#         return self.result

class AdvancedFilterDialog(ctk.CTkToplevel):
    """
    改进版高级筛选对话框，集成日期选择器组件
    """
    def __init__(self, parent, current_filters=None):
        super().__init__(parent)
        self.transient(parent)
        self.title("高级筛选")
        scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.85
        ctk.set_widget_scaling(scale_factor)
        self.base_size = config_manager.load_ui_scale()
        dialog_font_size = int((self.base_size - 1) * scale_factor)

        self.geometry(f"{int(400 * scale_factor)}x{450 * scale_factor}")  # 增加高度以容纳日期选择器
        self.result = None
        if current_filters is None:
            current_filters = {}

        label_font = ("Microsoft YaHei UI", dialog_font_size)
        entry_font = ("Microsoft YaHei UI", dialog_font_size)

        pad_s = int(2 * scale_factor)
        pad_m = int(4 * scale_factor)
        pad_l = int(6 * scale_factor)
        pad_xl = int(10 * scale_factor)

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=15, pady=15, fill="both", expand=True)

        # --- 筛选条件控件 ---
        ctk.CTkLabel(main_frame, text="项目名称:").grid(row=0, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_product_name = ctk.CTkEntry(main_frame)
        self.entry_product_name.insert(0, current_filters.get("product_name", ""))
        self.entry_product_name.grid(row=0, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="规格型号:").grid(row=1, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_model_number = ctk.CTkEntry(main_frame)
        self.entry_model_number.insert(0, current_filters.get("model_number", ""))
        self.entry_model_number.grid(row=1, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="购买方:").grid(row=2, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_buyer = ctk.CTkEntry(main_frame)
        self.entry_buyer.insert(0, current_filters.get("buyer", ""))
        self.entry_buyer.grid(row=2, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="销售方:").grid(row=3, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.entry_seller = ctk.CTkEntry(main_frame)
        self.entry_seller.insert(0, current_filters.get("seller", ""))
        self.entry_seller.grid(row=3, column=1, padx=pad_m, pady=pad_l, sticky="ew")
        
        ctk.CTkLabel(main_frame, text="交易类型:").grid(row=4, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.combo_type = ctk.CTkComboBox(main_frame, values=["全部", "入库", "出库"])
        self.combo_type.set(current_filters.get("transaction_type", "全部"))
        self.combo_type.grid(row=4, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        # --- 日期选择器 ---
        ctk.CTkLabel(main_frame, text="开始日期:").grid(row=5, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.date_start = tkc.DateEntry(
            main_frame,
            date_pattern='yyyy-mm-dd',
            font=entry_font,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        if current_filters.get("start_date"):
            try:
                self.date_start.set_date(datetime.strptime(current_filters["start_date"], '%Y-%m-%d'))
            except ValueError:
                pass
        self.date_start.grid(row=5, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        ctk.CTkLabel(main_frame, text="结束日期:").grid(row=6, column=0, padx=pad_m, pady=pad_l, sticky="w")
        self.date_end = tkc.DateEntry(
            main_frame,
            date_pattern='yyyy-mm-dd',
            font=entry_font,
            background='darkblue',
            foreground='white',
            borderwidth=2
        )
        if current_filters.get("end_date"):
            try:
                self.date_end.set_date(datetime.strptime(current_filters["end_date"], '%Y-%m-%d'))
            except ValueError:
                pass
        self.date_end.grid(row=6, column=1, padx=pad_m, pady=pad_l, sticky="ew")

        # --- 按钮 ---
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=pad_xl, sticky="ew")
        button_frame.columnconfigure((0, 1), weight=1)
        
        btn_apply = ctk.CTkButton(button_frame, text="应用筛选", command=self.apply_filters)
        btn_apply.grid(row=0, column=1, padx=pad_xl, pady=pad_m, sticky="ew")

        btn_reset = ctk.CTkButton(button_frame, text="重置规则", command=self.reset_filters, fg_color="gray")
        btn_reset.grid(row=0, column=0, padx=pad_xl, pady=pad_m, sticky="ew")
        
        self.grab_set()
        self.lift()

    def apply_filters(self):
        """收集筛选条件并验证日期范围"""
        start_date = self.date_start.get_date().strftime('%Y-%m-%d')
        end_date = self.date_end.get_date().strftime('%Y-%m-%d')

        # 验证日期范围合理性
        if start_date and end_date:
            if datetime.strptime(start_date, '%Y-%m-%d') > datetime.strptime(end_date, '%Y-%m-%d'):
                tkmb.showerror("日期错误", "结束日期不能早于开始日期", parent=self)
                return

        self.result = {
            "product_name": self.entry_product_name.get().strip(),
            "model_number": self.entry_model_number.get().strip(),
            "buyer": self.entry_buyer.get().strip(),
            "seller": self.entry_seller.get().strip(),
            "transaction_type": self.combo_type.get(),
            "start_date": start_date if start_date else None,
            "end_date": end_date if end_date else None,
        }
        # 清理空值
        self.result = {k: v for k, v in self.result.items() if v and v != "全部"}
        self.destroy()

    def reset_filters(self):
        """重置所有筛选条件"""
        self.date_start.set_date(datetime.now())
        self.date_end.set_date(datetime.now())
        self.result = {}
        self.destroy()

    def get_filters(self):
        self.wait_window(self)
        return self.result
