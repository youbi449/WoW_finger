import tkinter as tk
import sys

def Gui(start_app, stop_app):
    def on_closing():
        sys.exit()
    window = tk.Tk()
    window.title("WoW Finger")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    label = tk.Label(window, text="App is running you can play")
    label.pack(padx=20, pady=20)
    button_start = tk.Button(window, text="Start", command=start_app)
    button_start.pack(padx=20, pady=20)
    button_stop = tk.Button(window, text="Stop", command=stop_app)
    button_stop.pack(padx=20, pady=20)
    window.mainloop()
