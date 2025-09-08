"""
AnnotationCanvas 库安装脚本
"""

from setuptools import setup, find_packages
import os

# 读取 README 文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取版本信息
def get_version():
    with open("annotation_canvas/__init__.py", "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    return "1.0.0"

setup(
    name="annotation-canvas",
    version=get_version(),
    author="KY",
    author_email="1980983959@qq.com",
    description="一个功能强大的图形标注画布组件，支持多种图形类型和交互操作",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/ky15705592706/annotation_canvas",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Visualization",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PySide6>=6.0.0",
        "pyqtgraph>=0.12.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-qt>=4.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
    },
    include_package_data=True,
    package_data={
        "annotation_canvas": [
            "config.json",
            "*.md",
        ],
    },
    entry_points={
        "console_scripts": [
            "annotation-canvas-demo=annotation_canvas.demo:main",
        ],
    },
    keywords="annotation canvas graphics drawing visualization PyQt PySide",
    project_urls={
        "Bug Reports": "https://github.com/ky15705592706/annotation_canvas/issues",
        "Source": "https://github.com/ky15705592706/annotation_canvas",
        "Documentation": "https://github.com/ky15705592706/annotation_canvas#readme",
    },
)
