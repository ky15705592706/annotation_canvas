"""
新的标注画布 - 使用事件驱动架构
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QMessageBox, QStatusBar
from PySide6.QtCore import Qt, Signal, QPointF, QRectF
from PySide6.QtGui import QMouseEvent, QWheelEvent, QKeyEvent, QKeySequence, QAction

import pyqtgraph as pg
from pyqtgraph import PlotWidget

from ..core import DrawType, DrawColor, PenWidth
from ..models import BaseShape
from ..utils.constants import (
    CanvasConstants, ZoomConstants, StateConstants
)
from ..utils.logger import get_logger
from .annotation_controller import AnnotationController

logger = get_logger(__name__)


class AnnotationCanvas(PlotWidget):
    """新的标注画布类 - 使用事件驱动架构"""
    
    # 信号定义
    shape_selected = Signal(BaseShape)
    shape_deselected = Signal()
    shape_added = Signal(BaseShape)  # 图形添加信号
    shape_moved = Signal(BaseShape)  # 图形移动信号 (修改后的图形)
    shape_modified = Signal(BaseShape)  # 图形修改信号 (修改后的图形)
    shape_deleted = Signal(BaseShape)  # 图形删除信号 (被删除的图形)
    
    def __init__(self):
        super().__init__()
        
        # 初始化状态
        self.annotation_mode: bool = False  # False=默认模式, True=标注模式
        
        # 创建控制器
        self.controller = AnnotationController(self)
        
        # 设置用户界面
        self._setup_ui()
        
        # 设置焦点策略
        self.setFocusPolicy(Qt.StrongFocus)
        
        # 初始化状态栏
        self._create_status_bar()
        self._update_status_bar()
    
    def _setup_ui(self):
        """设置用户界面"""
        # 设置画布基本属性
        self.setBackground('w')
        self.showGrid(x=True, y=True, alpha=CanvasConstants.GRID_ALPHA)
        self.setLabel('left', 'Y')
        self.setLabel('bottom', 'X')
        self.setAspectLocked(True)
        self.setMouseEnabled(x=True, y=True)
        self.setMenuEnabled(True)
        
        # 设置默认视图范围
        self.view = self.getViewBox()
        self.view.setRange(QRectF(
            CanvasConstants.DEFAULT_X_MIN, CanvasConstants.DEFAULT_Y_MIN,
            CanvasConstants.DEFAULT_X_MAX - CanvasConstants.DEFAULT_X_MIN,
            CanvasConstants.DEFAULT_Y_MAX - CanvasConstants.DEFAULT_Y_MIN
        ))
    
    def _create_status_bar(self):
        """创建状态栏"""
        # 创建状态栏
        self.status_bar = QStatusBar()
        
        # 添加状态标签
        self.status_label = QLabel(StateConstants.STATUS_READY)
        self.coordinate_label = QLabel(StateConstants.INITIAL_COORDINATE_TEXT)
        self.zoom_label = QLabel(StateConstants.INITIAL_ZOOM_TEXT)
        self.tool_label = QLabel(f"工具: {self.controller.get_current_tool().name}")
        self.color_label = QLabel(f"颜色: {self.controller.get_current_color().name}")
        self.snap_label = QLabel("网格吸附: 关闭")
        
        # 添加到状态栏
        self.status_bar.addWidget(self.status_label)
        self.status_bar.addWidget(self.tool_label)
        self.status_bar.addWidget(self.color_label)
        self.status_bar.addWidget(self.snap_label)
        self.status_bar.addPermanentWidget(self.coordinate_label)
        self.status_bar.addPermanentWidget(self.zoom_label)
        
        # 设置样式
        self.status_bar.setStyleSheet("QStatusBar { background-color: #f0f0f0; border-top: 1px solid #c0c0c0; }")
    
    
    def _update_status_bar(self):
        """更新状态栏"""
        if self.status_label:
            mode_text = "标注模式" if self.annotation_mode else "默认模式"
            current_state = self.controller.get_current_state()
            
            # 根据当前状态显示不同的提示
            if current_state.name == "CREATING_POLYGON":
                status_text = "多边形创建中 - 左键添加顶点，ESC取消，点击起始点自动闭合"
            else:
                status_text = f"{StateConstants.STATUS_READY} - {mode_text}"
            
            self.status_label.setText(status_text)
        
        if self.tool_label:
            self.tool_label.setText(f"工具: {self.controller.get_current_tool().name}")
        
        if self.color_label:
            self.color_label.setText(f"颜色: {self.controller.get_current_color().name}")
        
        if self.snap_label:
            from ..utils.config import Config
            config = Config()
            snap_status = "开启" if config.is_snap_to_grid() else "关闭"
            self.snap_label.setText(f"网格吸附: {snap_status}")
        
        if self.coordinate_label:
            self.coordinate_label.setText(StateConstants.INITIAL_COORDINATE_TEXT)
        
        if self.zoom_label:
            self.zoom_label.setText(StateConstants.INITIAL_ZOOM_TEXT)
    
    # 鼠标事件处理
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """处理鼠标按下事件"""
        if self.annotation_mode and event.button() == Qt.MouseButton.LeftButton:
            # 标注模式：处理标注功能
            self.controller.handle_mouse_press(event)
        else:
            # 默认模式：使用PlotWidget的默认行为
            super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """处理鼠标移动事件"""
        if self.annotation_mode:
            # 标注模式：处理标注功能
            self.controller.handle_mouse_move(event)
            self._update_status_bar()
        else:
            # 默认模式：使用PlotWidget的默认行为
            super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """处理鼠标释放事件"""
        if self.annotation_mode and event.button() == Qt.MouseButton.LeftButton:
            # 标注模式：处理标注功能
            self.controller.handle_mouse_release(event)
        else:
            # 默认模式：使用PlotWidget的默认行为
            super().mouseReleaseEvent(event)
    
    def wheelEvent(self, event: QWheelEvent) -> None:
        """处理滚轮事件"""
        # 检查缩放限制
        delta = event.angleDelta().y()
        zoom_factor = 1.0 + (delta / ZoomConstants.ZOOM_FACTOR_DIVISOR)
        
        # 只有放大时才检查限制
        if zoom_factor > 1.0:
            current_pixel_size = self.getViewBox().viewPixelSize()[0]
            new_pixel_size = current_pixel_size / zoom_factor
            
            if new_pixel_size < ZoomConstants.MAX_ZOOM_PIXEL_SIZE:
                return  # 已达到最大放大倍数
        
        super().wheelEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """处理键盘按下事件"""
        
        # 传递给控制器处理所有快捷键
        self.controller.handle_key_press(event)
    
    
    def _toggle_annotation_mode(self) -> None:
        """切换标注模式"""
        self.annotation_mode = not self.annotation_mode
        mode_text = "标注模式" if self.annotation_mode else "默认模式"
        
        # 更新状态栏显示当前模式
        self._update_status_bar()
    
    def _clear_all_annotations(self) -> None:
        """清空所有标注"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空所有标注吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.controller.clear_all_shapes()
    
    
    
    # 工具设置方法
    def set_current_tool(self, tool: DrawType) -> None:
        """设置当前工具"""
        self.controller.set_current_tool(tool)
        self._update_status_bar()
    
    def set_current_color(self, color: DrawColor) -> None:
        """设置当前颜色"""
        self.controller.set_current_color(color)
        self._update_status_bar()
    
    def set_current_width(self, width: PenWidth) -> None:
        """设置当前线宽"""
        self.controller.set_current_width(width)
        self._update_status_bar()
    
    def get_current_tool(self) -> DrawType:
        """获取当前工具"""
        return self.controller.get_current_tool()
    
    def get_current_color(self) -> DrawColor:
        """获取当前颜色"""
        return self.controller.get_current_color()
    
    def get_current_width(self) -> PenWidth:
        """获取当前线宽"""
        return self.controller.get_current_width()
    
    # 缩放方法
    def zoom_in(self) -> None:
        """放大"""
        from ..utils.constants import DisplayConstants
        factor = DisplayConstants.ZOOM_IN_FACTOR
        self.getViewBox().scaleBy((factor, factor))
    
    def zoom_out(self) -> None:
        """缩小"""
        from ..utils.constants import DisplayConstants
        factor = DisplayConstants.ZOOM_OUT_FACTOR
        self.getViewBox().scaleBy((factor, factor))
    
    # 数据管理方法
    def add_shape(self, shape: BaseShape) -> None:
        """添加图形（不支持撤销）"""
        self.controller.add_shape(shape)
    
    def add_shape_with_undo(self, shape: BaseShape) -> bool:
        """添加图形（支持撤销）"""
        success = self.controller.add_shape_with_undo(shape)
        
        if success:
            # 更新状态栏
            self._update_status_bar()
            logger.info("添加图形成功，可以通过 Ctrl+Z 撤销")
        
        return success
    
    def remove_shape(self, shape: BaseShape) -> bool:
        """移除图形"""
        return self.controller.remove_shape(shape)
    
    def clear_all(self) -> None:
        """清空所有图形"""
        self.controller.clear_all_shapes()
    
    def update_display(self) -> None:
        """更新显示"""
        self.controller.update_display()
    
    def get_shapes(self):
        """获取所有图形"""
        return self.controller.get_shapes()
    
    def get_selected_shape(self):
        """获取选中的图形"""
        return self.controller.get_selected_shape()
    
    # 数据导入导出
    def export_data(self) -> dict:
        """导出数据"""
        return self.controller.export_data()
    
    def import_data(self, data: dict) -> bool:
        """导入数据（不支持撤销）"""
        return self.controller.import_data(data)
    
    def import_data_with_undo(self, data: dict) -> bool:
        """导入数据（支持撤销）"""
        success = self.controller.import_data_with_undo(data)
        
        if success:
            # 更新状态栏
            self._update_status_bar()
            logger.info("导入数据成功，可以通过 Ctrl+Z 撤销")
        
        return success
    
    # 调试方法
    def set_debug_mode(self, enabled: bool) -> None:
        """设置调试模式"""
        self.controller.set_debug_mode(enabled)
    
    def get_current_state(self):
        """获取当前状态"""
        return self.controller.get_current_state()
    
    def get_input_state(self) -> dict:
        """获取输入状态"""
        return self.controller.get_input_state()
    
    # 兼容性属性
    @property
    def plot_widget(self):
        """兼容性属性 - 返回自身"""
        return self
    
    def cleanup(self) -> None:
        """清理资源"""
        logger.debug("画布开始清理资源")
        
        # 清理控制器
        if hasattr(self, 'controller') and self.controller:
            self.controller.cleanup()
        
        # 清理 PyQtGraph 资源
        try:
            # 断开所有信号连接
            if hasattr(self, 'plotItem') and self.plotItem:
                if hasattr(self.plotItem, 'vb') and self.plotItem.vb:
                    # 清理 ViewBox
                    self.plotItem.vb.clear()
                    # 断开信号连接
                    self.plotItem.vb.disconnect()
        except Exception as e:
            logger.debug(f"清理 PyQtGraph 资源时出现异常: {e}")
        
        logger.debug("画布资源清理完成")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.cleanup()
        super().closeEvent(event)