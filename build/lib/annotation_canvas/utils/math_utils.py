# This Python file uses the following encoding: utf-8

"""
数学工具 - 提供数学计算相关的工具函数
"""

import math
from typing import List, Tuple, Optional
from PySide6.QtCore import QPointF

class MathUtils:
    """数学工具类"""
    
    @staticmethod
    def clamp(value: float, min_val: float, max_val: float) -> float:
        """将值限制在指定范围内"""
        return max(min_val, min(max_val, value))
    
    @staticmethod
    def lerp(a: float, b: float, t: float) -> float:
        """线性插值"""
        return a + t * (b - a)
    
    @staticmethod
    def smooth_step(edge0: float, edge1: float, x: float) -> float:
        """平滑步进函数"""
        t = MathUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * (3.0 - 2.0 * t)
    
    @staticmethod
    def smoother_step(edge0: float, edge1: float, x: float) -> float:
        """更平滑的步进函数"""
        t = MathUtils.clamp((x - edge0) / (edge1 - edge0), 0.0, 1.0)
        return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
    
    @staticmethod
    def degrees_to_radians(degrees: float) -> float:
        """角度转弧度"""
        return degrees * math.pi / 180.0
    
    @staticmethod
    def radians_to_degrees(radians: float) -> float:
        """弧度转角度"""
        return radians * 180.0 / math.pi
    
    @staticmethod
    def normalize_angle(angle: float) -> float:
        """将角度标准化到 [0, 2π) 范围"""
        while angle < 0:
            angle += 2 * math.pi
        while angle >= 2 * math.pi:
            angle -= 2 * math.pi
        return angle
    
    @staticmethod
    def angle_difference(angle1: float, angle2: float) -> float:
        """计算两个角度之间的最小差值"""
        diff = angle1 - angle2
        while diff > math.pi:
            diff -= 2 * math.pi
        while diff < -math.pi:
            diff += 2 * math.pi
        return diff
    
    @staticmethod
    def is_almost_equal(a: float, b: float, epsilon: float = 1e-6) -> bool:
        """检查两个浮点数是否几乎相等"""
        return abs(a - b) < epsilon
    
    @staticmethod
    def is_almost_zero(value: float, epsilon: float = 1e-6) -> bool:
        """检查浮点数是否几乎为零"""
        return abs(value) < epsilon
    
    @staticmethod
    def round_to_precision(value: float, precision: int) -> float:
        """将浮点数舍入到指定精度"""
        factor = 10 ** precision
        return round(value * factor) / factor
    
    @staticmethod
    def factorial(n: int) -> int:
        """计算阶乘"""
        if n < 0:
            raise ValueError("阶乘不能计算负数")
        if n == 0 or n == 1:
            return 1
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result
    
    @staticmethod
    def binomial_coefficient(n: int, k: int) -> int:
        """计算二项式系数 C(n, k)"""
        if k < 0 or k > n:
            return 0
        if k == 0 or k == n:
            return 1
        
        # 使用对称性优化
        if k > n - k:
            k = n - k
        
        result = 1
        for i in range(k):
            result = result * (n - i) // (i + 1)
        
        return result
    
    @staticmethod
    def bezier_curve(points: List[QPointF], t: float) -> QPointF:
        """计算贝塞尔曲线上的点"""
        n = len(points) - 1
        if n < 0:
            return QPointF(0, 0)
        
        x = 0.0
        y = 0.0
        
        for i, point in enumerate(points):
            coeff = MathUtils.binomial_coefficient(n, i)
            term = coeff * (1 - t) ** (n - i) * t ** i
            x += term * point.x()
            y += term * point.y()
        
        return QPointF(x, y)
    
    @staticmethod
    def bezier_curve_derivative(points: List[QPointF], t: float) -> QPointF:
        """计算贝塞尔曲线的导数（切线方向）"""
        n = len(points) - 1
        if n < 1:
            return QPointF(0, 0)
        
        x = 0.0
        y = 0.0
        
        for i in range(n):
            coeff = MathUtils.binomial_coefficient(n - 1, i)
            term = coeff * (1 - t) ** (n - 1 - i) * t ** i
            dx = points[i + 1].x() - points[i].x()
            dy = points[i + 1].y() - points[i].y()
            x += term * dx
            y += term * dy
        
        return QPointF(x * n, y * n)
    
    @staticmethod
    def bezier_curve_points(points: List[QPointF], num_points: int = 50) -> List[QPointF]:
        """生成贝塞尔曲线上的点列表"""
        if len(points) < 2:
            return points.copy()
        
        curve_points = []
        for i in range(num_points + 1):
            t = i / num_points
            point = MathUtils.bezier_curve(points, t)
            curve_points.append(point)
        
        return curve_points
    
    @staticmethod
    def catmull_rom_spline(points: List[QPointF], t: float) -> QPointF:
        """计算Catmull-Rom样条曲线上的点"""
        if len(points) < 2:
            return QPointF(0, 0) if not points else points[0]
        
        if len(points) == 2:
            # 线性插值
            p0, p1 = points[0], points[1]
            return QPointF(
                p0.x() + t * (p1.x() - p0.x()),
                p0.y() + t * (p1.y() - p0.y())
            )
        
        # 找到包含t的线段
        n = len(points) - 1
        segment = int(t * n)
        segment = MathUtils.clamp(segment, 0, n - 1)
        
        # 计算局部参数
        local_t = t * n - segment
        local_t = MathUtils.clamp(local_t, 0.0, 1.0)
        
        # 获取控制点
        p0 = points[max(0, segment - 1)]
        p1 = points[segment]
        p2 = points[min(segment + 1, len(points) - 1)]
        p3 = points[min(segment + 2, len(points) - 1)]
        
        # Catmull-Rom公式
        t2 = local_t * local_t
        t3 = t2 * local_t
        
        x = 0.5 * ((2 * p1.x()) +
                   (-p0.x() + p2.x()) * local_t +
                   (2 * p0.x() - 5 * p1.x() + 4 * p2.x() - p3.x()) * t2 +
                   (-p0.x() + 3 * p1.x() - 3 * p2.x() + p3.x()) * t3)
        
        y = 0.5 * ((2 * p1.y()) +
                   (-p0.y() + p2.y()) * local_t +
                   (2 * p0.y() - 5 * p1.y() + 4 * p2.y() - p3.y()) * t2 +
                   (-p0.y() + 3 * p1.y() - 3 * p2.y() + p3.y()) * t3)
        
        return QPointF(x, y)
    
    @staticmethod
    def catmull_rom_spline_points(points: List[QPointF], num_points: int = 50) -> List[QPointF]:
        """生成Catmull-Rom样条曲线上的点列表"""
        if len(points) < 2:
            return points.copy()
        
        curve_points = []
        for i in range(num_points + 1):
            t = i / num_points
            point = MathUtils.catmull_rom_spline(points, t)
            curve_points.append(point)
        
        return curve_points
    
    @staticmethod
    def gaussian_blur_1d(data: List[float], sigma: float) -> List[float]:
        """一维高斯模糊"""
        if not data:
            return data
        
        n = len(data)
        if n == 1:
            return data.copy()
        
        # 计算核大小
        kernel_size = int(2 * sigma * 3) + 1
        if kernel_size % 2 == 0:
            kernel_size += 1
        
        # 生成高斯核
        kernel = []
        center = kernel_size // 2
        sum_val = 0.0
        
        for i in range(kernel_size):
            x = i - center
            val = math.exp(-(x * x) / (2 * sigma * sigma))
            kernel.append(val)
            sum_val += val
        
        # 归一化核
        kernel = [val / sum_val for val in kernel]
        
        # 应用卷积
        result = []
        for i in range(n):
            val = 0.0
            for j in range(kernel_size):
                src_idx = i + j - center
                if 0 <= src_idx < n:
                    val += data[src_idx] * kernel[j]
            result.append(val)
        
        return result
    
    @staticmethod
    def moving_average(data: List[float], window_size: int) -> List[float]:
        """移动平均"""
        if not data or window_size <= 0:
            return data.copy()
        
        if window_size >= len(data):
            avg = sum(data) / len(data)
            return [avg] * len(data)
        
        result = []
        for i in range(len(data)):
            start = max(0, i - window_size // 2)
            end = min(len(data), i + window_size // 2 + 1)
            window_data = data[start:end]
            avg = sum(window_data) / len(window_data)
            result.append(avg)
        
        return result
