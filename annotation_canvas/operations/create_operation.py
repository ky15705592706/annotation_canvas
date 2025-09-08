"""
创建操作 - 处理图形创建操作
"""

from typing import Any, Dict, Optional
from PySide6.QtCore import QPointF
from .stateful_operation import StatefulOperation
from ..models.shape import BaseShape
from ..core.enums import DrawType

class CreateOperation(StatefulOperation):
    """创建操作类"""
    
    def __init__(self, shape: BaseShape, data_manager, description: str = ""):
        super().__init__(description or f"创建{shape.shape_type.name}图形")
        self.shape = shape
        self.data_manager = data_manager
        
        # 设置操作函数
        self.set_execute_function(self._execute_create)
        self.set_undo_function(self._undo_create)
        self.set_redo_function(self._execute_create)  # 重做使用相同的执行函数
    
    def _execute_create(self) -> bool:
        """执行创建操作"""
        self.data_manager.add_shape(self.shape)
        return True
    
    def _undo_create(self) -> bool:
        """撤销创建操作"""
        return self.data_manager.remove_shape(self.shape)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'shape': self.shape.to_dict(),
            'executed': self.executed
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], data_manager) -> 'CreateOperation':
        """从字典创建实例，用于反序列化"""
        # 根据图形类型创建相应的图形实例
        shape_data = data['shape']
        shape_type = DrawType(shape_data['shape_type'])
        
        if shape_type == DrawType.POINT:
            from ..models.point import PointShape
            shape = PointShape.from_dict(shape_data)
        elif shape_type == DrawType.RECTANGLE:
            from ..models.rectangle import RectangleShape
            shape = RectangleShape.from_dict(shape_data)
        elif shape_type == DrawType.ELLIPSE:
            from ..models.ellipse import EllipseShape
            shape = EllipseShape.from_dict(shape_data)
        elif shape_type == DrawType.POLYGON:
            from ..models.polygon import PolygonShape
            shape = PolygonShape.from_dict(shape_data)
        else:
            raise ValueError(f"不支持的图形类型: {shape_type}")
        
        operation = cls(shape, data_manager, data.get('description', ''))
        operation.executed = data.get('executed', False)
        return operation

class CreatePointOperation(CreateOperation):
    """创建点操作"""
    
    def __init__(self, position: QPointF, color, pen_width, data_manager):
        from ..models.point import PointShape
        shape = PointShape(position, color, pen_width)
        super().__init__(shape, data_manager, f"创建点({position.x():.1f}, {position.y():.1f})")

class CreateRectangleOperation(CreateOperation):
    """创建矩形操作"""
    
    def __init__(self, start_point: QPointF, end_point: QPointF, color, pen_width, data_manager):
        from ..models.rectangle import RectangleShape
        shape = RectangleShape(start_point, end_point, color, pen_width)
        super().__init__(shape, data_manager, f"创建矩形({start_point.x():.1f}, {start_point.y():.1f}) -> ({end_point.x():.1f}, {end_point.y():.1f})")

class CreateEllipseOperation(CreateOperation):
    """创建椭圆操作"""
    
    def __init__(self, start_point: QPointF, end_point: QPointF, color, pen_width, data_manager):
        from ..models.ellipse import EllipseShape
        shape = EllipseShape(start_point, end_point, color, pen_width)
        super().__init__(shape, data_manager, f"创建椭圆({start_point.x():.1f}, {start_point.y():.1f}) -> ({end_point.x():.1f}, {end_point.y():.1f})")

class CreatePolygonOperation(CreateOperation):
    """创建多边形操作"""
    
    def __init__(self, vertices: list, color, pen_width, data_manager):
        from ..models.polygon import PolygonShape
        shape = PolygonShape(vertices, color, pen_width)
        super().__init__(shape, data_manager, f"创建多边形({len(vertices)}个顶点)")
