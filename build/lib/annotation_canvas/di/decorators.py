"""
依赖注入装饰器

提供依赖注入相关的装饰器。
"""

from typing import Any, Type, TypeVar, Callable
from functools import wraps

T = TypeVar('T')


def injectable(cls: Type[T]) -> Type[T]:
    """
    标记类为可注入的
    
    Args:
        cls: 要标记的类
        
    Returns:
        标记后的类
    """
    cls._injectable = True
    return cls


def inject(interface: Type[T]) -> T:
    """
    注入依赖
    
    Args:
        interface: 要注入的接口类型
        
    Returns:
        注入的实例
    """
    # 这里简化实现，实际使用时需要从容器中获取
    # 在实际项目中，这通常通过框架或容器来处理
    raise NotImplementedError("inject 装饰器需要配合 DI 容器使用")
