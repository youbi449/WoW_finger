from lib.Config import Config
import pygetwindow as gw
import time
import keyboard as k
import locale
from keyboard._keyboard_event import KEY_DOWN, KEY_UP
import threading
from lib.GUI import GUI
from winotify import Notification
import logging
import sys
import os
import ctypes

FORBIDDEN_KEYS = [17, 30, 31, 32, 57, 91, 28, 1]  # w, a, s, d, space, windows keycodes
WINDOW_ALLOWED = ["World of Warcraft"]
DELAY_BETWEEN_SPAM = 0.2

class App:
    """
    Main application class for WoW Finger.
    Handles keyboard events and window management for World of Warcraft automation.
    """
    def __init__(self, forbidden_keys, delay):
        # Get the application path
        if getattr(sys, 'frozen', False):
            self.application_path = os.path.dirname(sys.executable)
        else:
            self.application_path = os.path.dirname(os.path.abspath(__file__))
            
        # Setup logging with correct path
        log_path = os.path.join(self.application_path, 'wow_finger.log')
        logging.basicConfig(
            filename=log_path,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info("Initializing WoW Finger application")
        self.logger.info(f"Application path: {self.application_path}")

        # Core components initialization
        self.config = Config(self.application_path)  # Pass application path to Config
        self.PAUSE = True
        self.window_allowed = WINDOW_ALLOWED
        self.forbidden_keys = forbidden_keys
        self.DELAY_BETWEEN_SPAM = delay
        self.key_pressed = None
        
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
            k.unhook_all()
            sys.exit(0)
        except Exception as e:
            self.logger.error(f"Error during application shutdown: {str(e)}")
            sys.exit(1)

    def notif(self, msg):
        """Send a system notification using Windows notifications"""
        try:
            toast = Notification(
                app_id="WoW Finger",
                title="WoW Finger",
                msg=msg,
                duration="short"
            )
            toast.show()
            self.logger.debug(f"Notification sent: {msg}")
        except Exception as e:
            self.logger.warning(f"Failed to send notification: {str(e)}")

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

    def toggle_pause(self):
        """Toggle the pause state of the application"""
        self.PAUSE = not self.PAUSE
        state = "Paused" if self.PAUSE else "Unpaused"
        self.logger.info(f"Application state changed to: {state}")
        self.notif(state)

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
            if not self.is_correct_window():
                return

            # Check for CTRL + F1 combination
            if key_code == self.config.pause_key_code and k.is_pressed('ctrl'):
                self.toggle_pause()
            elif (
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
        """Process active keys and trigger actions"""
        try:
            if not self.PAUSE and self.is_correct_window() and self.key_pressed is not None:
                self.logger.debug(f"Processing key: {self.key_pressed}")
                self.spam_key_if_needed(self.key_pressed)
        except Exception as e:
            self.logger.error(f"Error processing keys: {str(e)}")

    def spam_key_if_needed(self, kp):
        """Handle key spamming logic"""
        if kp is None:
            return

        try:
            for _ in range(5):
                if self.key_pressed != kp or self.PAUSE or not self.is_correct_window():
                    self.logger.debug(f"Stopping spam for key: {kp}")
                    break

                self.send_key(kp)
                time.sleep(self.DELAY_BETWEEN_SPAM)
        except Exception as e:
            self.logger.error(f"Error in key spam routine: {str(e)}")

    def send_key(self, kp):
        """
        Send a keyboard event using scan codes for better keyboard layout compatibility.
        Args:
            kp (tuple): Tuple containing (scan_code, key_name)
        """
        if kp is None:
            return

        try:
            scan_code = kp[0]
            self.logger.debug(f"Sending key scan code: {scan_code}")
            k.send(scan_code)
        except Exception as e:
            self.logger.error(f"Error sending key event: {str(e)}")

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
