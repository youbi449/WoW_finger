import pyautogui
import pygetwindow as gw
import time
from pynput import keyboard
from Gui import Gui
import keyboard as k
import threading

Debug = True
key_being_held = None
modifier_holded = None
forbidden_keys = ["z", "q", "s", "d", "space"]
modifiers = ["shift", "ctrl_l"]
DELAY_BETWEEN_KEYS = 0.7

APP_START = False
keys_active = set()

def start_app():
    global APP_START
    APP_START = True


def stop_app():
    global APP_START
    APP_START = False


def spam_key():

    while key_being_held:
        active_window = gw.getActiveWindow()
        log(active_window.title)
        if active_window.title == "World of Warcraft":
            log(f"Key currently being held: {key_being_held}")
            try:

                    pyautogui.hotkey(key_being_held)

            except TypeError:
                log(f"Skipped invalid key: {key_being_held}")
            time.sleep(DELAY_BETWEEN_KEYS)


def on_press(key):
    global key_being_held, modifier_holded, modifiers
    try:
        key_char = key.char  # Pour les KeyCode, qui représentent les touches caractères
    except AttributeError:
        key_char = key.name  # Pour les Key, qui représentent les touches spéciales

    if key_char in forbidden_keys:
        return

    if not modifier_holded or modifier_holded != key_char:
        if any(mod in key_char for mod in modifiers):
            modifier_holded = key_char
            log(f"modifier registered {modifier_holded}")

    if key_being_held is None and not any(mod in key_char for mod in modifiers):

        key_being_held = key_char
        log(f"{key_char} registered")


def on_release(key):
    global key_being_held, modifier_holded

    if str(key) == modifier_holded:
        modifier_holded = None
        log(f"modifier unhooked")
    else:
        key_being_held = None
    log("Key released")
    log(key_being_held)


def log(message):
    if Debug:
        print(message)


gui_thread = threading.Thread(target=Gui, args=(start_app, stop_app))
gui_thread.start()

listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

try:
    while True:
        if APP_START:
            spam_key()
        time.sleep(0.1)
except KeyboardInterrupt:
    listener.stop()
