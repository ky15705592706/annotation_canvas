# This Python file uses the following encoding: utf-8

"""
椭圆图形类 - 实现椭圆图形的数据结构和行为
"""

from typing import List, Dict, Any, Tuple
from PySide6.QtCore import QPointF, QRectF
from ..core.enums import DrawType, DrawColor, PenWidth, ControlPointType
from .shape import BaseShape
from .control_point import ControlPoint

class EllipseShape(BaseShape):
    """椭圆图形类 - 矩形内接椭圆"""
    
    def __init__(self, start_point: QPointF, end_point: QPointF, 
                 color: DrawColor = DrawColor.RED, pen_width: PenWidth = PenWidth.MEDIUM, z_order: int = None):
        self.start_point = start_point
        self.end_point = end_point
        super().__init__(DrawType.ELLIPSE, color, pen_width, z_order)
    
    def _initialize_control_points(self):
        """初始化控制点 - 椭圆有两个对角控制点"""
        # 左上角控制点
        top_left_cp = ControlPoint(
            position=self.start_point,
            control_type=ControlPointType.CORNER,
            index=0,
            size=8.0
        )
        
        # 右下角控制点
        bottom_right_cp = ControlPoint(
            position=self.end_point,
            control_type=ControlPointType.CORNER,
            index=1,
            size=8.0
        )
        
        self.control_points = [top_left_cp, bottom_right_cp]
    
    def get_bounds(self) -> QRectF:
        """获取图形边界矩形"""
        min_x = min(self.start_point.x(), self.end_point.x())
        min_y = min(self.start_point.y(), self.end_point.y())
        max_x = max(self.start_point.x(), self.end_point.x())
        max_y = max(self.start_point.y(), self.end_point.y())
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def get_center(self) -> QPointF:
        """获取椭圆中心"""
        bounds = self.get_bounds()
        return QPointF(
            bounds.x() + bounds.width() / 2,
            bounds.y() + bounds.height() / 2
        )
    
    
    def get_radius_x(self) -> float:
        """获取X轴半径"""
        return abs(self.end_point.x() - self.start_point.x()) / 2
    
    def get_radius_y(self) -> float:
        """获取Y轴半径"""
        return abs(self.end_point.y() - self.start_point.y()) / 2
    
    def contains_point(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在图形内"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
            
        center = self.get_center()
        radius_x = self.get_radius_x()
        radius_y = self.get_radius_y()
        
        # 检查半径是否有效
        if radius_x <= 0 or radius_y <= 0:
            # 如果椭圆无效，使用矩形判定
            bounds = self.get_bounds()
            expanded_bounds = QRectF(
                bounds.x() - tolerance,
                bounds.y() - tolerance,
                bounds.width() + 2 * tolerance,
                bounds.height() + 2 * tolerance
            )
            return expanded_bounds.contains(point)
        
        # 计算点到椭圆中心的距离
        dx = (point.x() - center.x()) / radius_x
        dy = (point.y() - center.y()) / radius_y
        distance = dx * dx + dy * dy
        
        # 在椭圆边界附近（考虑容差）
        tolerance_factor = tolerance / min(radius_x, radius_y) if min(radius_x, radius_y) > 0 else 1.0
        return distance <= (1.0 + tolerance_factor) ** 2
    
    
    def contains_point_on_boundary(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在椭圆轮廓线上（仅轮廓线，不包括内部）"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
            
        center = self.get_center()
        radius_x = self.get_radius_x()
        radius_y = self.get_radius_y()
        
        # 检查半径是否有效
        if radius_x <= 0 or radius_y <= 0:
            # 如果椭圆无效，使用矩形边界判定
            bounds = self.get_bounds()
            left = bounds.left()
            right = bounds.right()
            top = bounds.top()
            bottom = bounds.bottom()
            
            # 检查是否在矩形边界附近
            if left - tolerance <= point.x() <= right + tolerance:
                if abs(point.y() - top) <= tolerance or abs(point.y() - bottom) <= tolerance:
                    return True
            
            if top - tolerance <= point.y() <= bottom + tolerance:
                if abs(point.x() - left) <= tolerance or abs(point.x() - right) <= tolerance:
                    return True
            
            return False
        
        # 计算点到椭圆中心的归一化距离
        dx = (point.x() - center.x()) / radius_x
        dy = (point.y() - center.y()) / radius_y
        distance = dx * dx + dy * dy
        
        # 计算容差因子
        tolerance_factor = tolerance / min(radius_x, radius_y) if min(radius_x, radius_y) > 0 else 1.0
        
        # 检查是否在椭圆边界附近（在边界上或略超出边界，但不在内部）
        return 1.0 - tolerance_factor <= distance <= 1.0 + tolerance_factor
    
    def move_by(self, offset: QPointF):
        """移动图形"""
        self.start_point = QPointF(
            self.start_point.x() + offset.x(),
            self.start_point.y() + offset.y()
        )
        self.end_point = QPointF(
            self.end_point.x() + offset.x(),
            self.end_point.y() + offset.y()
        )
        # 更新控制点位置
        self.update_control_points()
    
    def scale_by_control_point(self, control_point: ControlPoint, new_position: QPointF):
        """通过控制点缩放图形"""
        if control_point.index == 0:  # 左上角控制点
            # 保持右下角不变，移动左上角
            self.start_point = new_position
        elif control_point.index == 1:  # 右下角控制点
            # 保持左上角不变，移动右下角
            self.end_point = new_position
        
        # 更新控制点位置
        self.update_control_points()
    
    def update_control_points(self):
        """更新控制点位置"""
        self.control_points[0].set_position(self.start_point)
        self.control_points[1].set_position(self.end_point)
    
    def get_start_point(self) -> QPointF:
        """获取起始点"""
        return self.start_point
    
    def get_end_point(self) -> QPointF:
        """获取结束点"""
        return self.end_point
    
    def set_start_point(self, point: QPointF):
        """设置起始点"""
        self.start_point = point
        self.update_control_points()
    
    def set_end_point(self, point: QPointF):
        """设置结束点"""
        self.end_point = point
        self.update_control_points()
    
    def get_width(self) -> float:
        """获取宽度"""
        return abs(self.end_point.x() - self.start_point.x())
    
    def get_height(self) -> float:
        """获取高度"""
        return abs(self.end_point.y() - self.start_point.y())
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'start_point': (self.start_point.x(), self.start_point.y()),
            'end_point': (self.end_point.x(), self.end_point.y())
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EllipseShape':
        """从字典创建实例，用于反序列化"""
        start_point = QPointF(data['start_point'][0], data['start_point'][1])
        end_point = QPointF(data['end_point'][0], data['end_point'][1])
        color = DrawColor(data.get('color', DrawColor.RED.value))
        pen_width = PenWidth(data.get('pen_width', PenWidth.MEDIUM.value))
        z_order = data.get('z_order', None)
        
        return cls(start_point, end_point, color, pen_width, z_order)
    
    def __str__(self) -> str:
        return f"EllipseShape(start=({self.start_point.x():.1f}, {self.start_point.y():.1f}), " \
               f"end=({self.end_point.x():.1f}, {self.end_point.y():.1f}))"
