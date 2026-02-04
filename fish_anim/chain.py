import math
from dataclasses import dataclass
from typing import List

@dataclass
class Vec2:
    x: float
    y: float
    
    def copy(self) -> 'Vec2':
        return Vec2(self.x, self.y)
    
    def __add__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vec2') -> 'Vec2':
        return Vec2(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vec2':
        return Vec2(self.x * scalar, self.y * scalar)
    
    def mag(self) -> float:
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def set_mag(self, m: float) -> 'Vec2':
        current = self.mag()
        if current == 0:
            return Vec2(m, 0)
        return self * (m / current)
    
    def heading(self) -> float:
        return math.atan2(self.y, self.x)
    
    @staticmethod
    def from_angle(angle: float) -> 'Vec2':
        return Vec2(math.cos(angle), math.sin(angle))
    
    @staticmethod
    def lerp(a: 'Vec2', b: 'Vec2', t: float) -> 'Vec2':
        return Vec2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t)
    
    @staticmethod
    def dist(a: 'Vec2', b: 'Vec2') -> float:
        return (a - b).mag()


def simplify_angle(angle: float) -> float:
    while angle >= 2 * math.pi:
        angle -= 2 * math.pi
    while angle < 0:
        angle += 2 * math.pi
    return angle


def relative_angle_diff(angle: float, anchor: float) -> float:
    angle = simplify_angle(angle + math.pi - anchor)
    anchor = math.pi
    return anchor - angle


def constrain_angle(angle: float, anchor: float, constraint: float) -> float:
    if abs(relative_angle_diff(angle, anchor)) <= constraint:
        return simplify_angle(angle)
    if relative_angle_diff(angle, anchor) > constraint:
        return simplify_angle(anchor - constraint)
    return simplify_angle(anchor + constraint)


def constrain_distance(pos: Vec2, anchor: Vec2, constraint: float) -> Vec2:
    return anchor + (pos - anchor).set_mag(constraint)


class Chain:
    def __init__(self, origin: Vec2, joint_count: int, link_size: int, angle_constraint: float = 2 * math.pi):
        self.link_size = link_size
        self.angle_constraint = angle_constraint
        self.joints: List[Vec2] = [origin.copy()]
        self.angles: List[float] = [0.0]
        
        for i in range(1, joint_count):
            self.joints.append(self.joints[i - 1] + Vec2(0, link_size))
            self.angles.append(0.0)
    
    def resolve(self, pos: Vec2):
        self.angles[0] = (pos - self.joints[0]).heading()
        self.joints[0] = pos
        
        for i in range(1, len(self.joints)):
            cur_angle = (self.joints[i - 1] - self.joints[i]).heading()
            self.angles[i] = constrain_angle(cur_angle, self.angles[i - 1], self.angle_constraint)
            self.joints[i] = self.joints[i - 1] - Vec2.from_angle(self.angles[i]).set_mag(self.link_size)
    
    def fabrik_resolve(self, pos: Vec2, anchor: Vec2):
        self.joints[0] = pos
        for i in range(1, len(self.joints)):
            self.joints[i] = constrain_distance(self.joints[i], self.joints[i - 1], self.link_size)
        
        self.joints[-1] = anchor
        for i in range(len(self.joints) - 2, -1, -1):
            self.joints[i] = constrain_distance(self.joints[i], self.joints[i + 1], self.link_size)
