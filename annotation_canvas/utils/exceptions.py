"""
异常处理模块 - 定义项目中的自定义异常
"""


class AnnotationError(Exception):
    """标注工具基础异常"""
    
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
    
    def __str__(self) -> str:
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class ShapeCreationError(AnnotationError):
    """图形创建异常"""
    
    def __init__(self, message: str, shape_type: str = None):
        super().__init__(message, "SHAPE_CREATION_ERROR")
        self.shape_type = shape_type


class ShapeOperationError(AnnotationError):
    """图形操作异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "SHAPE_OPERATION_ERROR")
        self.operation = operation


class EventHandlerError(AnnotationError):
    """事件处理异常"""
    
    def __init__(self, message: str, event_type: str = None):
        super().__init__(message, "EVENT_HANDLER_ERROR")
        self.event_type = event_type


class ConfigError(AnnotationError):
    """配置异常"""
    
    def __init__(self, message: str, config_key: str = None):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key


class DataManagerError(AnnotationError):
    """数据管理异常"""
    
    def __init__(self, message: str, operation: str = None):
        super().__init__(message, "DATA_MANAGER_ERROR")
        self.operation = operation


class StateManagerError(AnnotationError):
    """状态管理异常"""
    
    def __init__(self, message: str, state: str = None):
        super().__init__(message, "STATE_MANAGER_ERROR")
        self.state = state


class RenderError(AnnotationError):
    """渲染异常"""
    
    def __init__(self, message: str, render_type: str = None):
        super().__init__(message, "RENDER_ERROR")
        self.render_type = render_type


class ValidationError(AnnotationError):
    """验证异常"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
