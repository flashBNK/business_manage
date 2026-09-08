class AssigneesNotFound(Exception):
    def __init__(self):
        super().__init__("Assignees not found.")
