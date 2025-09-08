"""
数据管理器 - 负责图形数据的CRUD操作
"""

from typing import List, Optional, Dict, Any
from PySide6.QtCore import QPointF

from ..events import EventBus, Event, EventType
from ..core import DrawType, DrawColor, PenWidth
from ..models import BaseShape
from ..factories import ShapeFactory
from ..utils.constants import InteractionConstants
from ..utils.logger import get_logger
from ..utils.exceptions import DataManagerError, ShapeCreationError

logger = get_logger(__name__)


class DataManager:
    """数据管理器 - 专门管理图形数据，负责导入导出"""
    
    def __init__(self, event_bus: EventBus):
        """
        初始化数据管理器
        
        Args:
            event_bus: 事件总线
        """
        self.event_bus = event_bus
        self._shapes: List[BaseShape] = []
        self._selected_shape: Optional[BaseShape] = None
        self._hovered_shape: Optional[BaseShape] = None
        self._temp_shape: Optional[BaseShape] = None
        self._metadata = {
            'version': '1.0',
            'created_time': None,
            'modified_time': None
        }
        
        # 当前工具设置
        self._current_tool = DrawType.POINT
        self._current_color = DrawColor.RED
        self._current_width = PenWidth.MEDIUM
    
    # 图形数据管理
    def add_shape(self, shape: BaseShape) -> None:
        """
        添加图形
        
        Args:
            shape: 要添加的图形
        """
        # 检查是否已经存在相同的图形（防止重复添加）
        if shape in self._shapes:
            logger.warning(f"图形已存在，跳过添加: {shape}")
            return
        
        self._shapes.append(shape)
        self._update_modified_time()
        
        # 发布事件
        self.event_bus.publish(Event(
            EventType.SHAPE_ADDED,
            {'shape': shape, 'index': len(self._shapes) - 1}
        ))
    
    def remove_shape(self, shape: BaseShape) -> bool:
        """
        移除图形
        
        Args:
            shape: 要移除的图形
            
        Returns:
            是否成功移除
        """
        if shape in self._shapes:
            index = self._shapes.index(shape)
            self._shapes.remove(shape)
            self._update_modified_time()
            
            # 如果移除的是选中的图形，清除选择
            if self._selected_shape == shape:
                self.clear_selection()
            
            # 如果移除的是悬停的图形，清除悬停
            if self._hovered_shape == shape:
                self._hovered_shape = None
            
            # 发布事件
            self.event_bus.publish(Event(
                EventType.SHAPE_REMOVED,
                {'shape': shape, 'index': index}
            ))
            return True
        return False
    
    def clear_all_shapes(self) -> None:
        """清空所有图形"""
        removed_shapes = self._shapes.copy()
        self._shapes.clear()
        self._selected_shape = None
        self._hovered_shape = None
        self._temp_shape = None
        self._update_modified_time()
        
        # 发布事件
        for shape in removed_shapes:
            self.event_bus.publish(Event(
                EventType.SHAPE_REMOVED,
                {'shape': shape, 'index': -1}
            ))
    
    def get_shapes(self) -> List[BaseShape]:
        """
        获取所有图形列表（直接引用，请勿修改）
        
        Returns:
            图形列表
        """
        return self._shapes
    
    def get_shape_count(self) -> int:
        """获取图形数量"""
        return len(self._shapes)
    
    # 选择管理
    def select_shape(self, shape: Optional[BaseShape]) -> None:
        """
        选择图形
        
        Args:
            shape: 要选择的图形，None表示清除选择
        """
        old_selected = self._selected_shape
        self._selected_shape = shape
        
        # 发布选择事件
        if old_selected and old_selected != shape:
            self.event_bus.publish(Event(
                EventType.SHAPE_DESELECTED,
                {'shape': old_selected}
            ))
        
        if shape and shape != old_selected:
            self.event_bus.publish(Event(
                EventType.SHAPE_SELECTED,
                {'shape': shape}
            ))
    
    def clear_selection(self) -> None:
        """清除选择"""
        self.select_shape(None)
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """获取选中的图形"""
        return self._selected_shape
    
    # 悬停管理
    def set_hovered_shape(self, shape: Optional[BaseShape]) -> None:
        """
        设置悬停的图形
        
        Args:
            shape: 悬停的图形，None表示清除悬停
        """
        if self._hovered_shape != shape:
            old_hovered = self._hovered_shape
            self._hovered_shape = shape
            
            # 发布悬停变化事件
            self.event_bus.publish(Event(
                EventType.HOVER_CHANGED,
                {'old_shape': old_hovered, 'new_shape': shape}
            ))
    
    def get_hovered_shape(self) -> Optional[BaseShape]:
        """获取悬停的图形"""
        return self._hovered_shape
    
    # 临时图形管理
    def set_temp_shape(self, shape: Optional[BaseShape]) -> None:
        """
        设置临时图形
        
        Args:
            shape: 临时图形，None表示清除临时图形
        """
        self._temp_shape = shape
    
    def get_temp_shape(self) -> Optional[BaseShape]:
        """获取临时图形"""
        return self._temp_shape
    
    # 工具设置
    def set_current_tool(self, tool: DrawType) -> None:
        """设置当前工具"""
        self._current_tool = tool
    
    def get_current_tool(self) -> DrawType:
        """获取当前工具"""
        return self._current_tool
    
    def set_current_color(self, color: DrawColor) -> None:
        """设置当前颜色"""
        self._current_color = color
    
    def get_current_color(self) -> DrawColor:
        """获取当前颜色"""
        return self._current_color
    
    def set_current_width(self, width: PenWidth) -> None:
        """设置当前线宽"""
        self._current_width = width
    
    def get_current_width(self) -> PenWidth:
        """获取当前线宽"""
        return self._current_width
    
    # 交互检测
    def get_hit_target(self, pos: QPointF, pixel_size: float) -> Dict[str, Any]:
        """
        获取指定位置的命中目标
        
        Args:
            pos: 鼠标位置
            pixel_size: 像素大小（用于容差计算）
            
        Returns:
            命中信息字典
        """
        # 检测控制点
        if self._selected_shape:
            cp = self._get_control_point_at(pos, self._selected_shape, pixel_size)
            if cp:
                return {'type': 'control_point', 'target': cp, 'shape': self._selected_shape}
        
        # 检测图形
        shape = self._get_shape_at(pos, pixel_size)
        if shape:
            return {'type': 'shape', 'target': shape}
        
        return {'type': 'none', 'target': None}
    
    def _get_control_point_at(self, pos: QPointF, shape: BaseShape, pixel_size: float) -> Optional[Any]:
        """获取指定位置的控制点"""
        from ..utils.geometry import GeometryUtils
        
        pixel_tolerance = InteractionConstants.CONTROL_POINT_TOLERANCE
        tolerance = pixel_tolerance * pixel_size if pixel_size > 0 else pixel_tolerance
        
        for cp in shape.get_control_points():
            # 使用距离计算而不是简单的坐标差比较
            distance = GeometryUtils.distance_between_points(pos, cp.position)
            if distance <= tolerance:
                return cp
        return None
    
    def _get_shape_at(self, pos: QPointF, pixel_size: float) -> Optional[BaseShape]:
        """获取指定位置的图形"""
        pixel_tolerance = InteractionConstants.PIXEL_TOLERANCE
        tolerance = pixel_tolerance * pixel_size if pixel_size > 0 else pixel_tolerance
        
        # 从后往前检查，优先选择最上层的图形
        for shape in reversed(self._shapes):
            if shape.contains_point_on_boundary(pos, tolerance):
                return shape
        return None
    
    # 数据导入导出
    def export_data(self) -> Dict[str, Any]:
        """
        导出数据
        
        Returns:
            导出的数据字典
        """
        return {
            'shapes': [shape.to_dict() for shape in self._shapes],
            'metadata': self._metadata.copy(),
            'settings': {
                'current_tool': self._current_tool.value,
                'current_color': self._current_color.value,
                'current_width': self._current_width.value
            }
        }
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """
        导入数据
        
        Args:
            data: 要导入的数据字典
            
        Returns:
            是否成功导入
        """
        try:
            # 清空现有数据
            self.clear_all_shapes()
            
            # 导入图形数据
            for shape_data in data.get('shapes', []):
                shape = self._create_shape_from_dict(shape_data)
                if shape:
                    self._shapes.append(shape)
            
            # 导入元数据
            self._metadata.update(data.get('metadata', {}))
            
            # 导入设置
            settings = data.get('settings', {})
            if 'current_tool' in settings:
                self._current_tool = DrawType(settings['current_tool'])
            if 'current_color' in settings:
                self._current_color = DrawColor(settings['current_color'])
            if 'current_width' in settings:
                self._current_width = PenWidth(settings['current_width'])
            
            self._update_modified_time()
            return True
            
        except Exception as e:
            error_msg = f"导入数据失败: {e}"
            logger.error(error_msg)
            raise DataManagerError(error_msg, operation="import_data") from e
    
    def _create_shape_from_dict(self, shape_data: Dict[str, Any]) -> Optional[BaseShape]:
        """从字典数据创建图形"""
        return ShapeFactory.create_from_dict(shape_data)
    
    def _update_modified_time(self) -> None:
        """更新修改时间"""
        import time
        self._metadata['modified_time'] = time.time()
        if not self._metadata.get('created_time'):
            self._metadata['created_time'] = time.time()
