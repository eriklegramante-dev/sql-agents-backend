"""Domain errors for history persistence."""


class DeletedHistoryError(Exception):
    """
    Exception raised when saving a session whose history is deleted.
    """
