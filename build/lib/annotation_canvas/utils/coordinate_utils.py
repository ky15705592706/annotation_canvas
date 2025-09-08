"""
坐标转换工具 - 提供通用的坐标转换功能
"""

from typing import Dict, Any, Tuple
from PySide6.QtCore import QPointF


class CoordinateUtils:
    """坐标转换工具类"""
    
    @staticmethod
    def qpointf_to_dict(point: QPointF) -> Dict[str, float]:
        """将QPointF转换为字典"""
        return {'x': point.x(), 'y': point.y()}
    
    @staticmethod
    def dict_to_qpointf(data: Dict[str, float]) -> QPointF:
        """将字典转换为QPointF"""
        return QPointF(data.get('x', 0.0), data.get('y', 0.0))
    
    @staticmethod
    def qpointf_to_tuple(point: QPointF) -> Tuple[float, float]:
        """将QPointF转换为元组"""
        return (point.x(), point.y())
    
    @staticmethod
    def tuple_to_qpointf(point_tuple: Tuple[float, float]) -> QPointF:
        """将元组转换为QPointF"""
        return QPointF(point_tuple[0], point_tuple[1])
    
    @staticmethod
    def points_to_dict_list(points: list) -> list:
        """将QPointF列表转换为字典列表"""
        return [CoordinateUtils.qpointf_to_dict(point) for point in points]
    
    @staticmethod
    def dict_list_to_points(data_list: list) -> list:
        """将字典列表转换为QPointF列表"""
        return [CoordinateUtils.dict_to_qpointf(data) for data in data_list]
