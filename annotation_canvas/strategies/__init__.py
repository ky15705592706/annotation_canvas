"""
策略模块 - 提供各种策略类
"""

from .render_strategy import RenderStrategy, PointRenderStrategy, RectangleRenderStrategy, EllipseRenderStrategy, PolygonRenderStrategy, RenderStrategyFactory

__all__ = [
    'RenderStrategy', 'PointRenderStrategy', 'RectangleRenderStrategy', 
    'EllipseRenderStrategy', 'PolygonRenderStrategy', 'RenderStrategyFactory'
]
