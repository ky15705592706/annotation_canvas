"""
改进的注解画布 - 使用依赖注入和事件驱动架构
"""

from typing import Optional, List
from PySide6.QtCore import QPointF, Qt, Signal, QTimer
from PySide6.QtGui import QMouseEvent, QKeyEvent, QWheelEvent
import pyqtgraph as pg

from ..core import DrawType, DrawColor, PenWidth
from ..models import BaseShape
from ..utils.constants import (
    AppConstants, CanvasConstants, InteractionConstants, 
    DisplayConstants, ColorConstants
)
from ..utils.logger import get_logger
from .annotation_controller import AnnotationController
from ..di import DIContainer

logger = get_logger(__name__)


class AnnotationCanvas(pg.PlotWidget):
    """AnnotationCanvas - 基于PyQtGraph的图形标注画布组件，使用依赖注入和事件驱动架构"""
    
    # 信号定义
    shape_added = Signal(BaseShape)
    shape_removed = Signal(BaseShape)
    shape_updated = Signal(BaseShape)
    shape_selected = Signal(BaseShape)
    shape_deselected = Signal(BaseShape)
    
    def __init__(self, parent=None, container: DIContainer = None):
        """
        初始化改进的画布
        
        Args:
            parent: 父组件
            container: 依赖注入容器（可选）
        """
        super().__init__(parent)
        
        # 创建或使用提供的依赖注入容器
        self.container = container or DIContainer()
        
        # 标注模式状态
        self.annotation_mode = False
        
        # 初始化画布
        self._setup_canvas()
        
        # 创建控制器
        self.controller = AnnotationController(self, self.container)
        
        # 从容器获取事件总线
        from ..events import EventBus
        self.event_bus = self.container.get(EventBus)
        
        # 设置事件处理
        self._setup_event_handling()
        
        # 订阅事件
        self._subscribe_events()
        
    
    def _setup_canvas(self):
        """设置画布"""
        # 设置画布属性
        self.setBackground(ColorConstants.CANVAS_BACKGROUND)
        self.setMouseEnabled(x=True, y=True)
        self.setMenuEnabled(False)
        self.setLabel('left', 'Y')
        self.setLabel('bottom', 'X')
        self.setTitle('改进的图形标注画布')
        
        # 设置网格
        self.showGrid(x=True, y=True, alpha=0.3)
        
        # 设置视图范围
        self.setXRange(0, CanvasConstants.DEFAULT_WIDTH)
        self.setYRange(0, CanvasConstants.DEFAULT_HEIGHT)
        
        # 设置交互
        self.setAspectLocked(True)
        self.setMouseEnabled(x=True, y=True)
        
        # 设置焦点策略以接收键盘事件
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _setup_event_handling(self):
        """设置事件处理"""
        # 连接信号
        self.scene().sigMouseClicked.connect(self._on_mouse_clicked)
        self.scene().sigMouseMoved.connect(self._on_mouse_moved)
        
        # 重写鼠标事件处理方法
        self.mousePressEvent = self._mouse_press_event
        self.mouseMoveEvent = self._mouse_move_event
        self.mouseReleaseEvent = self._mouse_release_event
        self.wheelEvent = self._wheel_event
    
    # 鼠标事件处理
    def _on_mouse_clicked(self, event):
        """处理鼠标点击事件（PyQtGraph信号）"""
        if self.annotation_mode and event.button() == Qt.LeftButton:
            # 标注模式：处理标注功能
            pos = event.pos()
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            self.controller.input_handler.handle_mouse_press(event, world_pos)
        # 默认模式：不处理，让PyQtGraph处理（拖拽坐标系）
    
    def _on_mouse_moved(self, event):
        """处理鼠标移动事件（PyQtGraph信号）"""
        if self.annotation_mode:
            # 标注模式：处理标注功能
            # PyQtGraph的sigMouseMoved信号直接传递QPointF，不是QMouseEvent
            pos = event  # event本身就是QPointF
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            # 创建一个模拟的QMouseEvent用于InputHandler
            from PySide6.QtGui import QMouseEvent
            from PySide6.QtCore import Qt
            mock_event = QMouseEvent(QMouseEvent.MouseMove, pos, Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            self.controller.input_handler.handle_mouse_move(mock_event, world_pos)
        # 默认模式：不处理，让PyQtGraph处理（拖拽坐标系）
    
    def _mouse_press_event(self, event: QMouseEvent):
        """处理鼠标按下事件（Qt事件）"""
        if self.annotation_mode and event.button() == Qt.LeftButton:
            # 标注模式：处理标注功能
            pos = event.pos()
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            self.controller.input_handler.handle_mouse_press(event, world_pos)
        else:
            # 默认模式：使用PlotWidget的默认行为（拖拽坐标系）
            super().mousePressEvent(event)
    
    def _mouse_move_event(self, event: QMouseEvent):
        """处理鼠标移动事件（Qt事件）"""
        if self.annotation_mode:
            # 标注模式：处理标注功能
            pos = event.pos()
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            self.controller.input_handler.handle_mouse_move(event, world_pos)
        else:
            # 默认模式：使用PlotWidget的默认行为（拖拽坐标系）
            super().mouseMoveEvent(event)
    
    def _mouse_release_event(self, event: QMouseEvent):
        """处理鼠标释放事件（Qt事件）"""
        if self.annotation_mode and event.button() == Qt.LeftButton:
            # 标注模式：处理标注功能
            pos = event.pos()
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            self.controller.input_handler.handle_mouse_release(event, world_pos)
        else:
            # 默认模式：使用PlotWidget的默认行为（拖拽坐标系）
            super().mouseReleaseEvent(event)
    
    def _wheel_event(self, event: QWheelEvent):
        """处理鼠标滚轮事件（Qt事件）"""
        if self.annotation_mode:
            # 标注模式：处理标注功能，但也允许缩放
            pos = event.position().toPoint()
            world_pos = self.plotItem.vb.mapSceneToView(pos)
            self.controller.input_handler.handle_wheel_event(event, world_pos)
            super().wheelEvent(event)
        else:
            # 默认模式：使用PlotWidget的默认行为（缩放坐标系）
            super().wheelEvent(event)
    
    # 键盘事件处理
    def keyPressEvent(self, event: QKeyEvent):
        """处理键盘按下事件"""
        self.controller.input_handler.handle_key_press(event)
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent):
        """处理键盘释放事件"""
        self.controller.input_handler.handle_key_release(event)
        super().keyReleaseEvent(event)
    
    # 公共API - 使用事件驱动的方式
    def set_draw_tool(self, tool: DrawType) -> None:
        """设置绘制工具"""
        from ..events import Event, EventType
        self.controller.data_manager.set_current_tool(tool)
        self.controller.event_bus.publish(Event(EventType.TOOL_CHANGED, {
            'tool': tool
        }))
    
    def set_draw_color(self, color: DrawColor) -> None:
        """设置绘制颜色"""
        from ..events import Event, EventType
        self.controller.data_manager.set_current_color(color)
        self.controller.event_bus.publish(Event(EventType.COLOR_CHANGED, {
            'color': color
        }))
    
    def set_pen_width(self, width: PenWidth) -> None:
        """设置画笔宽度"""
        from ..events import Event, EventType
        self.controller.data_manager.set_current_width(width)
        self.controller.event_bus.publish(Event(EventType.WIDTH_CHANGED, {
            'width': width
        }))
    
    def get_draw_tool(self) -> DrawType:
        """获取当前绘制工具"""
        return self.controller.data_manager.get_current_tool()
    
    def get_draw_color(self) -> DrawColor:
        """获取当前绘制颜色"""
        return self.controller.data_manager.get_current_color()
    
    def get_pen_width(self) -> PenWidth:
        """获取当前画笔宽度"""
        return self.controller.data_manager.get_current_width()
    
    def add_shape(self, shape: BaseShape) -> None:
        """添加图形"""
        self.controller.data_manager.add_shape(shape)
    
    def remove_shape(self, shape: BaseShape) -> None:
        """删除图形"""
        self.controller.data_manager.remove_shape(shape)
    
    def get_shapes(self) -> List[BaseShape]:
        """获取所有图形（事件驱动）"""
        return self.controller.get_all_shapes()
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """获取选中的图形（事件驱动）"""
        return self.controller.get_selected_shape()
    
    def select_shape(self, shape: Optional[BaseShape]) -> None:
        """选择图形（事件驱动）"""
        self.controller.select_shape(shape)
    
    def clear_all_shapes(self) -> None:
        """清空所有图形"""
        self.controller.clear_all_shapes()
    
    def get_shape_at_position(self, position: QPointF, tolerance: float = None) -> Optional[BaseShape]:
        """获取指定位置的图形（事件驱动）"""
        return self.controller.get_shape_at_position(position, tolerance)
    
    # Z轴管理
    def set_shape_z_order(self, shape: BaseShape, z_order: int) -> None:
        """设置图形的z轴层级"""
        from ..events import Event, EventType
        shape.set_z_order(z_order)
        self.controller.event_bus.publish(Event(EventType.SHAPE_UPDATED, {
            'shape': shape
        }))
    
    def bring_shape_to_front(self, shape: BaseShape) -> None:
        """将图形置于最前"""
        from ..events import Event, EventType
        shape.bring_to_front()
        self.controller.event_bus.publish(Event(EventType.SHAPE_UPDATED, {
            'shape': shape
        }))
    
    def send_shape_to_back(self, shape: BaseShape) -> None:
        """将图形置于最后"""
        from ..events import Event, EventType
        shape.send_to_back()
        self.controller.event_bus.publish(Event(EventType.SHAPE_UPDATED, {
            'shape': shape
        }))
    
    def get_shape_z_order(self, shape: BaseShape) -> int:
        """获取图形的z轴层级"""
        return shape.get_z_order()
    
    # 延迟删除功能
    def clear_all_delayed(self, delay_ms: int = 0) -> None:
        """延迟清空所有图形"""
        QTimer.singleShot(delay_ms, self.clear_all_shapes)
    
    def remove_shape_delayed(self, shape: BaseShape, delay_ms: int = 0) -> None:
        """延迟删除单个图形"""
        QTimer.singleShot(delay_ms, lambda: self.remove_shape(shape))
    
    def remove_shapes_delayed(self, shapes: List[BaseShape], delay_ms: int = 0) -> None:
        """延迟删除多个图形"""
        QTimer.singleShot(delay_ms, lambda: [self.remove_shape(shape) for shape in shapes])
    
    def remove_all_except_delayed(self, keep_shape: BaseShape, delay_ms: int = 0) -> None:
        """延迟删除除指定图形外的所有图形"""
        QTimer.singleShot(delay_ms, lambda: self.remove_all_except(keep_shape))
    
    def remove_all_except(self, keep_shape: BaseShape) -> None:
        """删除除指定图形外的所有图形"""
        all_shapes = self.get_shapes()
        shapes_to_remove = [shape for shape in all_shapes if shape != keep_shape]
        for shape in shapes_to_remove:
            self.controller.data_manager.remove_shape(shape)
    
    # 撤销重做
    def undo(self) -> None:
        """撤销操作"""
        self.controller.undo()
    
    def redo(self) -> None:
        """重做操作"""
        self.controller.redo()
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return self.controller.can_undo()
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return self.controller.can_redo()
    
    def get_operation_history(self) -> List[str]:
        """获取操作历史"""
        return self.controller.get_operation_history()
    
    # 数据导入导出
    def export_data(self) -> dict:
        """导出数据"""
        return self.controller.data_manager.export_data()
    
    def import_data(self, data: dict) -> None:
        """导入数据"""
        self.controller.data_manager.import_data(data)
    
    def _subscribe_events(self) -> None:
        """订阅事件"""
        # 订阅模式改变事件
        from ..events import EventType
        self.event_bus.subscribe(EventType.MODE_CHANGED, self._on_mode_changed)
    
    def _on_mode_changed(self, event) -> None:
        """处理模式改变事件"""
        mode = event.data.get('mode')
        key_event = event.data.get('key_event', False)
        if mode == 'annotation_toggle':
            self._toggle_annotation_mode()
    
    def _toggle_annotation_mode(self) -> None:
        """切换标注模式"""
        self.annotation_mode = not self.annotation_mode
        mode_text = "标注模式" if self.annotation_mode else "默认模式"
        logger.info(f"切换标注模式: {mode_text}")
        
        # 可以在这里添加状态栏更新或其他UI反馈
        # 例如：self.statusBar().showMessage(f"当前模式: {mode_text}")
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.info("清理AnnotationCanvas资源")
        if hasattr(self, 'controller'):
            self.controller.cleanup()
