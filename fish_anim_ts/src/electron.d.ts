export {};

declare global {
  interface Window {
    electronAPI?: {
      onMousePosition: (callback: (pos: { x: number; y: number }) => void) => void;
    };
  }
}
