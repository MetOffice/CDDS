# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
Classes to support model output usage
"""
from mip_convert.config_manager import AbstractConfig


class AbstractDataSourceUser(AbstractConfig):
    """
    Abstract class containing common code for parsing the data_source
    section of the project config file
    """
    SECTION = 'data_source'

    @property
    def calendar(self):
        return self._get_from_section('calendar')

    @property
    def streamnames(self):
        return self._get_space_sep_list('streams')

    @property
    def runnames(self):
        return self._get_space_sep_list('runs')

    def _get_space_sep_list(self, option):
        return self._get_from_section(option).split()

    def _get_from_section(self, option):
        return self._project_config.get(self.SECTION, option)

    def _has_option(self, option):
        return self._project_config.has_option(self.SECTION, option)
