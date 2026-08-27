class MembersNotFound(Exception):
    def __init__(self):
        super().__init__("Members doesn't have user.")


class MemberAlreadyActivated(Exception):
    def __init__(self):
        super().__init__("Member already activated.")
