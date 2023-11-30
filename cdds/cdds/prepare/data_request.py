# (C) British Crown Copyright 2018-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
This module contains the code to identify critical changes to variables
between different versions of the data request
"""
from collections import defaultdict
import logging

from cf_units import Unit
from typing import Tuple, Dict, List

# TODO: kerstin => Dependency to Mip Convert should be removed
from mip_convert.new_variable import VariableModelToMIPMapping
from cdds.prepare.data_request_interface.data_request_wrapper import DataRequestWrapper, ExperimentNotFoundError
from cdds.prepare.data_request_interface.variables import (retrieve_data_request_variables,
                                                           describe_differences,
                                                           DataRequestVariable)
from cdds.prepare.constants import ALLOWED_POSITIVE, CRITICAL_FIELDS, PRIORITY_UNSET


def list_variables_for_experiment(
        data_request: DataRequestWrapper, experiment_id: str, fallback_experiment_id: str = None
) -> Tuple[Dict[str, Dict[str, DataRequestVariable]], Dict[str, str]]:
    """
     Return the |MIP requested variables| for the experiment provided by the ``experient_id`` parameter
     from the specified version of the |data request|.
     The returned |MIP requested variables| are organised by |MIP table|, then |MIP requested variable name|.

    :param data_request: The specified version of the |data request|.
    :type data_request: DataRequestWrapper
    :param experiment_id: The |experiment identifier|.
    :type experiment_id: str
    :param fallback_experiment_id: The fallback |experiment identifier| if the `experiment_id` is not found.
    :type fallback_experiment_id: str
    :return: The |MIP requested variables| for the experiment from the
        specified version of the |data request| and their metadata
    :rtype: Tuple[Dict[str, Dict[str, DataRequestVariable]], Dict[str, str]]
    """
    logger = logging.getLogger(__name__)
    try_fallback = False
    try:
        variables, metadata = retrieve_data_request_variables(experiment_id, data_request)
    except ExperimentNotFoundError as enf:
        if fallback_experiment_id is None:
            raise enf
        try_fallback = True

    if try_fallback:
        variables, metadata = retrieve_data_request_variables(fallback_experiment_id, data_request)

    result = defaultdict(dict)
    for variable in variables:
        result[variable.mip_table][variable.variable_name] = variable

    if try_fallback:
        logger.info(
            'Experiment "{exp_id}" not found in data request version "{dr_ver}".Using "{fallback_exp_id}" instead,'
            'found "{num_vars}" variables in that experiment.'.format(
                num_vars=len(variables),
                exp_id=experiment_id,
                dr_ver=data_request.version,
                fallback_exp_id=fallback_experiment_id,
            ))
    else:
        logger.info(
            'Found "{num_vars}" variables for experiment "{exp_id}" in data request version "{dr_ver}" '.format(
                num_vars=len(variables),
                exp_id=experiment_id,
                dr_ver=data_request.version))

    return dict(result), metadata


def get_data_request_variables(
        experiment_id: str, fallback_experiment_id: str = None
) -> Tuple[Dict[str, Dict[str, DataRequestVariable]], Dict[str, str]]:
    """
    Return the |MIP requested variables| for the experiment provided by the ``experient_id``
    parameter from the specified version of the |data request| and their metadata.

    :param experiment_id: The |experiment identifier|.
    :type experiment_id: str
    :param fallback_experiment_id: The fallback |experiment identifier| if the `experiment_id` is not found.
    :type fallback_experiment_id: str
    :return: The |MIP requested variables| for the experiment from the specified version of the |data request|
        and their metadata.
    :rtype: Tuple[Dict[str, Dict[str, DataRequestVariable]], Dict[str, str]]
    """
    logger = logging.getLogger(__name__)
    # Retrieve the 'MIP requested variables' for a given 'experiment' of the 'data request'.
    data_request = DataRequestWrapper()
    logger.debug('Retrieving variables for experiment "{}" from the data request'.format(experiment_id))

    return list_variables_for_experiment(data_request, experiment_id, fallback_experiment_id)


def check_variable_model_data_request(
        variable: DataRequestVariable,
        model_data_request_variables: Dict[str, Dict[str, DataRequestVariable]],
        comments: List[str]) -> DataRequestVariable:
    """
     Return the |MIP requested variable| from the version of the |data request| used to setup the |model|.

    :param variable: The |MIP requested variable|.
    :type variable: DataRequestVariable
    :param model_data_request_variables: The |MIP requested variable| from the version of the |data request|
        used to setup the |model|.
    :type model_data_request_variables: Dict[str, Dict[str, DataRequestVariable]]
    :param comments: The comments related to the |MIP requested variable|.
    :type comments: List[str]
    :return: The |MIP requested variable| from the version of the |data request| used to setup the |model|.
    :rtype: DataRequestVariable
    """
    mip_table = variable.mip_table
    variable_name = variable.variable_name

    model_variable = None

    if mip_table in model_data_request_variables:
        if variable_name in model_data_request_variables[mip_table]:
            model_variable = (model_data_request_variables[mip_table][variable_name])
        else:
            comments.append('Variable "{}/{}" not found in model data request'.format(mip_table, variable_name))
    else:
        comments.append('MIP table "{}" not found in model data request'.format(mip_table))
    return model_variable


def check_data_request_changes(
        variable: DataRequestVariable, model_variable: DataRequestVariable,
        mapping: VariableModelToMIPMapping, comments: List[str]) -> bool:
    """
    Return whether the |MIP requested variable| has changed significantly between the version of
    the |data request| used to setup the |model| and the specified version of the |data request|.

    *Note*:
    Only data request variable attributes in the `CRITICAL_FIELDS` list are checked.

    :param variable: The |MIP requested variable|.
    :type variable: DataRequestVariable
    :param model_variable: The |MIP requested variable| from the version of the |data request| used
        to setup the |model|.
    :type model_variable: DataRequestVariable
    :param mapping: The |model to MIP mapping| for the |MIP requested variable|.
    :type mapping: VariableModelToMIPMapping
    :param comments: The comments related to the |MIP requested variable|.
    :type comments: List[str]
    :return: Whether the |MIP requested variable| has changed significantly between the version of
        the |data request| used to setup the |model| and the specified version of the |data request|.
    :rtype: bool
    """
    logger = logging.getLogger(__name__)

    if model_variable is None:
        critical_data_request_changes = False
    else:
        differences = describe_differences(model_variable, variable)
        critical_fields = CRITICAL_FIELDS[:]
        # Don't check for dimension, positive and units changes if these have
        # already been accounted for in the mappings.
        if mapping:
            if set(mapping.dimension) == set(variable.dimensions):
                critical_fields.remove('dimensions')
            if positive_is_compatible(mapping.positive, variable.positive):
                critical_fields.remove('positive')
            if Unit(mapping.units).is_convertible(Unit(variable.units)):
                critical_fields.remove('units')
            else:
                log_msg = '{}: Units not OK: "{}" != "{}"'.format(
                    '{0.mip_table}/{0.variable_name}'.format(variable), mapping.units, variable.units
                )
                logger.debug(log_msg)

        # Check through the differences for critical changes.
        critical_data_request_changes = False
        for field in critical_fields:
            if field in differences:
                msg = 'Field "{}" has changed in data request between versions "{}" and "{}": {}.'.format(
                    field, model_variable.data_request.version, variable.data_request.version, differences[field])
                comments.append(msg)
                critical_data_request_changes = True
    return critical_data_request_changes


def positive_is_compatible(positive1: str, positive2: str) -> bool:
    """
    Return True if two positive values are compatible.

    :param positive1: A ``positive`` value to check.
    :type positive1: str
    :param positive2: The other``positive`` value to check.
    :type positive2: str
    :return: False if only one of the arguments supplied is None, otherwise True.
    :rtype: bool
    """
    for positive in [positive1, positive2]:
        if positive not in ALLOWED_POSITIVE:
            raise RuntimeError('Invalid positive value: "{}"'.format(repr(positive)))

    return sum([positive1 is None, positive2 is None]) != 1


def calculate_priority(mips: List[str], data_request_variable: DataRequestVariable) -> int:
    """
    Return the priority of the |MIP requested variable| given the list of |MIPs| to contribute to
    and the information about the |MIP requested variable| from the |data request|.

    *Note*: that if no |MIPs| are to be contributed to then a value of ``PRIORITY_UNSET`` is returned.

    :param mips: The list of |MIPs| to contribute to.
    :type mips: List[str]
    :param data_request_variable: The |MIP requested variable| from the |data request|.
    :type data_request_variable: DataRequestVariable
    :return: The priority for the |MIP requested variable|.
    :rtype: int
    """
    priority = PRIORITY_UNSET
    for requesting_mip, mip_priority in (iter(data_request_variable.priorities.items())):
        if requesting_mip in mips:
            priority = min(priority, mip_priority)
    return priority


def check_priority(priority: int, max_priority: int, comments: List[str]) -> bool:
    """
    Return whether the priority provided to the ``priority`` parameter is equal to or less
    than the maximum priority provided to the ``max_priority`` parameter.

    *Note*: that high priority is 1, low priority is 3.

    :param priority: The priority of the |MIP requested variable| (after resolving |MIP| requests).
    :type priority: int
    :param max_priority: The maximum priority to consider.
    :type max_priority: int
    :param comments: The comments related to the |MIP requested variable|.
    :type comments: List[str]
    :return: Whether the priority is equal to or less than the maximum priority.
    :rtype: bool
    """
    priority_ok = priority <= max_priority
    if not priority_ok:
        comments.append('Priority={} > MAX_PRIORITY={}'.format(priority, max_priority))
        if priority == PRIORITY_UNSET:
            comments.append('No active MIPs for this variable')
    return priority_ok


def calculate_ensemble_size(mips: List[str], data_request_variable: DataRequestVariable) -> int:
    """
    Return the ensemble size of the |MIP requested variable| given the list of |MIPs| to contribute
    to and the information about the |MIP requested variable| from the |data request|.

    *Note*: that if no |MIPs| are to be contributed to, then a value of 0 should be returned.

    :param mips: The list of |MIPs| to contribute to.
    :type mips: List[str]
    :param data_request_variable: The |MIP requested variable| from the |data request|.
    :type data_request_variable: DataRequestVariable
    :return: The largest required ensemble size for the |MIP requested variable|
    :rtype: int
    """
    ensemble_size = 0
    for requesting_mip, mip_ensemble_size in (iter(data_request_variable.ensemble_sizes.items())):
        if requesting_mip in mips:
            ensemble_size = max(ensemble_size, mip_ensemble_size)
    return ensemble_size
