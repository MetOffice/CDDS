# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
import enum
import logging
import os

from cdds_common.common.io import read_json


class ProducibleState(enum.Enum):
    """
    Enum to specify the possible state if a variable is
    producible, not producible or unknown
    """
    PRODUCE = 1
    NOT_PRODUCE = 2
    UNKNOWN = 3

    @staticmethod
    def to_variables_data_value(state):
        """
        Convert the given state to the corresponding represented value in the
        variables data file.

        Parameters
        ----------
        state: :class: `cdds_prepare.mapping_status.ProducibleState`
            state that should be convert to the value that will be stored in
            the variables data file

        Returns
        -------
        : :class: `string`
            yes if producible, no if not and 'unknown' if unknown
        """
        if state == ProducibleState.PRODUCE:
            return 'yes'
        elif state == ProducibleState.NOT_PRODUCE:
            return 'no'
        else:
            return 'unknown'


class MappingStatus(object):
    """
    Singleton to avoid multiple loading of the mapping_status_data.json
    """

    MAPPING_STATUS_FILE = 'mapping_status_data.json'
    KEY_FORMAT = '{}/{}'

    _instance = None

    @staticmethod
    def get_instance():
        if MappingStatus._instance is None:
            MappingStatus()
        return MappingStatus._instance

    def __init__(self):
        if self._instance is not None:
            raise Exception(
                'Class is a singleton and can not initialised twice!'
            )

        self._mappings = self._load_mappings()
        MappingStatus._instance = self

    def _load_mappings(self):
        """
        Load the mappings from the mapping_status_data.json.

        Returns
        -------
        :class: :dict:
            Returns the mapping data <mip_table/variable : plan>
        """
        cdds_directory = os.path.dirname(os.path.realpath(__file__))
        data_file = os.path.join(cdds_directory, self.MAPPING_STATUS_FILE)
        return read_json(data_file)

    def producible(self, variable_name, mip_table):
        """
        Checks if a variable in the given mip table can be produced
        or not. Therefore, the mapping_status_data.json is used
        as reference.

        Parameters
        ----------
        variable_name: :class: `string`
            name of the variable
        mip_table: :class: `string`
            corresponding mip table name

        Returns
        -------
        :class: `cdds_prepare.mapping_status.ProducibleState`
            if the variable is producible or not
        """
        key = self.KEY_FORMAT.format(mip_table, variable_name)
        if key in list(self._mappings.keys()):
            value = self._mappings[key]
            if value == 'do-not-produce':
                return ProducibleState.NOT_PRODUCE
            return ProducibleState.PRODUCE
        else:
            logger = logging.getLogger(__name__)
            logger.debug(('Cannot determine if {} is producible or not. '
                          'So, hope the best.').format(key))
            return ProducibleState.UNKNOWN
