"""
椭圆图形渲染策略 - 优化版本
"""

from typing import Optional
from PySide6.QtCore import QPointF
import pyqtgraph as pg
from pyqtgraph import PlotDataItem

from ..core import DrawType
from ..models.ellipse import EllipseShape
from .base_render_strategy import BaseRenderStrategy
from .render_utils import create_pen
from ..utils.constants import DisplayConstants
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EllipseRenderStrategy(BaseRenderStrategy[EllipseShape]):
    """椭圆图形渲染策略 - 优化版本"""
    
    def _create_graphics_item_impl(self, shape: EllipseShape) -> Optional[PlotDataItem]:
        """
        创建椭圆图形项的具体实现
        
        Args:
            shape: 椭圆图形对象
            
        Returns:
            Optional[PlotDataItem]: 创建的椭圆图形项
        """
        try:
            # 获取椭圆边界
            start = shape.get_start_point()
            end = shape.get_end_point()
            
            # 计算椭圆中心点和半径
            center_x = (start.x() + end.x()) / 2
            center_y = (start.y() + end.y()) / 2
            radius_x = abs(end.x() - start.x()) / 2
            radius_y = abs(end.y() - start.y()) / 2
            
            # 生成椭圆点
            points_count = DisplayConstants.ELLIPSE_POINTS_COUNT
            x_data, y_data = self._generate_ellipse_points(
                center_x, center_y, radius_x, radius_y, points_count
            )
            
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
            logger.error(f"创建椭圆图形项失败: {e}")
            return None
    
    def _update_graphics_item_impl(self, shape: EllipseShape, graphics_item: PlotDataItem) -> bool:
        """
        更新椭圆图形项的具体实现
        
        Args:
            shape: 椭圆图形对象
            graphics_item: 椭圆图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            # 获取椭圆边界
            start = shape.get_start_point()
            end = shape.get_end_point()
            
            # 计算椭圆中心点和半径
            center_x = (start.x() + end.x()) / 2
            center_y = (start.y() + end.y()) / 2
            radius_x = abs(end.x() - start.x()) / 2
            radius_y = abs(end.y() - start.y()) / 2
            
            # 生成椭圆点
            points_count = DisplayConstants.ELLIPSE_POINTS_COUNT
            x_data, y_data = self._generate_ellipse_points(
                center_x, center_y, radius_x, radius_y, points_count
            )
            
            # 更新数据
            graphics_item.setData(x_data, y_data)
            
            # 更新画笔
            pen = create_pen(shape.color, shape.pen_width, shape.is_hovered())
            graphics_item.setPen(pen)
            
            # 应用悬停效果
            self._apply_hover_effect(graphics_item, shape.is_hovered())
            
            return True
            
        except Exception as e:
            logger.error(f"更新椭圆图形项失败: {e}")
            return False
    
    def _generate_ellipse_points(self, center_x: float, center_y: float, 
                                radius_x: float, radius_y: float, points_count: int) -> tuple:
        """
        生成椭圆点数据
        
        Args:
            center_x: 中心点X坐标
            center_y: 中心点Y坐标
            radius_x: X轴半径
            radius_y: Y轴半径
            points_count: 点数
            
        Returns:
            tuple: (x_data, y_data) 椭圆点数据
        """
        import math
        
        x_data = []
        y_data = []
        
        for i in range(points_count + 1):  # +1 确保闭合
            angle = 2 * math.pi * i / points_count
            x = center_x + radius_x * math.cos(angle)
            y = center_y + radius_y * math.sin(angle)
            x_data.append(x)
            y_data.append(y)
        
        return x_data, y_data
    
    def get_shape_type(self) -> DrawType:
        """
        获取支持的图形类型
        
        Returns:
            DrawType: 椭圆图形类型
        """
        return DrawType.ELLIPSE
