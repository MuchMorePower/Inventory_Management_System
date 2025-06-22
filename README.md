## 商品库存管理系统 - 完整项目文档

### 引言

本文档旨在为“商品库存管理系统”提供一份全面、详细的技术说明。内容涵盖了项目的整体架构、数据库设计、各核心模块的功能职责以及主要函数的实现细节，旨在为后续的维护、扩展或二次开发提供清晰的指导和参考。

---

### 1. 项目结构

项目采用了分层设计的思想，将数据持久化、业务逻辑和用户界面清晰地分离，以提高代码的可维护性、可读性和可扩展性。

```
inventory-management/
├── database/
│   └── inventory.db       # SQLite 数据库文件，由程序自动生成和管理
├── config/
│   └── settings.json      # 配置文件，用于保存公司名称和UI设置
├── app/
│   ├── core/
│   │   ├── __init__.py      # 包初始化文件
│   │   ├── config_manager.py# 【配置层】负责读写settings.json配置文件
│   │   ├── data_manager.py  # 【数据访问层】负责所有数据库的直接读写
│   │   └── inventory.py     # 【业务逻辑层】负责处理所有业务规则
│   └── ui/
│       ├── __init__.py      # 包初始化文件
│       ├── styles.py        # 【样式层】新增：用于管理UI样式和动态缩放
│       ├── dialogs.py       # 【表现层-组件】定义了各种弹出的对话框
│       └── main_window.py   # 【表现层-主视图】主窗口的UI界面与事件处理
└── main.py                  # 【程序主入口】启动和组织整个应用

```

---

### 2. 数据库表结构 (`transactions` 表)

本系统使用 SQLite 数据库，所有交易数据都存储在名为 `transactions` 的单一表中。该表的设计旨在以原子化的方式记录每一次库存变动。

| 字段名 (Column)    | 数据类型 (Type) | 约束 (Constraint)           | 描述 (Description)                                        |
| ------------------ | --------------- | --------------------------- | --------------------------------------------------------- |
| `id`               | `INTEGER`       | `PRIMARY KEY AUTOINCREMENT` | 唯一标识符，自动递增，作为每条记录的主键。                |
| `transaction_time` | `DATETIME`      | `DEFAULT CURRENT_TIMESTAMP` | 记录插入数据库的精确时间，由数据库自动生成。              |
| `insertion_date`   | `DATE`          | `NOT NULL`                  | **业务操作日期** (YYYY-MM-DD)，由用户指定或在导入时生成。 |
| `product_name`     | `TEXT`          | `NOT NULL`                  | 商品的名称。                                              |
| `model_number`     | `TEXT`          | `NOT NULL`                  | 商品的规格型号。                                          |
| `unit`             | `TEXT`          |                             | 商品的计量单位（如：个、台、箱）。                        |
| `quantity`         | `INTEGER`       | `NOT NULL`                  | 交易数量。**正数代表入库，负数代表出库**。                |
| `unit_price`       | `REAL`          | `NOT NULL`                  | 本次交易的商品单价。                                      |
| `total_amount`     | `REAL`          | `NOT NULL`                  | 本次交易的总金额 (`abs(quantity) * unit_price`)。         |
| `is_undone`        | `BOOLEAN`       | `DEFAULT 0`                 | 标记记录是否已撤销 (0: 有效, 1: 已撤销)。                |
| `notes`            | `TEXT`          | `DEFAULT ''`                | 备注信息，可选。                                          |
| `buyer`            | `TEXT`          | `DEFAULT ''`                | 购买方（出库时录）。                          |
| `seller`           | `TEXT`          | `DEFAULT ''`                | 销售方（入库时录）。                          |

#### 关键更新说明：
1. **新增字段**：
   - `buyer`：记录商品出库时的购买方信息
   - `seller`：记录商品入库时的销售方信息
   
2. **字段约束**：
   - 所有新增字段均设置默认值为空字符串 `DEFAULT ''`
   - 确保与旧版本数据库的兼容性（自动迁移时不会报错）

3. **初始化逻辑**：
   ```python
   # 数据库初始化时自动创建表结构
   initialize_database()

### 3. `main.py` (主程序入口)

作为整个应用程序的启动器，它的职责单一而重要。

* **作用**:
    * **实例化核心服务**: 创建 `InventoryManager` 的实例，这是整个应用业务逻辑的中央处理器。
    * **构建用户界面**: 创建主窗口 `MainWindow` 的实例。
    * **依赖注入**: 将 `InventoryManager` 的实例作为参数传递给 `MainWindow`。这种模式被称为“依赖注入”，它有效地解耦了UI层和逻辑层。UI层不需要关心业务逻辑是如何实现的，只需要知道调用哪个对象的方法即可，这极大地增强了代码的灵活性。
    * **启动事件循环**: 调用 `mainloop()` 方法，使程序进入等待和响应用户操作的状态。

---

### 4. `app/core/data_manager.py` (数据管理模块)

该模块是应用的“数据访问层”，是唯一与数据库文件直接对话的部分。它将原始的SQL查询语句封装成易于调用的Python函数，对上层屏蔽了数据库操作的复杂细节。

* `get_db_connection()`: 建立并返回一个到 `inventory.db` 的连接。通过 `sqlite3.Row` 工厂，使得查询结果可以像字典一样通过列名访问，提高了代码的可读性。
* `initialize_database()`: 执行 `CREATE TABLE IF NOT EXISTS` SQL语句，确保程序在任何环境下（即使是第一次运行）都能找到所需的表结构。
* `add_transaction(...)`: 封装 `INSERT` 语句，负责向数据库中安全地插入一条新的交易记录。
* `get_all_transactions(...)`: 封装 `SELECT * FROM ...` 语句，提供一个统一的接口来获取全部或仅有效的交易数据。
* `get_transaction_by_id(...)`: 封装带 `WHERE id = ?` 条件的 `SELECT` 查询，用于精确获取单条记录。
* `get_transactions_by_ids(ids)`: **(新增)** 封装 `WHERE id IN (...)` 查询，专为“导出选中”功能服务，能一次性高效地批量获取多条指定记录。
* `update_transaction_undone_status(...)`: 封装 `UPDATE ... SET is_undone = ?` 语句，用于执行撤销和恢复操作。
* `delete_transaction_permanently(...)`: 封装 `DELETE FROM ...` 语句，提供物理删除数据的接口。
* `get_transactions_by_date(...)`: 利用SQLite的 `strftime` 函数，封装按年、月、日进行日期维度筛选的 `SELECT` 查询。
* `get_transactions_by_filter(...)`: 利用 `LIKE` 和 `%` 通配符，封装按商品名称或型号进行模糊搜索的 `SELECT` 查询。
* `get_product_summary()`: 封装带有 `GROUP BY` 和 `SUM(quantity)` 的聚合查询，这是计算每种商品总库存的核心，直接为“库存汇总”视图提供数据支持。

---

### 5. `app/core/inventory.py` (库存核心逻辑模块)

作为应用的“业务逻辑层”，此模块是连接UI和数据的桥梁。它不直接执行SQL，而是调用 `data_manager` 的函数来操作数据，并在此过程中实施应用的业务规则。

* `record_inbound(...)` / `record_outbound(...)`: 实现出入库的核心规则。例如，`record_outbound` 会将UI传入的正数量转换为负数，以符合数据库的设计。这里也可以轻松扩展更复杂的逻辑，如检查库存是否充足。
* `undo_transaction(...)` / `redo_transaction(...)`: 实现撤销/恢复的业务流，它们会先检查记录的当前状态，避免无效操作，然后再调用数据层更新状态。
* `_format_and_save_to_excel(records, path)`: **(关键重构)** 这是一个私有的辅助方法，体现了“不要重复自己”(DRY)的原则。它将“导出全部”和“导出选中”功能中重复的数据格式化（如添加“类型”列、处理`NaN`值）和文件保存代码提取出来，使主功能函数更简洁、逻辑更清晰。
* `export_to_excel(path)` / `export_selected_records(ids, path)`: 这两个函数分别代表“导出全部”和“导出选中”的业务。它们各自负责获取所需的数据集（全部或部分），然后统一调用 `_format_and_save_to_excel` 来完成最后的导出工作。
* `import_from_excel(path)`: 实现文件导入的完整流程。它利用强大的 `pandas` 库读取Excel数据，然后逐行进行严格的业务验证（如必需字段是否为空，数据类型是否正确），只有通过验证的数据才会被分发到 `record_inbound` 或 `record_outbound` 方法进行处理。

---

### 6. `app/ui/main_window.py` (主窗口界面)

作为“表现层”的核心，它负责构建用户所看到的主界面，并通过事件驱动的方式响应用户的每一个操作。

* `__init__(...)`: 构造函数，负责窗口的整体初始化。它像一个总建筑师，按顺序创建和摆放顶部的操作按钮区、中间的数据表格区和底部的状态栏区。
* **DPI感知代码**: 在类定义前运行，通过`ctypes`库直接与Windows系统API交互，声明本应用为高DPI感知。这可以防止在高清显示器上，操作系统对窗口进行强制的位图拉伸，从而从根本上解决了字体和控件模糊的问题。
* `setup_transactions_view()` / `setup_summary_view()`: 这两个方法动态地配置 `Treeview` 组件，使其能在“交易明细”和“库存汇总”两种完全不同的视图之间无缝切换，提高了组件的复用性。
* `populate_treeview(rows)`: 负责将数据“渲染”到表格中。它循环遍历数据行，并将每一行插入 `Treeview`，同时根据数据内容（如是否已撤销）应用不同的视觉样式（tag），为用户提供直观的视觉反馈。
* `show_context_menu(event)`: 响应用户的右键单击事件。它能精确地获取鼠标点击位置（`event.x_root`, `event.y_root`）和主窗口的位置，通过计算差值，实现在鼠标指针旁弹出上下文菜单的精确操作。
* `import_from_excel_dialog()` / `export_to_excel_dialog()` / `export_selected_dialog()`: 这三个方法是UI与导入导出功能的连接点。它们通过 `filedialog` 模块弹出标准的文件选择/保存对话框，获取用户指定的文件路径后，立即调用 `InventoryManager` 中对应的业务逻辑方法来执行真正的操作，并将执行结果通过消息框(`tkmb`)反馈给用户。

---

### 7. `app/ui/dialogs.py` (对话框模块)

这个文件将所有需要从主窗口弹出的交互式子窗口进行封装，是模块化UI设计的重要体现。将对话框独立出来，使得主窗口的代码更简洁，也便于未来对特定对话框进行复用或修改。

* `TransactionDialog`: 一个多功能的对话框，根据传入的参数，既可用于“商品入库”，也可用于“商品出库”，甚至可以预留用于未来的“编辑”功能。
  * `__init__(...)`: 负责构建对话框的全部UI元素。它接收 `parent` (父窗口), `title` (窗口标题), `existing_data` (用于填充编辑数据)等参数。通过 `self.transient(parent)` 和 `self.grab_set()` 将对话框设置为“模态(modal)”模式，强制用户必须先完成对话框的操作才能返回主窗口，确保了操作流程的原子性。
  * `_validate_input()`: 这是一个关键的内部验证函数。在用户点击“确认”后，它会逐一检查所有必填输入框，确保数据类型正确（例如，`数量`必须是正整数，`单价`必须是有效的数字）且格式符合要求（例如，`操作日期`必须是 `YYYY-MM-DD` 格式）。这种前端验证能第一时间给用户提供清晰的反馈，避免无效数据进入到后端的业务逻辑层。
  * `get_input_data()`: 这是该对话框与主窗口交互的核心方法。它通过 `self.parent.wait_window(self)` 阻塞主窗口的后续代码执行，直到此对话框被关闭。如果用户点击“确认”并通过验证，它会返回一个包含所有输入数据的字典；如果用户点击“取消”或直接关闭窗口，它将返回 `None`。主窗口通过判断这个返回值来决定是否要继续执行后续的业务逻辑。
* `DateQueryDialog`: 一个专用于按日期查询的轻量级对话框。
  * `__init__(...)`: 创建三个简洁的输入框，分别用于输入年、月、日，为用户提供一个直观的日期筛选界面。
  * `_confirm_input()`: 在用户点击“查询”后，此方法会获取输入框中的内容，并进行基础的有效性检查（例如，年份是否为4位数字，月份是否在1-12之间）。它允许用户只填写部分字段（如只查年份、或只查年月），并将有效的查询条件打包成一个字典。
  * `get_query_dates()`: 采用与 `TransactionDialog` 相同的 `wait_window` 机制，等待用户输入。操作完成后，返回一个包含日期查询参数（如 `{'year': '2025', 'month': '06'}`）的字典，或者在用户取消时返回 `None`。
