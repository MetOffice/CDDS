# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable=no-member, logging-format-interpolation
"""
Produce the |output netCDF files| for a |MIP| using
|model output files| that cover a single uninterrupted time period and
information provided in the |user configuration file|.
"""
import glob
import iris
import logging
import os

from mip_convert.configuration.cv_config import CVConfig
from mip_convert.configuration.json_config import MIPConfig
from mip_convert.configuration.python_config import UserConfig, ModelToMIPMappingConfig
from mip_convert.configuration.text_config import HybridHeightConfig, SitesConfig

from mip_convert.common import RelativePathError

from mip_convert.load import load
from mip_convert.load.pp.pp import PpError
from mip_convert.load.pp.pp_axis import PpAxisError, ExtractorException
from mip_convert.load.pp.pp_variable import PpVariableError
from mip_convert.load.pp.aggregator import AggregatorError

from mip_convert.model_date import CdDateError
from mip_convert.new_variable import VariableMetadata, VariableModelToMIPMapping, VariableMIPMetadata

from mip_convert.process import REQUIRED_OPTIONS
from mip_convert.process.mapping_config import MappingTableError
from mip_convert.process.process import ProcessorError
from mip_convert.process.quality_control import OutOfBoundsError

from mip_convert.save import save
from mip_convert.save.cmor import cmor_lite
from mip_convert.save.cmor.cmor_dataset import Dataset
from mip_convert.requirements import software_versions
from mip_convert.variable import VariableError


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
    exit_code = 0

    # Retrieve the logger.
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

    known_errors = (
        ValueError, IOError, PpError, AggregatorError, PpAxisError,
        ExtractorException, PpVariableError,
        VariableError, RelativePathError, MappingTableError,
        OutOfBoundsError, CdDateError, ProcessorError, RuntimeError)

    # For each 'MIP requested variable name' produce the
    # 'output netCDF files'.
    count = 0
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
        filenames = get_input_files(
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
            except known_errors as known_error:
                exit_code = 2
                message = 'Unable to produce MIP requested variable "{}" for "{}": {}'
                logger.critical(message.format(variable_name, mip_table_name, known_error))
                logger.exception(known_error)
            except Exception as error:
                count += 1
                exit_code = 2
                message = 'Unable to produce MIP requested variable "{}" for "{}": {}'
                logger.critical(message.format(variable_name, mip_table_name, error))
                logger.exception(error)
                continue

    if count == total_number_of_variables:
        logger.info('Critical Errors of unknown type found in all variables, therefore MIP convert has failed.')
        exit_code = 1

    # Close CMOR.
    cmor_lite.close()
    logger.info('*** Finished conversions ***')
    return exit_code


def setup_cmor(user_config, relaxed_cmor=False):
    """
    Setup |CMOR| in preparation for writing the |output netCDF files|.

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :param relaxed_cmor: If true then CMOR will not perform CMIP6 validation
    :type relaxed_cmor: bool
    """
    logger = logging.getLogger(__name__)
    logger.debug('Setup CMOR:')
    logger.debug('*' * 20)
    cmor_lite.setup(user_config)
    cmor_lite.dataset(get_cmor_dataset(user_config, relaxed_cmor))
    logger.debug('*' * 20)


def produce_mip_requested_variable(
        variable_name, stream_id, substream, mip_table, user_config, site_information, hybrid_height_information,
        replacement_coordinates, model_to_mip_mappings, filenames):
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
        user_config.deflate_level, user_config.shuffle, user_config.reference_time, user_config.masking
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


def get_cmor_dataset(user_config, relaxed_cmor=False):
    """
    Return the items required for ``cmor_dataset_json``.

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :param relaxed_cmor: If true no cmip6 validation will be run
    :type relaxed_cmor: bool
    :return: the items required for ``cmor_dataset_json``
    :rtype: :class:`save.cmor.cmor_dataset.Dataset` object
    """
    # Read and validate the associated Controlled Vocabularies (CV) file, if defined.
    cv_config = get_cv_config(user_config)
    cmor_dataset = Dataset(user_config, cv_config, relaxed_cmor)
    # Ensure the required global attributes exist, then ensure the values conform to the CVs for those attributes
    # that are not currently checked by CMOR.
    cmor_dataset.validate_required_global_attributes()
    return cmor_dataset


def get_cv_config(user_config):
    """
    Return the Controlled Vocabularies (CV).

    :param user_config: the |user configuration file|
    :type user_config: :class:`configuration.UserConfig` object
    :return: the Controlled Vocabularies (CV)
    :rtype: :class:`configuration.CVConfig` object
    """
    logger = logging.getLogger(__name__)
    cv_file_name = '{}_CV.json'.format(user_config.mip_era)
    cv_path = os.path.join(user_config.inpath, cv_file_name)
    cv_config = CVConfig(cv_path)
    logger.debug('CV file "{}" exists'.format(cv_path))
    return cv_config


def get_requested_variables(user_config, requested_stream_ids):
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


def get_input_files(root_load_path, suite_id, stream_id, substream, ancil_files):
    """
    Return the filenames (including the full path) of the files
    required to produce the |output netCDF files| for the
    |MIP requested variables|.

    :param root_load_path: the full path to the root directory
        containing the |model output files|
    :type root_load_path: string
    :param suite_id: the |run identifier| of the model
    :type suite_id: string
    :param stream_id: the |stream identifier|
    :type stream_id: string
    :param ancil_files: the filenames (including the full path) of any
        ancillary files
    :type ancil_files: list of strings
    :return: the filenames (including the full path) of the files
        required to produce the |output netCDF files| for the
        |MIP requested variables|.
    :rtype: list of strings
    :raises IOError: if no |model output files| are found in the
        directory ``/<root_load_path>/<suite_id>/<stream_id>/``
    """
    logger = logging.getLogger(__name__)

    # Construct the names of the 'model output files'.
    filenames = []
    if stream_id != 'ancil':
        model_output_dir = os.path.join(root_load_path, suite_id, stream_id)

        for extension in ['.pp', '.nc']:
            if substream is None:
                model_output_files = _get_model_output_files(model_output_dir, extension)
            else:
                model_output_files = _get_model_output_files(model_output_dir, substream + extension)

            if model_output_files:
                logger.debug('Using all "*{}" model output files from "{}"'.format(extension, model_output_dir))
                filenames.extend(model_output_files)

        if not filenames:
            logger.warning('No model output files in "{}"'.format(model_output_dir))

    # Add any ancillary files to the list.
    if ancil_files is not None:
        logger.debug('Using ancillary files "{}"'.format(ancil_files))
        filenames.extend(ancil_files)

    if not filenames:
        raise IOError('No model output files in "{}" or ancillaries'.format(model_output_dir))

    return filenames


def _get_model_output_files(model_output_dir, extension):
    filename_pattern = '*{}'.format(extension)
    return glob.glob(os.path.join(model_output_dir, filename_pattern))


def get_model_to_mip_mappings(model_id, mip_table_name):
    """
    Return an object that enables access to the
    |model to MIP mappings|.

    :param model_id: the |model identifier|
    :type model_id: string
    :param mip_table_name: the name of the |MIP table|
    :type mip_table_name: string
    :return: access to the |model to MIP mappings|
    :rtype: :class:`configuration.ModelToMIPMappingConfig` object
    """
    # Read and validate the 'model to MIP mappings'.
    logger = logging.getLogger(__name__)
    dirname = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'process')
    suffix = 'mappings.cfg'

    # Always load the common mappings.
    pathname = os.path.join(dirname, 'common_{suffix}'.format(suffix=suffix))
    model_to_mip_mappings = ModelToMIPMappingConfig(pathname, model_id)
    logger.debug('Reading the common model to MIP mappings')

    # Then load the specific mappings based on the hierarchy, if they exist.
    mip_table_id = mip_table_name.split('_')[1]
    base_model_configuration = model_id.split('-')[0]
    hierarchy = [
        '{mip_table_id}_{suffix}'.format(mip_table_id=mip_table_id, suffix=suffix),
        '{base_model_configuration}_{suffix}'.format(base_model_configuration=base_model_configuration, suffix=suffix),
        '{base_model_configuration}_{mip_table_id}_{suffix}'.format(base_model_configuration=base_model_configuration,
                                                                    mip_table_id=mip_table_id,
                                                                    suffix=suffix),
        '{model_configuration}_{suffix}'.format(model_configuration=model_id, suffix=suffix),
        '{model_configuration}_{mip_table_id}_{suffix}'.format(model_configuration=model_id,
                                                               mip_table_id=mip_table_id,
                                                               suffix=suffix),
    ]

    for filename in hierarchy:
        pathname = os.path.join(dirname, filename)
        if os.path.isfile(pathname):
            model_to_mip_mappings.read(pathname)
            logger.debug('Reading "{filename}"'.format(filename=filename))

    return model_to_mip_mappings


def get_mip_table(mip_table_dir, mip_table_name):
    """
    Return an object that enables access to the |MIP table|.

    :param mip_table_dir: the name of the validated |MIP table|
        directory
    :type mip_table_dir: string
    :param mip_table_name: the name of the |MIP table|
    :type mip_table_name: string
    :return: access to the |MIP table|
    :rtype: :class:`configuration.MIPConfig` object
    """
    # Read and validate the 'MIP table'.
    logger = logging.getLogger(__name__)
    mip_table_path = os.path.join(mip_table_dir, mip_table_name)
    mip_table = MIPConfig(mip_table_path)
    logger.debug('MIP table "{}" exists'.format(mip_table_path))
    return mip_table


def get_variable_model_to_mip_mapping(model_to_mip_mappings, variable_name, mip_table_id):
    """
    Return an object that enables access to the
    |model to MIP mappings| for a specific |MIP requested variable|.

    :param model_to_mip_mappings: the |model to MIP mappings|
    :type model_to_mip_mappings:
        :class:`configuration.ModelToMIPMappingConfig` object
    :param variable_name: the |MIP requested variable name|
    :type variable_name: string
    :param mip_table_id: the |MIP table identifier|
    :type mip_table_id: string
    :return: access to the |model to MIP mappings| for a specific
        |MIP requested variable|
    :rtype: :class:`new_variable.VariableModelToMIPMapping` object
    :raises RuntimeError: if any of the required options
        (``expression``, ``mip_table_id``, ``positive``, ``units``) are
        not available for the |MIP requested variable|
    """
    model_to_mip_mapping = model_to_mip_mappings.select_mapping(variable_name, mip_table_id)

    for option in REQUIRED_OPTIONS:
        if option not in model_to_mip_mapping:
            message = 'No "{}" available for "{}" for "{}"'
            raise RuntimeError(message.format(option, variable_name, mip_table_id))

    # Create the object that enables access to the 'model to MIP mappings' for a specific 'MIP requested variable'.
    variable_model_to_mip_mapping = VariableModelToMIPMapping(variable_name,
                                                              model_to_mip_mapping,
                                                              model_to_mip_mappings.model_id)
    return variable_model_to_mip_mapping


def get_variable_mip_metadata(variable_name, mip_table):
    """
    Return an object that enables access to the |MIP table| for a
    specific |MIP requested variable|.

    :param variable_name: the |MIP requested variable name|
    :type variable_name: string
    :param mip_table: the |MIP table|
    :type mip_table: :class:`configuration.MIPConfig` object
    :return: access to the |MIP table| for a specific
        |MIP requested variable| and additional constraint information
    :rtype: :class:`new_variable.VariableMIPMetadata` object
    :raises KeyError: if |MIP requested variable name| does not exist
        in the MIP table
    """
    try:
        variable_info = mip_table.variables[variable_name]
    except KeyError:
        message = 'Variable "{variable_name}" does not exist in MIP table "{mip_table_name}"'
        raise KeyError(message.format(variable_name=variable_name, mip_table_name=mip_table.name))

    variable_mip_metadata = VariableMIPMetadata(variable_info, mip_table.axes)
    return variable_mip_metadata
