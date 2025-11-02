class CustomException(Exception):
    message = "Unknown Error Occurred"
    status = 404

    def __init__(self, message: str = None, status: int = None):
        if message:
            self.message = message
        if status:
            self.status = status


class PermissionDeniedException(CustomException):
    message = "Not Enough Permissions"


class CredentialsInvalidException(CustomException):
    message = "Credentials Invalid"


class AlreadyExistsException(CustomException):
    message = "Already Exists"
    status = 409


class NotFoundException(CustomException):
    message = "Not Found"
    status = 404
