# (C) British Crown Copyright 2019-2025, Met Office.
# Please see LICENSE.md for license details.
"""The :mod:`ancils` module contains functions for removing ancillaries from the |model to MIP mappings|."""
import logging

from cdds.common.constants import ANCIL_VARIABLES
from cdds.common.plugins.grid import GridType
from cdds.common.plugins.plugins import PluginStore


def remove_ancils_from_mapping(mapping, model_id):
    """Return the |model to MIP mapping| for a |MIP requested variable| with any ancillaries removed.

    Parameters
    ----------
    mapping: :class:`mip_convert.new_variable.VariableModelToMIPMapping`
        The |model to MIP mapping| for a |MIP requested variable|.
    model_id : str
        The model ID for that the MIP mapping is for

    Returns
    -------
    :class:`mip_convert.new_variable.VariableModelToMIPMapping`
        The |model to MIP mapping| for a |MIP requested variable|
        with any ancillaries removed.
    """
    logger = logging.getLogger(__name__)
    filtered_loadables = []
    removed_ancil_names = []

    plugin = PluginStore.instance().get_plugin()
    ancil_variables = plugin.models_parameters(model_id).all_ancil_variables()
    ancil_variables.extend(ANCIL_VARIABLES)

    for loadable in mapping.loadables:
        # Strip bracket constraints to isolate the bare identifier (e.g. 'mask_3D_U' from
        # 'mask_3D_U[depth<1]' or 'm01s00i505' from 'm01s00i505[lbproc=128]'), allowing for
        # direct matching against NetCDF and PP ancil variables.
        base_loadable_name = loadable.name.split('[')[0]
        if base_loadable_name not in ancil_variables:
            filtered_loadables.append(loadable)
        else:
            removed_ancil_names.append(loadable.name)

    variable_key = ('{0.mip_table_id}/{0.mip_requested_variable_name}'
                    '').format(mapping)
    if removed_ancil_names:
        logger.debug(
            'Removed the following ancillaries from the model to MIP mapping '
            'for "{}": "{}"'
            ''.format(variable_key, '", "'.join(removed_ancil_names)))
        mapping.loadables = filtered_loadables

    return mapping
