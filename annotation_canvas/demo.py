"""
AnnotationCanvas 演示程序

这个演示程序展示了如何使用 AnnotationCanvas 库创建图形标注应用。
"""

import sys
import random
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QPushButton, QLabel, QComboBox, QGroupBox,
    QMenuBar, QMenu, QStatusBar, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence

# 处理相对导入问题
try:
    from .ui.annotation_canvas import AnnotationCanvas
    from .core.enums import DrawType, DrawColor, PenWidth
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from annotation_canvas.ui.annotation_canvas import AnnotationCanvas
    from annotation_canvas.core.enums import DrawType, DrawColor, PenWidth


class AnnotationCanvasDemo(QMainWindow):
    """AnnotationCanvas 演示窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AnnotationCanvas 演示程序")
        self.setGeometry(100, 100, 1200, 800)
        
        # 创建画布
        self.canvas = AnnotationCanvas()
        
        # 初始化UI
        self._init_ui()
        self._init_menu()
        self._init_status_bar()
        
        # 连接信号
        self._connect_signals()
        
        # 设置默认工具
        self.canvas.set_draw_tool(DrawType.POINT)
    
    def _init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 左侧控制面板
        control_panel = self._create_control_panel()
        main_layout.addWidget(control_panel, 0)
        
        # 右侧画布
        main_layout.addWidget(self.canvas, 1)
    
    def _create_control_panel(self):
        """创建控制面板"""
        panel = QGroupBox("控制面板")
        layout = QVBoxLayout(panel)
        
        # 工具选择
        tool_group = QGroupBox("绘图工具")
        tool_layout = QVBoxLayout(tool_group)
        
        self.tool_combo = QComboBox()
        self.tool_combo.addItems([
            "点 (Point)",
            "矩形 (Rectangle)", 
            "椭圆 (Ellipse)",
            "多边形 (Polygon)"
        ])
        tool_layout.addWidget(QLabel("选择工具:"))
        tool_layout.addWidget(self.tool_combo)
        
        # 颜色选择
        color_group = QGroupBox("颜色设置")
        color_layout = QVBoxLayout(color_group)
        
        self.color_combo = QComboBox()
        self.color_combo.addItems([
            "红色 (Red)",
            "绿色 (Green)",
            "蓝色 (Blue)",
            "黄色 (Yellow)",
            "紫色 (Purple)",
            "橙色 (Orange)",
            "黑色 (Black)",
            "白色 (White)"
        ])
        color_layout.addWidget(QLabel("选择颜色:"))
        color_layout.addWidget(self.color_combo)
        
        # 线宽选择
        width_group = QGroupBox("线宽设置")
        width_layout = QVBoxLayout(width_group)
        
        self.width_combo = QComboBox()
        self.width_combo.addItems([
            "细 (Thin)",
            "中等 (Medium)",
            "粗 (Thick)"
        ])
        width_layout.addWidget(QLabel("选择线宽:"))
        width_layout.addWidget(self.width_combo)
        
        # 操作按钮
        action_group = QGroupBox("操作")
        action_layout = QVBoxLayout(action_group)
        
        self.clear_btn = QPushButton("清空画布")
        self.undo_btn = QPushButton("撤销 (Ctrl+Z)")
        self.redo_btn = QPushButton("重做 (Ctrl+Y)")
        
        # 添加图形按钮
        self.add_shape_btn = QPushButton("添加测试图形（支持撤销）")
        self.add_shape_no_undo_btn = QPushButton("添加测试图形（不支持撤销）")
        
        action_layout.addWidget(self.clear_btn)
        action_layout.addWidget(self.undo_btn)
        action_layout.addWidget(self.redo_btn)
        action_layout.addWidget(self.add_shape_btn)
        action_layout.addWidget(self.add_shape_no_undo_btn)
        
        # 缩放按钮
        zoom_group = QGroupBox("缩放")
        zoom_layout = QVBoxLayout(zoom_group)
        
        self.zoom_in_btn = QPushButton("放大 (Ctrl+=)")
        self.zoom_out_btn = QPushButton("缩小 (Ctrl+-)")
        self.zoom_fit_btn = QPushButton("适应窗口")
        
        zoom_layout.addWidget(self.zoom_in_btn)
        zoom_layout.addWidget(self.zoom_out_btn)
        zoom_layout.addWidget(self.zoom_fit_btn)
        
        # 添加到主布局
        layout.addWidget(tool_group)
        layout.addWidget(color_group)
        layout.addWidget(width_group)
        layout.addWidget(action_group)
        layout.addWidget(zoom_group)
        layout.addStretch()
        
        return panel
    
    def _init_menu(self):
        """初始化菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件(&F)")
        
        new_action = QAction("新建(&N)", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_file)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        # 导入菜单
        import_action = QAction("导入数据(&I)", self)
        import_action.triggered.connect(self._import_data)
        file_menu.addAction(import_action)
        
        # 导出菜单
        export_action = QAction("导出数据(&E)", self)
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出(&X)", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 编辑菜单
        edit_menu = menubar.addMenu("编辑(&E)")
        
        undo_action = QAction("撤销(&U)", self)
        # 移除快捷键，让画布自己处理
        undo_action.triggered.connect(self._undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("重做(&R)", self)
        # 移除快捷键，让画布自己处理
        redo_action.triggered.connect(self._redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        clear_action = QAction("清空(&C)", self)
        clear_action.triggered.connect(self._clear_canvas)
        edit_menu.addAction(clear_action)
        
        # 视图菜单
        view_menu = menubar.addMenu("视图(&V)")
        
        zoom_in_action = QAction("放大(&I)", self)
        zoom_in_action.setShortcut(QKeySequence("Ctrl+="))
        zoom_in_action.triggered.connect(self._zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("缩小(&O)", self)
        zoom_out_action.setShortcut(QKeySequence("Ctrl+-"))
        zoom_out_action.triggered.connect(self._zoom_out)
        view_menu.addAction(zoom_out_action)
        
        zoom_fit_action = QAction("适应窗口(&F)", self)
        zoom_fit_action.triggered.connect(self._zoom_fit)
        view_menu.addAction(zoom_fit_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助(&H)")
        
        about_action = QAction("关于(&A)", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _init_status_bar(self):
        """初始化状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def _connect_signals(self):
        """连接信号"""
        # 工具选择
        self.tool_combo.currentIndexChanged.connect(self._on_tool_changed)
        self.color_combo.currentIndexChanged.connect(self._on_color_changed)
        self.width_combo.currentIndexChanged.connect(self._on_width_changed)
        
        # 按钮
        self.clear_btn.clicked.connect(self._clear_canvas)
        self.undo_btn.clicked.connect(self._undo)
        self.redo_btn.clicked.connect(self._redo)
        self.add_shape_btn.clicked.connect(self._add_test_shape_with_undo)
        self.add_shape_no_undo_btn.clicked.connect(self._add_test_shape_no_undo)
        self.zoom_in_btn.clicked.connect(self._zoom_in)
        self.zoom_out_btn.clicked.connect(self._zoom_out)
        self.zoom_fit_btn.clicked.connect(self._zoom_fit)
        
        # 画布信号
        self.canvas.shape_added.connect(self._on_shape_added)
        self.canvas.shape_updated.connect(self._on_shape_updated)
        self.canvas.shape_removed.connect(self._on_shape_removed)
        self.canvas.shape_selected.connect(self._on_shape_selected)
        self.canvas.shape_deselected.connect(self._on_shape_deselected)
        
        # 事件总线信号 - 处理ESC键取消多边形
        from annotation_canvas.events import EventType
        self.canvas.controller.event_bus.subscribe(EventType.CONFIRM_CANCEL_POLYGON, self._on_confirm_cancel_polygon)
    
    def _on_tool_changed(self, index):
        """工具改变"""
        tools = [DrawType.POINT, DrawType.RECTANGLE, DrawType.ELLIPSE, DrawType.POLYGON]
        if 0 <= index < len(tools):
            self.canvas.set_draw_tool(tools[index])
            self.status_bar.showMessage(f"当前工具: {tools[index].name}")
    
    def _on_color_changed(self, index):
        """颜色改变"""
        colors = [
            DrawColor.RED, DrawColor.GREEN, DrawColor.BLUE, DrawColor.YELLOW,
            DrawColor.PURPLE, DrawColor.ORANGE, DrawColor.BLACK, DrawColor.WHITE
        ]
        if 0 <= index < len(colors):
            self.canvas.set_draw_color(colors[index])
            self.status_bar.showMessage(f"当前颜色: {colors[index].name}")
    
    def _on_width_changed(self, index):
        """线宽改变"""
        widths = [PenWidth.THIN, PenWidth.MEDIUM, PenWidth.THICK]
        if 0 <= index < len(widths):
            self.canvas.set_pen_width(widths[index])
            self.status_bar.showMessage(f"当前线宽: {widths[index].name}")
    
    def _on_shape_added(self, shape):
        """处理图形添加信号"""
        # 获取图形信息
        shape_info = {
            'type': shape.shape_type.name,
            'color': shape.color.name,
            'pen_width': shape.pen_width.name,
            'position': None,
            'bounds': None
        }
        
        # 根据图形类型获取位置信息
        if hasattr(shape, 'get_position'):
            pos = shape.get_position()
            shape_info['position'] = (pos.x(), pos.y())
        elif hasattr(shape, 'get_center'):
            center = shape.get_center()
            shape_info['position'] = (center.x(), center.y())
        
        # 获取边界信息
        bounds = shape.get_bounds()
        shape_info['bounds'] = {
            'x': bounds.x(),
            'y': bounds.y(),
            'width': bounds.width(),
            'height': bounds.height()
        }
        
        # 更新状态栏显示图形信息
        self.status_bar.showMessage(
            f"已添加 {shape_info['type']} 图形 - "
            f"颜色: {shape_info['color']}, "
            f"线宽: {shape_info['pen_width']}"
        )
        
        # 打印图形信息到控制台（实际使用时可以替换为其他处理逻辑）
        print(f"图形添加信号触发: {shape_info}")
    
    def _on_shape_updated(self, shape):
        """处理图形更新信号"""
        self.status_bar.showMessage(f"图形已更新 - {shape.shape_type.name}")
    
    def _on_shape_removed(self, shape):
        """处理图形删除信号"""
        self.status_bar.showMessage(f"图形已删除 - {shape.shape_type.name}")
        
        print(f"图形删除信号触发:")
        print(f"  图形类型: {shape.shape_type.name}")
        if hasattr(shape, 'get_position'):
            pos = shape.get_position()
            print(f"  删除前位置: ({pos.x():.1f}, {pos.y():.1f})")
    
    def _on_shape_selected(self, shape):
        """处理图形选择信号"""
        self.status_bar.showMessage(f"图形已选中 - {shape.shape_type.name}")
        print(f"图形选择信号触发: {shape.shape_type.name}")
    
    def _on_shape_deselected(self, shape):
        """处理图形取消选择信号"""
        self.status_bar.showMessage("取消选择图形")
        print("图形取消选择信号触发")
    
    def _on_confirm_cancel_polygon(self, event):
        """处理确认取消多边形事件"""
        vertex_count = event.data.get('vertex_count', 0)
        
        # 显示确认对话框
        reply = QMessageBox.question(
            self, "取消多边形创建", 
            f"当前多边形已有 {vertex_count} 个顶点，确定要取消创建吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 确认取消，发布确认事件
            from annotation_canvas.events import Event, EventType
            self.canvas.controller.event_bus.publish(Event(
                EventType.CANCEL_POLYGON_CONFIRMED,
                {'confirmed': True}
            ))
            self.status_bar.showMessage("已取消多边形创建")
        else:
            # 取消操作，继续多边形创建
            from annotation_canvas.events import Event, EventType
            self.canvas.controller.event_bus.publish(Event(
                EventType.CANCEL_POLYGON_CONFIRMED,
                {'confirmed': False}
            ))
            self.status_bar.showMessage("继续多边形创建")
    
    def _new_file(self):
        """新建文件"""
        reply = QMessageBox.question(
            self, "新建文件", 
            "确定要清空当前画布吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._clear_canvas()
    
    def _clear_canvas(self):
        """清空画布"""
        self.canvas.clear_all_shapes()
        self.status_bar.showMessage("画布已清空")
    
    def _undo(self):
        """撤销"""
        self.canvas.undo()
        self.status_bar.showMessage("撤销操作")
    
    def _redo(self):
        """重做"""
        self.canvas.redo()
        self.status_bar.showMessage("重做操作")
    
    def _zoom_in(self):
        """放大"""
        # 使用PyQtGraph的缩放功能
        self.canvas.getViewBox().scaleBy(1.1)
        self.status_bar.showMessage("放大")
    
    def _zoom_out(self):
        """缩小"""
        # 使用PyQtGraph的缩放功能
        self.canvas.getViewBox().scaleBy(0.9)
        self.status_bar.showMessage("缩小")
    
    def _zoom_fit(self):
        """适应窗口"""
        # 使用PyQtGraph的自动范围功能
        self.canvas.getViewBox().autoRange()
        self.status_bar.showMessage("适应窗口")
    
    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self, "关于 AnnotationCanvas",
            """
            <h3>AnnotationCanvas 演示程序</h3>
            <p>这是一个基于 PySide6 和 PyQtGraph 的图形标注画布组件。</p>
            <p><b>主要特性：</b></p>
            <ul>
            <li>支持点、矩形、椭圆、多边形等多种图形类型</li>
            <li>实时预览和交互操作</li>
            <li>完整的撤销重做系统</li>
            <li>图形悬停高亮和控制点操作</li>
            <li>网格吸附和坐标转换</li>
            </ul>
            <p><b>使用方法：</b></p>
            <ul>
            <li>选择绘图工具，在画布上点击创建图形</li>
            <li>选中图形后可以拖拽移动或缩放</li>
            <li>使用 Ctrl+Z 撤销，Ctrl+Y 重做</li>
            <li>使用 Ctrl+= 放大，Ctrl+- 缩小</li>
            </ul>
            """
        )
    
    def _add_test_shape_with_undo(self):
        """添加测试图形（支持撤销）"""
        from annotation_canvas.models import PointShape, RectangleShape
        from PySide6.QtCore import QPointF
        
        # 创建随机位置的测试图形
        x = random.randint(-100, 100)
        y = random.randint(-100, 100)
        
        # 获取当前设置
        current_tool = self.canvas.controller.data_manager.get_current_tool()
        current_color = self.canvas.controller.data_manager.get_current_color()
        current_width = self.canvas.controller.data_manager.get_current_width()
        
        if current_tool == DrawType.POINT:
            shape = PointShape(QPointF(x, y), current_color, current_width)
        elif current_tool == DrawType.RECTANGLE:
            shape = RectangleShape(
                QPointF(x, y), 
                QPointF(x + 30, y + 20), 
                current_color, 
                current_width
            )
        else:
            # 默认创建点
            shape = PointShape(QPointF(x, y), current_color, current_width)
        
        # 使用支持撤销的添加方法
        success = self.canvas.add_shape(shape)
        
        if success:
            self.status_bar.showMessage(f"已添加 {shape.shape_type.name} 图形（支持撤销）")
        else:
            self.status_bar.showMessage("添加图形失败")
    
    def _add_test_shape_no_undo(self):
        """添加测试图形（不支持撤销）"""
        from annotation_canvas.models import PointShape, RectangleShape
        from PySide6.QtCore import QPointF
        
        # 创建随机位置的测试图形
        x = random.randint(-100, 100)
        y = random.randint(-100, 100)
        
        # 获取当前设置
        current_tool = self.canvas.controller.data_manager.get_current_tool()
        current_color = self.canvas.controller.data_manager.get_current_color()
        current_width = self.canvas.controller.data_manager.get_current_width()
        
        if current_tool == DrawType.POINT:
            shape = PointShape(QPointF(x, y), current_color, current_width)
        elif current_tool == DrawType.RECTANGLE:
            shape = RectangleShape(
                QPointF(x, y), 
                QPointF(x + 30, y + 20), 
                current_color, 
                current_width
            )
        else:
            # 默认创建点
            shape = PointShape(QPointF(x, y), current_color, current_width)
        
        # 使用不支持撤销的添加方法
        self.canvas.add_shape(shape)
        self.status_bar.showMessage(f"已添加 {shape.shape_type.name} 图形（不支持撤销）")
    
    def _import_data(self):
        """导入数据"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, "导入数据", "", "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 读取文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 使用导入方法
                success = self.canvas.import_data(data)
                
                if success:
                    shape_count = len(data.get('shapes', []))
                    QMessageBox.information(
                        self, "导入成功", 
                        f"成功导入 {shape_count} 个图形\n可以通过 Ctrl+Z 撤销导入操作"
                    )
                    self.status_bar.showMessage(f"已导入 {shape_count} 个图形")
                else:
                    QMessageBox.warning(self, "导入失败", "导入数据失败")
                    
            except Exception as e:
                QMessageBox.critical(self, "导入错误", f"导入文件时发生错误：\n{str(e)}")
    
    def _export_data(self):
        """导出数据"""
        from PySide6.QtWidgets import QFileDialog, QMessageBox
        import json
        
        # 选择文件
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出数据", "annotation_data.json", "JSON文件 (*.json);;所有文件 (*)"
        )
        
        if file_path:
            try:
                # 导出数据
                data = self.canvas.export_data()
                
                # 保存文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                shape_count = len(data.get('shapes', []))
                QMessageBox.information(
                    self, "导出成功", 
                    f"成功导出 {shape_count} 个图形到文件：\n{file_path}"
                )
                self.status_bar.showMessage(f"已导出 {shape_count} 个图形")
                
            except Exception as e:
                QMessageBox.critical(self, "导出错误", f"导出文件时发生错误：\n{str(e)}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("AnnotationCanvas Demo")
    app.setApplicationVersion("1.0.0")
    
    # 创建演示窗口
    demo = AnnotationCanvasDemo()
    demo.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
