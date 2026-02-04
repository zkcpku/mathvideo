import { Vec2 } from './vec2';

export function simplifyAngle(angle: number): number {
  while (angle >= 2 * Math.PI) {
    angle -= 2 * Math.PI;
  }
  while (angle < 0) {
    angle += 2 * Math.PI;
  }
  return angle;
}

export function relativeAngleDiff(angle: number, anchor: number): number {
  angle = simplifyAngle(angle + Math.PI - anchor);
  anchor = Math.PI;
  return anchor - angle;
}

export function constrainAngle(
  angle: number,
  anchor: number,
  constraint: number
): number {
  if (Math.abs(relativeAngleDiff(angle, anchor)) <= constraint) {
    return simplifyAngle(angle);
  }
  if (relativeAngleDiff(angle, anchor) > constraint) {
    return simplifyAngle(anchor - constraint);
  }
  return simplifyAngle(anchor + constraint);
}

export function constrainDistance(
  pos: Vec2,
  anchor: Vec2,
  constraint: number
): Vec2 {
  return anchor.add(pos.sub(anchor).setMag(constraint));
}

export class Chain {
  linkSize: number;
  angleConstraint: number;
  joints: Vec2[];
  angles: number[];

  constructor(
    origin: Vec2,
    jointCount: number,
    linkSize: number,
    angleConstraint: number = 2 * Math.PI
  ) {
    this.linkSize = linkSize;
    this.angleConstraint = angleConstraint;
    this.joints = [origin.copy()];
    this.angles = [0.0];

    for (let i = 1; i < jointCount; i++) {
      this.joints.push(this.joints[i - 1].add(new Vec2(0, linkSize)));
      this.angles.push(0.0);
    }
  }

  resolve(pos: Vec2): void {
    this.angles[0] = pos.sub(this.joints[0]).heading();
    this.joints[0] = pos;

    for (let i = 1; i < this.joints.length; i++) {
      const curAngle = this.joints[i - 1].sub(this.joints[i]).heading();
      this.angles[i] = constrainAngle(
        curAngle,
        this.angles[i - 1],
        this.angleConstraint
      );
      this.joints[i] = this.joints[i - 1].sub(
        Vec2.fromAngle(this.angles[i]).setMag(this.linkSize)
      );
    }
  }
}
