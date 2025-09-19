"""
输入处理器 - 将原始输入转换为语义化事件
"""

from typing import Optional
from PySide6.QtCore import QPointF
from PySide6.QtGui import QMouseEvent, QKeyEvent, QWheelEvent
from PySide6.QtCore import Qt

from ..events import EventBus, Event, EventType
from ..core import DrawType, DrawColor, PenWidth
from ..utils.logger import get_logger

logger = get_logger(__name__)


class InputHandler:
    """输入处理器 - 将原始输入转换为语义化事件"""
    
    def __init__(self, event_bus: EventBus, canvas_context=None):
        """
        初始化输入处理器
        
        Args:
            event_bus: 事件总线
            canvas_context: 画布上下文，用于获取pixel_size等信息
        """
        self.event_bus = event_bus
        self.canvas_context = canvas_context
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.middle_button_pressed = False
        
        # 鼠标状态跟踪
        self.last_mouse_pos: Optional[QPointF] = None
        self.mouse_dragging = False
        
        # 键盘状态跟踪
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
    
    def _get_pixel_size(self) -> float:
        """获取当前像素大小"""
        if self.canvas_context and hasattr(self.canvas_context, 'getViewBox'):
            try:
                return self.canvas_context.getViewBox().viewPixelSize()[0]
            except:
                pass
        from ..utils.constants import InteractionConstants
        return InteractionConstants.DEFAULT_PIXEL_SIZE
    
    def handle_mouse_press(self, event: QMouseEvent, world_pos: QPointF) -> None:
        """
        处理鼠标按下事件
        
        Args:
            event: 鼠标事件
            world_pos: 世界坐标位置
        """
        button = event.button()
        
        # 更新按钮状态
        if button == Qt.MouseButton.LeftButton:
            self.left_button_pressed = True
        elif button == Qt.MouseButton.RightButton:
            self.right_button_pressed = True
        elif button == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = True
        
        # 更新鼠标位置
        self.last_mouse_pos = world_pos
        
        # 发布鼠标按下事件
        self.event_bus.publish(Event(
            EventType.MOUSE_PRESS,
            {
                'position': world_pos,
                'button': button,
                'left_button_pressed': self.left_button_pressed,
                'right_button_pressed': self.right_button_pressed,
                'middle_button_pressed': self.middle_button_pressed,
                'modifiers': event.modifiers(),
                'ctrl_pressed': self.ctrl_pressed,
                'shift_pressed': self.shift_pressed,
                'alt_pressed': self.alt_pressed,
                'pixel_size': self._get_pixel_size()
            }
        ))
    
    def handle_mouse_move(self, event: QMouseEvent, world_pos: QPointF) -> None:
        """
        处理鼠标移动事件
        
        Args:
            event: 鼠标事件
            world_pos: 世界坐标位置
        """
        # 检查是否开始拖拽
        if self.left_button_pressed and not self.mouse_dragging:
            self.mouse_dragging = True
        
        # 发布鼠标移动事件
        self.event_bus.publish(Event(
            EventType.MOUSE_MOVE,
            {
                'position': world_pos,
                'last_position': self.last_mouse_pos,
                'left_button_pressed': self.left_button_pressed,
                'right_button_pressed': self.right_button_pressed,
                'middle_button_pressed': self.middle_button_pressed,
                'dragging': self.mouse_dragging,
                'modifiers': event.modifiers(),
                'ctrl_pressed': self.ctrl_pressed,
                'shift_pressed': self.shift_pressed,
                'alt_pressed': self.alt_pressed,
                'pixel_size': self._get_pixel_size()
            }
        ))
        
        # 更新鼠标位置
        self.last_mouse_pos = world_pos
    
    def handle_mouse_release(self, event: QMouseEvent, world_pos: QPointF) -> None:
        """
        处理鼠标释放事件
        
        Args:
            event: 鼠标事件
            world_pos: 世界坐标位置
        """
        button = event.button()
        
        # 更新按钮状态
        if button == Qt.MouseButton.LeftButton:
            self.left_button_pressed = False
        elif button == Qt.MouseButton.RightButton:
            self.right_button_pressed = False
        elif button == Qt.MouseButton.MiddleButton:
            self.middle_button_pressed = False
        
        # 发布鼠标释放事件
        self.event_bus.publish(Event(
            EventType.MOUSE_RELEASE,
            {
                'position': world_pos,
                'button': button,
                'left_button_pressed': self.left_button_pressed,
                'right_button_pressed': self.right_button_pressed,
                'middle_button_pressed': self.middle_button_pressed,
                'dragging': self.mouse_dragging,
                'modifiers': event.modifiers(),
                'ctrl_pressed': self.ctrl_pressed,
                'shift_pressed': self.shift_pressed,
                'alt_pressed': self.alt_pressed
            }
        ))
        
        # 重置拖拽状态
        self.mouse_dragging = False
    
    def handle_wheel_event(self, event: QWheelEvent, world_pos: QPointF) -> None:
        """
        处理滚轮事件
        
        Args:
            event: 滚轮事件
            world_pos: 世界坐标位置
        """
        # 发布滚轮事件（可以扩展EventType来支持）
        delta = event.angleDelta().y()
        self.event_bus.publish(Event(
            EventType.MOUSE_MOVE,  # 暂时复用MOUSE_MOVE事件
            {
                'position': world_pos,
                'wheel_delta': delta,
                'wheel_event': True,
                'modifiers': event.modifiers(),
                'ctrl_pressed': self.ctrl_pressed,
                'shift_pressed': self.shift_pressed,
                'alt_pressed': self.alt_pressed
            }
        ))
    
    def handle_key_press(self, event: QKeyEvent) -> None:
        """
        处理键盘按下事件
        
        Args:
            event: 键盘事件
        """
        key = event.key()
        modifiers = event.modifiers()
        
        # 更新修饰键状态
        self.ctrl_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        self.shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        self.alt_pressed = bool(modifiers & Qt.KeyboardModifier.AltModifier)
        
        
        # 只处理非修饰键的键盘事件
        if key not in [Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            # 发布键盘事件（可以扩展EventType来支持）
            self.event_bus.publish(Event(
                EventType.MODE_CHANGED,  # 暂时复用MODE_CHANGED事件
                {
                    'key': key,
                    'text': event.text(),
                    'modifiers': modifiers,
                    'ctrl_pressed': self.ctrl_pressed,
                    'shift_pressed': self.shift_pressed,
                    'alt_pressed': self.alt_pressed,
                    'key_event': True
                }
            ))
    
    def handle_key_release(self, event: QKeyEvent) -> None:
        """
        处理键盘释放事件
        
        Args:
            event: 键盘事件
        """
        key = event.key()
        modifiers = event.modifiers()
        
        # 更新修饰键状态
        self.ctrl_pressed = bool(modifiers & Qt.KeyboardModifier.ControlModifier)
        self.shift_pressed = bool(modifiers & Qt.KeyboardModifier.ShiftModifier)
        self.alt_pressed = bool(modifiers & Qt.KeyboardModifier.AltModifier)
    
    def reset_state(self) -> None:
        """重置输入状态"""
        self.left_button_pressed = False
        self.right_button_pressed = False
        self.middle_button_pressed = False
        self.mouse_dragging = False
        self.last_mouse_pos = None
        self.ctrl_pressed = False
        self.shift_pressed = False
        self.alt_pressed = False
    
    def get_current_state(self) -> dict:
        """
        获取当前输入状态
        
        Returns:
            当前状态字典
        """
        return {
            'left_button_pressed': self.left_button_pressed,
            'right_button_pressed': self.right_button_pressed,
            'middle_button_pressed': self.middle_button_pressed,
            'mouse_dragging': self.mouse_dragging,
            'last_mouse_pos': self.last_mouse_pos,
            'ctrl_pressed': self.ctrl_pressed,
            'shift_pressed': self.shift_pressed,
            'alt_pressed': self.alt_pressed
        }
    
    def cleanup(self) -> None:
        """清理资源"""
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        
        # 取消所有事件订阅
        if hasattr(self, '_event_handlers') and self._event_handlers:
            for event_type, handler in self._event_handlers.items():
                self.event_bus.unsubscribe(event_type, handler)
            self._event_handlers.clear()
        
        # 重置状态
        self.reset_state()
        
