# (C) British Crown Copyright 2020-2022, Met Office.
# Please see LICENSE.rst for license details.
# pylint: disable = no-member
"""
The :mod:`user_config` module defines the information to be read from
the |user configuration file|.
"""
from cdds.common.constants import USER_CONFIG_OPTIONS
from hadsdk.common import (check_run_bounds_format,
                           check_file, check_files, check_number,
                           check_date_format,
                           check_directory,
                           check_variant_label_format)


def cmor_setup_config():
    """
    Define the |CMOR| setup-specific information to be read from the
    |user configuration file|.

    For more information, please see the `cmor_setup section`_ in the
    `MIP Convert User Guide`_.
    """
    section = 'cmor_setup'
    options = [item for items in list(USER_CONFIG_OPTIONS[section].values())
               for item in items]
    config = {option: _get_config(option, section) for option in options}
    config['mip_table_dir'] = _get_config(
        'inpath', section, required_by_mip_convert=True,
        check_function=check_directory)
    config['cmor_log_file'] = _get_config('logfile', section)
    return config


def cmor_dataset_config():
    """
    Define the |CMOR| dataset-specific information to be read from the
    |user configuration file|.

    For more information, please see the `cmor_dataset section`_ in the
    `MIP Convert User Guide`_.
    """
    section = 'cmor_dataset'
    options = [item for items in list(USER_CONFIG_OPTIONS[section].values())
               for item in items]
    config = {option: _get_config(option, section) for option in options}
    config['calendar'] = _get_config(
        'calendar', section, required_by_mip_convert=True)
    config['mip'] = _get_config('activity_id', section, value_type='multiple')
    config['mip_era'] = _get_config(
        'mip_era', section, required_by_mip_convert=True)
    config['output_dir'] = _get_config(
        'outpath', section, required_by_mip_convert=True,
        check_function=check_directory)
    config['model_id'] = _get_config(
        'source_id', section, required_by_mip_convert=True)
    config['model_type'] = _get_config(
        'source_type', section, value_type='multiple')
    config['parent_model_id'] = _get_config('parent_source_id', section)
    config['variant_label'] = _get_config(
        'variant_label', section, required_by_mip_convert=True,
        check_function=check_variant_label_format)
    return config


def request_config():
    """
    Define the request information to be read from the
    |user configuration file|.

    For more information, please see the `request section`_ in the
    `MIP Convert User Guide`_.
    """
    section = 'request'
    options = [item for items in list(USER_CONFIG_OPTIONS[section].values())
               for item in items]
    config = {option: _get_config(option, section) for option in options}
    config['ancil_files'] = _get_config(
        'ancil_files', section, value_type='multiple', default_value=True)
    config['atmos_timestep'] = _get_config(
        'atmos_timestep', section, python_type=int, default_value=True,
        check_function=check_number)
    config['child_base_date'] = _get_config(
        'base_date', section, required_by_mip_convert=True,
        check_function=check_date_format)
    config['deflate_level'] = _get_config(
        'deflate_level', section, python_type=int, default_value=True)
    config['hybrid_heights_files'] = _get_config(
        'hybrid_heights_files', section, value_type='multiple',
        default_value=True, check_function=check_files)
    config['replacement_coordinates_file'] = _get_config(
        'replacement_coordinates_file', section, default_value=True)
    config['run_bounds'] = _get_config(
        'run_bounds', section, value_type='multiple',
        required_by_mip_convert=True,
        check_function=check_run_bounds_format)
    config['shuffle'] = _get_config(
        'shuffle', section, python_type=bool, default_value=True)
    config['suite_id'] = _get_config(
        'suite_id', section, required_by_mip_convert=True)
    config['sites_file'] = _get_config(
        'sites_file', section, default_value=True, check_function=check_file)
    config['model_output_dir'] = _get_config(
        'sourcedir', section, required_by_mip_convert=True,
        name='root_load_path', check_function=check_directory)
    return config


def _get_config(option, section, python_type=str, value_type='single',
                default_value=False, required_by_cmor=False,
                required_by_mip_convert=False, name='default',
                check_function=None):
    """
    Return the information related to a specific ``option`` from the
    |user configuration file|.

    This information is used by :class:`configuration.python_config.PythonConfig` to
    add the options from the |user configuration file| as attributes to
    the :class:`configuration.UserConfig` object.

    Parameters
    ----------
    option: str
        The name of the option from the |user configuration file|.

    section: str
        The name of the section that the ``option`` belongs to in the
        |user configuration file|.

    python_type: callable
        The Python type of the value of the option from the
        |user configuration file|, e.g. :obj:`str`, :obj:`int`.

    value_type: str
        The type of the value of the option from the
        |user configuration file|; valid values are ``single`` and
        ``multiple``.

    default_value: bool
        If :obj:`True`, an attribute with a value of :obj:`None` will
        be added to the :class:`configuration.UserConfig` object,
        otherwise no attribute will be added.

    required_by_cmor: bool
        If :obj:`True`, the option is required by |CMOR|.

    required_by_mip_convert: bool
        If :obj:`True`, the option is required by ``mip_convert``.

    name: str
        The name of the attribute that will be added to the
        :class:`configuration.UserConfig` object.

    check_function: func
        The function that will be used to perform any checks or validation
        before the attribute is added to the :class:`configuration.UserConfig`
        object.

    Returns
    -------
    : :obj:`dict`
        The information related to the ``option`` from the
        |user configuration file|.
    """
    if name == 'default':
        name = option
    config = {
        'section': section,
        'python_type': python_type,
        'value_type': value_type,
        'default_value': default_value,
        'required_by_cmor': required_by_cmor,
        'required_by_mip_convert': required_by_mip_convert,
        'name': name,
        'check_function': check_function}
    return config
