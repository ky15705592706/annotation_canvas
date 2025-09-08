"""
渲染策略 - 使用策略模式处理不同图形的渲染
"""

from abc import ABC, abstractmethod
from typing import Optional, Any
from PySide6.QtCore import QPointF

import pyqtgraph as pg
from pyqtgraph import PlotDataItem, ScatterPlotItem

from ..core import DrawType
from ..models import BaseShape, PointShape, RectangleShape, EllipseShape, PolygonShape
from ..utils.constants import DisplayConstants, ColorConstants
from ..utils.geometry import GeometryUtils
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RenderStrategy(ABC):
    """渲染策略基类"""
    
    @abstractmethod
    def create_graphics_item(self, shape: BaseShape) -> Optional[Any]:
        """创建图形项"""
        pass
    
    @abstractmethod
    def update_graphics_item(self, shape: BaseShape, graphics_item: Any) -> bool:
        """更新图形项"""
        pass
    
    @abstractmethod
    def get_shape_type(self) -> DrawType:
        """获取支持的图形类型"""
        pass


class PointRenderStrategy(RenderStrategy):
    """点图形渲染策略"""
    
    def create_graphics_item(self, shape: PointShape) -> ScatterPlotItem:
        """创建点图形项"""
        # 根据悬停状态选择大小和宽度
        if shape.is_hovered():
            size = DisplayConstants.POINT_SIZE_HOVER
            width = DisplayConstants.POINT_WIDTH_HOVER
        else:
            size = DisplayConstants.POINT_SIZE_NORMAL
            width = DisplayConstants.POINT_WIDTH_NORMAL
        
        color = shape.get_color_rgb()
        
        graphics_item = ScatterPlotItem(
            [shape.position.x()], [shape.position.y()],
            size=size, pen=pg.mkPen(color=color, width=width),
            brush=pg.mkBrush(color=color), symbol='o'
        )
        
        # 如果悬停，添加高亮边框
        if shape.is_hovered():
            border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=2)
            graphics_item.setPen(border_pen)
        
        return graphics_item
    
    def update_graphics_item(self, shape: PointShape, graphics_item: ScatterPlotItem) -> bool:
        """更新点图形项"""
        try:
            graphics_item.setData([shape.position.x()], [shape.position.y()])
            
            # 根据悬停状态选择大小和宽度
            if shape.is_hovered():
                size = DisplayConstants.POINT_SIZE_HOVER
                width = DisplayConstants.POINT_WIDTH_HOVER
                border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=2)
            else:
                size = DisplayConstants.POINT_SIZE_NORMAL
                width = DisplayConstants.POINT_WIDTH_NORMAL
                border_pen = None
            
            color = shape.get_color_rgb()
            graphics_item.setPen(pg.mkPen(color=color, width=width))
            graphics_item.setBrush(pg.mkBrush(color=color))
            
            # 如果悬停，添加高亮边框
            if border_pen:
                graphics_item.setPen(border_pen)
            
            return True
        except Exception as e:
            logger.error(f"更新点图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """获取支持的图形类型"""
        return DrawType.POINT


class RectangleRenderStrategy(RenderStrategy):
    """矩形图形渲染策略"""
    
    def create_graphics_item(self, shape: RectangleShape) -> PlotDataItem:
        """创建矩形图形项"""
        color = shape.get_color_rgb()
        
        # 根据悬停状态选择线宽
        if shape.is_hovered():
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
        else:
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
        
        # 获取矩形的四个顶点
        start = shape.get_start_point()
        end = shape.get_end_point()
        
        # 计算矩形的四个角点
        x1, y1 = start.x(), start.y()
        x2, y2 = end.x(), end.y()
        
        # 创建闭合的矩形路径
        x_data = [x1, x2, x2, x1, x1]
        y_data = [y1, y1, y2, y2, y1]
        
        graphics_item = PlotDataItem(
            x_data, y_data,
            pen=pg.mkPen(color=color, width=width),
            connect='all'
        )
        
        # 如果悬停，添加高亮边框
        if shape.is_hovered():
            border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
            graphics_item.setPen(border_pen)
        
        return graphics_item
    
    def update_graphics_item(self, shape: RectangleShape, graphics_item: PlotDataItem) -> bool:
        """更新矩形图形项"""
        try:
            color = shape.get_color_rgb()
            
            # 根据悬停状态选择线宽
            if shape.is_hovered():
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
            else:
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
            
            # 获取矩形的四个顶点
            start = shape.get_start_point()
            end = shape.get_end_point()
            
            # 计算矩形的四个角点
            x1, y1 = start.x(), start.y()
            x2, y2 = end.x(), end.y()
            
            # 创建闭合的矩形路径
            x_data = [x1, x2, x2, x1, x1]
            y_data = [y1, y1, y2, y2, y1]
            
            graphics_item.setData(x_data, y_data)
            
            # 根据悬停状态设置画笔
            if shape.is_hovered():
                border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
                graphics_item.setPen(border_pen)
            else:
                graphics_item.setPen(pg.mkPen(color=color, width=width))
            
            return True
        except Exception as e:
            logger.error(f"更新矩形图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """获取支持的图形类型"""
        return DrawType.RECTANGLE


class EllipseRenderStrategy(RenderStrategy):
    """椭圆图形渲染策略"""
    
    def create_graphics_item(self, shape: EllipseShape) -> PlotDataItem:
        """创建椭圆图形项"""
        color = shape.get_color_rgb()
        
        # 根据悬停状态选择线宽
        if shape.is_hovered():
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
        else:
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
        
        # 获取椭圆的中心点和半径
        center = shape.get_center()
        radius_x = shape.get_radius_x()
        radius_y = shape.get_radius_y()
        
        # 生成椭圆上的点
        points = GeometryUtils.ellipse_points(center, radius_x, radius_y)
        
        if points:
            x_data = [p.x() for p in points]
            y_data = [p.y() for p in points]
            
            graphics_item = PlotDataItem(
                x_data, y_data,
                pen=pg.mkPen(color=color, width=width),
                connect='all'
            )
            
            # 如果悬停，添加高亮边框
            if shape.is_hovered():
                border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
                graphics_item.setPen(border_pen)
            
            return graphics_item
        
        return None
    
    def update_graphics_item(self, shape: EllipseShape, graphics_item: PlotDataItem) -> bool:
        """更新椭圆图形项"""
        try:
            color = shape.get_color_rgb()
            
            # 根据悬停状态选择线宽
            if shape.is_hovered():
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
            else:
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
            
            # 获取椭圆的中心点和半径
            center = shape.get_center()
            radius_x = shape.get_radius_x()
            radius_y = shape.get_radius_y()
            
            # 生成椭圆上的点
            points = GeometryUtils.ellipse_points(center, radius_x, radius_y)
            
            if points:
                x_data = [p.x() for p in points]
                y_data = [p.y() for p in points]
                
                graphics_item.setData(x_data, y_data)
                
                # 根据悬停状态设置画笔
                if shape.is_hovered():
                    border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
                    graphics_item.setPen(border_pen)
                else:
                    graphics_item.setPen(pg.mkPen(color=color, width=width))
                
                return True
            
            return False
        except Exception as e:
            logger.error(f"更新椭圆图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """获取支持的图形类型"""
        return DrawType.ELLIPSE


class PolygonRenderStrategy(RenderStrategy):
    """多边形图形渲染策略"""
    
    def create_graphics_item(self, shape: PolygonShape) -> PlotDataItem:
        """创建多边形图形项"""
        color = shape.get_color_rgb()
        
        # 根据悬停状态选择线宽
        if shape.is_hovered():
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
        else:
            width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
        
        if not shape.vertices:
            return None
        
        # 提取顶点坐标
        x_data = [v.x() for v in shape.vertices]
        y_data = [v.y() for v in shape.vertices]
        
        # 如果是闭合多边形，添加第一个顶点到末尾
        if shape.closed and len(shape.vertices) > 2:
            x_data.append(x_data[0])
            y_data.append(y_data[0])
        
        graphics_item = PlotDataItem(
            x_data, y_data,
            pen=pg.mkPen(color=color, width=width),
            connect='all'
        )
        
        # 如果悬停，添加高亮边框
        if shape.is_hovered():
            border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
            graphics_item.setPen(border_pen)
        
        return graphics_item
    
    def update_graphics_item(self, shape: PolygonShape, graphics_item: PlotDataItem) -> bool:
        """更新多边形图形项"""
        try:
            color = shape.get_color_rgb()
            
            # 根据悬停状态选择线宽
            if shape.is_hovered():
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH + DisplayConstants.HOVER_WIDTH_INCREASE
            else:
                width = DisplayConstants.DEFAULT_GRAPHICS_WIDTH
            
            if not shape.vertices:
                return False
            
            # 提取顶点坐标
            x_data = [v.x() for v in shape.vertices]
            y_data = [v.y() for v in shape.vertices]
            
            # 如果是闭合多边形，添加第一个顶点到末尾
            if shape.closed and len(shape.vertices) > 2:
                x_data.append(x_data[0])
                y_data.append(y_data[0])
            
            graphics_item.setData(x_data, y_data)
            
            # 根据悬停状态设置画笔
            if shape.is_hovered():
                border_pen = pg.mkPen(color=ColorConstants.SHAPE_HOVER, width=width + 2)
                graphics_item.setPen(border_pen)
            else:
                graphics_item.setPen(pg.mkPen(color=color, width=width))
            
            return True
        except Exception as e:
            logger.error(f"更新多边形图形项失败: {e}")
            return False
    
    def get_shape_type(self) -> DrawType:
        """获取支持的图形类型"""
        return DrawType.POLYGON


class RenderStrategyFactory:
    """渲染策略工厂"""
    
    _strategies = {
        DrawType.POINT: PointRenderStrategy(),
        DrawType.RECTANGLE: RectangleRenderStrategy(),
        DrawType.ELLIPSE: EllipseRenderStrategy(),
        DrawType.POLYGON: PolygonRenderStrategy(),
    }
    
    @classmethod
    def get_strategy(cls, shape_type: DrawType) -> Optional[RenderStrategy]:
        """获取渲染策略"""
        return cls._strategies.get(shape_type)
    
    @classmethod
    def get_strategy_for_shape(cls, shape: BaseShape) -> Optional[RenderStrategy]:
        """根据图形对象获取渲染策略"""
        return cls.get_strategy(shape.shape_type)
    
    @classmethod
    def create_graphics_item(cls, shape: BaseShape) -> Optional[Any]:
        """使用策略创建图形项"""
        strategy = cls.get_strategy_for_shape(shape)
        if strategy:
            return strategy.create_graphics_item(shape)
        else:
            logger.warning(f"没有找到图形类型的渲染策略: {shape.shape_type}")
            return None
    
    @classmethod
    def update_graphics_item(cls, shape: BaseShape, graphics_item: Any) -> bool:
        """使用策略更新图形项"""
        strategy = cls.get_strategy_for_shape(shape)
        if strategy:
            return strategy.update_graphics_item(shape, graphics_item)
        else:
            logger.warning(f"没有找到图形类型的渲染策略: {shape.shape_type}")
            return False
    
    @classmethod
    def get_supported_types(cls) -> list:
        """获取支持的图形类型列表"""
        return list(cls._strategies.keys())
    
    @classmethod
    def is_supported_type(cls, shape_type: DrawType) -> bool:
        """检查是否支持指定的图形类型"""
        return shape_type in cls._strategies
