# Electron Desktop Pet App Architecture Guide
## Fish Animation - Complete Analysis for QQ Penguin Replication

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Electron Main Process](#electron-main-process)
4. [Preload Script](#preload-script)
5. [Renderer Process](#renderer-process)
6. [Animation System](#animation-system)
7. [Math Libraries](#math-libraries)
8. [Build Configuration](#build-configuration)
9. [Replication Guide for QQ Penguin](#replication-guide-for-qq-penguin)

---

## Project Overview

**Fish Animation** is a transparent, always-on-top Electron desktop pet that follows your mouse cursor. It demonstrates:
- Multi-display support with transparent overlay windows
- Smooth animation loop with requestAnimationFrame
- Canvas-based 2D character rendering
- Physics-based movement with state machines
- React + TypeScript for UI logic
- Vite for fast build/dev

### Tech Stack
- **Electron** 40.1.0 - Desktop app framework
- **React** 19.2.4 - UI component logic
- **Vite** 7.2.4 - Dev server & bundler
- **TypeScript** 5.9.3 - Type safety
- **Canvas 2D API** - Character rendering

### Key Features
✅ Transparent, always-on-top window (no taskbar)
✅ Multi-monitor support (spans all displays)
✅ Mouse-following behavior
✅ Jumping animation toward cursor
✅ Idle bouncing animation
✅ Landing/charging states
✅ Scaling and stretch animations
✅ Custom-drawn character (penguin-like)

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Electron Main Process                     │
│  (electron/main.cjs)                                         │
│  • Creates transparent BrowserWindow                         │
│  • Sets up screen bounds (multi-display)                     │
│  • Broadcasts mouse position every 16ms                      │
│  • Configures always-on-top, frameless, non-focusable        │
└──────────────────────────┬──────────────────────────────────┘
                           │ IPC: 'mouse-position'
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   Preload Script                             │
│  (electron/preload.cjs)                                      │
│  • contextBridge.exposeInMainWorld()                         │
│  • Creates window.electronAPI.onMousePosition()              │
│  • Context isolation enabled                                 │
└──────────────────────────┬──────────────────────────────────┘
                           │ ipcRenderer.on()
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                  React Renderer Process                      │
│  (index.html → src/main.tsx → src/App.tsx)                   │
│                                                              │
│  ┌─ FishCanvas Component ─────────────────────────────────┐ │
│  │ • Canvas setup with DPR scaling                        │ │
│  │ • useAnimationLoop hook (requestAnimationFrame)        │ │
│  │ • Mouse position tracking (Electron or browser)        │ │
│  │ • Render loop: clear → fish.resolve() → fish.render() │ │
│  └───────────────────────────────────────────────────────┘ │
│           │                                    │             │
│           ↓ uses                               ↓ renders     │
│                                                              │
│  ┌─ Fish Class ─────────────┐    ┌─ Canvas 2D Context ──┐ │
│  │ • State machine          │    │ • drawBody()         │ │
│  │ • Physics (jump, fall)   │    │ • drawEyes()         │ │
│  │ • Animation timing       │    │ • drawScarf()        │ │
│  │ • Gaze direction         │    │ • drawBeak()         │ │
│  └──────────────────────────┘    │ • drawStar()         │ │
│           │                       │ • drawShadow()       │ │
│           ↓ uses                  └──────────────────────┘ │
│                                                              │
│  ┌─ Math Libraries ──────────────────────────────────────┐ │
│  │ • Vec2: 2D vector math (add, sub, lerp, mag, etc)    │ │
│  │ • Chain: IK chain for skeletal animation             │ │
│  │ • Spline: Catmull-Rom curve interpolation            │ │
│  └───────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

                           Vite Dev Server
                      (Hot reload on dev)
```

---

## Electron Main Process

### File: `electron/main.cjs`

```javascript
const { app, BrowserWindow, screen, globalShortcut } = require('electron');
const path = require('path');

let mainWindow;
let mouseInterval;

function createWindow() {
  // 1. MULTI-DISPLAY SUPPORT
  // Calculate total bounds across all displays
  const displays = screen.getAllDisplays();
  
  let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
  for (const display of displays) {
    const { x, y, width: w, height: h } = display.bounds;
    minX = Math.min(minX, x);
    minY = Math.min(minY, y);
    maxX = Math.max(maxX, x + w);
    maxY = Math.max(maxY, y + h);
  }
  
  const totalWidth = maxX - minX;
  const totalHeight = maxY - minY;

  // 2. WINDOW CONFIGURATION FOR TRANSPARENT OVERLAY
  mainWindow = new BrowserWindow({
    x: minX,
    y: minY,
    width: totalWidth,
    height: totalHeight,
    transparent: true,        // ← Allows transparent pixels
    frame: false,              // ← No window chrome/title bar
    alwaysOnTop: true,         // ← Always visible above other windows
    skipTaskbar: true,         // ← Don't show in taskbar
    hasShadow: false,          // ← No window shadow
    resizable: false,          // ← User can't resize
    movable: false,            // ← User can't move
    minimizable: false,        // ← No minimize button
    maximizable: false,        // ← No maximize button
    closable: true,            // ← Can close via Cmd+Q or other means
    focusable: false,          // ← Window doesn't steal focus
    backgroundColor: '#00000000', // ← Fully transparent RGBA
    webPreferences: {
      nodeIntegration: false,  // ← Security: No Node access in renderer
      contextIsolation: true,  // ← Security: Preload script isolated
      preload: path.join(__dirname, 'preload.cjs'),
    },
  });

  // 3. MAKE WINDOW CLICK-THROUGH (ignores mouse events)
  mainWindow.setIgnoreMouseEvents(true);
  
  // 4. VISIBLE ON ALL WORKSPACES (macOS/Linux)
  mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  
  // 5. ALWAYS ON TOP WITH HIGHEST Z-ORDER
  mainWindow.setAlwaysOnTop(true, 'floating', 1);

  // 6. MOUSE TRACKING LOOP - Broadcast cursor position to renderer
  // Updates every 16ms (~60 FPS)
  mouseInterval = setInterval(() => {
    if (mainWindow && !mainWindow.isDestroyed()) {
      const point = screen.getCursorScreenPoint();  // Global mouse position
      const winBounds = mainWindow.getBounds();
      
      // Convert global coordinates to window-local coordinates
      const localX = point.x - winBounds.x;
      const localY = point.y - winBounds.y;
      
      // Send to renderer process via IPC
      mainWindow.webContents.send('mouse-position', { 
        x: localX,
        y: localY
      });
    }
  }, 16);

  // 7. LOAD APP - Dev or Production
  const isDev = process.env.NODE_ENV === 'development';
  
  if (isDev) {
    mainWindow.loadURL('http://localhost:5173');  // Vite dev server
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
  }

  // 8. CLEANUP ON WINDOW CLOSE
  mainWindow.on('closed', () => {
    if (mouseInterval) clearInterval(mouseInterval);
    mainWindow = null;
  });
}

app.whenReady().then(() => {
  createWindow();
  // Removed Escape shortcut to prevent quitting
});

app.on('window-all-closed', () => {
  app.quit();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

app.on('activate', () => {
  if (mainWindow === null) {
    createWindow();
  }
});
```

### Key Concepts for Main Process:
1. **Transparent Window**: `transparent: true` + `backgroundColor: '#00000000'`
2. **Always-on-top**: `alwaysOnTop: true` + `setAlwaysOnTop(true, 'floating', 1)`
3. **Click-through**: `setIgnoreMouseEvents(true)` - mouse events pass through
4. **Multi-display**: Calculate bounds of all displays, create window that spans all
5. **Mouse Tracking**: `screen.getCursorScreenPoint()` polled every 16ms
6. **IPC Communication**: `mainWindow.webContents.send('mouse-position', data)`

---

## Preload Script

### File: `electron/preload.cjs`

```javascript
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  onMousePosition: (callback) => {
    ipcRenderer.on('mouse-position', (_event, pos) => callback(pos));
  },
});
```

### Type Definition

### File: `src/electron.d.ts`

```typescript
export {};

declare global {
  interface Window {
    electronAPI?: {
      onMousePosition: (callback: (pos: { x: number; y: number }) => void) => void;
    };
  }
}
```

### Security Pattern:
- **Context Bridge**: Safe bridge between isolated preload script and renderer
- **ipcRenderer.on()**: Listen for 'mouse-position' events from main
- **No Node access**: Renderer can only use exposed APIs
- **Fallback**: If not in Electron (browser dev), uses native mousemove event

---

## Renderer Process

### File: `src/App.tsx`

```typescript
import { FishCanvas } from './components/FishCanvas'

function App() {
  return <FishCanvas />
}

export default App
```

Very simple - just renders the canvas component.

### File: `src/components/FishCanvas.tsx`

This is the core rendering loop:

```typescript
import { useRef, useEffect, useCallback } from 'react';
import { Fish } from '../lib/fish';
import { Vec2 } from '../lib/vec2';
import { useAnimationLoop } from '../hooks/useAnimationLoop';

export function FishCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fishRef = useRef<Fish | null>(null);
  const mousePosRef = useRef<Vec2>(new Vec2(0, 0));
  const dprRef = useRef<number>(1);

  // SETUP: Initialize canvas, handle resizing
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      // Device pixel ratio for high-DPI displays (Retina, 4K, etc)
      const dpr = window.devicePixelRatio || 1;
      dprRef.current = dpr;
      
      const width = window.innerWidth;
      const height = window.innerHeight;

      // Set internal canvas resolution (higher for DPR)
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      
      // But CSS size stays at window size
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      // Scale 2D context to match DPR
      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }

      // Create fish at center, scale 0.7
      if (!fishRef.current) {
        fishRef.current = new Fish(new Vec2(width / 2, height / 2), 0.7);
      }
    };

    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  // SETUP: Listen for mouse position updates
  useEffect(() => {
    if (window.electronAPI) {
      // Running in Electron - use IPC
      window.electronAPI.onMousePosition((pos) => {
        mousePosRef.current = new Vec2(pos.x, pos.y);
      });
    } else {
      // Running in browser - use native mousemove
      const handleMouseMove = (e: MouseEvent) => {
        mousePosRef.current = new Vec2(e.clientX, e.clientY);
      };
      window.addEventListener('mousemove', handleMouseMove);
      return () => window.removeEventListener('mousemove', handleMouseMove);
    }
  }, []);

  // RENDER LOOP: Clear canvas, update fish, render
  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const fish = fishRef.current;
    if (!canvas || !fish) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = dprRef.current;
    const width = canvas.width / dpr;
    const height = canvas.height / dpr;

    // Reset transform and clear canvas
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);

    // UPDATE: Resolve fish physics/animation for this frame
    fish.resolve(mousePosRef.current);
    
    // RENDER: Draw fish to canvas
    fish.render(ctx);
  }, []);

  // Use custom animation loop hook
  useAnimationLoop(render);

  // Return full-screen canvas
  return (
    <canvas
      ref={canvasRef}
      style={{
        display: 'block',
        position: 'fixed',
        top: 0,
        left: 0,
      }}
    />
  );
}
```

### Key Rendering Concepts:
1. **High-DPI Support**: `devicePixelRatio` scaling for Retina/4K displays
2. **Dual coordinates**: Internal canvas coords (DPR-scaled) vs CSS coords
3. **requestAnimationFrame**: Via custom `useAnimationLoop` hook
4. **Electron Detection**: Check `window.electronAPI` to use IPC or fallback
5. **Update-Render pattern**: `fish.resolve()` then `fish.render()`

### File: `src/hooks/useAnimationLoop.ts`

```typescript
import { useEffect, useRef } from 'react';

export function useAnimationLoop(callback: (deltaTime: number) => void): void {
  const callbackRef = useRef(callback);
  const lastTimeRef = useRef<number>(0);

  // Keep callback reference fresh
  useEffect(() => {
    callbackRef.current = callback;
  }, [callback]);

  // Set up animation loop
  useEffect(() => {
    let animationId: number;

    const loop = (time: number) => {
      // Calculate delta time on first frame
      if (lastTimeRef.current === 0) {
        lastTimeRef.current = time;
      }
      const deltaTime = time - lastTimeRef.current;
      lastTimeRef.current = time;

      // Call render function with delta
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

### File: `index.html`

```html
<!doctype html>
<html lang="en" style="background: transparent;">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Fish Animation</title>
  </head>
  <body style="background: transparent;">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

Key: `style="background: transparent"` on both `<html>` and `<body>`.

### File: `src/index.css`

```css
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: transparent;
}

#root {
  width: 100%;
  height: 100%;
  background: transparent;
}
```

---

## Animation System

### File: `src/lib/fish.ts` - The Character Controller

The `Fish` class is the core of the animation system. It:
- Manages state machine (idle → charging → jumping → landing)
- Handles physics (jumping toward mouse, falling)
- Calculates animations (squash/stretch, rotation, etc.)
- Renders the character using Canvas 2D API

```typescript
import { Vec2 } from './vec2';

type JumpState = 'idle' | 'charging' | 'jumping' | 'landing';

export class Fish {
  // Position and scale
  pos: Vec2;
  scale: number;

  // State machine
  state: JumpState = 'idle';
  stateTime = 0;

  // Jump physics
  jumpStart: Vec2 = new Vec2(0, 0);
  jumpTarget: Vec2 = new Vec2(0, 0);
  jumpHeight = 0;

  // Animation properties
  stretchX = 1;     // Horizontal scale for squash/stretch
  stretchY = 1;     // Vertical scale for squash/stretch
  facingAngle = 0;  // Direction character faces
  earWiggle = 0;    // Idle animation parameter

  // Timing parameters (in seconds)
  chargeDuration = 0.12;   // Crouch before jump
  jumpDuration = 0.35;     // Time in air
  landDuration = 0.08;     // Landing squash
  idleTime = 0;            // Time in idle state
  idleThreshold = 0.02;    // Delay before jumping to mouse

  // Physics
  baseJumpHeight = 70;
  baseJumpDistance = 100;

  constructor(origin: Vec2, scale: number = 1.0) {
    this.scale = scale;
    this.pos = origin.copy();
    this.baseJumpHeight *= scale;
    this.baseJumpDistance *= scale;
  }

  // MAIN UPDATE FUNCTION
  resolve(mousePos: Vec2): void {
    const dt = 1 / 60;  // Assume 60 FPS
    const toMouse = mousePos.sub(this.pos);
    const dist = toMouse.mag();

    // GAZE: Always look toward mouse if > 5 pixels away
    if (dist > 5) {
      const targetAngle = Math.atan2(toMouse.y, toMouse.x);
      let angleDiff = targetAngle - this.facingAngle;
      
      // Normalize angle difference to [-PI, PI]
      while (angleDiff > Math.PI) angleDiff -= Math.PI * 2;
      while (angleDiff < -Math.PI) angleDiff += Math.PI * 2;
      
      // Smoothly interpolate facing angle
      this.facingAngle += angleDiff * 0.15;
    }

    // STATE MACHINE
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

    // Continuous idle animation (ear/fin wiggle)
    this.earWiggle += 0.12;
  }

  // STATE: IDLE - Waiting or gently bouncing
  private handleIdle(mousePos: Vec2, dist: number, dt: number): void {
    const jumpThreshold = 40 * this.scale;
    
    if (dist > jumpThreshold) {
      // Mouse far away, accumulate idle time
      this.idleTime += dt;
      
      if (this.idleTime > this.idleThreshold) {
        // Trigger jump after delay
        this.state = 'charging';
        this.stateTime = 0;
        this.jumpStart = this.pos.copy();

        // Calculate target
        const direction = mousePos.sub(this.pos);
        const jumpDist = Math.min(dist, this.baseJumpDistance);
        this.jumpTarget = this.pos.add(direction.setMag(jumpDist));
      }
    } else {
      // Mouse close, reset idle timer
      this.idleTime = 0;
    }

    // IDLE ANIMATION: Gentle vertical bounce
    const idleBounce = Math.sin(Date.now() * 0.006) * 0.04;
    this.stretchX = 1 + idleBounce;
    this.stretchY = 1 - idleBounce;
    this.jumpHeight = 0;
  }

  // STATE: CHARGING - Crouch before jump
  private handleCharging(mousePos: Vec2, dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.chargeDuration, 1);

    // SQUASH ANIMATION: Compress before jump
    this.stretchX = 1 + 0.25 * t;  // Get wider
    this.stretchY = 1 - 0.2 * t;   // Get shorter

    // Update target in case mouse moved
    const direction = mousePos.sub(this.pos);
    const dist = direction.mag();
    const jumpDist = Math.min(dist, this.baseJumpDistance);
    this.jumpTarget = this.pos.add(direction.setMag(jumpDist));

    // Charge complete?
    if (t >= 1) {
      this.state = 'jumping';
      this.stateTime = 0;
      this.jumpStart = this.pos.copy();
    }
  }

  // STATE: JUMPING - In the air
  private handleJumping(dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.jumpDuration, 1);

    // POSITION: Lerp from start to target
    this.pos = Vec2.lerp(this.jumpStart, this.jumpTarget, t);

    // HEIGHT: Arc (sine wave)
    this.jumpHeight = Math.sin(t * Math.PI) * this.baseJumpHeight;

    // STRETCH: Compress during jump
    const stretchPhase = t < 0.3 ? t / 0.3 : (1 - t) / 0.7;
    this.stretchY = 1 + stretchPhase * 0.15;  // Stretch vertically
    this.stretchX = 1 - stretchPhase * 0.1;   // Compress horizontally

    // Jump complete?
    if (t >= 1) {
      this.state = 'landing';
      this.stateTime = 0;
      this.jumpHeight = 0;
    }
  }

  // STATE: LANDING - Impact squash
  private handleLanding(dt: number): void {
    this.stateTime += dt;
    const t = Math.min(this.stateTime / this.landDuration, 1);

    // SQUASH: Compress on landing
    const squash = Math.sin(t * Math.PI) * 0.2;
    this.stretchX = 1 + squash;   // Get wider
    this.stretchY = 1 - squash;   // Get shorter
    this.jumpHeight = 0;

    // Landing complete?
    if (t >= 1) {
      this.state = 'idle';
      this.stateTime = 0;
      this.idleTime = 0;
    }
  }

  // RENDERING
  render(ctx: CanvasRenderingContext2D): void {
    ctx.save();

    const renderX = this.pos.x;
    const renderY = this.pos.y - this.jumpHeight;

    // Shadow only during jump
    if (this.jumpHeight > 5) {
      this.drawShadow(ctx);
    }

    ctx.save();
    ctx.translate(renderX, renderY);
    ctx.scale(this.scale * this.stretchX, this.scale * this.stretchY);

    // Draw order matters! Back to front:
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

    // Flipper wiggle: faster during jump, slower at idle
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
    // Gradient for 3D effect
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
    // Radial gradient for rounded appearance
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
```

---

## Math Libraries

### File: `src/lib/vec2.ts` - 2D Vector Math

```typescript
export class Vec2 {
  constructor(
    public readonly x: number,
    public readonly y: number
  ) {}

  // Create a copy
  copy(): Vec2 {
    return new Vec2(this.x, this.y);
  }

  // Vector addition: A + B
  add(other: Vec2): Vec2 {
    return new Vec2(this.x + other.x, this.y + other.y);
  }

  // Vector subtraction: A - B
  sub(other: Vec2): Vec2 {
    return new Vec2(this.x - other.x, this.y - other.y);
  }

  // Scalar multiplication: V * s
  mul(scalar: number): Vec2 {
    return new Vec2(this.x * scalar, this.y * scalar);
  }

  // Vector magnitude (length): |V|
  mag(): number {
    return Math.sqrt(this.x * this.x + this.y * this.y);
  }

  // Set magnitude to m (normalize + scale)
  // Used to set direction and distance
  setMag(m: number): Vec2 {
    const current = this.mag();
    if (current === 0) {
      return new Vec2(m, 0);
    }
    return this.mul(m / current);
  }

  // Angle from vector (atan2)
  heading(): number {
    return Math.atan2(this.y, this.x);
  }

  // Create unit vector from angle
  static fromAngle(angle: number): Vec2 {
    return new Vec2(Math.cos(angle), Math.sin(angle));
  }

  // Linear interpolation: A + (B - A) * t
  // t=0 → A, t=1 → B, t=0.5 → midpoint
  static lerp(a: Vec2, b: Vec2, t: number): Vec2 {
    return new Vec2(a.x + (b.x - a.x) * t, a.y + (b.y - a.y) * t);
  }

  // Distance between two points
  static dist(a: Vec2, b: Vec2): number {
    return a.sub(b).mag();
  }
}
```

**Used for:**
- Mouse position tracking
- Jump trajectory calculations
- Gaze direction (via `heading()`)
- Smooth interpolation between positions

### File: `src/lib/chain.ts` - Inverse Kinematics Chain

```typescript
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

    // Create chain of joints
    for (let i = 1; i < jointCount; i++) {
      this.joints.push(this.joints[i - 1].add(new Vec2(0, linkSize)));
      this.angles.push(0.0);
    }
  }

  // Forward kinematics solve
  // Move first joint to pos, propagate constraints down chain
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
```

**Use case:** Could be used for tail animation (not currently used in Fish, but available for extension).

### File: `src/lib/spline.ts` - Catmull-Rom Curve Interpolation

```typescript
export type Point = [number, number];

export function catmullRomSpline(
  points: Point[],
  numSegments: number = 10
): Point[] {
  if (points.length < 4) {
    return points;
  }

  const result: Point[] = [];

  // For each segment between points[i] and points[i+1]
  for (let i = 1; i < points.length - 2; i++) {
    const p0 = points[i - 1];
    const p1 = points[i];
    const p2 = points[i + 1];
    const p3 = points[i + 2];

    // Subdivide segment into numSegments smaller segments
    for (let j = 0; j < numSegments; j++) {
      const t = j / numSegments;
      const t2 = t * t;
      const t3 = t2 * t;

      // Catmull-Rom formula (parameterized cubic curve)
      const x =
        0.5 *
        (2 * p1[0] +
          (-p0[0] + p2[0]) * t +
          (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
          (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3);

      const y =
        0.5 *
        (2 * p1[1] +
          (-p0[1] + p2[1]) * t +
          (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
          (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3);

      result.push([x, y]);
    }
  }

  return result;
}
```

**Use case:** Could be used for smooth tail or body curves (not currently in Fish, but available for extension).

---

## Build Configuration

### File: `vite.config.ts`

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: true,
  },
})
```

### File: `tsconfig.json`

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "types": ["vite/client"],
    "skipLibCheck": true,

    /* Bundler mode */
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "verbatimModuleSyntax": true,
    "moduleDetection": "force",
    "noEmit": true,

    /* Linting */
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,

    /* React */
    "jsx": "react-jsx"
  },
  "include": ["src"]
}
```

### File: `package.json`

```json
{
  "name": "fish_anim_ts",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "main": "electron/main.cjs",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "electron:dev": "concurrently \"vite\" \"wait-on http://localhost:5173 && NODE_ENV=development electron .\"",
    "electron:build": "pnpm build && electron-builder",
    "electron:start": "electron ."
  },
  "build": {
    "appId": "com.fish.animation",
    "productName": "Fish Animation",
    "mac": {
      "category": "public.app-category.utilities",
      "target": "dmg"
    },
    "files": [
      "dist/**/*",
      "electron/**/*"
    ]
  },
  "devDependencies": {
    "@types/react": "^19.2.10",
    "@types/react-dom": "^19.2.3",
    "@vitejs/plugin-react": "^5.1.3",
    "concurrently": "^9.2.1",
    "electron": "^40.1.0",
    "electron-builder": "^26.7.0",
    "typescript": "~5.9.3",
    "vite": "^7.2.4",
    "wait-on": "^9.0.3"
  },
  "dependencies": {
    "react": "^19.2.4",
    "react-dom": "^19.2.4"
  }
}
```

---

## Replication Guide for QQ Penguin

### Step 1: Project Setup

```bash
# Create new project from this template
git clone <fish_anim_ts_repo> penguin_pet
cd penguin_pet
pnpm install
```

### Step 2: Change Character Design

**Modify `src/lib/fish.ts`:**
- Rename `Fish` class to `Penguin`
- Update all `draw*()` methods to draw QQ penguin shape
- Adjust `baseJumpHeight` and `baseJumpDistance` for penguin physics
- Modify colors/styles (black/white instead of current colors)

**Key drawing methods to update:**
```typescript
// Example: Draw penguin head instead of fish
private drawHead(ctx: CanvasRenderingContext2D): void {
  // QQ penguin head: circle with eyes
  ctx.fillStyle = '#000000';
  ctx.beginPath();
  ctx.arc(0, -50, 35, 0, Math.PI * 2);
  ctx.fill();
  
  // White belly area
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.ellipse(0, -40, 25, 30, 0, 0, Math.PI * 2);
  ctx.fill();
  
  // Eyes
  ctx.fillStyle = '#ffffff';
  ctx.beginPath();
  ctx.arc(-12, -55, 8, 0, Math.PI * 2);
  ctx.fill();
  ctx.beginPath();
  ctx.arc(12, -55, 8, 0, Math.PI * 2);
  ctx.fill();
  
  // Pupils
  ctx.fillStyle = '#000000';
  const pupilOffsetX = Math.cos(this.facingAngle) * 3;
  const pupilOffsetY = Math.sin(this.facingAngle) * 3;
  
  ctx.beginPath();
  ctx.arc(-12 + pupilOffsetX, -55 + pupilOffsetY, 4, 0, Math.PI * 2);
  ctx.fill();
  
  ctx.beginPath();
  ctx.arc(12 + pupilOffsetX, -55 + pupilOffsetY, 4, 0, Math.PI * 2);
  ctx.fill();
}
```

### Step 3: Adjust Physics

**In `src/lib/fish.ts` (now `penguin.ts`), modify the constructor:**

```typescript
constructor(origin: Vec2, scale: number = 1.0) {
  this.scale = scale;
  this.pos = origin.copy();
  
  // Penguin has different jump physics
  this.baseJumpHeight = 60 * scale;     // Shorter jumps (penguins waddle)
  this.baseJumpDistance = 80 * scale;   // Shorter hops
  
  this.chargeDuration = 0.15;           // Longer charge animation
  this.jumpDuration = 0.4;              // Slower jump
}
```

### Step 4: Update State Machine Animations

**Modify idle, charging, jumping, landing states for penguin personality:**

```typescript
// Waddle during idle instead of smooth bounce
private handleIdle(mousePos: Vec2, dist: number, dt: number): void {
  // ... existing logic ...
  
  // WADDLE: Side-to-side movement
  const waddlePhase = Date.now() * 0.008;
  const waddleX = Math.sin(waddlePhase) * 3; // Small side-to-side
  this.stretchX = 1 + waddleX * 0.02;
  this.stretchY = 1 - Math.abs(waddleX) * 0.01;
}
```

### Step 5: Update Window Appearance

**In `electron/main.cjs`, adjust for penguin size:**

```typescript
mainWindow = new BrowserWindow({
  x: minX,
  y: minY,
  width: totalWidth,
  height: totalHeight,
  // ... keep all the transparent settings the same ...
});

// If penguin is smaller, could limit window size:
// width: Math.min(500, totalWidth),
// height: Math.min(500, totalHeight),
```

### Step 6: Add Sound Effects (Optional Enhancement)

```typescript
// In src/lib/penguin.ts
private playSound(soundType: 'jump' | 'land' | 'idle') {
  const audio = new Audio(`/sounds/${soundType}.mp3`);
  audio.volume = 0.3;
  audio.play().catch(() => {});
}

// Call in state transitions:
private handleCharging(mousePos: Vec2, dt: number): void {
  // ... existing code ...
  if (t >= 1) {
    this.playSound('jump');
    this.state = 'jumping';
    // ...
  }
}
```

### Step 7: Add Right-Click Menu (Optional)

**In `electron/main.cjs`:**

```typescript
const { Menu } = require('electron');

const contextMenu = Menu.buildFromTemplate([
  { label: 'Quit', click: () => app.quit() },
  { label: 'Hide', click: () => mainWindow.hide() },
]);

mainWindow.webContents.on('context-menu', () => {
  contextMenu.popup();
});
```

### Step 8: Build & Package

```bash
# Development
pnpm electron:dev

# Build for distribution
pnpm electron:build

# Output: dist/Penguin-1.0.0.dmg (macOS)
```

---

## Data Flow Diagram

```
Main Process                  Renderer Process
═════════════════════════════════════════════════════════════

┌──────────────────────────┐
│ Electron Main            │
│ • setInterval(16ms)      │
│ • screen.getCursor...()  │
└──────────┬───────────────┘
           │
           │ IPC: 'mouse-position'
           │ {x, y}
           ↓
┌──────────────────────────────────────┐
│ Preload Script (contextBridge)       │
│ • Receives IPC event                 │
│ • Calls callback in renderer         │
└──────────┬───────────────────────────┘
           │
           ↓
┌──────────────────────────────────────┐
│ FishCanvas Component                 │
│ • mousePosRef ← {x, y}               │
└──────────┬───────────────────────────┘
           │
           │ requestAnimationFrame
           ↓
┌──────────────────────────────────────┐
│ render() callback                    │
│ 1. fish.resolve(mousePosRef)         │
│    • Updates state machine           │
│    • Calculates animations           │
│ 2. fish.render(ctx)                  │
│    • Draws to canvas                 │
└──────────────────────────────────────┘
```

---

## Key Learnings

### 1. **Transparent Windows**
- Requires `transparent: true` + `backgroundColor: '#00000000'`
- Also need `frame: false` for no title bar
- `setIgnoreMouseEvents(true)` makes it click-through

### 2. **Always-on-Top**
- Use `alwaysOnTop: true` during creation
- Call `setAlwaysOnTop(true, 'floating', 1)` for highest z-order
- `setVisibleOnAllWorkspaces()` for macOS/Linux

### 3. **Multi-Display**
- Calculate total bounds across all displays
- Create window size = max extent of all displays
- Mouse position needs conversion: `globalPos - windowPos = localPos`

### 4. **Animation Loop**
- 60 FPS assumed (dt = 1/60)
- `requestAnimationFrame` for smooth rendering
- Clear → Update → Render pattern

### 5. **High-DPI Support**
- Use `window.devicePixelRatio` for internal canvas size
- But keep CSS size at window.innerWidth/Height
- Scale 2D context: `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)`

### 6. **State Machine Design**
- Four states: idle → charging → jumping → landing
- Each state handles timing, animation, transitions
- Smooth interpolation (lerp) for position/angle

### 7. **Canvas Drawing**
- Draw order matters (back to front)
- Use transforms: `translate()`, `scale()`, `rotate()`
- Gradients for 3D effect

### 8. **Security (Context Isolation)**
- Main process has full Node access
- Preload script: limited access
- Renderer: only exposed APIs via contextBridge
- No `nodeIntegration` in renderer

---

## File Structure for Reference

```
penguin_pet/
├── electron/
│   ├── main.cjs              # Electron main process
│   └── preload.cjs           # Security preload
├── src/
│   ├── App.tsx               # Root component
│   ├── main.tsx              # React entry point
│   ├── index.css             # Global styles
│   ├── electron.d.ts         # Type definitions
│   ├── components/
│   │   └── FishCanvas.tsx    # Canvas component
│   ├── hooks/
│   │   ├── useAnimationLoop.ts
│   │   └── useMousePosition.ts
│   └── lib/
│       ├── penguin.ts        # Character class (modified fish.ts)
│       ├── vec2.ts           # 2D vector math
│       ├── chain.ts          # IK chain (optional)
│       └── spline.ts         # Curve interpolation (optional)
├── index.html                # HTML template
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript config
├── package.json              # Dependencies
└── electron-builder.json     # Build configuration
```

---

## Common Customizations

### Smaller/Larger Character
```typescript
// In FishCanvas.tsx resize function:
fishRef.current = new Fish(new Vec2(width / 2, height / 2), 0.5); // 50% size
```

### Faster/Slower Movement
```typescript
// In Fish class:
chargeDuration = 0.1;    // Faster charge (was 0.12)
jumpDuration = 0.25;     // Faster jump (was 0.35)
landDuration = 0.05;     // Faster land (was 0.08)
```

### Different Jump Behavior
```typescript
private handleJumping(dt: number): void {
  // ... existing code ...
  
  // Instead of parabolic arc, use different curve:
  // Slow fall: exponential
  // Fast start: different easing
  
  const easeOutCubic = (t: number) => {
    const x = t - 1;
    return x * x * x + 1;
  };
  
  this.jumpHeight = easeOutCubic(t) * this.baseJumpHeight;
}
```

### Always Visible (Never Hide)
```typescript
// In electron/main.cjs
mainWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
mainWindow.setAlwaysOnTop(true, 'floating', 1);

// For macOS, add:
if (process.platform === 'darwin') {
  mainWindow.setWindowButtonVisibility(false);
}
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Window not transparent | Check `backgroundColor: '#00000000'` and `transparent: true` |
| Mouse position wrong | Ensure you're converting global coords to window-local: `globalPos - windowBounds.x/y` |
| Choppy animation | Check `dt = 1/60` calculation in resolve(), verify `requestAnimationFrame` is called |
| Blurry on Retina | Check `devicePixelRatio` scaling in canvas setup |
| App won't build | Run `pnpm install` first, ensure Electron version matches platform |
| IPC not working | Check preload script path in `webPreferences.preload`, verify contextIsolation enabled |

---

## Next Steps

1. **Clone the fish project** as a starting point
2. **Modify character design** - update draw methods
3. **Test in browser first** - remove Electron, test rendering
4. **Add sound effects** - use Web Audio API or HTML5 Audio
5. **Package for distribution** - use electron-builder
6. **Add configuration** - allow user to resize window, change pet size
7. **Add animations** - idle tricks, reaction to events
8. **Publish** - create installer, distribute to users

