# (C) British Crown Copyright 2023-2025, Met Office.
# Please see LICENSE.md for license details.

"""
A dummy QC plugin for development
"""

from compliance_checker.base import BaseCheck, BaseNCCheck, Result


class DummyCheck(BaseNCCheck):
    """
    Dummy checker class
    """

    register_checker = True
    name = 'dummy'

    __cache = {
        'dummy_cache': None
    }

    def __init__(self, **kwargs):
        super(DummyCheck, self).__init__()
        self.__messages = []
        self.__cache['dummy_cache'] = kwargs['config']['dummy_cache']

    def setup(self, netcdf_file):
        pass

    @property
    def passed(self):
        return self.__messages == []

    @property
    def error_messages(self):
        return self.__messages

    @classmethod
    def _make_result(cls, level, score, out_of, name, messages):
        return Result(level, (score, out_of), name, messages)

    def _add_error_message(self, message):
        self.__messages.append(message)

    def check_dummy_validator(self, netcdf_file):
        """
        Dummy validation method

        Parameters
        ----------
        netcdf_file : netCDF4.Dataset
            an open netCDF file

        Returns
        -------
        compliance_checker.base.Result
            container with check's results
        """

        out_of = 1
        self.__messages = []

        try:
            netcdf_file.getncattr('foo')
        except AttributeError as e:
            self._add_error_message(str(e))

        level = BaseCheck.HIGH
        score = 1 if self.passed else 0
        return self._make_result(level, score, out_of, 'Dummy validator', self.__messages)
