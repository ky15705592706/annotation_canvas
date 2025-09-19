"""
Z轴工具函数 - 简化的Z轴验证功能
"""

from .constants import ZAxisConstants
from .logger import get_logger

logger = get_logger(__name__)


def validate_z_order(z_order: int) -> int:
    """验证并修正Z轴层级值"""
    if z_order < ZAxisConstants.MIN_Z_ORDER:
        logger.warning(f"Z轴层级值 {z_order} 小于最小值 {ZAxisConstants.MIN_Z_ORDER}，已修正")
        return ZAxisConstants.MIN_Z_ORDER
    elif z_order > ZAxisConstants.MAX_Z_ORDER:
        logger.warning(f"Z轴层级值 {z_order} 大于最大值 {ZAxisConstants.MAX_Z_ORDER}，已修正")
        return ZAxisConstants.MAX_Z_ORDER
    else:
        return z_order


def is_valid_z_order(z_order: int) -> bool:
    """检查Z轴层级值是否有效"""
    return ZAxisConstants.MIN_Z_ORDER <= z_order <= ZAxisConstants.MAX_Z_ORDER


def get_z_order_range() -> tuple:
    """获取Z轴层级范围"""
    return (ZAxisConstants.MIN_Z_ORDER, ZAxisConstants.MAX_Z_ORDER)


def clamp_z_order(z_order: int) -> int:
    """将Z轴层级值限制在有效范围内"""
    return max(ZAxisConstants.MIN_Z_ORDER, 
              min(ZAxisConstants.MAX_Z_ORDER, z_order))
