# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
Exceptions raised by accessing MASS
"""
from enum import Enum


class MassFailure(Enum):

    def __new__(cls, *args, **kwds):
        value = len(cls.__members__) + 1
        obj = object.__new__(cls)
        obj._value_ = value
        return obj

    def __init__(self, label='', code=None, description=None):
        self.label = label
        self.code = code
        self.description = description

    def get_message(self, command, stdout=None, stderr=None):
        command_str = ' '.join(command)
        message_template = '{} while running MASS command: "{}".\n{}'
        if stdout:
            message_template += '\n{}'.format(stdout)
        if stderr:
            message_template += '\n{}'.format(stderr)
        return message_template.format(self.label, command_str, self.description)

    NOT_EXIST_ERROR = (
        'Not Exist Error',
        2,
        'This could cause by a not existent mooseURI.'
    )
    USER_ERROR = (
        'User Error',
        2,
        'This could cause by a wrong mooseURI, a wrong password or insufficient permissions on a data set.'
    )
    SYSTEM_ERROR = (
        'System Error',
        3,
        'This could cause by a system outage or when the system times-out as a result of excessive load.'
    )
    CLIENT_ERROR = (
        'Client System Error',
        4,
        'An error in the client system external to MOOSE occurred, e.g. file I/O or format-conversion.'
    )
    ACCESS_ERROR = (
        'General Access Error',
        5,
        'The system is running, but general access, or the requested command-type has been temporarily disabled.'
    )
    DIR_ALREADY_EXIST_ERROR = (
        'Directory Already Exist Error',
        10,
        'This could cause by trying to create a directory that already exists.'
    )


class MassError(Exception):
    """
    Raised if errors occur when accessing MASS or processing MASS commands.
    """
    def __init__(self, mass_failure, command):
        super(MassError, self).__init__(mass_failure.get_message(command))
        self.msg = mass_failure.get_message(command)


class FileNotExistMassError(MassError):
    """
    Raised if errors occur when accessing a non existing MASS location.
    """
    def __init__(self, command):
        super(FileNotExistMassError, self).__init__(MassFailure.NOT_EXIST_ERROR, command)


class DirAlreadyExistMassError(MassError):
    """
    Raised if errors occur when trying to create an already existing directory
    """

    def __init__(self, command):
        super(DirAlreadyExistMassError, self).__init__(MassFailure.DIR_ALREADY_EXIST_ERROR, command)


class VariableArchivingError(Exception):
    pass
