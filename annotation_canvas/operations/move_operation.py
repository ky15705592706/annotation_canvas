"""
移动操作 - 处理图形移动操作
"""

from typing import Any, Dict, List
from PySide6.QtCore import QPointF
from .preview_operation import PreviewOperation
from ..models.shape import BaseShape
from ..utils.coordinate_utils import CoordinateUtils

class MoveOperation(PreviewOperation):
    """移动操作类"""
    
    def __init__(self, shapes: List[BaseShape], offset: QPointF, description: str = "", already_executed: bool = False):
        super().__init__(description or f"移动{len(shapes)}个图形", already_executed)
        self.shapes = shapes.copy()  # 创建副本
        self.offset = offset
        
        # 设置操作函数
        self.set_execute_function(self._execute_with_preview_check)
        self.set_undo_function(self._undo_move)
        self.set_redo_function(self._redo_always)
    
    def _do_execute(self) -> bool:
        """实际执行移动操作"""
        for shape in self.shapes:
            shape.move_by(self.offset)
        return True
    
    def _undo_move(self) -> bool:
        """撤销移动操作"""
        return self._do_undo()
    
    def _do_undo(self) -> bool:
        """实际撤销移动操作"""
        reverse_offset = QPointF(-self.offset.x(), -self.offset.y())
        for shape in self.shapes:
            shape.move_by(reverse_offset)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'shapes': [shape.to_dict() for shape in self.shapes],
            'offset': CoordinateUtils.qpointf_to_dict(self.offset),
            'executed': self.executed
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], data_manager) -> 'MoveOperation':
        """从字典创建实例，用于反序列化"""
        # 重建图形列表
        shapes = []
        for shape_data in data.get('shapes', []):
            # 这里需要根据图形类型创建相应的图形实例
            # 简化处理，实际应用中需要更复杂的工厂模式
            pass
        
        offset_data = data.get('offset', {'x': 0, 'y': 0})
        offset = CoordinateUtils.dict_to_qpointf(offset_data)
        
        operation = cls(shapes, offset, data.get('description', ''))
        operation.executed = data.get('executed', False)
        return operation
