"""
渲染模块 - 负责图形的渲染显示
"""

from .canvas_renderer import CanvasRenderer

# 优化后的渲染组件
from .z_axis_manager import ZAxisManager
from .render_utils import (
    get_color_rgb, get_line_width, create_pen, create_brush, 
    create_hover_pen, get_point_size, get_point_width
)
from .base_render_strategy import BaseRenderStrategy
from .optimized_render_factory import OptimizedRenderFactory

__all__ = [
    'CanvasRenderer',
    'ZAxisManager',
    'get_color_rgb', 'get_line_width', 'create_pen', 'create_brush', 
    'create_hover_pen', 'get_point_size', 'get_point_width',
    'BaseRenderStrategy',
    'OptimizedRenderFactory'
]
