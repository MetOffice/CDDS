# (C) British Crown Copyright 2020-2021, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`common.py` module contains the helping resp. common
functions for the cdd_prepare module.
"""
import configparser

from collections import defaultdict
from hadsdk.ancils import remove_ancils_from_mapping
from mip_convert.request import get_model_to_mip_mappings, get_variable_model_to_mip_mapping


def retrieve_mappings(data_request_variables, mip_era, model_id):
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
    mappings = defaultdict(dict)
    for mip_table_id in data_request_variables:
        mip_table_name = '{}_{}'.format(mip_era, mip_table_id)
        model_to_mip_mappings = get_model_to_mip_mappings(model_id, mip_table_name)
        for variable_name in data_request_variables[mip_table_id]:
            try:
                mapping = get_variable_model_to_mip_mapping(model_to_mip_mappings, variable_name, mip_table_id)
                mapping = remove_ancils_from_mapping(mapping)
            except (RuntimeError, configparser.Error) as exc:
                mapping = exc
            mappings[mip_table_id][variable_name] = mapping
    return mappings
