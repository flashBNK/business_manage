class InvalidRequestStructAdmPosition(Exception):
    def __init__(self):
        super().__init__("Invalid request input data.")


class StructAdmPositionNotFound(Exception):
    def __init__(self):
        super().__init__("StructAdmPosition not found.")


class StructAdmPositionIsUsed(Exception):
    def __init__(self, position_name: str):
        super().__init__(f"Position {position_name} is used in StructAmdPosition.")
