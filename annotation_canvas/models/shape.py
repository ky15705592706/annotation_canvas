"""
图形基类 - 定义所有图形的通用接口和行为
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from PySide6.QtCore import QPointF, QRectF
from ..core.enums import DrawType, DrawColor, PenWidth, ControlPointType
from .control_point import ControlPoint
from ..utils.constants import ZAxisConstants

class BaseShape(ABC):
    """图形基类"""
    
    def __init__(self, shape_type: DrawType, color: DrawColor = DrawColor.RED, 
                 pen_width: PenWidth = PenWidth.MEDIUM, z_order: int = None):
        self.shape_type = shape_type
        self.color = color
        self.pen_width = pen_width
        self.visible = True
        self.selected = False
        self.hovered = False
        self.control_points: List[ControlPoint] = []
        self.graphics_item = None  # PyQtGraph图形项引用
        self.metadata: Dict[str, Any] = {}  # 额外数据存储
        
        # Z轴层级管理
        self.z_order = z_order if z_order is not None else ZAxisConstants.DEFAULT_Z_ORDER
        self._validate_z_order()
        
        # 初始化控制点
        self._initialize_control_points()
    
    @abstractmethod
    def _initialize_control_points(self):
        """初始化控制点 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_bounds(self) -> QRectF:
        """获取图形边界矩形 - 子类必须实现"""
        pass
    
    @abstractmethod
    def contains_point(self, point: QPointF, tolerance: float = None) -> bool:
        """检查点是否在图形内 - 子类必须实现"""
        pass
    
    
    @abstractmethod
    def move_by(self, offset: QPointF):
        """移动图形 - 子类必须实现"""
        pass
    
    @abstractmethod
    def scale_by_control_point(self, control_point: ControlPoint, new_position: QPointF):
        """通过控制点缩放图形 - 子类必须实现"""
        pass
    
    @abstractmethod
    def get_center(self) -> QPointF:
        """获取图形中心点 - 子类必须实现"""
        pass
    
    def set_center(self, center: QPointF) -> None:
        """设置图形中心点（通用实现）"""
        current_center = self.get_center()
        offset = center - current_center
        self.move_by(offset)
    
    def get_control_points(self) -> List[ControlPoint]:
        """获取控制点列表"""
        return self.control_points
    
    def get_control_point_at_position(self, position: QPointF, tolerance: float = None) -> Optional[ControlPoint]:
        """获取指定位置的控制点"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.CONTROL_POINT_TOLERANCE
            
        for cp in self.control_points:
            if cp.contains_point(position, tolerance):
                return cp
        return None
    
    def update_control_points(self):
        """更新控制点位置 - 子类可以重写"""
        pass
    
    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.selected = selected
        for cp in self.control_points:
            cp.set_visible(selected)
    
    def is_selected(self) -> bool:
        """检查是否选中"""
        return self.selected
    
    def set_visible(self, visible: bool):
        """设置可见性"""
        self.visible = visible
    
    def is_visible(self) -> bool:
        """检查是否可见"""
        return self.visible
    
    def set_hovered(self, hovered: bool):
        """设置悬停状态"""
        self.hovered = hovered
    
    def is_hovered(self) -> bool:
        """检查是否悬停"""
        return self.hovered
    
    def set_metadata(self, key: str, value: Any) -> None:
        """设置元数据"""
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """获取元数据"""
        return self.metadata.get(key, default)
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """批量更新元数据"""
        self.metadata.update(metadata)
    
    def clear_metadata(self) -> None:
        """清空元数据"""
        self.metadata.clear()
    
    def _validate_z_order(self) -> None:
        """验证并修正z轴层级值"""
        from ..utils.z_axis_utils import validate_z_order
        self.z_order = validate_z_order(self.z_order)
    
    def set_z_order(self, z_order: int) -> None:
        """设置z轴层级"""
        self.z_order = z_order
        self._validate_z_order()
        self._update_graphics_item_z_order()
    
    def get_z_order(self) -> int:
        """获取z轴层级"""
        return self.z_order
    
    def bring_to_front(self) -> None:
        """将图形置于最前"""
        self.set_z_order(ZAxisConstants.FOREGROUND_Z_ORDER)
    
    def send_to_back(self) -> None:
        """将图形置于最后"""
        self.set_z_order(ZAxisConstants.BACKGROUND_Z_ORDER)
    
    def _update_graphics_item_z_order(self) -> None:
        """
        更新图形项的z轴层级（自动调用）
        
        Note:
            使用ZAxisManager统一处理Z轴设置
        """
        if self.graphics_item is not None:
            from ..render import ZAxisManager
            ZAxisManager.set_z_order(self.graphics_item, self.z_order)
    
    def get_color_rgb(self) -> Tuple[int, int, int]:
        """获取颜色RGB值"""
        color_map = {
            DrawColor.RED: (255, 0, 0),
            DrawColor.GREEN: (0, 255, 0),
            DrawColor.BLUE: (0, 0, 255),
            DrawColor.YELLOW: (255, 255, 0),
            DrawColor.PURPLE: (128, 0, 128),
            DrawColor.ORANGE: (255, 165, 0),
            DrawColor.BLACK: (0, 0, 0),
            DrawColor.WHITE: (255, 255, 255),
        }
        return color_map.get(self.color, (255, 0, 0))
    
    def get_line_width(self) -> int:
        """获取线宽数值"""
        width_map = {
            PenWidth.THIN: 1,
            PenWidth.MEDIUM: 2,
            PenWidth.THICK: 3,
            PenWidth.ULTRA_THIN: 0.5,
            PenWidth.ULTRA_THICK: 5,
        }
        return width_map.get(self.pen_width, 2)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        return {
            'shape_type': self.shape_type.value,
            'color': self.color.value,
            'pen_width': self.pen_width.value,
            'visible': self.visible,
            'selected': self.selected,
            'z_order': self.z_order,
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseShape':
        """从字典创建实例，用于反序列化"""
        # 子类需要实现具体的创建逻辑
        raise NotImplementedError("子类必须实现 from_dict 方法")
    
    def __str__(self) -> str:
        return f"{self.shape_type.name}Shape(color={self.color.name}, width={self.pen_width.name})"
    
    def __repr__(self) -> str:
        return self.__str__()
