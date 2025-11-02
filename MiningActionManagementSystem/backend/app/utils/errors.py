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


class FileUpload(CustomException):
    message = "Failed to Upload File(s)"


class FileNotFound(CustomException):
    message = "File not found"
