"""
事件处理基类 - 提供统一的事件处理模式
"""

from abc import ABC, abstractmethod
from typing import Dict, Callable, Any, Optional, List
from .event_bus import EventBus
from .event import Event, EventType
from ..utils.logger import get_logger

logger = get_logger(__name__)


class EventHandlerBase(ABC):
    """事件处理基类 - 提供统一的事件处理模式"""
    
    def __init__(self, event_bus: EventBus):
        """
        初始化事件处理器
        
        Args:
            event_bus: 事件总线
        """
        self.event_bus = event_bus
        self._event_handlers: Dict[EventType, Callable] = {}
        self._subscribed_events: List[EventType] = []
        
        # 注册事件处理器
        self._register_event_handlers()
        
        # 订阅事件
        self._subscribe_events()
    
    @abstractmethod
    def _register_event_handlers(self) -> None:
        """注册事件处理器 - 子类必须实现"""
        pass
    
    def _subscribe_events(self) -> None:
        """订阅事件"""
        for event_type, handler in self._event_handlers.items():
            self.event_bus.subscribe(event_type, handler)
            self._subscribed_events.append(event_type)
    
    def _unsubscribe_events(self) -> None:
        """取消订阅事件"""
        for event_type in self._subscribed_events:
            if event_type in self._event_handlers:
                self.event_bus.unsubscribe(event_type, self._event_handlers[event_type])
        self._subscribed_events.clear()
    
    def register_handler(self, event_type: EventType, handler: Callable) -> None:
        """
        注册事件处理器
        
        Args:
            event_type: 事件类型
            handler: 处理函数
        """
        self._event_handlers[event_type] = handler
        self.event_bus.subscribe(event_type, handler)
        self._subscribed_events.append(event_type)
    
    def unregister_handler(self, event_type: EventType) -> None:
        """
        取消注册事件处理器
        
        Args:
            event_type: 事件类型
        """
        if event_type in self._event_handlers:
            handler = self._event_handlers[event_type]
            self.event_bus.unsubscribe(event_type, handler)
            del self._event_handlers[event_type]
            if event_type in self._subscribed_events:
                self._subscribed_events.remove(event_type)
    
    def get_subscribed_events(self) -> List[EventType]:
        """获取已订阅的事件列表"""
        return self._subscribed_events.copy()
    
    def is_subscribed(self, event_type: EventType) -> bool:
        """检查是否已订阅指定事件"""
        return event_type in self._subscribed_events
    
    def cleanup(self) -> None:
        """清理资源 - 取消所有事件订阅"""
        self._unsubscribe_events()
        self._event_handlers.clear()
    
    def __del__(self):
        """析构函数 - 确保清理资源"""
        try:
            self.cleanup()
        except:
            pass  # 忽略析构时的错误


class SimpleEventHandler(EventHandlerBase):
    """简单事件处理器 - 使用装饰器模式"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self._handler_map: Dict[EventType, str] = {}
    
    def _register_event_handlers(self) -> None:
        """注册事件处理器 - 子类重写此方法"""
        pass
    
    def event_handler(self, event_type: EventType):
        """
        事件处理器装饰器
        
        Args:
            event_type: 事件类型
        """
        def decorator(func):
            self._handler_map[event_type] = func.__name__
            self.register_handler(event_type, func)
            return func
        return decorator
    
    def get_handler_method_name(self, event_type: EventType) -> Optional[str]:
        """获取事件处理器方法名"""
        return self._handler_map.get(event_type)


class BatchEventHandler(EventHandlerBase):
    """批量事件处理器 - 处理多个相关事件"""
    
    def __init__(self, event_bus: EventBus, event_types: List[EventType]):
        """
        初始化批量事件处理器
        
        Args:
            event_bus: 事件总线
            event_types: 要处理的事件类型列表
        """
        self._target_event_types = event_types
        super().__init__(event_bus)
    
    def _register_event_handlers(self) -> None:
        """注册批量事件处理器"""
        for event_type in self._target_event_types:
            self._event_handlers[event_type] = self._handle_batch_event
    
    def _handle_batch_event(self, event: Event) -> None:
        """处理批量事件"""
        try:
            self.on_batch_event(event)
        except Exception as e:
            logger.error(f"批量事件处理失败: {event.event_type.name}, 错误: {e}")
    
    @abstractmethod
    def on_batch_event(self, event: Event) -> None:
        """处理批量事件 - 子类必须实现"""
        pass


class ConditionalEventHandler(EventHandlerBase):
    """条件事件处理器 - 根据条件决定是否处理事件"""
    
    def __init__(self, event_bus: EventBus):
        super().__init__(event_bus)
        self._conditions: Dict[EventType, Callable] = {}
    
    def _register_event_handlers(self) -> None:
        """注册条件事件处理器"""
        pass
    
    def add_conditional_handler(self, event_type: EventType, 
                              condition: Callable[[Event], bool], 
                              handler: Callable[[Event], None]) -> None:
        """
        添加条件事件处理器
        
        Args:
            event_type: 事件类型
            condition: 条件函数
            handler: 处理函数
        """
        self._conditions[event_type] = condition
        
        def conditional_handler(event: Event) -> None:
            if condition(event):
                handler(event)
        
        self.register_handler(event_type, conditional_handler)
    
    def remove_conditional_handler(self, event_type: EventType) -> None:
        """移除条件事件处理器"""
        if event_type in self._conditions:
            del self._conditions[event_type]
        self.unregister_handler(event_type)
