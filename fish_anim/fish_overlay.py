#!/usr/bin/env python3
import sys
from AppKit import (
    NSApplication, NSWindow, NSView, NSScreen, NSColor,
    NSBorderlessWindowMask, NSTimer,
    NSApplicationActivationPolicyAccessory, NSEvent, NSKeyDownMask,
    NSFloatingWindowLevel
)
from Quartz import CGEventCreate, CGEventGetLocation, CGGetActiveDisplayList, CGDisplayBounds
from PyObjCTools import AppHelper
from objc import super
from Foundation import NSMakeRect

sys.path.insert(0, '/Users/zhangkechi/Documents/GitHub/math_video/.worktrees/fish_demo/fish_anim')
from chain import Vec2
from fish_native import Fish


def get_cg_display_bounds():
    err, displays, count = CGGetActiveDisplayList(10, None, None)
    min_x = min(CGDisplayBounds(d).origin.x for d in displays)
    min_y = min(CGDisplayBounds(d).origin.y for d in displays)
    max_x = max(CGDisplayBounds(d).origin.x + CGDisplayBounds(d).size.width for d in displays)
    max_y = max(CGDisplayBounds(d).origin.y + CGDisplayBounds(d).size.height for d in displays)
    return min_x, min_y, max_x, max_y


class FishView(NSView):
    def initWithFrame_cgBounds_(self, frame, cg_bounds):
        self = super().initWithFrame_(frame)
        if self is None:
            return None
        
        self.cg_min_x, self.cg_min_y, self.cg_max_x, self.cg_max_y = cg_bounds
        self.cg_height = self.cg_max_y - self.cg_min_y
        self.view_height = frame.size.height
        
        self.fish = Fish(Vec2(frame.size.width / 2, frame.size.height / 2), scale=0.5)
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
        
        norm_x = (mouse_loc.x - self.cg_min_x) / (self.cg_max_x - self.cg_min_x)
        norm_y = (mouse_loc.y - self.cg_min_y) / (self.cg_max_y - self.cg_min_y)
        
        frame = self.frame()
        local_x = norm_x * frame.size.width
        local_y = (1 - norm_y) * frame.size.height
        
        self.fish.resolve(Vec2(local_x, local_y))
        self.setNeedsDisplay_(True)


class FishApp:
    def __init__(self):
        self.app = NSApplication.sharedApplication()
        self.app.setActivationPolicy_(NSApplicationActivationPolicyAccessory)
        
        screens = NSScreen.screens()
        min_x = min(s.frame().origin.x for s in screens)
        min_y = min(s.frame().origin.y for s in screens)
        max_x = max(s.frame().origin.x + s.frame().size.width for s in screens)
        max_y = max(s.frame().origin.y + s.frame().size.height for s in screens)
        
        global_frame = NSMakeRect(min_x, min_y, max_x - min_x, max_y - min_y)
        local_frame = NSMakeRect(0, 0, max_x - min_x, max_y - min_y)
        
        cg_bounds = get_cg_display_bounds()
        
        self.window = NSWindow.alloc().initWithContentRect_styleMask_backing_defer_(
            global_frame,
            NSBorderlessWindowMask,
            2,
            False
        )
        
        self.window.setLevel_(NSFloatingWindowLevel + 1)
        self.window.setOpaque_(False)
        self.window.setBackgroundColor_(NSColor.clearColor())
        self.window.setIgnoresMouseEvents_(True)
        self.window.setCollectionBehavior_(1 << 0 | 1 << 4)
        
        self.view = FishView.alloc().initWithFrame_cgBounds_(local_frame, cg_bounds)
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
        print("Fish started! Press ESC to quit (or Ctrl+C in terminal).")
        AppHelper.runEventLoop()


if __name__ == "__main__":
    app = FishApp()
    app.run()
