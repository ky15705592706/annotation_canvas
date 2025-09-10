#!/usr/bin/env python3
"""
清理 Python 缓存文件脚本
自动清理项目中的所有 __pycache__ 目录和 .pyc 文件
"""

import os
import shutil
import sys
from pathlib import Path

def find_pycache_dirs(root_dir):
    """查找所有 __pycache__ 目录"""
    pycache_dirs = []
    for root, dirs, files in os.walk(root_dir):
        for dir_name in dirs:
            if dir_name == "__pycache__":
                pycache_dirs.append(os.path.join(root, dir_name))
    return pycache_dirs

def find_pyc_files(root_dir):
    """查找所有 .pyc 文件"""
    pyc_files = []
    for root, dirs, files in os.walk(root_dir):
        for file_name in files:
            if file_name.endswith('.pyc'):
                pyc_files.append(os.path.join(root, file_name))
    return pyc_files

def cleanup_cache(root_dir):
    """清理缓存文件和日志目录"""
    print(f"正在清理目录: {root_dir}")
    print("=" * 50)
    
    total_size = 0
    
    # 查找并删除 __pycache__ 目录
    pycache_dirs = find_pycache_dirs(root_dir)
    print(f"找到 {len(pycache_dirs)} 个 __pycache__ 目录:")
    
    for pycache_dir in pycache_dirs:
        try:
            # 计算目录大小
            dir_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                          for dirpath, dirnames, filenames in os.walk(pycache_dir)
                          for filename in filenames)
            total_size += dir_size
            
            print(f"  - {pycache_dir}")
            shutil.rmtree(pycache_dir)
            print(f"    ✅ 已删除")
        except Exception as e:
            print(f"    ❌ 删除失败: {e}")
    
    # 查找并删除 .pyc 文件
    pyc_files = find_pyc_files(root_dir)
    print(f"\n找到 {len(pyc_files)} 个 .pyc 文件:")
    
    for pyc_file in pyc_files:
        try:
            file_size = os.path.getsize(pyc_file)
            total_size += file_size
            print(f"  - {pyc_file}")
            os.remove(pyc_file)
            print(f"    ✅ 已删除")
        except Exception as e:
            print(f"    ❌ 删除失败: {e}")
    
    # 删除日志目录
    logs_dir = os.path.join(root_dir, "logs")
    logs_deleted = False
    if os.path.exists(logs_dir):
        try:
            # 计算日志目录大小
            logs_size = sum(os.path.getsize(os.path.join(dirpath, filename))
                           for dirpath, dirnames, filenames in os.walk(logs_dir)
                           for filename in filenames)
            total_size += logs_size
            
            print(f"\n找到日志目录: {logs_dir}")
            shutil.rmtree(logs_dir)
            print(f"    ✅ 已删除")
            logs_deleted = True
        except Exception as e:
            print(f"    ❌ 删除失败: {e}")
    else:
        print(f"\n日志目录不存在: {logs_dir}")
    
    # 显示清理结果
    print("\n" + "=" * 50)
    print(f"清理完成!")
    print(f"删除了 {len(pycache_dirs)} 个 __pycache__ 目录")
    print(f"删除了 {len(pyc_files)} 个 .pyc 文件")
    if logs_deleted:
        print(f"删除了日志目录")
    print(f"释放空间: {total_size / 1024:.2f} KB")

def main():
    """主函数"""
    # 获取当前目录
    current_dir = os.getcwd()
    
    print("Python 缓存和日志清理工具")
    print("=" * 50)
    print(f"目标目录: {current_dir}")
    print("开始自动清理...")
    
    # 执行清理
    try:
        cleanup_cache(current_dir)
    except KeyboardInterrupt:
        print("\n\n清理操作被用户中断")
    except Exception as e:
        print(f"\n清理过程中发生错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
