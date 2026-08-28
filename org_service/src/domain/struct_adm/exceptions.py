class StructAdmNotFound(Exception):
    def __init__(self):
        super().__init__("StructAdm not found.")
