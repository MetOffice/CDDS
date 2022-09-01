# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`my_module` module contains the code required to [...].
"""


class ThisReasonError(Exception):
    """
    Exception for use when an exit code of 2 is required.
    """
    def __init__(self, msg):
        super(ThisReasonError, self).__init__(msg)
        self.msg = msg


class ThatReasonError(Exception):
    """
    Exception for use when an exit code of 3 is required.
    """
    def __init__(self, msg):
        super(ThatReasonError, self).__init__(msg)
        self.msg = msg


class AnotherReasonError(Exception):
    """
    Exception for use when an exit code of 4 is required.
    """
    def __init__(self, msg):
        super(AnotherReasonError, self).__init__(msg)
        self.msg = msg


def my_function(arguments):
    """
    Description of ``my_function``.

    Parameters
    ----------
    arguments: :class:`cdds.arguments.Arguments` object
        The arguments specific to the `my_script` script.

    Raises
    ------
    ThisReasonError
        If ``x`` is not equal to ``x-ray``.
    ThatReasonError
        If ``y`` is not equal to ``yankee``.
    AnotherReasonError
        If ``z`` is not equal to ``zulu``.
    """
    if arguments.x != 'x-ray':
        raise ThisReasonError('This is the reason')
    if arguments.y != 'yankee':
        raise ThatReasonError('That is the reason')
    if arguments.z != 'zulu':
        raise AnotherReasonError('Another reason')

    print('I am the output of "my_script"')
