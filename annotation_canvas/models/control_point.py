"""
控制点类 - 定义控制点的数据结构和行为
"""

from typing import Optional, Tuple
from PySide6.QtCore import QPointF, QRectF
from ..core.enums import ControlPointType

class ControlPoint:
    """控制点类"""
    
    def __init__(self, position: QPointF, control_type: ControlPointType, 
                 index: int = 0, size: float = None):
        self.position = position
        self.control_type = control_type
        self.index = index
        from ..utils.constants import InteractionConstants
        self.size = size if size is not None else InteractionConstants.CONTROL_POINT_DEFAULT_SIZE
        self.visible = True
        self.hovered = False
        self.dragging = False
        self.original_position = position
        self.graphics_item = None  # PyQtGraph图形项引用
    
    def contains_point(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在控制点范围内"""
        from ..utils.geometry import GeometryUtils
        from ..utils.constants import InteractionConstants
        
        distance = GeometryUtils.distance_between_points(point, self.position)
        if tolerance is None:
            tolerance = InteractionConstants.CONTROL_POINT_TOLERANCE
        return distance <= tolerance
    
    def get_bounds(self) -> QRectF:
        """获取控制点边界矩形"""
        half_size = self.size / 2
        return QRectF(
            self.position.x() - half_size,
            self.position.y() - half_size,
            self.size,
            self.size
        )
    
    def set_position(self, position: QPointF):
        """设置控制点位置"""
        self.position = position
        if self.graphics_item:
            self.graphics_item.setData([position.x()], [position.y()])
    
    def get_position(self) -> QPointF:
        """获取控制点位置"""
        return self.position
    
    def start_dragging(self):
        """开始拖拽"""
        self.dragging = True
        self.original_position = self.position
    
    def stop_dragging(self):
        """停止拖拽"""
        self.dragging = False
    
    def is_dragging(self) -> bool:
        """检查是否正在拖拽"""
        return self.dragging
    
    def set_visible(self, visible: bool):
        """设置可见性"""
        self.visible = visible
        if self.graphics_item:
            self.graphics_item.setVisible(visible)
    
    def is_visible(self) -> bool:
        """检查是否可见"""
        return self.visible
    
    def set_hovered(self, hovered: bool):
        """设置悬停状态"""
        self.hovered = hovered
    
    def is_hovered(self) -> bool:
        """检查是否悬停"""
        return self.hovered
    
    def get_color(self) -> Tuple[int, int, int]:
        """获取控制点颜色"""
        from ..utils.constants import ColorConstants
        
        if self.dragging:
            return ColorConstants.CONTROL_POINT_DRAGGING
        elif self.hovered:
            return ColorConstants.CONTROL_POINT_HOVER
        elif self.control_type == ControlPointType.CENTER:
            return ColorConstants.CONTROL_POINT_CENTER
        elif self.control_type == ControlPointType.CORNER:
            return ColorConstants.CONTROL_POINT_CORNER
        elif self.control_type == ControlPointType.EDGE:
            return ColorConstants.CONTROL_POINT_EDGE
        elif self.control_type == ControlPointType.VERTEX:
            return ColorConstants.CONTROL_POINT_VERTEX
        else:
            return ColorConstants.CONTROL_POINT_DEFAULT
    
    def get_style(self) -> str:
        """获取控制点样式"""
        if self.control_type == ControlPointType.CENTER:
            return "circle"
        elif self.control_type == ControlPointType.CORNER:
            return "square"
        elif self.control_type == ControlPointType.EDGE:
            return "diamond"
        elif self.control_type == ControlPointType.VERTEX:
            return "triangle"
        else:
            return "circle"
    
    def to_dict(self) -> dict:
        """转换为字典格式，用于序列化"""
        return {
            'position': (self.position.x(), self.position.y()),
            'control_type': self.control_type.value,
            'index': self.index,
            'size': self.size,
            'visible': self.visible,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ControlPoint':
        """从字典创建实例，用于反序列化"""
        position = QPointF(data['position'][0], data['position'][1])
        control_type = ControlPointType(data['control_type'])
        index = data.get('index', 0)
        from ..utils.constants import InteractionConstants
        size = data.get('size', InteractionConstants.CONTROL_POINT_DEFAULT_SIZE)
        visible = data.get('visible', True)
        
        cp = cls(position, control_type, index, size)
        cp.set_visible(visible)
        return cp
    
    def __str__(self) -> str:
        return f"ControlPoint({self.control_type.name}, pos=({self.position.x():.1f}, {self.position.y():.1f}))"
    
    def __repr__(self) -> str:
        return self.__str__()
