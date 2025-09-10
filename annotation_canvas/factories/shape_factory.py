"""
图形工厂 - 负责创建各种类型的图形
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QPointF

from ..core import DrawType, DrawColor, PenWidth
from ..models import BaseShape, PointShape, RectangleShape, EllipseShape, PolygonShape
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ShapeFactory:
    """图形工厂类 - 负责创建各种类型的图形"""
    
    @staticmethod
    def create_shape(shape_type: DrawType, **kwargs) -> Optional[BaseShape]:
        """
        根据类型创建图形
        
        Args:
            shape_type: 图形类型
            **kwargs: 图形参数
            
        Returns:
            创建的图形对象，如果类型不支持则返回None
        """
        try:
            if shape_type == DrawType.POINT:
                return ShapeFactory._create_point(**kwargs)
            elif shape_type == DrawType.RECTANGLE:
                return ShapeFactory._create_rectangle(**kwargs)
            elif shape_type == DrawType.ELLIPSE:
                return ShapeFactory._create_ellipse(**kwargs)
            elif shape_type == DrawType.POLYGON:
                return ShapeFactory._create_polygon(**kwargs)
            else:
                logger.warning(f"不支持的图形类型: {shape_type}")
                return None
                
        except Exception as e:
            logger.error(f"创建图形失败: {e}")
            return None
    
    @staticmethod
    def _create_point(**kwargs) -> PointShape:
        """创建点图形"""
        position = kwargs.get('position', QPointF(0, 0))
        color = kwargs.get('color', DrawColor.RED)
        pen_width = kwargs.get('pen_width', PenWidth.MEDIUM)
        
        return PointShape(position, color, pen_width)
    
    @staticmethod
    def _create_rectangle(**kwargs) -> RectangleShape:
        """创建矩形图形"""
        start_point = kwargs.get('start_point', QPointF(0, 0))
        end_point = kwargs.get('end_point', QPointF(0, 0))
        color = kwargs.get('color', DrawColor.RED)
        pen_width = kwargs.get('pen_width', PenWidth.MEDIUM)
        
        return RectangleShape(start_point, end_point, color, pen_width)
    
    @staticmethod
    def _create_ellipse(**kwargs) -> EllipseShape:
        """创建椭圆图形"""
        start_point = kwargs.get('start_point', QPointF(0, 0))
        end_point = kwargs.get('end_point', QPointF(0, 0))
        color = kwargs.get('color', DrawColor.RED)
        pen_width = kwargs.get('pen_width', PenWidth.MEDIUM)
        
        return EllipseShape(start_point, end_point, color, pen_width)
    
    @staticmethod
    def _create_polygon(**kwargs) -> PolygonShape:
        """创建多边形图形"""
        vertices = kwargs.get('vertices', [])
        color = kwargs.get('color', DrawColor.RED)
        pen_width = kwargs.get('pen_width', PenWidth.MEDIUM)
        
        return PolygonShape(vertices, color, pen_width)
    
    @staticmethod
    def create_from_dict(shape_data: Dict[str, Any]) -> Optional[BaseShape]:
        """
        从字典数据创建图形
        
        Args:
            shape_data: 图形数据字典
            
        Returns:
            创建的图形对象
        """
        try:
            shape_type = DrawType(shape_data.get('shape_type'))
            
            # 提取通用属性
            color = DrawColor(shape_data.get('color', DrawColor.RED.value))
            pen_width = PenWidth(shape_data.get('pen_width', PenWidth.MEDIUM.value))
            
            # 根据类型提取特定参数
            if shape_type == DrawType.POINT:
                position_data = shape_data.get('position', {})
                # 兼容元组格式 (x, y) 和字典格式 {'x': x, 'y': y}
                if isinstance(position_data, (list, tuple)) and len(position_data) >= 2:
                    position = QPointF(position_data[0], position_data[1])
                else:
                    position = QPointF(position_data.get('x', 0), position_data.get('y', 0))
                return ShapeFactory._create_point(position=position, color=color, pen_width=pen_width)
                
            elif shape_type == DrawType.RECTANGLE:
                start_data = shape_data.get('start_point', {})
                end_data = shape_data.get('end_point', {})
                # 兼容元组格式 (x, y) 和字典格式 {'x': x, 'y': y}
                if isinstance(start_data, (list, tuple)) and len(start_data) >= 2:
                    start_point = QPointF(start_data[0], start_data[1])
                else:
                    start_point = QPointF(start_data.get('x', 0), start_data.get('y', 0))
                
                if isinstance(end_data, (list, tuple)) and len(end_data) >= 2:
                    end_point = QPointF(end_data[0], end_data[1])
                else:
                    end_point = QPointF(end_data.get('x', 0), end_data.get('y', 0))
                
                return ShapeFactory._create_rectangle(
                    start_point=start_point, end_point=end_point, 
                    color=color, pen_width=pen_width
                )
                
            elif shape_type == DrawType.ELLIPSE:
                start_data = shape_data.get('start_point', {})
                end_data = shape_data.get('end_point', {})
                # 兼容元组格式 (x, y) 和字典格式 {'x': x, 'y': y}
                if isinstance(start_data, (list, tuple)) and len(start_data) >= 2:
                    start_point = QPointF(start_data[0], start_data[1])
                else:
                    start_point = QPointF(start_data.get('x', 0), start_data.get('y', 0))
                
                if isinstance(end_data, (list, tuple)) and len(end_data) >= 2:
                    end_point = QPointF(end_data[0], end_data[1])
                else:
                    end_point = QPointF(end_data.get('x', 0), end_data.get('y', 0))
                
                return ShapeFactory._create_ellipse(
                    start_point=start_point, end_point=end_point, 
                    color=color, pen_width=pen_width
                )
                
            elif shape_type == DrawType.POLYGON:
                vertices_data = shape_data.get('vertices', [])
                vertices = [QPointF(v.get('x', 0), v.get('y', 0)) for v in vertices_data]
                return ShapeFactory._create_polygon(vertices=vertices, color=color, pen_width=pen_width)
            
            else:
                logger.warning(f"不支持的图形类型: {shape_type}")
                return None
                
        except Exception as e:
            logger.error(f"从字典创建图形失败: {e}")
            return None
    
    @staticmethod
    def get_supported_types() -> list:
        """获取支持的图形类型列表"""
        return [DrawType.POINT, DrawType.RECTANGLE, DrawType.ELLIPSE, DrawType.POLYGON]
    
    @staticmethod
    def is_supported_type(shape_type: DrawType) -> bool:
        """检查是否支持指定的图形类型"""
        return shape_type in ShapeFactory.get_supported_types()
