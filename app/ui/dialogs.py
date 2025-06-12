# app/ui/dialogs.py
import customtkinter as ctk
from datetime import datetime
import tkinter.messagebox as tkmb # For simple pop-up messages

class TransactionDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="交易记录", existing_data=None, transaction_type=""): # transaction_type: "入库" or "出库"
        super().__init__(parent)
        self.transient(parent) # 确保在父窗口之上，并随父窗口最小化
        self.title(title)
        self.parent = parent
        self.existing_data = existing_data
        self.result = None
        self.transaction_type = transaction_type # "入库" or "出库"

        # 定义通用字体 (您可以根据需要调整)
        label_font = ("Arial", 14) # 中文字体: "Microsoft YaHei" "SimSun"
        entry_font = ("Arial", 14)
        button_font = ("Arial", 14, "bold")
        textbox_font = ("Arial", 13) # 文本框内容字体可以稍小

        self.geometry("450x520") # 调整对话框大小

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # 项目名称
        self.label_product_name = ctk.CTkLabel(main_frame, text="项目名称:")
        self.label_product_name.grid(row=0, column=0, padx=5, pady=8, sticky="w")
        self.entry_product_name = ctk.CTkEntry(main_frame, width=250)
        self.entry_product_name.grid(row=0, column=1, padx=5, pady=8, sticky="ew")

        # 规格型号
        self.label_model_number = ctk.CTkLabel(main_frame, text="规格型号:")
        self.label_model_number.grid(row=1, column=0, padx=5, pady=8, sticky="w")
        self.entry_model_number = ctk.CTkEntry(main_frame, width=250)
        self.entry_model_number.grid(row=1, column=1, padx=5, pady=8, sticky="ew")

        # 单位
        self.label_unit = ctk.CTkLabel(main_frame, text="单位:")
        self.label_unit.grid(row=2, column=0, padx=5, pady=8, sticky="w")
        self.entry_unit = ctk.CTkEntry(main_frame, width=250)
        self.entry_unit.grid(row=2, column=1, padx=5, pady=8, sticky="ew")

        # 数量
        self.label_quantity = ctk.CTkLabel(main_frame, text="数量:")
        self.label_quantity.grid(row=3, column=0, padx=5, pady=8, sticky="w")
        self.entry_quantity = ctk.CTkEntry(main_frame, width=250)
        self.entry_quantity.grid(row=3, column=1, padx=5, pady=8, sticky="ew")
        
        # 单价
        self.label_unit_price = ctk.CTkLabel(main_frame, text="单价:")
        self.label_unit_price.grid(row=4, column=0, padx=5, pady=8, sticky="w")
        self.entry_unit_price = ctk.CTkEntry(main_frame, width=250)
        self.entry_unit_price.grid(row=4, column=1, padx=5, pady=8, sticky="ew")

        # 操作日期
        self.label_insertion_date = ctk.CTkLabel(main_frame, text="操作日期 (YYYY-MM-DD):")
        self.label_insertion_date.grid(row=5, column=0, padx=5, pady=8, sticky="w")
        self.entry_insertion_date = ctk.CTkEntry(main_frame, width=250)
        self.entry_insertion_date.grid(row=5, column=1, padx=5, pady=8, sticky="ew")
        self.entry_insertion_date.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # 备注
        self.label_notes = ctk.CTkLabel(main_frame, text="备注:")
        self.label_notes.grid(row=6, column=0, padx=5, pady=8, sticky="nw") # sticky nw for textbox
        self.entry_notes = ctk.CTkTextbox(main_frame, width=250, height=80)
        self.entry_notes.grid(row=6, column=1, padx=5, pady=8, sticky="ew")
        
        # 填充现有数据 (用于编辑)
        # 注意：编辑操作在库存管理中通常是复杂的。
        # 简单的做法是允许修改非关键信息（如备注），或撤销后重新输入。
        # 这里我们假设可以修改，但实际中要谨慎。
        if self.existing_data:
            self.entry_product_name.insert(0, self.existing_data.get('product_name', ''))
            self.entry_model_number.insert(0, self.existing_data.get('model_number', ''))
            self.entry_unit.insert(0, self.existing_data.get('unit', ''))
            # 对于编辑，我们显示的是该次交易的绝对数量
            self.entry_quantity.insert(0, str(abs(self.existing_data.get('quantity', ''))))
            self.entry_unit_price.insert(0, str(self.existing_data.get('unit_price', '')))
            self.entry_insertion_date.delete(0, 'end')
            self.entry_insertion_date.insert(0, self.existing_data.get('insertion_date', datetime.now().strftime('%Y-%m-%d')))
            self.entry_notes.insert("1.0", self.existing_data.get('notes', ''))
            
            # 如果是编辑，通常不允许修改影响库存的关键计算字段，除非特殊处理
            if "编辑" in title:
                 self.entry_product_name.configure(state="disabled")
                 self.entry_model_number.configure(state="disabled")
                 # self.entry_quantity.configure(state="disabled") # 数量修改要特别小心
                 # self.entry_unit.configure(state="disabled")
        
        # 按钮框架
        button_frame = ctk.CTkFrame(main_frame) # No explicit fg_color means transparent or theme-based
        button_frame.grid(row=7, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.columnconfigure((0,1), weight=1) # Make buttons expand

        self.button_confirm = ctk.CTkButton(button_frame, text="确认", command=self._confirm_input)
        self.button_confirm.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        self.button_cancel = ctk.CTkButton(button_frame, text="取消", command=self._cancel_event, fg_color="gray")
        self.button_cancel.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.grab_set()
        self.lift()
        self.entry_product_name.focus_set()

    def _validate_input(self):
        product_name = self.entry_product_name.get().strip()
        model_number = self.entry_model_number.get().strip()
        unit = self.entry_unit.get().strip() # 单位可以为空
        quantity_str = self.entry_quantity.get().strip()
        unit_price_str = self.entry_unit_price.get().strip()
        insertion_date = self.entry_insertion_date.get().strip()

        if not all([product_name, model_number, quantity_str, unit_price_str, insertion_date]):
            tkmb.showerror("输入错误", "项目名称, 规格型号, 数量, 单价, 操作日期不能为空!", parent=self)
            return False

        try:
            quantity = int(quantity_str)
            if quantity <= 0 : # 确保输入的数量是正数，符号由入库/出库决定
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
            tkmb.showerror("输入错误", "日期格式应为 YYYY-MM-DD!", parent=self)
            return False
        
        return True

    def _confirm_input(self):
        if not self._validate_input():
            return

        notes = self.entry_notes.get("1.0", "end-1c").strip()
        
        # 获取并转换数据
        quantity = int(self.entry_quantity.get().strip())
        
        # 如果是编辑，我们这里不改变原始quantity的符号，它代表那次操作的量
        # 如果是新建出库，则在inventory_manager中处理为负数
        # 对于dialog本身，它只关心用户输入的绝对量

        self.result = {
            "product_name": self.entry_product_name.get().strip(),
            "model_number": self.entry_model_number.get().strip(),
            "unit": self.entry_unit.get().strip(),
            "quantity": quantity, # 保持用户输入的（正）数量
            "unit_price": float(self.entry_unit_price.get().strip()),
            "insertion_date": self.entry_insertion_date.get().strip(),
            "notes": notes
        }
        if self.existing_data and 'id' in self.existing_data:
            self.result['id'] = self.existing_data['id']
            # 保留原始的quantity符号，因为编辑的是历史记录
            self.result['original_quantity_sign'] = 1 if self.existing_data.get('quantity', 0) > 0 else -1
            # 或者直接用原始的quantity，让调用者决定如何处理编辑
            self.result['db_quantity'] = self.existing_data.get('quantity')
            
        self.grab_release()
        self.destroy()

    def _cancel_event(self, event=None):
        self.result = None
        self.grab_release()
        self.destroy()

    def get_input_data(self):
        self.parent.wait_window(self)
        return self.result


class DateQueryDialog(ctk.CTkToplevel):
    def __init__(self, parent, title="按日期查询"):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None

        # 定义通用字体 (您可以根据需要调整)
        label_font = ("Arial", 14) # 中文字体: "Microsoft YaHei" "SimSun"
        entry_font = ("Arial", 14)
        button_font = ("Arial", 14, "bold")
        textbox_font = ("Arial", 13) # 文本框内容字体可以稍小

        self.geometry("450x280") # 调整大小

        main_frame = ctk.CTkFrame(self)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        self.label_year = ctk.CTkLabel(main_frame, text="年份 (YYYY):")
        self.label_year.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.entry_year = ctk.CTkEntry(main_frame, width=200)
        self.entry_year.grid(row=0, column=1, padx=5, pady=10, sticky="ew")

        self.label_month = ctk.CTkLabel(main_frame, text="月份 (MM):")
        self.label_month.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.entry_month = ctk.CTkEntry(main_frame, width=200)
        self.entry_month.grid(row=1, column=1, padx=5, pady=10, sticky="ew")

        self.label_day = ctk.CTkLabel(main_frame, text="日期 (DD):")
        self.label_day.grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.entry_day = ctk.CTkEntry(main_frame, width=200)
        self.entry_day.grid(row=2, column=1, padx=5, pady=10, sticky="ew")

        button_frame = ctk.CTkFrame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20, sticky="ew")
        button_frame.columnconfigure((0,1), weight=1)

        self.button_confirm = ctk.CTkButton(button_frame, text="查询", command=self._confirm_input)
        self.button_confirm.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        self.button_cancel = ctk.CTkButton(button_frame, text="取消", command=self._cancel_event, fg_color="gray")
        self.button_cancel.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        self.grab_set()
        self.lift()
        self.entry_year.focus_set()

    def _confirm_input(self):
        year_str = self.entry_year.get().strip()
        month_str = self.entry_month.get().strip()
        day_str = self.entry_day.get().strip()
        
        query_params = {}
        if year_str:
            try:
                if not (1000 <= int(year_str) <= 9999):
                     tkmb.showerror("输入错误", "请输入有效的4位年份!", parent=self)
                     return
                query_params['year'] = year_str
            except ValueError:
                tkmb.showerror("输入错误", "年份必须是有效的数字!", parent=self)
                return
        if month_str:
            try:
                m = int(month_str)
                if not (1 <= m <= 12):
                    tkmb.showerror("输入错误", "月份必须在1-12之间!", parent=self)
                    return
                query_params['month'] = month_str # zfill in data_manager
            except ValueError:
                tkmb.showerror("输入错误", "月份必须是有效的数字!", parent=self)
                return
        if day_str:
            try:
                d = int(day_str)
                if not (1 <= d <= 31): # 简单校验
                    tkmb.showerror("输入错误", "日期必须在1-31之间!", parent=self)
                    return
                query_params['day'] = day_str # zfill in data_manager
            except ValueError:
                tkmb.showerror("输入错误", "日期必须是有效的数字!", parent=self)
                return

        if not query_params:
             tkmb.showinfo("提示", "请输入至少一个查询条件 (年/月/日)。", parent=self)
             return

        self.result = query_params
        self.grab_release()
        self.destroy()

    def _cancel_event(self, event=None):
        self.result = None
        self.grab_release()
        self.destroy()

    def get_query_dates(self):
        self.parent.wait_window(self)
        return self.result