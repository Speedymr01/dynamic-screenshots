import pyautogui
import tkinter as tk
from pynput import keyboard
import time
from datetime import datetime
import threading
import sys

region = None
status_window = None
status_label = None
button_windows = []


def exit_app():
    print("Exiting application...")
    import os
    os._exit(0)

def select_region():
    global region

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
    pass


def show_status(message, duration=None, bg_color="blue"):
    global status_window, status_label
    
    def create_or_update():
        global status_window, status_label
        
        if status_window is None:
            try:
                status_window = tk.Tk()
                status_window.overrideredirect(True)
                status_window.attributes("-topmost", True)
                status_window.attributes("-alpha", 0.8)
                
                screen_width = status_window.winfo_screenwidth()
                status_window.geometry(f"250x50+{screen_width-270}+80")
                
                status_label = tk.Label(status_window, text=message, 
                                 bg=bg_color, fg="white", font=("Arial", 12, "bold"))
                status_label.pack(fill=tk.BOTH, expand=True)
                
                if duration:
                    status_window.after(duration, lambda: update_status_to_waiting())
                
                status_window.mainloop()
            except:
                pass
        else:
            try:
                status_label.config(text=message, bg=bg_color)
                if duration:
                    status_window.after(duration, lambda: update_status_to_waiting())
            except:
                status_window = None
                status_label = None
    
    if status_window is None:
        threading.Thread(target=create_or_update, daemon=True).start()
    else:
        create_or_update()


def update_status_to_waiting():
    show_status("✅ Ready to capture", None, "blue")


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
    print("Select a region by dragging...")
    show_status("📐 Selecting region...", None, "purple")
    select_region()
    if region is not None:
        show_status("✅ Ready to capture", None, "blue")
    else:
        show_status("⚠️ No region selected", None, "orange")


def on_screenshot_hotkey():
    print("Taking screenshot...")
    take_screenshot()


def show_button_overlays():
    global button_windows
    
    if button_windows:
        return
    
    def create_select_button():
        btn_win = tk.Tk()
        btn_win.overrideredirect(True)
        btn_win.attributes("-topmost", True)
        btn_win.attributes("-alpha", 0.9)
        
        screen_width = btn_win.winfo_screenwidth()
        btn_win.geometry(f"180x60+{screen_width-200}+140")
        
        btn = tk.Button(btn_win, text="📐 Select Region", 
                        command=on_select_hotkey,
                        bg="blue", fg="white", font=("Arial", 11, "bold"),
                        relief=tk.RAISED, bd=3)
        btn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_windows.append(btn_win)
        btn_win.mainloop()
    
    def create_capture_button():
        btn_win = tk.Tk()
        btn_win.overrideredirect(True)
        btn_win.attributes("-topmost", True)
        btn_win.attributes("-alpha", 0.9)
        
        screen_width = btn_win.winfo_screenwidth()
        btn_win.geometry(f"180x60+{screen_width-200}+210")
        
        btn = tk.Button(btn_win, text="� Capture", 
                        command=on_screenshot_hotkey,
                        bg="green", fg="white", font=("Arial", 11, "bold"),
                        relief=tk.RAISED, bd=3)
        btn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_windows.append(btn_win)
        btn_win.mainloop()
    
    def create_exit_button():
        btn_win = tk.Tk()
        btn_win.overrideredirect(True)
        btn_win.attributes("-topmost", True)
        btn_win.attributes("-alpha", 0.9)
        
        screen_width = btn_win.winfo_screenwidth()
        btn_win.geometry(f"180x60+{screen_width-200}+280")
        
        btn = tk.Button(btn_win, text="❌ Exit", 
                        command=exit_app,
                        bg="red", fg="white", font=("Arial", 11, "bold"),
                        relief=tk.RAISED, bd=3)
        btn.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        button_windows.append(btn_win)
        btn_win.mainloop()
    
    threading.Thread(target=create_select_button, daemon=True).start()
    threading.Thread(target=create_capture_button, daemon=True).start()
    threading.Thread(target=create_exit_button, daemon=True).start()


# Hotkeys:
# Ctrl+Alt+S → select region
# Ctrl+Alt+C → screenshot (capture) region
show_button_overlays()
with keyboard.GlobalHotKeys({
    '<ctrl>+<alt>+s': on_select_hotkey,
    '<ctrl>+<alt>+c': on_screenshot_hotkey
}) as listener:
    print("Press Ctrl+Alt+S to select region, Ctrl+Alt+C to capture screenshot.")
    listener.join()
