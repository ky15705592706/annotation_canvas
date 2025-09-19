"""
Z轴层级管理器 - 统一处理图形项的Z轴设置
"""

from typing import Any, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ZAxisManager:
    """Z轴层级管理器"""
    
    @staticmethod
    def set_z_order(graphics_item: Any, z_order: int) -> bool:
        """
        设置图形项的Z轴层级
        
        Args:
            graphics_item: PyQtGraph图形项
            z_order: Z轴层级值
            
        Returns:
            bool: 设置是否成功
        """
        if graphics_item is None:
            logger.warning("图形项为None，无法设置Z轴")
            return False
        
        # 验证Z轴层级值
        from ..utils.z_axis_utils import is_valid_z_order, clamp_z_order
        if not is_valid_z_order(z_order):
            logger.warning(f"Z轴层级值 {z_order} 无效，已自动修正")
            z_order = clamp_z_order(z_order)
            
        try:
            # ScatterPlotItem使用z属性
            if hasattr(graphics_item, 'z'):
                graphics_item.z = z_order
                return True
            # 其他图形项使用setZValue方法
            elif hasattr(graphics_item, 'setZValue'):
                graphics_item.setZValue(z_order)
                return True
            else:
                logger.warning(f"图形项不支持Z轴设置: {type(graphics_item)}")
                return False
        except Exception as e:
            logger.error(f"设置Z轴失败: {e}, 图形项类型: {type(graphics_item)}")
            return False
    
    @staticmethod
    def get_z_order(graphics_item: Any) -> Optional[int]:
        """
        获取图形项的Z轴层级
        
        Args:
            graphics_item: PyQtGraph图形项
            
        Returns:
            int: Z轴层级值，如果获取失败返回None
        """
        if graphics_item is None:
            return None
            
        try:
            if hasattr(graphics_item, 'z'):
                return getattr(graphics_item, 'z', None)
            elif hasattr(graphics_item, 'zValue'):
                return graphics_item.zValue()
            else:
                return None
        except Exception as e:
            logger.warning(f"获取Z轴失败: {e}")
            return None
