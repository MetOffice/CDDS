# (C) British Crown Copyright 2018-2023, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`variables` module contains the code required to determine the
|MIP requested variables| for the request.
"""
from collections import defaultdict
import logging
import os

from cdds.common.grids import retrieve_grid_info, grid_overrides
from cdds.common.plugins.plugins import PluginStore


def retrieve_variables_by_grid(requested_variables, mip_table_directory):
    """
    Return the |MIP requested variables| by grid.

    The |MIP requested variables| are returned as a dictionary, where
    the key is the grid and the value is a nested dictionary that can
    be written to a file via :mod:`configparser`, e.g. ``{section1:
    {option1: value1, option2: value2}, {section2: {}}``, where the
    section is ``stream_<stream_id>``, the option is the |MIP table|
    and the value is a space seperated list of
    |MIP requested variables|.

    Parameters
    ----------
    requested_variables: :class:`cdds.common.variables.RequestedVariablesList`
        The information from the |requested variables list|.
    mip_table_directory: str
        Location of MIP tables (used to identify MIP table name prefix)

    Returns
    -------
    : dict
        The |MIP requested variables| by grid.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)

    variables_by_grid = defaultdict(
        lambda: defaultdict(lambda: defaultdict(str)))
    active_variables = requested_variables.active_variables_by_mip_table
    for mip_table_id, variable_list in active_variables.items():
        for variable in variable_list:
            variable_name, stream_id, substream = variable
            grid_info = retrieve_grid_info(
                variable_name, mip_table_id, requested_variables.model_id, grid_overrides())
            if grid_info is None:
                logger.critical('No grid information available for "{}" for "{}"'
                                ''.format(variable_name, mip_table_id))
                continue
            if stream_id is None:
                logger.critical('No stream identifier available for "{}" for '
                                '"{}"'.format(variable_name, mip_table_id))
                continue
            section = 'stream_{}'.format(stream_id)
            # Still need to support substreams in MIP Convert.
            if substream is None:
                section = 'stream_{}'.format(stream_id)
            else:
                section = 'stream_{}_{}'.format(stream_id, substream)
                logger.debug('Updating grid information for substream "{}"'
                             ''.format(substream))
            grid_info = tuple(list(grid_info) + [substream])
            # Work out whether specific (e.g. CMIP6_Amon) tables are being used or generic (MIP_APmon)
            mip_table = identify_mip_table_name(requested_variables.mip_era, mip_table_directory, mip_table_id)
            if variables_by_grid[grid_info][section][mip_table]:
                variables_by_grid[grid_info][section][mip_table] += ' '
            variables_by_grid[grid_info][section][mip_table] += variable_name
    return variables_by_grid


def identify_mip_table_name(mip_era, mip_table_directory, mip_table_id, prefix=''):
    """
    Identify whether the MIP being used is a generic table (named MIP_XXX.json)
    or a specific one (named <MIP_ERA>_XXX.json) and return the corresponding file name

    Parameters
    ----------
    mip_era : str
        MIP era
    mip_table_directory : str
        MIP table directory
    mip_table_id : str
        MIP table id

    Returns
    -------
    : str
        MIP table name

    Raises
    ------
    RuntimeError
        If no appropriate file can be found on disk
    """
    logger = logging.getLogger(__name__)
    plugin = PluginStore.instance().get_plugin()
    specific_mip_table = '{}{}_{}'.format(plugin.mip_table_prefix(), mip_era, mip_table_id)
    if not os.path.exists(os.path.join(mip_table_directory, specific_mip_table + '.json')):
        logger.debug('Could not find specific MIP table "{}" in directory "{}".'.format(
                     specific_mip_table, mip_table_directory))
        # try generic tables
        generic_mip_table = 'MIP_{}'.format(mip_table_id)
        # Fail if table is not found
        logger.debug('Looking for generic MIP table "{}" in directory "{}".'.format(
                     generic_mip_table, mip_table_directory))
        # Raise error if neither is found
        if not os.path.exists(os.path.join(mip_table_directory, generic_mip_table + '.json')):
            raise RuntimeError('Could not find specific or generic MIP table')
        else:
            mip_table = generic_mip_table
    else:
        mip_table = specific_mip_table
    return mip_table


def retrieve_streams_by_grid(requested_variables):
    """
    Returns the streams in the |MIP requested variables|.

    Parameters
    ----------
    requested_variables: :class:`cdds.common.variables.RequestedVariablesList`
        The information from the |requested variables list|.

    Returns
    -------
    : list
        Streams in the |MIP requested variables|
    """
    streams = []
    active_variables = requested_variables.active_variables_by_mip_table
    for mip_table_id, variable_list in active_variables.items():
        for variable in variable_list:
            variable_name, stream_id, substream = variable
            streams.append(stream_id)
    return streams
