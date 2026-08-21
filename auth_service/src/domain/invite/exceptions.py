class InviteNotFound(Exception):
    def __init__(self):
        super().__init__("Email doesn't have invites.")

class TooManyAttempts(Exception):
    def __init__(self):
        super().__init__("Too many code verification attempts.")

class InvalidOrExpiredCode(Exception):
    def __init__(self):
        super().__init__("Invalid or expired verification code.")

class InviteAlreadyUsed(Exception):
    def __init__(self):
        super().__init__("Invite already used.")