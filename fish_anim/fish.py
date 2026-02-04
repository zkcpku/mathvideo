import math
import pygame
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
    def __init__(self, origin: Vec2):
        self.spine = Chain(origin, 12, 64, math.pi / 8)
        self.body_color = (58, 124, 165)
        self.fin_color = (129, 195, 215)
        self.body_width = [68, 81, 84, 83, 77, 64, 51, 38, 32, 19]
    
    def resolve(self, mouse_pos: Vec2):
        head_pos = self.spine.joints[0]
        target_pos = head_pos + (mouse_pos - head_pos).set_mag(16)
        self.spine.resolve(target_pos)
    
    def get_pos(self, i: int, angle_offset: float, length_offset: float) -> Tuple[float, float]:
        joint = self.spine.joints[i]
        angle = self.spine.angles[i]
        width = self.body_width[i] if i < len(self.body_width) else 10
        return (
            joint.x + math.cos(angle + angle_offset) * (width + length_offset),
            joint.y + math.sin(angle + angle_offset) * (width + length_offset)
        )
    
    def display(self, screen: pygame.Surface):
        j = self.spine.joints
        a = self.spine.angles
        
        head_to_mid1 = relative_angle_diff(a[0], a[6])
        head_to_mid2 = relative_angle_diff(a[0], a[7])
        head_to_tail = head_to_mid1 + relative_angle_diff(a[6], a[11])
        
        self._draw_pectoral_fins(screen)
        self._draw_ventral_fins(screen)
        self._draw_caudal_fin(screen, head_to_tail)
        self._draw_body(screen)
        self._draw_dorsal_fin(screen, head_to_mid1, head_to_mid2)
        self._draw_eyes(screen)
    
    def _draw_pectoral_fins(self, screen: pygame.Surface):
        for side in [1, -1]:
            pos = self.get_pos(3, math.pi / 3 * side, 0)
            angle = self.spine.angles[2] - math.pi / 4 * side
            self._draw_rotated_ellipse(screen, pos, 160, 64, angle, self.fin_color)
    
    def _draw_ventral_fins(self, screen: pygame.Surface):
        for side in [1, -1]:
            pos = self.get_pos(7, math.pi / 2 * side, 0)
            angle = self.spine.angles[6] - math.pi / 4 * side
            self._draw_rotated_ellipse(screen, pos, 96, 32, angle, self.fin_color)
    
    def _draw_caudal_fin(self, screen: pygame.Surface, head_to_tail: float):
        j = self.spine.joints
        a = self.spine.angles
        
        points = []
        for i in range(8, 12):
            tail_width = 1.5 * head_to_tail * (i - 8) ** 2
            points.append((
                j[i].x + math.cos(a[i] - math.pi / 2) * tail_width,
                j[i].y + math.sin(a[i] - math.pi / 2) * tail_width
            ))
        
        for i in range(11, 7, -1):
            tail_width = max(-13, min(13, head_to_tail * 6))
            points.append((
                j[i].x + math.cos(a[i] + math.pi / 2) * tail_width,
                j[i].y + math.sin(a[i] + math.pi / 2) * tail_width
            ))
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, self.fin_color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 4)
    
    def _draw_body(self, screen: pygame.Surface):
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
        if len(smooth_points) >= 3:
            pygame.draw.polygon(screen, self.body_color, smooth_points)
            pygame.draw.polygon(screen, (255, 255, 255), smooth_points, 4)
    
    def _draw_dorsal_fin(self, screen: pygame.Surface, head_to_mid1: float, head_to_mid2: float):
        j = self.spine.joints
        a = self.spine.angles
        
        points = [
            (j[4].x, j[4].y),
            (j[5].x, j[5].y),
            (j[6].x, j[6].y),
            (j[7].x, j[7].y),
            (j[6].x + math.cos(a[6] + math.pi / 2) * head_to_mid2 * 16,
             j[6].y + math.sin(a[6] + math.pi / 2) * head_to_mid2 * 16),
            (j[5].x + math.cos(a[5] + math.pi / 2) * head_to_mid1 * 16,
             j[5].y + math.sin(a[5] + math.pi / 2) * head_to_mid1 * 16),
        ]
        
        if len(points) >= 3:
            pygame.draw.polygon(screen, self.fin_color, points)
            pygame.draw.polygon(screen, (255, 255, 255), points, 4)
    
    def _draw_eyes(self, screen: pygame.Surface):
        for side in [1, -1]:
            pos = self.get_pos(0, math.pi / 2 * side, -18)
            pygame.draw.circle(screen, (255, 255, 255), (int(pos[0]), int(pos[1])), 12)
    
    def _draw_rotated_ellipse(self, screen: pygame.Surface, center: Tuple[float, float], 
                               width: int, height: int, angle: float, color: Tuple[int, int, int]):
        surface = pygame.Surface((width + 10, height + 10), pygame.SRCALPHA)
        pygame.draw.ellipse(surface, color, (5, 5, width, height))
        pygame.draw.ellipse(surface, (255, 255, 255), (5, 5, width, height), 4)
        rotated = pygame.transform.rotate(surface, -math.degrees(angle))
        rect = rotated.get_rect(center=center)
        screen.blit(rotated, rect)
