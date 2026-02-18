import pyautogui
import tkinter as tk
from pynput import keyboard
import time
from datetime import datetime
import threading

region = None  # (x, y, width, height)
region_locked = False
overlay_window = None
status_window = None
hotkey_window = None

def select_region():
    global region
    
    if region_locked:
        print("Region is locked! Press Ctrl+Alt+L to unlock.")
        return

    root = tk.Tk()
    root.attributes("-alpha", 0.3)
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.config(cursor="cross")
    root.title("Select Region")

    start_x = start_y = 0
    rect = None

    canvas = tk.Canvas(root, bg="gray")
    canvas.pack(fill=tk.BOTH, expand=True)

    def on_mouse_down(event):
        nonlocal start_x, start_y, rect
        start_x, start_y = event.x, event.y
        rect = canvas.create_rectangle(start_x, start_y, start_x, start_y,
                                       outline="red", width=2)

    def on_mouse_drag(event):
        canvas.coords(rect, start_x, start_y, event.x, event.y)

    def on_mouse_up(event):
        global region
        end_x, end_y = event.x, event.y
        x1, y1 = min(start_x, end_x), min(start_y, end_y)
        x2, y2 = max(start_x, end_x), max(start_y, end_y)
        region = (x1, y1, x2 - x1, y2 - y1)
        print(f"Region selected: {region}")
        root.destroy()

    canvas.bind("<ButtonPress-1>", on_mouse_down)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_up)

    root.mainloop()


def hide_status():
    global status_window
    if status_window:
        try:
            status_window.quit()
            status_window.destroy()
        except:
            pass
        status_window = None


def show_status(message, duration=None, bg_color="blue"):
    global status_window
    
    hide_status()
    
    def create_status():
        global status_window
        
        status_window = tk.Tk()
        status_window.overrideredirect(True)
        status_window.attributes("-topmost", True)
        status_window.attributes("-alpha", 0.8)
        
        screen_width = status_window.winfo_screenwidth()
        status_window.geometry(f"250x50+{screen_width-270}+80")
        
        label = tk.Label(status_window, text=message, 
                         bg=bg_color, fg="white", font=("Arial", 12, "bold"))
        label.pack(fill=tk.BOTH, expand=True)
        
        if duration:
            status_window.after(duration, lambda: update_status_to_waiting())
        
        status_window.mainloop()
    
    threading.Thread(target=create_status, daemon=True).start()


def update_status_to_waiting():
    if region_locked:
        show_status("✅ Waiting for screenshot...", None, "blue")


def take_screenshot():
    global region
    print(f"Current region value: {region}")
    if region is None:
        print("No region selected yet.")
        show_status("⚠️ No region selected!", None, "orange")
        return

    show_status("📸 Saving screenshot...", 1000, "green")
    
    x, y, w, h = region
    img = pyautogui.screenshot(region=(x, y, w, h))
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
    filename = f"screenshot_{timestamp}.png"
    img.save(filename)
    print(f"Saved {filename}")


def on_select_hotkey():
    global region_locked
    print("Select a region by dragging...")
    select_region()
    if region is not None:
        region_locked = True
        threading.Thread(target=show_lock_overlay, daemon=True).start()
        show_status("✅ Waiting for screenshot...", None, "blue")


def on_screenshot_hotkey():
    print("Taking screenshot...")
    take_screenshot()


def show_hotkey_overlay():
    global hotkey_window
    
    if hotkey_window:
        return
    
    def create_hotkey():
        global hotkey_window
        
        hotkey_window = tk.Tk()
        hotkey_window.overrideredirect(True)
        hotkey_window.attributes("-topmost", True)
        hotkey_window.attributes("-alpha", 0.8)
        
        screen_width = hotkey_window.winfo_screenwidth()
        hotkey_window.geometry(f"220x90+{screen_width-240}+140")
        
        frame = tk.Frame(hotkey_window, bg="darkblue", padx=5, pady=5)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Hotkeys:", bg="darkblue", fg="white", 
                 font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(frame, text="Ctrl+Alt+S - Select", bg="darkblue", fg="white", 
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(frame, text="Ctrl+Alt+C - Capture", bg="darkblue", fg="white", 
                 font=("Arial", 9)).pack(anchor="w")
        tk.Label(frame, text="Ctrl+Alt+L - Lock/Unlock", bg="darkblue", fg="white", 
                 font=("Arial", 9)).pack(anchor="w")
        
        hotkey_window.mainloop()
    
    threading.Thread(target=create_hotkey, daemon=True).start()


def hide_lock_overlay():
    global overlay_window
    if overlay_window:
        try:
            overlay_window.quit()
            overlay_window.destroy()
        except:
            pass
        overlay_window = None


def show_lock_overlay():
    global overlay_window
    
    hide_lock_overlay()
    
    def create_overlay():
        global overlay_window
        
        overlay_window = tk.Tk()
        overlay_window.overrideredirect(True)
        overlay_window.attributes("-topmost", True)
        overlay_window.attributes("-alpha", 0.8)
        
        screen_width = overlay_window.winfo_screenwidth()
        overlay_window.geometry(f"200x50+{screen_width-220}+20")
        
        if region_locked:
            label = tk.Label(overlay_window, text="🔒 Region Locked", 
                             bg="green", fg="white", font=("Arial", 12, "bold"))
        else:
            label = tk.Label(overlay_window, text="🔓 Region Not Locked", 
                             bg="gray", fg="white", font=("Arial", 12, "bold"))
        label.pack(fill=tk.BOTH, expand=True)
        
        overlay_window.mainloop()
    
    threading.Thread(target=create_overlay, daemon=True).start()


def toggle_lock():
    global region_locked
    
    if region is None:
        print("No region selected yet. Select a region first.")
        show_status("⚠️ Select region first!", None, "orange")
        return
    
    region_locked = not region_locked
    
    if region_locked:
        print(f"Region LOCKED at {region}")
        hide_lock_overlay()
        threading.Thread(target=show_lock_overlay, daemon=True).start()
        show_status("✅ Waiting for screenshot...", None, "blue")
    else:
        print("Region UNLOCKED")
        hide_lock_overlay()
        threading.Thread(target=show_lock_overlay, daemon=True).start()
        show_status("⏸️ Region unlocked", None, "gray")


# Hotkeys:
# Ctrl+Alt+S → select region
# Ctrl+Alt+C → screenshot (capture) region
# Ctrl+Alt+L → lock/unlock region
show_hotkey_overlay()
with keyboard.GlobalHotKeys({
    '<ctrl>+<alt>+s': on_select_hotkey,
    '<ctrl>+<alt>+c': on_screenshot_hotkey,
    '<ctrl>+<alt>+l': toggle_lock
}) as listener:
    print("Press Ctrl+Alt+S to select region, Ctrl+Alt+C to capture screenshot, Ctrl+Alt+L to lock/unlock.")
    listener.join()
