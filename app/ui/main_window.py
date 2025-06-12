# app/ui/main_window.py
import customtkinter as ctk
from tkinter import ttk # For Treeview
import tkinter.messagebox as tkmb
from tkinter import filedialog
from .dialogs import TransactionDialog, DateQueryDialog
from app.core.inventory import InventoryManager
from datetime import datetime

class MainWindow(ctk.CTk):

    
    def __init__(self, inventory_manager: InventoryManager):
        super().__init__()
        self.inventory_manager = inventory_manager

        # --- 【关键修改 1: 设立“一键调节”的总控制开关】 ---
        # 只需修改下面这个变量，就能统一调整所有UI元素的大小
        # 推荐值范围: 13 (紧凑), 15 (默认), 18 (较大)
        base_size = 8

        # --- 自动DPI缩放 (这部分保持不变，它负责适配不同显示器的系统缩放) ---
        ctk.set_widget_scaling(ctk.ScalingTracker.get_window_scaling(self))
        ctk.set_window_scaling(ctk.ScalingTracker.get_window_scaling(self))
        scale_factor = ctk.ScalingTracker.get_window_scaling(self)

        self.title("商品管理系统 (响应式布局版)")
        self.state('zoomed')
        self.minsize(800, 500) # 将最小尺寸调大一点以适应更大的基础尺寸

        # --- 【关键修改 2: 所有尺寸都基于 base_size 派生】 ---
        font_style = "Microsoft YaHei UI"
        
        # 1. CustomTkinter 控件的字体 (使用基础尺寸)
        label_font = (font_style, base_size)
        entry_font = (font_style, base_size)
        button_font = (font_style, base_size, "bold")
        
        # 2. ttk.Treeview 的字体 (基础尺寸 * 系统缩放因子)
        treeview_font_size = int(base_size * scale_factor)
        treeview_font = (font_style, treeview_font_size)
        heading_font = (font_style, int((base_size - 1) * scale_factor), 'bold') # 标题字可以略小

        # 3. ttk.Treeview 的行高 (基于字体大小计算，再乘以系统缩放因子)
        # 经验法则：行高通常是字体大小的 1.8 到 2 倍
        treeview_rowheight = int(base_size * 1.6 * scale_factor)

        # 4. 固定宽度按钮的宽度 (也基于基础尺寸计算)
        search_button_width = int(base_size * 2.0)
        date_button_width = int(base_size * 2.0)

        # 4. 【新增：控制顶部操作按钮的尺寸】
        #    高度是字体大小的倍数，宽度也一样，这样可以保持比例
        action_button_height = int(base_size * 2.5)
        action_button_width = int(base_size * 4.2) # 给一个统一的宽度，确保最长的文字也能放下

        # --- 后续代码使用上面计算出的变量 ---
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.top_frame.pack(fill="x", pady=(0, 10))
        self.middle_frame = ctk.CTkFrame(self.main_frame)
        self.middle_frame.pack(fill="both", expand=True)
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame.pack(fill="x", pady=(10, 0))

       # --- 【关键修改：在创建按钮时传入 width 和 height】 ---
        self.top_frame.grid_columnconfigure(1, weight=1)
        action_button_frame = ctk.CTkFrame(self.top_frame)
        action_button_frame.grid(row=0, column=0, padx=(0, 10), pady=5, sticky="w")

        # 所有按钮都使用统一的 button_font
        # 为所有按钮应用统一、可控的尺寸
        self.btn_inbound = ctk.CTkButton(action_button_frame, text="商品入库", command=self.open_inbound_dialog, font=button_font, 
                                        width=action_button_width, height=action_button_height)
        self.btn_inbound.pack(side="left", padx=5)

        self.btn_outbound = ctk.CTkButton(action_button_frame, text="商品出库", command=self.open_outbound_dialog, font=button_font, 
                                        width=action_button_width, height=action_button_height)
        self.btn_outbound.pack(side="left", padx=5)

        self.btn_import_excel = ctk.CTkButton(action_button_frame, text="导入Excel", command=self.import_from_excel_dialog, font=button_font, 
                                            fg_color="green", hover_color="#006400", 
                                            width=action_button_width, height=action_button_height)
        self.btn_import_excel.pack(side="left", padx=5)

        self.btn_export_excel = ctk.CTkButton(action_button_frame, text="导出Excel", command=self.export_to_excel_dialog, font=button_font, 
                                            fg_color="#005792", hover_color="#003961", 
                                            width=action_button_width, height=action_button_height)
        self.btn_export_excel.pack(side="left", padx=5)

        self.btn_export_selected = ctk.CTkButton(action_button_frame, text="导出选中", command=self.export_selected_dialog, font=button_font, 
                                                fg_color="#C05A00", hover_color="#8C4000", 
                                                width=action_button_width, height=action_button_height)
        self.btn_export_selected.pack(side="left", padx=5)

        self.btn_show_summary = ctk.CTkButton(action_button_frame, text="库存汇总", command=self.show_product_summary, font=button_font, 
                                            width=action_button_width, height=action_button_height)
        self.btn_show_summary.pack(side="left", padx=5)
        
        self.btn_show_all_transactions = ctk.CTkButton(action_button_frame, text="全部记录", command=self.load_all_transactions_view, font=button_font, 
                                                        width=action_button_width, height=action_button_height)
        self.btn_show_all_transactions.pack(side="left", padx=5)

        

        # Part 2: 右侧的筛选器区域
        filter_frame = ctk.CTkFrame(self.top_frame)
        filter_frame.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        filter_frame.grid_columnconfigure((1, 3), weight=1)

        # --- 【本次核心修复：为右侧所有控件应用统一高度】 ---
        self.label_filter_name = ctk.CTkLabel(filter_frame, text="项目名称:", font=label_font)
        self.label_filter_name.grid(row=0, column=0, padx=(5,0), sticky="w")
        
        self.entry_filter_name = ctk.CTkEntry(filter_frame, placeholder_text="筛选项目名称...", font=entry_font, 
                                            height=action_button_height) # <-- 应用高度
        self.entry_filter_name.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.label_filter_model = ctk.CTkLabel(filter_frame, text="规格型号:", font=label_font)
        self.label_filter_model.grid(row=0, column=2, padx=(10,0), sticky="w")
        
        self.entry_filter_model = ctk.CTkEntry(filter_frame, placeholder_text="筛选规格型号...", font=entry_font, 
                                            height=action_button_height) # <-- 应用高度
        self.entry_filter_model.grid(row=0, column=3, padx=5, sticky="ew")
        
        self.btn_filter_search = ctk.CTkButton(filter_frame, text="筛选", width=search_button_width, command=self.filter_records, font=button_font, 
                                            height=action_button_height) # <-- 应用高度
        self.btn_filter_search.grid(row=0, column=4, padx=5)
        
        self.btn_date_search = ctk.CTkButton(filter_frame, text="按日期查", width=date_button_width, command=self.open_date_query_dialog, font=button_font, 
                                            height=action_button_height) # <-- 应用高度
        self.btn_date_search.grid(row=0, column=5, padx=5)

        self.tree_style = ttk.Style()
        self.tree_style.theme_use("default")
        
        # Treeview 样式配置使用上面计算好的变量
        heading_bg = "#565B5E"
        even_row_bg = "#303437"
        text_color = "#DCE4EE"
        if ctk.get_appearance_mode().lower() == "light":
            heading_bg = "#E5E5E5"
            even_row_bg = "#F0F0F0"
            text_color = "#1A1A1A"
        
        self.tree_style.configure("Treeview.Heading", font=heading_font, background=heading_bg, foreground=text_color, relief="flat")
        self.tree_style.map("Treeview.Heading", background=[('active', '#4A4D50')])
        self.tree_style.configure("Treeview", background=even_row_bg, fieldbackground=even_row_bg, foreground=text_color, rowheight=treeview_rowheight, font=treeview_font)
        self.tree_style.map('Treeview', background=[('selected', '#2C74B3')])

        self.tree = ttk.Treeview(self.middle_frame, style="Treeview")
        self.tree.pack(side="left", fill="both", expand=True)

        self.scrollbar_y = ctk.CTkScrollbar(self.middle_frame, command=self.tree.yview)
        self.scrollbar_y.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set)
        self.scrollbar_x = ctk.CTkScrollbar(self.middle_frame, command=self.tree.xview, orientation="horizontal")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.tree.configure(xscrollcommand=self.scrollbar_x.set)

        self.tree.bind("<Double-1>", self.on_double_click_item)
        self.tree.bind("<Button-3>", self.show_context_menu)
        
        self.context_menu = ctk.CTkFrame(self, border_width=1)
        
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="状态: 就绪", anchor="w", font=label_font)
        self.status_label.pack(side="left", padx=10, pady=5)
        self.selected_total_label = ctk.CTkLabel(self.bottom_frame, text="选中总金额: 0.00", anchor="e", font=label_font)
        self.selected_total_label.pack(side="right", padx=10, pady=5)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.current_view_mode = "transactions"
        self.setup_transactions_view()
        self.load_all_transactions_view()


    def setup_transactions_view(self):
        self.current_view_mode = "transactions"
        self.tree['columns'] = ("ID", "日期", "项目名称", "规格型号", 
                                "单位", "类型", "数量", "单价", 
                                "总金额", "状态", "备注", "原始时间")
        
        # --- 【本次核心修复】 ---
        # 获取系统缩放因子，用于计算列宽
        scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.9

        # 定义基础列宽，然后乘以缩放因子得到最终宽度
        # --- 【关键修改: 全面减小基础列宽】 ---
        self.tree.column("#0", width=0, stretch=ctk.NO)
        self.tree.column("ID", anchor=ctk.W, width=int(50 * scale_factor), minwidth=int(35 * scale_factor))
        self.tree.column("日期", anchor=ctk.W, width=int(110 * scale_factor), minwidth=int(90 * scale_factor))
        self.tree.column("项目名称", anchor=ctk.W, width=int(160 * scale_factor), minwidth=int(120 * scale_factor))
        self.tree.column("规格型号", anchor=ctk.W, width=int(140 * scale_factor), minwidth=int(100 * scale_factor))
        self.tree.column("单位", anchor=ctk.CENTER, width=int(60 * scale_factor), minwidth=int(40 * scale_factor))
        self.tree.column("类型", anchor=ctk.CENTER, width=int(70 * scale_factor), minwidth=int(50 * scale_factor))
        self.tree.column("数量", anchor=ctk.E, width=int(80 * scale_factor), minwidth=int(60 * scale_factor))
        self.tree.column("单价", anchor=ctk.E, width=int(90 * scale_factor), minwidth=int(70 * scale_factor))
        self.tree.column("总金额", anchor=ctk.E, width=int(100 * scale_factor), minwidth=int(80 * scale_factor))
        self.tree.column("状态", anchor=ctk.CENTER, width=int(70 * scale_factor), minwidth=int(50 * scale_factor))
        self.tree.column("备注", anchor=ctk.W, width=int(160 * scale_factor), minwidth=int(120 * scale_factor))
        self.tree.column("原始时间", anchor=ctk.W, width=int(150 * scale_factor), minwidth=int(130 * scale_factor))

        self.tree.heading("#0", text="", anchor=ctk.W)
        self.tree.heading("ID", text="ID", anchor=ctk.W)
        self.tree.heading("日期", text="操作日期", anchor=ctk.W)
        self.tree.heading("项目名称", text="项目名称", anchor=ctk.W)
        self.tree.heading("规格型号", text="规格型号", anchor=ctk.W)
        self.tree.heading("单位", text="单位", anchor=ctk.CENTER)
        self.tree.heading("类型", text="类型", anchor=ctk.CENTER)
        self.tree.heading("数量", text="数量", anchor=ctk.E)
        self.tree.heading("单价", text="单价", anchor=ctk.E)
        self.tree.heading("总金额", text="总金额", anchor=ctk.E)
        self.tree.heading("状态", text="状态", anchor=ctk.CENTER)
        self.tree.heading("备注", text="备注", anchor=ctk.W)
        self.tree.heading("原始时间", text="记录时间", anchor=ctk.W)
        self.clear_filters()


    def setup_summary_view(self):
        self.current_view_mode = "summary"
        self.tree['columns'] = ("项目名称", "规格型号", "单位", "当前库存")
        
        scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.9

        self.tree.column("#0", width=0, stretch=ctk.NO)
        self.tree.column("#0", width=0, stretch=ctk.NO)
        self.tree.column("项目名称", anchor=ctk.W, width=int(220 * scale_factor))
        self.tree.column("规格型号", anchor=ctk.W, width=int(180 * scale_factor))
        self.tree.column("单位", anchor=ctk.CENTER, width=int(80 * scale_factor))
        self.tree.column("当前库存", anchor=ctk.E, width=int(120 * scale_factor))

        self.tree.heading("#0", text="", anchor=ctk.W)
        self.tree.heading("项目名称", text="项目名称", anchor=ctk.W)
        self.tree.heading("规格型号", text="规格型号", anchor=ctk.W)
        self.tree.heading("单位", text="单位", anchor=ctk.CENTER)
        self.tree.heading("当前库存", text="当前库存", anchor=ctk.E)
        self.clear_filters()


    def populate_treeview(self, data_rows):
        # Clear existing data
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Populate with new data
        if self.current_view_mode == "transactions":
            for row in data_rows:
                # Determine type and status for display
                trans_type = "入库" if row['quantity'] > 0 else "出库"
                status = "已撤销" if row['is_undone'] else "有效"
                
                # Format numbers for display
                quantity_display = abs(row['quantity']) # Display absolute quantity
                unit_price_display = f"{row['unit_price']:.2f}"
                total_amount_display = f"{row['total_amount']:.2f}"
                
                # Using row['id'] as the IID for the item
                self.tree.insert(parent='', index='end', iid=row['id'], text="", 
                                 values=(row['id'], row['insertion_date'], row['product_name'], 
                                         row['model_number'], row['unit'], trans_type,
                                         quantity_display, unit_price_display, total_amount_display,
                                         status, row['notes'], row['transaction_time']))
                if row['is_undone']: # Apply a tag for styling undone rows
                    self.tree.item(row['id'], tags=('undone',))

            # Configure tag for undone rows (e.g., strikethrough or different color)
            # Note: ttk.Treeview strikethrough is not straightforward. Graying out text is easier.
            self.tree.tag_configure('undone', foreground='gray')


        elif self.current_view_mode == "summary":
            iid_counter = 0
            for row in data_rows:
                self.tree.insert(parent='', index='end', iid=iid_counter, text="",
                                 values=(row['product_name'], row['model_number'],
                                         row['unit'], row['current_stock']))
                iid_counter += 1
        self.on_tree_select(None) # Update totals display

    def load_all_transactions_view(self):
        if self.current_view_mode != "transactions":
            self.setup_transactions_view()
        transactions = self.inventory_manager.get_all_records(include_undone=True) # Show all including undone
        self.populate_treeview(transactions)
        self.status_label.configure(text="状态: 显示所有交易记录")
        self.clear_filters()

    def show_product_summary(self):
        self.setup_summary_view()
        summary_data = self.inventory_manager.get_product_summary_view()
        self.populate_treeview(summary_data)
        self.status_label.configure(text="状态: 显示库存汇总")

    def open_inbound_dialog(self):
        dialog = TransactionDialog(self, title="商品入库", transaction_type="入库")
        data = dialog.get_input_data()
        if data:
            success, message = self.inventory_manager.record_inbound(
                data['product_name'], data['model_number'], data['unit'],
                data['quantity'], data['unit_price'], data['insertion_date'], data['notes']
            )
            if success:
                tkmb.showinfo("成功", message, parent=self)
                self.refresh_current_view()
            else:
                tkmb.showerror("失败", message, parent=self)

    def open_outbound_dialog(self):
        dialog = TransactionDialog(self, title="商品出库", transaction_type="出库")
        data = dialog.get_input_data()
        if data:
            success, message = self.inventory_manager.record_outbound(
                data['product_name'], data['model_number'], data['unit'],
                data['quantity'], data['unit_price'], data['insertion_date'], data['notes']
            )
            if success:
                tkmb.showinfo("成功", message, parent=self)
                self.refresh_current_view()
            else:
                tkmb.showerror("失败", message, parent=self)
                
    def open_edit_dialog(self, item_id):
        # Editing past transactions can be complex.
        # A common approach is to undo and re-enter.
        # For this example, let's allow editing notes or date of a non-undone transaction.
        # True editing of quantity/price of past records might require recalculating summaries or be disallowed.
        
        # For now, editing is disabled via double click, context menu provides other actions.
        # If editing were enabled:
        # transaction = self.inventory_manager.get_transaction_by_id(item_id) # Need method in inventory.py
        # if transaction:
        #     dialog = TransactionDialog(self, title=f"编辑记录 ID: {item_id}", existing_data=dict(transaction))
        #     data = dialog.get_input_data()
        #     if data:
        #         # Call an update method in inventory_manager
        #         # success, message = self.inventory_manager.update_transaction_details(item_id, data)
        #         # ... handle response ...
        #         print(f"TODO: Implement editing for {item_id} with data: {data}")
        #         tkmb.showinfo("提示", "编辑功能待详细实现，通常涉及撤销原记录并创建新记录。", parent=self)
        # else:
        #    tkmb.showerror("错误", "无法加载交易数据进行编辑。", parent=self)
        tkmb.showinfo("提示", "编辑功能：建议先撤销，再重新入库/出库。", parent=self)


    def on_double_click_item(self, event):
        if self.current_view_mode != "transactions": return
        
        selected_item_iid = self.tree.focus() # Get IID of focused item
        if not selected_item_iid: return

        # item_values = self.tree.item(selected_item_iid, 'values')
        # item_id = item_values[0] # Assuming ID is the first value
        item_id = selected_item_iid # We used DB ID as IID
        
        self.open_edit_dialog(item_id)


    def show_context_menu(self, event):
        """显示右键菜单"""
        # 清理旧的菜单项 (如果之前创建过)
        for widget in self.context_menu.winfo_children():
            widget.destroy()

        selected_iid = self.tree.identify_row(event.y) # Get item under mouse
        if not selected_iid:
            return

        self.tree.selection_set(selected_iid) # Select the item
        self.tree.focus(selected_iid)

        # 获取选中的交易记录信息
        if self.current_view_mode != "transactions":
            self.context_menu.place_forget() # Hide if not in transactions view
            return
            
        item_id = selected_iid # IID is the transaction ID
        transaction = self.inventory_manager.get_transaction_details(item_id) # Get full data

        if not transaction:
            return

        # --- 创建菜单项 ---
        # 使用 CTkButton 作为菜单项
        # 为避免每次都创建，可以将菜单的创建移到 __init__，然后根据上下文显示/隐藏
        # 但动态创建也行，对于少量选项

        if not transaction['is_undone']:
            undo_button = ctk.CTkButton(self.context_menu, text="撤销此记录",
                                        command=lambda id=item_id: self.undo_selected_transaction(id),
                                        width=120, height=28, )
            undo_button.pack(pady=2, padx=5, fill="x")
        else:
            redo_button = ctk.CTkButton(self.context_menu, text="恢复此记录",
                                        command=lambda id=item_id: self.redo_selected_transaction(id),
                                        width=120, height=28)
            redo_button.pack(pady=2, padx=5, fill="x")

        # edit_button = ctk.CTkButton(self.context_menu, text="编辑此记录",
        #                              command=lambda id=item_id: self.open_edit_dialog(id),
        #                              width=120, height=28)
        # edit_button.pack(pady=2, padx=5, fill="x")
        
        delete_button = ctk.CTkButton(self.context_menu, text="永久删除",
                                      command=lambda id=item_id: self.delete_selected_transaction(id),
                                      fg_color="red", hover_color="#C00000", width=120, height=28)
        delete_button.pack(pady=(2,5), padx=5, fill="x")


        # 定位并显示菜单
        # self.context_menu.place(x=event.x_root - self.winfo_x() , y=event.y_root - self.winfo_y())
        self.context_menu.place(x=event.x_root - self.winfo_rootx() + 5, 
                                y=event.y_root - self.winfo_rooty() + 5)
        # 绑定事件以在点击外部时隐藏菜单
        self.bind_all("<Button-1>", self.hide_context_menu_on_click_outside, add="+")


    def hide_context_menu_on_click_outside(self, event):
        # 检查点击是否在 context_menu 内部
        if not (self.context_menu.winfo_containing(event.x_root, event.y_root) == self.context_menu or \
           any(widget == self.context_menu.winfo_containing(event.x_root, event.y_root) for widget in self.context_menu.winfo_children())):
            self.context_menu.place_forget()
            self.unbind_all("<Button-1>") # 解绑，避免影响其他点击事件


    def undo_selected_transaction(self, transaction_id):
        self.context_menu.place_forget()
        if tkmb.askyesno("确认操作", f"确定要撤销记录 ID: {transaction_id} 吗？\n此操作会影响库存统计。", parent=self):
            success, message = self.inventory_manager.undo_transaction(transaction_id)
            tkmb.showinfo("结果", message, parent=self)
            if success:
                self.refresh_current_view()

    def redo_selected_transaction(self, transaction_id):
        self.context_menu.place_forget()
        if tkmb.askyesno("确认操作", f"确定要恢复记录 ID: {transaction_id} 吗？", parent=self):
            success, message = self.inventory_manager.redo_transaction(transaction_id) # Assuming you add this
            tkmb.showinfo("结果", message, parent=self)
            if success:
                self.refresh_current_view()
                
    def delete_selected_transaction(self, transaction_id):
        self.context_menu.place_forget()
        if tkmb.askyesno("警告：永久删除", f"确定要永久删除记录 ID: {transaction_id} 吗？\n此操作不可恢复！", parent=self):
            success, message = self.inventory_manager.delete_transaction(transaction_id)
            tkmb.showinfo("结果", message, parent=self)
            if success:
                self.refresh_current_view()


    def refresh_current_view(self):
        if self.current_view_mode == "transactions":
            # Re-apply filters if they exist or load all
            name_filter = self.entry_filter_name.get().strip()
            model_filter = self.entry_filter_model.get().strip()
            if name_filter or model_filter:
                self.filter_records()
            else:
                self.load_all_transactions_view()
        elif self.current_view_mode == "summary":
            self.show_product_summary()
        self.on_tree_select(None) # Recalculate totals

    def filter_records(self):
        if self.current_view_mode != "transactions":
            self.setup_transactions_view() # Switch to transaction view if filtering
            
        name_filter = self.entry_filter_name.get().strip()
        model_filter = self.entry_filter_model.get().strip()

        if not name_filter and not model_filter:
            self.load_all_transactions_view() # Show all if filters are empty
            return

        transactions = self.inventory_manager.get_records_by_filter(name_filter, model_filter)
        self.populate_treeview(transactions)
        self.status_label.configure(text=f"状态: 筛选结果 (名称: '{name_filter}', 型号: '{model_filter}')")

    def clear_filters(self):
        self.entry_filter_name.delete(0, 'end')
        self.entry_filter_model.delete(0, 'end')

    def open_date_query_dialog(self):
        dialog = DateQueryDialog(self)
        dates = dialog.get_query_dates()
        if dates:
            if self.current_view_mode != "transactions":
                self.setup_transactions_view()
            
            transactions = self.inventory_manager.get_records_by_date(
                year=dates.get('year'), month=dates.get('month'), day=dates.get('day')
            )
            self.populate_treeview(transactions)
            
            date_str_parts = []
            if dates.get('year'): date_str_parts.append(f"年:{dates['year']}")
            if dates.get('month'): date_str_parts.append(f"月:{dates['month']}")
            if dates.get('day'): date_str_parts.append(f"日:{dates['day']}")
            self.status_label.configure(text=f"状态: 按日期查询 ({', '.join(date_str_parts)})")
            self.clear_filters()

    def on_tree_select(self, event):
        """当Treeview中的选择变化时调用"""
        if self.current_view_mode != "transactions":
            self.selected_total_label.configure(text="选中总金额: N/A (非交易视图)")
            return

        selected_iids = self.tree.selection() # Get IIDs of selected items
        if not selected_iids:
            self.selected_total_label.configure(text="选中总金额: 0.00")
            return

        # Our IIDs are the database transaction IDs
        transaction_ids_to_sum = [iid for iid in selected_iids] 
        
        totals = self.inventory_manager.calculate_selected_totals(transaction_ids_to_sum)
        self.selected_total_label.configure(text=f"选中总金额: {totals['total_amount']:.2f} (共 {totals['count']} 条有效记录)")

    def import_from_excel_dialog(self):
        """打开文件对话框以选择要导入的Excel文件。"""
        file_path = filedialog.askopenfilename(
            title="选择要导入的Excel文件",
            filetypes=(("Excel Files", "*.xlsx"), ("All files", "*.*")),
            parent=self
        )
        if not file_path:
            return # 用户取消了选择

        # 执行导入，并给出状态提示
        self.status_label.configure(text="状态: 正在从Excel导入...")
        self.update_idletasks() # 强制UI立即更新状态标签
        
        success, message = self.inventory_manager.import_from_excel(file_path)
        
        if success:
            tkmb.showinfo("成功", message, parent=self)
            self.refresh_current_view() # 导入成功后刷新视图以显示新数据
        else:
            tkmb.showerror("导入失败", message, parent=self)
            self.status_label.configure(text="状态: 导入失败或部分失败")

    def export_to_excel_dialog(self):
        """打开文件对话框以选择保存Excel文件的位置。"""
        # 建议一个默认文件名，包含当前日期和时间
        default_filename = f"库存记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        file_path = filedialog.asksaveasfilename(
            title="选择保存位置",
            defaultextension=".xlsx",
            filetypes=(("Excel Files", "*.xlsx"), ("All files", "*.*")),
            initialfile=default_filename,
            parent=self
        )
        if not file_path:
            return # 用户取消了选择

        # 执行导出，并给出状态提示
        self.status_label.configure(text="状态: 正在导出到Excel...")
        self.update_idletasks() # 强制UI立即更新状态标签
        
        success, message = self.inventory_manager.export_to_excel(file_path)
        
        if success:
            tkmb.showinfo("成功", message, parent=self)
            self.status_label.configure(text="状态: 导出成功")
        else:
            tkmb.showerror("导出失败", message, parent=self)
            self.status_label.configure(text="状态: 导出失败")

    def export_selected_dialog(self):
        """打开文件对话框以导出选中的交易记录。"""
        # 1. 获取Treeview中所有被选中的行的IID
        selected_ids = self.tree.selection()

        if not selected_ids:
            tkmb.showinfo("提示", "请先在表格中选择至少一条要导出的记录。", parent=self)
            return

        # 2. 打开保存对话框
        default_filename = f"选中记录_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        file_path = filedialog.asksaveasfilename(
            title="选择保存位置",
            defaultextension=".xlsx",
            filetypes=(("Excel Files", "*.xlsx"), ("All files", "*.*")),
            initialfile=default_filename,
            parent=self
        )
        if not file_path:
            return

        # 3. 调用新的业务逻辑方法
        self.status_label.configure(text=f"状态: 正在导出 {len(selected_ids)} 条选中记录...")
        self.update_idletasks()
        
        # 注意：这里我们调用的是新的 export_selected_records 方法
        success, message = self.inventory_manager.export_selected_records(list(selected_ids), file_path)
        
        if success:
            tkmb.showinfo("成功", message, parent=self)
            self.status_label.configure(text="状态: 导出成功")
        else:
            tkmb.showerror("导出失败", message, parent=self)
            self.status_label.configure(text="状态: 导出失败")
