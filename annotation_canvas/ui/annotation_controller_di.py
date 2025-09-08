"""
主控制器 - 使用依赖注入容器
"""

from typing import Optional, List
from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QMouseEvent, QKeyEvent, QWheelEvent

from ..events import EventBus, Event, EventType
from ..data import DataManager
from ..input import InputHandler
from ..state import StateManager
from ..render import CanvasRenderer
from ..core import DrawType, DrawColor, PenWidth, OperationState
from ..models import BaseShape
from ..operations import OperationManager
from di import DIContainer, injectable, inject
from ..utils.logger import get_logger

logger = get_logger(__name__)


@injectable
class AnnotationController:
    """主控制器 - 使用依赖注入容器"""
    
    def __init__(self, canvas, event_bus: EventBus, data_manager: DataManager, 
                 input_handler: InputHandler, state_manager: StateManager, 
                 renderer: CanvasRenderer, operation_manager: OperationManager):
        """
        初始化主控制器
        
        Args:
            canvas: 画布对象
            event_bus: 事件总线
            data_manager: 数据管理器
            input_handler: 输入处理器
            state_manager: 状态管理器
            renderer: 渲染器
            operation_manager: 操作管理器
        """
        self.canvas = canvas
        self.event_bus = event_bus
        self.data_manager = data_manager
        self.input_handler = input_handler
        self.state_manager = state_manager
        self.renderer = renderer
        self.operation_manager = operation_manager
        
        # 设置调试模式（可选）
        self.event_bus.set_debug_mode(False)
        
        # 订阅一些全局事件
        self._subscribe_global_events()
    
    def _subscribe_global_events(self) -> None:
        """订阅全局事件"""
        self.event_bus.subscribe(EventType.STATE_CHANGED, self._on_state_changed)
        self.event_bus.subscribe(EventType.MODE_CHANGED, self._on_mode_changed)
        self.event_bus.subscribe(EventType.CONFIRM_CANCEL_POLYGON, self._on_confirm_cancel_polygon)
    
    def _on_state_changed(self, event: Event) -> None:
        """处理状态变化事件"""
        new_state = event.data.get('new_state')
        if new_state:
            logger.debug(f"状态变化: {new_state}")
    
    def _on_mode_changed(self, event: Event) -> None:
        """处理模式变化事件"""
        new_mode = event.data.get('new_mode')
        if new_mode:
            logger.debug(f"模式变化: {new_mode}")
    
    def _on_confirm_cancel_polygon(self, event: Event) -> None:
        """处理确认取消多边形事件"""
        confirmed = event.data.get('confirmed', False)
        if confirmed:
            logger.info("用户确认取消多边形创建")
            # 发布取消多边形确认事件
            self.event_bus.publish(Event(EventType.CANCEL_POLYGON_CONFIRMED, {}))
    
    # 撤销重做方法
    def _undo(self) -> None:
        """撤销操作"""
        if self.operation_manager.can_undo():
            operation = self.operation_manager.undo()
            if operation:
                logger.info(f"撤销操作: {operation.get_description()}")
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
        else:
            logger.info("没有可撤销的操作")
    
    def _redo(self) -> None:
        """重做操作"""
        if self.operation_manager.can_redo():
            operation = self.operation_manager.redo()
            if operation:
                logger.info(f"重做操作: {operation.get_description()}")
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
        else:
            logger.info("没有可重做的操作")
    
    # 事件处理方法
    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """处理鼠标按下事件"""
        world_pos = self._map_to_world_coordinates(event.pos())
        self.input_handler.handle_mouse_press(event, world_pos)
    
    def handle_mouse_move(self, event: QMouseEvent) -> None:
        """处理鼠标移动事件"""
        world_pos = self._map_to_world_coordinates(event.pos())
        self.input_handler.handle_mouse_move(event, world_pos)
        
        # 更新悬停状态
        self._update_hover_state(world_pos)
    
    def handle_mouse_release(self, event: QMouseEvent) -> None:
        """处理鼠标释放事件"""
        world_pos = self._map_to_world_coordinates(event.pos())
        self.input_handler.handle_mouse_release(event, world_pos)
    
    def handle_wheel_event(self, event: QWheelEvent) -> None:
        """处理滚轮事件"""
        world_pos = self._map_to_world_coordinates(event.pos())
        self.input_handler.handle_wheel_event(event, world_pos)
    
    def handle_key_press(self, event: QKeyEvent) -> None:
        """处理键盘按下事件"""
        self.input_handler.handle_key_press(event)
    
    def handle_key_release(self, event: QKeyEvent) -> None:
        """处理键盘释放事件"""
        self.input_handler.handle_key_release(event)
    
    def _map_to_world_coordinates(self, screen_pos) -> QPointF:
        """将屏幕坐标转换为世界坐标"""
        return self.canvas.plotItem.vb.mapSceneToView(screen_pos)
    
    def _update_hover_state(self, world_pos: QPointF) -> None:
        """更新悬停状态"""
        # 获取像素大小用于容差计算
        pixel_size = self.canvas.getViewBox().viewPixelSize()[0]
        
        # 获取命中目标
        hit_target = self.data_manager.get_hit_target(world_pos, pixel_size)
        
        # 更新悬停状态
        if hit_target['type'] == 'shape':
            self.data_manager.set_hovered_shape(hit_target['target'])
        else:
            self.data_manager.set_hovered_shape(None)
    
    # 工具设置方法
    def set_current_tool(self, tool: DrawType) -> None:
        """设置当前工具"""
        self.data_manager.set_current_tool(tool)
    
    def set_current_color(self, color: DrawColor) -> None:
        """设置当前颜色"""
        self.data_manager.set_current_color(color)
    
    def set_current_width(self, width: PenWidth) -> None:
        """设置当前线宽"""
        self.data_manager.set_current_width(width)
    
    def get_current_tool(self) -> DrawType:
        """获取当前工具"""
        return self.data_manager.get_current_tool()
    
    def get_current_color(self) -> DrawColor:
        """获取当前颜色"""
        return self.data_manager.get_current_color()
    
    def get_current_width(self) -> PenWidth:
        """获取当前线宽"""
        return self.data_manager.get_current_width()
    
    def get_current_state(self) -> OperationState:
        """获取当前状态"""
        return self.state_manager.current_state
    
    # 数据管理方法
    def add_shape(self, shape) -> None:
        """添加图形"""
        self.data_manager.add_shape(shape)
    
    def remove_shape(self, shape) -> bool:
        """移除图形"""
        return self.data_manager.remove_shape(shape)
    
    def clear_all_shapes(self) -> None:
        """清空所有图形"""
        self.data_manager.clear_all_shapes()
    
    def get_all_shapes(self) -> List[BaseShape]:
        """获取所有图形"""
        return self.data_manager.get_shapes()
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """获取选中的图形"""
        return self.data_manager.get_selected_shape()
    
    def select_shape(self, shape: Optional[BaseShape]) -> None:
        """选中图形"""
        self.data_manager.select_shape(shape)
    
    def deselect_all(self) -> None:
        """取消所有选择"""
        self.data_manager.clear_selection()
    
    # 操作管理方法
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return self.operation_manager.can_undo()
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return self.operation_manager.can_redo()
    
    def undo(self) -> None:
        """撤销操作"""
        self._undo()
    
    def redo(self) -> None:
        """重做操作"""
        self._redo()
    
    # 清理方法
    def cleanup(self) -> None:
        """清理资源"""
        if hasattr(self.state_manager, 'cleanup'):
            self.state_manager.cleanup()
        if hasattr(self.renderer, 'cleanup'):
            self.renderer.cleanup()
        logger.debug("控制器已清理")


def create_controller_with_di(canvas) -> AnnotationController:
    """
    使用依赖注入创建控制器
    
    Args:
        canvas: 画布对象
        
    Returns:
        控制器实例
    """
    container = DIContainer()
    
    # 注册服务
    container.register_singleton(EventBus)
    container.register_singleton(OperationManager)
    container.register_transient(DataManager)
    container.register_transient(InputHandler)
    container.register_transient(StateManager)
    container.register_transient(CanvasRenderer)
    container.register_transient(AnnotationController)
    
    # 注册画布实例
    container.register_instance(type(canvas), canvas)
    
    # 创建控制器
    controller = container.get(AnnotationController)
    return controller
