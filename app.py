from lib.Config import Config
import pygetwindow as gw
import time
import keyboard as k
import locale
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import threading
from lib.GUI import GUI
from plyer import notification

import sys

FORBIDDEN_KEYS = [17, 30, 31, 32, 57, 91, 28, 1]  # w, a, s, d, space, windows keycodes
WINDOW_ALLOWED = ["World of Warcraft"]
FRENCH_SCANC = [16, 44]
DELAY_BETWEEN_SPAM = 0.2


class App:
    def __init__(self, forbidden_keys, delay):
        self.config = Config()
        self.PAUSE = True
        self.window_allowed = WINDOW_ALLOWED
        self.forbidden_keys = forbidden_keys
        self.DELAY_BETWEEN_SPAM = delay
        self.key_pressed = None
        self.keyboard_layout = locale.getlocale()[0]
        self.gui_thread = threading.Thread(
            target=GUI, args=(self.toggle_pause, self.kill_app), daemon=True
        )
        self.gui_thread.start()

    def kill_app(self):
        self.PAUSE = True
        k.unhook_all()
        sys.exit()

    def notif(self, msg):
        notification.notify(title="Wow Finger", message=msg, app_name="Wow Finger")

    def is_correct_window(self):
        active_window = gw.getActiveWindow()
        is_correct = active_window and active_window.title in self.window_allowed
        if not is_correct:
            self.key_pressed = None
        return is_correct

    def toggle_pause(self):
        self.PAUSE = not self.PAUSE
        self.notif("Paused" if self.PAUSE else "Unpaused")

    def is_key_forbidden(self, key):
        return key in self.forbidden_keys

    def on_action(self, e):

        if e.event_type == KEY_DOWN:
            self.on_key_pressed((e.scan_code, e.name.lower()))
        elif e.event_type == KEY_UP:
            self.on_key_released((e.scan_code, e.name.lower()))

    def on_key_pressed(self, key):
        key_code = key[0]
        if self.is_correct_window():
            if key_code == self.config.pause_key_code:
                self.toggle_pause()
            elif (
                key_code not in self.forbidden_keys
                and not k.is_modifier(key_code)
                and not self.PAUSE
                and self.key_pressed != key
            ):
                self.key_pressed = key

    def on_key_released(self, key):
        if not k.is_pressed(key[0]) and self.key_pressed == key:
            self.key_pressed = None

    def sync_keys(self):
        for i in list(self.key_pressed):
            if not k.is_pressed(i[0]):
                print("key not sync !")
                self.key_pressed.remove(i)
        return

    def start(self):
        print("App is running...")
        k.hook(self.on_action)
        while True:
            if not self.gui_thread.is_alive():
                print("GUI thread is not alive, exiting...")
                exit()
            self.process_keys()
            time.sleep(self.DELAY_BETWEEN_SPAM)

    def process_keys(self):
        if not self.PAUSE and self.is_correct_window() and self.key_pressed is not None:
            print(f"Processing key: {self.key_pressed}")
            self.spam_key_if_needed(self.key_pressed)

    def spam_key_if_needed(self, kp):
        if kp is None:
            return
        for _ in range(5):
            if self.key_pressed == kp and not self.PAUSE and self.is_correct_window():
                print(f"Spamming key: {kp}")
                self.send_key(kp)
            else:
                print(f"Stopping spam for key: {kp}")
                break
            time.sleep(self.DELAY_BETWEEN_SPAM)

    def send_key(self, kp):
        if kp is None:
            return
        if self.keyboard_layout == "fr_FR" and kp[0] in FRENCH_SCANC:
            print(f"Sending key (FR layout): {kp[1]}")
            k.send(kp[1])
        else:
            print(f"Sending key: {kp[0]}")
            k.send(kp[0])


if __name__ == "__main__":
    app = App(forbidden_keys=FORBIDDEN_KEYS, delay=DELAY_BETWEEN_SPAM)
    app.start()
