import time

from Gui import Gui
import keyboard as k
import threading
import os
import pygetwindow as gw
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import keyboard

Debug = True
forbidden_keys = [17, 30, 31, 32, 57]  # z, q, s, d, space keycodes
WoW = ["World of Warcraft"]
DELAY_BETWEEN_KEYS = 0.3

APP_START = False
CHAT_PAUSE = False
keys_active = set()


def start_app():
    global APP_START
    APP_START = True


def stop_app():
    global APP_START
    APP_START = False


def spam_key():

    while len(keys_active) > 0:
        resync()
        log(keys_active)
        active_window = gw.getActiveWindow()

        if active_window:
            if active_window.title in WoW:

                try:
                    hotkey = list(keys_active)
                    log(f"LES CODES {hotkey}")
                    if hotkey:  # Vérifie que hotkey n'est pas vide
                        log(f"key sent {hotkey}")

                        for hk in hotkey:
                            k.send(int(hk))
                        time.sleep(0.1)
                    else:
                        log("No valid hotkey to send.")
                except TypeError:
                    log(f"Skipped invalid key: {keys_active}")
                time.sleep(DELAY_BETWEEN_KEYS)


def on_press(key):
    global CHAT_PAUSE
    if key == 28:  # keycode for "enter"
        CHAT_PAUSE = not CHAT_PAUSE
    elif key == 1 and CHAT_PAUSE:  # keycode for "esc"
        # that mean user start a message and didn't send it with enter

        CHAT_PAUSE = False
    else:
        if key in forbidden_keys or k.is_modifier(key):
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
    if e.event_type == KEY_DOWN:
        on_press(e.scan_code)
    elif e.event_type == KEY_UP:
        on_release(e.scan_code)


def log(message):
    if Debug:
        print(message)


def resync():
    """Assure que le set est correctement synchronisé avec les entrées utilisateur"""
    keys_to_check = list(keys_active)  # Crée une copie de la liste pour itérer
    for key in keys_to_check:
        if not k.is_pressed(key):
            if key in keys_active:  # Ajoute une vérification avant de supprimer
                keys_active.remove(key)
                log(f"WARNING A KEY DELETED: {key}")
            else:
                log(f"Key already removed: {key}")


gui_thread = threading.Thread(target=Gui, args=(start_app, stop_app), daemon=True)
gui_thread.start()


k.hook(lambda e: on_action(e))

try:
    while True:
        resync()
        if not gui_thread.is_alive():
            exit()
        if APP_START and not CHAT_PAUSE:
            spam_key()
        time.sleep(0.1)
except KeyboardInterrupt:
    exit(1)
