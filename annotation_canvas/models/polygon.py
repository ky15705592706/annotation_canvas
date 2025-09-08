# This Python file uses the following encoding: utf-8

"""
多边形图形类 - 实现多边形图形的数据结构和行为
"""

from typing import List, Dict, Any, Tuple
from PySide6.QtCore import QPointF, QRectF
from ..core.enums import DrawType, DrawColor, PenWidth, ControlPointType
from ..utils.constants import InteractionConstants
from .shape import BaseShape
from .control_point import ControlPoint

class PolygonShape(BaseShape):
    """多边形图形类"""
    
    def __init__(self, vertices: List[QPointF], color: DrawColor = DrawColor.RED, 
                 pen_width: PenWidth = PenWidth.MEDIUM):
        self.vertices = vertices.copy() if vertices else []
        self.closed = True  # 默认闭合
        super().__init__(DrawType.POLYGON, color, pen_width)
    
    def _initialize_control_points(self):
        """初始化控制点 - 多边形每个顶点一个控制点"""
        self.control_points = []
        for i, vertex in enumerate(self.vertices):
            from ..utils.constants import InteractionConstants
            cp = ControlPoint(
                position=vertex,
                control_type=ControlPointType.VERTEX,
                index=i,
                size=InteractionConstants.CONTROL_POINT_DEFAULT_SIZE
            )
            self.control_points.append(cp)
    
    def get_bounds(self) -> QRectF:
        """获取图形边界矩形"""
        if not self.vertices:
            return QRectF()
        
        x_coords = [v.x() for v in self.vertices]
        y_coords = [v.y() for v in self.vertices]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    
    def get_center(self) -> QPointF:
        """获取多边形重心"""
        if not self.vertices:
            return QPointF(0, 0)
        
        x_sum = sum(v.x() for v in self.vertices)
        y_sum = sum(v.y() for v in self.vertices)
        n = len(self.vertices)
        
        return QPointF(x_sum / n, y_sum / n)
    
    
    def contains_point(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在图形内（射线法）"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
        
        if len(self.vertices) < InteractionConstants.POLYGON_MIN_VERTICES:
            return False
        
        x, y = point.x(), point.y()
        n = len(self.vertices)
        inside = False
        
        p1x, p1y = self.vertices[0].x(), self.vertices[0].y()
        for i in range(1, n + 1):
            p2x, p2y = self.vertices[i % n].x(), self.vertices[i % n].y()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    
    def contains_point_on_boundary(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在多边形轮廓线上（仅轮廓线，不包括内部）"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
        
        if len(self.vertices) < 2:
            return False
        
        x, y = point.x(), point.y()
        n = len(self.vertices)
        
        # 检查是否在任何一条边上
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            
            # 计算点到线段的距离
            from ..utils.geometry import GeometryUtils
            if GeometryUtils.point_to_line_distance(point, p1, p2) <= tolerance:
                return True
        
        return False
    
    
    def move_by(self, offset: QPointF):
        """移动图形"""
        for i, vertex in enumerate(self.vertices):
            self.vertices[i] = QPointF(
                vertex.x() + offset.x(),
                vertex.y() + offset.y()
            )
        
        # 更新控制点位置
        self.update_control_points()
    
    def scale_by_control_point(self, control_point: ControlPoint, new_position: QPointF):
        """通过控制点缩放图形"""
        if 0 <= control_point.index < len(self.vertices):
            self.vertices[control_point.index] = new_position
            # 更新控制点位置
            self.update_control_points()
    
    def update_control_points(self):
        """更新控制点位置"""
        # 确保控制点数量与顶点数量一致
        while len(self.control_points) < len(self.vertices):
            cp = ControlPoint(
                position=QPointF(0, 0),
                control_type=ControlPointType.VERTEX,
                index=len(self.control_points),
                size=8.0
            )
            self.control_points.append(cp)
        
        # 移除多余的控制点
        while len(self.control_points) > len(self.vertices):
            self.control_points.pop()
        
        # 更新控制点位置
        for i, vertex in enumerate(self.vertices):
            if i < len(self.control_points):
                self.control_points[i].set_position(vertex)
    
    def add_vertex(self, vertex: QPointF, index: int = -1):
        """添加顶点"""
        if index == -1:
            self.vertices.append(vertex)
        else:
            self.vertices.insert(index, vertex)
        
        # 重新初始化控制点
        self._initialize_control_points()
    
    def remove_vertex(self, index: int):
        """移除顶点"""
        if 0 <= index < len(self.vertices):
            self.vertices.pop(index)
            # 重新初始化控制点
            self._initialize_control_points()
    
    def get_vertex(self, index: int) -> QPointF:
        """获取顶点"""
        if 0 <= index < len(self.vertices):
            return self.vertices[index]
        return QPointF(0, 0)
    
    def set_vertex(self, index: int, vertex: QPointF):
        """设置顶点"""
        if 0 <= index < len(self.vertices):
            self.vertices[index] = vertex
            # 更新控制点位置
            self.update_control_points()
    
    def get_vertex_count(self) -> int:
        """获取顶点数量"""
        return len(self.vertices)
    
    def is_closed(self) -> bool:
        """检查多边形是否闭合"""
        if len(self.vertices) < 3:
            return False
        
        # 检查第一个和最后一个顶点是否相同
        first = self.vertices[0]
        last = self.vertices[-1]
        return abs(first.x() - last.x()) < 1e-6 and abs(first.y() - last.y()) < 1e-6
    
    def close_polygon(self):
        """闭合多边形"""
        if len(self.vertices) >= InteractionConstants.POLYGON_MIN_VERTICES and not self.is_closed():
            self.vertices.append(self.vertices[0])
            self._initialize_control_points()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'vertices': [(v.x(), v.y()) for v in self.vertices]
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PolygonShape':
        """从字典创建实例，用于反序列化"""
        vertices = [QPointF(v[0], v[1]) for v in data.get('vertices', [])]
        color = DrawColor(data.get('color', DrawColor.RED.value))
        pen_width = PenWidth(data.get('pen_width', PenWidth.MEDIUM.value))
        
        return cls(vertices, color, pen_width)
    
    def __str__(self) -> str:
        return f"PolygonShape(vertices={len(self.vertices)}, closed={self.is_closed()})"
