from logging import exception


class Error(Exception):
    """Base class for other exceptions"""

    pass


class InvalidDataDirectoryError(Error):
    """Raised when command line data directory path doesn't exist"""

    pass


class UnequalNumberOfDataFiles(Error):
    """
    Raised when there are unequal number of files in the relevant data
    data directories. Namely, datahunt, iaa, and schema
    """

    pass
