class CustomException(Exception):
    message = "Unknown Error Occurred"
    status = 404

    def __init__(self, message: str = None, status: int = None):
        if message:
            self.message = message
        if status:
            self.status = status


class PermissionDeniedException(CustomException):
    status = 403
    message = "Not Enough Permissions"


class CredentialsInvalidException(CustomException):
    message = "Credentials Invalid"
    status = 401


class FileNotFound(CustomException):
    message = "File not found"


class FileUpload(CustomException):
    message = "Failed to Upload File(s)"


class CannotDeleteNotification(CustomException):
    status = 403
    message = "Cannot Delete Notification"


class PDFGenerationFail(CustomException):
    message = "Failed to generate pdf"
