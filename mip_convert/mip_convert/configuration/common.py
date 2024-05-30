# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
# pylint: disable = no-member
"""
The :mod:`configuration` module contains the configuration classes that
store the information read from the configuration files.
"""
import logging
from abc import ABCMeta, abstractmethod


class AbstractConfig(object, metaclass=ABCMeta):
    """
    Read configuration files.
    """

    def __init__(self, read_path):
        """
        Store the information read from the configuration file in the
        ``config`` attribute.

        :param read_path: the full path to the configuration file
        :type read_path: string
        """
        self.logger = logging.getLogger(__name__)
        if read_path is None:
            raise RuntimeError("Please provide the full path to the configuration file")
        self.read_path = read_path
        self.read(read_path=self.read_path)

    @abstractmethod
    def read(self, read_path):
        """
        Read the file.
        """
        pass


class ValidateConfigError(Exception):
    """
    Exception for use when there are problems validating the
    configuration files.
    """

    def __init__(self, msg):
        super(ValidateConfigError, self).__init__(msg)
        self.msg = msg
