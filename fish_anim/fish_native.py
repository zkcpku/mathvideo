import math
from typing import List, Tuple
from chain import Chain, Vec2, relative_angle_diff


def catmull_rom_spline(points: List[Tuple[float, float]], num_segments: int = 10) -> List[Tuple[float, float]]:
    if len(points) < 4:
        return points
    
    result = []
    for i in range(1, len(points) - 2):
        p0, p1, p2, p3 = points[i - 1], points[i], points[i + 1], points[i + 2]
        for t in range(num_segments):
            t = t / num_segments
            t2 = t * t
            t3 = t2 * t
            
            x = 0.5 * ((2 * p1[0]) +
                       (-p0[0] + p2[0]) * t +
                       (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                       (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) +
                       (-p0[1] + p2[1]) * t +
                       (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                       (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            result.append((x, y))
    
    return result


class Fish:
    def __init__(self, origin: Vec2, scale: float = 1.0):
        self.scale = scale
        self.spine = Chain(origin, 12, int(64 * scale), math.pi / 8)
        self.body_color = (58/255, 124/255, 165/255, 1.0)
        self.fin_color = (129/255, 195/255, 215/255, 1.0)
        self.stroke_color = (1.0, 1.0, 1.0, 1.0)
        self.body_width = [int(w * scale) for w in [68, 81, 84, 83, 77, 64, 51, 38, 32, 19]]
    
    def resolve(self, mouse_pos: Vec2):
        head_pos = self.spine.joints[0]
        target_pos = head_pos + (mouse_pos - head_pos).set_mag(16 * self.scale)
        self.spine.resolve(target_pos)
    
    def get_pos(self, i: int, angle_offset: float, length_offset: float) -> Tuple[float, float]:
        joint = self.spine.joints[i]
        angle = self.spine.angles[i]
        width = self.body_width[i] if i < len(self.body_width) else 10
        return (
            joint.x + math.cos(angle + angle_offset) * (width + length_offset),
            joint.y + math.sin(angle + angle_offset) * (width + length_offset)
        )
    
    def draw(self, ctx):
        from Quartz import CGContextSetRGBFillColor, CGContextSetRGBStrokeColor, CGContextSetLineWidth
        from Quartz import CGContextBeginPath, CGContextMoveToPoint, CGContextAddLineToPoint
        from Quartz import CGContextClosePath, CGContextDrawPath, kCGPathFillStroke, kCGPathFill
        from Quartz import CGContextAddEllipseInRect, CGContextFillEllipseInRect, CGContextStrokeEllipseInRect
        from Quartz import CGContextSaveGState, CGContextRestoreGState, CGContextTranslateCTM, CGContextRotateCTM
        from Foundation import NSMakeRect
        
        j = self.spine.joints
        a = self.spine.angles
        
        head_to_mid1 = relative_angle_diff(a[0], a[6])
        head_to_mid2 = relative_angle_diff(a[0], a[7])
        head_to_tail = head_to_mid1 + relative_angle_diff(a[6], a[11])
        
        CGContextSetLineWidth(ctx, 4)
        
        self._draw_pectoral_fins(ctx)
        self._draw_ventral_fins(ctx)
        self._draw_caudal_fin(ctx, head_to_tail)
        self._draw_body(ctx)
        self._draw_dorsal_fin(ctx, head_to_mid1, head_to_mid2)
        self._draw_eyes(ctx)
    
    def _draw_polygon(self, ctx, points, fill_color, stroke=True):
        from Quartz import CGContextSetRGBFillColor, CGContextSetRGBStrokeColor
        from Quartz import CGContextBeginPath, CGContextMoveToPoint, CGContextAddLineToPoint
        from Quartz import CGContextClosePath, CGContextDrawPath, kCGPathFillStroke, kCGPathFill
        
        if len(points) < 3:
            return
        
        CGContextBeginPath(ctx)
        CGContextMoveToPoint(ctx, points[0][0], points[0][1])
        for p in points[1:]:
            CGContextAddLineToPoint(ctx, p[0], p[1])
        CGContextClosePath(ctx)
        
        CGContextSetRGBFillColor(ctx, fill_color[0], fill_color[1], fill_color[2], fill_color[3])
        if stroke:
            CGContextSetRGBStrokeColor(ctx, 1, 1, 1, 1)
            CGContextDrawPath(ctx, kCGPathFillStroke)
        else:
            CGContextDrawPath(ctx, kCGPathFill)
    
    def _draw_ellipse(self, ctx, center, width, height, angle, fill_color):
        from Quartz import CGContextSaveGState, CGContextRestoreGState, CGContextTranslateCTM, CGContextRotateCTM
        from Quartz import CGContextSetRGBFillColor, CGContextSetRGBStrokeColor
        from Quartz import CGContextFillEllipseInRect, CGContextStrokeEllipseInRect
        from Foundation import NSMakeRect
        
        CGContextSaveGState(ctx)
        CGContextTranslateCTM(ctx, center[0], center[1])
        CGContextRotateCTM(ctx, angle)
        
        rect = NSMakeRect(-width/2, -height/2, width, height)
        CGContextSetRGBFillColor(ctx, fill_color[0], fill_color[1], fill_color[2], fill_color[3])
        CGContextFillEllipseInRect(ctx, rect)
        CGContextSetRGBStrokeColor(ctx, 1, 1, 1, 1)
        CGContextStrokeEllipseInRect(ctx, rect)
        
        CGContextRestoreGState(ctx)
    
    def _draw_pectoral_fins(self, ctx):
        for side in [1, -1]:
            pos = self.get_pos(3, math.pi / 3 * side, 0)
            angle = self.spine.angles[2] - math.pi / 4 * side
            self._draw_ellipse(ctx, pos, 160 * self.scale, 64 * self.scale, angle, self.fin_color)
    
    def _draw_ventral_fins(self, ctx):
        for side in [1, -1]:
            pos = self.get_pos(7, math.pi / 2 * side, 0)
            angle = self.spine.angles[6] - math.pi / 4 * side
            self._draw_ellipse(ctx, pos, 96 * self.scale, 32 * self.scale, angle, self.fin_color)
    
    def _draw_caudal_fin(self, ctx, head_to_tail: float):
        j = self.spine.joints
        a = self.spine.angles
        
        points = []
        for i in range(8, 12):
            tail_width = 1.5 * head_to_tail * (i - 8) ** 2 * self.scale
            points.append((
                j[i].x + math.cos(a[i] - math.pi / 2) * tail_width,
                j[i].y + math.sin(a[i] - math.pi / 2) * tail_width
            ))
        
        for i in range(11, 7, -1):
            tail_width = max(-13, min(13, head_to_tail * 6)) * self.scale
            points.append((
                j[i].x + math.cos(a[i] + math.pi / 2) * tail_width,
                j[i].y + math.sin(a[i] + math.pi / 2) * tail_width
            ))
        
        self._draw_polygon(ctx, points, self.fin_color)
    
    def _draw_body(self, ctx):
        points = []
        
        for i in range(10):
            points.append(self.get_pos(i, math.pi / 2, 0))
        points.append(self.get_pos(9, math.pi, 0))
        for i in range(9, -1, -1):
            points.append(self.get_pos(i, -math.pi / 2, 0))
        points.append(self.get_pos(0, -math.pi / 6, 0))
        points.append(self.get_pos(0, 0, 4))
        points.append(self.get_pos(0, math.pi / 6, 0))
        
        points.append(points[0])
        points.append(points[1])
        points.append(points[2])
        
        smooth_points = catmull_rom_spline(points, 8)
        self._draw_polygon(ctx, smooth_points, self.body_color)
    
    def _draw_dorsal_fin(self, ctx, head_to_mid1: float, head_to_mid2: float):
        j = self.spine.joints
        a = self.spine.angles
        
        points = [
            (j[4].x, j[4].y),
            (j[5].x, j[5].y),
            (j[6].x, j[6].y),
            (j[7].x, j[7].y),
            (j[6].x + math.cos(a[6] + math.pi / 2) * head_to_mid2 * 16 * self.scale,
             j[6].y + math.sin(a[6] + math.pi / 2) * head_to_mid2 * 16 * self.scale),
            (j[5].x + math.cos(a[5] + math.pi / 2) * head_to_mid1 * 16 * self.scale,
             j[5].y + math.sin(a[5] + math.pi / 2) * head_to_mid1 * 16 * self.scale),
        ]
        
        self._draw_polygon(ctx, points, self.fin_color)
    
    def _draw_eyes(self, ctx):
        from Quartz import CGContextSetRGBFillColor, CGContextFillEllipseInRect
        from Foundation import NSMakeRect
        
        CGContextSetRGBFillColor(ctx, 1, 1, 1, 1)
        eye_size = 24 * self.scale
        eye_offset = 18 * self.scale
        for side in [1, -1]:
            pos = self.get_pos(0, math.pi / 2 * side, -eye_offset)
            rect = NSMakeRect(pos[0] - eye_size/2, pos[1] - eye_size/2, eye_size, eye_size)
            CGContextFillEllipseInRect(ctx, rect)
