# main.py
import customtkinter as ctk
from app.ui.main_window import MainWindow
from app.core.inventory import InventoryManager
from app.core.data_manager import initialize_database # Ensure DB is ready

if __name__ == "__main__":
    initialize_database() # 确保数据库和表已创建
    
    inventory_manager = InventoryManager()
    
    app = MainWindow(inventory_manager)
    app.mainloop()