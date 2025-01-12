import tkinter as tk
import sys
from lib.Config import Config


def GUI(toggle_pause, kill_app):
    """
    Create and manage the graphical user interface for the WoW Finger application.
    Displays the application status and controls for pausing/stopping the application.
    """
    config = Config()
    window = tk.Tk()
    window.title("WoW Finger")
    window.protocol("WM_DELETE_WINDOW", kill_app)
    label = tk.Label(window, text="App is running you can play")
    label.pack(padx=20, pady=20)
    button_start = tk.Button(window, text="Start/Stop", command=toggle_pause)
    button_start.pack(padx=20, pady=20)

    pause_info = tk.Label(window, text="Press CTRL + F1 to toggle pause", font=("Arial", 10, "bold"))
    pause_info.pack(padx=20, pady=10)

    window.mainloop()
