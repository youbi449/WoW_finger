from lib.Config import Config
import pygetwindow as gw
import time
import keyboard as k
import locale
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import threading
from lib.GUI import GUI
from lib.WebOverlay import WebOverlay
import logging
import sys
import os
import ctypes
from ctypes import wintypes
import win32gui
import win32con
import win32api
import multiprocessing

# Define keyboard layout constants
QWERTY_LAYOUT_ID = 0x0409  # US English QWERTY layout ID

FORBIDDEN_KEYS = [17, 30, 31, 32, 57, 91, 28, 1]  # w, a, s, d, space, windows keycodes
WINDOW_ALLOWED = ["World of Warcraft"]
DELAY_BETWEEN_SPAM = 0.1  # Reduced from 0.2 to 0.1 seconds for faster spam

def set_keyboard_layout():
    """
    Set keyboard layout to US QWERTY for the current thread only.
    This ensures consistent key mapping without affecting the system-wide layout.
    """
    try:
        # Get the current thread ID
        thread_id = win32api.GetCurrentThreadId()
        
        # Load the US English (QWERTY) keyboard layout
        layout = win32api.LoadKeyboardLayout("00000409", win32con.KLF_ACTIVATE)
        
        # Set the keyboard layout for the current thread only
        user32 = ctypes.WinDLL('user32', use_last_error=True)
        result = user32.ActivateKeyboardLayout(layout, 0)
        
        # Set the input locale for the current thread
        if not user32.SetThreadInputLocale(layout):
            raise ctypes.WinError(ctypes.get_last_error())
            
        return True
    except Exception as e:
        logging.error(f"Failed to set keyboard layout: {e}")
        return False

class App:
    """
    Main application class for WoW Finger.
    Handles keyboard events and window management for World of Warcraft automation.
    Uses thread-local QWERTY layout for consistent key mapping while preserving system layout.
    """
    def __init__(self, forbidden_keys, delay):
        # Set keyboard layout for current thread only
        if not set_keyboard_layout():
            logging.warning("Failed to set keyboard layout for current thread. Key mapping might be inconsistent.")

        # Get the application path
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))
            
        # Setup logging with correct path
        log_path = os.path.join(self.application_path, 'wow_finger.log')
        logging.basicConfig(
            filename=log_path,
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(module)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing WoW Finger application")
        self.logger.info(f"Application path: {self.application_path}")

        # Core components initialization
        self.config = Config(self.application_path)
        self.PAUSE = True
        self.window_allowed = WINDOW_ALLOWED
        self.forbidden_keys = forbidden_keys
        self.DELAY_BETWEEN_SPAM = delay
        self.key_pressed = None
        
        # Initialize status overlay
        try:
            self.logger.debug("Creating status overlay...")
            self.overlay = WebOverlay(self.config)
            
            # Start overlay in a separate thread
            self.overlay_thread = threading.Thread(
                target=self.overlay.start,
                daemon=True
            )
            self.overlay_thread.start()
            self.logger.info("Status overlay initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize status overlay: {e}", exc_info=True)
            self.overlay = None
        
        # Start GUI in separate thread
        try:
            self.gui_thread = threading.Thread(
                target=GUI, 
                args=(self.toggle_pause, self.kill_app), 
                daemon=True
            )
            self.gui_thread.start()
            self.logger.info("GUI thread started successfully")
        except Exception as e:
            self.logger.error(f"Failed to start GUI thread: {str(e)}")
            raise

    def kill_app(self):
        """Safely terminate the application"""
        try:
            self.logger.info("Shutting down application")
            self.PAUSE = True
            if self.overlay:
                self.overlay.destroy()
            k.unhook_all()
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {str(e)}")
            sys.exit(1)

    def toggle_pause(self):
        """Toggle the pause state of the application"""
        try:
            # Toggle state
            self.PAUSE = not self.PAUSE
            state = "Paused" if self.PAUSE else "Unpaused"
            self.logger.info(f"Application state changed to: {state}")
            
            # Update overlay
            if self.overlay:
                is_active = not self.PAUSE  # When PAUSE is False, app is active (ON)
                self.logger.debug(f"Setting overlay to: {'ON' if is_active else 'OFF'}")
                self.overlay.update_status(is_active)
                self.logger.debug("Overlay update completed")
        except Exception as e:
            self.logger.error(f"Error in toggle_pause: {str(e)}", exc_info=True)

    def on_action(self, e):
        """Handle keyboard events"""
        try:
            if e.event_type == KEY_DOWN:
                self.on_key_pressed((e.scan_code, e.name))
            elif e.event_type == KEY_UP:
                self.on_key_released((e.scan_code, e.name))
        except Exception as e:
            self.logger.error(f"Error in keyboard event handler: {str(e)}")

    def on_key_pressed(self, key):
        """
        Handle key press events.
        Manages pause toggle with CTRL + F1 and key spam functionality.
        """
        try:
            key_code, key_name = key
            
            # Check for CTRL + F1 combination first, regardless of window
            if key_code == self.config.pause_key_code and k.is_pressed('ctrl'):
                self.logger.debug("CTRL + F1 detected, toggling pause state")
                self.toggle_pause()
                return

            # Other key checks only if in correct window
            if not self.is_correct_window():
                return

            if (
                key_code not in self.forbidden_keys
                and not k.is_modifier(key_code)
                and not self.PAUSE
                and self.key_pressed != key
            ):
                self.key_pressed = key
                self.logger.debug(f"Key pressed: {key}")
        except Exception as e:
            self.logger.error(f"Error handling key press: {str(e)}")

    def on_key_released(self, key):
        """Handle key release events"""
        try:
            if not k.is_pressed(key[0]) and self.key_pressed == key:
                self.key_pressed = None
                self.logger.debug(f"Key released: {key}")
        except Exception as e:
            self.logger.error(f"Error handling key release: {str(e)}")

    def process_keys(self):
        """
        Process active keys and trigger actions.
        Continuously sends key events while the key is held down.
        """
        try:
            if not self.PAUSE and self.is_correct_window() and self.key_pressed is not None:
                self.spam_key(self.key_pressed)
        except Exception as e:
            self.logger.error(f"Error processing keys: {str(e)}")
            
    def spam_key(self, key_info):
        """
        Handles the key spamming logic with improved timing and safety checks.
        
        Args:
            key_info (tuple): Tuple containing (scan_code, key_name)
        """
        if key_info is None:
            return

        try:
            key_name = key_info[1]
            
            # Verify the key is still being held down
            if not k.is_pressed(key_name):
                self.key_pressed = None
                return
                
            # Send the key event
            self.send_key(key_info)
            
            # Minimal delay to prevent system overload
            time.sleep(self.DELAY_BETWEEN_SPAM)
            
        except Exception as e:
            self.logger.error(f"Error in spam_key: {str(e)}")
            self.key_pressed = None  # Reset on error

    def send_key(self, key_info):
        """
        Sends a keyboard event with improved error handling and QWERTY layout compatibility.
        Uses scan codes to ensure consistent key mapping regardless of physical keyboard layout.
        
        Args:
            key_info (tuple): Tuple containing (scan_code, key_name)
        """
        if key_info is None:
            return

        try:
            scan_code = key_info[0]
            
            # Send the key event using scan code for layout independence
            k.send(scan_code, do_press=True, do_release=True)
            self.logger.debug(f"Sending key with scan code: {scan_code}")
            
        except Exception as e:
            self.logger.error(f"Error sending key event: {str(e)}")
            self.key_pressed = None  # Reset key state on error

    def start(self):
        """Start the application main loop"""
        self.logger.info("Starting application main loop")
        try:
            k.hook(self.on_action)
            while True:
                if not self.gui_thread.is_alive():
                    self.logger.warning("GUI thread terminated, shutting down")
                    self.kill_app()
                
                self.process_keys()
                time.sleep(self.DELAY_BETWEEN_SPAM)
        except Exception as e:
            self.logger.critical(f"Critical error in main loop: {str(e)}")
            self.kill_app()

    def is_correct_window(self):
        """Check if the active window is World of Warcraft"""
        try:
            active_window = gw.getActiveWindow()
            is_correct = active_window and active_window.title in self.window_allowed
            if not is_correct and self.key_pressed is not None:
                self.key_pressed = None
                self.logger.debug("Key pressed reset due to window change")
            return is_correct
        except Exception as e:
            self.logger.error(f"Error checking window: {str(e)}")
            return False

def is_admin():
    """Check if the program is running with administrator privileges"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if __name__ == "__main__":
    try:
        if not is_admin():
            logging.warning("Application needs administrator privileges to function properly")
            # Re-run the program with admin rights
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
            
        app = App(forbidden_keys=FORBIDDEN_KEYS, delay=DELAY_BETWEEN_SPAM)
        app.start()
    except Exception as e:
        logging.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)
