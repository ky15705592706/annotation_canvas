"""
事件定义模块
"""

import time
from enum import Enum
from typing import Any, Dict


class EventType(Enum):
    """事件类型枚举"""
    # 鼠标事件
    MOUSE_PRESS = "mouse_press"
    MOUSE_MOVE = "mouse_move"
    MOUSE_RELEASE = "mouse_release"
    
    # 数据事件
    SHAPE_ADDED = "shape_added"
    SHAPE_REMOVED = "shape_removed"
    SHAPE_SELECTED = "shape_selected"
    SHAPE_DESELECTED = "shape_deselected"
    SHAPE_UPDATED = "shape_updated"
    
    # 数据查询事件
    REQUEST_SHAPE_AT_POSITION = "request_shape_at_position"
    REQUEST_ALL_SHAPES = "request_all_shapes"
    REQUEST_SELECTED_SHAPE = "request_selected_shape"
    REQUEST_HOVERED_SHAPE = "request_hovered_shape"
    REQUEST_SHAPE_BOUNDS = "request_shape_bounds"
    REQUEST_SHAPE_CONTAINS_POINT = "request_shape_contains_point"
    
    # 数据响应事件
    RESPONSE_SHAPE_AT_POSITION = "response_shape_at_position"
    RESPONSE_ALL_SHAPES = "response_all_shapes"
    RESPONSE_SELECTED_SHAPE = "response_selected_shape"
    RESPONSE_HOVERED_SHAPE = "response_hovered_shape"
    RESPONSE_SHAPE_BOUNDS = "response_shape_bounds"
    RESPONSE_SHAPE_CONTAINS_POINT = "response_shape_contains_point"
    
    # 状态事件
    STATE_CHANGED = "state_changed"
    MODE_CHANGED = "mode_changed"
    
    # 渲染事件
    DISPLAY_UPDATE_REQUESTED = "display_update_requested"
    HOVER_CHANGED = "hover_changed"
    CONTROL_POINT_HOVER_CHANGED = "control_point_hover_changed"
    
    # 确认事件
    CONFIRM_CANCEL_POLYGON = "confirm_cancel_polygon"
    CANCEL_POLYGON_CONFIRMED = "cancel_polygon_confirmed"
    
    # 操作事件
    OPERATION_EXECUTED = "operation_executed"
    OPERATION_UNDONE = "operation_undone"
    OPERATION_REDONE = "operation_redone"
    
    # 工具设置事件
    TOOL_CHANGED = "tool_changed"
    COLOR_CHANGED = "color_changed"
    WIDTH_CHANGED = "width_changed"


class Event:
    """基础事件类"""
    
    def __init__(self, event_type: EventType, data: Dict[str, Any] = None):
        """
        初始化事件
        
        Args:
            event_type: 事件类型
            data: 事件数据字典
        """
        self.type = event_type
        self.data = data or {}
        self.timestamp = time.time()
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"Event({self.type.value}, {self.data})"
    
    def __repr__(self) -> str:
        """调试表示"""
        return f"Event(type={self.type}, data={self.data}, timestamp={self.timestamp})"
