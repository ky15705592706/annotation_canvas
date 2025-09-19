# This Python file uses the following encoding: utf-8

"""
工具模块 - 提供通用工具函数
"""

from .geometry import GeometryUtils
from .math_utils import MathUtils
from .config import Config
from .logger import get_logger
from .z_axis_utils import validate_z_order, is_valid_z_order, get_z_order_range, clamp_z_order
from .coordinate_utils_functions import (
    qpointf_to_dict, dict_to_qpointf, qpointf_to_tuple, tuple_to_qpointf,
    points_to_dict_list, dict_list_to_points
)
from .exceptions import (
    AnnotationError, ShapeCreationError, ShapeOperationError,
    EventHandlerError, ConfigError, DataManagerError,
    StateManagerError, RenderError, ValidationError
)

__all__ = [
    'GeometryUtils', 'MathUtils', 'Config', 'get_logger',
    'validate_z_order', 'is_valid_z_order', 'get_z_order_range', 'clamp_z_order',
    'qpointf_to_dict', 'dict_to_qpointf', 'qpointf_to_tuple', 'tuple_to_qpointf',
    'points_to_dict_list', 'dict_list_to_points',
    'AnnotationError', 'ShapeCreationError', 'ShapeOperationError',
    'EventHandlerError', 'ConfigError', 'DataManagerError',
    'StateManagerError', 'RenderError', 'ValidationError'
]
