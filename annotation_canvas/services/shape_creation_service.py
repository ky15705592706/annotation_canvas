"""
图形创建服务 - 提供统一的图形创建逻辑
"""

from typing import Optional
from PySide6.QtCore import QPointF

from ..events import EventBus, Event, EventType
from ..core import DrawType, DrawColor, PenWidth
from ..models import BaseShape
from ..factories import ShapeFactory
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ShapeCreationService:
    """图形创建服务 - 提供统一的图形创建逻辑"""
    
    def __init__(self, event_bus: EventBus, data_manager, operation_manager=None):
        """
        初始化图形创建服务
        
        Args:
            event_bus: 事件总线
            data_manager: 数据管理器
            operation_manager: 操作管理器（可选）
        """
        self.event_bus = event_bus
        self.data_manager = data_manager
        self.operation_manager = operation_manager
    
    def create_and_add_shape(self, shape_type: DrawType, **kwargs) -> Optional[BaseShape]:
        """
        创建图形并添加到数据管理器
        
        Args:
            shape_type: 图形类型
            **kwargs: 图形参数
            
        Returns:
            创建的图形对象
        """
        try:
            # 使用工厂创建图形
            shape = ShapeFactory.create_shape(shape_type, **kwargs)
            if not shape:
                logger.error(f"创建图形失败: {shape_type}")
                return None
            
            # 通过操作管理器执行创建操作
            if self.operation_manager:
                from ..operations import CreateOperation
                description = self._generate_description(shape_type, shape, **kwargs)
                create_operation = CreateOperation(shape, self.data_manager, description)
                self.operation_manager.execute_operation(create_operation)
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
                # 自动选中新创建的图形
                self.data_manager.select_shape(shape)
            else:
                # 如果没有操作管理器，直接添加
                self.data_manager.add_shape(shape)
                self.data_manager.select_shape(shape)
            
            return shape
            
        except Exception as e:
            logger.error(f"创建图形失败: {e}")
            return None
    
    def create_temp_shape(self, shape_type: DrawType, **kwargs) -> Optional[BaseShape]:
        """
        创建临时图形
        
        Args:
            shape_type: 图形类型
            **kwargs: 图形参数
            
        Returns:
            创建的临时图形对象
        """
        try:
            # 使用工厂创建图形
            shape = ShapeFactory.create_shape(shape_type, **kwargs)
            if not shape:
                logger.error(f"创建临时图形失败: {shape_type}")
                return None
            
            # 设置为临时图形
            self.data_manager.set_temp_shape(shape)
            
            # 发布图形更新事件
            self.event_bus.publish(Event(
                EventType.SHAPE_UPDATED,
                {'shape': shape}
            ))
            
            return shape
            
        except Exception as e:
            logger.error(f"创建临时图形失败: {e}")
            return None
    
    def update_temp_shape(self, shape: BaseShape, **kwargs) -> bool:
        """
        更新临时图形
        
        Args:
            shape: 要更新的图形
            **kwargs: 更新参数
            
        Returns:
            是否更新成功
        """
        try:
            if not shape:
                return False
            
            # 根据图形类型更新
            if shape.shape_type == DrawType.RECTANGLE:
                if 'end_point' in kwargs:
                    shape.set_end_point(kwargs['end_point'])
            elif shape.shape_type == DrawType.ELLIPSE:
                if 'end_point' in kwargs:
                    shape.set_end_point(kwargs['end_point'])
            elif shape.shape_type == DrawType.POLYGON:
                if 'vertices' in kwargs:
                    shape.vertices = kwargs['vertices'].copy()
                if 'closed' in kwargs:
                    shape.closed = kwargs['closed']
            
            # 发布图形更新事件
            self.event_bus.publish(Event(
                EventType.SHAPE_UPDATED,
                {'shape': shape}
            ))
            
            return True
            
        except Exception as e:
            logger.error(f"更新临时图形失败: {e}")
            return False
    
    def finish_temp_shape_creation(self, shape: BaseShape) -> bool:
        """
        完成临时图形创建，将其转换为正式图形
        
        Args:
            shape: 临时图形
            
        Returns:
            是否成功完成创建
        """
        try:
            if not shape:
                return False
            
            # 通过操作管理器执行创建操作
            if self.operation_manager:
                from ..operations import CreateOperation
                description = self._generate_description(shape.shape_type, shape)
                create_operation = CreateOperation(shape, self.data_manager, description)
                self.operation_manager.execute_operation(create_operation)
                # 触发显示更新
                self.event_bus.publish(Event(EventType.DISPLAY_UPDATE_REQUESTED))
                # 自动选中新创建的图形
                self.data_manager.select_shape(shape)
            else:
                # 如果没有操作管理器，直接添加
                self.data_manager.add_shape(shape)
                self.data_manager.select_shape(shape)
            
            # 清理临时图形
            self.data_manager.set_temp_shape(None)
            
            return True
            
        except Exception as e:
            logger.error(f"完成图形创建失败: {e}")
            return False
    
    def _generate_description(self, shape_type: DrawType, shape: BaseShape, **kwargs) -> str:
        """
        生成操作描述
        
        Args:
            shape_type: 图形类型
            shape: 图形对象
            **kwargs: 额外参数
            
        Returns:
            操作描述
        """
        if shape_type == DrawType.POINT:
            if hasattr(shape, 'position'):
                pos = shape.position
                return f"创建点({pos.x():.1f}, {pos.y():.1f})"
            else:
                return "创建点"
                
        elif shape_type == DrawType.RECTANGLE:
            if hasattr(shape, 'get_start_point') and hasattr(shape, 'get_end_point'):
                start = shape.get_start_point()
                end = shape.get_end_point()
                return f"创建矩形({start.x():.1f}, {start.y():.1f}) -> ({end.x():.1f}, {end.y():.1f})"
            else:
                return "创建矩形"
                
        elif shape_type == DrawType.ELLIPSE:
            if hasattr(shape, 'get_start_point') and hasattr(shape, 'get_end_point'):
                start = shape.get_start_point()
                end = shape.get_end_point()
                return f"创建椭圆({start.x():.1f}, {start.y():.1f}) -> ({end.x():.1f}, {end.y():.1f})"
            else:
                return "创建椭圆"
                
        elif shape_type == DrawType.POLYGON:
            if hasattr(shape, 'vertices'):
                vertex_count = len(shape.vertices)
                return f"创建多边形({vertex_count}个顶点)"
            else:
                return "创建多边形"
        
        return f"创建{shape_type.name}图形"
