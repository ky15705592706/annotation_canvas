"""
AnnotationCanvas - 功能强大的图形标注画布组件

这是一个基于 PySide6 和 PyQtGraph 的图形标注画布组件，支持多种图形类型、
交互操作、撤销重做等功能。

主要特性：
- 支持点、矩形、椭圆、多边形等多种图形类型
- 实时预览和交互操作
- 完整的撤销重做系统
- 图形悬停高亮和控制点操作
- 网格吸附和坐标转换
- 事件驱动的架构设计
- 高度可扩展的渲染策略模式

使用示例：
    from annotation_canvas import AnnotationCanvas
    from PySide6.QtWidgets import QApplication
    
    app = QApplication([])
    canvas = AnnotationCanvas()
    canvas.show()
    app.exec()
"""

__version__ = "1.0.0"
__author__ = "KY"
__email__ = "1980983959@qq.com"
__license__ = "GPL-3.0"

# 导入主要组件
from .ui.annotation_canvas import AnnotationCanvas
from .ui.annotation_controller import AnnotationController

# 导入核心类
from .core.enums import DrawType, DrawColor, PenWidth, ControlPointType
from .models.shape import BaseShape
from .models.point import PointShape
from .models.rectangle import RectangleShape
from .models.ellipse import EllipseShape
from .models.polygon import PolygonShape

# 导入工具类
from .utils.constants import AppConstants, CanvasConstants, InteractionConstants, DisplayConstants, ColorConstants
from .utils.config import Config
from .utils.logger import get_logger

# 导入事件系统
from .events.event import Event, EventType
from .events.event_bus import EventBus
from .events.event_handler_base import EventHandlerBase

# 导入操作管理
from .operations.operation_manager import OperationManager
from .operations.base_operation import BaseOperation
from .operations.create_operation import CreateOperation
from .operations.delete_operation import DeleteOperation
from .operations.move_operation import MoveOperation
from .operations.scale_operation import ScaleOperation
from .operations.import_operation import ImportOperation

# 导入工厂和服务
from .factories.shape_factory import ShapeFactory
from .services.shape_creation_service import ShapeCreationService

# 导入渲染策略
from .render.optimized_render_factory import OptimizedRenderFactory as RenderStrategyFactory

# 定义公开的API
__all__ = [
    # 版本信息
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # 主要组件
    "AnnotationCanvas",
    "AnnotationController",
    
    # 核心枚举
    "DrawType",
    "DrawColor", 
    "PenWidth",
    "ControlPointType",
    
    # 图形模型
    "BaseShape",
    "PointShape",
    "RectangleShape",
    "EllipseShape",
    "PolygonShape",
    
    # 工具类
    "AppConstants",
    "CanvasConstants",
    "InteractionConstants",
    "DisplayConstants",
    "ColorConstants",
    "Config",
    "get_logger",
    
    # 事件系统
    "Event",
    "EventType",
    "EventBus",
    "EventHandlerBase",
    
    # 操作管理
    "OperationManager",
    "BaseOperation",
    "CreateOperation",
    "DeleteOperation",
    "MoveOperation",
    "ScaleOperation",
    "ImportOperation",
    
    # 工厂和服务
    "ShapeFactory",
    "ShapeCreationService",
    
    # 渲染策略
    "RenderStrategyFactory",
]

# 便捷函数
def create_canvas(parent=None):
    """
    创建一个配置好的 AnnotationCanvas 实例
    
    Args:
        parent: 父窗口组件（当前版本忽略此参数）
        
    Returns:
        AnnotationCanvas: 配置好的画布实例
    """
    return AnnotationCanvas()

def create_demo_app():
    """
    创建一个演示应用程序
    
    Returns:
        QApplication: 配置好的应用程序实例
    """
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
    from PySide6.QtCore import Qt
    
    app = QApplication([])
    
    # 创建主窗口
    window = QMainWindow()
    window.setWindowTitle("AnnotationCanvas Demo")
    window.resize(800, 600)
    
    # 创建画布
    canvas = create_canvas()
    
    # 设置中央组件
    central_widget = QWidget()
    layout = QVBoxLayout(central_widget)
    layout.addWidget(canvas)
    window.setCentralWidget(central_widget)
    
    # 显示窗口
    window.show()
    
    return app, window, canvas
