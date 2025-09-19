"""
改进的注解控制器 - 使用依赖注入和事件驱动架构
"""

from typing import Optional, List
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QWheelEvent

from ..events import EventBus, Event, EventType, EventDataAccess, EventDataProvider
from ..data import DataManager
from ..input import InputHandler
from ..state import StateManager
from ..render import CanvasRenderer
from ..core import DrawType, DrawColor, PenWidth, OperationState
from ..models import BaseShape
from ..operations import OperationManager
from ..di import DIContainer
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnnotationController:
    """AnnotationController - 使用依赖注入和事件驱动架构的注解控制器"""
    
    def __init__(self, canvas, container: DIContainer = None):
        """
        初始化改进的控制器
        
        Args:
            canvas: 画布对象
            container: 依赖注入容器（可选）
        """
        self.canvas = canvas
        
        # 创建或使用提供的依赖注入容器
        self.container = container or DIContainer()
        
        # 注册服务到容器
        self._register_services()
        
        # 获取服务实例
        self.event_bus = self.container.get(EventBus)
        self.data_manager = self.container.get(DataManager)
        self.input_handler = self.container.get(InputHandler)
        self.state_manager = self.container.get(StateManager)
        self.renderer = self.container.get(CanvasRenderer)
        self.operation_manager = self.container.get(OperationManager)
        
        # 创建事件数据访问
        self.data_access = EventDataAccess(self.event_bus)
        self.data_provider = EventDataProvider(self.event_bus, self.data_manager)
        
        # 设置调试模式
        self.event_bus.set_debug_mode(False)
        
        # 订阅全局事件
        self._subscribe_global_events()
        
    
    def _register_services(self):
        """注册服务到依赖注入容器"""
        # 注册事件总线（单例）
        self.container.register_instance(EventBus, EventBus())
        
        # 注册画布实例
        self.container.register_instance(type(self.canvas), self.canvas)
        
        # 注册数据管理器（单例，依赖事件总线）
        self.container.register_singleton(DataManager, DataManager, [EventBus])
        
        # 注册输入处理器（单例，依赖事件总线和画布）
        self.container.register_singleton(InputHandler, InputHandler, [EventBus, type(self.canvas)])
        
        # 注册状态管理器（单例，依赖事件总线、数据管理器和操作管理器）
        self.container.register_singleton(StateManager, StateManager, [EventBus, DataManager, OperationManager])
        
        # 注册渲染器（单例，依赖事件总线、数据管理器和画布）
        self.container.register_singleton(CanvasRenderer, CanvasRenderer, [EventBus, DataManager, type(self.canvas)])
        
        # 注册操作管理器（单例，依赖事件总线）
        self.container.register_singleton(OperationManager, OperationManager, [EventBus])
        
    
    def _subscribe_global_events(self) -> None:
        """订阅全局事件"""
        self.event_bus.subscribe(EventType.STATE_CHANGED, self._on_state_changed)
        self.event_bus.subscribe(EventType.MODE_CHANGED, self._on_mode_changed)
        self.event_bus.subscribe(EventType.CONFIRM_CANCEL_POLYGON, self._on_confirm_cancel_polygon)
        self.event_bus.subscribe(EventType.SHAPE_ADDED, self._on_shape_added)
        self.event_bus.subscribe(EventType.SHAPE_UPDATED, self._on_shape_updated)
        self.event_bus.subscribe(EventType.SHAPE_REMOVED, self._on_shape_deleted)
        self.event_bus.subscribe(EventType.SHAPE_SELECTED, self._on_shape_selected)
        self.event_bus.subscribe(EventType.SHAPE_DESELECTED, self._on_shape_deselected)
        self.event_bus.subscribe(EventType.OPERATION_EXECUTED, self._on_operation_executed)
        self.event_bus.subscribe(EventType.OPERATION_UNDONE, self._on_operation_undone)
        self.event_bus.subscribe(EventType.OPERATION_REDONE, self._on_operation_redone)
    
    # 事件处理方法
    def _on_state_changed(self, event: Event) -> None:
        """处理状态变化事件"""
        old_state = event.data['old_state']
        new_state = event.data['new_state']
    
    def _on_mode_changed(self, event: Event) -> None:
        """处理模式变化事件"""
        if event.data.get('key_event'):
            from ..utils.constants import KeyConstants
            
            key = event.data['key']
            ctrl_pressed = event.data['ctrl_pressed']
            
            # 处理ESC键
            if key == KeyConstants.ESCAPE:
                if self.state_manager.current_state == OperationState.CREATING_POLYGON:
                    self.state_manager._cancel_creating_polygon()
                return
            
            # 处理Delete键
            if key == KeyConstants.KEY_DELETE:
                if event.data.get('shift_pressed', False):
                    # Shift+Delete - 删除所有图形
                    self.clear_all_shapes()
                else:
                    # Delete - 删除选中的图形
                    self._delete_selected_shape()
                return
            
            # 处理快捷键
            if ctrl_pressed:
                if key == KeyConstants.KEY_A:  # Ctrl+A - 切换标注模式
                    # 通过事件系统通知画布切换标注模式
                    self.event_bus.publish(Event(EventType.MODE_CHANGED, {
                        'mode': 'annotation_toggle'
                    }))
                elif key == KeyConstants.KEY_1:  # Ctrl+1 - 切换绘制工具
                    self._cycle_draw_tool()
                elif key == KeyConstants.KEY_2:  # Ctrl+2 - 切换颜色
                    self._cycle_color()
                elif key == KeyConstants.KEY_3:  # Ctrl+3 - 切换线宽
                    self._cycle_width()
                elif key == KeyConstants.KEY_Z:  # Ctrl+Z - 撤销
                    self.undo()
                elif key == KeyConstants.KEY_Y:  # Ctrl+Y - 重做
                    self.redo()
    
    def _on_confirm_cancel_polygon(self, event: Event) -> None:
        """处理确认取消多边形事件"""
        confirmed = event.data.get('confirmed', False)
        if confirmed:
            self.state_manager._cancel_creating_polygon()
    
    def _on_shape_added(self, event: Event) -> None:
        """处理图形添加事件"""
        shape = event.data.get('shape')
        if shape:
            # 发出画布信号
            self.canvas.shape_added.emit(shape)
    
    def _on_shape_updated(self, event: Event) -> None:
        """处理图形更新事件"""
        shape = event.data.get('shape')
        if shape:
            # 发出画布信号
            self.canvas.shape_updated.emit(shape)
    
    def _on_shape_deleted(self, event: Event) -> None:
        """处理图形删除事件"""
        shape = event.data.get('shape')
        if shape:
            # 发出画布信号
            self.canvas.shape_removed.emit(shape)
    
    def _on_shape_selected(self, event: Event) -> None:
        """处理图形选中事件"""
        shape = event.data.get('shape')
        if shape:
            # 发出画布信号
            self.canvas.shape_selected.emit(shape)
    
    def _on_shape_deselected(self, event: Event) -> None:
        """处理图形取消选中事件"""
        shape = event.data.get('shape')
        if shape:
            # 发出画布信号
            self.canvas.shape_deselected.emit(shape)
    
    def _on_operation_executed(self, event: Event) -> None:
        """处理操作执行事件"""
        operation = event.data.get('operation')
        if operation:
            pass
    
    def _on_operation_undone(self, event: Event) -> None:
        """处理操作撤销事件"""
        operation = event.data.get('operation')
        if operation:
            pass
    
    def _on_operation_redone(self, event: Event) -> None:
        """处理操作重做事件"""
        operation = event.data.get('operation')
        if operation:
            pass
    
    # 公共方法 - 使用事件驱动的方式
    def get_shape_at_position(self, position: QPointF, tolerance: float = None) -> Optional[BaseShape]:
        """获取指定位置的图形（事件驱动）"""
        return self.data_access.get_shape_at_position(position, tolerance)
    
    def get_all_shapes(self) -> List[BaseShape]:
        """获取所有图形（事件驱动）"""
        return self.data_access.get_all_shapes()
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """获取选中的图形（事件驱动）"""
        return self.data_access.get_selected_shape()
    
    def get_hovered_shape(self) -> Optional[BaseShape]:
        """获取悬停的图形（事件驱动）"""
        return self.data_access.get_hovered_shape()
    
    def select_shape(self, shape: Optional[BaseShape]) -> None:
        """选择图形（事件驱动）"""
        self.data_manager.select_shape(shape)
    
    def clear_all_shapes(self) -> None:
        """清空所有图形"""
        shapes = self.get_all_shapes()
        for shape in shapes:
            self.data_manager.remove_shape(shape)
    
    def _delete_selected_shape(self) -> None:
        """删除选中的图形"""
        selected_shape = self.get_selected_shape()
        if selected_shape:
            self.data_manager.remove_shape(selected_shape)
    
    # 移除此方法，所有模式切换都通过事件系统处理
    
    def _cycle_draw_tool(self) -> None:
        """循环切换绘制工具"""
        current_tool = self.data_manager.get_current_tool()
        tools = [DrawType.POINT, DrawType.RECTANGLE, DrawType.ELLIPSE, DrawType.POLYGON]
        current_index = tools.index(current_tool) if current_tool in tools else 0
        next_tool = tools[(current_index + 1) % len(tools)]
        
        self.data_manager.set_current_tool(next_tool)
        self.event_bus.publish(Event(EventType.TOOL_CHANGED, {
            'tool': next_tool
        }))
    
    def _cycle_color(self) -> None:
        """循环切换颜色"""
        current_color = self.data_manager.get_current_color()
        colors = [DrawColor.RED, DrawColor.GREEN, DrawColor.BLUE, DrawColor.YELLOW, DrawColor.PURPLE]
        current_index = colors.index(current_color) if current_color in colors else 0
        next_color = colors[(current_index + 1) % len(colors)]
        
        self.data_manager.set_current_color(next_color)
        self.event_bus.publish(Event(EventType.COLOR_CHANGED, {
            'color': next_color
        }))
    
    def _cycle_width(self) -> None:
        """循环切换线宽"""
        current_width = self.data_manager.get_current_width()
        widths = [PenWidth.THIN, PenWidth.MEDIUM, PenWidth.THICK]
        current_index = widths.index(current_width) if current_width in widths else 0
        next_width = widths[(current_index + 1) % len(widths)]
        
        self.data_manager.set_current_width(next_width)
        self.event_bus.publish(Event(EventType.WIDTH_CHANGED, {
            'width': next_width
        }))
    
    def undo(self) -> None:
        """撤销操作"""
        self.operation_manager.undo()
    
    def redo(self) -> None:
        """重做操作"""
        self.operation_manager.redo()
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return self.operation_manager.can_undo()
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return self.operation_manager.can_redo()
    
    def get_operation_history(self) -> List[str]:
        """获取操作历史"""
        return [op.get_description() for op in self.operation_manager.get_history()]
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("清理AnnotationController资源")
        self.container.clear()
