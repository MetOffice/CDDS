# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`variables` module contains the code required to handle the
information from the |requested variables list|.
"""
from collections import defaultdict
import os

from cdds.common import validate_checksum
from mip_convert.configuration.json_config import JSONConfig


class RequestedVariablesList(JSONConfig):
    """
    Store the information about the |requested variables list|.
    """
    ALLOWED_ATTRIBUTES = [
        'checksum', 'experiment_id', 'history',
        'metadata', 'mip', 'model_id', 'model_type',
        'production_info', 'requested_variables', 'status',
        'suite_branch', 'suite_id', 'suite_revision']

    def __init__(self, read_path):
        """
        Parameters
        ----------
        read_path: string
            The full path to the |requested variables list|
        """
        super(RequestedVariablesList, self).__init__(read_path)
        self._validate_checksum()
        # Is this too fragile?
        self.mip_era = os.path.basename(read_path).split('_')[0]
        self._add_attributes()

    def _validate_checksum(self):
        validate_checksum(self.config)

    def _add_attributes(self):
        for attribute in RequestedVariablesList.ALLOWED_ATTRIBUTES:
            value = None
            if attribute in self.config:
                value = self.config[attribute]
            setattr(self, attribute, value)

    @property
    def active_variables(self):
        """
        list: the list of variable dicts for variables that are active.
        """
        active_variables = []
        for variable in self.requested_variables:
            if variable['active']:
                self.logger.debug(
                    '"{miptable}_{label}" is active'.format(**variable))
                active_variables += [variable]
        return active_variables

    @property
    def active_variables_by_mip_table(self):
        """
        dict: The active |MIP requested variables| by
        |MIP table identifier|.
        """
        active_variables = defaultdict(list)
        for variable in self.requested_variables:
            variable_name = variable['label']
            mip_table_id = variable['miptable']
            if "/" in variable["stream"]:
                stream_id, substream = variable["stream"].split("/")
            else:
                stream_id = variable["stream"]
                substream = None
            self.logger.debug('Checking whether "{}_{}" is active'
                              ''.format(mip_table_id, variable_name))
            if variable['active']:
                self.logger.debug('"{}_{}" is active'
                                  ''.format(mip_table_id, variable_name))
                active_variables[mip_table_id].append((variable_name, stream_id, substream))
        return active_variables

    def get_dimensions(self, variable_id, mip_table_id):
        """
        """
        var_list = [
            v1 for v1 in self.requested_variables
            if v1['label'] == variable_id and
            v1['miptable'] == mip_table_id]
        try:
            var_info = var_list[0]
        except IndexError:
            return None
        return var_info['dimensions']

    def get_frequency(self, variable_id, mip_table_id):
        """
        """
        var_list = [
            v1 for v1 in self.requested_variables
            if v1['label'] == variable_id and
            v1['miptable'] == mip_table_id]
        try:
            var_info = var_list[0]
        except IndexError:
            return None
        return var_info['frequency']
