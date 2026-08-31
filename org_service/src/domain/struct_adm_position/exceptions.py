class InvalidRequestStructAdmPosition(Exception):
    def __init__(self):
        super().__init__("Invalid request input data.")
