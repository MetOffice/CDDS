# (C) British Crown Copyright 2015-2025, Met Office.
# Please see LICENSE.md for license details.
# pylint: disable=no-member, logging-format-interpolation
"""
Produce the |output netCDF files| for a |MIP| using
|model output files| that cover a single uninterrupted time period and
information provided in the |user configuration file|.
"""
import iris
import logging

from mip_convert.save.cmor import cmor_lite
from mip_convert.requirements import software_versions
from mip_convert.requested_variables import get_requested_variables, produce_mip_requested_variable
from mip_convert.save.setup_cmor import setup_cmor

from mip_convert.configuration.text_config import HybridHeightConfig, SitesConfig
from mip_convert.configuration.python_config import UserConfig

from mip_convert.mip_table import get_model_to_mip_mappings
from mip_convert.mip_table import get_mip_table
from mip_convert.model_output_files import get_files_to_produce_output_netcdf_files


def convert(parameters):
    """
    Produce the |output netCDF files| for a |MIP| using
    |model output files|.

    If a |MIP requested variable| is unable to be produced, for
    example, if there is:

    * no |model to MIP mapping| corresponding to the
      |MIP requested variable name|
    * no entry in the |MIP table| corresponding to the
      |MIP requested variable name|
    * a problem with loading the relevant data from the
      |model output files|, processing the |input variable| /
      |input variables| or saving the |MIP output variable|

    no exceptions are raised; instead, an appropriate ``CRITICAL``
    message will be written to the log and the exit code will be set
    equal to 2.

    :param parameters: the names of the parameters and their validated
                       values
    :type parameters: :class:`argparse.Namespace` object
    """
    # Retrieve the logger.
    exit_code = 0
    logger = logging.getLogger(__name__)
    logger.info('*** Starting conversions ***')

    # Read and validate the 'user configuration file'.
    user_config = UserConfig(parameters.config_file, software_versions())

    # Setup CMOR in preparation for writing the 'output netCDF files', which includes reading and validating
    # the associated Controlled Vocabularies (CV) file, if defined, and ensuring that the required global options exist.
    setup_cmor(user_config, parameters.relaxed_cmor)

    # Read and validate the sites file.
    site_information = None
    if user_config.sites_file is not None:
        site_information = SitesConfig(user_config.sites_file)

    # Read and validate the hybrid heights file.
    hybrid_height_information = None
    if user_config.hybrid_heights_files is not None:
        hybrid_height_information = [HybridHeightConfig(hybrid_heights_file)
                                     for hybrid_heights_file in user_config.hybrid_heights_files]

    # Load the replacement coordinates file.
    replacement_coordinates = None
    if user_config.replacement_coordinates_file:
        replacement_coordinates = iris.load(user_config.replacement_coordinates_file)

    # Retrieve the 'MIP requested variable names' from the 'user configuration file'.
    requested_variables = get_requested_variables(user_config, parameters.stream_identifiers)

    # For each 'MIP requested variable name' produce the
    # 'output netCDF files'.
    total_number_of_variables_with_errors = 0
    total_number_of_variables = 0
    for (stream_id, substream, mip_table_name), variable_names in list(requested_variables.items()):
        msg_template = 'MIP requested variable names for stream identifier '
        if substream is None:
            msg_template += '"{stream_id}" and MIP table "{mip_table_name}": "{variable_names}"'
        else:
            msg_template += '"{stream_id}", substream {substream}, and MIP table "{mip_table_name}": "{variable_names}"'

        logger.debug(msg_template.format(stream_id=stream_id,
                                         mip_table_name=mip_table_name,
                                         substream=substream,
                                         variable_names=variable_names))

        # Determine the list of filenames required to produce the
        # 'output netCDF files' for the 'MIP requested variables'.
        filenames = get_files_to_produce_output_netcdf_files(
            user_config.root_load_path, user_config.suite_id, stream_id, substream, user_config.ancil_files
        )

        # Read and validate the 'model to MIP mappings'.
        model_to_mip_mappings = get_model_to_mip_mappings(user_config.source_id, mip_table_name)

        # Read and validate the 'MIP table'.
        mip_table_name_json = mip_table_name + '.json'
        mip_table = get_mip_table(user_config.inpath, mip_table_name_json)

        for variable_name in variable_names:
            total_number_of_variables += 1
            try:
                produce_mip_requested_variable(variable_name, stream_id, substream, mip_table, user_config,
                                               site_information, hybrid_height_information, replacement_coordinates,
                                               model_to_mip_mappings, filenames)
            except Exception as error:
                total_number_of_variables_with_errors += 1
                message = 'Unable to produce MIP requested variable "{}" for "{}": {}'
                logger.critical(message.format(variable_name, mip_table_name, error))
                logger.exception(error)

    if total_number_of_variables_with_errors == total_number_of_variables:
        logger.info('Critical Errors found in all variables, therefore MIP convert has failed.')
        exit_code = 1
    elif total_number_of_variables_with_errors > 0:
        exit_code = 2

    # Close CMOR.
    cmor_lite.close()
    logger.info('*** Finished conversions ***')
    return exit_code
