# Development Log: Green Spirit Animation

This document records the transformation process from the original fish animation to the final "Green Spirit" desktop pet.

## 1. Initial Transformation (Fish -> Spirit)
**Goal**: Convert the existing `fish_anim_ts` (spine-based fish) into a green, round sprite with leaf ears.

- **Model Change**:
  - Removed the `Chain` based inverse kinematics system used for the fish body.
  - Implemented a single `pos` based entity.
- **Visuals**:
  - **Body**: Changed from long fish shape to a "teardrop/blob" shape.
  - **Color**: Switched to Cyan/Green palette (`#00ffd2` body, `#00dc64` leaves).
  - **Features**: Added two leaf-shaped ears on top and large front-facing eyes.

## 2. Movement Logic Overhaul (Swimming -> Jumping)
**Goal**: The sprite should move by jumping/hopping instead of swimming.

- **Physics Engine**:
  - Implemented a **State Machine**: `Idle` -> `Charging` (Squash) -> `Jumping` (Stretch) -> `Landing` (Squash).
  - **Jumping Physics**: Replaced direct velocity tracking with a parabolic arc calculation using `jumpHeight` (sine wave based) and linear interpolation for X/Y position.
  - **Squash & Stretch**: Added `stretchX` and `stretchY` factors linked to the animation states to give a "jelly-like" feel.
  - **Shadow**: Added a dynamic shadow that shrinks and fades as the sprite jumps higher.

## 3. Visual Refinement: Texture & Glow
**Goal**: The sprite looked too flat/solid. Needed a translucent, glowing "spirit" look.

- **Gradients**:
  - Replaced solid fill with `CanvasGradient` (Radial) for the body.
  - Inner Color: Bright Cyan (`#00FFF0`).
  - Outer Color: Darker Cyan (`#00C0C0`) with translucent edges.
- **Lighting**:
  - Added an outer glow using `ctx.shadowBlur`.
  - Added "Rim Light" (edge highlighting) using a semi-transparent white stroke.
  - Enhanced Eyes: Added a secondary highlight to the pupil for a glassy/wet look.

## 4. Shape Correction (Triangular -> Round)
**Goal**: The body shape looked too triangular/conical. Needed to be a rounder, squishy ball.

- **Bezier Curve Tuning**:
  - **Shoulders**: Pushed control points horizontally outward immediately from the top.
  - **Top**: Flattened the top dome (instead of a sharp peak).
  - **Bottom**: Widened the bottom curve to act like a "bowl".
- **Result**: A shape that resembles a water drop or slime sitting on a surface.

## 5. Ear Correction
**Goal**: The leaf ears looked asymmetrical or "wonky" during rotation.

- **Symmetry Fix**:
  - Standardized rotation logic: `angle = side * 0.6 + wiggle`.
  - **Root Position**: Fixed the "stem" connection point to exactly match the top of the body curve (`height * 0.75`).
  - **Geometry**: Redrew leaves to point "up" in their local coordinate system, ensuring perfect mirror symmetry when rendered.

## 6. Final Polish
- **Scaling**: Reduced global scale to `0.7` for a cuter, more compact look.
- **App Behavior**: Removed the global `Escape` key shortcut in Electron to prevent accidental exits.
- **Documentation**: Updated `AGENTS.md` with the new architecture and parameters.

## Current State
The project is now a desktop overlay app featuring a semi-transparent, glowing green sprite that hops towards the mouse cursor with physics-based squash-and-stretch animation.
