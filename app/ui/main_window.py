# app/ui/main_window.py
import customtkinter as ctk
from tkinter import ttk # For Treeview
import tkinter.messagebox as tkmb
from tkinter import filedialog
from .dialogs import TransactionDialog, SettingsDialog, AdvancedFilterDialog
from app.core.inventory import InventoryManager
from app.core import config_manager
from datetime import datetime
import tkinter as tk
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except AttributeError:
    ctypes.windll.user32.SetProcessDPIAware()

class MainWindow(ctk.CTk):

    
    def __init__(self, inventory_manager: InventoryManager):
        super().__init__()
        self.inventory_manager = inventory_manager
        self.active_filters = {}
        self.company_name = config_manager.load_company_name()
        # --- 加载配置 ---
        self.company_name = config_manager.load_company_name()
        self.base_size = config_manager.load_ui_scale()
        self.ttk_scale_adjustment = config_manager.load_ttk_scale_adjustment()
        # --- 【核心】在初始化时获取一次系统缩放因子 ---
        self.scale_factor = ctk.ScalingTracker.get_window_scaling(self)
        ctk.set_widget_scaling(self.scale_factor)


        self.title(f"商品管理系统 - {self.company_name}" if self.company_name else "商品管理系统")

        self.state('zoomed')
        self.minsize(1024, 600)

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # --- 【第1步：构建UI骨架】 ---
        self._create_widgets()
        # --- 【第2步：应用样式和尺寸】 ---
        self._apply_styles()
        # --- 【第3步：加载初始数据】 ---
        self.current_view_mode = "transactions"
        self.setup_transactions_view()
        self.load_all_transactions_view()

        

    def _create_widgets(self):
        """创建所有的UI控件骨架，但不设置尺寸和样式"""
        # 菜单栏
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="系统设置...", command=self.open_settings_dialog)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.quit)
        
        # 布局框架
        self.main_frame = ctk.CTkFrame(self)
        self.top_frame = ctk.CTkFrame(self.main_frame)
        self.middle_frame = ctk.CTkFrame(self.main_frame)
        self.bottom_frame = ctk.CTkFrame(self.main_frame)
        
        # 顶部控件
        self.action_button_frame = ctk.CTkFrame(self.top_frame)
        self.advanced_filter_frame = ctk.CTkFrame(self.top_frame)
        
        self.btn_inbound = ctk.CTkButton(self.action_button_frame, text="商品入库", command=self.open_inbound_dialog)
        self.btn_outbound = ctk.CTkButton(self.action_button_frame, text="商品出库", command=self.open_outbound_dialog)
        self.btn_import_excel = ctk.CTkButton(self.action_button_frame, text="导入Excel", fg_color="green", hover_color="#006400", command=self.import_from_excel_dialog)
        self.btn_export_excel = ctk.CTkButton(self.action_button_frame, text="导出Excel", fg_color="#005792", hover_color="#003961", command=self.export_to_excel_dialog)
        self.btn_export_selected = ctk.CTkButton(self.action_button_frame, text="导出选中", fg_color="#C05A00", hover_color="#8C4000", command=self.export_selected_dialog)
        self.btn_show_summary = ctk.CTkButton(self.action_button_frame, text="库存汇总", command=self.show_product_summary)
        self.btn_show_all_transactions = ctk.CTkButton(self.action_button_frame, text="全部记录", command=self.load_all_transactions_view)
        
        self.btn_advanced_filter = ctk.CTkButton(self.advanced_filter_frame, text="高级筛选...", command=self.open_advanced_filter_dialog)
        self.btn_clear_filter = ctk.CTkButton(self.advanced_filter_frame, text="清除筛选", command=self.clear_all_filters, fg_color="gray")
        
        # Treeview
        self.tree_style = ttk.Style()
        # <<< 关键修正：在创建 Treeview 时，必须添加 show="headings" 选项 >>>
        self.tree = ttk.Treeview(self.middle_frame, show="headings") 
        self.scrollbar_y = ctk.CTkScrollbar(self.middle_frame, command=self.tree.yview)
        self.scrollbar_x = ctk.CTkScrollbar(self.middle_frame, command=self.tree.xview, orientation="horizontal")
        self.tree.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # 底部状态栏
        self.status_label = ctk.CTkLabel(self.bottom_frame, text="状态: 就绪", anchor="w")
        self.selected_total_label = ctk.CTkLabel(self.bottom_frame, text="选中总金额: 0.00", anchor="e")

        # 绑定事件
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        self.context_menu = ctk.CTkFrame(self, border_width=1)

    def _apply_styles(self):
        """【核心】根据 base_size 和两个缩放因子计算并应用所有UI尺寸和样式"""
        font_style = "Microsoft YaHei UI"
        # self.ttk_scale_adjustment = 1
        
        # 1. CTkinter控件的样式，只受 base_size 影响
        base_style_size = self.base_size
        label_font = (font_style, base_style_size)
        button_font = (font_style, base_style_size, "bold")
        action_button_height = int(base_style_size * 2.5)
        action_button_width = int(base_style_size * 6.5)

        # 2. ttk 部件的最终缩放因子 = 系统DPI因子 * 用户微调系数
        final_ttk_scale = self.scale_factor * self.ttk_scale_adjustment

        # 3. ttk 部件的尺寸和字体使用 final_ttk_scale
        menu_font = (font_style, int(base_style_size * 0.8))
        treeview_font_size = int(base_style_size * 0.9 * final_ttk_scale)
        treeview_font = (font_style, treeview_font_size)
        heading_font_size = int((base_style_size - 1) * 0.9 * final_ttk_scale)
        heading_font = (font_style, heading_font_size, 'bold')
        treeview_rowheight = int(base_style_size * 2.5 * final_ttk_scale) 
        
        # 4. 间距也最好进行缩放
        pad_m = int(5 * self.scale_factor)
        pad_l = int(10 * self.scale_factor)
        
        # 应用布局
        self.main_frame.pack(fill="both", expand=True, padx=pad_l, pady=pad_l)
        self.top_frame.pack(fill="x", pady=(0, pad_l))
        self.top_frame.grid_columnconfigure(1, weight=1)
        self.middle_frame.pack(fill="both", expand=True)
        self.bottom_frame.pack(fill="x", pady=(pad_l, 0))
        
        self.action_button_frame.grid(row=0, column=0, padx=(0, pad_l), pady=pad_m, sticky="w")
        self.advanced_filter_frame.grid(row=0, column=1, padx=pad_m, pady=pad_m, sticky="e")

        # 应用菜单样式
        self.file_menu.configure(font=menu_font)
        
        # 应用按钮样式
        btn_kwargs = {"font": button_font, "width": action_button_width, "height": action_button_height}
        all_buttons = [
            self.btn_inbound, self.btn_outbound, self.btn_import_excel, self.btn_export_excel, 
            self.btn_export_selected, self.btn_show_summary, self.btn_show_all_transactions,
            self.btn_advanced_filter, self.btn_clear_filter
        ]
        for btn in all_buttons:
            btn.configure(**btn_kwargs)
            btn.pack(side="left", padx=pad_m)

        # 应用Treeview样式
        self.tree_style.theme_use("default")
        self.tree_style.configure("Treeview.Heading", font=heading_font)
        self.tree_style.configure("Treeview", rowheight=treeview_rowheight, font=treeview_font)
        self.tree.configure(style="Treeview")
        
        # <<< 关键修正：正确的滚动条和Treeview布局顺序 >>>
        self.scrollbar_y.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.tree.pack(side="left", fill="both", expand=True) 
        
        # 应用底部状态栏样式
        self.status_label.configure(font=label_font)
        self.selected_total_label.configure(font=label_font)
        self.status_label.pack(side="left", padx=pad_l, pady=pad_m)
        self.selected_total_label.pack(side="right", padx=pad_l, pady=pad_m)

    def setup_transactions_view(self):
        self.current_view_mode = "transactions"
        self.tree['columns'] = ("ID", "日期", "项目名称", "规格型号", "购买方", "销售方", 
                                "单位", "类型", "数量", "单价", "总金额", )
        
        
        # 获取系统缩放因子，用于计算列宽
        scale_factor = ctk.ScalingTracker.get_window_scaling(self) * 0.9

        # 定义基础列宽，然后乘以缩放因子得到最终宽度
       

        self.tree.column("#0", width=0, stretch=ctk.NO)
        self.tree.column("ID", anchor=ctk.W, width=int(30 * scale_factor), minwidth=int(25 * scale_factor))
        self.tree.column("日期", anchor=ctk.W, width=int(85 * scale_factor), minwidth=int(75 * scale_factor))
        self.tree.column("项目名称", anchor=ctk.W, width=int(160 * scale_factor), minwidth=int(120 * scale_factor))
        self.tree.column("规格型号", anchor=ctk.W, width=int(140 * scale_factor), minwidth=int(100 * scale_factor))
        self.tree.column("购买方", anchor=ctk.W, width=int(150 * scale_factor), minwidth=int(120 * scale_factor))
        self.tree.column("销售方", anchor=ctk.W, width=int(150 * scale_factor), minwidth=int(120 * scale_factor))
        self.tree.column("单位", anchor=ctk.CENTER, width=int(30 * scale_factor), minwidth=int(26 * scale_factor))
        self.tree.column("类型", anchor=ctk.CENTER, width=int(50 * scale_factor), minwidth=int(40 * scale_factor))
        self.tree.column("数量", anchor=ctk.E, width=int(60 * scale_factor), minwidth=int(50 * scale_factor))
        self.tree.column("单价", anchor=ctk.E, width=int(90 * scale_factor), minwidth=int(70 * scale_factor))
        self.tree.column("总金额", anchor=ctk.E, width=int(100 * scale_factor), minwidth=int(80 * scale_factor))
        

        for col in self.tree['columns']:
            self.tree.heading(col, text=col, anchor=ctk.W if col not in ['单位', '类型', '数量', '单价', '总金额'] else ctk.CENTER if col in ['单位', '类型'] else ctk.E)

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
        

    def populate_treeview(self, data_rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        if self.current_view_mode == "transactions":
            for row in data_rows:
                row_dict = dict(row)
                trans_type = "入库" if row_dict['quantity'] > 0 else "出库"
                status = "已撤销" if row_dict['is_undone'] else "有效"
                
                values = (
                    row_dict['id'], row_dict['insertion_date'], row_dict['product_name'], 
                    row_dict['model_number'], row_dict.get('buyer', ''), row_dict.get('seller', ''),
                    row_dict['unit'], trans_type, abs(row_dict['quantity']),
                    f"{row_dict['unit_price']:.2f}", f"{row_dict['total_amount']:.2f}",
                    
                )
                self.tree.insert(parent='', index='end', iid=row_dict['id'], text="", values=values)
                if row_dict['is_undone']:
                    self.tree.item(row_dict['id'], tags=('undone',))
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

    def open_settings_dialog(self):
        """打开统一的设置对话框"""
        dialog = SettingsDialog(self, current_name=self.company_name, current_scale=self.base_size, current_ttk_adjustment=self.ttk_scale_adjustment)
        settings = dialog.get_settings()

        if settings is not None:
            # 保存公司名称
            new_name = settings['company_name']
            if new_name != self.company_name:
                self.company_name = new_name
                config_manager.save_company_name(new_name)
                self.title(f"商品管理系统 - {self.company_name}" if self.company_name else "商品管理系统")

            # 保存并应用UI缩放
            new_scale = settings['ui_scale']
            if new_scale != self.base_size:
                self.base_size = new_scale
                config_manager.save_ui_scale(new_scale)
                self._apply_styles()
            
            new_ttk_scale_adjustment = settings['ttk_scale_adjustment']
            if new_ttk_scale_adjustment != self.ttk_scale_adjustment:
                self.ttk_scale_adjustment = new_ttk_scale_adjustment
                config_manager.save_ttk_scale_adjustment(new_ttk_scale_adjustment)
                self._apply_styles()

            tkmb.showinfo("成功", "设置已保存。", parent=self)

    def open_inbound_dialog(self):
        dialog = TransactionDialog(self, title="商品入库", transaction_type="入库", company_name=self.company_name)
        data = dialog.get_input_data()
        if data:
            success, message = self.inventory_manager.record_inbound(
                data['product_name'], data['model_number'], data['unit'],
                data['quantity'], data['unit_price'], data['insertion_date'], 
                data['notes'], data['buyer'], data['seller']
            )
            if success:
                tkmb.showinfo("成功", message, parent=self)
                self.refresh_current_view()
            else:
                tkmb.showerror("失败", message, parent=self)

    def open_outbound_dialog(self):
        dialog = TransactionDialog(self, title="商品出库", transaction_type="出库", company_name=self.company_name)
        data = dialog.get_input_data()
        if data:
            success, message = self.inventory_manager.record_outbound(
                data['product_name'], data['model_number'], data['unit'],
                data['quantity'], data['unit_price'], data['insertion_date'], 
                data['notes'], data['buyer'], data['seller']
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

    def open_advanced_filter_dialog(self):
        dialog = AdvancedFilterDialog(self, current_filters=self.active_filters)
        filters = dialog.get_filters()

        if filters is not None:
            self.active_filters = filters
            if not filters:
                self.clear_all_filters()
            else:
                self.apply_advanced_filters()

    def apply_advanced_filters(self):
        if not self.active_filters:
            self.load_all_transactions_view()
            return
            
        transactions = self.inventory_manager.get_records_with_advanced_filter(self.active_filters)
        self.populate_treeview(transactions)
        self.status_label.configure(text=f"状态: 已应用 {len(self.active_filters)} 条高级筛选规则")

    def clear_all_filters(self):
        self.active_filters = {}
        self.load_all_transactions_view()

    def load_all_transactions_view(self):
        # 如果有筛选规则，应该清除它们再加载全部
        if self.active_filters:
            self.clear_all_filters()
        else:
            if self.current_view_mode != "transactions":
                self.setup_transactions_view()
            transactions = self.inventory_manager.get_all_records(include_undone=True)
            self.populate_treeview(transactions)
            self.status_label.configure(text="状态: 显示所有交易记录")

    def refresh_current_view(self):
        if self.current_view_mode == "transactions":
            # 刷新时，重新应用当前激活的筛选规则
            self.apply_advanced_filters()
        elif self.current_view_mode == "summary":
            self.show_product_summary()

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
