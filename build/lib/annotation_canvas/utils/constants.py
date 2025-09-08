"""
常量定义 - 定义项目中使用的各种常量值
"""

# 应用相关常量
class AppConstants:
    """应用相关常量"""
    
    # 应用信息
    APP_NAME = "标注工具"
    APP_VERSION = "v1.0.0"
    WINDOW_TITLE = f"{APP_NAME} {APP_VERSION}"

# 画布相关常量
class CanvasConstants:
    """画布相关常量"""
    
    # 画布尺寸
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # 默认视图范围
    DEFAULT_X_MIN = -200
    DEFAULT_X_MAX = 200
    DEFAULT_Y_MIN = -200
    DEFAULT_Y_MAX = 200
    
    # 网格设置
    GRID_ALPHA = 0.3
    
    # 布局边距
    LAYOUT_MARGINS = (0, 0, 0, 0)

# 交互相关常量
class InteractionConstants:
    """交互相关常量"""
    
    # 像素容差
    PIXEL_TOLERANCE = 5.0
    
    # 控制点容差
    CONTROL_POINT_TOLERANCE = 12.0
    
    # 控制点默认大小
    CONTROL_POINT_DEFAULT_SIZE = 8.0
    
    # 多边形吸附距离
    POLYGON_SNAP_DISTANCE = 15.0
    
    # 多边形最小顶点数
    POLYGON_MIN_VERTICES = 3
    
    # 多边形确认取消最小顶点数
    POLYGON_CANCEL_MIN_VERTICES = 1
    
    # 最小拖拽距离
    MIN_DRAG_DISTANCE_PIXELS = 10.0
    
    # 图形默认容差
    SHAPE_DEFAULT_TOLERANCE = 5.0
    
    # 图形中心区域比例
    SHAPE_CENTER_RATIO = 0.3
    
    
    # 默认像素大小
    DEFAULT_PIXEL_SIZE = 0.01

# 键盘相关常量
class KeyConstants:
    """键盘相关常量"""
    
    # 功能键
    ESCAPE = 0x01000000  # Qt.Key_Escape
    
    # 字母键
    KEY_A = 0x41
    KEY_G = 0x47
    KEY_Z = 0x5A
    KEY_Y = 0x59
    
    # 数字键
    KEY_1 = 0x31
    KEY_2 = 0x32
    KEY_3 = 0x33
    
    # 特殊键
    KEY_DELETE = 0x01000007  # Qt.Key_Delete
    
# 缩放相关常量
class ZoomConstants:
    """缩放相关常量"""
    
    # 缩放因子计算
    ZOOM_FACTOR_DIVISOR = 1200.0
    
    # 最大放大倍数对应的像素大小
    MAX_ZOOM_PIXEL_SIZE = 1e-6
    

# 图形显示相关常量
class DisplayConstants:
    """图形显示相关常量"""
    
    # 点图形
    POINT_SIZE_NORMAL = 20.0
    POINT_SIZE_HOVER = 25.0
    POINT_WIDTH_NORMAL = 3
    POINT_WIDTH_HOVER = 4
    
    # 控制点
    CONTROL_POINT_SIZE_NORMAL = 8.0
    CONTROL_POINT_SIZE_HOVER = 12.0
    CONTROL_POINT_WIDTH_NORMAL = 2
    CONTROL_POINT_WIDTH_HOVER = 3
    
    # 悬停线宽增加
    HOVER_WIDTH_INCREASE = 2
    
    # 椭圆点数
    ELLIPSE_POINTS_COUNT = 50
    
    # 默认图形参数
    DEFAULT_GRAPHICS_WIDTH = 2
    
    # 缩放比例
    ZOOM_IN_FACTOR = 1.2
    ZOOM_OUT_FACTOR = 0.8
    

# 颜色相关常量
class ColorConstants:
    """颜色相关常量"""
    
    # 控制点颜色
    CONTROL_POINT_DRAGGING = (255, 165, 0)  # 橙色
    CONTROL_POINT_HOVER = (255, 255, 0)     # 黄色
    CONTROL_POINT_CENTER = (0, 120, 215)    # 蓝色
    CONTROL_POINT_CORNER = (255, 0, 0)      # 红色
    CONTROL_POINT_EDGE = (0, 255, 0)        # 绿色
    CONTROL_POINT_VERTEX = (128, 0, 128)    # 紫色
    CONTROL_POINT_DEFAULT = (100, 100, 100) # 灰色
    
    # 图形悬停颜色
    SHAPE_HOVER = (255, 255, 0)  # 黄色
    
    
    # 标准颜色映射
    COLOR_MAP = {
        'RED': (255, 0, 0),
        'GREEN': (0, 255, 0),
        'BLUE': (0, 0, 255),
        'YELLOW': (255, 255, 0),
        'PURPLE': (128, 0, 128),
        'ORANGE': (255, 165, 0),
        'BLACK': (0, 0, 0),
        'WHITE': (255, 255, 255),
    }

# 状态相关常量
class StateConstants:
    """状态相关常量"""
    
    # 状态标签文本
    STATUS_READY = "就绪"
    STATUS_COORDINATE_DRAG = "坐标系拖拽模式 - 拖拽视图"
    STATUS_POLYGON_CLOSE = "点击闭合多边形"
    STATUS_POLYGON_CONTINUE = "继续添加顶点，或按ESC取消"
    
    
    # 初始显示文本
    INITIAL_COORDINATE_TEXT = "坐标: (0, 0)"
    INITIAL_ZOOM_TEXT = "缩放: 1.0x"
    
    # 坐标显示格式
    COORDINATE_FORMAT = "坐标: ({:.1f}, {:.1f})"
    ZOOM_FORMAT = "缩放: {}%"

# 操作相关常量
class OperationConstants:
    """操作相关常量"""
    
    
    # 操作描述
    OPERATION_CREATE_POINT = "创建POINT图形"
    OPERATION_CREATE_RECTANGLE = "创建RECTANGLE图形"
    OPERATION_CREATE_ELLIPSE = "创建ELLIPSE图形"
    OPERATION_CREATE_POLYGON = "创建POLYGON图形"
    OPERATION_MOVE = "移动{}图形"
    OPERATION_SCALE = "缩放{}图形"
    OPERATION_DELETE = "删除{}图形"
