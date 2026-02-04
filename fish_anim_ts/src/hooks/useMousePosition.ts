import { useState, useEffect, type RefObject } from 'react';
import { Vec2 } from '../lib/vec2';

export function useMousePosition(
  elementRef: RefObject<HTMLElement | null>
): Vec2 {
  const [position, setPosition] = useState<Vec2>(new Vec2(0, 0));

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const element = elementRef.current;
      if (element) {
        const rect = element.getBoundingClientRect();
        setPosition(new Vec2(e.clientX - rect.left, e.clientY - rect.top));
      } else {
        setPosition(new Vec2(e.clientX, e.clientY));
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => {
      window.removeEventListener('mousemove', handleMouseMove);
    };
  }, [elementRef]);

  return position;
}
