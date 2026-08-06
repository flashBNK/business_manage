class UserNotFound(Exception):
    def __init__(self):
        super().__init__(f'User not found.')