# (C) British Crown Copyright 2016-2021, Met Office.
# Please see LICENSE.rst for license details.
""" Exception classes to distinguish between different
metadata-related errors.
"""


class DaoConnectionException(Exception):
    """ Exception raised for dao connection problems. """

    def __init__(self, msg):
        super(DaoConnectionException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class DaoMetadataException(Exception):
    """ Exception raised for metadata issues we can't resolve that
    would result in invalid CIM documents (such as a simulation with
    multiple calendars).
    """

    def __init__(self, msg):
        super(DaoMetadataException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class DaoContractException(Exception):
    """ Exception raised if a dao breaches the contract to supply the
    metadata required to create a valid CIM element with pyesdoc.
    """

    def __init__(self, msg):
        super(DaoContractException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class DaoInvalidInputException(Exception):
    """ Exception raised for invalid/missing parameter input. """

    def __init__(self, msg):
        super(DaoInvalidInputException, self).__init__(msg)
        self.msg = msg

    def __str__(self):
        self.msg = "DaoInvalidInputException: %s" % self.msg
        return repr(self.msg)
