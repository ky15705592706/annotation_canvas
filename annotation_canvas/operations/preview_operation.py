"""
预览操作基类 - 处理实时预览相关的操作逻辑
"""

from abc import abstractmethod
from typing import Any, Dict
from PySide6.QtCore import QPointF
from .stateful_operation import StatefulOperation


class PreviewOperation(StatefulOperation):
    """支持实时预览的操作基类"""
    
    def __init__(self, description: str = "", already_executed: bool = False):
        super().__init__(description)
        self.already_executed = already_executed  # 标记是否已经执行过（实时预览中）
    
    def _execute_with_preview_check(self) -> bool:
        """执行操作（带预览检查）"""
        # 如果已经执行过（实时预览中），则不需要再次执行
        if self.already_executed:
            return True
        
        return self._do_execute()
    
    def _redo_always(self) -> bool:
        """重做操作（总是执行）"""
        # 重做时总是执行，不管already_executed状态
        return self._do_execute()
    
    @abstractmethod
    def _do_execute(self) -> bool:
        """实际执行操作 - 子类必须实现"""
        pass
    
    @abstractmethod
    def _do_undo(self) -> bool:
        """实际撤销操作 - 子类必须实现"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'already_executed': self.already_executed
        })
        return base_dict
