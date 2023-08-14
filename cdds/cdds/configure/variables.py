# (C) British Crown Copyright 2018-2022, Met Office.
# Please see LICENSE.rst for license details.
"""
The :mod:`variables` module contains the code required to determine the
|MIP requested variables| for the request.
"""
from collections import defaultdict
import logging

from cdds.common.grids import retrieve_grid_info, grid_overrides


def retrieve_variables_by_grid(requested_variables):
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
            mip_table = '{}_{}'.format(requested_variables.mip_era, mip_table_id)
            if variables_by_grid[grid_info][section][mip_table]:
                variables_by_grid[grid_info][section][mip_table] += ' '
            variables_by_grid[grid_info][section][mip_table] += variable_name
    return variables_by_grid


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
