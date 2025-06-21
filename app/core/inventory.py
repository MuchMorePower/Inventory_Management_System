# app/core/inventory.py
from . import data_manager
import pandas as pd
from datetime import datetime

class InventoryManager:
    def __init__(self):
        pass # data_manager is used directly via its functions

    def record_inbound(self, product_name, model_number, unit, quantity, unit_price, insertion_date_str, notes="", buyer="", seller=""):
        """
        记录入库
        已更新，增加 buyer 和 seller 参数
        """
        if quantity <= 0:
            return False, "入库数量必须大于0"
        # 入库时，我们记录的是销售方(seller)
        result_id = data_manager.add_transaction(product_name, model_number, unit, quantity, unit_price, insertion_date_str, notes, buyer, seller)
        return (True, "入库成功") if result_id else (False, "数据库操作失败")
    
    def record_outbound(self, product_name, model_number, unit, quantity, unit_price, insertion_date_str, notes="", buyer="", seller=""):
        """
        记录出库
        已更新，增加 buyer 和 seller 参数
        """
        if quantity <= 0:
            return False, "出库数量必须大于0"
        
        # 出库时，我们记录的是购买方(buyer)
        result_id = data_manager.add_transaction(product_name, model_number, unit, -quantity, unit_price, insertion_date_str, notes, buyer, seller)
        return (True, "出库成功") if result_id else (False, "数据库操作失败")
    
    def undo_transaction(self, transaction_id):
        """撤销一笔交易"""
        transaction = data_manager.get_transaction_by_id(transaction_id)
        if not transaction:
            return False, "交易不存在"
        if transaction['is_undone']:
            return False, "交易已撤销，无需重复操作"
        
        success = data_manager.update_transaction_undone_status(transaction_id, True)
        if success:
            return True, "交易撤销成功"
        else:
            return False, "交易撤销失败"
            
    def redo_transaction(self, transaction_id): # 新增：恢复已撤销的交易
        """恢复（重做）一笔已撤销的交易"""
        transaction = data_manager.get_transaction_by_id(transaction_id)
        if not transaction:
            return False, "交易不存在"
        if not transaction['is_undone']: # 如果不是已撤销状态
            return False, "交易未被撤销，无需恢复"
        
        success = data_manager.update_transaction_undone_status(transaction_id, False) # 设置为未撤销
        if success:
            return True, "交易恢复成功"
        else:
            return False, "交易恢复失败"

    def delete_transaction(self, transaction_id):
        """永久删除一条记录 (如果需要)"""
        # 实际应用中，物理删除可能需要权限或记录，这里简单实现
        success = data_manager.delete_transaction_permanently(transaction_id)
        if success:
            return True, "记录已永久删除"
        else:
            return False, "删除失败"

    def get_all_records(self, include_undone=False):
        """获取所有交易记录 (UI显示用)"""
        return data_manager.get_all_transactions(include_undone=include_undone)
   
    def get_records_with_advanced_filter(self, filter_criteria: dict):
        """调用数据层执行高级筛选"""
        return data_manager.get_transactions_with_advanced_filter(filter_criteria)

    def get_product_summary_view(self):
        """获取商品汇总视图"""
        return data_manager.get_product_summary()

    def get_current_stock_for_product(self, product_name, model_number):
        """获取特定商品当前库存"""
        summary = data_manager.get_product_summary()
        for item in summary:
            if item['product_name'] == product_name and item['model_number'] == model_number:
                return item['current_stock']
        return 0
        
    def calculate_selected_totals(self, selected_transaction_ids):
        """计算选定交易的总金额 (税额暂不处理)"""
        total_value = 0
        valid_transactions = 0
        for tid in selected_transaction_ids:
            transaction = data_manager.get_transaction_by_id(tid)
            if transaction and not transaction['is_undone']: # 只计算有效且未撤销的
                total_value += transaction['total_amount']
                valid_transactions +=1
        return {"total_amount": total_value, "count": valid_transactions}
    
    def get_transaction_details(self, transaction_id):
        """获取单个交易记录的详细信息"""
        return data_manager.get_transaction_by_id(transaction_id)
    
    def _format_and_save_to_excel(self, records: list, file_path: str) -> tuple[bool, str]:
        """
        【私有辅助方法】将给定的记录列表格式化并保存到Excel。
        """
        if not records:
            return False, "没有可导出的记录。"
        try:
            records_as_dicts = [dict(row) for row in records]
            df = pd.DataFrame(records_as_dicts)

            df.fillna('', inplace=True)

            # --- 数据格式化 ---
            df['类型'] = df['quantity'].apply(lambda x: "入库" if x > 0 else "出库")
            df['状态'] = df['is_undone'].apply(lambda x: "已撤销" if x else "有效")
            df['quantity'] = df['quantity'].abs()

            # --- 重命名并排序 ---
            df_to_export = df.rename(columns={
                'id': 'ID',
                'insertion_date': '操作日期',
                'product_name': '项目名称',
                'model_number': '规格型号',
                'unit': '单位',
                'quantity': '数量',
                'unit_price': '单价',
                'total_amount': '总金额',
                'notes': '备注',
                'transaction_time': '记录时间',
                'buyer': '购买方',
                'seller': '销售方'
            })
            export_columns = [
                'ID', '操作日期', '项目名称', '规格型号', '购买方', '销售方', '单位', '类型',
                '数量', '单价', '总金额', '状态', '备注', '记录时间'
            ]
            
            export_columns_exist = [col for col in export_columns if col in df_to_export.columns]
            df_to_export = df_to_export[export_columns_exist]
            
            df_to_export.to_excel(file_path, index=False, engine='openpyxl')
            return True, f"成功导出 {len(df)} 条记录到 {file_path}"

        except KeyError as e:
            return False, f"导出失败：处理数据时找不到预期的列名 {e}。"
        except Exception as e:
            return False, f"导出失败，发生未知错误: {e}"

    def export_to_excel(self, file_path: str) -> tuple[bool, str]:
        """【导出全部】将所有交易记录导出到 Excel 文件。"""
        records = data_manager.get_all_transactions(include_undone=True)
        return self._format_and_save_to_excel(records, file_path)

    def export_selected_records(self, transaction_ids: list, file_path: str) -> tuple[bool, str]:
        """【导出选中】将指定的交易记录导出到 Excel 文件。"""
        records = data_manager.get_transactions_by_ids(transaction_ids)
        return self._format_and_save_to_excel(records, file_path)
    
        
    def import_from_excel(self, file_path: str) -> tuple[bool, str]:
        """从 Excel 文件导入交易记录。"""
        try:
            df = pd.read_excel(file_path).fillna('')

            required_columns = ['项目名称', '规格型号', '类型', '数量', '单价', '操作日期']
            for col in required_columns:
                if col not in df.columns:
                    return False, f"导入失败：Excel文件中缺少必需的列 '{col}'。"

            success_count = 0
            fail_count = 0
            error_messages = []

            for index, row in df.iterrows():
                try:
                    product_name = str(row['项目名称']).strip()
                    model_number = str(row['规格型号']).strip()
                    trans_type = str(row['类型']).strip()
                    quantity = int(row['数量'])
                    unit_price = float(row['单价'])
                    
                    try:
                        insertion_date = pd.to_datetime(row['操作日期']).strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        fail_count += 1
                        error_messages.append(f"行 {index+2}: '操作日期'格式无效 ({row['操作日期']})")
                        continue
                        
                    unit = str(row.get('单位', '')).strip()
                    notes = str(row.get('备注', '')).strip()
                    buyer = str(row.get('购买方', '')).strip()
                    seller = str(row.get('销售方', '')).strip()

                    if not all([product_name, model_number, trans_type]):
                        fail_count += 1
                        error_messages.append(f"行 {index+2}: 项目名称, 规格型号, 类型不能为空。")
                        continue
                    
                    if quantity <= 0:
                        fail_count += 1
                        error_messages.append(f"行 {index+2}: 数量必须为正数。")
                        continue

                    if trans_type == "入库":
                        self.record_inbound(product_name, model_number, unit, quantity, unit_price, insertion_date, notes, buyer=buyer, seller=seller)
                    elif trans_type == "出库":
                        self.record_outbound(product_name, model_number, unit, quantity, unit_price, insertion_date, notes, buyer=buyer, seller=seller)
                    else:
                        fail_count += 1
                        error_messages.append(f"行 {index+2}: 类型 '{trans_type}' 无效，应为'入库'或'出库'。")
                        continue
                    
                    success_count += 1
                except (ValueError, TypeError) as e:
                    fail_count += 1
                    error_messages.append(f"行 {index+2}: 数据格式错误 - {e}")
                    continue

            if fail_count > 0:
                summary = f"导入完成。成功: {success_count}, 失败: {fail_count}。\n\n错误详情:\n" + "\n".join(error_messages[:5])
                return False, summary
            else:
                return True, f"成功导入 {success_count} 条记录。"
        except Exception as e:
            return False, f"导入失败: {e}"
        