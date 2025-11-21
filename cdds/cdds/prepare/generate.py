# (C) British Crown Copyright 2017-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
This module contains the code to generate |requested variables lists|.
"""
import configparser
import glob
import logging
import os
from argparse import Namespace
from collections import defaultdict
from datetime import datetime
from typing import Any

from mip_convert.plugins.plugins import MappingPluginStore
from mip_convert.requested_variables import get_variable_model_to_mip_mapping

from cdds import __version__
from cdds.common import set_checksum
from cdds.common.cdds_files.cdds_directories import component_directory
from cdds.common.io import write_json
from cdds.common.mappings.ancils import remove_ancils_from_mapping
from cdds.common.mip_tables import UserMipTables
from cdds.common.plugins.plugins import PluginStore
from cdds.common.request.request import Request, read_request
from cdds.configure.user_config import create_user_config_files
from cdds.inventory.dao import DBVariableStatus, InventoryDAO
from cdds.prepare.constants import (
    VARIABLE_IN_INVENTORY_COMMENT,
    VARIABLE_IN_INVENTORY_LOG,
    VARIABLE_NOT_IN_INVENTORY_LOG,
)
from cdds.prepare.mapping_status import MappingStatus
from cdds.prepare.user_variable import UserDefinedVariable, parse_variable_list


def generate_variable_list(arguments: Namespace) -> int:
    """
    Generate the |requested variables list|.

    :param arguments: The names of the command line arguments and their validated values.
    :type arguments: Namespace
    :raises
    """
    """
    Generate the |requested variables list|.

    Parameters
    ----------
    arguments: :class:`argparse.Namespace` object
        The names of the command line arguments and their validated
        values.

    Raises
    ------
    IOError
        If the |requested variables list| already exists.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)
    logger.debug('CDDS Prepare version "{}"'.format(__version__))

    # Read the request information.
    request = read_request(arguments.request)
    # Retrieve the name of the 'requested variables list'.
    plugin = PluginStore.instance().get_plugin()
    request_variables_filename = plugin.requested_variables_list_filename(request)
    if arguments.output_dir is not None:
        output_file = os.path.join(arguments.output_dir, request_variables_filename)
    else:
        # use proc directory
        output_file = os.path.join(plugin.proc_directory(request), 'prepare', request_variables_filename)
    if os.path.exists(output_file) and request.misc.no_overwrite:
        raise IOError('Output file "{}" already exists'.format(output_file))

    cmip_tables = UserMipTables(request.common.mip_table_dir)

    with open(request.data.variable_list_file, "r") as fh:
        requested_variables = [line.strip() for line in fh.readlines()]

    user_requested_variables = parse_variable_list(cmip_tables, requested_variables)

    model_to_mip_mappings = retrieve_mappings(
        user_requested_variables,
        request.metadata.mip_era,
        request.metadata.model_id,
    )

    logger.info('Bypassing the Data Request and using Mip Tables.')
    # Bypass data request and build variables directly from tables.
    requested_variables = resolve_requested_variables(user_requested_variables, model_to_mip_mappings)
    variable_constructor = VariablesConstructor(request, requested_variables)
    var_list = variable_constructor.construct_requested_variables_list()

    check_variables_result = check_variables_recognised(var_list)
    check_streams_match = check_streams_match_variables(var_list, request)
    if check_variables_result or check_streams_match != 0:
        logger.warning("Issues found but continuing, a non zero exit code will be returned")

    # TODO: take inventory check into account!
    # Write the 'requested variables list'.
    logger.info('Writing the Requested variables list to "{}".'.format(output_file))
    write_json(f"{output_file}", var_list)

    if (arguments.reconfigure):
        reconfigure_mip_cfg_file(request, output_file)

    logger.info('*** Complete ***')

    return 1 if check_variables_result or check_streams_match else 0


def check_variables_recognised(var_list: dict[str, Any]) -> int:
    """
    Checks for unrecognised variables in the provided list and logs critical messages if they exist.

    Parameters
    ----------
    var_list : dict
        The user requested variables.
    Returns
    -------
    int
        Returns 1 if there are any unrecognised (inactive) variables, otherwise returns 0.
    Logs
    ----
    Critical log messages for each unrecognised variable, including its comments.
    """

    logger = logging.getLogger(__name__)
    unrecognised_variables = []
    for var in var_list['requested_variables']:
        if not var['active']:
            unrecognised_variables.append(var)

    for x in unrecognised_variables:
        logger.critical(f'Unrecognised variable: {x["miptable"]}/{x["label"]}{x["comments"]}')
    if unrecognised_variables:
        return 1
    else:
        return 0


def check_streams_match_variables(var_list: dict[str, Any], request: Any) -> int:
    """
    Compares the set of streams present in the variables list file with those from the request file.
    Logs critical errors for any streams found in one but not the other, and returns a status code of 1 if
    mismatches are found.

    Note: Variables in the list can include substreams in format 'stream/substream' (e.g., 'onm/scalar'),
    so the base stream ID (before '/') is used for comparison with request streams.

    Parameters
    ----------
    var_list : dict
        Variables from the variables file.
    request : object
        Request containing all information for the MIP convert cfg file.
    Returns
    -------
    int
        Returns 1 if there are mismatched streams between variables list and the request streams, otherwise returns 0.
    Logs
    ----
    Critical
        Logs critical messages for each mismatched stream found.
    """

    logger = logging.getLogger(__name__)
    variables_list_streams = set()
    request_streams = set()
    requested_streams = request.data.streams
    for var in var_list['requested_variables']:
        stream = var['stream']
        base_stream = stream.split('/')[0] if '/' in stream else stream
        variables_list_streams.add(base_stream)

    for var in requested_streams:
        request_streams.add(var)

    streams_in_variables_list_but_not_in_request = variables_list_streams.difference(request_streams)
    streams_in_request_but_not_in_variables_list = request_streams.difference(variables_list_streams)

    if streams_in_variables_list_but_not_in_request:
        for stream in streams_in_variables_list_but_not_in_request:
            logger.critical(
                f'Stream "{stream}" found in variables list but not in request file streams: {request_streams}'
            )

    if streams_in_request_but_not_in_variables_list:
        for stream in streams_in_request_but_not_in_variables_list:
            logger.critical(
                f'Stream "{stream}" found in request streams but not in variables list file: {variables_list_streams}'
            )

    if streams_in_variables_list_but_not_in_request or streams_in_request_but_not_in_variables_list:
        return 1
    else:
        return 0


def reconfigure_mip_cfg_file(request: Request, requested_variables_file: str) -> None:
    """
    Reconfigure the MIP convert configuration file.

    :param request: Request containing all information for the MIP convert cfg file
    :type request: Request
    :param component: requested_variables_file
    :type component: str
    :return: Path to the requested variable file
    :rtype: str
    """
    logger = logging.getLogger()
    logger.info('* Starting reconfiguration *')

    configure_dir = component_directory(request, 'configure')
    if os.path.exists(configure_dir):
        mip_convert_files_to_remove = glob.glob(configure_dir + '/mip_convert.cfg*')
        for mip_convert_file_to_remove in mip_convert_files_to_remove:
            logger.info('Removing MIP convert configuration file: {}'.format(mip_convert_file_to_remove))
            os.remove(mip_convert_file_to_remove)

    logger.info('Creating new MIP convert configuration in {}'.format(configure_dir))
    create_user_config_files(request, requested_variables_file, configure_dir)
    logger.info('* Completed reconfiguration *')


def retrieve_mappings(variables: list[UserDefinedVariable], mip_era, model_id) -> dict[str, dict[str, Any]]:
    """
    Return the |model to MIP mappings| for the |MIP requested variables|.

    The returned |model to MIP mappings| are organised by |MIP table|,
    then |MIP requested variable name|. Note if the
    |model to MIP mapping| is not found for a given
    |MIP requested variable|, the exception raised will be returned
    instead of the |model to MIP mapping|.

    Parameters
    ----------
    data_request_variables : dict of :class:`DataRequestVariables`
        The |MIP requested variables| from the |data request|.
    mip_era : str
        The |MIP era|.
    model_id : str
        The |model identifier|.

    Returns
    -------
    : dict of :class:`VariableModelToMIPMapping`
        The |model to MIP mappings| for the |MIP requested variables|.
    """
    mapping_plugin = MappingPluginStore.instance().get_plugin()
    mappings: dict = defaultdict(dict)

    for variable in variables:
        mip_table_name = "{}_{}".format(mip_era, variable.mip_table)
        model_to_mip_mappings = mapping_plugin.load_model_to_mip_mapping(mip_table_name)
        try:
            mapping = get_variable_model_to_mip_mapping(model_to_mip_mappings, variable.var_name, variable.mip_table)
            mapping = remove_ancils_from_mapping(mapping, model_id)
        except (RuntimeError, configparser.Error) as exc:
            mapping = exc
        mappings[variable.mip_table][variable.var_name] = mapping

    return mappings


def check_mappings(variable: UserDefinedVariable, model_to_mip_mappings):
    """
    Return whether the |MIP requested variable| provided by the
    ``variable`` parameter has an associated |model to MIP mapping|
    provided by the ``model_to_mip_mappings`` parameter, along with the
    |model to MIP mapping|.

    Parameters
    ----------
    variable : :class:`DataRequestVariable`
        The |MIP requested variable| from the |data request|.
    comments : list
        The comments related to the |MIP requested variable|.

    Returns
    -------
    : bool, :class:`VariableModelToMIPMapping`
        Whether the |MIP requested variable| has an associated
        |model to MIP mapping|, along with the |model to MIP mapping|
        for the |MIP requested variable|.
    """
    mapping = model_to_mip_mappings[variable.mip_table][variable.variable_name]
    comments = []
    if isinstance(mapping, Exception):
        variable_in_mappings = False
        comments.append(str(mapping))
        # Return None rather than an exception as it is easier for subsequent checks to handle.
    else:
        variable_in_mappings = True

    return variable_in_mappings, comments


def resolve_requested_variables(request_variables: list[UserDefinedVariable], model_to_mip_mappings):
    """
    Return the resolved |MIP requested variables|.

    Returns
    -------
    : list
        The resolved |MIP requested variables|.
    """
    mapping_data = MappingStatus.get_instance()

    requested_variables = []
    for variable in request_variables:
        # Mappings check (returns mapping object for use in subsequent checks.
        variable_in_model = True
        variable_in_mappings, comments = check_mappings(variable, model_to_mip_mappings)

        # Combine all above flags to determine whether this variable should be active.
        active = all([variable_in_model, variable_in_mappings])

        requested_variable = {
            "active": active,
            "producible": mapping_data.producible_state(variable.variable_name, variable.mip_table),
            "cell_methods": variable.cell_methods,
            "comments": sorted(comments),
            "dimensions": variable.dimensions,
            "frequency": variable.frequency,
            "in_model": variable_in_model,
            "in_mappings": variable_in_mappings,
            "label": variable.variable_name,
            "miptable": variable.mip_table,
            "stream": variable.stream,
        }
        requested_variables.append(requested_variable)

    return requested_variables


class VariablesConstructor:
    def __init__(self, request: Request, requested_variables: list[UserDefinedVariable]):
        self.request = request
        self.requested_variables = requested_variables

    def construct_requested_variables_list(self):
        """
        Return the |requested variables list| using the values in the config object.

        Returns
        -------
        dict:
            The |requested variables list|.
        """

        requested_variables_list = {
            "experiment_id": self.request.metadata.experiment_id,
            "history": [{"comment": "Requested variables file created.", "time": datetime.now().isoformat()}],
            "mip": self.request.metadata.mip,
            "mip_era": self.request.metadata.mip_era,
            "model_id": self.request.metadata.model_id,
            "model_type": ' '.join(self.request.metadata.model_type),
            "production_info": 'Produced using CDDS Prepare version "{}"'.format(__version__),
            "metadata": {},
            "status": "ok",
            "requested_variables": self.requested_variables,
            "suite_branch": self.request.data.model_workflow_branch,
            "suite_id": self.request.data.model_workflow_id,
            "suite_revision": self.request.data.model_workflow_revision,
        }

        set_checksum(requested_variables_list)
        return requested_variables_list


class InventoryVariablesConstructor(VariablesConstructor):
    """
    Class that provides function for listing variables with
    additional in the inventory database
    """

    def __init__(self, db_file, config):
        """
        Parameters
        ----------
        db_file: str
            path to the inventory database configuration file
        config: `cdds.prepare.parameters.VariableParameters` object
            all input parameters for constructing the list of approved variables
        """
        super(InventoryVariablesConstructor, self).__init__(config)
        self._dao = InventoryDAO(db_file)
        self._db_data = self._dao.get_variables_data(config.model_id, config.experiment_id, config.variant_label)

    def additional_active_checks(self, variable, comments):
        """
        Returns if the requested variable is according the inventory database active or not.
        A variable is active if the status in the inventory database is not 'available' or 'in progress'. If the
        variable is not found in the inventory database, it is active by default.
        A comment will be added if a variable is inactive.
        Parameters
        ----------
        variable: :class:`DataRequestVariable`
            The |MIP requested variable| from the |data request|.
        comments: list
            The comments related to the |MIP requested variable|.
        Returns
        -------
        : bool
            Whether the |MIP requested variable| is activated in the inventory database.
        """
        logger = logging.getLogger(__name__)
        try:
            is_active = self._check_inventory_status(variable, comments)
            message = VARIABLE_IN_INVENTORY_LOG.format(variable.mip_table, variable.variable_name, is_active)
        except KeyError:
            message = VARIABLE_NOT_IN_INVENTORY_LOG.format(variable.mip_table, variable.variable_name)
            is_active = True
        logger.debug(message)
        return is_active

    def _check_inventory_status(self, variable, comments):
        db_variable = self._db_data.get_variable(variable.mip_table, variable.variable_name)
        active_state = DBVariableStatus.AVAILABLE
        in_progess_state = DBVariableStatus.IN_PROGRESS
        is_active = db_variable.has_not_status(active_state) and db_variable.has_not_status(in_progess_state)

        if not is_active:
            comments.append(VARIABLE_IN_INVENTORY_COMMENT.format(
                db_variable.id, db_variable.version, db_variable.status
            ))
        return is_active

    def clean_up(self):
        self._dao.close()
