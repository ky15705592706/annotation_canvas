"""
渲染工具函数 - 简化的渲染相关工具
"""

from typing import Tuple
import pyqtgraph as pg

from ..core import DrawColor, PenWidth
from ..utils.constants import DisplayConstants, ColorConstants


# 颜色RGB映射常量
COLOR_RGB_MAP = {
    DrawColor.RED: (255, 0, 0),
    DrawColor.GREEN: (0, 255, 0),
    DrawColor.BLUE: (0, 0, 255),
    DrawColor.YELLOW: (255, 255, 0),
    DrawColor.PURPLE: (128, 0, 128),
    DrawColor.ORANGE: (255, 165, 0),
    DrawColor.BLACK: (0, 0, 0),
    DrawColor.WHITE: (255, 255, 255),
}

# 线宽映射常量
PEN_WIDTH_MAP = {
    PenWidth.THIN: 2,
    PenWidth.MEDIUM: 4,
    PenWidth.THICK: 6,
    PenWidth.ULTRA_THIN: 1,
    PenWidth.ULTRA_THICK: 8,
}


def get_color_rgb(color: DrawColor) -> Tuple[int, int, int]:
    """获取颜色的RGB值"""
    return COLOR_RGB_MAP.get(color, (255, 0, 0))


def get_line_width(pen_width: PenWidth) -> int:
    """获取线宽数值"""
    return PEN_WIDTH_MAP.get(pen_width, 2)


def create_pen(color: DrawColor, pen_width: PenWidth, is_hovered: bool = False) -> pg.mkPen:
    """创建画笔"""
    rgb_color = get_color_rgb(color)
    width = get_line_width(pen_width)
    
    if is_hovered:
        width += DisplayConstants.HOVER_WIDTH_INCREASE
    
    return pg.mkPen(color=rgb_color, width=width)


def create_brush(color: DrawColor) -> pg.mkBrush:
    """创建画刷"""
    rgb_color = get_color_rgb(color)
    return pg.mkBrush(color=rgb_color)


def create_hover_pen() -> pg.mkPen:
    """创建悬停高亮画笔"""
    return pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=2)


def get_point_size(is_hovered: bool = False) -> float:
    """获取点图形大小"""
    if is_hovered:
        return DisplayConstants.POINT_SIZE_HOVER
    else:
        return DisplayConstants.POINT_SIZE_NORMAL


def get_point_width(pen_width: PenWidth = None, is_hovered: bool = False) -> int:
    """获取点图形线宽"""
    if pen_width is not None:
        # 使用图形的线宽设置
        base_width = get_line_width(pen_width)
        if is_hovered:
            return base_width + DisplayConstants.HOVER_WIDTH_INCREASE
        else:
            return base_width
    else:
        # 使用默认线宽设置（向后兼容）
        if is_hovered:
            return DisplayConstants.POINT_WIDTH_HOVER
        else:
            return DisplayConstants.POINT_WIDTH_NORMAL
