# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
"""Top level routines involved in changing states of data to MASS, i.e.
submission of data (embargoed -> available) and retraction (available ->
withdrawn).
"""
import logging

from argparse import Namespace

from cdds.common.request.request import read_request, Request
from cdds.deprecated.transfer import dds, state
from cdds.deprecated.transfer.common import (
    load_rabbit_mq_credentials, cfg_from_cdds_general_config,
    drs_facet_builder_from_request, log_filesets, find_mass)
from cdds.deprecated.transfer.drs import filter_filesets
from cdds.deprecated.transfer.moo_cmd import LS_ONLY
from cdds.deprecated.config import CDDSConfigGeneral


def run_move_in_mass(request: Request, args: Namespace) -> None:
    """Perform a state change process; load the request and configuration information, identify files in MASS
    to change state, perform the moves required and send appropriate messages to the CEDA rabbit MQ server.

    Parameters
    ----------
    request : Request
        The information contains in the request cfg file
    args : Namespace
        Parsed command line arguments
    """
    logger = logging.getLogger(__name__)
    # Construct configs
    logger.info('Reading CDDS General Config')
    config_general = CDDSConfigGeneral(request)
    transfer_cfg = cfg_from_cdds_general_config(config_general, request)

    # Attempt to load rabbit credentials
    success = load_rabbit_mq_credentials(transfer_cfg)
    if not success and not request.common.simulation:
        message = 'A Rabbit MQ server cannot be contacted so messages cannot be sent.'
        logger.critical(message)
        raise RuntimeError(message)

    drs_fixed_facet_builder = drs_facet_builder_from_request(request, transfer_cfg)  # type: ignore
    logger.info('Using following facets to identify data sets to move: "{}"'
                ''.format(repr(drs_fixed_facet_builder.facets)))

    transfer_service = dds.DataTransfer(transfer_cfg, request.metadata.mip_era)
    if request.common.simulation:
        logger.info('Cannot fully simulate `move_in_mass`. Allowing moo ls commands')
        transfer_service._simulation = LS_ONLY
    logger.info('Searching mass for file sets in state "{}"'.format(args.original_state))

    filesets = find_mass(drs_fixed_facet_builder, args.original_state, transfer_service)

    # filter based on approved variables file
    approved_variables_file = args.approved_variables_path
    logger.info('Limiting state change to variables specified in "{}"'.format(approved_variables_file))
    variables_to_operate_on = read_variables_list_file(approved_variables_file)
    filter_filesets(filesets, variables_to_operate_on)

    log_filesets(filesets)
    try:
        logger.info('Moving file sets to state "{}"'.format(args.new_state))
        move_in_mass(filesets, transfer_service, args.original_state, args.new_state)
        logger.info('Moving complete')
    except Exception as err:
        logger.critical('Moving failed')
        logger.exception(err)
        raise


def move_in_mass(filesets, transfer_service, original_state, new_state):
    """Move the specified set of files between the original and new
    states using the data transfer service provided.

    Parameters
    ----------
    filesets : :class:`cdds.deprecated.transfer.drs.AtomicDatasetCollection`
        Sets of files to be moved.
    transfer_service: :class:`cdds.deprecated.transfer.dds.DataTransfer`
        Data transfer service.
    original_state : str
        State to move data sets from.
    new_state : :class:`cdds.deprecated.transfer.state.State`
        State to move data sets to.

    Notes
    -----
    The original and new states must be in cdds.deprecated.transfer.state.KNOWN,
    i.e. 'embargoed', 'available', 'withdrawn' or 'superceded'.
    """
    # Construct objects representing each state
    start_state = state.make_state(original_state)
    end_state = state.make_state(new_state)
    # make state change.
    transfer_service.change_mass_state(filesets, start_state, end_state)


def read_variables_list_file(file_name):
    """Return a list of variables to operate on, read from the specified
    file. Each entry in the file must be of the format
    `<mip_table>/<variable_name>;<dataset_filepath>` or
    `<mip_table>/<variable_name>` (for backward compatibility).

    Parameters
    ----------
    file_name : str
        Name of the file to read.

    Returns
    -------
    list of tuples
        Variables to limit state change to (mip_table, var_name).

    Raises
    ------
    RuntimeError
        If an entry in the file is not of the correct format
    """
    logger = logging.getLogger(__name__)
    variable_list = []
    with open(file_name) as file_handle:
        for i, line in enumerate(file_handle.readlines()):
            try:
                if ';' in line:
                    variable_string, data_path = line.split(';')
                    mip_table, var_name = variable_string.strip().split('/')
                    # use last two directories in the directory path to work out
                    # what the cmor name is. This is a little hacky, but otherwise
                    # a fair bit of work with the MIP tables is needed.
                    mip_table_path, out_name = data_path.strip().split('/')[-2:]

                    if mip_table_path != mip_table:
                        raise RuntimeError(
                            'MIP table and data path inconsistent: '
                            '"{}", "{}"'.format(variable_string, data_path))
                    if out_name != var_name:
                        logger.debug(
                            'Replacing variable name "{}" with "{}"'
                            ''.format(var_name, out_name))
                        var_name = out_name

                else:
                    mip_table, var_name = line.strip().split('/')

            except ValueError:
                raise RuntimeError(
                    'Could not interpret line {} ("{}") from file "{}" as a '
                    'variable'.format(i, line, file_name))
            variable_list.append((mip_table, var_name))
    return variable_list
