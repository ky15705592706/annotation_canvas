"""
事件驱动的数据访问接口
"""

from typing import Optional, List, Any, Callable
from PySide6.QtCore import QPointF, QRectF
from .event import Event, EventType
from .event_bus import EventBus
from ..models import BaseShape
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EventDataAccess:
    """事件驱动的数据访问类"""
    
    def __init__(self, event_bus: EventBus):
        """
        初始化事件数据访问
        
        Args:
            event_bus: 事件总线
        """
        self.event_bus = event_bus
        self._response_handlers = {}
        self._pending_requests = {}
        self._request_id_counter = 0
        
        # 注册响应处理器
        self._register_response_handlers()
    
    def _register_response_handlers(self):
        """注册响应事件处理器"""
        self._response_handlers = {
            EventType.RESPONSE_SHAPE_AT_POSITION: self._handle_shape_at_position_response,
            EventType.RESPONSE_ALL_SHAPES: self._handle_all_shapes_response,
            EventType.RESPONSE_SELECTED_SHAPE: self._handle_selected_shape_response,
            EventType.RESPONSE_HOVERED_SHAPE: self._handle_hovered_shape_response,
            EventType.RESPONSE_SHAPE_BOUNDS: self._handle_shape_bounds_response,
            EventType.RESPONSE_SHAPE_CONTAINS_POINT: self._handle_shape_contains_point_response,
        }
        
        for event_type, handler in self._response_handlers.items():
            self.event_bus.subscribe(event_type, handler)
    
    def _generate_request_id(self) -> str:
        """生成请求ID"""
        self._request_id_counter += 1
        return f"req_{self._request_id_counter}"
    
    def _wait_for_response(self, request_id: str, timeout: float = 1.0) -> Any:
        """等待响应"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if request_id in self._pending_requests:
                response = self._pending_requests.pop(request_id)
                return response
            time.sleep(0.01)  # 避免忙等待
        
        logger.warning(f"请求 {request_id} 超时")
        return None
    
    def get_shape_at_position(self, position: QPointF, tolerance: float = None) -> Optional[BaseShape]:
        """
        获取指定位置的图形
        
        Args:
            position: 位置
            tolerance: 容差
            
        Returns:
            BaseShape: 图形对象，如果没有则返回None
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_SHAPE_AT_POSITION, {
            'request_id': request_id,
            'position': position,
            'tolerance': tolerance
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('shape') if response else None
    
    def get_all_shapes(self) -> List[BaseShape]:
        """
        获取所有图形
        
        Returns:
            List[BaseShape]: 图形列表
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_ALL_SHAPES, {
            'request_id': request_id
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('shapes', []) if response else []
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """
        获取选中的图形
        
        Returns:
            BaseShape: 选中的图形，如果没有则返回None
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_SELECTED_SHAPE, {
            'request_id': request_id
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('shape') if response else None
    
    def get_hovered_shape(self) -> Optional[BaseShape]:
        """
        获取悬停的图形
        
        Returns:
            BaseShape: 悬停的图形，如果没有则返回None
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_HOVERED_SHAPE, {
            'request_id': request_id
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('shape') if response else None
    
    def get_shape_bounds(self, shape: BaseShape) -> Optional[QRectF]:
        """
        获取图形边界
        
        Args:
            shape: 图形对象
            
        Returns:
            QRectF: 边界矩形
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_SHAPE_BOUNDS, {
            'request_id': request_id,
            'shape': shape
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('bounds') if response else None
    
    def shape_contains_point(self, shape: BaseShape, point: QPointF, tolerance: float = None) -> bool:
        """
        检查图形是否包含点
        
        Args:
            shape: 图形对象
            point: 点
            tolerance: 容差
            
        Returns:
            bool: 是否包含
        """
        request_id = self._generate_request_id()
        
        # 发布请求事件
        self.event_bus.publish(Event(EventType.REQUEST_SHAPE_CONTAINS_POINT, {
            'request_id': request_id,
            'shape': shape,
            'point': point,
            'tolerance': tolerance
        }))
        
        # 等待响应
        response = self._wait_for_response(request_id)
        return response.get('contains', False) if response else False
    
    # 响应处理器
    def _handle_shape_at_position_response(self, event: Event):
        """处理位置图形响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data
    
    def _handle_all_shapes_response(self, event: Event):
        """处理所有图形响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data
    
    def _handle_selected_shape_response(self, event: Event):
        """处理选中图形响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data
    
    def _handle_hovered_shape_response(self, event: Event):
        """处理悬停图形响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data
    
    def _handle_shape_bounds_response(self, event: Event):
        """处理图形边界响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data
    
    def _handle_shape_contains_point_response(self, event: Event):
        """处理图形包含点响应"""
        request_id = event.data.get('request_id')
        if request_id:
            self._pending_requests[request_id] = event.data


class EventDataProvider:
    """事件数据提供者"""
    
    def __init__(self, event_bus: EventBus, data_manager):
        """
        初始化事件数据提供者
        
        Args:
            event_bus: 事件总线
            data_manager: 数据管理器
        """
        self.event_bus = event_bus
        self.data_manager = data_manager
        
        # 注册请求处理器
        self._register_request_handlers()
    
    def _register_request_handlers(self):
        """注册请求事件处理器"""
        self.event_bus.subscribe(EventType.REQUEST_SHAPE_AT_POSITION, self._handle_shape_at_position_request)
        self.event_bus.subscribe(EventType.REQUEST_ALL_SHAPES, self._handle_all_shapes_request)
        self.event_bus.subscribe(EventType.REQUEST_SELECTED_SHAPE, self._handle_selected_shape_request)
        self.event_bus.subscribe(EventType.REQUEST_HOVERED_SHAPE, self._handle_hovered_shape_request)
        self.event_bus.subscribe(EventType.REQUEST_SHAPE_BOUNDS, self._handle_shape_bounds_request)
        self.event_bus.subscribe(EventType.REQUEST_SHAPE_CONTAINS_POINT, self._handle_shape_contains_point_request)
    
    def _handle_shape_at_position_request(self, event: Event):
        """处理位置图形请求"""
        request_id = event.data.get('request_id')
        position = event.data.get('position')
        tolerance = event.data.get('tolerance')
        
        shape = self.data_manager.get_shape_at_position(position, tolerance)
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_SHAPE_AT_POSITION, {
            'request_id': request_id,
            'shape': shape
        }))
    
    def _handle_all_shapes_request(self, event: Event):
        """处理所有图形请求"""
        request_id = event.data.get('request_id')
        shapes = self.data_manager.get_shapes()
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_ALL_SHAPES, {
            'request_id': request_id,
            'shapes': shapes
        }))
    
    def _handle_selected_shape_request(self, event: Event):
        """处理选中图形请求"""
        request_id = event.data.get('request_id')
        shape = self.data_manager.get_selected_shape()
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_SELECTED_SHAPE, {
            'request_id': request_id,
            'shape': shape
        }))
    
    def _handle_hovered_shape_request(self, event: Event):
        """处理悬停图形请求"""
        request_id = event.data.get('request_id')
        shape = self.data_manager.get_hovered_shape()
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_HOVERED_SHAPE, {
            'request_id': request_id,
            'shape': shape
        }))
    
    def _handle_shape_bounds_request(self, event: Event):
        """处理图形边界请求"""
        request_id = event.data.get('request_id')
        shape = event.data.get('shape')
        
        bounds = shape.get_bounds() if shape else None
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_SHAPE_BOUNDS, {
            'request_id': request_id,
            'bounds': bounds
        }))
    
    def _handle_shape_contains_point_request(self, event: Event):
        """处理图形包含点请求"""
        request_id = event.data.get('request_id')
        shape = event.data.get('shape')
        point = event.data.get('point')
        tolerance = event.data.get('tolerance')
        
        contains = shape.contains_point(point, tolerance) if shape else False
        
        # 发布响应事件
        self.event_bus.publish(Event(EventType.RESPONSE_SHAPE_CONTAINS_POINT, {
            'request_id': request_id,
            'contains': contains
        }))
