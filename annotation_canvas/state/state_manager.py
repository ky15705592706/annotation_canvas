"""
事件驱动的状态管理器
"""

from typing import Optional, Dict, Any
from PySide6.QtCore import QPointF

from ..events import EventBus, Event, EventType, EventHandlerBase
from ..core import OperationState, DrawType, DrawColor, PenWidth
from ..data import DataManager
from ..models import BaseShape, PolygonShape
from ..factories import ShapeFactory
from ..services import ShapeCreationService
from ..utils.constants import InteractionConstants
from ..utils.geometry import GeometryUtils
from ..utils.config import Config


class StateManager(EventHandlerBase):
    """事件驱动的状态管理器"""
    
    def __init__(self, event_bus: EventBus, data_manager: DataManager, operation_manager=None):
        """
        初始化状态管理器
        
        Args:
            event_bus: 事件总线
            data_manager: 数据管理器
            operation_manager: 操作管理器（可选）
        """
        super().__init__(event_bus)
        self.data_manager = data_manager
        self.operation_manager = operation_manager
        self.current_state = OperationState.IDLE
        
        # 创建图形创建服务
        self.shape_creation_service = ShapeCreationService(event_bus, data_manager, operation_manager)
        
        # 状态相关的临时数据
        self.drag_start_pos: Optional[QPointF] = None
        self.drag_start_shape: Optional[BaseShape] = None
        self.drag_start_control_point: Optional[Any] = None
        self.polygon_vertices: list = []
        self.temp_polygon: Optional[PolygonShape] = None  # 持久的临时多边形对象
    
    def _register_event_handlers(self) -> None:
        """注册事件处理器"""
        self._event_handlers = {
            EventType.MOUSE_PRESS: self._on_mouse_press,
            EventType.MOUSE_MOVE: self._on_mouse_move,
            EventType.MOUSE_RELEASE: self._on_mouse_release,
            EventType.SHAPE_SELECTED: self._on_shape_selected,
            EventType.SHAPE_DESELECTED: self._on_shape_deselected,
            EventType.CANCEL_POLYGON_CONFIRMED: self._on_cancel_polygon_confirmed,
        }
    
    def _on_mouse_press(self, event: Event) -> None:
        """处理鼠标按下事件"""
        pos = event.data['position']
        pixel_size = event.data.get('pixel_size', InteractionConstants.DEFAULT_PIXEL_SIZE)
        
        # 获取命中目标
        hit_target = self._get_hit_target(pos, pixel_size)
        
        # 根据当前状态和命中目标决定状态转换
        if self.current_state == OperationState.IDLE:
            self._handle_idle_mouse_press(pos, hit_target)
        elif self.current_state == OperationState.CREATING_POLYGON:
            self._handle_polygon_mouse_press(pos, hit_target, pixel_size)
    
    def _on_mouse_move(self, event: Event) -> None:
        """处理鼠标移动事件"""
        pos = event.data['position']
        dragging = event.data.get('dragging', False)
        pixel_size = event.data.get('pixel_size', InteractionConstants.DEFAULT_PIXEL_SIZE)
        
        # 处理悬停检测（在空闲状态下）
        if self.current_state == OperationState.IDLE:
            self._handle_control_point_hover(pos, pixel_size)
            self._handle_shape_hover(pos, pixel_size)
        
        # 根据当前状态处理移动
        if self.current_state == OperationState.MOVING:
            self._handle_moving(pos, dragging)
        elif self.current_state == OperationState.SCALING:
            self._handle_scaling(pos, dragging)
        elif self.current_state == OperationState.CREATING_RECT:
            self._handle_creating_rect(pos, dragging)
        elif self.current_state == OperationState.CREATING_ELLIPSE:
            self._handle_creating_ellipse(pos, dragging)
        elif self.current_state == OperationState.CREATING_POLYGON:
            self._handle_creating_polygon(pos, dragging, pixel_size)
    
    def _on_mouse_release(self, event: Event) -> None:
        """处理鼠标释放事件"""
        pos = event.data['position']
        left_pressed = event.data['left_button_pressed']
        
        if left_pressed:
            return  # 左键仍然按下，不处理
        
        # 根据当前状态处理释放
        if self.current_state == OperationState.CREATING_POINT:
            self._finish_creating_point(pos)
        elif self.current_state == OperationState.CREATING_RECT:
            self._finish_creating_rect(pos)
        elif self.current_state == OperationState.CREATING_ELLIPSE:
            self._finish_creating_ellipse(pos)
        elif self.current_state == OperationState.MOVING:
            self._finish_moving(pos)
        elif self.current_state == OperationState.SCALING:
            self._finish_scaling(pos)
        # 注意：CREATING_POLYGON 状态不需要在鼠标释放时处理，因为它通过多次点击完成
        
        # 大部分操作完成后回到空闲状态
        if self.current_state in [OperationState.CREATING_POINT, OperationState.CREATING_RECT, 
                                 OperationState.CREATING_ELLIPSE, OperationState.MOVING, OperationState.SCALING]:
            self._change_state(OperationState.IDLE)
    
    def _on_shape_selected(self, event: Event) -> None:
        """处理图形选择事件"""
        pass  # 目前不需要特殊处理
    
    def _on_shape_deselected(self, event: Event) -> None:
        """处理图形取消选择事件"""
        pass  # 目前不需要特殊处理
    
    def _on_cancel_polygon_confirmed(self, event: Event) -> None:
        """处理确认取消多边形事件"""
        self._do_cancel_polygon()
    
    def _handle_control_point_hover(self, pos: QPointF, pixel_size: float) -> None:
        """处理控制点悬停检测"""
        selected_shape = self.data_manager.get_selected_shape()
        if not selected_shape:
            return
        
        # 检查是否有控制点被悬停
        hovered_control_point = None
        for cp in selected_shape.get_control_points():
            # 计算世界坐标距离
            world_distance = GeometryUtils.distance_between_points(pos, cp.position)
            # 转换为像素距离
            pixel_distance = world_distance / pixel_size if pixel_size > 0 else world_distance
            
            if pixel_distance <= InteractionConstants.CONTROL_POINT_TOLERANCE:
                hovered_control_point = cp
                break
        
        # 更新控制点悬停状态
        for cp in selected_shape.get_control_points():
            was_hovered = cp.hovered
            cp.set_hovered(cp == hovered_control_point)
            
            # 如果悬停状态改变，更新显示
            if was_hovered != cp.hovered:
                self.event_bus.publish(Event(
                    EventType.CONTROL_POINT_HOVER_CHANGED,
                    {'control_point': cp, 'hovered': cp.hovered}
                ))
    
    def _handle_shape_hover(self, pos: QPointF, pixel_size: float) -> None:
        """处理图形悬停检测"""
        # 获取命中目标
        hit_target = self.data_manager.get_hit_target(pos, pixel_size)
        
        # 确定悬停的图形
        hovered_shape = None
        if hit_target['type'] == 'shape':
            hovered_shape = hit_target['target']
        
        # 更新悬停状态
        current_hovered = self.data_manager.get_hovered_shape()
        if current_hovered != hovered_shape:
            # 清除旧图形的悬停状态
            if current_hovered:
                current_hovered.set_hovered(False)
                self.event_bus.publish(Event(
                    EventType.HOVER_CHANGED,
                    {'shape': current_hovered, 'hovered': False}
                ))
            
            # 设置新图形的悬停状态
            if hovered_shape:
                hovered_shape.set_hovered(True)
                self.event_bus.publish(Event(
                    EventType.HOVER_CHANGED,
                    {'shape': hovered_shape, 'hovered': True}
                ))
            
            # 直接更新数据管理器的内部状态，避免重复发布事件
            self.data_manager._hovered_shape = hovered_shape
    
    def _handle_idle_mouse_press(self, pos: QPointF, hit_target: Dict[str, Any]) -> None:
        """处理空闲状态下的鼠标按下"""
        hit_type = hit_target['type']
        
        # 确保清理任何残留的临时数据
        self._cleanup_temp_data()
        
        if hit_type == 'control_point':
            # 开始缩放
            self.drag_start_control_point = hit_target['target']
            self.drag_start_shape = hit_target['shape']
            self.drag_start_pos = pos
            # 记录缩放开始时的控制点位置
            self.scale_start_pos = self.drag_start_control_point.position
            self._change_state(OperationState.SCALING)
            
        elif hit_type == 'shape':
            # 开始移动
            self.drag_start_shape = hit_target['target']
            self.drag_start_pos = pos
            # 记录移动开始时的鼠标位置和图形位置
            self.move_start_mouse_pos = pos
            if hasattr(self.drag_start_shape, 'get_position'):
                self.move_start_shape_pos = self.drag_start_shape.get_position()
            elif hasattr(self.drag_start_shape, 'get_center'):
                self.move_start_shape_pos = self.drag_start_shape.get_center()
            else:
                self.move_start_shape_pos = QPointF(0, 0)
            self.data_manager.select_shape(hit_target['target'])
            self._change_state(OperationState.MOVING)
            
        else:
            # 空白区域，根据当前工具创建图形
            current_tool = self.data_manager.get_current_tool()
            
            if current_tool == DrawType.POINT:
                self._change_state(OperationState.CREATING_POINT)
            elif current_tool == DrawType.RECTANGLE:
                self.drag_start_pos = pos
                self._change_state(OperationState.CREATING_RECT)
            elif current_tool == DrawType.ELLIPSE:
                self.drag_start_pos = pos
                self._change_state(OperationState.CREATING_ELLIPSE)
            elif current_tool == DrawType.POLYGON:
                self.polygon_vertices = [pos]
                self.temp_polygon = None  # 重置临时多边形
                self._change_state(OperationState.CREATING_POLYGON)
    
    def _handle_polygon_mouse_press(self, pos: QPointF, hit_target: Dict[str, Any], pixel_size: float = InteractionConstants.DEFAULT_PIXEL_SIZE) -> None:
        """处理多边形创建过程中的鼠标按下"""
        hit_type = hit_target['type']
        
        if hit_type == 'none':
            # 检查是否点击了起始点附近（完成多边形创建）
            if len(self.polygon_vertices) >= InteractionConstants.POLYGON_MIN_VERTICES and self.polygon_vertices:
                start_point = self.polygon_vertices[0]
                distance = GeometryUtils.distance_between_points(pos, start_point)
                # 使用像素距离而不是世界距离来判断
                pixel_distance = distance / pixel_size if pixel_size > 0 else distance
                
                if pixel_distance <= InteractionConstants.POLYGON_SNAP_DISTANCE:
                    # 如果检测到吸附，完成多边形创建
                    self._finish_creating_polygon()
                    return
            
            # 添加顶点
            self.polygon_vertices.append(pos)
        else:
            # 点击了图形，完成多边形创建
            self._finish_creating_polygon()
    
    def _handle_moving(self, pos: QPointF, dragging: bool) -> None:
        """处理移动状态"""
        if not dragging or not self.drag_start_shape or not self.drag_start_pos:
            return
        
        # 检查是否启用网格吸附
        if Config().is_snap_to_grid():
            # 应用网格吸附
            snapped_pos = self._apply_snap_to_grid(pos)
        else:
            # 自由移动，不应用网格吸附
            snapped_pos = pos
        
        # 计算从开始位置到当前位置的总偏移量
        total_offset = snapped_pos - self.drag_start_pos
        
        # 直接设置图形的绝对位置（实时预览）
        if hasattr(self, 'move_start_shape_pos') and self.move_start_shape_pos:
            new_position = self.move_start_shape_pos + total_offset
            
            # 直接设置绝对位置，避免增量移动
            if hasattr(self.drag_start_shape, 'set_position'):
                self.drag_start_shape.set_position(new_position)
            elif hasattr(self.drag_start_shape, 'set_center'):
                self.drag_start_shape.set_center(new_position)
        
        # 发布图形更新事件
        self.event_bus.publish(Event(
            EventType.SHAPE_UPDATED,
            {'shape': self.drag_start_shape}
        ))
    
    def _handle_scaling(self, pos: QPointF, dragging: bool) -> None:
        """处理缩放状态"""
        if not dragging or not self.drag_start_shape or not self.drag_start_control_point:
            return
        
        # 检查是否启用网格吸附
        if Config().is_snap_to_grid():
            # 应用网格吸附
            snapped_pos = self._apply_snap_to_grid(pos)
        else:
            # 自由缩放，不应用网格吸附
            snapped_pos = pos
        
        # 实时更新图形缩放
        if (hasattr(self.drag_start_shape, 'scale_by_control_point') and 
            hasattr(self, 'scale_start_pos') and self.scale_start_pos):
            # 直接缩放到新位置（绝对缩放）
            self.drag_start_shape.scale_by_control_point(
                self.drag_start_control_point, 
                snapped_pos
            )
        
        # 发布图形更新事件
        self.event_bus.publish(Event(
            EventType.SHAPE_UPDATED,
            {'shape': self.drag_start_shape}
        ))
    
    def _handle_creating_rect(self, pos: QPointF, dragging: bool) -> None:
        """处理矩形创建"""
        if not dragging or not self.drag_start_pos:
            return
        
        # 创建或更新临时矩形
        temp_shape = self.data_manager.get_temp_shape()
        if not temp_shape or temp_shape.shape_type != DrawType.RECTANGLE:
            # 创建新的临时矩形
            temp_shape = self.shape_creation_service.create_temp_shape(
                DrawType.RECTANGLE,
                start_point=self.drag_start_pos,
                end_point=pos,
                color=self.data_manager.get_current_color(),
                pen_width=self.data_manager.get_current_width()
            )
        else:
            # 更新现有临时矩形
            self.shape_creation_service.update_temp_shape(temp_shape, end_point=pos)
    
    def _handle_creating_ellipse(self, pos: QPointF, dragging: bool) -> None:
        """处理椭圆创建"""
        if not dragging or not self.drag_start_pos:
            return
        
        # 创建或更新临时椭圆
        temp_shape = self.data_manager.get_temp_shape()
        if not temp_shape or temp_shape.shape_type != DrawType.ELLIPSE:
            # 创建新的临时椭圆
            temp_shape = self.shape_creation_service.create_temp_shape(
                DrawType.ELLIPSE,
                start_point=self.drag_start_pos,
                end_point=pos,
                color=self.data_manager.get_current_color(),
                pen_width=self.data_manager.get_current_width()
            )
        else:
            # 更新现有临时椭圆
            self.shape_creation_service.update_temp_shape(temp_shape, end_point=pos)
    
    def _handle_creating_polygon(self, pos: QPointF, dragging: bool, pixel_size: float = InteractionConstants.DEFAULT_PIXEL_SIZE) -> None:
        """处理多边形创建"""
        if not self.polygon_vertices:
            return
        
        # 检查是否靠近第一个点（吸附检测）
        preview_pos = pos
        is_snapped_to_start = False
        if len(self.polygon_vertices) >= InteractionConstants.POLYGON_MIN_VERTICES:
            first_vertex = self.polygon_vertices[0]
            # 计算两点间距离
            world_distance = GeometryUtils.distance_between_points(pos, first_vertex)
            
            # 计算像素距离
            pixel_distance = world_distance / pixel_size if pixel_size > 0 else 0
            
            if pixel_distance <= InteractionConstants.POLYGON_SNAP_DISTANCE:
                # 如果检测到吸附，预览位置设为第一个顶点
                preview_pos = first_vertex
                is_snapped_to_start = True
        
        # 创建或更新临时多边形
        temp_vertices = self.polygon_vertices + [preview_pos]
        
        # 如果是第一次创建临时多边形，创建新对象
        if self.temp_polygon is None:
            self.temp_polygon = self.shape_creation_service.create_temp_shape(
                DrawType.POLYGON,
                vertices=temp_vertices,
                color=self.data_manager.get_current_color(),
                pen_width=self.data_manager.get_current_width()
            )
        else:
            # 更新现有临时多边形的顶点，但不设置closed=True来避免显示预览线
            self.shape_creation_service.update_temp_shape(
                self.temp_polygon, 
                vertices=temp_vertices.copy(),
                closed=False  # 始终设置为False，不显示预览线
            )
    
    def _finish_creating_point(self, pos: QPointF) -> None:
        """完成点创建"""
        self.shape_creation_service.create_and_add_shape(
            DrawType.POINT,
            position=pos,
            color=self.data_manager.get_current_color(),
            pen_width=self.data_manager.get_current_width()
        )
    
    def _finish_creating_rect(self, pos: QPointF) -> None:
        """完成矩形创建"""
        temp_shape = self.data_manager.get_temp_shape()
        if temp_shape and temp_shape.shape_type == DrawType.RECTANGLE:
            temp_shape.set_end_point(pos)
            self.shape_creation_service.finish_temp_shape_creation(temp_shape)
    
    def _finish_creating_ellipse(self, pos: QPointF) -> None:
        """完成椭圆创建"""
        temp_shape = self.data_manager.get_temp_shape()
        if temp_shape and temp_shape.shape_type == DrawType.ELLIPSE:
            temp_shape.set_end_point(pos)
            self.shape_creation_service.finish_temp_shape_creation(temp_shape)
    
    def _finish_creating_polygon(self) -> None:
        """完成多边形创建"""
        if len(self.polygon_vertices) >= InteractionConstants.POLYGON_MIN_VERTICES:  # 至少需要3个顶点
            # 先清理临时多边形显示
            if self.temp_polygon:
                # 发布事件移除临时多边形
                self.event_bus.publish(Event(
                    EventType.SHAPE_REMOVED,
                    {'shape': self.temp_polygon, 'index': -1}
                ))
            
            # 创建正式的多边形
            self.shape_creation_service.create_and_add_shape(
                DrawType.POLYGON,
                vertices=self.polygon_vertices,
                color=self.data_manager.get_current_color(),
                pen_width=self.data_manager.get_current_width()
            )
        
        # 清理临时数据
        self.polygon_vertices = []
        self.temp_polygon = None
        self.data_manager.set_temp_shape(None)
        
        # 强制清理显示缓存
        self.event_bus.publish(Event(
            EventType.DISPLAY_UPDATE_REQUESTED,
            {'clear_temp': True, 'force_cleanup': True}
        ))
        
        # 回到空闲状态
        self._change_state(OperationState.IDLE)
    
    def _cleanup_temp_data(self) -> None:
        """清理临时数据"""
        # 清理多边形相关临时数据
        if self.polygon_vertices or self.temp_polygon:
            self.polygon_vertices = []
            if self.temp_polygon:
                # 发布事件移除临时多边形
                self.event_bus.publish(Event(
                    EventType.SHAPE_REMOVED,
                    {'shape': self.temp_polygon, 'index': -1}
                ))
            self.temp_polygon = None
            self.data_manager.set_temp_shape(None)
    
    def _cancel_creating_polygon(self) -> None:
        """取消多边形创建"""
        # 检查是否有顶点需要确认
        if len(self.polygon_vertices) > InteractionConstants.POLYGON_CANCEL_MIN_VERTICES:
            # 发布确认取消事件，让UI层处理弹窗
            self.event_bus.publish(Event(
                EventType.CONFIRM_CANCEL_POLYGON,
                {'vertex_count': len(self.polygon_vertices)}
            ))
        else:
            # 没有顶点或只有一个顶点，直接取消
            self._do_cancel_polygon()
    
    def _do_cancel_polygon(self) -> None:
        """执行多边形取消操作"""
        # 先清理临时多边形显示
        if self.temp_polygon:
            # 发布事件移除临时多边形
            self.event_bus.publish(Event(
                EventType.SHAPE_REMOVED,
                {'shape': self.temp_polygon, 'index': -1}
            ))
        
        # 清理临时数据
        self.polygon_vertices = []
        self.temp_polygon = None
        self.data_manager.set_temp_shape(None)
        
        # 回到空闲状态
        self._change_state(OperationState.IDLE)
    
    def _finish_moving(self, pos: QPointF) -> None:
        """完成移动"""
        # 如果有移动距离，记录移动操作
        if (self.drag_start_shape and hasattr(self, 'move_start_mouse_pos') and 
            hasattr(self, 'move_start_shape_pos') and self.move_start_mouse_pos and self.move_start_shape_pos):
            
            # 计算总的移动距离（从开始到结束）
            total_mouse_offset = pos - self.move_start_mouse_pos
            
            # 如果有实际移动，记录操作
            if total_mouse_offset.x() != 0 or total_mouse_offset.y() != 0:
                # 通过操作管理器执行移动操作
                if self.operation_manager:
                    from ..operations import MoveOperation
                    move_operation = MoveOperation(
                        [self.drag_start_shape], 
                        total_mouse_offset,
                        f"移动{self.drag_start_shape.shape_type.name}图形",
                        already_executed=True  # 标记为已执行，因为图形已经在实时预览中移动
                    )
                    self.operation_manager.execute_operation(move_operation)
                    
                    # 发布移动事件
                    self.event_bus.publish(Event(
                        EventType.SHAPE_UPDATED,
                        {
                            'shape': self.drag_start_shape,
                            'update_type': 'move'
                        }
                    ))
                    
                    # 触发显示更新
                    self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
        
        # 清理临时数据
        self.drag_start_shape = None
        self.drag_start_pos = None
        if hasattr(self, 'move_start_mouse_pos'):
            self.move_start_mouse_pos = None
        if hasattr(self, 'move_start_shape_pos'):
            self.move_start_shape_pos = None
    
    def _finish_scaling(self, pos: QPointF) -> None:
        """完成缩放"""
        # 如果有缩放变化，记录缩放操作
        if (self.drag_start_shape and self.drag_start_control_point and 
            hasattr(self, 'scale_start_pos') and self.scale_start_pos):
            
            # 计算最终的缩放变化
            final_control_point_pos = self.drag_start_control_point.position
            scale_offset = final_control_point_pos - self.scale_start_pos
            
            # 如果有实际缩放变化，记录操作
            if scale_offset.x() != 0 or scale_offset.y() != 0:
                # 通过操作管理器执行缩放操作
                if self.operation_manager:
                    from ..operations import ScaleOperation
                    scale_operation = ScaleOperation(
                        self.drag_start_shape,
                        self.drag_start_control_point,
                        self.scale_start_pos,
                        final_control_point_pos,
                        f"缩放{self.drag_start_shape.shape_type.name}图形",
                        already_executed=True  # 标记为已执行，因为图形已经在实时预览中缩放
                    )
                    self.operation_manager.execute_operation(scale_operation)
                    
                    # 发布修改事件
                    self.event_bus.publish(Event(
                        EventType.SHAPE_UPDATED,
                        {
                            'shape': self.drag_start_shape,
                            'update_type': 'modify'
                        }
                    ))
                    
                    # 触发显示更新
                    self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
        
        # 清理临时数据
        self.drag_start_shape = None
        self.drag_start_control_point = None
        self.drag_start_pos = None
        if hasattr(self, 'scale_start_pos'):
            self.scale_start_pos = None
    
    def _get_hit_target(self, pos: QPointF, pixel_size: float = InteractionConstants.DEFAULT_PIXEL_SIZE) -> Dict[str, Any]:
        """获取命中目标"""
        return self.data_manager.get_hit_target(pos, pixel_size)
    
    
    
    def _apply_snap_to_grid(self, pos: QPointF) -> QPointF:
        """应用网格吸附"""
        config = Config()
        grid_size = config.get_grid_size()
        return GeometryUtils.snap_to_grid(pos, grid_size)
    
    def _change_state(self, new_state: OperationState) -> None:
        """改变状态并发布事件"""
        if new_state != self.current_state:
            old_state = self.current_state
            self.current_state = new_state
            
            # 发布状态变化事件
            self.event_bus.publish(Event(
                EventType.STATE_CHANGED,
                {'old_state': old_state, 'new_state': new_state}
            ))
    
    def get_current_state(self) -> OperationState:
        """获取当前状态"""
        return self.current_state
    
    def cleanup(self) -> None:
        """清理资源"""
        from ..utils.logger import get_logger
        logger = get_logger(__name__)
        logger.debug("状态管理器开始清理资源")
        
        # 取消所有事件订阅
        if hasattr(self, '_event_handlers') and self._event_handlers:
            for event_type, handler in self._event_handlers.items():
                self.event_bus.unsubscribe(event_type, handler)
            self._event_handlers.clear()
        
        # 重置状态
        self.current_state = OperationState.IDLE
        self.temp_shape = None
        
        logger.debug("状态管理器资源清理完成")
