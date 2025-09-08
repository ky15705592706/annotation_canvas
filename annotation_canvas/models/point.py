# This Python file uses the following encoding: utf-8

"""
点图形类 - 实现点图形的数据结构和行为
"""

from typing import List, Dict, Any, Tuple
from PySide6.QtCore import QPointF, QRectF
from ..core.enums import DrawType, DrawColor, PenWidth, ControlPointType
from .shape import BaseShape
from .control_point import ControlPoint

class PointShape(BaseShape):
    """点图形类"""
    
    def __init__(self, position: QPointF, color: DrawColor = DrawColor.RED, 
                 pen_width: PenWidth = PenWidth.MEDIUM):
        self.position = position
        super().__init__(DrawType.POINT, color, pen_width)
    
    def _initialize_control_points(self):
        """初始化控制点 - 点图形只有一个中心控制点"""
        center_cp = ControlPoint(
            position=self.position,
            control_type=ControlPointType.CENTER,
            index=0,
            size=8.0
        )
        self.control_points = [center_cp]
    
    def get_bounds(self) -> QRectF:
        """获取图形边界矩形"""
        # 点图形的边界是一个小正方形
        size = 10.0  # 点的显示大小
        half_size = size / 2
        return QRectF(
            self.position.x() - half_size,
            self.position.y() - half_size,
            size,
            size
        )
    
    def contains_point(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在图形内"""
        from ..utils.geometry import GeometryUtils
        from ..utils.constants import InteractionConstants
        
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
            
        distance = GeometryUtils.distance_between_points(point, self.position)
        return distance <= tolerance
    
    
    def contains_point_on_boundary(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在点图形轮廓线上 - 点图形的轮廓线就是点本身"""
        return self.contains_point(point, tolerance)
    
    def move_by(self, offset: QPointF):
        """移动图形"""
        self.position = QPointF(
            self.position.x() + offset.x(),
            self.position.y() + offset.y()
        )
        # 更新控制点位置
        self.control_points[0].set_position(self.position)
    
    def scale_by_control_point(self, control_point: ControlPoint, new_position: QPointF):
        """通过控制点缩放图形 - 点图形不支持缩放，只支持移动"""
        # 点图形不支持缩放，直接移动
        self.position = new_position
        self.control_points[0].set_position(self.position)
    
    def get_center(self) -> QPointF:
        """获取点中心（点图形的中心就是位置）"""
        return self.position
    
    def get_position(self) -> QPointF:
        """获取点位置"""
        return self.position
    
    def set_position(self, position: QPointF):
        """设置点位置"""
        self.position = position
        self.control_points[0].set_position(position)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'position': (self.position.x(), self.position.y())
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PointShape':
        """从字典创建实例，用于反序列化"""
        position = QPointF(data['position'][0], data['position'][1])
        color = DrawColor(data.get('color', DrawColor.RED.value))
        pen_width = PenWidth(data.get('pen_width', PenWidth.MEDIUM.value))
        
        return cls(position, color, pen_width)
    
    def __str__(self) -> str:
        return f"PointShape(pos=({self.position.x():.1f}, {self.position.y():.1f}))"
