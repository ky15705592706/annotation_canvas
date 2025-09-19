"""
多边形图形渲染策略 - 优化版本
"""

from typing import Optional, List
from PySide6.QtCore import QPointF
import pyqtgraph as pg
from pyqtgraph import PlotDataItem

from ..core import DrawType
from ..models.polygon import PolygonShape
from .base_render_strategy import BaseRenderStrategy
from .render_utils import create_pen
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PolygonRenderStrategy(BaseRenderStrategy[PolygonShape]):
    """多边形图形渲染策略 - 优化版本"""
    
    def _create_graphics_item_impl(self, shape: PolygonShape) -> Optional[PlotDataItem]:
        """
        创建多边形图形项的具体实现
        
        Args:
            shape: 多边形图形对象
            
        Returns:
            Optional[PlotDataItem]: 创建的多边形图形项
        """
        try:
            # 获取多边形顶点
            vertices = shape.get_vertices()
            if len(vertices) < 2:
                logger.warning("多边形顶点数量不足")
                return None
            
            # 生成多边形点数据
            x_data, y_data = self._generate_polygon_points(vertices, shape.closed)
            
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
            logger.error(f"创建多边形图形项失败: {e}")
            return None
    
    def _update_graphics_item_impl(self, shape: PolygonShape, graphics_item: PlotDataItem) -> bool:
        """
        更新多边形图形项的具体实现
        
        Args:
            shape: 多边形图形对象
            graphics_item: 多边形图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取多边形顶点
            vertices = shape.get_vertices()
            if len(vertices) < 2:
                logger.warning("多边形顶点数量不足")
                return False
            
            # 生成多边形点数据
            x_data, y_data = self._generate_polygon_points(vertices, shape.closed)
            
            # 更新数据
            graphics_item.setData(x_data, y_data)
            
            # 更新画笔
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            graphics_item.setPen(pen)
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return True
            
        except Exception as e:
            logger.error(f"更新多边形图形项失败: {e}")
            return False
    
    def _generate_polygon_points(self, vertices: List[QPointF], is_closed: bool) -> tuple:
        """
        生成多边形点数据
        
        Args:
            vertices: 顶点列表
            is_closed: 是否闭合
            
        Returns:
            tuple: (x_data, y_data) 多边形点数据
        """
        x_data = [vertex.x() for vertex in vertices]
        y_data = [vertex.y() for vertex in vertices]
        
        # 如果闭合，添加起始点
        if is_closed and len(vertices) > 2:
            x_data.append(vertices[0].x())
            y_data.append(vertices[0].y())
        
        return x_data, y_data
    
    def get_shape_type(self) -> DrawType:
        """
        获取支持的图形类型
        
        Returns:
            DrawType: 多边形图形类型
        """
        return DrawType.POLYGON
