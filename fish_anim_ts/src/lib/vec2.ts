export class Vec2 {
  constructor(
    public readonly x: number,
    public readonly y: number
  ) {}

  copy(): Vec2 {
    return new Vec2(this.x, this.y);
  }

  add(other: Vec2): Vec2 {
    return new Vec2(this.x + other.x, this.y + other.y);
  }

  sub(other: Vec2): Vec2 {
    return new Vec2(this.x - other.x, this.y - other.y);
  }

  mul(scalar: number): Vec2 {
    return new Vec2(this.x * scalar, this.y * scalar);
  }

  mag(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  }

  setMag(m: number): Vec2 {
    const current = this.mag();
    if (current === 0) {
      return new Vec2(m, 0);
    }
    return this.mul(m / current);
  }

  heading(): number {
    return Math.atan2(this.y, this.x);
  }

  static fromAngle(angle: number): Vec2 {
    return new Vec2(Math.cos(angle), Math.sin(angle));
  }

  static lerp(a: Vec2, b: Vec2, t: number): Vec2 {
    return new Vec2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
  }

  static dist(a: Vec2, b: Vec2): number {
    return a.sub(b).mag();
  }
}
