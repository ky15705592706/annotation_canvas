"""
日志系统模块
"""

import logging
import sys
from typing import Optional
from pathlib import Path


class Logger:
    """日志管理器"""
    
    _instance: Optional['Logger'] = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._setup_logging()
            self._initialized = True
    
    def _setup_logging(self):
        """设置日志配置"""
        # 创建日志目录
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 配置根日志器
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "annotation_tool.log", encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        # 设置不同模块的日志级别
        logging.getLogger('PySide6').setLevel(logging.WARNING)
        logging.getLogger('pyqtgraph').setLevel(logging.WARNING)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取指定名称的日志器"""
        return logging.getLogger(name)


def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    logger_manager = Logger()
    return logger_manager.get_logger(name)
