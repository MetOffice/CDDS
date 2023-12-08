# (C) British Crown Copyright 2017-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains the code to generate |requested variables lists|.
"""
import os
import logging

from argparse import Namespace
from datetime import datetime

from cdds.common.io import write_json
from cdds.common import set_checksum

from cdds.common.request.request import read_request

from cdds import __version__
from cdds.common.plugins.plugins import PluginStore
from cdds.prepare.mapping_status import MappingStatus, ProducibleState
from cdds.prepare.parameters import VariableParameters


def generate_variable_list(arguments: Namespace) -> None:
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
    output_file = request.requested_variables_list_file_name
    if arguments.output_dir is not None:
        output_file = os.path.join(arguments.output_dir, output_file)
    if os.path.exists(output_file) and request.misc.no_overwrite:
        raise IOError('Output file "{}" already exists'.format(output_file))

    # Bypass data request and build variables directly from tables.
    config = VariableParameters(request)

    # Determine which 'MIP requested variables' can and will be produced.
    logger.info('Bypassing the Data Request and using Mip Tables.')
    constructor = VariablesConstructor(config)

    requested_variables_list = constructor.construct_requested_variables_list()

    # Write the 'requested variables list'.
    logger.debug('Writing the Requested variables list to "{}".'.format(output_file))
    write_json(output_file, requested_variables_list)

    logger.info('*** Complete ***')


class VariablesConstructor:
    """
    Abstract class for all classes constructing the
    requested list of variables
    """

    def __init__(self, config):
        self._config = config
        self._plugin = PluginStore.instance().get_plugin()

    def construct_requested_variables_list(self):
        """
        Return the |requested variables list| using the values in the config object.

        Returns
        -------
        dict:
            The |requested variables list|.
        """
        requested_variables = self.resolve_requested_variables()

        requested_variables_list = {
            'experiment_id': self._config.experiment_id,
            'history': [
                {'comment': 'Requested variables file created.',
                 'time': datetime.now().isoformat()}
            ],
            'mip': self._config.request_mip,
            'mip_era': self._config.request_mip_era,
            'model_id': self._config.model_id,
            'model_type': self._config.model_type,
            'production_info': 'Produced using CDDS Prepare version "{}"'.format(__version__),
            'metadata': self._config.experiment_metadata,
            'status': 'ok',
            'requested_variables': requested_variables,
            'suite_branch': self._config.suite_branch,
            'suite_id': self._config.suite_id,
            'suite_revision': self._config.suite_revision
        }

        if self._config.request_mip_era == 'CMIP6':
            requested_variables_list.update({'MAX_PRIORITY': self._config.max_priority,
                                             'MIPS_RESPONDED_TO': self._config.mips})

        set_checksum(requested_variables_list)
        return requested_variables_list

    def resolve_requested_variables(self):
        """
        Return the resolved |MIP requested variables|.

        Returns
        -------
        : list
            The resolved |MIP requested variables|.
        """
        requested_variables = []
        for mip_table in sorted(self._config.request_variables):
            for variable_name, variable in sorted(self._config.request_variables[mip_table].items()):
                comments = []

                # Variable in model check.
                variable_in_model = self.check_in_model(variable, comments)

                # Mappings check (returns mapping object for use in subsequent checks.
                variable_in_mappings, _ = self.check_mappings(variable, comments)

                # Combine all above flags to determine whether this variable should be active.
                active = all([variable_in_model, variable_in_mappings])

                producible_state = self.check_producible(variable_name, mip_table)

                requested_variable = {
                    'active': active,
                    'producible': producible_state,
                    'cell_methods': variable.cell_methods,
                    'comments': sorted(comments),
                    'dimensions': variable.dimensions,
                    'frequency': variable.frequency,
                    'in_model': variable_in_model,
                    'in_mappings': variable_in_mappings,
                    'label': variable_name,
                    'miptable': mip_table,
                    'stream': variable.stream
                }
                requested_variables.append(requested_variable)

        return requested_variables

    def check_in_model(self, variable, comments):
        """
        Return whether the |MIP requested variable| provided by the
        ``variable`` parameter is enabled in the model suite provided by the
        ``model_suite_variables``.

        If the |MIP requested variable| is disabled or not found in model
        suite, a message is added to the comments provided by the
        ``comments`` parameter.

        Parameters
        ----------
        variable : :class:`DataRequestVariable`
            The |MIP requested variable| from the |data request|.
        comments : list
            The comments related to the |MIP requested variable|.

        Returns
        -------
        : bool
            Whether the |MIP requested variable| is enabled in the model
            suite.
        """
        key = '{}/{}'.format(variable.mip_table, variable.variable_name)
        variable_enabled = key in self._config.enabled_suite_variables
        variable_disabled = key in self._config.disabled_suite_variables
        if not variable_enabled:
            if variable_disabled:
                comments.append('Variable not enabled in model suite')
            else:
                comments.append('Variable does not exist in model suite')
        return variable_enabled

    def check_mappings(self, variable, comments):
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
        mapping = self._config.model_to_mip_mappings[variable.mip_table][variable.variable_name]
        if isinstance(mapping, Exception):
            variable_in_mappings = False
            comments.append(str(mapping))
            # Return None rather than an exception as it is easier for subsequent checks to handle.
            mapping = None
        else:
            variable_in_mappings = True

        return variable_in_mappings, mapping

    @staticmethod
    def check_producible(variable_name, mip_table):
        """
        Check if a variable with given name and in given MIP table will be
        produced or not. The string representation of the producible state
        will be returned that is needed for the variables data list.

        Parameters
        ----------
        variable_name: string
            name of the requested variable
        mip_table: string
            name of the MIP table of the requested variable

        Returns
        -------
        : string
            the string value of the producible state for the variables data list
        """
        mapping_data = MappingStatus.get_instance()
        producible = mapping_data.producible(variable_name, mip_table)
        return ProducibleState.to_variables_data_value(producible)
