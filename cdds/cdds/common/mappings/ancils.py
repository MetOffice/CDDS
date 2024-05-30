# THIS FILE IS PART OF CDDS
# Copyright (C) British Crown (Met Office) & Contributors.
# Licenced under the BSD 3 clause license https://opensource.org/license/bsd-3-clause
# See the LICENSE file in the top level of this repository for full details.
"""
The :mod:`ancils` module contains functions for removing ancillaries
from the |model to MIP mappings|.
"""
import logging

from cdds.common.constants import ANCIL_VARIABLES


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
    for loadable in mapping.loadables:
        if loadable.name not in ANCIL_VARIABLES and loadable.stash not in ANCIL_VARIABLES:
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
