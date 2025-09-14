# AnnotationCanvas

一个功能强大的图形标注画布组件，基于 PySide6 和 PyQtGraph 构建。

## 特性

- 🎨 **多种图形类型**：支持点、矩形、椭圆、多边形等图形
- 🖱️ **交互操作**：拖拽移动、控制点缩放、悬停高亮
- ↩️ **撤销重做**：完整的操作历史管理
- 🎯 **实时预览**：创建和编辑时的实时视觉反馈
- ⌨️ **快捷键支持**：丰富的键盘快捷键操作
- 🎛️ **网格吸附**：可选的网格对齐功能
- 🏗️ **事件驱动架构**：模块化设计，易于扩展

## 安装

### 从源码安装

```bash
# 克隆仓库
git clone https://github.com/ky15705592706/annotation_canvas.git
cd annotation_canvas

# 安装依赖
pip install -r requirements.txt

# 安装包
pip install -e .
```

### 依赖要求

- Python >= 3.8
- PySide6 >= 6.0.0
- pyqtgraph >= 0.12.0

## 快速开始

### 基本使用

```python
import sys
from PySide6.QtWidgets import QApplication
from annotation_canvas import AnnotationCanvas

# 创建应用
app = QApplication(sys.argv)

# 创建画布
canvas = AnnotationCanvas()
canvas.show()

# 运行应用
app.exec()
```

### 演示程序

```bash
python run_demo.py
```

## 功能特性

### 图形类型

- **点 (Point)**：单点标注
- **矩形 (Rectangle)**：矩形区域标注
- **椭圆 (Ellipse)**：椭圆区域标注
- **多边形 (Polygon)**：任意多边形标注

### 交互操作

- **创建图形**：选择工具后点击画布创建
- **移动图形**：拖拽图形进行移动
- **缩放图形**：拖拽控制点进行缩放
- **删除图形**：选中后按 Delete 键删除
- **悬停高亮**：鼠标悬停时图形高亮显示

### 快捷键

- **Ctrl+A**：切换标注模式
- **Ctrl+1**：循环切换绘制工具
- **Ctrl+2**：循环切换颜色
- **Ctrl+3**：循环切换线宽
- **Ctrl+G**：切换网格吸附
- **Delete**：删除选中的图形
- **Shift+Delete**：清空所有标注
- **Ctrl+Z**：撤销操作
- **Ctrl+Y**：重做操作
- **ESC**：取消多边形创建

### 多边形创建

多边形创建支持任意多个顶点（至少3个）：

1. **开始创建**：选择多边形工具，在画布上点击开始创建
2. **添加顶点**：左键点击添加顶点
3. **吸附功能**：当鼠标靠近起始点时，会自动吸附到起始点位置
4. **自动闭合**：当吸附到起始点时，点击左键会自动闭合多边形并完成创建
5. **完成创建**：
   - 点击起始点附近自动闭合
   - 或按 ESC 键取消创建

## 高级用法

### 自定义配置

```python
from annotation_canvas.utils.config import Config

# 获取配置实例
config = Config()

# 修改配置
config.set('canvas.background_color', [240, 240, 240])
config.set('interaction.snap_to_grid', True)
```

### 常量配置

```python
from annotation_canvas.utils.constants import ColorConstants, CanvasConstants

# 修改颜色常量
ColorConstants.SHAPE_DEFAULT = [255, 0, 0]  # 红色

# 修改画布常量
CanvasConstants.GRID_SIZE = 20
```

### 数据导入导出

```python
# 导出数据
data = canvas.export_data()

# 导入数据
success = canvas.import_data(data)
```

### 信号监听

```python
from PySide6.QtCore import QObject

class ShapeMonitor(QObject):
    def __init__(self, canvas):
        super().__init__()
        # 连接图形添加信号
        canvas.shape_added.connect(self.on_shape_added)
        canvas.shape_selected.connect(self.on_shape_selected)
        canvas.shape_deselected.connect(self.on_shape_deselected)
    
    def on_shape_added(self, shape):
        """处理图形添加信号"""
        print(f"添加了图形: {shape.shape_type.name}")
        print(f"位置: {shape.get_position()}")
        print(f"颜色: {shape.color.name}")
    
    def on_shape_moved(self, shape):
        """处理图形移动信号"""
        print(f"移动了图形: {shape.shape_type.name}")
        if hasattr(shape, 'get_position'):
            pos = shape.get_position()
            print(f"当前位置: ({pos.x():.1f}, {pos.y():.1f})")
    
    def on_shape_modified(self, shape):
        """处理图形修改信号"""
        print(f"修改了图形: {shape.shape_type.name}")
        bounds = shape.get_bounds()
        print(f"当前边界: x:{bounds.x():.1f}, y:{bounds.y():.1f}, w:{bounds.width():.1f}, h:{bounds.height():.1f}")
    
    def on_shape_deleted(self, shape):
        """处理图形删除信号"""
        print(f"删除了图形: {shape.shape_type.name}")
        if hasattr(shape, 'get_position'):
            pos = shape.get_position()
            print(f"删除前位置: ({pos.x():.1f}, {pos.y():.1f})")
    
    def on_shape_selected(self, shape):
        """处理图形选择信号"""
        print(f"选择了图形: {shape.shape_type.name}")
    
    def on_shape_deselected(self):
        """处理图形取消选择信号"""
        print("取消选择图形")

# 使用示例
canvas = AnnotationCanvas()
monitor = ShapeMonitor(canvas)
```

## 架构设计

### 事件驱动架构

- **EventBus**：事件总线，负责事件的发布和订阅
- **Event**：事件对象，包含事件类型和数据
- **EventType**：事件类型枚举，定义所有可能的事件

### 模块化设计

- **DataManager**：数据管理器，专门负责图形数据的 CRUD 操作
- **InputHandler**：输入处理器，将原始输入转换为语义化事件
- **StateManager**：状态管理器，监听事件并管理状态转换
- **CanvasRenderer**：渲染器，监听数据变化事件并更新显示
- **OperationManager**：操作管理器，支持撤销重做功能

### 设计模式

- **工厂模式**：ShapeFactory 统一创建图形对象
- **策略模式**：RenderStrategyFactory 处理不同图形的渲染
- **状态模式**：StatefulOperation 管理操作状态
- **依赖注入**：DIContainer 管理模块依赖关系

## 开发

### 项目结构

```
annotation_canvas/
├── core/                 # 核心模块
├── events/              # 事件系统
├── data/                # 数据管理
├── input/               # 输入处理
├── state/               # 状态管理
├── render/              # 渲染
├── operations/          # 操作管理
├── models/              # 数据模型
├── utils/               # 工具类
├── ui/                  # 用户界面
├── demo.py              # 演示程序
└── __init__.py          # 包初始化
```

### 运行测试

```bash
# 运行演示程序
python run_demo.py

# 检查代码质量
flake8 annotation_canvas/
```

## 许可证

GPL-3.0 License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

- 作者：KY
- 邮箱：1980983959@qq.com
- 项目地址：https://github.com/ky15705592706/annotation_canvas