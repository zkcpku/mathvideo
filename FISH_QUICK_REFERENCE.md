# Quick Reference: Fish App Architecture

## 🎯 Core Components Overview

### 1. Electron Main Process (electron/main.cjs)
**Purpose:** Window management, mouse tracking, IPC

```
✓ Creates transparent, always-on-top window
✓ Spans all monitors with screen.getAllDisplays()
✓ Polls mouse position every 16ms
✓ Sends position via IPC to renderer
✓ Window settings:
  - transparent: true
  - frame: false
  - alwaysOnTop: true
  - focusable: false
  - setIgnoreMouseEvents(true) ← click-through!
```

### 2. Preload Script (electron/preload.cjs)
**Purpose:** Secure bridge for IPC communication

```javascript
contextBridge.exposeInMainWorld('electronAPI', {
  onMousePosition: (callback) => {
    ipcRenderer.on('mouse-position', (_event, pos) => callback(pos));
  },
});
```

### 3. React Renderer (src/components/FishCanvas.tsx)
**Purpose:** Canvas rendering, animation loop

```typescript
1. Setup Canvas with High-DPI Support
   - devicePixelRatio scaling
   - Internal size = window size × dpr
   - CSS size = window size

2. Setup Mouse Tracking
   - Check window.electronAPI (Electron vs Browser)
   - Use Electron IPC or fallback to mousemove

3. Animation Loop (useAnimationLoop hook)
   - requestAnimationFrame continuous loop
   - Each frame: fish.resolve() → fish.render()

4. Clear → Update → Draw
   - ctx.clearRect() full canvas
   - fish.resolve(mousePos) ← physics/state update
   - fish.render(ctx) ← draw to canvas
```

### 4. Character Class (src/lib/fish.ts)
**Purpose:** Physics, state machine, rendering

```
State Machine:
  idle → charging → jumping → landing → idle

States:
• idle: Wait for mouse > threshold, gentle bounce
• charging: Crouch animation, squash/stretch
• jumping: Arc in air, position lerp
• landing: Impact squash/bounce

Animations:
✓ Squash/stretch: stretchX, stretchY
✓ Jump height: parabolic arc (sin curve)
✓ Gaze: facing angle toward mouse
✓ Idle wiggle: ear/fin rotation
✓ Shadow: opacity fades based on jump height
```

### 5. Math Libraries

| Library | Purpose | Usage |
|---------|---------|-------|
| vec2.ts | 2D vectors | position, direction, lerp, distance |
| chain.ts | IK chain | skeletal animation (optional) |
| spline.ts | Catmull-Rom | smooth curves (optional) |

---

## 📊 Data Flow

```
Mouse Position Flow:
  screen.getCursorScreenPoint()
    ↓ (convert to window-local)
  mainWindow.webContents.send('mouse-position')
    ↓ (IPC)
  preload.cjs receives event
    ↓ (contextBridge)
  window.electronAPI.onMousePosition(callback)
    ↓ (in renderer)
  FishCanvas: mousePosRef.current = pos
    ↓ (used by render loop)
  fish.resolve(mousePos)

Rendering Loop:
  requestAnimationFrame(loop)
    ↓
  canvas.clearRect()
    ↓
  fish.resolve(mousePos) ← updates position, state, animations
    ↓
  fish.render(ctx) ← draws all body parts (back-to-front)
```

---

## 🔧 Key Configuration

### Window Setup
```javascript
// Make window transparent and overlay
const mainWindow = new BrowserWindow({
  transparent: true,
  frame: false,
  alwaysOnTop: true,
  focusable: false,
  backgroundColor: '#00000000',
  ...
});

// Make it click-through
mainWindow.setIgnoreMouseEvents(true);

// Highest z-order
mainWindow.setAlwaysOnTop(true, 'floating', 1);

// Visible on all workspaces (macOS/Linux)
mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
```

### Canvas High-DPI
```typescript
const dpr = window.devicePixelRatio;
canvas.width = window.innerWidth * dpr;   // Internal resolution
canvas.style.width = `${window.innerWidth}px`;  // CSS size
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);  // Scale context
```

### Rendering Code (Core Loop)
```typescript
const render = useCallback(() => {
  // Update physics
  fish.resolve(mousePosRef.current);  // ← uses mouse position!
  
  // Render
  ctx.clearRect(0, 0, width, height);
  fish.render(ctx);
}, []);

useAnimationLoop(render);  // Called 60× per second
```

---

## 🎨 Character Drawing

### Render Method Structure
```typescript
render(ctx: CanvasRenderingContext2D) {
  ctx.save();
  ctx.translate(this.pos.x, this.pos.y - this.jumpHeight);
  ctx.scale(this.scale * this.stretchX, this.scale * this.stretchY);
  
  // Draw order (back to front):
  this.drawFeet(ctx);        // Layer 1
  this.drawFlippers(ctx);    // Layer 2
  this.drawBody(ctx);        // Layer 3
  this.drawBelly(ctx);       // Layer 4
  this.drawScarf(ctx);       // Layer 5
  this.drawEyes(ctx);        // Layer 6
  this.drawBeak(ctx);        // Layer 7
  this.drawStar(ctx);        // Layer 8
  
  ctx.restore();
}
```

### Animation Techniques
```typescript
// 1. Time-based animation
const idleBounce = Math.sin(Date.now() * 0.006) * 0.04;

// 2. State-time animation (0 to 1)
const t = this.stateTime / this.jumpDuration;
const jumpHeight = Math.sin(t * Math.PI) * this.baseJumpHeight;

// 3. Smooth interpolation (lerp)
this.pos = Vec2.lerp(this.jumpStart, this.jumpTarget, t);

// 4. Angle following
const targetAngle = Math.atan2(toMouse.y, toMouse.x);
this.facingAngle += angleDiff * 0.15;  // Smooth lerp
```

---

## 🚀 Build & Run

### Development
```bash
pnpm electron:dev
# Starts: Vite dev server + Electron app
# Loads: http://localhost:5173
```

### Production Build
```bash
pnpm electron:build
# Output: Electron installer for your OS
```

### Scripts
```json
{
  "scripts": {
    "dev": "vite",                                    // Just frontend
    "build": "tsc && vite build",                    // Build frontend
    "electron:dev": "concurrently \"vite\" \"wait-on http://localhost:5173 && NODE_ENV=development electron .\"",
    "electron:build": "pnpm build && electron-builder",
    "electron:start": "electron ."
  }
}
```

---

## 📝 Penguin Port Checklist

- [ ] Copy project as template
- [ ] Rename Fish → Penguin class
- [ ] Redraw character (update draw methods)
- [ ] Adjust physics (jumpHeight, jumpDistance)
- [ ] Adjust timings (chargeDuration, jumpDuration)
- [ ] Update colors (black/white for penguin)
- [ ] Test in browser (remove Electron)
- [ ] Test in Electron dev
- [ ] Add sound effects (optional)
- [ ] Create build/installer
- [ ] Package for distribution

---

## 🐛 Debugging Tips

1. **Transparent window not working?**
   - Check: `backgroundColor: '#00000000'` AND `transparent: true`
   - Verify: CSS background is also transparent

2. **Mouse position wrong?**
   - Main process sends global coordinates
   - Must convert: `localX = globalX - window.x`
   - Check: No offset in canvas CSS positioning

3. **Animation choppy?**
   - Verify: useAnimationLoop actually called
   - Check: requestAnimationFrame is running
   - Debug: Log frame count with counter

4. **Blurry on Retina?**
   - Must scale canvas.width/height by devicePixelRatio
   - BUT keep CSS width/height at window size

5. **IPC not receiving mouse?**
   - Check: Main process setInterval is running
   - Verify: Preload script path correct
   - Ensure: contextIsolation: true
   - Look: For errors in DevTools console

---

## 💡 Key Concepts

### State Machine Timing
```typescript
// Each state manages time progression
stateTime += dt;
const t = Math.min(stateTime / stateDuration, 1);  // 0 to 1

// Use t for easing
const easedValue = Math.sin(t * Math.PI);  // 0 → 1 → 0 (parabolic)
```

### Lerping Between Values
```typescript
// Smooth transition from A to B over time
const value = Vec2.lerp(startPos, endPos, t);
// t=0 → startPos, t=1 → endPos, t=0.5 → midpoint
```

### Drawing Transforms
```typescript
ctx.save();                     // Save state
ctx.translate(x, y);           // Move origin
ctx.scale(scaleX, scaleY);     // Scale (squash/stretch)
ctx.rotate(angle);             // Rotate

// Draw at origin (0, 0)
ctx.fillRect(-10, -10, 20, 20);

ctx.restore();                  // Restore state
```

### Angle Math
```typescript
// Get angle from vector
const angle = Math.atan2(dy, dx);

// Get unit vector from angle
const vec = new Vec2(Math.cos(angle), Math.sin(angle));

// Normalize angle difference to [-π, π]
let diff = targetAngle - currentAngle;
while (diff > Math.PI) diff -= 2 * Math.PI;
while (diff < -Math.PI) diff += 2 * Math.PI;
```

---

## 📚 File Reference

| File | Lines | Purpose |
|------|-------|---------|
| electron/main.cjs | 98 | Window, mouse tracking, IPC |
| electron/preload.cjs | 8 | Security bridge |
| src/App.tsx | 7 | Root component |
| src/components/FishCanvas.tsx | 89 | Canvas & render loop |
| src/lib/fish.ts | 395 | Character class |
| src/lib/vec2.ts | 51 | 2D vector math |
| src/lib/chain.ts | 81 | IK chain (optional) |
| src/lib/spline.ts | 44 | Catmull-Rom (optional) |
| src/hooks/useAnimationLoop.ts | 32 | Animation loop hook |
| vite.config.ts | 10 | Vite config |
| index.html | 14 | HTML template |

**Total: ~729 lines of source code**

---

## 🎓 Learning Path

1. **Understand IPC flow**
   - How main process sends mouse position
   - How preload script receives it
   - How renderer uses it

2. **Understand canvas rendering**
   - High-DPI scaling
   - Transform stack (translate, scale, rotate)
   - Drawing order

3. **Understand state machine**
   - 4 states with timing
   - Transitions between states
   - Time-parameterized animations

4. **Understand animation math**
   - Linear interpolation (lerp)
   - Easing functions (sin, ease-out, etc.)
   - Angle interpolation

5. **Understand physics**
   - Jump trajectory (parabolic)
   - Distance constraints
   - Squash/stretch

---
