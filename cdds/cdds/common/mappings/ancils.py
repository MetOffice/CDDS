# (C) British Crown Copyright 2019-2022, Met Office.
# Please see LICENSE.md for license details.
"""
The :mod:`ancils` module contains functions for removing ancillaries
from the |model to MIP mappings|.
"""
import logging

from cdds.common.constants import ANCIL_VARIABLES
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore


def remove_ancils_from_mapping(mapping):
    """
    Return the |model to MIP mapping| for a |MIP requested variable|
    with any ancillaries removed.

    Parameters
    ----------
    mapping: \
        :class:`mip_convert.new_variable.VariableModelToMIPMapping`
        The |model to MIP mapping| for a |MIP requested variable|.

    Returns
    -------
    : :class:`mip_convert.new_variable.VariableModelToMIPMapping`
        The |model to MIP mapping| for a |MIP requested variable|
        with any ancillaries removed.
    """
    logger = logging.getLogger(__name__)
    filtered_loadables = []
    removed_loadable_names = []

    plugin = PluginStore.instance().get_plugin()
    ancil_variables = plugin.models_parameters(mapping.model_id).all_ancil_variables()
    ancil_variables.extend(ANCIL_VARIABLES)

    for loadable in mapping.loadables:
        if loadable.name not in ancil_variables and loadable.stash not in ancil_variables:
            filtered_loadables.append(loadable)
        else:
            removed_loadable_names.append(loadable.name)

    variable_key = ('{0.mip_table_id}/{0.mip_requested_variable_name}'
                    '').format(mapping)
    if removed_loadable_names:
        logger.debug(
            'Removed the following ancillaries from the model to MIP mapping '
            'for "{}": "{}"'
            ''.format(variable_key, '", "'.join(removed_loadable_names)))
        mapping.loadables = filtered_loadables

    return mapping
