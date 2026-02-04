import pygame
import os
from pynput import mouse as pynput_mouse
from chain import Vec2
from fish import Fish

os.environ['SDL_VIDEO_WINDOW_POS'] = '0,0'

def main():
    pygame.init()
    
    info = pygame.display.Info()
    screen_width, screen_height = info.current_w, info.current_h
    
    screen = pygame.display.set_mode((screen_width, screen_height), pygame.NOFRAME)
    pygame.display.set_caption("Fish")
    
    hwnd = pygame.display.get_wm_info().get('window')
    if hwnd:
        try:
            from AppKit import NSApp, NSApplication, NSFloatingWindowLevel
            from Quartz import CGWindowLevelForKey, kCGOverlayWindowLevelKey
            NSApplication.sharedApplication()
            window = NSApp.windows()[0]
            window.setLevel_(CGWindowLevelForKey(kCGOverlayWindowLevelKey))
            window.setOpaque_(False)
            window.setBackgroundColor_(NSApp.windows()[0].backgroundColor().colorWithAlphaComponent_(0))
            window.setIgnoresMouseEvents_(True)
        except:
            pass
    
    clock = pygame.time.Clock()
    fish = Fish(Vec2(screen_width // 2, screen_height // 2))
    
    mouse_pos = [screen_width // 2, screen_height // 2]
    
    def on_move(x, y):
        mouse_pos[0] = x
        mouse_pos[1] = y
    
    listener = pynput_mouse.Listener(on_move=on_move)
    listener.start()
    
    transparent_color = (1, 1, 1)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        fish.resolve(Vec2(mouse_pos[0], mouse_pos[1]))
        
        screen.fill(transparent_color)
        screen.set_colorkey(transparent_color)
        fish.display(screen)
        
        pygame.display.flip()
        clock.tick(60)
    
    listener.stop()
    pygame.quit()


if __name__ == "__main__":
    main()
