from pynput import mouse
import threading
import time
import random
import sys
import signal

# === CONFIGURATION ===
CLICK_DELAY_MIN = 0.05   # Minimum delay between clicks
CLICK_DELAY_MAX = 0.07   # Maximum delay between clicks
LEFT_CLICK_COUNT = 5     # Number of left clicks per trigger
RIGHT_CLICK_COUNT = 5    # Number of right clicks per trigger
RUN_TIME = 600           # Auto-stop after 600 seconds (10 minutes)

mouse_controller = mouse.Controller()

# === GLOBAL FLAGS ===
left_clicking_in_progress = False
right_clicking_in_progress = False
clicker_active = False  # <--- toggled by middle mouse button


# === CLICK FUNCTIONS ===
def human_left_clicks():
    """Performs human-like left clicks."""
    global left_clicking_in_progress
    if left_clicking_in_progress:
        return
    left_clicking_in_progress = True
    try:
        for _ in range(LEFT_CLICK_COUNT):
            mouse_controller.click(mouse.Button.left)
            time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
        print("[DEBUG] Done left clicks")
    finally:
        left_clicking_in_progress = False


def human_right_clicks():
    """Performs human-like right clicks."""
    global right_clicking_in_progress
    if right_clicking_in_progress:
        return
    right_clicking_in_progress = True
    try:
        for _ in range(RIGHT_CLICK_COUNT):
            mouse_controller.click(mouse.Button.right)
            time.sleep(random.uniform(CLICK_DELAY_MIN, CLICK_DELAY_MAX))
        print("[DEBUG] Done right clicks")
    finally:
        right_clicking_in_progress = False


# === EVENT HANDLER ===
def on_click(x, y, button, pressed):
    global clicker_active

    if not pressed:
        return

    # Toggle clicker ON/OFF with middle mouse button
    if button == mouse.Button.middle:
        clicker_active = not clicker_active
        state = "ACTIVATED ✅" if clicker_active else "DEACTIVATED ⛔"
        print(f"[DEBUG] Clicker {state}")
        return

    # Only respond to clicks if active
    if not clicker_active:
        return

    if button == mouse.Button.left:
        threading.Thread(target=human_left_clicks, daemon=True).start()
    elif button == mouse.Button.right:
        threading.Thread(target=human_right_clicks, daemon=True).start()


# === AUTO SHUTDOWN ===
def auto_shutdown():
    """Stops the script automatically after RUN_TIME seconds."""
    time.sleep(RUN_TIME)
    print(f"[DEBUG] Auto-shutdown triggered after {RUN_TIME} seconds")
    sys.exit(0)


# === MAIN ENTRY ===
if __name__ == "__main__":
    # Start mouse listener
    mouse.Listener(on_click=on_click).start()

    # Start auto-shutdown timer
    threading.Thread(target=auto_shutdown, daemon=True).start()

    print("[INFO] Script started. Press MIDDLE mouse button to activate/deactivate.")
    signal.pause()
