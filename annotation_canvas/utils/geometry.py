# This Python file uses the following encoding: utf-8

"""
几何计算工具 - 提供几何计算相关的工具函数
"""

from typing import List, Tuple, Optional
from PySide6.QtCore import QPointF, QRectF
import math

class GeometryUtils:
    """几何计算工具类"""
    
    @staticmethod
    def distance_between_points(p1: QPointF, p2: QPointF) -> float:
        """计算两点间距离"""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def angle_between_points(p1: QPointF, p2: QPointF) -> float:
        """计算两点间角度（弧度）"""
        dx = p2.x() - p1.x()
        dy = p2.y() - p1.y()
        return math.atan2(dy, dx)
    
    @staticmethod
    def point_on_line(p1: QPointF, p2: QPointF, t: float) -> QPointF:
        """计算线段上的点（t=0为起点，t=1为终点）"""
        return QPointF(
            p1.x() + t * (p2.x() - p1.x()),
            p1.y() + t * (p2.y() - p1.y())
        )
    
    @staticmethod
    def point_to_line_distance(point: QPointF, line_start: QPointF, line_end: QPointF) -> float:
        """计算点到线段的距离"""
        # 计算线段向量
        line_vec_x = line_end.x() - line_start.x()
        line_vec_y = line_end.y() - line_start.y()
        
        # 计算点到线段起点的向量
        point_vec_x = point.x() - line_start.x()
        point_vec_y = point.y() - line_start.y()
        
        # 线段长度的平方
        line_length_sq = line_vec_x * line_vec_x + line_vec_y * line_vec_y
        
        if line_length_sq == 0:
            # 线段长度为0，返回点到起点的距离
            return math.sqrt(point_vec_x * point_vec_x + point_vec_y * point_vec_y)
        
        # 计算投影参数 t
        t = max(0, min(1, (point_vec_x * line_vec_x + point_vec_y * line_vec_y) / line_length_sq))
        
        # 计算投影点
        projection_x = line_start.x() + t * line_vec_x
        projection_y = line_start.y() + t * line_vec_y
        
        # 计算点到投影点的距离
        dx = point.x() - projection_x
        dy = point.y() - projection_y
        return math.sqrt(dx * dx + dy * dy)
    
    @staticmethod
    def is_point_in_rect(point: QPointF, rect: QRectF) -> bool:
        """检查点是否在矩形内"""
        return rect.contains(point)
    
    @staticmethod
    def is_point_in_circle(point: QPointF, center: QPointF, radius: float) -> bool:
        """检查点是否在圆形内"""
        distance = GeometryUtils.distance_between_points(point, center)
        return distance <= radius
    
    @staticmethod
    def is_point_in_ellipse(point: QPointF, center: QPointF, radius_x: float, radius_y: float) -> bool:
        """检查点是否在椭圆内"""
        if radius_x <= 0 or radius_y <= 0:
            return False
        
        dx = (point.x() - center.x()) / radius_x
        dy = (point.y() - center.y()) / radius_y
        distance = dx * dx + dy * dy
        return distance <= 1.0
    
    @staticmethod
    def is_point_in_polygon(point: QPointF, vertices: List[QPointF]) -> bool:
        """检查点是否在多边形内（射线法）"""
        if len(vertices) < 3:
            return False
        
        x, y = point.x(), point.y()
        n = len(vertices)
        inside = False
        
        p1x, p1y = vertices[0].x(), vertices[0].y()
        for i in range(1, n + 1):
            p2x, p2y = vertices[i % n].x(), vertices[i % n].y()
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    @staticmethod
    def polygon_center(vertices: List[QPointF]) -> QPointF:
        """计算多边形重心"""
        if not vertices:
            return QPointF(0, 0)
        
        x_sum = sum(v.x() for v in vertices)
        y_sum = sum(v.y() for v in vertices)
        n = len(vertices)
        
        return QPointF(x_sum / n, y_sum / n)
    
    @staticmethod
    def polygon_bounds(vertices: List[QPointF]) -> QRectF:
        """计算多边形边界矩形"""
        if not vertices:
            return QRectF()
        
        x_coords = [v.x() for v in vertices]
        y_coords = [v.y() for v in vertices]
        
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        return QRectF(min_x, min_y, max_x - min_x, max_y - min_y)
    
    @staticmethod
    def rect_center(rect: QRectF) -> QPointF:
        """计算矩形中心点"""
        return QPointF(
            rect.x() + rect.width() / 2,
            rect.y() + rect.height() / 2
        )
    
    @staticmethod
    def rect_corners(rect: QRectF) -> List[QPointF]:
        """获取矩形的四个角点"""
        return [
            QPointF(rect.x(), rect.y()),  # 左上角
            QPointF(rect.x() + rect.width(), rect.y()),  # 右上角
            QPointF(rect.x() + rect.width(), rect.y() + rect.height()),  # 右下角
            QPointF(rect.x(), rect.y() + rect.height())  # 左下角
        ]
    
    @staticmethod
    def rect_edges(rect: QRectF) -> List[Tuple[QPointF, QPointF]]:
        """获取矩形的四条边"""
        corners = GeometryUtils.rect_corners(rect)
        return [
            (corners[0], corners[1]),  # 上边
            (corners[1], corners[2]),  # 右边
            (corners[2], corners[3]),  # 下边
            (corners[3], corners[0])   # 左边
        ]
    
    @staticmethod
    def ellipse_points(center: QPointF, radius_x: float, radius_y: float, num_points: int = 50) -> List[QPointF]:
        """生成椭圆上的点"""
        if radius_x <= 0 or radius_y <= 0:
            return []
        
        points = []
        for i in range(num_points + 1):
            angle = i * 2 * math.pi / num_points
            x = center.x() + radius_x * math.cos(angle)
            y = center.y() + radius_y * math.sin(angle)
            points.append(QPointF(x, y))
        
        return points
    
    @staticmethod
    def snap_to_grid(point: QPointF, grid_size: float) -> QPointF:
        """将点对齐到网格"""
        x = round(point.x() / grid_size) * grid_size
        y = round(point.y() / grid_size) * grid_size
        return QPointF(x, y)
    
    @staticmethod
    def snap_to_point(point: QPointF, snap_points: List[QPointF], tolerance: float = None) -> Optional[QPointF]:
        """将点吸附到最近的吸附点"""
        from ..utils.constants import InteractionConstants
        if tolerance is None:
            tolerance = InteractionConstants.SHAPE_DEFAULT_TOLERANCE
            
        if not snap_points:
            return None
        
        min_distance = float('inf')
        closest_point = None
        
        for snap_point in snap_points:
            distance = GeometryUtils.distance_between_points(point, snap_point)
            if distance < min_distance and distance <= tolerance:
                min_distance = distance
                closest_point = snap_point
        
        return closest_point
    
    @staticmethod
    def line_intersection(p1: QPointF, p2: QPointF, p3: QPointF, p4: QPointF) -> Optional[QPointF]:
        """计算两条直线的交点"""
        # 计算直线参数
        denom = (p1.x() - p2.x()) * (p3.y() - p4.y()) - (p1.y() - p2.y()) * (p3.x() - p4.x())
        
        if abs(denom) < 1e-10:
            # 直线平行
            return None
        
        t = ((p1.x() - p3.x()) * (p3.y() - p4.y()) - (p1.y() - p3.y()) * (p3.x() - p4.x())) / denom
        
        # 计算交点
        x = p1.x() + t * (p2.x() - p1.x())
        y = p1.y() + t * (p2.y() - p1.y())
        
        return QPointF(x, y)
    
    @staticmethod
    def rotate_point(point: QPointF, center: QPointF, angle: float) -> QPointF:
        """绕中心点旋转点"""
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # 平移到原点
        x = point.x() - center.x()
        y = point.y() - center.y()
        
        # 旋转
        new_x = x * cos_a - y * sin_a
        new_y = x * sin_a + y * cos_a
        
        # 平移回原位置
        return QPointF(new_x + center.x(), new_y + center.y())
    
    @staticmethod
    def scale_point(point: QPointF, center: QPointF, scale_x: float, scale_y: float) -> QPointF:
        """以中心点为基准缩放点"""
        # 平移到原点
        x = point.x() - center.x()
        y = point.y() - center.y()
        
        # 缩放
        new_x = x * scale_x
        new_y = y * scale_y
        
        # 平移回原位置
        return QPointF(new_x + center.x(), new_y + center.y())
