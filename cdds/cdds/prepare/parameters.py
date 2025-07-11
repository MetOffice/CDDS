# (C) British Crown Copyright 2020-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""
The :mod:`configuration.py` module contains the object containing
all request configurations that are necessary for list all variables
that are deactivated.
"""
import logging

from typing import Dict, List, Tuple

from cdds.prepare.common import retrieve_mappings
from cdds.prepare.user_variable import list_all_variables, UserDefinedVariable

from cdds.common.plugins.plugins import PluginStore, CddsPlugin
from cdds.common.plugins.models import ModelParameters
from cdds.common.request.request import Request

from mip_convert.new_variable import VariableModelToMIPMapping


class VariableParameters(object):
    """
    Stores and manage the request configuration / arguments of the
    command line to list variables

    arguments: `argparse.Namespace` object
        The names of the command line arguments

    request: class:`cdds.common.request.request.Request`
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

    def __init__(self, request: Request):
        """
        Create new instance

        :param request: The information from the rose suite request.
        :type request: Request
        """
        self._request: Request = request

        self._plugin: CddsPlugin = PluginStore.instance().get_plugin()
        self._model_params: ModelParameters = self._plugin.models_parameters(self._request.metadata.model_id)

        self._request_variables, self._experiment_metadata = self._retrieve_requested_variables()
        self._model_to_mip_mappings = self._retrieve_model_to_mip_mappings()
        self._model_suite_variables = self._retrieve_model_suite_variables()

    @property
    def request_variables(self):
        return self._request_variables

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
    def experiment_id(self) -> str:
        return self._request.metadata.experiment_id

    @property
    def variant_label(self) -> str:
        return self._request.metadata.variant_label

    @property
    def request_mip(self) -> str:
        return self._request.metadata.mip

    @property
    def request_mip_era(self) -> str:
        return self._request.metadata.mip_era

    @property
    def model_id(self) -> str:
        return self._request.metadata.model_id

    @property
    def model_type(self) -> str:
        return ' '.join(self._request.metadata.model_type)

    @property
    def suite_id(self) -> str:
        return self._request.data.model_workflow_id

    @property
    def suite_branch(self) -> str:
        return self._request.data.model_workflow_branch

    @property
    def suite_revision(self) -> str:
        return self._request.data.model_workflow_revision

    @property
    def experiment_metadata(self) -> Dict[str, str]:
        return self._experiment_metadata

    def _retrieve_model_to_mip_mappings(self) -> Dict[str, Dict[str, VariableModelToMIPMapping]]:
        # Retrieve the 'model to MIP mappings' for the 'MIP requested variables'.
        return retrieve_mappings(self._request_variables,
                                 self._request.metadata.mip_era,
                                 self._request.metadata.model_id)

    def _retrieve_requested_variables(self) -> Tuple[Dict[str, Dict[str, UserDefinedVariable]], Dict[str, str]]:
        # Retrieve the 'MIP requested variables' for the 'experiment' from the specified version of the 'data request'.
        logger = logging.getLogger(__name__)
        logger.info(
            'Building MIP variables from the given mip tables "{}" and a list of requested variables '
            'provided in "{}"'.format(
                self._request.common.mip_table_dir, self._request.data.variable_list_file))

        variables = list_all_variables(self._request.data.variable_list_file, self._request.common.mip_table_dir)
        metadata: Dict[str, str] = {}
        return variables, metadata

    def _retrieve_model_suite_variables(self) -> Dict[str, List[str]]:
        with open(self._request.data.variable_list_file, 'r') as f:
            variables = [variable.strip().split(':')[0] for variable in f.readlines()]

        return {'enabled': variables, 'disabled': []}
