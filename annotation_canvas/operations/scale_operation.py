"""
缩放操作 - 处理图形缩放操作
"""

from typing import Any, Dict, List
from PySide6.QtCore import QPointF
from .preview_operation import PreviewOperation
from ..models.shape import BaseShape
from ..models.control_point import ControlPoint
from ..utils.coordinate_utils_functions import qpointf_to_dict, dict_to_qpointf

class ScaleOperation(PreviewOperation):
    """缩放操作类"""
    
    def __init__(self, shape: BaseShape, control_point: ControlPoint, old_position: QPointF, new_position: QPointF, description: str = "", already_executed: bool = False):
        super().__init__(description or f"缩放{shape.shape_type.name}图形", already_executed)
        self.shape = shape
        self.control_point = control_point
        self.old_position = old_position
        self.new_position = new_position
        
        # 设置操作函数
        self.set_execute_function(self._execute_with_preview_check)
        self.set_undo_function(self._undo_scale)
        self.set_redo_function(self._redo_always)
    
    def _do_execute(self) -> bool:
        """实际执行缩放操作"""
        self.shape.scale_by_control_point(self.control_point, self.new_position)
        return True
    
    def _undo_scale(self) -> bool:
        """撤销缩放操作"""
        return self._do_undo()
    
    def _do_undo(self) -> bool:
        """实际撤销缩放操作"""
        self.shape.scale_by_control_point(self.control_point, self.old_position)
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'shape': self.shape.to_dict(),
            'control_point': self.control_point.to_dict(),
            'old_position': qpointf_to_dict(self.old_position),
            'new_position': qpointf_to_dict(self.new_position),
            'executed': self.executed
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], data_manager) -> 'ScaleOperation':
        """从字典创建实例，用于反序列化"""
        # 重建图形和控制点
        shape_data = data.get('shape', {})
        control_point_data = data.get('control_point', {})
        
        # 这里需要根据图形类型创建相应的图形实例
        # 简化处理，实际应用中需要更复杂的工厂模式
        shape = None
        control_point = None
        
        old_pos_data = data.get('old_position', {'x': 0, 'y': 0})
        new_pos_data = data.get('new_position', {'x': 0, 'y': 0})
        old_position = dict_to_qpointf(old_pos_data)
        new_position = dict_to_qpointf(new_pos_data)
        
        operation = cls(shape, control_point, old_position, new_position, data.get('description', ''))
        operation.executed = data.get('executed', False)
        return operation
