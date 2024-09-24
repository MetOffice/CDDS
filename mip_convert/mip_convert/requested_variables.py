# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
import logging

from iris.cube import CubeList
from typing import List, Dict, Tuple

from mip_convert.configuration.text_config import HybridHeightConfig, SitesConfig
from mip_convert.configuration.python_config import UserConfig

from mip_convert.load import load

from mip_convert.new_variable import VariableMetadata
from mip_convert.configuration.json_config import MIPConfig
from mip_convert.configuration.python_config import ModelToMIPMappingConfig

from mip_convert.save import save
from mip_convert.save.cmor import cmor_lite
from mip_convert.mip_table import get_variable_model_to_mip_mapping, get_variable_mip_metadata


def get_requested_variables(
        user_config: UserConfig, requested_stream_ids: List[str]) -> Dict[Tuple[str, str, str], List[str]]:
    """
    Return the |MIP requested variable names| based on the
    |stream identifiers| provided by the ``requested_stream_ids``
    parameter. If the value provided in the ``requested_stream_ids``
    parameter is ``None`` the |MIP requested variable names| for all
    |stream identifiers| are returned.

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :param requested_stream_ids: the requested |stream identifiers|
    :type requested_stream_ids: list
    :return: the |MIP requested variable names| in the form
        ``{(stream_id_1, mip_table_name_1): [var_1, var_2]}``
    :rtype: dictionary
    :raises RuntimeError: if there are no
        |MIP requested variable names| defined in the
        |user configuration file|
    """
    if requested_stream_ids is None:
        requested_variables = user_config.streams_to_process
    else:
        requested_variables = {}
        streams_to_process = user_config.streams_to_process
        for ((stream_id, substream, mip_table_name), variable_names) in list(streams_to_process.items()):
            if stream_id in requested_stream_ids:
                requested_variables[(stream_id, substream, mip_table_name)] = variable_names

    if not requested_variables:
        raise RuntimeError('There are no MIP requested variable names defined in the user configuration file')

    return requested_variables


def produce_mip_requested_variable(
        variable_name: str, stream_id: str, substream: str, mip_table: MIPConfig, user_config: UserConfig,
        site_information: SitesConfig, hybrid_height_information: HybridHeightConfig, replacement_coordinates: CubeList,
        model_to_mip_mappings: ModelToMIPMappingConfig, filenames: List[str]) -> None:
    """
    Produce the |output netCDF files| for the |MIP requested variable|.

    Parameters
    ----------
    variable_name: string
        The |MIP requested variable name|.
    stream_id: string
        The |stream identifier|.
    substream: string
        The substream identifier.
    mip_table: :class:`configuration.MIPConfig`
        Access to the |MIP table|.
    user_config: :class:`configuration.UserConfig`
        Access to the |user configuration file|.
    site_information: :class:`SitesConfig`
        Information related to the sites.
    hybrid_height_information: list of :class:`HybridHeightConfig`
        Information related to the hybrid heights.
    replacement_coordinates: :class:`iris.cube.CubeList`
        The replacement coordinates.
    model_to_mip_mappings: :class:`configuration.ModelToMIPMappingConfig`
        Access to the |model to MIP mappings|.
    filenames: list of strings
        The filenames (including the full path) of the files required
        to produce the |output netCDF files| for the
        |MIP requested variable|.
    """
    # Retrieve the logger.
    logger = logging.getLogger(__name__)
    logger.debug('Creating MIP requested variable "{}"'.format(variable_name))

    # Retrieve the 'model to MIP mapping' for the 'MIP requested variable'.
    variable_model_to_mip_mapping = get_variable_model_to_mip_mapping(model_to_mip_mappings,
                                                                      variable_name,
                                                                      mip_table.id)

    # Retrieve the information about the 'MIP requested variable name' from the 'MIP table'.
    variable_mip_metadata = get_variable_mip_metadata(variable_name, mip_table)

    # Create the 'VariableMetadata' object, which contains all the information related to a 'MIP requested variable'.
    variable_metadata = VariableMetadata(
        variable_name, stream_id, substream, mip_table.name, variable_mip_metadata, site_information,
        hybrid_height_information, replacement_coordinates, variable_model_to_mip_mapping,
        user_config.atmos_timestep, user_config.run_bounds, user_config.calendar, user_config.base_date,
        user_config.deflate_level, user_config.shuffle, user_config.reference_time, user_config.masking,
        user_config.halo_removals
    )

    # Load the data from the 'model output files' and store each 'input variable' in the 'Variable' object
    # (which corresponds to a 'MIP requested variable').
    variable = load(filenames, variable_metadata)
    logger.debug('Variable object contains: {}'.format(variable.info))

    # Create the CMOR saver.
    saver = cmor_lite.get_saver(mip_table.name, variable_name)

    # Process the data by performing the appropriate 'model to MIP mapping', then save the 'MIP output variable'
    # to an 'output netCDF file'.
    for time_slice in variable.slices_over():
        time_slice.process()
        logger.debug('MIP output variable contains: {}'.format(time_slice.info))
        save(time_slice, saver)

    # Close the 'output netCDF file'.
    cmor_lite.close(saver.varid)
    logger.info('Successfully produced "{}: {}"'.format(mip_table.name, variable_name))
