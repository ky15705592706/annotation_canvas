"""
点图形渲染策略 - 优化版本
"""

from typing import Optional
from PySide6.QtCore import QPointF
import pyqtgraph as pg
from pyqtgraph import ScatterPlotItem

from ..core import DrawType
from ..models.point import PointShape
from .base_render_strategy import BaseRenderStrategy
from .render_utils import get_point_size, get_point_width, create_pen, create_brush
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PointRenderStrategy(BaseRenderStrategy[PointShape]):
    """点图形渲染策略 - 优化版本"""
    
    def _create_graphics_item_impl(self, shape: PointShape) -> Optional[ScatterPlotItem]:
        """
        创建点图形项的具体实现
        
        Args:
            shape: 点图形对象
            
        Returns:
            Optional[ScatterPlotItem]: 创建的点图形项
        """
        try:
            # 获取渲染属性
            size = get_point_size(shape.is_hovered())
            width = get_point_width(shape.pen_width, shape.is_hovered())
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            brush = create_brush(shape.color)
            
            # 创建ScatterPlotItem
            graphics_item = ScatterPlotItem(
                [shape.position.x()], [shape.position.y()],
                size=size, pen=pen, brush=brush, symbol='o'
            )
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return graphics_item
            
        except Exception as e:
            logger.error(f"创建点图形项失败: {e}")
            return None
    
    def _update_graphics_item_impl(self, shape: PointShape, graphics_item: ScatterPlotItem) -> bool:
        """
        更新点图形项的具体实现
        
        Args:
            shape: 点图形对象
            graphics_item: 点图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 更新位置
            graphics_item.setData([shape.position.x()], [shape.position.y()])
            
            # 更新渲染属性
            size = get_point_size(shape.is_hovered())
            width = get_point_width(shape.pen_width, shape.is_hovered())
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            brush = create_brush(shape.color)
            
            # 应用属性
            graphics_item.setPen(pen)
            graphics_item.setBrush(brush)
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return True
            
        except Exception as e:
            logger.error(f"更新点图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """
        获取支持的图形类型
        
        Returns:
            DrawType: 点图形类型
        """
        return DrawType.POINT
