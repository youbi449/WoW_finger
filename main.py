import time

from Gui import Gui
import keyboard as k
import threading
import pygetwindow as gw
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import os
from plyer import notification


Debug = True
forbidden_keys = [17, 30, 31, 32, 57, 91]  # w, a, s, d, space, windows keycodes
WoW = ["World of Warcraft"]
DELAY_BETWEEN_KEYS = 0.3

APP_START = False
PAUSE = False

keys_active = set()


# try to get the pause key from the config file
try:
    with open("config.ini", "r") as config_file:
        for line in config_file:
            if line.startswith("PAUSE_KEY"):
                PAUSE_KEY = k.key_to_scan_codes(line.strip().split("=")[1], True)
                break
        else:
            PAUSE_KEY = None
except FileNotFoundError:
    PAUSE_KEY = None


def notif(message):
    notification.notify(
        title="Wow Finger", message=message, app_name="Wow Finger"
    )


def start_app():
    global APP_START
    if not PAUSE_KEY:
        notif("You have to set a pause key, else you can't use the app")
        return
    # to avoid the notification spam
    if not APP_START:
        APP_START = True
        notif("App is now running")


def stop_app():
    global APP_START
    if APP_START:
        # to avoid the notification spam
        APP_START = False
        notif("App is now stopped")


def spam_key():

    while len(keys_active) > 0:

        log(keys_active)

        try:
            hotkey = list(keys_active)
            log(f"LES CODES {hotkey}")
            if hotkey:
                log(f"key sent {hotkey}")

                for hk in hotkey:
                    k.send(hk)
                resync()
                time.sleep(0.1)
            else:
                log("No valid hotkey to send.")
        except TypeError:
            log(f"Skipped invalid key: {keys_active}")
        time.sleep(DELAY_BETWEEN_KEYS)


def on_press(key):
    global PAUSE
    if key in PAUSE_KEY:

        if is_correct_window():
            PAUSE = not PAUSE
            log(f"toggle pause {PAUSE}")
            if PAUSE:
                notif("App is now paused")
            else:
                notif("App is now running")
    if key in forbidden_keys or k.is_modifier(key):
        return

    elif key not in keys_active and key not in PAUSE_KEY:
        keys_active.add(key)


def on_release(key):

    if key in keys_active:
        keys_active.remove(key)


def on_action(e):
    if e.event_type == KEY_DOWN:
        on_press(e.scan_code)
    elif e.event_type == KEY_UP:
        on_release(e.scan_code)


def log(message):
    if Debug:
        print(message)


def set_pause_key(key):
    global PAUSE_KEY
    PAUSE_KEY = k.key_to_scan_codes(key, True)
    update_config("PAUSE_KEY", key)
    log(f"Pause key set to {PAUSE_KEY}")
    notif(f"Pause key set to {key}")


def update_config(settings_name, settings_value):
    try:
        with open("config.ini", "r+") as c:
            content = c.readlines()
            found = False
            for i, line in enumerate(content):
                if line.startswith(settings_name):
                    content[i] = f"{settings_name}={settings_value}\n"
                    found = True
                    break
            if not found:
                content.append(f"{settings_name}={settings_value}\n")
            c.seek(0)
            c.writelines(content)
            c.truncate()
    except FileNotFoundError:
        with open("config.ini", "w") as c:
            c.write(f"{settings_name}={settings_value}\n")


def is_correct_window():
    active_window = gw.getActiveWindow()
    return (
        active_window.title in WoW if active_window and active_window.title else False
    )


def resync():
    """Assure que le set est correctement synchronisé avec les entrées utilisateur"""
    keys_to_check = list(keys_active)
    for key in keys_to_check:
        if not k.is_pressed(key):
            if key in keys_active:
                keys_active.remove(key)
                log(f"WARNING A KEY DELETED: {key}")
            else:
                log(f"Key already removed: {key}")


gui_thread = threading.Thread(
    target=Gui, args=(start_app, stop_app, set_pause_key), daemon=True
)
gui_thread.start()


k.hook(lambda e: on_action(e))

try:
    while True:

        if not gui_thread.is_alive():
            exit()
        if APP_START and not PAUSE:
            if is_correct_window():
                spam_key()

            else:
                log("no active window")

        time.sleep(0.1)
except KeyboardInterrupt:
    exit(1)
