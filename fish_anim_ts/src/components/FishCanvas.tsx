import { useRef, useEffect, useCallback } from 'react';
import { Fish } from '../lib/fish';
import { Vec2 } from '../lib/vec2';
import { useAnimationLoop } from '../hooks/useAnimationLoop';

export function FishCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const fishRef = useRef<Fish | null>(null);
  const mousePosRef = useRef<Vec2>(new Vec2(0, 0));
  const dprRef = useRef<number>(1);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const resize = () => {
      const dpr = window.devicePixelRatio || 1;
      dprRef.current = dpr;
      const width = window.innerWidth;
      const height = window.innerHeight;

      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;

      const ctx = canvas.getContext('2d');
      if (ctx) {
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      }

      if (!fishRef.current) {
        fishRef.current = new Fish(new Vec2(width / 2, height / 2), 0.7);
      }
    };

    resize();
    window.addEventListener('resize', resize);
    return () => window.removeEventListener('resize', resize);
  }, []);

  useEffect(() => {
    if (window.electronAPI) {
      window.electronAPI.onMousePosition((pos) => {
        mousePosRef.current = new Vec2(pos.x, pos.y);
      });
    } else {
      const handleMouseMove = (e: MouseEvent) => {
        mousePosRef.current = new Vec2(e.clientX, e.clientY);
      };
      window.addEventListener('mousemove', handleMouseMove);
      return () => window.removeEventListener('mousemove', handleMouseMove);
    }
  }, []);

  const render = useCallback(() => {
    const canvas = canvasRef.current;
    const fish = fishRef.current;
    if (!canvas || !fish) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = dprRef.current;
    const width = canvas.width / dpr;
    const height = canvas.height / dpr;

    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);

    fish.resolve(mousePosRef.current);
    fish.render(ctx);
  }, []);

  useAnimationLoop(render);

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
