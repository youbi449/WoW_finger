class Observable:
    def __init__(self):
        self._observers = {}

    def register_observer(self, var_name, callback):
        if var_name not in self._observers:
            self._observers[var_name] = []
        self._observers[var_name].append(callback)

    def notify_observers(self, var_name, value):
        if var_name in self._observers:
            for callback in self._observers[var_name]:
                callback(value)