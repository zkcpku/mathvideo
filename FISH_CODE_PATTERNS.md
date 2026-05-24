# Fish App - Code Patterns & Implementation Guide

## Pattern 1: State Machine with Timing

**Location:** `src/lib/fish.ts`

```typescript
// Define states
type JumpState = 'idle' | 'charging' | 'jumping' | 'landing';

// State properties
state: JumpState = 'idle';
stateTime = 0;

// Timing constants
chargeDuration = 0.12;
jumpDuration = 0.35;
landDuration = 0.08;

// Main update
resolve(mousePos: Vec2): void {
  const dt = 1 / 60;  // Delta time
  
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
}

// Each state handler
private handleCharging(mousePos: Vec2, dt: number): void {
  this.stateTime += dt;
  
  // Normalize to [0, 1]
  const t = Math.min(this.stateTime / this.chargeDuration, 1);
  
  // Animate based on t
  this.stretchX = 1 + 0.25 * t;
  this.stretchY = 1 - 0.2 * t;
  
  // Transition when complete
  if (t >= 1) {
    this.state = 'jumping';
    this.stateTime = 0;
  }
}
```

**Key Pattern:**
- Each state increments `stateTime`
- Normalize to `t ∈ [0, 1]`
- Animate linearly or with easing functions
- Transition when `t >= 1`

**For Penguin:** Modify each handler to implement penguin-specific animations.

---

## Pattern 2: Time-Based Animation (Continuous)

**Location:** `src/lib/fish.ts`

```typescript
// Idle bounce - continuous, uses global time
private handleIdle(mousePos: Vec2, dist: number, dt: number): void {
  // Using Date.now() for continuous oscillation
  const idleBounce = Math.sin(Date.now() * 0.006) * 0.04;
  this.stretchX = 1 + idleBounce;
  this.stretchY = 1 - idleBounce;
}

// Alternative: Using stateTime for continuous loop
const wigglePhase = Date.now() * 0.008;
const wipperWiggle = Math.sin(this.state === 'jumping' 
  ? this.stateTime * 20  // Fast during jump
  : this.earWiggle);      // Slow at idle
```

**Key Pattern:**
- Use `Date.now() * frequency` for continuous loops
- Or use `stateTime * frequency` within a state
- Apply sine/cosine for oscillation
- Multiply by amplitude to scale result

**For Penguin:** Add waddle animation during idle:
```typescript
const waddlePhase = Date.now() * 0.008;
const waddleAmount = Math.sin(waddlePhase) * 0.1;
this.pos.x += waddleAmount;  // Side-to-side waddle
```

---

## Pattern 3: Easing & Interpolation

### Linear Interpolation (Lerp)

```typescript
// Smooth position change from A to B
this.pos = Vec2.lerp(this.jumpStart, this.jumpTarget, t);
// Where t ∈ [0, 1]
// t=0 → jumpStart, t=1 → jumpTarget

// Lerp implementation
static lerp(a: Vec2, b: Vec2, t: number): Vec2 {
  return new Vec2(
    a.x + (b.x - a.x) * t,  // Interpolate x
    a.y + (b.y - a.y) * t   // Interpolate y
  );
}
```

### Easing Functions

```typescript
// Parabolic arc (sine wave) - used for jump height
const jumpHeight = Math.sin(t * Math.PI) * this.baseJumpHeight;
// Creates perfect parabola: 0 → max → 0

// Squash/stretch easing
const stretchPhase = t < 0.3 ? t / 0.3 : (1 - t) / 0.7;
// Compress early, expand late

// Ease-out cubic
const easeOutCubic = (t: number) => {
  const x = t - 1;
  return x * x * x + 1;  // Fast start, slow end
};

// Ease-in-out sine
const easeInOutSine = (t: number) => {
  return -(Math.cos(Math.PI * t) - 1) / 2;
};
```

**For Penguin:** Use different easing for waddle jumps:
```typescript
// Slower, bouncier jump
const t = this.stateTime / this.jumpDuration;
const bounceHeight = Math.sin(t * Math.PI * 1.5) * this.baseJumpHeight;
// Amplitude 1.5π instead of π = more bouncy
```

---

## Pattern 4: Canvas Transform Stack

**Location:** `src/lib/fish.ts` - render method

```typescript
render(ctx: CanvasRenderingContext2D): void {
  // Save current transform state
  ctx.save();
  
  // Apply transforms (order matters!)
  ctx.translate(renderX, renderY - this.jumpHeight);
  ctx.scale(this.scale * this.stretchX, this.scale * this.stretchY);
  ctx.rotate(this.rotation);  // Optional
  
  // Draw from local origin (0, 0)
  this.drawBody(ctx);      // At (0, 0)
  this.drawEyes(ctx);      // At (0, 0)
  // All drawing is in local coordinates!
  
  // Restore previous transform
  ctx.restore();
}

// Per-part transformation
private drawFlippers(ctx: CanvasRenderingContext2D): void {
  for (const side of [-1, 1]) {
    ctx.save();
    ctx.scale(side, 1);      // Flip for right flipper
    ctx.rotate(flipperWiggle);
    
    // Draw flipper at local origin
    ctx.beginPath();
    ctx.moveTo(50, -8);
    ctx.bezierCurveTo(...);
    ctx.fill();
    
    ctx.restore();
  }
}
```

**Key Pattern:**
- `ctx.save()` / `ctx.restore()` for nested transforms
- All drawing coordinates are relative to current origin
- Transforms compound: translate → scale → rotate
- Mirror/flip using `ctx.scale(-1, 1)`

**For Penguin:** Add tilt during movement:
```typescript
ctx.rotate(this.facingAngle * 0.3);  // Tilt in direction of movement
```

---

## Pattern 5: Vector Math for Direction & Distance

**Location:** `src/lib/vec2.ts` and `src/lib/fish.ts`

```typescript
// Calculate direction to target
const toMouse = mousePos.sub(this.pos);
const dist = toMouse.mag();

// Get unit direction (normalized)
const direction = toMouse.setMag(1);  // Length = 1

// Set specific distance
const jumpDist = Math.min(dist, this.baseJumpDistance);
this.jumpTarget = this.pos.add(direction.setMag(jumpDist));

// Get angle from vector
const angle = toMouse.heading();  // atan2(y, x)

// Create vector from angle
const vec = Vec2.fromAngle(angle);

// Create vector with magnitude
const vec = Vec2.fromAngle(angle).setMag(distance);
```

**Implementations:**

```typescript
// Distance and magnitude
export class Vec2 {
  mag(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  }
  
  // Normalize and scale
  setMag(m: number): Vec2 {
    const current = this.mag();
    if (current === 0) return new Vec2(m, 0);
    return this.mul(m / current);
  }
  
  // Get angle
  heading(): number {
    return Math.atan2(this.y, this.x);
  }
  
  // Create from angle
  static fromAngle(angle: number): Vec2 {
    return new Vec2(Math.cos(angle), Math.sin(angle));
  }
}
```

**For Penguin:** Use for waddle direction:
```typescript
const waddleDir = Vec2.fromAngle(Date.now() * 0.004);
this.waddleOffset = waddleDir.mul(this.waddleAmount);
```

---

## Pattern 6: Smooth Angle Following

**Location:** `src/lib/fish.ts`

```typescript
// Current angle
facingAngle = 0;

// Update facing angle
const targetAngle = Math.atan2(toMouse.y, toMouse.x);
let angleDiff = targetAngle - this.facingAngle;

// Normalize to [-π, π] (shortest path)
while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;

// Smooth interpolation (lerp factor = 0.15)
this.facingAngle += angleDiff * 0.15;
```

**Why normalize angle difference?**
- If angle goes from 350° to 10°, difference is -340°
- But actually only 20° away!
- Normalize: 20° → shortest clockwise rotation
- This prevents spinning the long way around

**For Penguin:** Use facing angle for eye gaze:
```typescript
private drawEyes(ctx: CanvasRenderingContext2D): void {
  const pupilOffsetX = Math.cos(this.facingAngle) * 2.5;
  const pupilOffsetY = Math.sin(this.facingAngle) * 2.5;
  
  // Draw pupils at offset position
  ctx.fillStyle = '#000000';
  ctx.beginPath();
  ctx.arc(-12 + pupilOffsetX, -55 + pupilOffsetY, 4, 0, Math.PI * 2);
  ctx.fill();
}
```

---

## Pattern 7: High-DPI Canvas Scaling

**Location:** `src/components/FishCanvas.tsx`

```typescript
useEffect(() => {
  const canvas = canvasRef.current;
  if (!canvas) return;

  const resize = () => {
    // Get DPI (Retina = 2, 4K = 3+)
    const dpr = window.devicePixelRatio || 1;
    dprRef.current = dpr;
    
    const width = window.innerWidth;
    const height = window.innerHeight;

    // Internal canvas size (high resolution)
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    
    // CSS size (visual size)
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;

    // Scale context to match
    const ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
  };

  resize();
  window.addEventListener('resize', resize);
  return () => window.removeEventListener('resize', resize);
}, []);
```

**Drawing with DPI:**

```typescript
const render = useCallback(() => {
  const ctx = canvas.getContext('2d');
  const dpr = dprRef.current;
  
  const width = canvas.width / dpr;
  const height = canvas.height / dpr;
  
  // Reset transform each frame
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  
  // Clear with CSS dimensions
  ctx.clearRect(0, 0, width, height);
  
  // Draw (coordinates are in CSS pixels, DPI handled by transform)
  fish.render(ctx);
}, []);
```

---

## Pattern 8: Electron IPC Communication

**Main Process (electron/main.cjs):**

```javascript
const { mainWindow, screen } = require('electron');

// Poll mouse position every 16ms
const mouseInterval = setInterval(() => {
  if (mainWindow && !mainWindow.isDestroyed()) {
    // Get global cursor position
    const point = screen.getCursorScreenPoint();
    const winBounds = mainWindow.getBounds();
    
    // Convert to window-local coordinates
    const localX = point.x - winBounds.x;
    const localY = point.y - winBounds.y;
    
    // Send via IPC
    mainWindow.webContents.send('mouse-position', {
      x: localX,
      y: localY
    });
  }
}, 16);  // 60 FPS
```

**Preload Script (electron/preload.cjs):**

```javascript
const { contextBridge, ipcRenderer } = require('electron');

// Expose safe API to renderer
contextBridge.exposeInMainWorld('electronAPI', {
  onMousePosition: (callback) => {
    ipcRenderer.on('mouse-position', (_event, pos) => {
      callback(pos);
    });
  },
});
```

**Type Definition (src/electron.d.ts):**

```typescript
declare global {
  interface Window {
    electronAPI?: {
      onMousePosition: (callback: (pos: { x: number; y: number }) => void) => void;
    };
  }
}
```

**Renderer (src/components/FishCanvas.tsx):**

```typescript
useEffect(() => {
  if (window.electronAPI) {
    // Running in Electron
    window.electronAPI.onMousePosition((pos) => {
      mousePosRef.current = new Vec2(pos.x, pos.y);
    });
  } else {
    // Running in browser - fallback
    const handleMouseMove = (e: MouseEvent) => {
      mousePosRef.current = new Vec2(e.clientX, e.clientY);
    };
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }
}, []);
```

**Key Pattern:**
- Main process: Collect data
- Send via `webContents.send(channel, data)`
- Preload: Expose callback via `contextBridge`
- Renderer: Use `window.electronAPI.onMousePosition(callback)`

---

## Pattern 9: Animation Loop Hook

**Location:** `src/hooks/useAnimationLoop.ts`

```typescript
export function useAnimationLoop(
  callback: (deltaTime: number) => void
): void {
  const callbackRef = useRef(callback);
  const lastTimeRef = useRef<number>(0);

  // Keep callback reference fresh
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Set up RAF loop
  useEffect(() => {
    let animationId: number;

    const loop = (time: number) => {
      // Calculate delta on first frame
      if (lastTimeRef.current === 0) {
        lastTimeRef.current = time;
      }
      
      const deltaTime = time - lastTimeRef.current;
      lastTimeRef.current = time;

      // Call user's render function
      callbackRef.current(deltaTime);
      
      // Schedule next frame
      animationId = requestAnimationFrame(loop);
    };

    animationId = requestAnimationFrame(loop);

    // Cleanup
    return () => {
      cancelAnimationFrame(animationId);
    };
  }, []);
}
```

**Usage:**

```typescript
const render = useCallback(() => {
  // Called ~60 times per second
  fish.resolve(mousePos);
  fish.render(ctx);
}, []);

useAnimationLoop(render);
```

---

## Pattern 10: React Refs for Mutable Values

**Location:** `src/components/FishCanvas.tsx`

```typescript
// Store references that don't need re-renders
const canvasRef = useRef<HTMLCanvasElement>(null);
const fishRef = useRef<Fish | null>(null);
const mousePosRef = useRef<Vec2>(new Vec2(0, 0));
const dprRef = useRef<number>(1);

// Access current values
const canvas = canvasRef.current;
const fish = fishRef.current;
const mousePos = mousePosRef.current;
const dpr = dprRef.current;

// Update references (no re-render)
fishRef.current = new Fish(...);
mousePosRef.current = new Vec2(x, y);

// Use in render loop
const render = useCallback(() => {
  const fish = fishRef.current;      // Current value
  const mousePos = mousePosRef.current;
  
  fish.resolve(mousePos);
  fish.render(ctx);
}, []);  // No dependencies needed!
```

**Why use Refs?**
- Don't trigger re-renders when updated
- Store mutable values
- Access current values in callbacks
- Useful for game objects, positions, state

---

## Integration Example: Complete Penguin State

```typescript
export class Penguin {
  // Position & physics
  pos: Vec2;
  scale: number;
  
  // State machine
  state: 'idle' | 'charging' | 'jumping' | 'landing' = 'idle';
  stateTime = 0;
  
  // Jump properties
  jumpStart: Vec2;
  jumpTarget: Vec2;
  jumpHeight = 0;
  
  // Animation
  stretchX = 1;
  stretchY = 1;
  facingAngle = 0;
  
  // Waddle animation (NEW FOR PENGUIN)
  waddlePhase = 0;
  
  // Timings
  chargeDuration = 0.15;
  jumpDuration = 0.4;
  landDuration = 0.08;
  idleThreshold = 0.02;
  
  // Physics
  baseJumpHeight = 60;
  baseJumpDistance = 80;
  
  resolve(mousePos: Vec2): void {
    const dt = 1 / 60;
    this.waddlePhase += dt;
    
    const toMouse = mousePos.sub(this.pos);
    const dist = toMouse.mag();
    
    // Update facing angle
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
  }
  
  private handleIdle(mousePos: Vec2, dist: number, dt: number): void {
    // Waddle animation
    const waddleAmount = Math.sin(this.waddlePhase * 4) * 2;
    this.pos.x += waddleAmount * 0.02;
    
    // Idle bounce
    const bounce = Math.sin(Date.now() * 0.006) * 0.02;
    this.stretchY = 1 - bounce;
    this.stretchX = 1 + bounce;
    
    // Decision logic (same as Fish)
    const jumpThreshold = 40 * this.scale;
    if (dist > jumpThreshold) {
      // Will transition to charging...
    }
  }
  
  render(ctx: CanvasRenderingContext2D): void {
    ctx.save();
    ctx.translate(this.pos.x, this.pos.y - this.jumpHeight);
    ctx.scale(this.scale * this.stretchX, this.scale * this.stretchY);
    
    // Draw penguin
    this.drawBody(ctx);
    this.drawBelly(ctx);
    this.drawEyes(ctx);
    this.drawBeak(ctx);
    
    ctx.restore();
  }
}
```

---

## Summary: Key Code Patterns

| Pattern | Where | Purpose |
|---------|-------|---------|
| State Machine | fish.ts resolve() | Manage animation states |
| Time-based Animation | handleIdle() | Continuous oscillations |
| Lerp | Vec2.lerp() | Smooth position transitions |
| Easing | Math.sin(t * π) | Smooth curves (not linear) |
| Canvas Transforms | fish.render() | Translate, scale, rotate |
| Vector Math | Vec2 class | Direction, distance, angles |
| Angle Interpolation | facingAngle update | Smooth rotation following |
| DPI Scaling | FishCanvas resize | Sharp rendering on all displays |
| IPC Communication | electron + preload | Cross-process data transfer |
| Animation Loop | useAnimationLoop hook | 60 FPS render callback |

---
