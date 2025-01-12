from .Observable import Observable
import keyboard as k
import os
import sys


class Config(Observable):
    """
    Configuration class for WoW Finger application.
    Manages application settings and configuration persistence.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls)
        return cls._instance

    def __init__(self, app_path=None):
        if not hasattr(self, "initialized"):
            super().__init__()
            self.app_path = app_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.config_path = os.path.join(self.app_path, "config.ini")
            # Fixed pause key combination: CTRL + F1
            self.pause_key = "ctrl+f1"
            self.pause_key_code = k.key_to_scan_codes('f1', True)[0]  # We'll check for CTRL in the app logic
            self.initialized = True

    def get_pause_key(self):
        try:
            with open(self.config_path, "r") as config_file:
                for line in config_file:
                    if line.startswith("PAUSE_KEY"):
                        key = line.strip().split("=")[1]
                        self.pause_key = key
                        try:
                            self.pause_key_code = k.key_to_scan_codes(key, True)[0]
                        except:
                            self.pause_key_code = None
                        break
                else:
                    self.pause_key_code = None
                    self.pause_key = "p"  # Default key
                    self.update_config("PAUSE_KEY", "p")
        except FileNotFoundError:
            self.pause_key_code = None
            self.pause_key = "p"  # Default key
            self.update_config("PAUSE_KEY", "p")

    def update_config(self, settings_name, settings_value):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r+") as c:
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
            else:
                with open(self.config_path, "w") as c:
                    c.write(f"{settings_name}={settings_value}\n")
        except Exception as e:
            print(f"Error updating config: {e}")
            # Continue without config
