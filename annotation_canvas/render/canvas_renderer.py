"""
事件驱动的画布渲染器
"""

from typing import Optional, Any
from PySide6.QtCore import QPointF

import pyqtgraph as pg
from pyqtgraph import PlotDataItem, ScatterPlotItem

from ..events import EventBus, Event, EventType, EventHandlerBase
from ..data import DataManager
from ..models import BaseShape
from ..strategies import RenderStrategyFactory
from ..utils.constants import (
    InteractionConstants, DisplayConstants, ColorConstants
)


class CanvasRenderer(EventHandlerBase):
    """事件驱动的画布渲染器"""
    
    def __init__(self, event_bus: EventBus, data_manager: DataManager, canvas):
        """
        初始化渲染器
        
        Args:
            event_bus: 事件总线
            data_manager: 数据管理器
            canvas: 画布对象
        """
        super().__init__(event_bus)
        self.data_manager = data_manager
        self.canvas = canvas
        
        # 图形项缓存
        self._shape_graphics_items = {}  # shape -> graphics_item
        self._control_point_items = {}   # control_point -> graphics_item
        self._temp_graphics_item = None  # 临时图形项（类似旧版本）
    
    def _register_event_handlers(self) -> None:
        """注册事件处理器"""
        self._event_handlers = {
            EventType.SHAPE_ADDED: self._on_shape_added,
            EventType.SHAPE_REMOVED: self._on_shape_removed,
            EventType.SHAPE_SELECTED: self._on_shape_selected,
            EventType.SHAPE_DESELECTED: self._on_shape_deselected,
            EventType.SHAPE_UPDATED: self._on_shape_updated,
            EventType.HOVER_CHANGED: self._on_hover_changed,
            EventType.CONTROL_POINT_HOVER_CHANGED: self._on_control_point_hover_changed,
            EventType.DISPLAY_UPDATE_REQUESTED: self._on_display_update_requested,
        }
    
    def _on_shape_added(self, event: Event) -> None:
        """处理图形添加事件"""
        shape = event.data['shape']
        self._render_shape(shape)
    
    def _on_shape_removed(self, event: Event) -> None:
        """处理图形移除事件"""
        shape = event.data['shape']
        self._remove_shape_from_display(shape)
    
    def _on_shape_selected(self, event: Event) -> None:
        """处理图形选择事件"""
        shape = event.data['shape']
        # 如果图形的图形项不在缓存中，创建它
        if shape not in self._shape_graphics_items:
            self._create_shape_graphics_item(shape)
        # 渲染控制点
        self._render_control_points(shape)
    
    def _on_shape_deselected(self, event: Event) -> None:
        """处理图形取消选择事件"""
        shape = event.data['shape']
        # 如果图形的图形项不在缓存中，创建它
        if shape not in self._shape_graphics_items:
            self._create_shape_graphics_item(shape)
        # 移除控制点
        self._remove_control_points(shape)
    
    def _on_shape_updated(self, event: Event) -> None:
        """处理图形更新事件"""
        shape = event.data['shape']
        self._update_shape_display(shape)
    
    def _on_hover_changed(self, event: Event) -> None:
        """处理悬停变化事件"""
        shape = event.data.get('shape')
        hovered = event.data.get('hovered', False)
        
        if shape:
            self._update_shape_display(shape, hovered=hovered)
    
    def _on_control_point_hover_changed(self, event: Event) -> None:
        """处理控制点悬停变化事件"""
        control_point = event.data['control_point']
        
        # 更新控制点显示
        self._update_control_point_display(control_point)
    
    def _on_display_update_requested(self, event: Event) -> None:
        """处理显示更新请求事件"""
        # 检查是否需要清理临时图形项
        clear_temp = event.data.get('clear_temp', False)
        force_cleanup = event.data.get('force_cleanup', False)
        
        if clear_temp:
            # 清理旧的临时图形项
            if self._temp_graphics_item:
                self.canvas.removeItem(self._temp_graphics_item)
                self._temp_graphics_item = None
            
            # 清理临时图形缓存
            temp_shape = self.data_manager.get_temp_shape()
            if temp_shape and temp_shape in self._shape_graphics_items:
                graphics_item = self._shape_graphics_items[temp_shape]
                self.canvas.removeItem(graphics_item)
                del self._shape_graphics_items[temp_shape]
                temp_shape.graphics_item = None
        
        # 强制清理：移除所有可能残留的临时图形项
        if force_cleanup:
            # 清理所有不在正式图形列表中的图形项
            shapes_to_remove = []
            for shape, graphics_item in self._shape_graphics_items.items():
                if shape not in self.data_manager.get_shapes():
                    shapes_to_remove.append(shape)
            
            for shape in shapes_to_remove:
                graphics_item = self._shape_graphics_items[shape]
                self.canvas.removeItem(graphics_item)
                del self._shape_graphics_items[shape]
                if hasattr(shape, 'graphics_item'):
                    shape.graphics_item = None
        
        # 更新所有显示
        self.update_all_display()
    
    def _render_shape(self, shape: BaseShape) -> None:
        """渲染图形"""
        if shape in self._shape_graphics_items:
            return  # 已经渲染过了
        
        graphics_item = self._create_shape_graphics_item(shape)
        if graphics_item:
            self._shape_graphics_items[shape] = graphics_item
            self.canvas.addItem(graphics_item)
            shape.graphics_item = graphics_item
    
    def _remove_shape_from_display(self, shape: BaseShape) -> None:
        """从显示中移除图形"""
        if shape in self._shape_graphics_items:
            graphics_item = self._shape_graphics_items[shape]
            self.canvas.removeItem(graphics_item)
            del self._shape_graphics_items[shape]
            shape.graphics_item = None
    
    def _create_shape_graphics_item(self, shape: BaseShape) -> Optional[Any]:
        """创建图形图形项"""
        # 使用渲染策略工厂创建图形项
        graphics_item = RenderStrategyFactory.create_graphics_item(shape)
        
        # 注意：不在这里添加到缓存或画布，由调用者负责
        return graphics_item
    
    def _update_shape_display(self, shape: BaseShape, selected: bool = None, hovered: bool = None) -> None:
        """更新图形显示"""
        # 如果图形不在缓存中，创建图形项
        if shape not in self._shape_graphics_items:
            graphics_item = self._create_shape_graphics_item(shape)
            if graphics_item:
                self._shape_graphics_items[shape] = graphics_item
                self.canvas.addItem(graphics_item)
                shape.graphics_item = graphics_item
        
        # 再次检查，确保图形项已创建
        if shape not in self._shape_graphics_items:
            return  # 如果仍然没有，跳过更新
        
        graphics_item = self._shape_graphics_items[shape]
        
        # 使用渲染策略更新图形项
        RenderStrategyFactory.update_graphics_item(shape, graphics_item)
    
    def _render_control_points(self, shape: BaseShape) -> None:
        """渲染控制点"""
        if not shape:
            return
        
        # 清除现有控制点
        self._remove_control_points(shape)
        
        # 渲染新的控制点
        for cp in shape.get_control_points():
            graphics_item = self._create_control_point_graphics_item(cp)
            if graphics_item:
                self._control_point_items[cp] = graphics_item
                self.canvas.addItem(graphics_item)
                cp.graphics_item = graphics_item
    
    def _remove_control_points(self, shape: BaseShape) -> None:
        """移除控制点"""
        if not shape:
            return
        
        for cp in shape.get_control_points():
            if cp in self._control_point_items:
                graphics_item = self._control_point_items[cp]
                self.canvas.removeItem(graphics_item)
                del self._control_point_items[cp]
                cp.graphics_item = None
    
    def _update_control_point_display(self, cp: Any) -> None:
        """更新控制点显示"""
        if cp in self._control_point_items:
            # 移除旧的控制点
            old_graphics_item = self._control_point_items[cp]
            self.canvas.removeItem(old_graphics_item)
            
            # 创建新的控制点（应用新的状态）
            new_graphics_item = self._create_control_point_graphics_item(cp)
            self._control_point_items[cp] = new_graphics_item
            self.canvas.addItem(new_graphics_item)  # 添加新的控制点到画布
            cp.graphics_item = new_graphics_item
    
    def _create_control_point_graphics_item(self, cp: Any) -> ScatterPlotItem:
        """创建控制点图形项"""
        # 根据控制点状态选择大小和宽度
        if cp.hovered:
            size = DisplayConstants.CONTROL_POINT_SIZE_HOVER
            width = DisplayConstants.CONTROL_POINT_WIDTH_HOVER
        else:
            size = DisplayConstants.CONTROL_POINT_SIZE_NORMAL
            width = DisplayConstants.CONTROL_POINT_WIDTH_NORMAL
        
        # 根据控制点类型选择颜色
        color = cp.get_color()
        
        # 创建控制点图形项
        graphics_item = ScatterPlotItem(
            [cp.position.x()], [cp.position.y()],
            size=size, pen=pg.mkPen(color=color, width=width),
            brush=pg.mkBrush(color=color), symbol='s'
        )
        
        # 如果悬停，添加黑色边框
        if cp.hovered:
            border_pen = pg.mkPen(color=ColorConstants.CONTROL_POINT_HOVER, width=1)
            graphics_item.setPen(border_pen)
        
        return graphics_item
    
    def update_all_display(self) -> None:
        """更新所有显示"""
        # 更新所有图形
        for shape in self.data_manager.get_shapes():
            self._update_shape_display(shape)
        
        # 更新临时图形（只有在临时图形存在且不在正式图形列表中时才显示）
        temp_shape = self.data_manager.get_temp_shape()
        if temp_shape and temp_shape not in self.data_manager.get_shapes():
            self._update_shape_display(temp_shape)
        
        # 更新选中图形的控制点
        selected_shape = self.data_manager.get_selected_shape()
        if selected_shape:
            self._render_control_points(selected_shape)
    
    def cleanup(self) -> None:
        """清理资源"""
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        logger.debug("渲染器开始清理资源")
        
        # 取消所有事件订阅
        if hasattr(self, '_event_handlers') and self._event_handlers:
            for event_type, handler in self._event_handlers.items():
                self.event_bus.unsubscribe(event_type, handler)
            self._event_handlers.clear()
        
        # 清理图形项缓存
        self._shape_graphics_items.clear()
        self._control_point_items.clear()
        self._temp_graphics_item = None
        
        logger.debug("渲染器资源清理完成")