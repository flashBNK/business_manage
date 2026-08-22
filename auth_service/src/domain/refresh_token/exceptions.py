class InvalidRefreshToken(Exception):
    def __init__(self):
        super().__init__("Refresh token is invalid or expired.")