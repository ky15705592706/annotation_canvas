"""
导入操作 - 支持撤销的图形数据导入
"""

from typing import Dict, Any, List
from .base_operation import BaseOperation
from ..models import BaseShape
from ..core import DrawType, DrawColor, PenWidth
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ImportOperation(BaseOperation):
    """导入操作类 - 支持撤销的图形数据导入"""
    
    def __init__(self, import_data: Dict[str, Any], data_manager, operation_manager):
        """
        初始化导入操作
        
        Args:
            import_data: 要导入的数据字典
            data_manager: 数据管理器
            operation_manager: 操作管理器
        """
        super().__init__()
        self.import_data = import_data
        self.data_manager = data_manager
        self.operation_manager = operation_manager
        
        # 保存导入前的状态
        self.original_shapes: List[BaseShape] = []
        self.original_settings: Dict[str, Any] = {}
        
        # 保存导入的图形
        self.imported_shapes: List[BaseShape] = []
        
        # 操作描述
        self.description = f"导入 {len(import_data.get('shapes', []))} 个图形"
    
    def execute(self) -> bool:
        """
        执行导入操作
        
        Returns:
            是否成功执行
        """
        try:
            # 保存当前状态
            self._save_current_state()
            
            # 清空现有数据
            self.data_manager.clear_all_shapes()
            
            # 导入图形数据
            imported_count = 0
            for shape_data in self.import_data.get('shapes', []):
                shape = self._create_shape_from_dict(shape_data)
                if shape:
                    self.data_manager.add_shape(shape)
                    self.imported_shapes.append(shape)
                    imported_count += 1
            
            # 导入设置
            self._import_settings()
            
            logger.info(f"成功导入 {imported_count} 个图形")
            return True
            
        except Exception as e:
            logger.error(f"导入操作执行失败: {e}")
            return False
    
    def undo(self) -> bool:
        """
        撤销导入操作
        
        Returns:
            是否成功撤销
        """
        try:
            # 清空当前数据
            self.data_manager.clear_all_shapes()
            
            # 恢复原始图形
            for shape in self.original_shapes:
                self.data_manager.add_shape(shape)
            
            # 恢复原始设置
            self._restore_settings()
            
            # 清空导入的图形列表
            self.imported_shapes.clear()
            
            logger.info(f"成功撤销导入操作，恢复了 {len(self.original_shapes)} 个原始图形")
            return True
            
        except Exception as e:
            logger.error(f"撤销导入操作失败: {e}")
            return False
    
    def redo(self) -> bool:
        """
        重做导入操作
        
        Returns:
            是否成功重做
        """
        return self.execute()
    
    def _save_current_state(self) -> None:
        """保存当前状态"""
        # 保存当前图形
        self.original_shapes = self.data_manager.get_shapes().copy()
        
        # 保存当前设置
        self.original_settings = {
            'current_tool': self.data_manager.get_current_tool(),
            'current_color': self.data_manager.get_current_color(),
            'current_width': self.data_manager.get_current_width()
        }
    
    def _import_settings(self) -> None:
        """导入设置"""
        settings = self.import_data.get('settings', {})
        
        if 'current_tool' in settings:
            self.data_manager.set_current_tool(DrawType(settings['current_tool']))
        
        if 'current_color' in settings:
            self.data_manager.set_current_color(DrawColor(settings['current_color']))
        
        if 'current_width' in settings:
            self.data_manager.set_current_width(PenWidth(settings['current_width']))
    
    def _restore_settings(self) -> None:
        """恢复设置"""
        if 'current_tool' in self.original_settings:
            self.data_manager.set_current_tool(self.original_settings['current_tool'])
        
        if 'current_color' in self.original_settings:
            self.data_manager.set_current_color(self.original_settings['current_color'])
        
        if 'current_width' in self.original_settings:
            self.data_manager.set_current_width(self.original_settings['current_width'])
    
    def _create_shape_from_dict(self, shape_data: Dict[str, Any]) -> BaseShape:
        """从字典数据创建图形"""
        from ..factories import ShapeFactory
        return ShapeFactory.create_from_dict(shape_data)
    
    def get_description(self) -> str:
        """获取操作描述"""
        return self.description
    
    def get_imported_shapes(self) -> List[BaseShape]:
        """获取导入的图形列表"""
        return self.imported_shapes.copy()
    
    def get_imported_count(self) -> int:
        """获取导入的图形数量"""
        return len(self.imported_shapes)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式，用于序列化"""
        return {
            'operation_type': 'import',
            'description': self.description,
            'import_data': self.import_data,
            'imported_count': self.get_imported_count()
        }
    
    def __str__(self) -> str:
        return f"ImportOperation(imported={self.get_imported_count()})"
    
    def __repr__(self) -> str:
        return self.__str__()
