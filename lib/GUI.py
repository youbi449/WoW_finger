import tkinter as tk
import sys
from lib.Config import Config


def GUI(toggle_pause, kill_app):
    """
    Create and manage the graphical user interface for the WoW Finger application.
    Displays the application status and controls for pausing/stopping the application.
    
    Args:
        toggle_pause (function): Callback function to toggle the pause state
        kill_app (function): Callback function to properly terminate the application
    """
    config = Config()
    window = tk.Tk()
    window.title("WoW Finger")
    window.geometry("300x250")  # Set a fixed size for better appearance
    window.resizable(False, False)  # Prevent window resizing
    
    # Configure window to stay on top
    window.attributes('-topmost', True)
    
    # Add some padding and style
    main_frame = tk.Frame(window, padx=10, pady=10)
    main_frame.pack(expand=True, fill='both')
    
    # Title with better styling
    title = tk.Label(main_frame, text="WoW Finger", font=("Arial", 16, "bold"))
    title.pack(pady=10)
    
    # Status label
    label = tk.Label(main_frame, text="Application is running", font=("Arial", 12))
    label.pack(pady=10)
    
    # Start/Stop button with better styling
    button_start = tk.Button(
        main_frame,
        text="Start/Stop (CTRL + F1)",
        command=toggle_pause,
        font=("Arial", 10),
        width=20,
        height=2
    )
    button_start.pack(pady=15)
    
    # Shortcut info
    pause_info = tk.Label(
        main_frame,
        text="Shortcut: CTRL + F1",
        font=("Arial", 10),
        fg="gray"
    )
    pause_info.pack(pady=5)
    
    # Exit button
    exit_button = tk.Button(
        main_frame,
        text="Exit",
        command=kill_app,
        font=("Arial", 10),
        width=15
    )
    exit_button.pack(pady=10)
    
    # Handle window close button
    window.protocol("WM_DELETE_WINDOW", kill_app)
    
    # Center the window on screen
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')
    
    window.mainloop()
