import tkinter as tk
import logging
import threading
import queue

class WebOverlay:
    def __init__(self, config, toggle_pause_callback=None):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.window = None
        self.is_active = False
        self.update_queue = queue.Queue()
        self.toggle_pause_callback = toggle_pause_callback
        
    def _create_window(self):
        """Create the overlay window"""
        try:
            # Create main window
            self.window = tk.Tk()
            self.window.title("Status")
            
            # Configure window properties
            self.window.attributes('-alpha', 0.8)  # Set transparency
            self.window.attributes('-topmost', True)  # Keep on top
            self.window.overrideredirect(True)  # Remove window decorations
            
            # Set window position and size
            self.window.geometry(f"80x40+{self.config.overlay_position_x}+{self.config.overlay_position_y}")
            
            # Create status label
            self.status_label = tk.Label(
                self.window,
                text="OFF",
                font=("Arial", self.config.overlay_font_size, "bold"),
                fg="red",
                bg="black",
                width=4,
                height=1
            )
            self.status_label.pack(expand=True, fill='both')
            
            # Add click event if callback is provided
            if self.toggle_pause_callback:
                self.status_label.bind('<Button-1>', lambda e: self.toggle_pause_callback())
            
            # Configure update checking
            self.window.after(100, self._check_updates)
            
            self.logger.info("Overlay window created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create overlay window: {e}", exc_info=True)
            raise
    
    def _check_updates(self):
        """Check for status updates"""
        try:
            try:
                is_active = self.update_queue.get_nowait()
                self.status_label.config(
                    text="ON" if is_active else "OFF",
                    fg="#00ff00" if is_active else "red"
                )
            except queue.Empty:
                pass
            
            if self.window:
                self.window.after(100, self._check_updates)
                
        except Exception as e:
            self.logger.error(f"Error checking updates: {e}")
    
    def start(self):
        """Start the overlay window"""
        try:
            self._create_window()
            self.window.mainloop()
            
        except Exception as e:
            self.logger.error(f"Failed to start overlay: {e}", exc_info=True)
            raise
    
    def update_status(self, is_active):
        """Update the overlay status"""
        try:
            if self.is_active != is_active:
                self.is_active = is_active
                self.update_queue.put(is_active)
                self.logger.debug(f"Status update queued: {'ON' if is_active else 'OFF'}")
        except Exception as e:
            self.logger.error(f"Error updating status: {e}")
    
    def destroy(self):
        """Destroy the overlay window"""
        try:
            if self.window:
                self.window.destroy()
                self.window = None
                self.logger.info("Overlay window destroyed")
        except Exception as e:
            self.logger.error(f"Error destroying overlay: {e}") 