"""
矩形图形渲染策略 - 优化版本
"""

from typing import Optional
from PySide6.QtCore import QPointF
import pyqtgraph as pg
from pyqtgraph import PlotDataItem

from ..core import DrawType
from ..models.rectangle import RectangleShape
from .base_render_strategy import BaseRenderStrategy
from .render_utils import create_pen
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RectangleRenderStrategy(BaseRenderStrategy[RectangleShape]):
    """矩形图形渲染策略 - 优化版本"""
    
    def _create_graphics_item_impl(self, shape: RectangleShape) -> Optional[PlotDataItem]:
        """
        创建矩形图形项的具体实现
        
        Args:
            shape: 矩形图形对象
            
        Returns:
            Optional[PlotDataItem]: 创建的矩形图形项
        """
        try:
            # 获取矩形顶点
            start = shape.get_start_point()
            end = shape.get_end_point()
            
            # 计算矩形的四个角点
            x1, y1 = start.x(), start.y()
            x2, y2 = end.x(), end.y()
            
            # 创建闭合的矩形路径
            x_data = [x1, x2, x2, x1, x1]
            y_data = [y1, y1, y2, y2, y1]
            
            # 创建画笔
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            
            # 创建PlotDataItem
            graphics_item = PlotDataItem(
                x_data, y_data,
                connect='all'
            )
            
            # 设置画笔（确保线宽被正确应用）
            graphics_item.setPen(pen)
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return graphics_item
            
        except Exception as e:
            logger.error(f"创建矩形图形项失败: {e}")
            return None
    
    def _update_graphics_item_impl(self, shape: RectangleShape, graphics_item: PlotDataItem) -> bool:
        """
        更新矩形图形项的具体实现
        
        Args:
            shape: 矩形图形对象
            graphics_item: 矩形图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取矩形顶点
            start = shape.get_start_point()
            end = shape.get_end_point()
            
            # 计算矩形的四个角点
            x1, y1 = start.x(), start.y()
            x2, y2 = end.x(), end.y()
            
            # 创建闭合的矩形路径
            x_data = [x1, x2, x2, x1, x1]
            y_data = [y1, y1, y2, y2, y1]
            
            # 更新数据
            graphics_item.setData(x_data, y_data)
            
            # 更新画笔
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            graphics_item.setPen(pen)
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return True
            
        except Exception as e:
            logger.error(f"更新矩形图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """
        获取支持的图形类型
        
        Returns:
            DrawType: 矩形图形类型
        """
        return DrawType.RECTANGLE
