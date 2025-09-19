"""
优化后的渲染策略工厂 - 降低耦合度
"""

from typing import Optional, Dict, Type, Any
from ..core import DrawType
from ..models import BaseShape
from .base_render_strategy import BaseRenderStrategy
from .point_render_strategy import PointRenderStrategy
from .rectangle_render_strategy import RectangleRenderStrategy
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OptimizedRenderFactory:
    """优化后的渲染策略工厂"""
    
    # 策略注册表 - 延迟导入避免循环依赖
    _strategies: Optional[Dict[DrawType, Type[BaseRenderStrategy]]] = None
    
    @classmethod
    def _get_strategies(cls) -> Dict[DrawType, Type[BaseRenderStrategy]]:
        """
        获取策略注册表（延迟加载）
        
        Returns:
            Dict[DrawType, Type[BaseRenderStrategy]]: 策略注册表
        """
        if cls._strategies is None:
            # 延迟导入避免循环依赖
            from .ellipse_render_strategy import EllipseRenderStrategy
            from .polygon_render_strategy import PolygonRenderStrategy
            
            cls._strategies = {
                DrawType.POINT: PointRenderStrategy,
                DrawType.RECTANGLE: RectangleRenderStrategy,
                DrawType.ELLIPSE: EllipseRenderStrategy,
                DrawType.POLYGON: PolygonRenderStrategy,
            }
        return cls._strategies
    
    @classmethod
    def create_graphics_item(cls, shape: BaseShape) -> Optional[Any]:
        """
        创建图形项
        
        Args:
            shape: 图形对象
            
        Returns:
            Optional[Any]: 创建的图形项
        """
        try:
            strategies = cls._get_strategies()
            strategy_class = strategies.get(shape.shape_type)
            
            if strategy_class is None:
                logger.warning(f"不支持的图形类型: {shape.shape_type}")
                return None
            
            # 创建策略实例
            strategy = strategy_class()
            return strategy.create_graphics_item(shape)
            
        except Exception as e:
            logger.error(f"创建图形项失败: {e}")
            return None
    
    @classmethod
    def update_graphics_item(cls, shape: BaseShape, graphics_item: Any) -> bool:
        """
        更新图形项
        
        Args:
            shape: 图形对象
            graphics_item: 图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            strategies = cls._get_strategies()
            strategy_class = strategies.get(shape.shape_type)
            
            if strategy_class is None:
                logger.warning(f"不支持的图形类型: {shape.shape_type}")
                return False
            
            # 创建策略实例
            strategy = strategy_class()
            return strategy.update_graphics_item(shape, graphics_item)
            
        except Exception as e:
            logger.error(f"更新图形项失败: {e}")
            return False
    
    @classmethod
    def register_strategy(cls, shape_type: DrawType, strategy_class: Type[BaseRenderStrategy]) -> None:
        """
        注册新的渲染策略
        
        Args:
            shape_type: 图形类型
            strategy_class: 策略类
        """
        strategies = cls._get_strategies()
        strategies[shape_type] = strategy_class
        logger.info(f"注册渲染策略: {shape_type} -> {strategy_class.__name__}")
    
    @classmethod
    def get_supported_types(cls) -> list:
        """
        获取支持的图形类型列表
        
        Returns:
            list: 支持的图形类型列表
        """
        strategies = cls._get_strategies()
        return list(strategies.keys())
    
    @classmethod
    def is_supported_type(cls, shape_type: DrawType) -> bool:
        """
        检查是否支持指定的图形类型
        
        Args:
            shape_type: 图形类型
            
        Returns:
            bool: 是否支持
        """
        strategies = cls._get_strategies()
        return shape_type in strategies
