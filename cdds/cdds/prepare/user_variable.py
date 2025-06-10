# (C) British Crown Copyright 2022-2025, Met Office.
# Please see LICENSE.md for license details.
import logging
from collections import defaultdict
from typing import Dict, Tuple, List

from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugins import PluginStore


class UserDefinedVariable(object):
    """
    Class to hold information on a user requested variable built from mip tables.
    It is designed to have close similarity to the DataRequestVariable Class from
    cdds.prepare.data_request_interface.
    """

    def __init__(self, mip_table: str, var_name: str, mip_table_dir: str, stream: str = None) -> None:
        """
        Construct an object representing a variable from given mip tables,
        based on its |MIP| table and |MIP requested variable| name.

        :param mip_table: |MIP table| for the variable.
        :type mip_table: str
        :param var_name: |MIP requested variable name.
        :type var_name: str
        :param mip_table_dir: Directory containing Mip tables
        :type mip_table_dir: str
        :param stream: Only consider this stream (optional)
        :type stream: str
        """
        self.mip_table = mip_table
        self.var_name = var_name
        self.stream = stream
        self.mt = UserMipTables(mip_table_dir)
        self.var_dict = self.mt.get_variable_meta(mip_table, var_name)
        self.var_dict['mip_table'] = self.mip_table

        self._set_attributes_from_variable()

    def _set_attributes_from_variable(self) -> None:
        # Set attributes from the given mip table
        self.cell_measures = self.var_dict['cell_measures']
        self.cell_methods = self.var_dict['cell_methods']
        self.comment = self.var_dict['comment']
        self.description = self.var_dict['comment']
        self.dimensions = self.var_dict['dimensions'].split()
        self.frequency = self.var_dict['frequency']
        self.long_name = self.var_dict['long_name']
        self.modeling_realm = self.var_dict.get('modeling_realm', None)
        self.output_variable_name = self.var_name
        self.positive = _blank_to_none(self.var_dict['positive'])
        self.standard_name = self.var_dict['standard_name']
        self.type = self.var_dict['type']
        self.units = self.var_dict['units']
        self.variable_name = self.var_name


def _blank_to_none(value: str) -> str:
    result = value
    if value == '':
        result = None
    return result


def validate_variable_list(mt: UserMipTables, variables_file: str) -> List[Tuple[str, str, str]]:
    """
    Check that the custom requested variables exist in the mip tables

    :param mt: Object holding information from the mip tables
    :type mt: UserMipTables
    :param variables_file: Path to the list of user requested variables
    :type variables_file: str
    :return: List of variables that are confirmed to be in the Mip Tables.
        List of tuples: (MIP table, variable, stream/substream)
    :rtype: List[Tuple[str, str, str]
    """
    logger = logging.getLogger(__name__)

    with open(variables_file, 'r') as f:
        requested_variables = f.readlines()

    variable_list = []
    for var_str in requested_variables:
        if ':' in var_str:
            mip_table_variable, stream_substream = var_str.strip().split(':')
            mip_table, variable = mip_table_variable.split('/')
        else:
            stream_info = PluginStore.instance().get_plugin().stream_info()
            mip_table, variable = var_str.strip().split('/')
            stream_id, substream = stream_info.retrieve_stream_id(variable, mip_table)
            stream_substream = '{}/{}'.format(stream_id, substream) if substream is not None else stream_id

        if mip_table not in mt.tables:
            err = 'Requested Mip Table "{}" not found in given Mip Tables'.format(mip_table)
            logger.error(err)
            raise RuntimeError(err)

        if variable not in mt.get_variables(mip_table):
            err = 'Requested variable "{}" not found in the "{}" Mip Table'.format(variable, mip_table)
            logger.error(err)
            raise RuntimeError(err)

        variable_list.append((mip_table, variable, stream_substream,))

    return variable_list


def list_all_variables(variables_file: str, mip_table_path: str) -> Dict[str, Dict[str, UserDefinedVariable]]:
    """
    Build a list of all the variables from the mip tables.

    :param variables_file: path to the list of user provided requested variables
    :type variables_file: str
    :param mip_table_path: path to the mip tables
    :type mip_table_path: str
    :return: Dictionary containing each requested variabled as a UserDefinedVariable
    :rtype: Dict[str, Dict[str, UserDefinedVariable]]
    """
    mt = UserMipTables(mip_table_path)
    variables_list = validate_variable_list(mt, variables_file)

    variable_list_new: Dict[str, Dict[str, UserDefinedVariable]] = defaultdict(dict)
    for table, variable, stream in variables_list:
        variable_list_new[table][variable] = UserDefinedVariable(table, variable, mip_table_path, stream)

    return dict(variable_list_new)
