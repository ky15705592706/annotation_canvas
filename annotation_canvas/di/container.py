"""
依赖注入容器

提供完善的依赖注入功能，用于管理模块之间的依赖关系。
"""

from typing import Any, Dict, Type, TypeVar, Callable, Optional, List, Set
from ..utils.logger import get_logger

logger = get_logger(__name__)

T = TypeVar('T')


class DIContainer:
    """依赖注入容器"""
    
    def __init__(self):
        self._services: Dict[Type, Type] = {}  # 接口 -> 实现类
        self._factories: Dict[Type, Callable] = {}  # 接口 -> 工厂函数
        self._singletons: Dict[Type, Any] = {}  # 接口 -> 单例实例
        self._scoped: Dict[Type, Any] = {}  # 接口 -> 作用域实例
        self._dependencies: Dict[Type, List[Type]] = {}  # 接口 -> 依赖列表
        self._initialization_order: List[Type] = []  # 初始化顺序
        self._initialized: Set[Type] = set()  # 已初始化的服务
    
    def register_singleton(self, interface: Type[T], implementation: Type[T], dependencies: List[Type] = None) -> None:
        """注册单例服务"""
        self._services[interface] = implementation
        self._dependencies[interface] = dependencies or []
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """注册工厂函数"""
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """注册实例"""
        self._singletons[interface] = instance
        self._initialized.add(interface)
    
    def register_scoped(self, interface: Type[T], implementation: Type[T], dependencies: List[Type] = None) -> None:
        """注册作用域服务（每次请求都创建新实例）"""
        self._services[interface] = implementation
        self._dependencies[interface] = dependencies or []
    
    def get(self, interface: Type[T]) -> T:
        """获取服务实例"""
        # 首先检查单例实例
        if interface in self._singletons:
            return self._singletons[interface]
        
        # 检查作用域实例
        if interface in self._scoped:
            return self._scoped[interface]
        
        # 检查工厂函数
        if interface in self._factories:
            instance = self._factories[interface]()
            return instance
        
        # 检查服务类
        if interface in self._services:
            # 检查是否已经初始化
            if interface in self._initialized:
                return self._singletons.get(interface) or self._scoped.get(interface)
            
            # 创建实例
            instance = self._create_instance(interface)
            
            # 根据注册类型决定存储方式
            if interface in self._services and interface not in self._factories:
                # 单例服务
                self._singletons[interface] = instance
            else:
                # 作用域服务
                self._scoped[interface] = instance
            
            self._initialized.add(interface)
            return instance
        
        raise ValueError(f"未找到服务: {interface.__name__}")
    
    def _create_instance(self, interface: Type[T]) -> T:
        """创建服务实例"""
        implementation = self._services[interface]
        dependencies = self._dependencies.get(interface, [])
        
        # 解析依赖
        resolved_dependencies = []
        for dep in dependencies:
            resolved_dep = self.get(dep)
            resolved_dependencies.append(resolved_dep)
        
        # 创建实例
        try:
            if resolved_dependencies:
                instance = implementation(*resolved_dependencies)
            else:
                instance = implementation()
            return instance
        except Exception as e:
            logger.error(f"创建实例失败: {interface.__name__}, 错误: {e}")
            raise
    
    def get_all(self, interface: Type[T]) -> List[T]:
        """获取所有实现指定接口的服务"""
        instances = []
        for service_interface, implementation in self._services.items():
            if issubclass(implementation, interface):
                instances.append(self.get(service_interface))
        return instances
    
    def is_registered(self, interface: Type[T]) -> bool:
        """检查服务是否已注册"""
        return (interface in self._services or 
                interface in self._factories or 
                interface in self._singletons)
    
    def clear(self) -> None:
        """清空容器"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()
        self._scoped.clear()
        self._dependencies.clear()
        self._initialization_order.clear()
        self._initialized.clear()
    
    def get_registration_info(self) -> Dict[str, Any]:
        """获取注册信息"""
        return {
            'services': {k.__name__: v.__name__ for k, v in self._services.items()},
            'factories': {k.__name__: v.__name__ for k, v in self._factories.items()},
            'singletons': {k.__name__: type(v).__name__ for k, v in self._singletons.items()},
            'dependencies': {k.__name__: [d.__name__ for d in v] for k, v in self._dependencies.items()},
            'initialized': [k.__name__ for k in self._initialized]
        }
