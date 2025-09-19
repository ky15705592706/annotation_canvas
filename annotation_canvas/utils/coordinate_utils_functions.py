"""
坐标转换工具函数 - 简化的坐标转换功能
"""

from typing import Dict, Any, Tuple, List
from PySide6.QtCore import QPointF


def qpointf_to_dict(point: QPointF) -> Dict[str, float]:
    """将QPointF转换为字典"""
    return {'x': point.x(), 'y': point.y()}


def dict_to_qpointf(data: Dict[str, float]) -> QPointF:
    """将字典转换为QPointF"""
    return QPointF(data.get('x', 0.0), data.get('y', 0.0))


def qpointf_to_tuple(point: QPointF) -> Tuple[float, float]:
    """将QPointF转换为元组"""
    return (point.x(), point.y())


def tuple_to_qpointf(point_tuple: Tuple[float, float]) -> QPointF:
    """将元组转换为QPointF"""
    return QPointF(point_tuple[0], point_tuple[1])


def points_to_dict_list(points: List[QPointF]) -> List[Dict[str, float]]:
    """将QPointF列表转换为字典列表"""
    return [qpointf_to_dict(point) for point in points]


def dict_list_to_points(data_list: List[Dict[str, float]]) -> List[QPointF]:
    """将字典列表转换为QPointF列表"""
    return [dict_to_qpointf(data) for data in data_list]
