class TicketNotFound(Exception):
    def __init__(self):
        super().__init__("Ticket not found.")


class TooManyAttempts(Exception):
    def __init__(self):
        super().__init__("Too many code verification attempts.")


class InvalidOrExpiredTicket(Exception):
    def __init__(self):
        super().__init__("Invalid or expired verification ticket.")


class TicketAlreadyUsed(Exception):
    def __init__(self):
        super().__init__("Ticket already used.")
