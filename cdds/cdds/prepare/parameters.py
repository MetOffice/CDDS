# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`configuration.py` module contains the object containing
all request configurations that are necessary for list all variables
that are deactivated.
"""
import logging

from cdds.prepare.constants import FALLBACK_EXPERIMENT_ID
from cdds.prepare.common import retrieve_mappings
from cdds.prepare.model_config import retrieve_model_suite_variables
from cdds.prepare.data_request import get_data_request_variables
from cdds.prepare.user_variable import list_all_variables

from cdds.common.plugins.plugins import PluginStore


class VariableParameters(object):
    """
    Stores and manage the request configuration / arguments of the
    command line to list variables

    arguments: `argparse.Namespace` object
        The names of the command line arguments

    request: class:`cdds.common.request.Request`
        The information from the CREM / rose suite request.

    data_request_variables: dict of :class:`DataRequestVariables`
        The |MIP requested variables| from the |data request|.

    experiment_metadata: dict
        Metadata associated with this list of |MIP requested variables|.

    model_data_request_variables: dict of :class:`DataRequestVariables`
        The |MIP requested variables| for the experiment from the
        specified version of the |data request|.

    model_to_mip_mappings: dict of :class:`VariableModelToMIPMapping`
        The |model to MIP mappings| for the |MIP requested variables|.

    model_suite_variables: dict
        The |MIP requested variables| from the model suite in the form
        ``{'enabled': ['mip_table1/var_name1', ...],
        'disabled': ['mip_table2/var_name2', ...]}``.
    """

    def __init__(self, arguments, request):
        """
        Parameters
        ----------
        arguments: `argparse.Namespace` object
            The names of the command line arguments
        request: class:`cdds.common.request.Request`
            The information from the CREM / rose suite request.
        """
        self._arguments = arguments
        self._request = request

        plugin = PluginStore.instance().get_plugin()
        self._model_params = plugin.models_parameters(self._request.model_id)

        self._data_request_variables, self._experiment_metadata = self._retrieve_data_requested_variables()
        self._model_data_request_variables = self._retrieve_model_data_request_variables()
        self._model_to_mip_mappings = self._retrieve_model_to_mip_mappings()
        self._model_suite_variables = self._retrieve_model_suite_variables()

    @property
    def data_request_variables(self):
        return self._data_request_variables

    @property
    def data_request_experiment(self):
        """
        Return the experiment to be used to query the data request.
        """
        logger = logging.getLogger(__name__)
        if self._arguments.alternate_data_request_experiment:
            data_request_experiment = self._arguments.alternate_data_request_experiment
            logger.warning(
                'Using experiment_id "{}" when querying the data request rather '
                'than "{}"'.format(data_request_experiment, self._request.experiment_id))
        else:
            data_request_experiment = self._request.experiment_id

        return data_request_experiment

    @property
    def model_data_request_variables(self):
        return self._model_data_request_variables

    @property
    def model_suite_variables(self):
        return self._model_suite_variables

    @property
    def enabled_suite_variables(self):
        return self._model_suite_variables['enabled']

    @property
    def disabled_suite_variables(self):
        return self._model_suite_variables['disabled']

    @property
    def model_to_mip_mappings(self):
        return self._model_to_mip_mappings

    @property
    def experiment_id(self):
        return self._request.experiment_id

    @property
    def variant_label(self):
        return self._request.variant_label

    @property
    def request_mip(self):
        return self._request.mip

    @property
    def request_mip_era(self):
        return self._request.mip_era

    @property
    def model_id(self):
        return self._request.model_id

    @property
    def model_type(self):
        return self._request.model_type

    @property
    def suite_id(self):
        return self._request.suite_id

    @property
    def suite_branch(self):
        return self._request.suite_branch

    @property
    def suite_revision(self):
        return self._request.suite_revision

    @property
    def mips(self):
        return self._arguments.mips

    @property
    def max_priority(self):
        return self._arguments.max_priority

    @property
    def mapping_status(self):
        return self._arguments.mapping_status

    @property
    def experiment_metadata(self):
        return self._experiment_metadata

    @property
    def data_request_version(self):
        return self._experiment_metadata['data_request_version']

    def _retrieve_data_requested_variables(self):
        # Retrieve the 'MIP requested variables' for the 'experiment' from the specified version of the 'data request'.
        logger = logging.getLogger(__name__)
        logger.info('Retrieving MIP requested variables from data request version '
                    '"{}"'.format(self._arguments.data_request_version))
        variables, experiment_metadata = get_data_request_variables(
            self._arguments.data_request_version,
            self.data_request_experiment,
            self._arguments.data_request_base_dir)

        if self._arguments.alternate_data_request_experiment:
            experiment_metadata['**WARNING**'] = (
                'Experiment metadata will refer to the experiment_id used when '
                'querying the data request ("{}") rather than the experiment_id '
                '("{}") to which this variable list corresponds'.format(
                    self.data_request_experiment, self._request.experiment_id
                )
            )
        return variables, experiment_metadata

    def _retrieve_model_data_request_variables(self):
        logger = logging.getLogger(__name__)
        # Retrieve the 'MIP requested variables' for the 'experiment' from
        # the version of the 'data request' used to setup the 'model'.
        data_req_ver_model = self._model_params.data_request_version
        logger.info('Retrieving MIP requested variables from data request version "{}" (used to setup the model)'
                    ''.format(data_req_ver_model))
        # Use piControl as a fallback, in case experiment was not defined at the time the model was configured.
        # The metadata from this version of the 'data request' is irrelevant.
        model_data_request_variables, _ = get_data_request_variables(data_req_ver_model,
                                                                     self.data_request_experiment,
                                                                     self._arguments.data_request_base_dir,
                                                                     FALLBACK_EXPERIMENT_ID)
        return model_data_request_variables

    def _retrieve_model_to_mip_mappings(self):
        # Retrieve the 'model to MIP mappings' for the 'MIP requested variables'.
        return retrieve_mappings(self._data_request_variables, self._request.mip_era, self._request.model_id)

    def _retrieve_model_suite_variables(self):
        logger = logging.getLogger(__name__)
        # Retrieve the 'MIP requested variables' from the model suite.
        logger.debug('Retrieving MIP requested variables from model suite '
                     '"{}/{}@{}"'.format(self._request.suite_id, self._request.suite_branch,
                                         self._request.suite_revision))
        return retrieve_model_suite_variables(
            self._model_to_mip_mappings, self._request.mip_era, self._request.model_type,
            self._request.suite_id, self._request.suite_branch, self._request.suite_revision)


class UserDefinedVariableParameters(VariableParameters):
    """
    Stores and manage the request configuration / arguments of the
    command line to list user defined variables.
    """

    def __init__(self, arguments, request):
        """
        Parameters
        ----------
        arguments: `argparse.Namespace` object
            The names of the command line arguments

        request: class:`cdds.common.request.Request`
            The information from the rose suite request.
        """
        super(UserDefinedVariableParameters, self).__init__(arguments, request)

    def _retrieve_data_requested_variables(self):
        # Retrieve the 'MIP requested variables' for the 'experiment' from the specified version of the 'data request'.
        logger = logging.getLogger(__name__)
        logger.info(
            'Building MIP variables from the given mip tables "{}" and a list of requested variables '
            'provided in "{}" with mip era "{}" stream defaults'.format(
                self._request.mip_table_dir, self._arguments.user_request_variables, self._arguments.mip_era_defaults))

        variables = list_all_variables(self._arguments.user_request_variables, self._request.mip_table_dir,
                                       self._arguments.mip_era_defaults)

        if self._arguments.alternate_data_request_experiment:
            experiment_metadata['**WARNING**'] = (
                'Experiment metadata will refer to the experiment_id used when '
                'querying the data request ("{}") rather than the experiment_id '
                '("{}") to which this variable list corresponds'.format(
                    self.data_request_experiment, self._request.experiment_id
                )
            )

        metadata = {'data_request_version': self._arguments.data_request_version}

        return variables, metadata

    def _retrieve_model_data_request_variables(self):
        return self._data_request_variables

    def _retrieve_model_suite_variables(self):
        with open(self._arguments.user_request_variables, 'r') as f:
            variables = [variable.strip().split(':')[0] for variable in f.readlines()]

        return {'enabled': variables, 'disabled': []}
