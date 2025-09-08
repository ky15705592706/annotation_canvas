"""
主控制器 - 协调各个模块
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
from ..operations import OperationManager, CreateOperation, DeleteOperation, MoveOperation, ScaleOperation
from ..utils.logger import get_logger

logger = get_logger(__name__)


class AnnotationController:
    """主控制器 - 协调各个模块"""
    
    def __init__(self, canvas) -> None:
        """
        初始化主控制器
        
        Args:
            canvas: 画布对象
        """
        self.canvas = canvas
        
        # 创建事件总线
        self.event_bus = EventBus()
        
        # 创建操作管理器
        self.operation_manager = OperationManager()
        
        # 创建各个模块
        self.data_manager = DataManager(self.event_bus)
        self.input_handler = InputHandler(self.event_bus, canvas)
        self.state_manager = StateManager(self.event_bus, self.data_manager, self.operation_manager)
        self.renderer = CanvasRenderer(self.event_bus, self.data_manager, canvas)
        
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
                    self._toggle_annotation_mode()
                elif key == KeyConstants.KEY_1:  # Ctrl+1 - 切换绘制工具
                    self._cycle_draw_tool()
                elif key == KeyConstants.KEY_2:  # Ctrl+2 - 切换颜色
                    self._cycle_color()
                elif key == KeyConstants.KEY_3:  # Ctrl+3 - 切换线宽
                    self._cycle_width()
                elif key == KeyConstants.KEY_G:  # Ctrl+G - 切换网格吸附
                    self._toggle_grid_snap()
                elif key == KeyConstants.KEY_Z:  # Ctrl+Z - 撤销
                    self._undo()
                elif key == KeyConstants.KEY_Y:  # Ctrl+Y - 重做
                    self._redo()
    
    def _toggle_annotation_mode(self) -> None:
        """切换标注模式"""
        # 调用画布的标注模式切换方法
        if hasattr(self, 'canvas') and hasattr(self.canvas, '_toggle_annotation_mode'):
            self.canvas._toggle_annotation_mode()
    
    def _cycle_draw_tool(self) -> None:
        """循环切换绘制工具"""
        tools = [DrawType.POINT, DrawType.RECTANGLE, DrawType.ELLIPSE, DrawType.POLYGON]
        current_tool = self.data_manager.get_current_tool()
        current_index = tools.index(current_tool)
        next_index = (current_index + 1) % len(tools)
        self.data_manager.set_current_tool(tools[next_index])
    
    def _cycle_color(self) -> None:
        """循环切换颜色"""
        colors = [DrawColor.RED, DrawColor.GREEN, DrawColor.BLUE, DrawColor.YELLOW, DrawColor.PURPLE]
        current_color = self.data_manager.get_current_color()
        current_index = colors.index(current_color)
        next_index = (current_index + 1) % len(colors)
        self.data_manager.set_current_color(colors[next_index])
    
    def _cycle_width(self) -> None:
        """循环切换线宽"""
        widths = [PenWidth.THIN, PenWidth.MEDIUM, PenWidth.THICK]
        current_width = self.data_manager.get_current_width()
        current_index = widths.index(current_width)
        next_index = (current_index + 1) % len(widths)
        self.data_manager.set_current_width(widths[next_index])
    
    def _toggle_grid_snap(self) -> None:
        """切换网格吸附"""
        from ..utils.config import Config
        config = Config()
        current_snap = config.is_snap_to_grid()
        new_snap = not current_snap
        config.set("drawing.snap_to_grid", new_snap)
        config.save_config()
        
        status = "启用" if new_snap else "禁用"
        logger.info(f"网格吸附已{status}")
        
        # 通知画布更新状态栏
        if hasattr(self, 'canvas') and hasattr(self.canvas, '_update_status_bar'):
            self.canvas._update_status_bar()
    
    def _undo(self) -> None:
        """撤销操作"""
        if self.operation_manager.can_undo():
            if self.operation_manager.undo():
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
                logger.info(f"撤销操作: {self.operation_manager.get_undo_description()}")
            else:
                logger.error("撤销操作失败")
        else:
            logger.info("没有可撤销的操作")
    
    def _redo(self) -> None:
        """重做操作"""
        if self.operation_manager.can_redo():
            if self.operation_manager.redo():
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
                logger.info(f"重做操作: {self.operation_manager.get_redo_description()}")
            else:
                logger.error("重做操作失败")
        else:
            logger.info("没有可重做的操作")
    
    def _delete_selected_shape(self) -> None:
        """删除选中的图形"""
        selected_shape = self.data_manager.get_selected_shape()
        if selected_shape:
            # 创建删除操作
            delete_operation = DeleteOperation([selected_shape], self.data_manager)
            self.operation_manager.execute_operation(delete_operation)
            
            # 触发显示更新
            self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
    
    
    # 鼠标事件处理
    def handle_mouse_press(self, event: QMouseEvent) -> None:
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
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
        if event.button() == Qt.MouseButton.LeftButton:
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
    
    # 数据管理方法
    def add_shape(self, shape) -> None:
        """添加图形"""
        self.data_manager.add_shape(shape)
    
    def remove_shape(self, shape) -> bool:
        """移除图形"""
        return self.data_manager.remove_shape(shape)
    
    def clear_all_shapes(self) -> None:
        """清空所有图形"""
        shapes = self.data_manager.get_shapes()
        if shapes:
            # 创建删除操作
            delete_operation = DeleteOperation(shapes, self.data_manager)
            self.operation_manager.execute_operation(delete_operation)
            
            # 触发显示更新
            self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
    
    def get_shapes(self) -> List[BaseShape]:
        """获取所有图形"""
        return self.data_manager.get_shapes()
    
    def get_selected_shape(self) -> Optional[BaseShape]:
        """获取选中的图形"""
        return self.data_manager.get_selected_shape()
    
    # 数据导入导出
    def export_data(self) -> dict:
        """导出数据"""
        return self.data_manager.export_data()
    
    def import_data(self, data: dict) -> bool:
        """导入数据"""
        return self.data_manager.import_data(data)
    
    # 渲染控制
    def update_display(self) -> None:
        """更新显示"""
        self.renderer.request_display_update()
    
    def set_debug_mode(self, enabled: bool) -> None:
        """设置调试模式"""
        self.event_bus.set_debug_mode(enabled)
    
    # 状态查询
    def get_current_state(self) -> OperationState:
        """获取当前状态"""
        return self.state_manager.get_current_state()
    
    def get_input_state(self) -> dict:
        """获取输入状态"""
        return self.input_handler.get_current_state()
    
    def _on_confirm_cancel_polygon(self, event: Event) -> None:
        """处理确认取消多边形事件"""
        from PySide6.QtWidgets import QMessageBox
        
        vertex_count = event.data.get('vertex_count', 0)
        
        # 显示确认对话框
        reply = QMessageBox.question(
            self.canvas,
            "确认取消",
            f"当前多边形已有 {vertex_count} 个顶点，确定要取消创建吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 用户确认取消，通知状态管理器执行取消操作
            self.event_bus.publish(Event(
                EventType.CANCEL_POLYGON_CONFIRMED,
                {}
            ))
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.debug("控制器开始清理资源")
        
        # 清理状态管理器
        if hasattr(self.state_manager, 'cleanup'):
            self.state_manager.cleanup()
        
        # 清理渲染器
        if hasattr(self.renderer, 'cleanup'):
            self.renderer.cleanup()
        
        # 清理输入处理器
        if hasattr(self.input_handler, 'cleanup'):
            self.input_handler.cleanup()
        
        logger.debug("控制器资源清理完成")
