class InvalidToken(Exception):
    def __init__(self):
        super().__init__("Token is invalid.")


class TokenExpired(Exception):
    def __init__(self):
        super().__init__("Token has expired.")
