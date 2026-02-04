import { Vec2 } from './vec2';
import { Chain, relativeAngleDiff } from './chain';
import { catmullRomSpline, type Point } from './spline';

export class Fish {
  spine: Chain;
  scale: number;
  bodyColor = 'rgb(58, 124, 165)';
  finColor = 'rgb(129, 195, 215)';
  bodyWidth: number[];

  constructor(origin: Vec2, scale: number = 0.1) {
    this.scale = scale;
    this.spine = new Chain(origin, 12, Math.round(64 * scale), Math.PI / 8);
    this.bodyWidth = [68, 81, 84, 83, 77, 64, 51, 38, 32, 19].map(w => Math.round(w * scale));
  }

  resolve(mousePos: Vec2): void {
    const headPos = this.spine.joints[0];
    const toMouse = mousePos.sub(headPos);
    const dist = toMouse.mag();
    const step = Math.min(16 * this.scale, dist);
    if (step < 0.01) return;
    const targetPos = headPos.add(toMouse.setMag(step));
    this.spine.resolve(targetPos);
  }

  getPos(i: number, angleOffset: number, lengthOffset: number): Point {
    const joint = this.spine.joints[i];
    const angle = this.spine.angles[i];
    const width = i < this.bodyWidth.length ? this.bodyWidth[i] : 10 * this.scale;
    return [
      joint.x + Math.cos(angle + angleOffset) * (width + lengthOffset * this.scale),
      joint.y + Math.sin(angle + angleOffset) * (width + lengthOffset * this.scale),
    ];
  }

  render(ctx: CanvasRenderingContext2D): void {
    const a = this.spine.angles;

    const headToMid1 = relativeAngleDiff(a[0], a[6]);
    const headToMid2 = relativeAngleDiff(a[0], a[7]);
    const headToTail = headToMid1 + relativeAngleDiff(a[6], a[11]);

    ctx.lineWidth = 4 * this.scale;

    this.drawPectoralFins(ctx);
    this.drawVentralFins(ctx);
    this.drawCaudalFin(ctx, headToTail);
    this.drawBody(ctx);
    this.drawDorsalFin(ctx, headToMid1, headToMid2);
    this.drawEyes(ctx);
  }

  private drawPolygon(
    ctx: CanvasRenderingContext2D,
    points: Point[],
    fillColor: string,
    stroke: boolean = true
  ): void {
    if (points.length < 3) return;

    ctx.beginPath();
    ctx.moveTo(points[0][0], points[0][1]);
    for (let i = 1; i < points.length; i++) {
      ctx.lineTo(points[i][0], points[i][1]);
    }
    ctx.closePath();

    ctx.fillStyle = fillColor;
    ctx.fill();

    if (stroke) {
      ctx.strokeStyle = 'white';
      ctx.stroke();
    }
  }

  private drawRotatedEllipse(
    ctx: CanvasRenderingContext2D,
    center: Point,
    width: number,
    height: number,
    angle: number,
    fillColor: string
  ): void {
    ctx.save();
    ctx.translate(center[0], center[1]);
    ctx.rotate(angle);

    ctx.beginPath();
    ctx.ellipse(0, 0, width / 2, height / 2, 0, 0, Math.PI * 2);
    ctx.fillStyle = fillColor;
    ctx.fill();
    ctx.strokeStyle = 'white';
    ctx.stroke();

    ctx.restore();
  }

  private drawPectoralFins(ctx: CanvasRenderingContext2D): void {
    for (const side of [1, -1]) {
      const pos = this.getPos(3, (Math.PI / 3) * side, 0);
      const angle = this.spine.angles[2] - (Math.PI / 4) * side;
      this.drawRotatedEllipse(ctx, pos, 160 * this.scale, 64 * this.scale, angle, this.finColor);
    }
  }

  private drawVentralFins(ctx: CanvasRenderingContext2D): void {
    for (const side of [1, -1]) {
      const pos = this.getPos(7, (Math.PI / 2) * side, 0);
      const angle = this.spine.angles[6] - (Math.PI / 4) * side;
      this.drawRotatedEllipse(ctx, pos, 96 * this.scale, 32 * this.scale, angle, this.finColor);
    }
  }

  private drawCaudalFin(
    ctx: CanvasRenderingContext2D,
    headToTail: number
  ): void {
    const j = this.spine.joints;
    const a = this.spine.angles;

    const points: Point[] = [];

    for (let i = 8; i < 12; i++) {
      const tailWidth = 1.5 * headToTail * Math.pow(i - 8, 2) * this.scale;
      points.push([
        j[i].x + Math.cos(a[i] - Math.PI / 2) * tailWidth,
        j[i].y + Math.sin(a[i] - Math.PI / 2) * tailWidth,
      ]);
    }

    for (let i = 11; i > 7; i--) {
      const tailWidth = Math.max(-13, Math.min(13, headToTail * 6)) * this.scale;
      points.push([
        j[i].x + Math.cos(a[i] + Math.PI / 2) * tailWidth,
        j[i].y + Math.sin(a[i] + Math.PI / 2) * tailWidth,
      ]);
    }

    this.drawPolygon(ctx, points, this.finColor);
  }

  private drawBody(ctx: CanvasRenderingContext2D): void {
    const points: Point[] = [];

    for (let i = 0; i < 10; i++) {
      points.push(this.getPos(i, Math.PI / 2, 0));
    }
    points.push(this.getPos(9, Math.PI, 0));
    for (let i = 9; i >= 0; i--) {
      points.push(this.getPos(i, -Math.PI / 2, 0));
    }
    points.push(this.getPos(0, -Math.PI / 6, 0));
    points.push(this.getPos(0, 0, 4));
    points.push(this.getPos(0, Math.PI / 6, 0));

    points.push(points[0]);
    points.push(points[1]);
    points.push(points[2]);

    const smoothPoints = catmullRomSpline(points, 8);
    if (smoothPoints.length >= 3) {
      this.drawPolygon(ctx, smoothPoints, this.bodyColor);
    }
  }

  private drawDorsalFin(
    ctx: CanvasRenderingContext2D,
    headToMid1: number,
    headToMid2: number
  ): void {
    const j = this.spine.joints;
    const a = this.spine.angles;

    const points: Point[] = [
      [j[4].x, j[4].y],
      [j[5].x, j[5].y],
      [j[6].x, j[6].y],
      [j[7].x, j[7].y],
      [
        j[6].x + Math.cos(a[6] + Math.PI / 2) * headToMid2 * 16 * this.scale,
        j[6].y + Math.sin(a[6] + Math.PI / 2) * headToMid2 * 16 * this.scale,
      ],
      [
        j[5].x + Math.cos(a[5] + Math.PI / 2) * headToMid1 * 16 * this.scale,
        j[5].y + Math.sin(a[5] + Math.PI / 2) * headToMid1 * 16 * this.scale,
      ],
    ];

    this.drawPolygon(ctx, points, this.finColor);
  }

  private drawEyes(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = 'white';
    for (const side of [1, -1]) {
      const pos = this.getPos(0, (Math.PI / 2) * side, -18);
      ctx.beginPath();
      ctx.arc(pos[0], pos[1], 12 * this.scale, 0, Math.PI * 2);
      ctx.fill();
    }
  }
}
