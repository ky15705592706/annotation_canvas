"""
渲染属性管理器 - 统一管理图形渲染属性
"""

from typing import Tuple, Optional, Any
from PySide6.QtCore import QPointF
import pyqtgraph as pg

from ..core import DrawColor, PenWidth
from ..utils.constants import DisplayConstants, ColorConstants
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RenderProperties:
    """渲染属性管理器"""
    
    @staticmethod
    def get_color_rgb(color: DrawColor) -> Tuple[int, int, int]:
        """
        获取颜色的RGB值
        
        Args:
            color: 颜色枚举
            
        Returns:
            Tuple[int, int, int]: RGB值
        """
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
        return color_map.get(color, (255, 0, 0))
    
    @staticmethod
    def get_line_width(pen_width: PenWidth) -> int:
        """
        获取线宽数值
        
        Args:
            pen_width: 线宽枚举
            
        Returns:
            int: 线宽数值
        """
        width_map = {
            PenWidth.THIN: 1,
            PenWidth.MEDIUM: 2,
            PenWidth.THICK: 3,
            PenWidth.ULTRA_THIN: 0.5,
            PenWidth.ULTRA_THICK: 5,
        }
        return width_map.get(pen_width, 2)
    
    @staticmethod
    def create_pen(color: DrawColor, pen_width: PenWidth, is_hovered: bool = False) -> pg.mkPen:
        """
        创建画笔
        
        Args:
            color: 颜色
            pen_width: 线宽
            is_hovered: 是否悬停
            
        Returns:
            pg.mkPen: PyQtGraph画笔对象
        """
        rgb_color = RenderProperties.get_color_rgb(color)
        width = RenderProperties.get_line_width(pen_width)
        
        if is_hovered:
            width += DisplayConstants.HOVER_WIDTH_INCREASE
        
        return pg.mkPen(color=rgb_color, width=width)
    
    @staticmethod
    def create_brush(color: DrawColor) -> pg.mkBrush:
        """
        创建画刷
        
        Args:
            color: 颜色
            
        Returns:
            pg.mkBrush: PyQtGraph画刷对象
        """
        rgb_color = RenderProperties.get_color_rgb(color)
        return pg.mkBrush(color=rgb_color)
    
    @staticmethod
    def create_hover_pen() -> pg.mkPen:
        """
        创建悬停高亮画笔
        
        Returns:
            pg.mkPen: 悬停高亮画笔
        """
        return pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=2)
    
    @staticmethod
    def get_point_size(is_hovered: bool = False) -> float:
        """
        获取点图形大小
        
        Args:
            is_hovered: 是否悬停
            
        Returns:
            float: 点图形大小
        """
        if is_hovered:
            return DisplayConstants.POINT_SIZE_HOVER
        else:
            return DisplayConstants.POINT_SIZE_NORMAL
    
    @staticmethod
    def get_point_width(is_hovered: bool = False) -> int:
        """
        获取点图形线宽
        
        Args:
            is_hovered: 是否悬停
            
        Returns:
            int: 点图形线宽
        """
        if is_hovered:
            return DisplayConstants.POINT_WIDTH_HOVER
        else:
            return DisplayConstants.POINT_WIDTH_NORMAL
