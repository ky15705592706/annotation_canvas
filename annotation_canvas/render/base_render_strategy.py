"""
基础渲染策略 - 使用泛型降低耦合度
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, TypeVar, Generic
from PySide6.QtCore import QPointF

from ..core import DrawType
from ..models import BaseShape
from .z_axis_manager import ZAxisManager
from .render_utils import create_hover_pen
from ..utils.logger import get_logger

logger = get_logger(__name__)

# 泛型类型变量
T = TypeVar('T', bound=BaseShape)


class BaseRenderStrategy(ABC, Generic[T]):
    """基础渲染策略 - 使用泛型降低耦合度"""
    
    def create_graphics_item(self, shape: T) -> Optional[Any]:
        """
        创建图形项
        
        Args:
            shape: 图形对象
            
        Returns:
            Optional[Any]: 创建的图形项
        """
        try:
            graphics_item = self._create_graphics_item_impl(shape)
            if graphics_item is not None:
                # 统一设置Z轴
                ZAxisManager.set_z_order(graphics_item, shape.get_z_order())
            return graphics_item
        except Exception as e:
            logger.error(f"创建图形项失败: {e}")
            return None
    
    def update_graphics_item(self, shape: T, graphics_item: Any) -> bool:
        """
        更新图形项
        
        Args:
            shape: 图形对象
            graphics_item: 图形项
            
        Returns:
            bool: 更新是否成功
        """
        try:
            success = self._update_graphics_item_impl(shape, graphics_item)
            if success and graphics_item is not None:
                # 统一更新Z轴
                ZAxisManager.set_z_order(graphics_item, shape.get_z_order())
            return success
        except Exception as e:
            logger.error(f"更新图形项失败: {e}")
            return False
    
    @abstractmethod
    def _create_graphics_item_impl(self, shape: T) -> Optional[Any]:
        """
        创建图形项的具体实现
        
        Args:
            shape: 图形对象
            
        Returns:
            Optional[Any]: 创建的图形项
        """
        pass
    
    @abstractmethod
    def _update_graphics_item_impl(self, shape: T, graphics_item: Any) -> bool:
        """
        更新图形项的具体实现
        
        Args:
            shape: 图形对象
            graphics_item: 图形项
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    @abstractmethod
    def get_shape_type(self) -> DrawType:
        """
        获取支持的图形类型
        
        Returns:
            DrawType: 图形类型
        """
        pass
    
    def _apply_hover_effect(self, graphics_item: Any, is_hovered: bool) -> None:
        """
        应用悬停效果
        
        Args:
            graphics_item: 图形项
            is_hovered: 是否悬停
        """
        if graphics_item is None:
            return
            
        try:
            if is_hovered and hasattr(graphics_item, 'setPen'):
                hover_pen = create_hover_pen()
                graphics_item.setPen(hover_pen)
        except Exception as e:
            logger.warning(f"应用悬停效果失败: {e}")
