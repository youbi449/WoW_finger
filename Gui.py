import tkinter as tk


def Gui(start_app, stop_app):
    window = tk.Tk()
    window.title("App Status")
    label = tk.Label(window, text="App is running you can play")
    label.pack(padx=20, pady=20)
    button_start = tk.Button(window, text="Start", command=start_app)
    button_start.pack(padx=20, pady=20)
    button_stop = tk.Button(window, text="Stop", command=stop_app)
    button_stop.pack(padx=20, pady=20)
    window.mainloop()
