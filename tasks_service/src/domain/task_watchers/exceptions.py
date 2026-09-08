class WatcherNotFound(Exception):
    def __init__(self):
        super().__init__("Watcher not found.")
