class UserNotFound(Exception):
    def __init__(self, message: str = ""):
        Exception.__init__(self, message)
        self.message = message


class FilmNotFound(Exception):
    def __init__(self, message: str = ""):
        Exception.__init__(self, message)
        self.message = message
