class InboxEventNotFound(Exception):
    def __init__(self):
        super().__init__("Inbox event not found.")
