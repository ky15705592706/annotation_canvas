"""
依赖注入容器模块

提供依赖注入功能，用于管理模块之间的依赖关系。
"""

from .container import DIContainer
from .decorators import injectable, inject

__all__ = ['DIContainer', 'injectable', 'inject']
