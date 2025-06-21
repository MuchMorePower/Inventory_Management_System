# app/ui/styles.py
import customtkinter as ctk

class DialogStyleBase:
    """
    所有对话框样式的基类。
    它负责根据 base_size 和系统缩放因子计算通用的样式。
    """
    def __init__(self, window, base_size: int):
        self.base_size = base_size
        self.scale_factor = ctk.ScalingTracker.get_window_scaling(window)
        self.font_style = "Microsoft YaHei UI"
        
        # --- 派生通用样式 ---
        font_size = int((self.base_size - 2) * self.scale_factor)
        self.label_font = (self.font_style, font_size)
        self.entry_font = (self.font_style, font_size)
        self.button_font = (self.font_style, font_size, "bold")
        self.pad_m = int(5 * self.scale_factor)
        self.pad_l = int(10 * self.scale_factor)

class SettingsDialogStyle(DialogStyleBase):
    """设置对话框的专属样式类。"""
    def __init__(self, window, base_size: int):
        super().__init__(window, base_size)

class TransactionDialogStyle(DialogStyleBase):
    """交易对话框的专属样式类。"""
    def __init__(self, window, base_size: int):
        super().__init__(window, base_size)
        # 为备注框定义一个更小的字体
        notes_font_size = int((self.base_size - 4) * self.scale_factor)
        self.notes_font = (self.font_style, notes_font_size)

class AdvancedFilterDialogStyle(DialogStyleBase):
    """高级筛选对话框的专属样式类。"""
    def __init__(self, window, base_size: int):
        super().__init__(window, base_size)

class UIStyleManager:
    """主窗口的样式管理器，负责主窗口所有复杂的UI样式和布局。"""
    def __init__(self, window, base_size: int):
        self.base_size = base_size
        self.font_style = "Microsoft YaHei UI"
        self.scale_factor = ctk.ScalingTracker.get_window_scaling(window)
        self._derive_all_styles()

    def update_base_size(self, new_base_size: int):
        """当用户更改缩放基准时，重新计算所有样式"""
        self.base_size = new_base_size
        self._derive_all_styles()

    def _derive_all_styles(self):
        """根据 base_size 和 scale_factor 计算所有UI元素的尺寸、字体和间距。"""
        # 字体
        self.label_font = (self.font_style, self.base_size)
        self.button_font = (self.font_style, self.base_size, "bold")
        self.treeview_font = (self.font_style, int(self.base_size * self.scale_factor))
        self.heading_font = (self.font_style, int((self.base_size - 1) * self.scale_factor), 'bold')

        # 尺寸和间距
        self.treeview_rowheight = int(self.base_size * 2.2 * self.scale_factor)
        self.action_button_height = int(self.base_size * 1.8)
        self.action_button_width = int(self.base_size * 6.5)
        self.pad_m = int(5 * self.scale_factor)
        self.pad_l = int(10 * self.scale_factor)
        
        self.button_kwargs = {"font": self.button_font, "width": self.action_button_width, "height": self.action_button_height}

    def apply_main_window_styles(self, window):
        """将计算好的样式应用到主窗口的各个部分"""
        window.main_frame.pack_configure(padx=self.pad_l, pady=self.pad_l)
        window.top_frame.pack_configure(pady=(0, self.pad_l))
        window.bottom_frame.pack_configure(pady=(self.pad_l, 0))
        
        window.action_button_frame.grid_configure(padx=(0, self.pad_l), pady=self.pad_m)
        window.advanced_filter_frame.grid_configure(padx=self.pad_m, pady=self.pad_m)
        
        all_buttons = [
            window.btn_inbound, window.btn_outbound, window.btn_import_excel, window.btn_export_excel, 
            window.btn_export_selected, window.btn_show_summary, window.btn_show_all_transactions,
            window.btn_advanced_filter, window.btn_clear_filter
        ]
        for btn in all_buttons:
            btn.configure(**self.button_kwargs)
            btn.pack_configure(padx=self.pad_m)

        window.tree_style.configure("Treeview.Heading", font=self.heading_font)
        window.tree_style.configure("Treeview", rowheight=self.treeview_rowheight, font=self.treeview_font)
        
        window.status_label.configure(font=self.label_font)
        window.selected_total_label.configure(font=self.label_font)