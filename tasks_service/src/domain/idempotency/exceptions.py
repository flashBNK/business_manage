class IdempotencyConflict(Exception):
    def __init__(self):
        super().__init__("Bad Idempotency code.")
