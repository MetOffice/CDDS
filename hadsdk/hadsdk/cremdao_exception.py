# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
Exception classes to distinguish between different metadata-related errors.
"""


class CremZeroRecordsException(Exception):
    """
    Exception raised for problem caused by no records retrieved.
    """

    def __init__(self, msg):
        super(CremZeroRecordsException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class CremOneRecordException(Exception):
    """
    Exception raised for problem caused by not retrieving just one record.
    """

    def __init__(self, msg):
        super(CremOneRecordException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class CremInvalidSQLException(Exception):
    """
    Exception raised for invalid SQL problems.
    """

    def __init__(self, msg):
        super(CremInvalidSQLException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class CremInvalidInputException(Exception):
    """
    Exception raised for invalid/missing parameter input.
    """

    def __init__(self, msg):
        super(CremInvalidInputException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class CremMetadataException(Exception):
    """
    Exception raised for metadata issues we can't resolve.
    """

    def __init__(self, msg):
        super(CremMetadataException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
