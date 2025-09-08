"""
主控制器 - 使用依赖注入容器

这个文件展示了如何使用依赖注入容器来管理模块依赖关系。
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
from ..di import DIContainer, injectable, inject
from ..utils.logger import get_logger

logger = get_logger(__name__)


@injectable
class AnnotationController:
    """主控制器 - 使用依赖注入容器"""
    
    def __init__(self, canvas, event_bus: EventBus, data_manager: DataManager, 
                 input_handler: InputHandler, state_manager: StateManager, 
                 renderer: CanvasRenderer, operation_manager: OperationManager):
        """
        初始化控制器
        
        Args:
            canvas: 画布组件
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
        
        # 设置画布的控制器引用
        self.canvas.controller = self
        
        # 初始化各个模块
        self._initialize_modules()
        
        logger.info("AnnotationController 初始化完成")
    
    def _initialize_modules(self) -> None:
        """初始化各个模块"""
        # 设置输入处理器
        self.input_handler.set_canvas(self.canvas)
        
        # 设置状态管理器
        self.state_manager.set_canvas(self.canvas)
        
        # 设置渲染器
        self.renderer.set_canvas(self.canvas)
        
        # 设置操作管理器
        self.operation_manager.set_canvas(self.canvas)
        
        logger.debug("所有模块初始化完成")
    
    def set_current_tool(self, tool: DrawType) -> None:
        """设置当前绘制工具"""
        self.state_manager.set_current_tool(tool)
        logger.debug(f"设置绘制工具: {tool.name}")
    
    def set_current_color(self, color: DrawColor) -> None:
        """设置当前颜色"""
        self.state_manager.set_current_color(color)
        logger.debug(f"设置颜色: {color.name}")
    
    def set_current_width(self, width: PenWidth) -> None:
        """设置当前线宽"""
        self.state_manager.set_current_width(width)
        logger.debug(f"设置线宽: {width.name}")
    
    def toggle_grid_snap(self) -> None:
        """切换网格吸附"""
        self.state_manager.toggle_grid_snap()
        logger.debug("切换网格吸附")
    
    def undo(self) -> None:
        """撤销操作"""
        if self.operation_manager:
            self.operation_manager.undo()
            logger.debug("执行撤销操作")
    
    def redo(self) -> None:
        """重做操作"""
        if self.operation_manager:
            self.operation_manager.redo()
            logger.debug("执行重做操作")
    
    def delete_selected(self) -> None:
        """删除选中的图形"""
        selected_shapes = self.data_manager.get_selected_shapes()
        if selected_shapes:
            for shape in selected_shapes:
                self.data_manager.remove_shape(shape)
            logger.debug(f"删除 {len(selected_shapes)} 个图形")
    
    def clear_all(self) -> None:
        """清空所有图形"""
        self.data_manager.clear_all_shapes()
        logger.debug("清空所有图形")
    
    def export_data(self) -> dict:
        """导出数据"""
        return self.data_manager.export_data()
    
    def import_data(self, data: dict) -> bool:
        """导入数据"""
        return self.data_manager.import_data(data)
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.debug("开始清理 AnnotationController 资源")
        
        # 清理各个模块
        if hasattr(self.input_handler, 'cleanup'):
            self.input_handler.cleanup()
        
        if hasattr(self.state_manager, 'cleanup'):
            self.state_manager.cleanup()
        
        if hasattr(self.renderer, 'cleanup'):
            self.renderer.cleanup()
        
        if hasattr(self.operation_manager, 'cleanup'):
            self.operation_manager.cleanup()
        
        logger.debug("AnnotationController 资源清理完成")


def create_controller_with_di(canvas) -> AnnotationController:
    """
    使用依赖注入容器创建控制器
    
    Args:
        canvas: 画布组件
        
    Returns:
        配置好的控制器实例
    """
    # 创建依赖注入容器
    container = DIContainer()
    
    # 注册服务
    container.register_singleton(EventBus, EventBus)
    container.register_singleton(DataManager, DataManager)
    container.register_singleton(InputHandler, InputHandler)
    container.register_singleton(StateManager, StateManager)
    container.register_singleton(CanvasRenderer, CanvasRenderer)
    container.register_singleton(OperationManager, OperationManager)
    
    # 创建实例
    event_bus = container.get(EventBus)
    data_manager = container.get(DataManager)
    input_handler = container.get(InputHandler)
    state_manager = container.get(StateManager)
    renderer = container.get(CanvasRenderer)
    operation_manager = container.get(OperationManager)
    
    # 创建控制器
    controller = AnnotationController(
        canvas=canvas,
        event_bus=event_bus,
        data_manager=data_manager,
        input_handler=input_handler,
        state_manager=state_manager,
        renderer=renderer,
        operation_manager=operation_manager
    )
    
    logger.info("使用依赖注入容器创建控制器完成")
    return controller
