import { Vec2 } from './vec2';

type JumpState = 'idle' | 'charging' | 'jumping' | 'landing';

export class Fish {
  pos: Vec2;
  scale: number;
  
  // Updated colors to match the image gradient
  bodyColorInner = '#00FFF0'; // Bright Cyan center
  bodyColorOuter = '#00C0C0'; // Darker Cyan edge
  leafColorStart = '#40FF80'; // Bright Green tip
  leafColorEnd = '#00A060';   // Dark Green base

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

    // Outer glow for that "spirit" look
    ctx.shadowBlur = 30 * this.scale;
    ctx.shadowColor = this.bodyColorInner;

    if (this.jumpHeight > 5) {
      this.drawShadow(ctx);
    }

    // Draw order: Ears (behind) -> Body -> Eyes
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
    const baseWidth = 60 * this.scale;
    const baseHeight = 55 * this.scale;

    const width = baseWidth * this.stretchX;
    const height = baseHeight * this.stretchY;

    ctx.save();
    ctx.translate(this.pos.x, renderY);

    // Create radial gradient for the "jelly" look
    const gradient = ctx.createRadialGradient(
      0, -height * 0.1, 0, // Light source slightly up
      0, 0, width * 1.2    // Outer radius
    );
    gradient.addColorStop(0, this.bodyColorInner);
    gradient.addColorStop(0.8, this.bodyColorOuter);
    gradient.addColorStop(1, 'rgba(0, 192, 192, 0.8)'); // Translucent edge

    ctx.beginPath();
    
    // Top point (connection to stem)
    // Lowered slightly to allow for a much flatter, rounder top dome
    ctx.moveTo(0, -height * 0.7);

    // Right side - SUPER ROUND
    ctx.bezierCurveTo(
      width * 0.6, -height * 0.7,  // CP1: Horizontal tangent at top (creates dome)
      width * 1.1, -height * 0.2,  // CP2: Wide middle
      width * 1.0, height * 0.4    // End: Lower flank
    );

    // Bottom - continuous smooth bowl
    ctx.bezierCurveTo(
      width * 0.95, height * 0.8,  // CP1: Round bottom corner
      -width * 0.95, height * 0.8, // CP2: Mirror
      -width * 1.0, height * 0.4   // End: Mirror
    );

    // Left side - mirror of right
    ctx.bezierCurveTo(
      -width * 1.1, -height * 0.2,
      -width * 0.6, -height * 0.7,
      0, -height * 0.7
    );

    ctx.closePath();

    ctx.fillStyle = gradient;
    ctx.fill();

    // Subtle rim light
    ctx.lineWidth = 3 * this.scale;
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
    ctx.stroke();

    ctx.restore();
  }

  private drawEars(ctx: CanvasRenderingContext2D, renderY: number): void {
    const leafLength = 60 * this.scale;
    const leafWidth = 35 * this.scale;

    // Stem connects exactly at the top point of the body (0.7 factor matches drawBody)
    const stemY = renderY - 55 * this.scale * 0.7 * this.stretchY;

    for (const side of [1, -1]) {
      ctx.save();
      ctx.translate(this.pos.x, stemY);

      // Wiggle effect
      const wiggle = Math.sin(this.earWiggle + side * 0.5) * 0.08;
      const moveWiggle = this.state === 'jumping' ? Math.sin(this.stateTime * 25) * 0.15 : 0;
      
      // Symmetrical rotation: +angle for Right (1), -angle for Left (-1)
      // 0.6 radians is about 35 degrees tilt from vertical
      const angle = side * 0.6 + wiggle + moveWiggle;
      ctx.rotate(angle);

      // Leaf gradient
      // Gradient runs from base (0,0) to tip (0, -leafLength)
      const gradient = ctx.createLinearGradient(0, 0, 0, -leafLength);
      gradient.addColorStop(0, this.leafColorEnd);   // Darker at base
      gradient.addColorStop(1, this.leafColorStart); // Brighter at tip

      // Draw leaf shape pointing UP
      ctx.beginPath();
      ctx.moveTo(0, 0);
      
      // Right curve of the leaf
      ctx.bezierCurveTo(
        leafWidth * 0.6, -leafLength * 0.3, // CP1: Wide base
        0, -leafLength,                     // CP2: Tip
        0, -leafLength                      // End: Tip
      );
      
      // Left curve of the leaf
      ctx.bezierCurveTo(
        -leafWidth * 0.6, -leafLength * 0.3, // CP1: Wide base
        0, 0,                                // CP2: Base
        0, 0                                 // End: Base
      );

      ctx.fillStyle = gradient;
      ctx.fill();

      // Leaf vein (center line)
      ctx.beginPath();
      ctx.moveTo(0, -5 * this.scale);
      ctx.lineTo(0, -leafLength * 0.7);
      ctx.lineWidth = 2 * this.scale;
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.3)';
      ctx.stroke();
      
      // Rim light for leaf
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.bezierCurveTo(
        leafWidth * 0.6, -leafLength * 0.3,
        0, -leafLength,
        0, -leafLength
      );
      ctx.bezierCurveTo(
        -leafWidth * 0.6, -leafLength * 0.3,
        0, 0,
        0, 0
      );
      ctx.lineWidth = 1.5 * this.scale;
      ctx.stroke();

      ctx.restore();
    }
  }

  private drawEyes(ctx: CanvasRenderingContext2D, renderY: number): void {
    const eyeSize = 20 * this.scale; // Larger eyes
    const pupilSize = 11 * this.scale;
    const eyeSpacing = 24 * this.scale * this.stretchX;
    // Lowered eye position significantly
    const eyeY = renderY + 10 * this.scale * this.stretchY;

    for (const side of [1, -1]) {
      const eyeX = this.pos.x + side * eyeSpacing;

      // Sclera
      ctx.beginPath();
      ctx.ellipse(
        eyeX, eyeY,
        eyeSize * this.stretchX,
        eyeSize * this.stretchY * 1.05, // Slightly tall
        side * -0.1, // Slight tilt inward
        0, Math.PI * 2
      );
      ctx.fillStyle = 'white';
      ctx.fill();

      const lookOffset = 3 * this.scale;
      const pupilX = eyeX + Math.cos(this.facingAngle) * lookOffset;
      const pupilY = eyeY + Math.sin(this.facingAngle) * lookOffset;

      // Pupil
      ctx.beginPath();
      ctx.ellipse(
        pupilX, pupilY,
        pupilSize, pupilSize * 1.1, // Tall pupil
        0, 0, Math.PI * 2
      );
      ctx.fillStyle = 'black';
      ctx.fill();

      // Large main highlight (soft reflection)
      ctx.globalAlpha = 0.9;
      ctx.beginPath();
      ctx.ellipse(
        pupilX - pupilSize * 0.3,
        pupilY - pupilSize * 0.3,
        pupilSize * 0.4, pupilSize * 0.3,
        Math.PI / 4, 0, Math.PI * 2
      );
      ctx.fillStyle = 'white';
      ctx.fill();
      
      // Secondary smaller highlight
      ctx.globalAlpha = 0.6;
      ctx.beginPath();
      ctx.arc(
        pupilX + pupilSize * 0.4,
        pupilY + pupilSize * 0.4,
        pupilSize * 0.15,
        0, Math.PI * 2
      );
      ctx.fillStyle = 'white';
      ctx.fill();
      ctx.globalAlpha = 1.0;
    }
  }
}