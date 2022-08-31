# (C) British Crown Copyright 2022, Met Office.
# Please see LICENSE.rst for license details.
import logging
from collections import defaultdict

from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugins import PluginStore


class UserDefinedVariable(object):
    """
    Class to hold information on a user requested variable built from
    mip tables. It is designed to have close similarity to the
    DataRequestVariable Class from hadsdk.
    """

    def __init__(self, mip_table, var_name, mip_table_dir, stream=None):
        """
        Construct an object representing a variable from given
        mip tables, based on its |MIP| table and
        |MIP requested variable| name.

        Parameters
        ----------
        mip_table : str, optional
            |MIP table| for the variable.
        var_name : str, optional
            |MIP requested variable name.
        mip_table_dir : str
            Directory containing Mip tables
        """

        self.mip_table = mip_table
        self.var_name = var_name
        self.stream = stream
        self.mt = UserMipTables(mip_table_dir)
        self.var_dict = self.mt.get_variable_meta(mip_table, var_name)
        self.var_dict['mip_table'] = self.mip_table

        self._set_attributes_from_variable()

    def _set_attributes_from_variable(self):
        # Set attributes from the given mip table
        self.cell_measures = self.var_dict['cell_measures']
        self.cell_methods = self.var_dict['cell_methods']
        self.comment = self.var_dict['comment']
        self.description = self.var_dict['comment']
        self.dimensions = self.var_dict['dimensions'].split()
        self.frequency = self.var_dict['frequency']
        self.long_name = self.var_dict['long_name']
        self.modeling_realm = self.var_dict['modeling_realm']
        self.output_variable_name = self.var_name
        self.positive = _blank_to_none(self.var_dict['positive'])
        self.standard_name = self.var_dict['standard_name']
        self.type = self.var_dict['type']
        self.units = self.var_dict['units']
        self.variable_name = self.var_name


def _blank_to_none(value):
    result = value
    if value == '':
        result = None
    return result


def validate_variable_list(mt, variables_file, mip_era):
    """
    Check that the custom requested variables exist in the mip tables

    Parameters
    ----------
    mt : cdds.common.mip_tables.UserMipTables
        Object holding information from the mip tables

    variables_file : str
        Path to the list of user requested variables

    mip_era : str
        Mip era

    RETURNS
    -------
    variable_list : list
        List of variables that are confirmed to be in the Mip Tables.

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


def list_all_variables(variables_file, mip_table_path, mip_era):
    """
    Build a list of all the variables from the mip tables.

    Parameters
    ----------
    variables_file : str
        path to the list of user provided requested variables

    mip_table_path : str
        path to the mip tables

    mip_era : str
        Mip era

    RETURNS
    -------
    variable_list_new : dict
        Dictionary containing each requested variabled as a UserDefinedVariable
    """

    mt = UserMipTables(mip_table_path)

    variables_list = validate_variable_list(mt, variables_file, mip_era)

    variable_list_new = defaultdict(dict)

    for table, variable, stream in variables_list:
        variable_list_new[table][variable] = UserDefinedVariable(table, variable, mip_table_path, stream)

    return dict(variable_list_new)
