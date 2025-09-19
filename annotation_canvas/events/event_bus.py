"""
事件总线模块
"""

from typing import Any, Dict, List, Callable
from .event import Event, EventType
from ..utils.logger import get_logger
from ..utils.exceptions import EventHandlerError

logger = get_logger(__name__)


class EventBus:
    """事件总线 - 负责事件的发布和订阅"""
    
    def __init__(self):
        """初始化事件总线"""
        self._subscribers: Dict[EventType, List[Callable]] = {}
        self._debug_mode = False
    
    def subscribe(self, event_type: EventType, callback: Callable):
        """
        订阅事件
        
        Args:
            event_type: 要订阅的事件类型
            callback: 事件处理回调函数
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)
            
            if self._debug_mode:
                pass
    
    def unsubscribe(self, event_type: EventType, callback: Callable):
        """
        取消订阅事件
        
        Args:
            event_type: 要取消订阅的事件类型
            callback: 事件处理回调函数
        """
        if event_type in self._subscribers:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                
                if self._debug_mode:
                    pass
    
    def publish(self, event: Event):
        """
        发布事件
        
        Args:
            event: 要发布的事件
        """
        if self._debug_mode:
            pass
        
        if event.type in self._subscribers:
            # 创建回调列表的副本，避免在回调中修改订阅列表
            callbacks = self._subscribers[event.type].copy()
            
            for callback in callbacks:
                try:
                    callback(event)
                except Exception as e:
                    error_msg = f"事件处理错误: {callback.__name__} -> {e}"
                    logger.error(error_msg)
                    import traceback
                    logger.error(traceback.format_exc())
                    
                    # 重新抛出为自定义异常
                    raise EventHandlerError(
                        error_msg, 
                        event_type=event.type.value if hasattr(event.type, 'value') else str(event.type)
                    ) from e
    
    def set_debug_mode(self, enabled: bool):
        """
        设置调试模式
        
        Args:
            enabled: 是否启用调试模式
        """
        self._debug_mode = enabled
    
    def get_subscriber_count(self, event_type: EventType) -> int:
        """
        获取指定事件类型的订阅者数量
        
        Args:
            event_type: 事件类型
            
        Returns:
            订阅者数量
        """
        return len(self._subscribers.get(event_type, []))
    
    def clear_subscribers(self, event_type: EventType = None):
        """
        清除订阅者
        
        Args:
            event_type: 指定的事件类型，如果为None则清除所有
        """
        if event_type is None:
            self._subscribers.clear()
        elif event_type in self._subscribers:
            self._subscribers[event_type].clear()
