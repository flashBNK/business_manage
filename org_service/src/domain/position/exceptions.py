class PositionNotFound(Exception):
    def __init__(self):
        super().__init__("Position not found.")


class InvalidRequestPosition(Exception):
    def __init__(self):
        super().__init__("Invalid request input data.")
