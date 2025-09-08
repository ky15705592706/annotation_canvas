"""
状态化操作基类 - 提供通用的状态管理逻辑
"""

from abc import abstractmethod
from typing import Any, Dict, Callable, Optional
from .base_operation import BaseOperation
from ..utils.logger import get_logger

logger = get_logger(__name__)


class StatefulOperation(BaseOperation):
    """状态化操作基类 - 提供通用的状态管理逻辑"""
    
    def __init__(self, description: str = ""):
        super().__init__(description)
        self.executed = False
        self._execute_func: Optional[Callable] = None
        self._undo_func: Optional[Callable] = None
        self._redo_func: Optional[Callable] = None
    
    def set_execute_function(self, func: Callable) -> None:
        """设置执行函数"""
        self._execute_func = func
    
    def set_undo_function(self, func: Callable) -> None:
        """设置撤销函数"""
        self._undo_func = func
    
    def set_redo_function(self, func: Callable) -> None:
        """设置重做函数"""
        self._redo_func = func
    
    def execute(self) -> bool:
        """执行操作"""
        if not self.executed and self._execute_func:
            try:
                result = self._execute_func()
                if result:
                    self.executed = True
                    logger.debug(f"操作执行成功: {self.description}")
                return result
            except Exception as e:
                logger.error(f"操作执行失败: {self.description}, 错误: {e}")
                return False
        return False
    
    def undo(self) -> bool:
        """撤销操作"""
        if self.executed and self._undo_func:
            try:
                result = self._undo_func()
                if result:
                    self.executed = False
                    logger.debug(f"操作撤销成功: {self.description}")
                return result
            except Exception as e:
                logger.error(f"操作撤销失败: {self.description}, 错误: {e}")
                return False
        return False
    
    def redo(self) -> bool:
        """重做操作"""
        if not self.executed and self._redo_func:
            try:
                result = self._redo_func()
                if result:
                    self.executed = True
                    logger.debug(f"操作重做成功: {self.description}")
                return result
            except Exception as e:
                logger.error(f"操作重做失败: {self.description}, 错误: {e}")
                return False
        return False
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return self.executed
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return not self.executed
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'executed': self.executed
        })
        return base_dict
    
    def reset_state(self) -> None:
        """重置操作状态"""
        self.executed = False
        logger.debug(f"操作状态已重置: {self.description}")


class SimpleStatefulOperation(StatefulOperation):
    """简单状态化操作 - 使用函数式接口"""
    
    def __init__(self, description: str, execute_func: Callable, 
                 undo_func: Callable, redo_func: Optional[Callable] = None):
        super().__init__(description)
        self.set_execute_function(execute_func)
        self.set_undo_function(undo_func)
        self.set_redo_function(redo_func or execute_func)  # 默认重做使用执行函数


class BatchStatefulOperation(StatefulOperation):
    """批量状态化操作 - 处理多个子操作"""
    
    def __init__(self, description: str, operations: list):
        super().__init__(description)
        self.operations = operations
        self._setup_batch_functions()
    
    def _setup_batch_functions(self) -> None:
        """设置批量操作函数"""
        self.set_execute_function(self._execute_batch)
        self.set_undo_function(self._undo_batch)
        self.set_redo_function(self._redo_batch)
    
    def _execute_batch(self) -> bool:
        """执行批量操作"""
        success = True
        for operation in self.operations:
            if not operation.execute():
                success = False
        return success
    
    def _undo_batch(self) -> bool:
        """撤销批量操作（逆序）"""
        success = True
        for operation in reversed(self.operations):
            if not operation.undo():
                success = False
        return success
    
    def _redo_batch(self) -> bool:
        """重做批量操作"""
        success = True
        for operation in self.operations:
            if not operation.redo():
                success = False
        return success
    
    def add_operation(self, operation) -> None:
        """添加子操作"""
        self.operations.append(operation)
        self._setup_batch_functions()  # 重新设置函数
    
    def get_operation_count(self) -> int:
        """获取子操作数量"""
        return len(self.operations)
