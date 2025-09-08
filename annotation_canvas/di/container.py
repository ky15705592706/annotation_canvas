"""
依赖注入容器

提供简单的依赖注入功能，用于管理模块之间的依赖关系。
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """注册单例服务"""
        self._services[interface] = implementation
        logger.debug(f"注册单例服务: {interface.__name__} -> {implementation.__name__}")
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """注册工厂函数"""
        self._factories[interface] = factory
        logger.debug(f"注册工厂函数: {interface.__name__}")
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """注册实例"""
        self._singletons[interface] = instance
        logger.debug(f"注册实例: {interface.__name__}")
    
    def get(self, interface: Type[T]) -> T:
        """获取服务实例"""
        # 首先检查单例实例
        if interface in self._singletons:
            return self._singletons[interface]
        
        # 检查工厂函数
        if interface in self._factories:
            instance = self._factories[interface]()
            logger.debug(f"通过工厂函数创建实例: {interface.__name__}")
            return instance
        
        # 检查服务类
        if interface in self._services:
            implementation = self._services[interface]
            instance = implementation()
            logger.debug(f"通过服务类创建实例: {interface.__name__}")
            return instance
        
        raise ValueError(f"未找到服务: {interface.__name__}")
    
    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        logger.debug("清空依赖注入容器")
