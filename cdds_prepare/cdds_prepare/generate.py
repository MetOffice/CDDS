# (C) British Crown Copyright 2017-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains the code to generate |requested variables lists|.
"""
from datetime import datetime
import os
import logging

from abc import ABCMeta, abstractmethod
from common.io import write_json
from hadsdk.common import set_checksum
from hadsdk.config import FullPaths
from hadsdk.constants import REQUIRED_KEYS_FOR_REQUESTED_VARIABLES_LIST
from hadsdk.request import read_request

from hadsdk.inventory.dao import InventoryDAO, DBVariableStatus

from common.plugins.plugins import PluginStore

from cdds_prepare import __version__
from cdds_prepare.auto_deactivation import run_auto_deactivate_variables
from cdds_prepare.constants import (KNOWN_GOOD_VARIABLES,
                                    VARIABLE_IN_INVENTORY_LOG,
                                    VARIABLE_NOT_IN_INVENTORY_LOG,
                                    VARIABLE_IN_INVENTORY_COMMENT)
from cdds_prepare.mapping_status import MappingStatus, ProducibleState
from cdds_prepare.data_request import (check_variable_model_data_request,
                                       check_data_request_changes,
                                       calculate_priority,
                                       check_priority,
                                       calculate_ensemble_size)
from cdds_prepare.parameters import VariableParameters, UserDefinedVariableParameters


def generate_variable_list(arguments):
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
    request = read_request(arguments.request,
                           REQUIRED_KEYS_FOR_REQUESTED_VARIABLES_LIST)

    # Retrieve the name of the 'requested variables list'.
    full_paths = FullPaths(arguments, request)
    output_file = full_paths.requested_variables_list_filename
    if arguments.output_dir is not None:
        output_file = os.path.join(arguments.output_dir, output_file)
    if os.path.exists(output_file) and arguments.no_overwrite:
        raise IOError('Output file "{}" already exists'.format(output_file))

    # Bypass data request and build variables directly from tables.
    if arguments.user_request_variables:
        config = UserDefinedVariableParameters(arguments, request)
    else:
        config = VariableParameters(arguments, request)

    # Determine which 'MIP requested variables' can and will be produced.
    if arguments.user_request_variables:
        logger.info('Bypassing the Data Request and using Mip Tables.')
        constructor = BypassDataRequestVariablesConstructor(config)
    elif arguments.no_inventory_check:
        logger.info('No inventory check')
        constructor = BaseVariablesConstructor(config)
    else:
        logger.info('Inventory check being performed using database "{}"'.format(arguments.db_file))
        constructor = InventoryVariablesConstructor(arguments.db_file, config)

    requested_variables_list = constructor.construct_requested_variables_list()
    constructor.clean_up()

    # Write the 'requested variables list'.
    logger.debug(
        'Writing the Requested variables list to "{}".'.format(output_file))
    write_json(output_file, requested_variables_list)

    if not arguments.no_auto_deactivation and not arguments.user_request_variables:
        run_auto_deactivate_variables(
            arguments.auto_deactivation_rules_file, output_file, request.model_id, request.experiment_id)

    logger.info('*** Complete ***')


class AbstractVariablesConstructor(object, metaclass=ABCMeta):
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
            'data_request_version': self._config.data_request_version,
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

        for mip_table in sorted(self._config.data_request_variables):
            for variable_name, variable in sorted(self._config.data_request_variables[mip_table].items()):
                comments = []
                # If the variable is in the model data request get it.
                model_data_request_variables = self._config.model_data_request_variables
                model_variable = check_variable_model_data_request(variable, model_data_request_variables, comments)

                # Variable in model check.
                variable_in_model = self.check_in_model(variable, comments)

                # Mappings check (returns mapping object for use in subsequent checks.
                variable_in_mappings, mapping = self.check_mappings(variable, comments)

                # Mapping status check.
                variable_required_status = self.check_status(mapping, comments)

                # Data request check.
                critical_data_request_changes = check_data_request_changes(variable, model_variable, mapping, comments)

                # Priority check.
                priority = calculate_priority(self._config.mips, variable)
                priority_ok = check_priority(priority, self._config.max_priority, comments)

                # Ensemble size check.
                ensemble_size = calculate_ensemble_size(self._config.mips, variable)

                # Combine all above flags to determine whether this variable should be active.
                active = self.check_active(
                    variable, model_variable, variable_in_model, variable_in_mappings, variable_required_status,
                    critical_data_request_changes, priority_ok, comments
                )

                producible_state = self.check_producible(variable_name, mip_table)

                stream_info = self._plugin.stream_info()
                stream_id, substream = stream_info.retrieve_stream_id(variable_name, mip_table)

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
                    'priority': priority,
                    'ensemble_size': ensemble_size,
                    'stream': '{}/{}'.format(stream_id, substream) if substream is not None else stream_id
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

    def check_status(self, mapping, comments):
        """
        Return whether the status of the |model to MIP mapping| matches the
        required status.

        Parameters
        ----------
        mapping : :class:`VariableModelToMIPMapping`
            The |model to MIP mapping| for the |MIP requested variable|.
        comments : list
            The comments related to the |MIP requested variable|.

        Returns
        -------
        : bool
            Whether the status of the |model to MIP mapping| matches the
            required status.
        """
        mapping_status_required = self._config.mapping_status
        if mapping is None:
            variable_required_status = False
        else:
            variable_required_status = True
            if mapping_status_required != 'all' and mapping.status != mapping_status_required:
                variable_required_status = False
                comments.append(
                    'Status requested was "{}" but model to MIP mapping status is '
                    '"{}"'.format(mapping_status_required, mapping.status)
                )

        return variable_required_status

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

    def check_active(self, variable, model_variable, variable_in_model, variable_in_mappings, variable_required_status,
                     critical_data_request_changes, priority_ok, comments):
        """
        Return whether the |MIP requested variable| should be activated.

        A critical message will be logged if there are important differences
        between the version of the |data request| used to setup the |model|
        and the specified version of the |data request|.

        Parameters
        ----------
        variable : :class:`DataRequestVariable`
            The |MIP requested variable| from the |data request|.
        model_variable : :class:`DataRequestVariable`
            The |MIP requested variable| from the version of the
            |data request| used to setup the |model|.
        variable_in_model : bool
            Whether the |MIP requested variable| is enabled in the model
            suite.
        variable_in_mappings : bool
            Whether the |MIP requested variable| has an associated
            |model to MIP mapping|.
        variable_required_status : bool
            Whether the status of the |model to MIP mapping| matches the
            required status.
        critical_data_request_changes : bool
            Whether the |MIP requested variable| has changed significantly
            between the version of the |data request| used to setup the
            |model| and the specified version of the |data request|.
        priority_ok : bool
            Whether the priority of the |MIP requested variable| (which can
            differ depending on the |MIP|) is equal to or less than the
            maximum priority.
        comments : list
            The comments related to the |MIP requested variable|.

        Returns
        -------
        : bool
            Whether the |MIP requested variable| should be activated.
        """

        logger = logging.getLogger(__name__)
        # critical_data_request_changes cannot be True if the variable in question
        # was not in the data request used to configure the model, i.e. when
        # model_variable is None.
        if model_variable is None:
            critical_data_request_changes = False
        else:
            kgv_key = (model_variable.data_request.version, variable.data_request.version)
            if kgv_key in KNOWN_GOOD_VARIABLES:
                if self.is_variable_list_in_known_variables(variable, kgv_key):
                    comments.append('Variable listed in KNOWN_GOOD_VARIABLES for data request version "{}"'
                                    ''.format(variable.data_request.version))
                    critical_data_request_changes = False

        additional_checks = self.additional_active_checks(variable, comments)

        active = all([variable_in_model,
                      variable_in_mappings,
                      variable_required_status,
                      not critical_data_request_changes,
                      priority_ok,
                      additional_checks])

        # critical log if the data request changes are the only cause for being unable to produce a variable.
        if critical_data_request_changes and all(
                [variable_in_model, variable_in_mappings, variable_required_status, priority_ok, additional_checks]):
            logger.critical(
                'Variable "{}/{}" not active due to data request changes between model version "{}" and version "{}"'
                ''.format(variable.mip_table, variable.variable_name, model_variable.data_request.version,
                          variable.data_request.version))
        return active

    @abstractmethod
    def additional_active_checks(self, variable, comments):
        pass

    @abstractmethod
    def clean_up(self):
        pass

    @staticmethod
    def is_variable_list_in_known_variables(variable, kgv_key):
        return ((variable.mip_table in KNOWN_GOOD_VARIABLES[kgv_key]) and
                (variable.variable_name in KNOWN_GOOD_VARIABLES[kgv_key][variable.mip_table]))


class BaseVariablesConstructor(AbstractVariablesConstructor):
    """
    Class that provides function for listing variables without
    any additional database information
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config: `cdds_prepare.parameters.VariableParameters` object
            all input parameters for constructing the list of approved variables
        """
        super(BaseVariablesConstructor, self).__init__(config)

    def additional_active_checks(self, variable, comments):
        return True

    def clean_up(self):
        pass


class BypassDataRequestVariablesConstructor(AbstractVariablesConstructor):
    """
    Class that provides function for listing variables without
    any additional database information
    """

    def __init__(self, config):
        """
        Parameters
        ----------
        config: `cdds_prepare.parameters.VariableParameters` object
            all input parameters for constructing the list of approved variables
        """
        super(BypassDataRequestVariablesConstructor, self).__init__(config)

    def resolve_requested_variables(self):
        """
        Return the resolved |MIP requested variables|.

        Returns
        -------
        : list
            The resolved |MIP requested variables|.
        """
        requested_variables = []
        for mip_table in sorted(self._config.data_request_variables):
            for variable_name, variable in sorted(self._config.data_request_variables[mip_table].items()):
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

    def clean_up(self):
        pass

    def additional_active_checks(self, variable, comments):
        return True


class InventoryVariablesConstructor(AbstractVariablesConstructor):
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
        config: `cdds_prepare.parameters.VariableParameters` object
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
