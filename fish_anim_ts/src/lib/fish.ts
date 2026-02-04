import { Vec2 } from './vec2';

type JumpState = 'idle' | 'charging' | 'jumping' | 'landing';

export class Fish {
  pos: Vec2;
  scale: number;
  bodyColor = 'rgba(0, 255, 210, 1)';
  leafColor = 'rgba(0, 220, 100, 1)';

  state: JumpState = 'idle';
  stateTime = 0;

  jumpStart: Vec2 = new Vec2(0, 0);
  jumpTarget: Vec2 = new Vec2(0, 0);
  jumpHeight = 0;

  stretchX = 1;
  stretchY = 1;

  chargeDuration = 0.12;
  jumpDuration = 0.35;
  landDuration = 0.08;
  idleTime = 0;
  idleThreshold = 0.02;

  baseJumpHeight = 60;
  baseJumpDistance = 100;

  facingAngle = 0;
  earWiggle = 0;

  constructor(origin: Vec2, scale: number = 1.0) {
    this.scale = scale;
    this.pos = origin.copy();
    this.baseJumpHeight *= scale;
    this.baseJumpDistance *= scale;
  }

  resolve(mousePos: Vec2): void {
    const dt = 1 / 60;
    const toMouse = mousePos.sub(this.pos);
    const dist = toMouse.mag();

    if (dist > 5) {
      const targetAngle = Math.atan2(toMouse.y, toMouse.x);
      let angleDiff = targetAngle - this.facingAngle;
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      this.facingAngle += angleDiff * 0.15;
    }

    switch (this.state) {
      case 'idle':
        this.handleIdle(mousePos, dist, dt);
        break;
      case 'charging':
        this.handleCharging(mousePos, dt);
        break;
      case 'jumping':
        this.handleJumping(dt);
        break;
      case 'landing':
        this.handleLanding(dt);
        break;
    }

    this.earWiggle += 0.12;
  }

  private handleIdle(mousePos: Vec2, dist: number, dt: number): void {
    const jumpThreshold = 40 * this.scale;
    if (dist > jumpThreshold) {
      this.idleTime += dt;
      if (this.idleTime > this.idleThreshold) {
        this.state = 'charging';
        this.stateTime = 0;
        this.jumpStart = this.pos.copy();

        const direction = mousePos.sub(this.pos);
        const jumpDist = Math.min(dist, this.baseJumpDistance);
        this.jumpTarget = this.pos.add(direction.setMag(jumpDist));
      }
    } else {
      this.idleTime = 0;
    }

    const idleBounce = Math.sin(Date.now() * 0.006) * 0.04;
    this.stretchX = 1 + idleBounce;
    this.stretchY = 1 - idleBounce;
    this.jumpHeight = 0;
  }

  private handleCharging(mousePos: Vec2, dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.chargeDuration, 1);

    this.stretchX = 1 + 0.25 * t;
    this.stretchY = 1 - 0.2 * t;

    const direction = mousePos.sub(this.pos);
    const dist = direction.mag();
    const jumpDist = Math.min(dist, this.baseJumpDistance);
    this.jumpTarget = this.pos.add(direction.setMag(jumpDist));

    if (t >= 1) {
      this.state = 'jumping';
      this.stateTime = 0;
      this.jumpStart = this.pos.copy();
    }
  }

  private handleJumping(dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.jumpDuration, 1);

    this.pos = Vec2.lerp(this.jumpStart, this.jumpTarget, t);

    this.jumpHeight = Math.sin(t * Math.PI) * this.baseJumpHeight;

    const stretchPhase = t < 0.3 ? t / 0.3 : (1 - t) / 0.7;
    this.stretchY = 1 + stretchPhase * 0.15;
    this.stretchX = 1 - stretchPhase * 0.1;

    if (t >= 1) {
      this.state = 'landing';
      this.stateTime = 0;
      this.jumpHeight = 0;
    }
  }

  private handleLanding(dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.landDuration, 1);

    const squash = Math.sin(t * Math.PI) * 0.2;
    this.stretchX = 1 + squash;
    this.stretchY = 1 - squash;
    this.jumpHeight = 0;

    if (t >= 1) {
      this.state = 'idle';
      this.stateTime = 0;
      this.idleTime = 0;
    }
  }

  render(ctx: CanvasRenderingContext2D): void {
    ctx.save();

    const renderY = this.pos.y - this.jumpHeight;

    ctx.shadowBlur = 20 * this.scale;
    ctx.shadowColor = this.bodyColor;

    if (this.jumpHeight > 5) {
      this.drawShadow(ctx);
    }

    this.drawEars(ctx, renderY);
    this.drawBody(ctx, renderY);
    this.drawEyes(ctx, renderY);

    ctx.shadowBlur = 0;
    ctx.restore();
  }

  private drawShadow(ctx: CanvasRenderingContext2D): void {
    const shadowScale = 1 - this.jumpHeight / (this.baseJumpHeight * 2);
    const shadowWidth = 40 * this.scale * shadowScale;
    const shadowHeight = 15 * this.scale * shadowScale;

    ctx.save();
    ctx.globalAlpha = 0.3 * shadowScale;
    ctx.beginPath();
    ctx.ellipse(this.pos.x, this.pos.y + 25 * this.scale, shadowWidth, shadowHeight, 0, 0, Math.PI * 2);
    ctx.fillStyle = 'black';
    ctx.fill();
    ctx.restore();
  }

  private drawBody(ctx: CanvasRenderingContext2D, renderY: number): void {
    const baseWidth = 50 * this.scale;
    const baseHeight = 60 * this.scale;

    const width = baseWidth * this.stretchX;
    const height = baseHeight * this.stretchY;

    ctx.save();
    ctx.translate(this.pos.x, renderY);

    ctx.beginPath();
    ctx.moveTo(0, -height * 0.6);

    ctx.bezierCurveTo(
      width * 0.8, -height * 0.5,
      width * 0.9, height * 0.1,
      width * 0.3, height * 0.4
    );

    ctx.quadraticCurveTo(0, height * 0.5, -width * 0.3, height * 0.4);

    ctx.bezierCurveTo(
      -width * 0.9, height * 0.1,
      -width * 0.8, -height * 0.5,
      0, -height * 0.6
    );

    ctx.closePath();

    ctx.fillStyle = this.bodyColor;
    ctx.fill();
    ctx.lineWidth = 2 * this.scale;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
    ctx.stroke();

    ctx.restore();
  }

  private drawEars(ctx: CanvasRenderingContext2D, renderY: number): void {
    const leafLength = 55 * this.scale;
    const leafWidth = 25 * this.scale;

    const earBaseY = renderY - 50 * this.scale * this.stretchY;

    for (const side of [1, -1]) {
      ctx.save();

      const earX = this.pos.x + side * 15 * this.scale * this.stretchX;
      ctx.translate(earX, earBaseY);

      const wiggle = Math.sin(this.earWiggle + side * 0.5) * 0.08;
      const moveWiggle = this.state === 'jumping' ? Math.sin(this.stateTime * 25) * 0.15 : 0;
      const angle = -Math.PI / 2 + side * 0.35 + wiggle + moveWiggle;

      ctx.rotate(angle);

      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.quadraticCurveTo(leafWidth * 0.6, leafLength * 0.4, 0, leafLength);
      ctx.quadraticCurveTo(-leafWidth * 0.6, leafLength * 0.4, 0, 0);

      ctx.fillStyle = this.leafColor;
      ctx.fill();
      ctx.lineWidth = 2 * this.scale;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.5)';
      ctx.stroke();

      ctx.restore();
    }
  }

  private drawEyes(ctx: CanvasRenderingContext2D, renderY: number): void {
    const eyeSize = 18 * this.scale;
    const pupilSize = 8 * this.scale;
    const eyeSpacing = 22 * this.scale * this.stretchX;
    const eyeY = renderY - 15 * this.scale * this.stretchY;

    for (const side of [1, -1]) {
      const eyeX = this.pos.x + side * eyeSpacing;

      ctx.beginPath();
      ctx.ellipse(
        eyeX, eyeY,
        eyeSize * this.stretchX,
        eyeSize * this.stretchY,
        0, 0, Math.PI * 2
      );
      ctx.fillStyle = 'white';
      ctx.fill();

      const lookOffset = 4 * this.scale;
      const pupilX = eyeX + Math.cos(this.facingAngle) * lookOffset;
      const pupilY = eyeY + Math.sin(this.facingAngle) * lookOffset;

      ctx.beginPath();
      ctx.arc(pupilX, pupilY, pupilSize, 0, Math.PI * 2);
      ctx.fillStyle = 'black';
      ctx.fill();

      ctx.beginPath();
      ctx.arc(
        pupilX - pupilSize * 0.3,
        pupilY - pupilSize * 0.3,
        pupilSize * 0.35,
        0, Math.PI * 2
      );
      ctx.fillStyle = 'white';
      ctx.fill();
    }
  }
}
