import tkinter as tk
import sys
import keyboard
from lib.Config import Config


def GUI(toggle_pause, kill_app):

    config = Config()
    window = tk.Tk()
    window.title("WoW Finger")
    window.protocol("WM_DELETE_WINDOW", kill_app)
    label = tk.Label(window, text="App is running you can play")
    label.pack(padx=20, pady=20)
    button_start = tk.Button(window, text="Start/Stop", command=toggle_pause)
    button_start.pack(padx=20, pady=20)

    label_pause_key = tk.Label(window, text="Pause Key")
    label_pause_key.pack(padx=20, pady=10)

    default_pause_key = config.pause_key
    entry_pause_key = tk.Entry(window)
    entry_pause_key.insert(0, default_pause_key)
    entry_pause_key.pack(padx=20, pady=10)

    def _set_pause_key():
        info_label.config(text="")
        key = entry_pause_key.get()

        try:
            if keyboard.key_to_scan_codes(key, True):
                config.set_pause_key(key)
        except ValueError as error_msg:
            info_label.config(text=error_msg)

    button_set = tk.Button(window, text="Set hotkey to PAUSE", command=_set_pause_key)
    button_set.pack(padx=20, pady=10)
    info_label = tk.Label(window, text="")
    info_label.pack(padx=20, pady=10)

    window.mainloop()
