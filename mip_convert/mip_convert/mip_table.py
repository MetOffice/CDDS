# (C) British Crown Copyright 2015-2022, Met Office.
# Please see LICENSE.rst for license details.
import logging
import os

from mip_convert.configuration.json_config import MIPConfig
from mip_convert.configuration.python_config import ModelToMIPMappingConfig
from mip_convert.new_variable import VariableModelToMIPMapping, VariableMIPMetadata
from mip_convert.process import REQUIRED_OPTIONS


def get_variable_model_to_mip_mapping(model_to_mip_mappings: ModelToMIPMappingConfig,
                                      variable_name: str, mip_table_id: str) -> VariableModelToMIPMapping:
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


def get_variable_mip_metadata(variable_name: str, mip_table: str) -> VariableMIPMetadata:
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


def get_mip_table(mip_table_dir: str, mip_table_name: str) -> MIPConfig:
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


def get_model_to_mip_mappings(model_id: str, mip_table_name: str) -> ModelToMIPMappingConfig:
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
        '{base_model_configuration}_{suffix}'.format(base_model_configuration=base_model_configuration, suffix=suffix),
        '{model_configuration}_{suffix}'.format(model_configuration=model_id, suffix=suffix),
        '{mip_table_id}_{suffix}'.format(mip_table_id=mip_table_id, suffix=suffix),
        '{base_model_configuration}_{mip_table_id}_{suffix}'.format(base_model_configuration=base_model_configuration,
                                                                    mip_table_id=mip_table_id,
                                                                    suffix=suffix)
    ]

    for filename in hierarchy:
        pathname = os.path.join(dirname, filename)
        if os.path.isfile(pathname):
            model_to_mip_mappings.read(pathname)
            logger.debug('Reading "{filename}"'.format(filename=filename))

    return model_to_mip_mappings
