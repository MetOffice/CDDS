# (C) British Crown Copyright 2018-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable = no-member
"""This module contains the code to identify critical changes to variables
between different versions of the data request
"""
from collections import defaultdict
import logging

from cf_units import Unit

from cdds.data_request_interface.load import (DataRequestWrapper,
                                              ExperimentNotFoundError)
from cdds.data_request_interface.variables import (
    retrieve_data_request_variables, describe_differences)

from cdds.prepare.constants import (ALLOWED_POSITIVE, CRITICAL_FIELDS,
                                    PRIORITY_UNSET)


def list_variables_for_experiment(data_request, experiment_id,
                                  fallback_experiment_id=None):
    """Return the |MIP requested variables| for the experiment provided by
    the ``experient_id`` parameter from the specified version of the
    |data request|.

    The returned |MIP requested variables| are organised by |MIP table|,
    then |MIP requested variable name|.

    Parameters
    ----------
    data_request : :class:`cdds.data_request_interface.load.DataRequestWrapper`
        The specified version of the |data request|.
    experiment_id : str
        The |experiment identifier|.

    Returns
    -------
    dict of :class:`DataRequestVariables`
        The |MIP requested variables| for the experiment from the
        specified version of the |data request|.
    """
    logger = logging.getLogger(__name__)
    try_fallback = False
    try:
        variables, metadata = retrieve_data_request_variables(experiment_id,
                                                              data_request)
    except ExperimentNotFoundError as enf:
        if fallback_experiment_id is None:
            raise enf
        try_fallback = True

    if try_fallback:
        variables, metadata = retrieve_data_request_variables(
            fallback_experiment_id,
            data_request)

    result = defaultdict(dict)
    for variable in variables:
        result[variable.mip_table][variable.variable_name] = variable

    if try_fallback:
        logger.info(
            'Experiment "{exp_id}" not found in data request version '
            '"{dr_ver}". Using "{fallback_exp_id}" instead, found '
            '"{num_vars}" variables in that experiment.'.format(
                num_vars=len(variables),
                exp_id=experiment_id,
                dr_ver=data_request.version,
                fallback_exp_id=fallback_experiment_id,
            ))
    else:
        logger.info(
            'Found "{num_vars}" variables for experiment "{exp_id}" in '
            'data request version "{dr_ver}" '.format(
                num_vars=len(variables),
                exp_id=experiment_id,
                dr_ver=data_request.version))

    return dict(result), metadata


def get_data_request_variables(data_request_version,
                               experiment_id, data_request_base_dir,
                               fallback_experiment_id=None):
    """Return the |MIP requested variables| for the experiment provided by
    the ``experient_id`` parameter from the specified version of the
    |data request|.

    The returned |MIP requested variables| are organised by |MIP table|,
    then |MIP requested variable name|.

    Parameters
    ----------
    data_request_version : str
        The version of the |data request|.
    experiment_id : str
        The |experiment identifier|.

    Returns
    -------
    dict of :class:`DataRequestVariables`
        The |MIP requested variables| for the experiment from the
        specified version of the |data request|.
    """
    logger = logging.getLogger(__name__)
    # Retrieve the 'MIP requested variables' for a given 'experiment' from
    # the specified version of the 'data request'.
    logger.debug('Loading data request version "{}"'
                 ''.format(data_request_version))
    data_request = DataRequestWrapper(data_request_version,
                                      data_request_base_dir)
    logger.debug('Retrieving variables for experiment "{}" from the '
                 'data request'.format(experiment_id))

    data_request_variables, metadata = list_variables_for_experiment(
        data_request, experiment_id, fallback_experiment_id)
    return data_request_variables, metadata


def check_variable_model_data_request(variable, model_data_request_variables,
                                      comments):
    """Return the |MIP requested variable| from the version of the
    |data request| used to setup the |model|.

    Parameters
    ----------
    variable : :class:`DataRequestVariable`
        The |MIP requested variable|.
    model_data_request_variable : dict of :class:`DataRequestVariable`
        The |MIP requested variable| from the version of the
        |data request| used to setup the |model|.
    comments : list
        The comments related to the |MIP requested variable|.

    Returns
    -------
    :class:`DataRequestVariable` or None
        The |MIP requested variable| from the version of the
        |data request| used to setup the |model|.
    """
    mip_table = variable.mip_table
    variable_name = variable.variable_name

    model_variable = None

    if mip_table in model_data_request_variables:
        if variable_name in model_data_request_variables[mip_table]:
            model_variable = (
                model_data_request_variables[mip_table][variable_name])
        else:
            comments.append('Variable "{}/{}" not found in model data '
                            'request'.format(mip_table, variable_name))
    else:
        comments.append('MIP table "{}" not found in model data '
                        'request'.format(mip_table))
    return model_variable


def check_data_request_changes(variable, model_variable, mapping, comments):
    """Return whether the |MIP requested variable| has changed
    significantly between the version of the |data request| used to
    setup the |model| and the specified version of the |data request|.

    Parameters
    ----------
    variable : :class:`DataRequestVariable`
        The |MIP requested variable|.
    model_variable : :class:`DataRequestVariable`
        The |MIP requested variable| from the version of the
        |data request| used to setup the |model|.
    mapping : :class:`VariableModelToMIPMapping`
        The |model to MIP mapping| for the |MIP requested variable|.
    comments : list
        The comments related to the |MIP requested variable|.

    Returns
    -------
    bool
        Whether the |MIP requested variable| has changed significantly
        between the version of the |data request| used to setup the
        |model| and the specified version of the |data request|.

    Notes
    -----
    Only data request variable attributes in the `CRITICAL_FIELDS` list
    are checked.
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
                logger.debug(
                    '{}: Units not OK: "{}" != "{}"'.format(
                        '{0.mip_table}/{0.variable_name}'.format(variable),
                        mapping.units, variable.units))
        # Check through the differences for critical changes.
        critical_data_request_changes = False
        for field in critical_fields:
            if field in differences:
                msg = ('Field "{}" has changed in data request '
                       'between versions "{}" and "{}": {}.'
                       '').format(field,
                                  model_variable.data_request.version,
                                  variable.data_request.version,
                                  differences[field])
                comments.append(msg)
                critical_data_request_changes = True
    return critical_data_request_changes


def positive_is_compatible(positive1, positive2):
    """Return True if two positive values are compatible.

    Parameters
    ----------
    positive1 : str
        A ``positive`` value to check.
    positive2 : str
        The other``positive`` value to check.

    Returns
    -------
    bool
        False if only one of the arguments supplied is None, otherwise
        True.

    Raises
    ------
    RuntimeError
        If either of the supplied arguments are not in the allowed list
        (``ALLOWED_POSITIVE``).
    """
    for positive in [positive1, positive2]:
        if positive not in ALLOWED_POSITIVE:
            raise RuntimeError('Invalid positive value: "{}"'
                               ''.format(repr(positive)))

    return sum([positive1 is None, positive2 is None]) != 1


def calculate_priority(mips, data_request_variable):
    """Return the priority of the |MIP requested variable| given the list
    of |MIPs| to contribute to and the information about the
    |MIP requested variable| from the |data request|.

    Note that if no |MIPs| are to be contributed to then a value of
    ``PRIORITY_UNSET`` is returned.

    Parameters
    ----------
    mips : list
        The list of |MIPs| to contribute to.
    data_request_variable : :class:`DataRequestVariable`
        The |MIP requested variable| from the |data request|.

    Returns
    -------
    int
        The priority for the |MIP requested variable|.
    """
    priority = PRIORITY_UNSET
    for requesting_mip, mip_priority in (
            iter(data_request_variable.priorities.items())):
        if requesting_mip in mips:
            priority = min(priority, mip_priority)
    return priority


def check_priority(priority, max_priority, comments):
    """Return whether the priority provided to the ``priority`` parameter
    is equal to or less than the maximum priority provided to the
    ``max_priority`` parameter.

    Note that high priority is 1, low priority is 3.

    Parameters
    ----------
    priority : int
        The priority of the |MIP requested variable| (after resolving
        |MIP| requests).
    max_priority : int
        The maximum priority to consider.
    comments : list
        The comments related to the |MIP requested variable|.

    Returns
    -------
    bool
        Whether the priority is equal to or less than the maximum
        priority.
    """
    priority_ok = priority <= max_priority
    if not priority_ok:
        comments.append('Priority={} > MAX_PRIORITY={}'
                        ''.format(priority, max_priority))
        if priority == PRIORITY_UNSET:
            comments.append('No active MIPs for this variable')
    return priority_ok


def calculate_ensemble_size(mips, data_request_variable):
    """Return the ensemble size of the |MIP requested variable| given the list
    of |MIPs| to contribute to and the information about the
    |MIP requested variable| from the |data request|.

    Note that if no |MIPs| are to be contributed to, then a value of
    0 should be returned.

    Parameters
    ----------
    mips : list
        The list of |MIPs| to contribute to.
    data_request_variable : :class:`DataRequestVariable`
        The |MIP requested variable| from the |data request|.

    Returns
    -------
    int
        The largest required ensemble size for the |MIP requested variable|
    """
    ensemble_size = 0
    for requesting_mip, mip_ensemble_size in (
            iter(data_request_variable.ensemble_sizes.items())):
        if requesting_mip in mips:
            ensemble_size = max(ensemble_size, mip_ensemble_size)
    return ensemble_size
