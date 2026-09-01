class InvalidRequestUsersPosition(Exception):
    def __init__(self):
        super().__init__("Invalid request input data.")


class UsersPositionNotFound(Exception):
    def __init__(self):
        super().__init__("Users position not found.")
