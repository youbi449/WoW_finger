from .Observable import Observable
import keyboard as k


class Config(Observable):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):  # Ensure __init__ is only called once
            super().__init__()
            self.pause_key = None
            self.pause_key_code = None
            self.get_pause_key()
            self.initialized = True

    def set_pause_key(self, key):
        print(f"{key} ")
        self.pause_key = key
        self.pause_key_code = k.key_to_scan_codes(key, True)
        self.update_config("PAUSE_KEY", key)

    def get_pause_key(self):
        # try to get the pause key from the config file
        try:
            with open("config.ini", "r") as config_file:
                for line in config_file:
                    if line.startswith("PAUSE_KEY"):
                        self.pause_key_code = k.key_to_scan_codes(
                            line.strip().split("=")[1], True
                        )[0]
                        self.pause_key = line.strip().split("=")[1]
                        break
                else:
                    self.pause_key_code = None
        except FileNotFoundError:
            self.pause_key_code = None

    def update_config(self, settings_name, settings_value):
        try:
            with open("config.ini", "r+") as c:
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
        except FileNotFoundError:
            with open("config.ini", "w") as c:
                c.write(f"{settings_name}={settings_value}\n")
