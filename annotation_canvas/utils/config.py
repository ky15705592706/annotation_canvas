# This Python file uses the following encoding: utf-8

"""
配置管理 - 管理应用程序配置
"""

import json
import os
from typing import Dict, Any, Optional
from ..core.enums import DrawType, DrawColor, PenWidth
from .logger import get_logger
from .exceptions import ConfigError

logger = get_logger(__name__)

class Config:
    """配置管理类 - 单例模式"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls, config_file: str = "config.json"):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, config_file: str = "config.json"):
        if not self._initialized:
            self.config_file = config_file
            self.config = self._load_default_config()
            self._initialized = True
        self.load_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """加载默认配置"""
        return {
            "app": {
                "name": "标注工具",
                "version": "1.0.0",
                "author": "KY"
            },
            "ui": {
                "window_width": 1200,
                "window_height": 800,
                "theme": "light",
                "language": "zh_CN"
            },
            "drawing": {
                "default_tool": DrawType.POINT.value,
                "default_color": DrawColor.RED.value,
                "default_pen_width": PenWidth.MEDIUM.value,
                "snap_to_grid": False,
                "grid_size": 10.0,
                "snap_tolerance": 5.0
            },
            "shapes": {
                "point": {
                    "size": 8.0,
                    "tolerance": 5.0
                },
                "rectangle": {
                    "min_size": 5.0,
                    "tolerance": 5.0
                },
                "ellipse": {
                    "min_size": 5.0,
                    "tolerance": 5.0
                },
                "polygon": {
                    "min_vertices": 3,
                    "snap_distance": 10.0,
                    "tolerance": 5.0
                }
            },
            "control_points": {
                "size": 8.0,
                "tolerance": 8.0,
                "visible": True,
                "colors": {
                    "center": (0, 120, 215),
                    "corner": (255, 0, 0),
                    "edge": (0, 255, 0),
                    "vertex": (128, 0, 128),
                    "custom": (100, 100, 100)
                }
            },
            "operations": {
                "max_history_size": 100,
                "auto_save_interval": 300,  # 秒
                "save_file_format": "json"
            },
            "performance": {
                "max_shapes": 1000,
                "update_interval": 16,  # 毫秒
                "enable_antialiasing": True,
                "enable_opengl": True
            }
        }
    
    def load_config(self) -> bool:
        """从文件加载配置"""
        # 避免重复加载
        if hasattr(self, '_config_loaded'):
            return True
            
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    self._merge_config(loaded_config)
                logger.info(f"配置已从文件加载: {self.config_file}")
                self._config_loaded = True
                return True
            else:
                # 只在第一次加载时打印
                if not hasattr(self, '_default_config_printed'):
                    logger.info(f"配置文件不存在，使用默认配置: {self.config_file}")
                    self._default_config_printed = True
                self._config_loaded = True
                return False
        except Exception as e:
            error_msg = f"加载配置文件失败: {e}"
            logger.error(error_msg)
            self._config_loaded = True
            raise ConfigError(error_msg, config_key=self.config_file) from e
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已保存到文件: {self.config_file}")
            return True
        except Exception as e:
            error_msg = f"保存配置文件失败: {e}"
            logger.error(error_msg)
            raise ConfigError(error_msg, config_key=self.config_file) from e
    
    def _merge_config(self, loaded_config: Dict[str, Any]):
        """合并配置"""
        def merge_dict(base: Dict[str, Any], update: Dict[str, Any]):
            for key, value in update.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    merge_dict(base[key], value)
                else:
                    base[key] = value
        
        merge_dict(self.config, loaded_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        keys = key.split('.')
        config = self.config
        
        # 导航到目标位置
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_app_name(self) -> str:
        """获取应用程序名称"""
        return self.get("app.name", "标注工具")
    
    def get_app_version(self) -> str:
        """获取应用程序版本"""
        return self.get("app.version", "1.0.0")
    
    def get_window_size(self) -> tuple:
        """获取窗口大小"""
        width = self.get("ui.window_width", 1200)
        height = self.get("ui.window_height", 800)
        return (width, height)
    
    def get_default_tool(self) -> DrawType:
        """获取默认工具"""
        tool_value = self.get("drawing.default_tool", DrawType.POINT.value)
        return DrawType(tool_value)
    
    def get_default_color(self) -> DrawColor:
        """获取默认颜色"""
        color_value = self.get("drawing.default_color", DrawColor.RED.value)
        return DrawColor(color_value)
    
    def get_default_pen_width(self) -> PenWidth:
        """获取默认线宽"""
        width_value = self.get("drawing.default_pen_width", PenWidth.MEDIUM.value)
        return PenWidth(width_value)
    
    def is_snap_to_grid(self) -> bool:
        """检查是否启用网格对齐"""
        return self.get("drawing.snap_to_grid", True)
    
    def get_grid_size(self) -> float:
        """获取网格大小"""
        return self.get("drawing.grid_size", 10.0)
    
    def get_snap_tolerance(self) -> float:
        """获取对齐容差"""
        return self.get("drawing.snap_tolerance", 5.0)
    
    def get_control_point_size(self) -> float:
        """获取控制点大小"""
        return self.get("control_points.size", 8.0)
    
    def get_control_point_tolerance(self) -> float:
        """获取控制点容差"""
        return self.get("control_points.tolerance", 8.0)
    
    def get_control_point_color(self, point_type: str) -> tuple:
        """获取控制点颜色"""
        colors = self.get("control_points.colors", {})
        return colors.get(point_type, (100, 100, 100))
    
    def get_max_history_size(self) -> int:
        """获取最大历史记录大小"""
        return self.get("operations.max_history_size", 100)
    
    def get_auto_save_interval(self) -> int:
        """获取自动保存间隔（秒）"""
        return self.get("operations.auto_save_interval", 300)
    
    def get_max_shapes(self) -> int:
        """获取最大图形数量"""
        return self.get("performance.max_shapes", 1000)
    
    def get_update_interval(self) -> int:
        """获取更新间隔（毫秒）"""
        return self.get("performance.update_interval", 16)
    
    def is_antialiasing_enabled(self) -> bool:
        """检查是否启用抗锯齿"""
        return self.get("performance.enable_antialiasing", True)
    
    def is_opengl_enabled(self) -> bool:
        """检查是否启用OpenGL"""
        return self.get("performance.enable_opengl", True)
    
    def reset_to_default(self):
        """重置为默认配置"""
        self.config = self._load_default_config()
        logger.info("配置已重置为默认值")
    
    def export_config(self, filename: str) -> bool:
        """导出配置到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"配置已导出到: {filename}")
            return True
        except Exception as e:
            logger.error(f"导出配置失败: {e}")
            return False
    
    def import_config(self, filename: str) -> bool:
        """从文件导入配置"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
                self._merge_config(imported_config)
            logger.info(f"配置已从文件导入: {filename}")
            return True
        except Exception as e:
            logger.error(f"导入配置失败: {e}")
            return False
    
    def __str__(self) -> str:
        return f"Config(file={self.config_file}, keys={len(self.config)})"
    
    def __repr__(self) -> str:
        return self.__str__()
