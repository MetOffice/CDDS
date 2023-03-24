# (C) British Crown Copyright 2017-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
Exceptions raised by CDDS convert
"""


class StreamError(Exception):
    """
    An error when dealing with the streams for a request.
    """
    pass


class ArgumentError(Exception):
    """
    An error in command line arguments.
    """
    pass


class SuiteCheckoutError(Exception):
    """
    Raised when there is an issue checking out a rose suite.
    """
    pass


class SuiteConfigMissingValueError(Exception):
    """
    Raised when a field in the rose-suite.conf file in the processing
    suite is not found.
    """
    pass


class SuiteSubmissionError(Exception):
    """
    Raised if there is an issue submitting a suite.
    """
    pass


class SuiteShutdownError(Exception):
    """
    Raised if there is an issue shutting a suite down.
    """
    pass


class ConcatenationDBError(Exception):
    """
    Raised if the concatenation database cannot be written.
    """
    pass


class SizingError(Exception):
    """
    Raised if "sizing" file cannot be produced to determine the CMOR
    file aggregation periods.
    """
    pass


class ConcatenationError(Exception):
    """
    Raised in the concatenation of multiple netCDF files fails.
    """
    pass


class WrapperEnvironmentError(Exception):
    """
    Raised in the MIP convert wrapper if an expected environment variable is
    not present.
    """
    pass


class WrapperMissingFilesError(Exception):
    """
    Raised if the wrapper processes no files when expecting to do work.
    """
    pass


class OrganiseEnvironmentError(Exception):
    """
    Raised in the concatenate organise files script if an expected environment
    variable is not present.
    """
    pass


class MipConvertWrapperDiskUsageError(Exception):
    """
    Raised in  the MIP convert wrapper if the usage of $TMPDIR space exceeds
    the amount requested.
    """
    pass


class OrganiseTransposeError(Exception):
    """
    Raised in the concatenate organise files script if the transposing of
    files and directories fails.
    """
    pass

class IncompatibleCalendarMode(Exception):
    """
    Raised if the currently loaded 'metomi.isodatetime.data.Calendar mode is not
    compatible.
    """
    pass
