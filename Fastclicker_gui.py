import customtkinter as ctk
from pynput import mouse
import threading
import time
import random
import sys
import signal

# === CONFIGURATION ===
CLICK_DELAY_MIN = 0.05
CLICK_DELAY_MAX = 0.07
LEFT_CLICK_COUNT = 5
RIGHT_CLICK_COUNT = 5
RUN_TIME = 600

mouse_controller = mouse.Controller()

# === GLOBAL FLAGS ===
left_clicking_in_progress = False
right_clicking_in_progress = False
clicker_active = False
shutdown_flag = False

# === CLICK FUNCTIONS ===
def human_left_clicks():
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
    global shutdown_flag
    """Stops the script automatically after RUN_TIME seconds."""
    time.sleep(RUN_TIME)
    if not shutdown_flag:
        print(f"[DEBUG] Auto-shutdown triggered after {RUN_TIME} seconds")
        sys.exit(0)


# === GUI ===
class ClickerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Fast Clicker Control Panel")
        self.geometry("400x350")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Labels
        self.title_label = ctk.CTkLabel(self, text="🖱️ Fast Clicker", font=("Arial", 20, "bold"))
        self.title_label.pack(pady=15)

        # Input fields
        self.left_click_var = ctk.StringVar(value=str(LEFT_CLICK_COUNT))
        self.right_click_var = ctk.StringVar(value=str(RIGHT_CLICK_COUNT))
        self.runtime_var = ctk.StringVar(value=str(RUN_TIME))

        self.left_input = self._create_input("Left Click Count", self.left_click_var)
        self.right_input = self._create_input("Right Click Count", self.right_click_var)
        self.runtime_input = self._create_input("Run Time (s)", self.runtime_var)

        # Status label
        self.status_label = ctk.CTkLabel(self, text="Status: DEACTIVATED ⛔", font=("Arial", 16))
        self.status_label.pack(pady=20)

        # Apply button
        self.apply_button = ctk.CTkButton(self, text="Apply Settings", command=self.apply_settings)
        self.apply_button.pack(pady=5)

        # Shutdown button
        self.shutdown_button = ctk.CTkButton(self, text="Shutdown Script", fg_color="red", hover_color="darkred", command=self.shutdown_script)
        self.shutdown_button.pack(pady=10)

        # Auto update status
        self.update_status()

        # Handle GUI close
        self.protocol("WM_DELETE_WINDOW", self.shutdown_script)

    def _create_input(self, label_text, var):
        frame = ctk.CTkFrame(self)
        frame.pack(pady=5)
        label = ctk.CTkLabel(frame, text=label_text)
        label.pack(side="left", padx=10)
        entry = ctk.CTkEntry(frame, textvariable=var, width=100)
        entry.pack(side="right", padx=10)
        return entry

    def apply_settings(self):
        global LEFT_CLICK_COUNT, RIGHT_CLICK_COUNT, RUN_TIME
        try:
            LEFT_CLICK_COUNT = int(self.left_click_var.get())
            RIGHT_CLICK_COUNT = int(self.right_click_var.get())
            RUN_TIME = int(self.runtime_var.get())
            print(f"[INFO] Updated: LEFT={LEFT_CLICK_COUNT}, RIGHT={RIGHT_CLICK_COUNT}, RUNTIME={RUN_TIME}")
        except ValueError:
            print("[ERROR] Invalid input. Please enter numbers only.")

    def update_status(self):
        state_text = "Status: ACTIVATED ✅" if clicker_active else "Status: DEACTIVATED ⛔"
        self.status_label.configure(text=state_text)
        self.after(500, self.update_status)  # refresh every 0.5s

    def shutdown_script(self):
        global shutdown_flag
        shutdown_flag = True
        print("[INFO] Shutting down script and GUI...")
        self.destroy()
        sys.exit(0)


# === MAIN ENTRY ===
if __name__ == "__main__":
    # Start mouse listener thread
    listener = mouse.Listener(on_click=on_click)
    listener.daemon = True
    listener.start()

    # Start auto-shutdown timer
    threading.Thread(target=auto_shutdown, daemon=True).start()

    print("[INFO] Script started. Press MIDDLE mouse button to activate/deactivate.")

    # Start GUI
    app = ClickerGUI()
    app.mainloop()
