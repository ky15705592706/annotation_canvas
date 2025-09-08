# This Python file uses the following encoding: utf-8

"""
枚举定义 - 定义所有使用的枚举类型
"""

from enum import Enum, IntEnum

class DrawType(IntEnum):
    """图形类型枚举"""
    NONE = 0
    POINT = 1      # 点：只需要一个点
    RECTANGLE = 2  # 矩形：只需要两个对角点
    ELLIPSE = 3    # 椭圆：矩形内接椭圆，只需要两个对角点
    POLYGON = 4    # 多边形：需要多个点

class DrawColor(IntEnum):
    """颜色枚举"""
    NONE = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    PURPLE = 5
    ORANGE = 6
    BLACK = 7
    WHITE = 8

class PenWidth(IntEnum):
    """线宽枚举"""
    NONE = 0
    THIN = 1
    MEDIUM = 2
    THICK = 3
    ULTRA_THIN = 4
    ULTRA_THICK = 5

class ControlPointType(IntEnum):
    """控制点类型枚举"""
    CENTER = 0     # 中心点
    CORNER = 1     # 角点
    EDGE = 2       # 边中点
    VERTEX = 3     # 顶点
    CUSTOM = 4     # 自定义控制点

class OperationState(IntEnum):
    """操作状态枚举"""
    IDLE = 0           # 空闲状态
    CREATING_POINT = 1 # 创建点
    CREATING_RECT = 2  # 创建矩形
    CREATING_ELLIPSE = 3 # 创建椭圆
    CREATING_POLYGON = 4 # 创建多边形
    MOVING = 5         # 移动图形
    SCALING = 6        # 缩放图形
    SELECTING = 7      # 选择图形

class InteractionMode(IntEnum):
    """交互模式枚举"""
    VIEW = 0        # 视图模式（平移、缩放）
    DRAW = 1        # 绘制模式
    EDIT = 2        # 编辑模式
    MEASURE = 3     # 测量模式
    ANNOTATE = 4    # 标注模式

class MouseLocation(Enum):
    """鼠标位置枚举"""
    NONE = "none"                    # 空白区域
    SHAPE = "shape"                  # 在图形上（非控制点）
    CONTROL_POINT = "control_point"  # 在控制点上
    SHAPE_CENTER = "shape_center"    # 在图形中心区域

class MouseButtonState(Enum):
    """鼠标按键状态枚举"""
    NONE = "none"              # 无按键
    PRESSED = "pressed"        # 按键按下
    DRAGGING = "dragging"      # 按键按下并拖拽
    RELEASED = "released"      # 按键释放

class ScaleMode(IntEnum):
    """缩放模式枚举"""
    FREE = 0           # 自由缩放
    PROPORTIONAL = 1   # 等比例缩放
    CONSTRAINED = 2    # 约束缩放（保持宽高比）
    GRID_SNAP = 3      # 网格对齐缩放
