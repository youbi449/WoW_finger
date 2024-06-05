
import time

from Gui import Gui
import keyboard as k
import threading

import pygetwindow as gw
from keyboard._keyboard_event import KEY_DOWN, KEY_UP

Debug = True
forbidden_keys = ["z", "q", "s", "d", "space", "ctrl", "maj", "shift"]
WoW = ["World of Warcraft"]
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

    while len(keys_active) > 0:

        log(keys_active)
        active_window = gw.getActiveWindow()

        if active_window:
            if active_window.title in WoW:

                try:
                    hotkey = "+".join(
                        [
                            cmd.lower()
                            for cmd in sorted(list(keys_active), key=len, reverse=True)
                        ]
                    )
                    log(f"key sent {hotkey}")
                    k.press_and_release(str(hotkey))
                    time.sleep(0.1)
                except TypeError:
                    log(f"Skipped invalid key: {keys_active}")
                time.sleep(DELAY_BETWEEN_KEYS)


def on_press(key):
    if key in forbidden_keys:
        return
    if key not in keys_active:
        keys_active.add(key)


def on_release(key):

    if key in keys_active:
        keys_active.remove(key)
        log(f"Key released: {key}")
    else:
        log(f"Tried to release a key not in active set: {key}")


def on_action(e):
    resync()
    if e.event_type == KEY_DOWN:
        on_press(e.name)
    elif e.event_type == KEY_UP:
        on_release(e.name)


def log(message):
    if Debug:
        print(message)


def resync():
    """Assure que le set est correctement synchronisé avec les entrées utilisateur"""
    keys_to_check = list(keys_active)  # Crée une copie de la liste pour itérer
    for key in keys_to_check:
        if not k.is_pressed(key):
            keys_active.remove(key)


gui_thread = threading.Thread(target=Gui, args=(start_app, stop_app))
gui_thread.start()


k.hook(lambda e: on_action(e))

try:
    while True:

        if APP_START:
            spam_key()
        time.sleep(0.1)
except KeyboardInterrupt:
    exit(1)
