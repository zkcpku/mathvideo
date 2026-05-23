import { Vec2 } from './vec2';

type JumpState = 'idle' | 'charging' | 'jumping' | 'landing';

export class Fish {
  pos: Vec2;
  scale: number;

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

  baseJumpHeight = 70;
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

    const renderX = this.pos.x;
    const renderY = this.pos.y - this.jumpHeight;

    // Shadow
    if (this.jumpHeight > 5) {
      this.drawShadow(ctx);
    }

    ctx.save();
    ctx.translate(renderX, renderY);
    ctx.scale(this.scale * this.stretchX, this.scale * this.stretchY);

    // Draw order: feet → flippers → body → belly → scarf → eyes → beak → star
    this.drawFeet(ctx);
    this.drawFlippers(ctx);
    this.drawBody(ctx);
    this.drawBelly(ctx);
    this.drawScarf(ctx);
    this.drawEyes(ctx);
    this.drawBeak(ctx);
    this.drawStar(ctx);

    ctx.restore();
    ctx.restore();
  }

  private drawShadow(ctx: CanvasRenderingContext2D): void {
    const shadowScale = Math.max(0.25, 1 - this.jumpHeight / (this.baseJumpHeight * 1.6));

    ctx.save();
    ctx.globalAlpha = 0.28 * shadowScale;
    ctx.fillStyle = 'rgba(0, 0, 0, 0.35)';
    ctx.beginPath();
    ctx.ellipse(
      this.pos.x,
      this.pos.y + 58 * this.scale,
      42 * this.scale * shadowScale,
      12 * this.scale * shadowScale,
      0, 0, Math.PI * 2
    );
    ctx.fill();
    ctx.restore();
  }

  private drawFeet(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = '#ff9f16';
    ctx.strokeStyle = '#d97800';
    ctx.lineWidth = 2;

    // Left foot
    ctx.beginPath();
    ctx.ellipse(-25, 61, 23, 8, -0.12, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Right foot
    ctx.beginPath();
    ctx.ellipse(25, 61, 23, 8, 0.12, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();
  }

  private drawFlippers(ctx: CanvasRenderingContext2D): void {
    ctx.fillStyle = '#050505';

    // Flipper wiggle during jump
    const flipperWiggle = this.state === 'jumping'
      ? Math.sin(this.stateTime * 20) * 0.15
      : Math.sin(this.earWiggle) * 0.03;

    for (const side of [-1, 1]) {
      ctx.save();
      ctx.rotate(side * flipperWiggle);

      ctx.beginPath();
      ctx.moveTo(side * 50, -8);
      ctx.bezierCurveTo(
        side * 78, 8,
        side * 73, 48,
        side * 53, 55
      );
      ctx.bezierCurveTo(
        side * 42, 40,
        side * 39, 10,
        side * 50, -8
      );
      ctx.closePath();
      ctx.fill();

      ctx.restore();
    }
  }

  private drawBody(ctx: CanvasRenderingContext2D): void {
    const bodyGrad = ctx.createLinearGradient(0, -72, 0, 72);
    bodyGrad.addColorStop(0, '#050505');
    bodyGrad.addColorStop(0.65, '#020202');
    bodyGrad.addColorStop(1, '#111111');

    ctx.fillStyle = bodyGrad;
    ctx.beginPath();
    ctx.moveTo(0, -72);

    // Right head/body
    ctx.bezierCurveTo(44, -72, 60, -48, 60, -10);
    // Right lower body
    ctx.bezierCurveTo(66, 38, 38, 72, 0, 72);
    // Left lower body
    ctx.bezierCurveTo(-38, 72, -66, 38, -60, -10);
    // Left head/body
    ctx.bezierCurveTo(-60, -48, -44, -72, 0, -72);

    ctx.closePath();
    ctx.fill();
  }

  private drawBelly(ctx: CanvasRenderingContext2D): void {
    const bellyGrad = ctx.createRadialGradient(-12, 10, 8, 0, 28, 52);
    bellyGrad.addColorStop(0, '#ffffff');
    bellyGrad.addColorStop(0.75, '#f7f7f7');
    bellyGrad.addColorStop(1, '#e8e8e8');

    ctx.fillStyle = bellyGrad;
    ctx.beginPath();
    ctx.ellipse(0, 27, 39, 45, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  private drawScarf(ctx: CanvasRenderingContext2D): void {
    ctx.lineCap = 'round';
    ctx.lineJoin = 'round';

    // Outer stroke (deep blue)
    ctx.strokeStyle = '#0872b8';
    ctx.lineWidth = 11;
    ctx.beginPath();
    ctx.moveTo(-53, -12);
    ctx.quadraticCurveTo(-20, 8, 3, 3);
    ctx.quadraticCurveTo(28, 0, 53, -14);
    ctx.stroke();

    // Inner highlight (cyan)
    ctx.strokeStyle = '#7ee8f2';
    ctx.lineWidth = 5;
    ctx.beginPath();
    ctx.moveTo(-51, -13);
    ctx.quadraticCurveTo(-20, 5, 3, 1);
    ctx.quadraticCurveTo(27, -1, 51, -15);
    ctx.stroke();
  }

  private drawEyes(ctx: CanvasRenderingContext2D): void {
    const eyeY = -43;
    const eyeRx = 12;
    const eyeRy = 21;
    const eyeSpacing = 17;

    // White sclera
    ctx.fillStyle = '#ffffff';

    ctx.beginPath();
    ctx.ellipse(-eyeSpacing, eyeY, eyeRx, eyeRy, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.ellipse(eyeSpacing, eyeY, eyeRx, eyeRy, 0, 0, Math.PI * 2);
    ctx.fill();

    // Pupils follow gaze
    const pupilOffsetX = Math.cos(this.facingAngle) * 2.5;
    const pupilOffsetY = Math.sin(this.facingAngle) * 2.5;

    ctx.fillStyle = '#111111';

    ctx.beginPath();
    ctx.ellipse(-eyeSpacing + pupilOffsetX, eyeY + pupilOffsetY + 1, 4.2, 6.5, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.ellipse(eyeSpacing + pupilOffsetX, eyeY + pupilOffsetY + 1, 4.2, 6.5, 0, 0, Math.PI * 2);
    ctx.fill();

    // Eye highlights
    ctx.fillStyle = 'rgba(255, 255, 255, 0.9)';

    ctx.beginPath();
    ctx.ellipse(-eyeSpacing - 2 + pupilOffsetX, eyeY - 2 + pupilOffsetY, 1.5, 2.2, 0, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.ellipse(eyeSpacing - 2 + pupilOffsetX, eyeY - 2 + pupilOffsetY, 1.5, 2.2, 0, 0, Math.PI * 2);
    ctx.fill();
  }

  private drawBeak(ctx: CanvasRenderingContext2D): void {
    const beakGrad = ctx.createLinearGradient(0, -30, 0, -13);
    beakGrad.addColorStop(0, '#ffd13b');
    beakGrad.addColorStop(1, '#ff8a00');

    ctx.fillStyle = beakGrad;
    ctx.strokeStyle = '#e27600';
    ctx.lineWidth = 1.5;

    ctx.beginPath();
    ctx.ellipse(0, -22, 20, 8, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.stroke();

    // Lower beak crease
    ctx.strokeStyle = 'rgba(180, 90, 0, 0.45)';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(-12, -20);
    ctx.quadraticCurveTo(0, -15, 12, -20);
    ctx.stroke();
  }

  private drawStar(ctx: CanvasRenderingContext2D): void {
    ctx.save();
    ctx.translate(36, 23);
    ctx.rotate(0.25);

    const outerR = 13;
    const innerR = 6;

    ctx.beginPath();
    for (let i = 0; i < 10; i++) {
      const angle = -Math.PI / 2 + i * Math.PI / 5;
      const r = i % 2 === 0 ? outerR : innerR;
      const x = Math.cos(angle) * r;
      const y = Math.sin(angle) * r;

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();

    ctx.fillStyle = '#ffd83b';
    ctx.strokeStyle = '#e5a600';
    ctx.lineWidth = 2;
    ctx.fill();
    ctx.stroke();

    ctx.restore();
  }
}
