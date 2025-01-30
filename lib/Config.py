from .Observable import Observable
import keyboard as k
import os
import sys
import configparser


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
            
            # Initialize configuration parser
            self.config = configparser.ConfigParser()
            
            # Default values
            self.pause_key = "f1"
            self.pause_key_code = k.key_to_scan_codes('f1', True)[0]
            
            # Overlay settings with defaults
            self.overlay_font_size = 20
            self.overlay_text_width = 4
            self.overlay_text_height = 1
            self.overlay_position_x = 10
            self.overlay_position_y = 10
            
            # Load configuration
            self.load_config()
            self.initialized = True

    def load_config(self):
        """Load all configuration settings from config.ini"""
        try:
            self.config.read(self.config_path)
            
            # Load General settings
            if 'General' in self.config:
                self.pause_key = self.config.get('General', 'PAUSE_KEY', fallback='f1')
                try:
                    self.pause_key_code = k.key_to_scan_codes(self.pause_key, True)[0]
                except:
                    self.pause_key_code = k.key_to_scan_codes('f1', True)[0]
            
            # Load Overlay settings
            if 'Overlay' in self.config:
                self.overlay_font_size = self.config.getint('Overlay', 'font_size', fallback=20)
                self.overlay_text_width = self.config.getint('Overlay', 'text_width', fallback=4)
                self.overlay_text_height = self.config.getint('Overlay', 'text_height', fallback=1)
                self.overlay_position_x = self.config.getint('Overlay', 'position_x', fallback=10)
                self.overlay_position_y = self.config.getint('Overlay', 'position_y', fallback=10)
            
            # Create config file if it doesn't exist
            if not os.path.exists(self.config_path):
                self.save_config()
                
        except Exception as e:
            print(f"Error loading config: {e}")
            # Continue with defaults

    def save_config(self):
        """Save all configuration settings to config.ini"""
        try:
            if not self.config.has_section('General'):
                self.config.add_section('General')
            if not self.config.has_section('Overlay'):
                self.config.add_section('Overlay')
            
            # Save General settings
            self.config.set('General', 'PAUSE_KEY', str(self.pause_key))
            
            # Save Overlay settings
            self.config.set('Overlay', 'font_size', str(self.overlay_font_size))
            self.config.set('Overlay', 'text_width', str(self.overlay_text_width))
            self.config.set('Overlay', 'text_height', str(self.overlay_text_height))
            self.config.set('Overlay', 'position_x', str(self.overlay_position_x))
            self.config.set('Overlay', 'position_y', str(self.overlay_position_y))
            
            with open(self.config_path, 'w') as configfile:
                self.config.write(configfile)
                
        except Exception as e:
            print(f"Error saving config: {e}")

    def update_config(self, section, key, value):
        """
        Update a specific configuration value
        
        Args:
            section (str): Configuration section name
            key (str): Configuration key
            value: Value to set
        """
        try:
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self.config.set(section, key, str(value))
            
            # Update instance variable if it exists
            var_name = f"{section.lower()}_{key.lower()}"
            if hasattr(self, var_name):
                setattr(self, var_name, value)
            
            self.save_config()
            
        except Exception as e:
            print(f"Error updating config: {e}")
