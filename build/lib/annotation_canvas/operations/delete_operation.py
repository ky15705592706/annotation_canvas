"""
删除操作 - 处理图形删除操作
"""

from typing import Any, Dict, List
from .stateful_operation import StatefulOperation
from ..models.shape import BaseShape

class DeleteOperation(StatefulOperation):
    """删除操作类"""
    
    def __init__(self, shapes: List[BaseShape], data_manager, description: str = ""):
        super().__init__(description or f"删除{len(shapes)}个图形")
        self.shapes = shapes.copy()  # 创建副本
        self.data_manager = data_manager
        
        # 设置操作函数
        self.set_execute_function(self._execute_delete)
        self.set_undo_function(self._undo_delete)
        self.set_redo_function(self._execute_delete)  # 重做使用相同的执行函数
    
    def _execute_delete(self) -> bool:
        """执行删除操作"""
        for shape in self.shapes:
            self.data_manager.remove_shape(shape)
        return True
    
    def _undo_delete(self) -> bool:
        """撤销删除操作"""
        for shape in self.shapes:
            self.data_manager.add_shape(shape)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'shapes': [shape.to_dict() for shape in self.shapes],
            'executed': self.executed
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], data_manager) -> 'DeleteOperation':
        """从字典创建实例，用于反序列化"""
        # 重建图形列表
        shapes = []
        for shape_data in data.get('shapes', []):
            # 这里需要根据图形类型创建相应的图形实例
            # 简化处理，实际应用中需要更复杂的工厂模式
            pass
        
        operation = cls(shapes, data_manager, data.get('description', ''))
        operation.executed = data.get('executed', False)
        return operation
