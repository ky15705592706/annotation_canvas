"""
操作基类 - 定义所有操作的通用接口
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from PySide6.QtCore import QPointF

class BaseOperation(ABC):
    """操作基类"""
    
    def __init__(self, description: str = ""):
        self.description = description
        self.timestamp = None
    
    @abstractmethod
    def execute(self) -> bool:
        """执行操作"""
        pass
    
    @abstractmethod
    def undo(self) -> bool:
        """撤销操作"""
        pass
    
    @abstractmethod
    def redo(self) -> bool:
        """重做操作"""
        pass
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return True
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return True
    
    def get_description(self) -> str:
        """获取操作描述"""
        return self.description
    
    def set_description(self, description: str):
        """设置操作描述"""
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        return {
            'description': self.description,
            'timestamp': self.timestamp,
            'operation_type': self.__class__.__name__
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BaseOperation':
        """从字典创建实例，用于反序列化"""
        # 子类需要实现具体的创建逻辑
        raise NotImplementedError("子类必须实现 from_dict 方法")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}: {self.description}"
    
    def __repr__(self) -> str:
        return self.__str__()

class CompositeOperation(BaseOperation):
    """复合操作 - 包含多个子操作"""
    
    def __init__(self, description: str = "", operations: List[BaseOperation] = None):
        super().__init__(description)
        self.operations = operations or []
    
    def add_operation(self, operation: BaseOperation):
        """添加子操作"""
        self.operations.append(operation)
    
    def execute(self) -> bool:
        """执行所有子操作"""
        success = True
        for operation in self.operations:
            if not operation.execute():
                success = False
        return success
    
    def undo(self) -> bool:
        """撤销所有子操作（逆序）"""
        success = True
        for operation in reversed(self.operations):
            if not operation.undo():
                success = False
        return success
    
    def redo(self) -> bool:
        """重做所有子操作"""
        success = True
        for operation in self.operations:
            if not operation.redo():
                success = False
        return success
    
    def can_undo(self) -> bool:
        """检查是否可以撤销"""
        return all(op.can_undo() for op in self.operations)
    
    def can_redo(self) -> bool:
        """检查是否可以重做"""
        return all(op.can_redo() for op in self.operations)
    
    def get_operation_count(self) -> int:
        """获取子操作数量"""
        return len(self.operations)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        base_dict = super().to_dict()
        base_dict.update({
            'operations': [op.to_dict() for op in self.operations]
        })
        return base_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CompositeOperation':
        """从字典创建实例，用于反序列化"""
        operations = []
        for op_data in data.get('operations', []):
            # 这里需要根据操作类型创建相应的操作实例
            # 简化处理，实际应用中需要更复杂的工厂模式
            pass
        
        return cls(data.get('description', ''), operations)
