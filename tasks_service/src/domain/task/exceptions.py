class ParticipantNotFound(Exception):
    def __init__(self):
        super().__init__("Participant not found.")


class ParticipantInactive(Exception):
    def __init__(self):
        super().__init__("Participant inactive.")


class ParticipantWrongCompany(Exception):
    def __init__(self):
        super().__init__("Participant wrong company.")


class TaskNotFound(Exception):
    def __init__(self):
        super().__init__("Task not found.")