#!/usr/bin/env python3
import sys
import math
from AppKit import (
    NSApplication, NSWindow, NSView, NSScreen, NSColor,
    NSBorderlessWindowMask, NSTimer, NSRunLoop, NSDefaultRunLoopMode,
    NSApplicationActivationPolicyAccessory, NSEvent, NSKeyDownMask,
    NSCommandKeyMask, NSFloatingWindowLevel
)
from Quartz import CGEventCreate, CGEventGetLocation
from PyObjCTools import AppHelper
from objc import super

sys.path.insert(0, '/Users/zhangkechi/Documents/GitHub/math_video/.worktrees/fish_demo/fish_anim')
from chain import Vec2
from fish_native import Fish


class FishView(NSView):
    def initWithFrame_(self, frame):
        self = super().initWithFrame_(frame)
        if self is None:
            return None
        
        screen_height = NSScreen.mainScreen().frame().size.height
        self.fish = Fish(Vec2(frame.size.width / 2, screen_height / 2), scale=0.5)
        self.screen_height = screen_height
        return self
    
    def drawRect_(self, rect):
        from Quartz import CGContextSetLineWidth
        from AppKit import NSGraphicsContext
        
        ctx = NSGraphicsContext.currentContext().CGContext()
        CGContextSetLineWidth(ctx, 2)
        self.fish.draw(ctx)
    
    def updateFish_(self, timer):
        event = CGEventCreate(None)
        mouse_loc = CGEventGetLocation(event)
        
        flipped_y = self.screen_height - mouse_loc.y
        self.fish.resolve(Vec2(mouse_loc.x, flipped_y))
        self.setNeedsDisplay_(True)


class FishApp:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        screen = NSScreen.mainScreen()
        screen_frame = screen.frame()
        
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            screen_frame,
            NSBorderlessWindowMask,
            2,
            False
        )
        
        self.window.setLevel_(NSFloatingWindowLevel + 1)
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setIgnoresMouseEvents_(True)
        self.window.setCollectionBehavior_(1 << 0 | 1 << 4)
        
        self.view = FishView.alloc().initWithFrame_(screen_frame)
        self.window.setContentView_(self.view)
        
        self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
            1.0 / 60.0,
            self.view,
            'updateFish:',
            None,
            True
        )
        
        NSEvent.addGlobalMonitorForEventsMatchingMask_handler_(
            NSKeyDownMask,
            self.handle_key
        )
        
        self.window.makeKeyAndOrderFront_(None)
    
    def handle_key(self, event):
        if event.keyCode() == 53:
            self.quit()
    
    def quit(self):
        self.timer.invalidate()
        self.app.terminate_(None)
    
    def run(self):
        print("Fish started! Press ESC to quit.")
        AppHelper.runEventLoop()


if __name__ == "__main__":
    app = FishApp()
    app.run()
