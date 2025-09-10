"""
操作管理器 - 管理操作历史和撤销恢复
"""

from typing import List, Optional, Dict, Any
from .base_operation import BaseOperation, CompositeOperation
import json
import time

class OperationManager:
    """操作管理器"""
    
    def __init__(self):
        self.operation_history: List[BaseOperation] = []
        self.current_index = -1
    
    def execute_operation(self, operation: BaseOperation) -> bool:
        """执行操作"""
        if operation.execute():
            # 如果当前不在历史记录末尾，删除后面的操作
            if self.current_index < len(self.operation_history) - 1:
                self.operation_history = self.operation_history[:self.current_index + 1]
            
            # 添加到历史记录
            self.operation_history.append(operation)
            self.current_index = len(self.operation_history) - 1
            
            return True
        return False
    
    def undo(self) -> bool:
        """撤销操作"""
        if not self.can_undo():
            return False
        
        # 获取当前操作
        current_operation = self.operation_history[self.current_index]
        
        # 撤销操作
        if current_operation.undo():
            # 更新当前索引
            self.current_index -= 1
            return True
        
        return False
    
    def redo(self) -> bool:
        """重做操作"""
        if not self.can_redo():
            return False
        
        # 获取下一个操作
        next_operation = self.operation_history[self.current_index + 1]
        
        # 重做操作
        if next_operation.redo():
            # 更新当前索引
            self.current_index += 1
            return True
        
        return False
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return (self.current_index >= 0 and 
                self.current_index < len(self.operation_history))
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return (self.current_index + 1 < len(self.operation_history))
    
    def get_undo_description(self) -> Optional[str]:
        """获取可撤销操作的描述"""
        if self.can_undo():
            return self.operation_history[self.current_index].get_description()
        return None
    
    def get_redo_description(self) -> Optional[str]:
        """获取可重做操作的描述"""
        if self.can_redo():
            return self.operation_history[self.current_index + 1].get_description()
        return None
    
    def clear_history(self):
        """清空历史记录"""
        self.operation_history.clear()
        self.current_index = -1
    
    def get_history_size(self) -> int:
        """获取历史记录大小"""
        return len(self.operation_history)
    
    def get_current_index(self) -> int:
        """获取当前索引"""
        return self.current_index
    
    def get_operation_at(self, index: int) -> Optional[BaseOperation]:
        """获取指定索引的操作"""
        if 0 <= index < len(self.operation_history):
            return self.operation_history[index]
        return None
    
    def get_operation_list(self) -> List[BaseOperation]:
        """获取操作列表"""
        return self.operation_history.copy()
    
    def create_composite_operation(self, description: str = "") -> CompositeOperation:
        """创建复合操作"""
        return CompositeOperation(description)
    
    def execute_composite_operation(self, composite_operation: CompositeOperation) -> bool:
        """执行复合操作"""
        if composite_operation.get_operation_count() == 0:
            return False
        
        return self.execute_operation(composite_operation)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        return {
            'current_index': self.current_index,
            'operation_history': [op.to_dict() for op in self.operation_history]
        }
    
    def from_dict(self, data: Dict[str, Any], context):
        """从字典创建实例，用于反序列化"""
        self.current_index = data.get('current_index', -1)
        
        # 清空现有数据
        self.operation_history.clear()
        
        # 重建操作历史
        for op_data in data.get('operation_history', []):
            # 这里需要根据操作类型创建相应的操作实例
            # 简化处理，实际应用中需要更复杂的工厂模式
            pass
    
    def save_to_file(self, filename: str):
        """保存到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            pass
    
    def load_from_file(self, filename: str, context):
        """从文件加载"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.from_dict(data, context)
        except Exception as e:
            pass
    
    def __str__(self) -> str:
        return f"OperationManager(history_size={len(self.operation_history)}, current_index={self.current_index})"
    
    def __repr__(self) -> str:
        return self.__str__()
